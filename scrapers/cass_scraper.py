"""
Cass Freight Index Scraper
Scrapes monthly Cass Freight Index data from press releases
Source: https://www.cassinfo.com/freight-audit-payment/cass-transportation-indexes
"""

import re
from datetime import datetime
from dateutil import parser as date_parser
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scrapers.base_scraper import BaseScraper
from lib.database import SessionLocal, MacroMetric


class CassScraper(BaseScraper):
    """Scrape Cass Freight Index from press releases"""

    BASE_URL = "https://www.cassinfo.com/freight-audit-payment/cass-transportation-indexes"

    def __init__(self):
        super().__init__('cass_scraper')

    def fetch(self):
        """Fetch Cass Index page"""
        self.logger.info(f"Fetching from {self.BASE_URL}")
        response = self.get(self.BASE_URL)
        response.raise_for_status()
        return response.text

    def parse(self, html):
        """Parse Cass Index data from HTML"""
        soup = self.soup(html)
        metrics = []

        # Look for index tables or text containing index values
        # Cass typically publishes:
        # - Shipments Index (volume indicator)
        # - Expenditures Index (pricing indicator)

        # Try to find the latest report section
        # This is a simplified parser - may need adjustment based on actual page structure

        # Look for text patterns like "Shipments Index: 1.234" or "January 2024: 1.234"
        text_content = soup.get_text()

        # Find shipments index mentions
        shipments_pattern = r'Shipments Index.*?(\d+\.\d+)'
        expenditures_pattern = r'Expenditures Index.*?(\d+\.\d+)'
        month_pattern = r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})'

        # Extract the most recent data
        # Note: This is a basic parser. The actual Cass website may need more sophisticated parsing

        # For now, let's try to extract from any tables
        tables = soup.find_all('table')

        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 3:
                    # Try to parse: Month | Shipments Index | Expenditures Index
                    try:
                        month_text = cells[0].get_text().strip()
                        shipments_value = self._parse_float(cells[1].get_text())
                        expenditures_value = self._parse_float(cells[2].get_text()) if len(cells) > 2 else None

                        # Try to parse month
                        month_date = self._parse_month(month_text)

                        if month_date and shipments_value:
                            metrics.append({
                                'month': month_date,
                                'cass_shipments_index': shipments_value,
                                'cass_expenditures_index': expenditures_value
                            })
                    except:
                        continue

        # If no data from tables, try text parsing
        if not metrics:
            self.logger.warning("Could not parse Cass data from tables, trying text extraction")
            # Fallback: return placeholder noting manual review needed
            metrics.append({
                'month': datetime.now().strftime('%Y-%m'),
                'cass_shipments_index': None,
                'cass_expenditures_index': None,
                '_note': 'Manual parsing required - check Cass website'
            })

        self.logger.info(f"Parsed {len(metrics)} Cass index records")
        return metrics

    def store(self, metrics):
        """Store Cass metrics in database"""
        db = SessionLocal()
        stored_count = 0

        try:
            for metric_data in metrics:
                if metric_data.get('_note'):
                    self.logger.warning(f"Skipping placeholder record: {metric_data['_note']}")
                    continue

                # Get or create record for this month
                existing = db.query(MacroMetric).filter_by(month=metric_data['month']).first()

                if existing:
                    # Update existing record
                    if metric_data.get('cass_shipments_index'):
                        existing.cass_shipments_index = metric_data['cass_shipments_index']
                    if metric_data.get('cass_expenditures_index'):
                        existing.cass_expenditures_index = metric_data['cass_expenditures_index']
                    existing.source = 'Cass'
                    existing.confidence = 1.0
                else:
                    # Create new record
                    new_metric = MacroMetric(
                        month=metric_data['month'],
                        cass_shipments_index=metric_data.get('cass_shipments_index'),
                        cass_expenditures_index=metric_data.get('cass_expenditures_index'),
                        source='Cass',
                        confidence=1.0
                    )
                    db.add(new_metric)
                    stored_count += 1

            db.commit()
            self.logger.info(f"Stored/updated {stored_count} Cass metrics")

        except Exception as e:
            db.rollback()
            self.logger.error(f"Error storing Cass metrics: {e}")
            raise
        finally:
            db.close()

    # === Helper Methods ===

    def _parse_float(self, text):
        """Extract float from text"""
        try:
            # Remove commas and other characters
            cleaned = re.sub(r'[^\d.]', '', text)
            return float(cleaned) if cleaned else None
        except:
            return None

    def _parse_month(self, text):
        """Parse month from text like 'January 2024' or '2024-01'"""
        try:
            # Try parsing as date
            dt = date_parser.parse(text, fuzzy=True)
            return dt.strftime('%Y-%m')
        except:
            return None


def main():
    """Run Cass scraper"""
    print("⚠️  NOTE: Cass scraper may require manual verification of parsed data")
    print("   Check the Cass website to ensure data is accurate")

    scraper = CassScraper()
    success = scraper.run()

    if success:
        print("✅ Cass scraper completed")
    else:
        print("❌ Cass scraper failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
