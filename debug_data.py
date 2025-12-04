"""
Debug script to check what data we actually have
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from lib.database import SessionLocal, DailyMetric, MacroMetric, Lane, Rate, NewsArticle
from sqlalchemy import func

db = SessionLocal()

print("=" * 60)
print("DATABASE DATA AUDIT")
print("=" * 60)

# Daily Metrics
print("\n📅 DAILY METRICS:")
total_daily = db.query(DailyMetric).count()
print(f"  Total records: {total_daily}")

diesel_count = db.query(DailyMetric).filter(DailyMetric.diesel_usd_per_gal.isnot(None)).count()
print(f"  - With diesel price: {diesel_count}")

gas_count = db.query(DailyMetric).filter(DailyMetric.gas_price.isnot(None)).count()
print(f"  - With gas price: {gas_count}")

oil_count = db.query(DailyMetric).filter(DailyMetric.oil_price.isnot(None)).count()
print(f"  - With oil price: {oil_count}")

if total_daily > 0:
    latest = db.query(DailyMetric).order_by(DailyMetric.date.desc()).first()
    print(f"  Latest date: {latest.date}")
    print(f"    - Diesel: ${latest.diesel_usd_per_gal}")
    print(f"    - Gas: ${latest.gas_price}")
    print(f"    - Oil: ${latest.oil_price}")

# Macro Metrics
print("\n📊 MACRO METRICS:")
total_macro = db.query(MacroMetric).count()
print(f"  Total records: {total_macro}")

cass_ship_count = db.query(MacroMetric).filter(MacroMetric.cass_shipments_index.isnot(None)).count()
print(f"  - With Cass Shipments: {cass_ship_count}")

cass_exp_count = db.query(MacroMetric).filter(MacroMetric.cass_expenditures_index.isnot(None)).count()
print(f"  - With Cass Expenditures: {cass_exp_count}")

ata_count = db.query(MacroMetric).filter(MacroMetric.ata_tonnage_index.isnot(None)).count()
print(f"  - With ATA Tonnage: {ata_count}")

ism_count = db.query(MacroMetric).filter(MacroMetric.ism_pmi.isnot(None)).count()
print(f"  - With ISM PMI: {ism_count}")

if total_macro > 0:
    latest = db.query(MacroMetric).order_by(MacroMetric.month.desc()).first()
    print(f"  Latest month: {latest.month}")
    print(f"    - Cass Shipments: {latest.cass_shipments_index}")
    print(f"    - Cass Expenditures: {latest.cass_expenditures_index}")
    print(f"    - ATA Tonnage: {latest.ata_tonnage_index}")
    print(f"    - ISM PMI: {latest.ism_pmi}")

# Lanes
print("\n🛣️  LANES:")
total_lanes = db.query(Lane).count()
print(f"  Total lanes: {total_lanes}")

if total_lanes > 0:
    # Top origins
    top_origins = db.query(
        Lane.origin,
        func.count(Lane.id).label('count')
    ).group_by(Lane.origin).order_by(func.count(Lane.id).desc()).limit(5).all()

    print("  Top 5 origin states:")
    for origin, count in top_origins:
        print(f"    - {origin}: {count} lanes")

# Rates
print("\n💰 RATES:")
total_rates = db.query(Rate).count()
print(f"  Total rate records: {total_rates}")

# News
print("\n📰 NEWS:")
total_news = db.query(NewsArticle).count()
print(f"  Total articles: {total_news}")

high_importance = db.query(NewsArticle).filter(NewsArticle.importance >= 4).count()
print(f"  - High importance (4-5): {high_importance}")

print("\n" + "=" * 60)
print("DIAGNOSIS:")
print("=" * 60)

issues = []
if diesel_count == 0:
    issues.append("❌ NO DIESEL DATA - EIA scraper likely failed")
if cass_ship_count == 0:
    issues.append("❌ NO CASS DATA - Cass scraper likely failed")
if ata_count == 0:
    issues.append("❌ NO ATA DATA - ATA scraper likely failed")
if total_lanes < 100:
    issues.append(f"❌ VERY FEW LANES ({total_lanes}) - USASpending scraper needs more data")
if ism_count == 0:
    issues.append("❌ NO FRED DATA - FRED scraper likely failed")

if issues:
    for issue in issues:
        print(issue)
else:
    print("✅ All data sources have data!")

db.close()
