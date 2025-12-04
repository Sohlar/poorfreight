"""
ATA Truck Tonnage Index Scraper
Scrapes monthly ATA Truck Tonnage Index from press releases
Source: https://www.trucking.org/economics-and-industry-data
"""

import re
from datetime import datetime
from dateutil import parser as date_parser
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scrapers.base_scraper import BaseScraper
from lib.database import SessionLocal, MacroMetric


class ATAScraper(BaseScraper):
    """Scrape ATA Truck Tonnage Index from press releases"""

    BASE_URL = "https://www.trucking.org/economics-and-industry-data"

    def __init__(self):
        super().__init__('ata_scraper')

    def fetch(self):
        """Fetch ATA Index page"""
        self.logger.info(f"Fetching from {self.BASE_URL}")
        response = self.get(self.BASE_URL)
        response.raise_for_status()
        return response.text

    def parse(self, html):
        """Parse ATA Tonnage Index from HTML"""
        soup = self.soup(html)
        metrics = []

        # ATA publishes monthly press releases with tonnage index
        # Look for text patterns with index values
        text_content = soup.get_text()

        # Common patterns in ATA releases:
        # "The index increased/decreased to 123.4 in January"
        # "January 2024: 123.4"
        # "Tonnage Index: 123.4"

        # Try to find all press release links or index mentions
        links = soup.find_all('a', href=True)

        # Look for recent press release links
        press_release_links = []
        for link in links:
            href = link.get('href', '')
            text = link.get_text().lower()
            if 'tonnage' in text or 'truck tonnage index' in href.lower():
                if href.startswith('http'):
                    press_release_links.append(href)
                elif href.startswith('/'):
                    press_release_links.append(f"https://www.trucking.org{href}")

        # Fetch and parse recent press releases
        for pr_link in press_release_links[:12]:  # Last 12 months
            try:
                self.logger.info(f"  Fetching press release: {pr_link}")
                pr_response = self.get(pr_link)
                pr_soup = self.soup(pr_response.text)
                pr_text = pr_soup.get_text()

                # Extract index value and month
                index_value = self._extract_index_value(pr_text)
                month = self._extract_month(pr_text, pr_link)

                if index_value and month:
                    metrics.append({
                        'month': month,
                        'ata_tonnage_index': index_value
                    })
                    self.logger.info(f"    Found: {month} = {index_value}")

            except Exception as e:
                self.logger.warning(f"  Could not parse press release {pr_link}: {e}")
                continue

        # Fallback: try parsing from main page
        if not metrics:
            self.logger.warning("No data from press releases, trying main page")
            # Look for tables or structured data on main page
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        try:
                            month_text = cells[0].get_text().strip()
                            value_text = cells[1].get_text().strip()

                            month = self._parse_month(month_text)
                            value = self._parse_float(value_text)

                            if month and value:
                                metrics.append({
                                    'month': month,
                                    'ata_tonnage_index': value
                                })
                        except:
                            continue

        if not metrics:
            self.logger.warning("Could not extract ATA data - manual review needed")
            metrics.append({
                'month': datetime.now().strftime('%Y-%m'),
                'ata_tonnage_index': None,
                '_note': 'Manual parsing required - check ATA website'
            })

        self.logger.info(f"Parsed {len(metrics)} ATA index records")
        return metrics

    def store(self, metrics):
        """Store ATA metrics in database"""
        db = SessionLocal()
        stored_count = 0

        try:
            for metric_data in metrics:
                if metric_data.get('_note'):
                    self.logger.warning(f"Skipping placeholder: {metric_data['_note']}")
                    continue

                # Get or create record for this month
                existing = db.query(MacroMetric).filter_by(month=metric_data['month']).first()

                if existing:
                    # Update existing record
                    if metric_data.get('ata_tonnage_index'):
                        existing.ata_tonnage_index = metric_data['ata_tonnage_index']
                    existing.source = 'ATA'
                    existing.confidence = 1.0
                else:
                    # Create new record
                    new_metric = MacroMetric(
                        month=metric_data['month'],
                        ata_tonnage_index=metric_data.get('ata_tonnage_index'),
                        source='ATA',
                        confidence=1.0
                    )
                    db.add(new_metric)
                    stored_count += 1

            db.commit()
            self.logger.info(f"Stored/updated {stored_count} ATA metrics")

        except Exception as e:
            db.rollback()
            self.logger.error(f"Error storing ATA metrics: {e}")
            raise
        finally:
            db.close()

    # === Helper Methods ===

    def _extract_index_value(self, text):
        """Extract index value from press release text"""
        # Common patterns:
        # "increased to 123.4"
        # "decreased to 123.4"
        # "index was 123.4"
        # "stood at 123.4"

        patterns = [
            r'(?:increased|decreased|rose|fell)\s+to\s+(\d+\.\d+)',
            r'index was\s+(\d+\.\d+)',
            r'stood at\s+(\d+\.\d+)',
            r'SA index.*?(\d+\.\d+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return float(match.group(1))

        return None

    def _extract_month(self, text, url=''):
        """Extract month/year from text or URL"""
        # Try URL first (often contains date)
        url_match = re.search(r'/(\d{4})/(\d{2})/', url)
        if url_match:
            year, month = url_match.groups()
            return f"{year}-{month}"

        # Try text parsing
        months = ['january', 'february', 'march', 'april', 'may', 'june',
                  'july', 'august', 'september', 'october', 'november', 'december']

        text_lower = text.lower()
        for i, month_name in enumerate(months, 1):
            if month_name in text_lower:
                # Find year near month name
                year_match = re.search(rf'{month_name}\s+(\d{{4}})', text_lower)
                if year_match:
                    year = year_match.group(1)
                    return f"{year}-{i:02d}"

        return None

    def _parse_float(self, text):
        """Extract float from text"""
        try:
            cleaned = re.sub(r'[^\d.]', '', text)
            return float(cleaned) if cleaned else None
        except:
            return None

    def _parse_month(self, text):
        """Parse month from text"""
        try:
            dt = date_parser.parse(text, fuzzy=True)
            return dt.strftime('%Y-%m')
        except:
            return None


def main():
    """Run ATA scraper"""
    print("⚠️  NOTE: ATA scraper may require manual verification")
    print("   Check the ATA website to ensure data is accurate")

    scraper = ATAScraper()
    success = scraper.run()

    if success:
        print("✅ ATA scraper completed")
    else:
        print("❌ ATA scraper failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
