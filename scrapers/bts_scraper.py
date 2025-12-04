"""
BTS (Bureau of Transportation Statistics) Freight Analysis Framework Scraper
Fetches freight volume data and top lane information
Source: https://www.bts.gov/faf
"""

import requests
import pandas as pd
from datetime import datetime
import sys
import os
import io

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scrapers.base_scraper import BaseScraper
from lib.database import SessionLocal, Lane


class BTSScraper(BaseScraper):
    """Scrape freight lane data from BTS Freight Analysis Framework"""

    # BTS FAF5 data URL (latest version as of 2024)
    # This is the regional database with O-D flows
    FAF_DATA_URL = "https://faf.ornl.gov/faf5/data/download_files/FAF5.4.1_2017-2022.csv"

    # State FIPS codes to names mapping (FAF regions)
    STATE_CODES = {
        '01': 'Alabama', '04': 'Arizona', '05': 'Arkansas', '06': 'California',
        '08': 'Colorado', '09': 'Connecticut', '10': 'Delaware', '12': 'Florida',
        '13': 'Georgia', '16': 'Idaho', '17': 'Illinois', '18': 'Indiana',
        '19': 'Iowa', '20': 'Kansas', '21': 'Kentucky', '22': 'Louisiana',
        '23': 'Maine', '24': 'Maryland', '25': 'Massachusetts', '26': 'Michigan',
        '27': 'Minnesota', '28': 'Mississippi', '29': 'Missouri', '30': 'Montana',
        '31': 'Nebraska', '32': 'Nevada', '33': 'New Hampshire', '34': 'New Jersey',
        '35': 'New Mexico', '36': 'New York', '37': 'North Carolina', '38': 'North Dakota',
        '39': 'Ohio', '40': 'Oklahoma', '41': 'Oregon', '42': 'Pennsylvania',
        '44': 'Rhode Island', '45': 'South Carolina', '46': 'South Dakota', '47': 'Tennessee',
        '48': 'Texas', '49': 'Utah', '50': 'Vermont', '51': 'Virginia',
        '53': 'Washington', '54': 'West Virginia', '55': 'Wisconsin', '56': 'Wyoming'
    }

    def __init__(self):
        super().__init__('bts_scraper')

    def fetch(self):
        """Fetch BTS FAF data"""
        self.logger.info("Fetching BTS Freight Analysis Framework data...")
        self.logger.info("This is a large file (~500MB), may take a few minutes...")

        try:
            response = self.get(self.FAF_DATA_URL, stream=True)
            response.raise_for_status()

            # Download in chunks to avoid memory issues
            chunks = []
            total_size = 0

            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    chunks.append(chunk)
                    total_size += len(chunk)
                    if total_size % (10 * 1024 * 1024) == 0:  # Log every 10MB
                        self.logger.info(f"Downloaded {total_size / (1024*1024):.1f} MB...")

            csv_data = b''.join(chunks)
            self.logger.info(f"Download complete: {total_size / (1024*1024):.1f} MB")

            return csv_data

        except Exception as e:
            self.logger.error(f"Failed to fetch BTS data: {e}")
            raise

    def parse(self, raw_data):
        """Parse BTS FAF data and identify top lanes"""
        self.logger.info("Parsing BTS FAF data...")

        try:
            # Load CSV into pandas
            df = pd.read_csv(io.BytesIO(raw_data), low_memory=False)

            self.logger.info(f"Loaded {len(df):,} records from BTS FAF database")

            # Filter for truck transportation only (mode codes 1=Truck, 2=Rail, etc.)
            # Mode: 1 = Truck, 2 = Rail, 3 = Water, 4 = Air, 5 = Multiple/Intermodal, 6 = Pipeline, 7 = Other
            truck_data = df[df['dms_mode'].isin([1, 5])]  # Truck and Intermodal

            self.logger.info(f"Filtered to {len(truck_data):,} truck/intermodal records")

            # Group by origin-destination pairs and sum tonnage
            # FAF uses 'dms_orig' and 'dms_dest' for origin/destination regions
            lane_volumes = truck_data.groupby(['dms_orig', 'dms_dest']).agg({
                'tons_2022': 'sum',  # Use most recent year available
                'value_2022': 'sum'
            }).reset_index()

            # Sort by tonnage to get top lanes
            lane_volumes = lane_volumes.sort_values('tons_2022', ascending=False)

            # Convert region codes to readable names
            lanes = []
            for idx, row in lane_volumes.head(5000).iterrows():  # Top 5000 lanes
                origin_code = str(row['dms_orig'])
                dest_code = str(row['dms_dest'])

                # Parse region codes (format: state code + region)
                origin_name = self._parse_region_code(origin_code)
                dest_name = self._parse_region_code(dest_code)

                # Skip if same origin and destination
                if origin_code == dest_code:
                    continue

                # Estimate distance (rough approximation based on region codes)
                # In production, would use geocoding
                distance = self._estimate_distance(origin_code, dest_code)

                lanes.append({
                    'origin': origin_name,
                    'destination': dest_name,
                    'annual_tons': float(row['tons_2022']) if pd.notna(row['tons_2022']) else 0,
                    'annual_value_millions': float(row['value_2022']) / 1000 if pd.notna(row['value_2022']) else 0,
                    'distance_miles': distance,
                    'equipment_type': 'van'  # Default, would need commodity analysis for specifics
                })

            self.logger.info(f"Identified {len(lanes)} top freight lanes")
            return lanes

        except Exception as e:
            self.logger.error(f"Error parsing BTS data: {e}")
            raise

    def _parse_region_code(self, code):
        """Convert FAF region code to readable name"""
        # FAF codes are like "011" = Alabama region 1
        # First 2 digits = state, last digit = region within state

        if len(str(code)) >= 2:
            state_code = str(code)[:2].zfill(2)
            region = str(code)[2:] if len(str(code)) > 2 else ''

            state_name = self.STATE_CODES.get(state_code, f"State_{state_code}")

            if region and region != '0':
                return f"{state_name} (Region {region})"
            else:
                return state_name

        return f"Region_{code}"

    def _estimate_distance(self, origin_code, dest_code):
        """Rough distance estimation based on region codes"""
        # Very rough approximation: use difference in state codes as proxy
        # In production, would use actual geocoding

        try:
            o_state = int(str(origin_code)[:2])
            d_state = int(str(dest_code)[:2])

            # Rough estimate: 500 miles per state difference
            # This is very approximate
            state_diff = abs(o_state - d_state)
            return max(100, state_diff * 500)  # Minimum 100 miles
        except:
            return 500  # Default

    def store(self, lanes):
        """Store top lanes in database"""
        db = SessionLocal()
        stored_count = 0
        updated_count = 0

        try:
            for lane_data in lanes:
                # Check if lane already exists
                existing = db.query(Lane).filter_by(
                    origin=lane_data['origin'],
                    destination=lane_data['destination'],
                    equipment_type=lane_data['equipment_type']
                ).first()

                if existing:
                    # Update volume rank based on tonnage
                    existing.volume_rank = stored_count + updated_count + 1
                    existing.distance_miles = lane_data['distance_miles']
                    updated_count += 1
                else:
                    # Create new lane record
                    new_lane = Lane(
                        origin=lane_data['origin'],
                        destination=lane_data['destination'],
                        equipment_type=lane_data['equipment_type'],
                        distance_miles=lane_data['distance_miles'],
                        volume_rank=stored_count + updated_count + 1
                    )
                    db.add(new_lane)
                    stored_count += 1

            db.commit()
            self.logger.info(f"Stored {stored_count} new + updated {updated_count} lanes")

        except Exception as e:
            db.rollback()
            self.logger.error(f"Error storing lanes: {e}")
            raise
        finally:
            db.close()


def main():
    """Run BTS scraper"""
    scraper = BTSScraper()

    print("⚠️  Note: BTS FAF data download is large (~500MB)")
    print("   This may take several minutes depending on your connection")
    print()

    success = scraper.run()

    if success:
        print("✅ BTS lane data scraper completed")
    else:
        print("❌ BTS lane data scraper failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
