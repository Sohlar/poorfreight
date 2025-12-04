"""
Run All Scrapers
Convenience script to run all data scrapers in sequence
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scrapers.news_scraper import NewsScraper
from scrapers.cass_scraper import CassScraper
from scrapers.ata_scraper import ATAScraper
from scrapers.fred_scraper import FREDScraper
from scrapers.eia_diesel_scraper import EIADieselScraper
from scrapers.bts_scraper import BTSScraper
from scrapers.usaspending_scraper import USASpendingScraper


def main():
    """Run all scrapers"""
    print("=" * 60)
    print("FREIGHT INTELLIGENCE PORTAL - DATA INGESTION")
    print("=" * 60)
    print()

    scrapers = [
        ("News (4 sources)", NewsScraper()),
        ("EIA Diesel Prices", EIADieselScraper()),
        ("FRED Economic Indicators", FREDScraper()),
        ("Cass Freight Index", CassScraper()),
        ("ATA Truck Tonnage", ATAScraper()),
        # ("BTS Top Freight Lanes", BTSScraper()),  # NOTE: Requires manual download - BTS blocks automated access
        ("USASpending Gov Contracts", USASpendingScraper()),
    ]

    results = {}

    for name, scraper in scrapers:
        print(f"\n{'='*60}")
        print(f"Running: {name}")
        print(f"{'='*60}\n")

        try:
            success = scraper.run()
            results[name] = "✅ Success" if success else "❌ Failed"
        except Exception as e:
            print(f"❌ Fatal error in {name}: {e}")
            results[name] = f"❌ Error: {e}"

    # Summary
    print(f"\n\n{'='*60}")
    print("SCRAPING SUMMARY")
    print(f"{'='*60}\n")

    for name, result in results.items():
        print(f"{name:.<40} {result}")

    print()

    # Check if any failed
    failed_count = sum(1 for r in results.values() if '❌' in r)
    if failed_count > 0:
        print(f"⚠️  {failed_count} scraper(s) failed")
        sys.exit(1)
    else:
        print("✅ All scrapers completed successfully!")
        sys.exit(0)


if __name__ == "__main__":
    main()
