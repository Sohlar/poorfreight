"""
EIA (Energy Information Administration) Diesel Price Scraper
Fetches weekly retail diesel prices (national and regional)
Source: https://www.eia.gov/
"""

import requests
from datetime import datetime
import sys
import os
from dotenv import load_dotenv

load_dotenv()

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scrapers.base_scraper import BaseScraper
from lib.database import SessionLocal, DailyMetric, DieselPrice


class EIADieselScraper(BaseScraper):
    """Scrape diesel prices from EIA API"""

    API_BASE = "https://api.eia.gov/v2/petroleum/pri/gnd/data/"

    # Diesel price series
    # EMD_EPD2D_PTE_NUS_DPG = US No 2 Diesel Retail Prices
    SERIES_ID = "EMD_EPD2D_PTE_NUS_DPG"

    def __init__(self):
        super().__init__('eia_diesel_scraper')
        self.api_key = os.getenv('EIA_API_KEY')

        if not self.api_key:
            self.logger.warning("EIA_API_KEY not found - will try web scraping fallback")

    def fetch(self):
        """Fetch diesel prices from EIA"""

        if self.api_key:
            return self._fetch_via_api()
        else:
            return self._fetch_via_web_scraping()

    def _fetch_via_api(self):
        """Fetch using EIA API (preferred method)"""
        self.logger.info("Fetching ALL diesel prices (national + regional) via EIA API with 5+ years of history...")

        # Fetch ALL diesel price data - national and regional
        # We want MAXIMUM data collection for detailed analysis
        # EIA API limits to 5000 records per request, so we'll fetch in batches

        all_data = []
        offset = 0
        length = 5000
        total_available = None

        try:
            # Fetch data in batches using pagination
            while True:
                params = {
                    'api_key': self.api_key,
                    'frequency': 'weekly',
                    'data[0]': 'value',
                    'sort[0][column]': 'period',
                    'sort[0][direction]': 'desc',
                    'offset': offset,
                    'length': length
                }

                response = self.get(self.API_BASE, params=params)
                response.raise_for_status()

                data = response.json()

                if 'response' in data and 'data' in data['response']:
                    batch = data['response']['data']

                    if not batch:
                        # No more data
                        break

                    all_data.extend(batch)

                    # Get total count from API response
                    if total_available is None and 'response' in data and 'total' in data['response']:
                        total_available = data['response']['total']
                        self.logger.info(f"API reports {total_available} total records available")

                    self.logger.info(f"Fetched batch: offset={offset}, records={len(batch)}, total_so_far={len(all_data)}")

                    # If we got fewer records than requested, we've reached the end
                    if len(batch) < length:
                        break

                    offset += length

                    # Safety limit: max 100k records (about 10+ years of weekly data for 29 regions)
                    if len(all_data) >= 100000:
                        self.logger.warning(f"Reached safety limit of 100,000 records")
                        break
                else:
                    self.logger.warning("Unexpected API response format, falling back to web scraping")
                    return self._fetch_via_web_scraping()

            self.logger.info(f"Fetched {len(all_data)} total diesel price records (all regions, all available history)")
            return all_data

        except Exception as e:
            self.logger.error(f"API fetch failed: {e}, falling back to web scraping")
            return self._fetch_via_web_scraping()

    def _fetch_via_web_scraping(self):
        """Fallback: scrape from EIA website"""
        self.logger.info("Fetching diesel prices via web scraping...")

        url = "https://www.eia.gov/dnav/pet/hist/LeafHandler.ashx?n=pet&s=emd_epd2d_pte_nus_dpg&f=w"

        response = self.get(url)
        response.raise_for_status()

        return response.text

    def parse(self, raw_data):
        """Parse EIA data"""

        if isinstance(raw_data, list):
            # API response
            return self._parse_api_data(raw_data)
        elif isinstance(raw_data, str):
            # HTML response
            return self._parse_html_data(raw_data)
        else:
            self.logger.error(f"Unknown data format: {type(raw_data)}")
            return []

    def _parse_api_data(self, data):
        """Parse API JSON response - collect ALL regional data"""
        prices = []

        for record in data:
            try:
                # EIA API returns period like "2024-12-02" (Monday of the week)
                date = record.get('period')
                value = record.get('value')
                region = record.get('duoarea', 'UNKNOWN')  # R10, R20, NUS, etc.
                region_name = record.get('area-name', 'Unknown')
                series_desc = record.get('series-description', '')

                if date and value:
                    prices.append({
                        'date': date,
                        'diesel_price': float(value),
                        'region_code': region,
                        'region_name': region_name,
                        'series_description': series_desc
                    })

            except Exception as e:
                self.logger.debug(f"Error parsing record: {e}")
                continue

        self.logger.info(f"Parsed {len(prices)} diesel price records from API (all regions)")
        return prices

    def _parse_html_data(self, html):
        """Parse HTML table (fallback)"""
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html, 'lxml')
        prices = []

        # Find data table
        tables = soup.find_all('table', class_='FloatTitle')

        for table in tables:
            rows = table.find_all('tr')

            for row in rows[1:]:  # Skip header
                cells = row.find_all('td')

                if len(cells) >= 2:
                    try:
                        date_text = cells[0].get_text().strip()
                        price_text = cells[1].get_text().strip()

                        # Parse date (format: "Dec 02, 2024")
                        try:
                            date_obj = datetime.strptime(date_text, "%b %d, %Y")
                            date = date_obj.strftime('%Y-%m-%d')
                        except:
                            # Try other formats
                            from dateutil import parser as date_parser
                            date_obj = date_parser.parse(date_text)
                            date = date_obj.strftime('%Y-%m-%d')

                        # Parse price
                        price = float(price_text.replace('$', '').strip())

                        prices.append({
                            'date': date,
                            'diesel_price': price
                        })

                    except Exception as e:
                        self.logger.debug(f"Error parsing row: {e}")
                        continue

        self.logger.info(f"Parsed {len(prices)} diesel prices from HTML")
        return prices

    def store(self, prices):
        """Store diesel prices in database"""
        db = SessionLocal()
        stored_count = 0
        updated_count = 0
        regional_stored = 0
        regional_updated = 0

        try:
            for price_data in prices:
                date = price_data['date']
                price = price_data['diesel_price']
                region_code = price_data.get('region_code', 'UNKNOWN')
                region_name = price_data.get('region_name', 'Unknown')
                series_desc = price_data.get('series_description', '')

                # Store ALL regional diesel prices in the DieselPrice table
                existing_regional = db.query(DieselPrice).filter_by(
                    date=date,
                    region_code=region_code
                ).first()

                if existing_regional:
                    existing_regional.price = price
                    existing_regional.region_name = region_name
                    existing_regional.series_description = series_desc
                    regional_updated += 1
                else:
                    new_regional = DieselPrice(
                        date=date,
                        region_code=region_code,
                        region_name=region_name,
                        price=price,
                        series_description=series_desc,
                        source='EIA'
                    )
                    db.add(new_regional)
                    regional_stored += 1

                # ALSO store national (NUS) price in DailyMetric for backward compatibility
                if region_code == 'NUS':
                    existing_daily = db.query(DailyMetric).filter_by(date=date).first()

                    if existing_daily:
                        existing_daily.diesel_usd_per_gal = price
                        if not existing_daily.source or 'EIA' not in existing_daily.source:
                            existing_daily.source = 'EIA'
                        updated_count += 1
                    else:
                        new_daily = DailyMetric(
                            date=date,
                            diesel_usd_per_gal=price,
                            source='EIA',
                            confidence=1.0
                        )
                        db.add(new_daily)
                        stored_count += 1

            db.commit()
            self.logger.info(f"Stored {regional_stored} new + updated {regional_updated} regional diesel prices")
            self.logger.info(f"Stored {stored_count} new + updated {updated_count} national diesel prices in DailyMetric")

        except Exception as e:
            db.rollback()
            self.logger.error(f"Error storing diesel prices: {e}")
            raise
        finally:
            db.close()


def main():
    """Run EIA diesel scraper"""
    scraper = EIADieselScraper()

    if not scraper.api_key:
        print("⚠️  Warning: EIA_API_KEY not set in .env")
        print("   Will use web scraping fallback")
        print("   Get a free API key at: https://www.eia.gov/opendata/register.php")
        print()

    success = scraper.run()

    if success:
        print("✅ EIA diesel scraper completed")
    else:
        print("❌ EIA diesel scraper failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
