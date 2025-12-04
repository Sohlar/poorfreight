"""
USASpending.gov API Scraper
Fetches government freight contract awards for benchmark pricing
Source: https://www.usaspending.gov/
API Docs: https://api.usaspending.gov/
"""

import requests
from datetime import datetime, timedelta
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scrapers.base_scraper import BaseScraper
from lib.database import SessionLocal, Rate, Lane


class USASpendingScraper(BaseScraper):
    """Scrape government freight contract data from USASpending.gov"""

    API_BASE = "https://api.usaspending.gov/api/v2/search/spending_by_award/"

    # PSC (Product Service Codes) for freight transportation
    # V1 = Trucking/motor freight
    # V2 = Freight forwarding
    FREIGHT_PSC_CODES = ['V1', 'V2']

    def __init__(self):
        super().__init__('usaspending_scraper')

    def fetch(self):
        """Fetch recent freight contract awards with pagination"""
        self.logger.info("Fetching government freight contracts from USASpending.gov...")

        # Get contracts from last 24 months for more data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=730)  # 2 years

        all_awards = []
        limit_per_page = 100
        max_contracts_per_psc = 2000  # Collect up to 2000 contracts per PSC code

        for psc_code in self.FREIGHT_PSC_CODES:
            try:
                self.logger.info(f"Fetching PSC code {psc_code} (Trucking/Freight)...")
                page = 1
                psc_total = 0

                while psc_total < max_contracts_per_psc:
                    payload = {
                        "filters": {
                            "time_period": [
                                {
                                    "start_date": start_date.strftime("%Y-%m-%d"),
                                    "end_date": end_date.strftime("%Y-%m-%d")
                                }
                            ],
                            "award_type_codes": ["A", "B", "C", "D"],  # Contracts
                            "psc_codes": [psc_code]
                        },
                        "fields": [
                            "Award ID",
                            "Recipient Name",
                            "Start Date",
                            "End Date",
                            "Award Amount",
                            "Description",
                            "awarding_agency_name",
                            "recipient_location_state_code",
                            "pop_state_code"  # Place of performance
                        ],
                        "page": page,
                        "limit": limit_per_page,
                        "sort": "Award Amount",
                        "order": "desc"
                    }

                    response = self.post(self.API_BASE, json=payload)
                    response.raise_for_status()

                    data = response.json()

                    if 'results' in data and len(data['results']) > 0:
                        awards = data['results']
                        all_awards.extend(awards)
                        psc_total += len(awards)
                        self.logger.info(f"  → Page {page}: {len(awards)} contracts (total: {psc_total})")

                        # If we got fewer results than the limit, we've reached the end
                        if len(awards) < limit_per_page:
                            break

                        page += 1
                    else:
                        self.logger.info(f"  → No more results for {psc_code}")
                        break

                self.logger.info(f"  ✓ Collected {psc_total} total contracts for {psc_code}")

            except Exception as e:
                self.logger.error(f"Error fetching PSC {psc_code}: {e}")
                continue

        self.logger.info(f"Total contracts fetched across all PSC codes: {len(all_awards)}")
        return all_awards

    def parse(self, raw_data):
        """Parse contract awards into rate data"""
        rates = []

        for award in raw_data:
            try:
                # Extract key fields
                award_id = award.get('Award ID', '')
                amount = award.get('Award Amount', 0)
                start_date = award.get('Start Date', '')
                description = award.get('Description', '').lower()
                recipient_state = award.get('recipient_location_state_code', '')
                pop_state = award.get('pop_state_code', '')  # Place of performance

                # Skip awards with no amount
                if not amount or amount <= 0:
                    continue

                # Try to extract origin/destination from description or states
                origin = recipient_state or 'Unknown'
                destination = pop_state or 'Unknown'

                # Skip if no geographic data
                if origin == 'Unknown' and destination == 'Unknown':
                    continue

                # Try to determine equipment type from description
                equipment_type = 'van'  # Default
                if 'reefer' in description or 'refrigerat' in description:
                    equipment_type = 'reefer'
                elif 'flatbed' in description or 'flat bed' in description:
                    equipment_type = 'flatbed'

                # Estimate rate per mile (very rough - would need actual mileage data)
                # For now, we'll store the contract value and note it's a contract
                rates.append({
                    'award_id': award_id,
                    'origin': origin,
                    'destination': destination,
                    'equipment_type': equipment_type,
                    'amount': float(amount),
                    'start_date': start_date,
                    'description': description[:200]  # Truncate
                })

            except Exception as e:
                self.logger.debug(f"Error parsing award: {e}")
                continue

        self.logger.info(f"Parsed {len(rates)} government freight contracts")
        return rates

    def store(self, contracts):
        """Store contract data in database"""
        db = SessionLocal()
        stored_count = 0
        lanes_created = 0

        try:
            for contract in contracts:
                # Get or create lane
                lane = db.query(Lane).filter_by(
                    origin=contract['origin'],
                    destination=contract['destination'],
                    equipment_type=contract['equipment_type']
                ).first()

                if not lane:
                    # Create new lane
                    lane = Lane(
                        origin=contract['origin'],
                        destination=contract['destination'],
                        equipment_type=contract['equipment_type'],
                        distance_miles=500  # Placeholder - would need geocoding
                    )
                    db.add(lane)
                    db.flush()  # Get lane ID
                    lanes_created += 1

                # Parse date
                try:
                    date_str = contract['start_date']
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                    date = date_obj.strftime('%Y-%m-%d')
                except:
                    date = datetime.now().strftime('%Y-%m-%d')

                # Check if rate already exists
                existing = db.query(Rate).filter_by(
                    lane_id=lane.id,
                    date=date,
                    source='USASpending'
                ).first()

                if not existing:
                    # Create new rate record
                    # Note: We're storing the contract amount, not rate per mile
                    # In a real system, we'd calculate actual rate per mile
                    new_rate = Rate(
                        lane_id=lane.id,
                        date=date,
                        rate_per_mile=0.0,  # Would need actual mileage to calculate
                        is_spot=False,
                        is_contract=True,
                        source='USASpending',
                        confidence_score=0.8  # Medium confidence due to limited data
                    )
                    db.add(new_rate)
                    stored_count += 1

            db.commit()
            self.logger.info(f"Stored {stored_count} contract rates, created {lanes_created} new lanes")

        except Exception as e:
            db.rollback()
            self.logger.error(f"Error storing contract data: {e}")
            raise
        finally:
            db.close()


def main():
    """Run USASpending scraper"""
    scraper = USASpendingScraper()

    print("ℹ️  Fetching government freight contracts from USASpending.gov")
    print("   This provides benchmark pricing from federal contracts")
    print()

    success = scraper.run()

    if success:
        print("✅ USASpending scraper completed")
    else:
        print("❌ USASpending scraper failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
