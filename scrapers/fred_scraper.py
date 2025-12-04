"""
FRED (Federal Reserve Economic Data) API Scraper
Fetches economic indicators that impact freight markets
Source: https://fred.stlouisfed.org/
"""

import requests
from datetime import datetime, timedelta
import sys
import os
from dotenv import load_dotenv

load_dotenv()

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scrapers.base_scraper import BaseScraper
from lib.database import SessionLocal, DailyMetric, MacroMetric


class FREDScraper(BaseScraper):
    """Scrape economic indicators from FRED API"""

    API_BASE = "https://api.stlouisfed.org/fred/series/observations"

    # Economic indicators relevant to freight
    SERIES = {
        # Manufacturing & Industrial
        'IPMAN': {'name': 'Industrial Production: Manufacturing', 'table': 'macro', 'field': 'industrial_production'},
        'BSCICP03USM665S': {'name': 'OECD Business Confidence: Manufacturing (US)', 'table': 'macro', 'field': 'ism_pmi'},

        # Consumer & Retail
        'RSXFS': {'name': 'Retail Sales', 'table': 'macro', 'field': 'retail_sales'},
        'UMCSENT': {'name': 'Consumer Sentiment', 'table': 'macro', 'field': 'consumer_sentiment'},

        # Transportation specific
        'TRUCKD11': {'name': 'ATA Truck Tonnage Index', 'table': 'macro', 'field': 'ata_tonnage_index'},
        'FRGSHPUSM649NCIS': {'name': 'Cass Freight Index: Shipments', 'table': 'macro', 'field': 'cass_shipments_index'},
        'FRGEXPUSM649NCIS': {'name': 'Cass Freight Index: Expenditures', 'table': 'macro', 'field': 'cass_expenditures_index'},

        # Fuel/Energy
        'GASREGW': {'name': 'Gas Prices (Weekly)', 'table': 'daily', 'field': 'gas_price'},
        'DCOILWTICO': {'name': 'Crude Oil WTI', 'table': 'daily', 'field': 'oil_price'},
    }

    def __init__(self):
        super().__init__('fred_scraper')
        self.api_key = os.getenv('FRED_API_KEY')

        if not self.api_key:
            self.logger.warning("FRED_API_KEY not found in .env - will use limited access")

    def fetch(self):
        """Fetch all configured FRED series"""
        all_data = {}

        for series_id, config in self.SERIES.items():
            try:
                self.logger.info(f"Fetching {config['name']} ({series_id})...")

                params = {
                    'series_id': series_id,
                    'file_type': 'json',
                    'sort_order': 'desc',
                    'limit': 100000  # Get ALL available history (FRED supports up to 100k)
                }

                if self.api_key:
                    params['api_key'] = self.api_key

                response = self.get(self.API_BASE, params=params)
                response.raise_for_status()

                data = response.json()

                if 'observations' in data:
                    all_data[series_id] = {
                        'config': config,
                        'observations': data['observations']
                    }
                    self.logger.info(f"  → {len(data['observations'])} observations")
                else:
                    self.logger.warning(f"  → No data returned for {series_id}")

            except Exception as e:
                self.logger.error(f"Error fetching {series_id}: {e}")
                continue

        return all_data

    def parse(self, raw_data):
        """Parse FRED observations into our data model"""
        daily_metrics = []
        macro_metrics = []

        for series_id, series_data in raw_data.items():
            config = series_data['config']
            observations = series_data['observations']

            for obs in observations:
                try:
                    date = obs['date']
                    value = obs['value']

                    # Skip missing values
                    if value == '.':
                        continue

                    value = float(value)

                    # Determine if daily or macro (monthly)
                    if config['table'] == 'daily':
                        daily_metrics.append({
                            'date': date,
                            'field': config['field'],
                            'value': value,
                            'source': f"FRED-{series_id}"
                        })
                    else:  # macro (monthly)
                        # Convert to YYYY-MM format
                        dt = datetime.strptime(date, '%Y-%m-%d')
                        month = dt.strftime('%Y-%m')

                        macro_metrics.append({
                            'month': month,
                            'field': config['field'],
                            'value': value,
                            'source': f"FRED-{series_id}"
                        })

                except Exception as e:
                    self.logger.debug(f"Error parsing observation: {e}")
                    continue

        self.logger.info(f"Parsed {len(daily_metrics)} daily + {len(macro_metrics)} macro observations")
        return {'daily': daily_metrics, 'macro': macro_metrics}

    def store(self, parsed_data):
        """Store FRED data in database"""
        db = SessionLocal()
        daily_stored = 0
        macro_stored = 0

        try:
            # Store daily metrics
            for metric in parsed_data['daily']:
                existing = db.query(DailyMetric).filter_by(date=metric['date']).first()

                if existing:
                    # Update field (e.g., gas_price, oil_price)
                    setattr(existing, metric['field'], metric['value'])
                    if not existing.source or 'FRED' not in existing.source:
                        existing.source = metric['source']
                else:
                    # Create new record
                    new_metric = DailyMetric(
                        date=metric['date'],
                        source=metric['source'],
                        confidence=1.0
                    )
                    setattr(new_metric, metric['field'], metric['value'])
                    db.add(new_metric)
                    db.flush()  # Make visible to subsequent queries
                    daily_stored += 1

            # Store macro metrics
            for metric in parsed_data['macro']:
                existing = db.query(MacroMetric).filter_by(month=metric['month']).first()

                if existing:
                    # Update field
                    setattr(existing, metric['field'], metric['value'])
                    if not existing.source or 'FRED' not in existing.source:
                        existing.source = metric['source']
                else:
                    # Create new record
                    new_metric = MacroMetric(
                        month=metric['month'],
                        source=metric['source'],
                        confidence=1.0
                    )
                    setattr(new_metric, metric['field'], metric['value'])
                    db.add(new_metric)
                    db.flush()  # Make visible to subsequent queries
                    macro_stored += 1

            db.commit()
            self.logger.info(f"Stored {daily_stored} daily + {macro_stored} macro metrics")

        except Exception as e:
            db.rollback()
            self.logger.error(f"Error storing FRED data: {e}")
            raise
        finally:
            db.close()


def main():
    """Run FRED scraper"""
    scraper = FREDScraper()

    if not scraper.api_key:
        print("⚠️  Warning: FRED_API_KEY not set in .env")
        print("   You can still use FRED data but with rate limits")
        print("   Get a free API key at: https://fred.stlouisfed.org/docs/api/api_key.html")
        print()

    success = scraper.run()

    if success:
        print("✅ FRED scraper completed")
    else:
        print("❌ FRED scraper failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
