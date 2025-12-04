# Data Sources Reference

Complete list of data sources integrated into the Freight Intelligence Portal.

---

## ✅ Active Data Sources

### 1. News Sources (RSS Feeds)

| Source | URL | Update Frequency | Auto-Tagged |
|--------|-----|------------------|-------------|
| **FreightWaves** | https://www.freightwaves.com/feed | Every 30min | ✅ |
| **Supply Chain Dive** | https://www.supplychaindive.com/feeds/news/ | Every 30min | ✅ |
| **Transport Topics** | https://www.ttnews.com/rss/feed/top-news | Every 30min | ✅ |
| **JOC** | https://www.joc.com/rss/all-categories | Every 30min | ✅ |

**What you get:**
- Freight industry news articles
- Auto-tagging: capacity, rates, diesel, ltl, ftl, contracts, economy, regulation, labor, etc.
- Auto-importance rating (1-5 stars)
- Full article extraction
- Personal notes and annotations

---

### 2. EIA - Energy Information Administration

**Source**: https://www.eia.gov/
**API Key**: Required (you have one in .env)
**Update Frequency**: Weekly (Wednesdays)

**Data Points:**
- U.S. No 2 Diesel Retail Prices ($/gallon)
- National average diesel price
- Historical data back to 1994

**Scraper**: `scrapers/eia_diesel_scraper.py`
**Database Table**: `daily_metrics.diesel_usd_per_gal`

---

### 3. FRED - Federal Reserve Economic Data

**Source**: https://fred.stlouisfed.org/
**API Key**: Required (you have one in .env)
**Update Frequency**: Varies by series (daily/monthly)

**Economic Indicators:**

| Series ID | Description | Frequency | Field Name |
|-----------|-------------|-----------|------------|
| **IPMAN** | Industrial Production: Manufacturing | Monthly | `industrial_production` |
| **ISM** | ISM Manufacturing PMI | Monthly | `ism_pmi` |
| **RSXFS** | Retail Sales | Monthly | `retail_sales` |
| **UMCSENT** | Consumer Sentiment Index | Monthly | `consumer_sentiment` |
| **TRUCKD11** | Truck Transportation Index | Monthly | `truck_transport_index` |
| **GASREGW** | Regular Gas Prices (Weekly) | Weekly | `gas_price` |
| **DCOILWTICO** | Crude Oil WTI | Daily | `oil_price` |

**Why these matter for freight:**
- **PMI**: Leading indicator of freight demand
- **Industrial Production**: Drives freight volumes
- **Retail Sales**: Consumer demand indicator
- **Consumer Sentiment**: Future spending predictor
- **Truck Index**: Direct freight market measure

**Scraper**: `scrapers/fred_scraper.py`
**Database Tables**: `daily_metrics` (daily series), `macro_metrics` (monthly series)

---

### 4. Cass Freight Index

**Source**: https://www.cassinfo.com/freight-audit-indexes
**API**: No (web scraping)
**Update Frequency**: Monthly

**Data Points:**
- Cass Shipments Index (volume indicator)
- Cass Expenditures Index (pricing indicator)
- Month-over-month and year-over-year changes

**Scraper**: `scrapers/cass_scraper.py`
**Database Table**: `macro_metrics`

⚠️ **Note**: May require manual verification as website structure changes.

---

### 5. ATA Truck Tonnage Index

**Source**: https://www.trucking.org/news-insights/ata-truck-tonnage-index
**API**: No (web scraping from press releases)
**Update Frequency**: Monthly

**Data Points:**
- ATA Truck Tonnage Index
- Seasonally adjusted values
- Month-over-month and year-over-year changes

**Scraper**: `scrapers/ata_scraper.py`
**Database Table**: `macro_metrics`

⚠️ **Note**: May require manual verification as website structure changes.

---

### 6. BTS - Bureau of Transportation Statistics

**Source**: https://www.bts.gov/faf (Freight Analysis Framework)
**API**: No (direct CSV download)
**Update Frequency**: Annual (updated yearly with 5-year forecasts)

**Data Points:**
- Top freight lanes by origin-destination pairs
- Annual freight tonnage by lane
- Freight value by lane
- Mode of transportation breakdown (truck, rail, water, air, etc.)
- Commodity-specific freight flows

**What this gives you:**
- Identify the top 50-100 highest volume freight lanes in the US
- Understand which O-D pairs move the most freight
- Regional freight patterns and trade flows
- Lane volume rankings for strategic planning

**Scraper**: `scrapers/bts_scraper.py`
**Database Table**: `lanes.volume_rank`

⚠️ **Note**: Large file download (~500MB). Run infrequently (quarterly or semi-annually).

---

### 7. USASpending.gov - Government Freight Contracts

**Source**: https://www.usaspending.gov/
**API**: Yes (free, no key required)
**Update Frequency**: Daily (contracts updated continuously)

**Data Points:**
- Federal government freight contract awards
- Contract amounts and dates
- Origin and destination states
- Awarding agencies
- Recipient carriers

**What this gives you:**
- Benchmark pricing from government freight contracts
- Understanding of government freight spending patterns
- Contract vs spot market comparison data
- Geographic coverage of government freight

**PSC Codes Tracked:**
- V1: Trucking and motor freight
- V2: Freight forwarding

**Scraper**: `scrapers/usaspending_scraper.py`
**Database Tables**: `lanes`, `rates` (is_contract=True)

⚠️ **Note**: Contract amounts may not include per-mile rates. Use for benchmarking only.

---

## 🔄 Data Update Schedule

### Recommended Cron Jobs

```bash
# News - every 30 minutes
*/30 * * * * cd /home/phus/dev/poorfreight && venv/bin/python scrapers/news_scraper.py

# EIA Diesel - daily at 7am (updates Wednesdays)
0 7 * * * cd /home/phus/dev/poorfreight && venv/bin/python scrapers/eia_diesel_scraper.py

# FRED - daily at 8am
0 8 * * * cd /home/phus/dev/poorfreight && venv/bin/python scrapers/fred_scraper.py

# Cass & ATA - first of month at 9am
0 9 1 * * cd /home/phus/dev/poorfreight && venv/bin/python scrapers/cass_scraper.py
0 9 1 * * cd /home/phus/dev/poorfreight && venv/bin/python scrapers/ata_scraper.py

# BTS Lanes - quarterly (Jan 1, Apr 1, Jul 1, Oct 1) at 10am
0 10 1 1,4,7,10 * cd /home/phus/dev/poorfreight && venv/bin/python scrapers/bts_scraper.py

# USASpending - weekly on Mondays at 9am
0 9 * * 1 cd /home/phus/dev/poorfreight && venv/bin/python scrapers/usaspending_scraper.py

# Or run all daily (excluding BTS which should be manual/quarterly)
0 6 * * * cd /home/phus/dev/poorfreight && venv/bin/python scrapers/run_all_scrapers.py
```

---

## 📊 Data Coverage Summary

| Category | Sources | Metrics | Historical Data |
|----------|---------|---------|-----------------|
| **News** | 4 | Articles with tags | Real-time |
| **Fuel Prices** | EIA, FRED | Diesel, gas, crude oil | 1994-present |
| **Macro Freight** | Cass, ATA, FRED | 3 freight indices | 24 months |
| **Economy** | FRED | 5 indicators | Years of history |
| **Lanes & Geography** | BTS | Top 100 O-D pairs, volumes | Annual updates |
| **Contract Rates** | USASpending | Gov't contracts | 12 months rolling |
| **Total** | **11 sources** | **20+ metrics** | **Extensive** |

---

## 🎯 Data Quality

### Confidence Levels

- **EIA**: 1.0 (Official government data)
- **FRED**: 1.0 (Federal Reserve data)
- **BTS**: 1.0 (Official government data - Freight Analysis Framework)
- **USASpending**: 0.8 (Official gov't data, but limited freight-specific details)
- **Cass**: 0.9 (Scraped from official site, may need verification)
- **ATA**: 0.9 (Scraped from official site, may need verification)
- **News**: 1.0 (Direct RSS feeds)

### Data Freshness

Check the **Data Quality Monitor** page (coming soon) to see:
- Last successful scraper run
- Data freshness by source
- Scraper success/failure rates

---

## 🚀 Future Data Sources (Not Yet Implemented)

### High Priority
- [ ] **DAT Freight & Analytics** - Spot rates (requires paid subscription)
- [ ] **Truckstop.com** - Load board data (requires paid subscription)
- [ ] **FreightWaves SONAR** - Capacity indicators (limited free tier)

### Medium Priority
- [x] **BTS (Bureau of Transportation Statistics)** - Freight Analysis Framework ✅ IMPLEMENTED
- [x] **USASpending.gov** - Government contract rates ✅ IMPLEMENTED
- [ ] **State DOTs** - Regional freight plans and data

### Lower Priority
- [ ] **LTL Carrier APIs** - FedEx Freight, XPO, Estes quotes
- [ ] **Port Authorities** - LA/Long Beach, Savannah container volumes
- [ ] **Railroad Data** - STB (Surface Transportation Board) data

---

## 🔧 Adding New Data Sources

To add a new data source:

1. **Create scraper** in `scrapers/your_scraper.py`:
   ```python
   from scrapers.base_scraper import BaseScraper

   class YourScraper(BaseScraper):
       def fetch(self): ...
       def parse(self, raw_data): ...
       def store(self, parsed_data): ...
   ```

2. **Update database schema** in `lib/database.py`:
   - Add new columns to DailyMetric or MacroMetric
   - Run: `python lib/database.py` to update schema

3. **Add to run_all_scrapers.py**:
   ```python
   scrapers = [
       ...
       ("Your Source", YourScraper()),
   ]
   ```

4. **Test**:
   ```bash
   python scrapers/your_scraper.py
   ```

---

## 📝 API Keys

You have API keys configured in `.env`:
- ✅ `FRED_API_KEY` - For Federal Reserve data
- ✅ `EIA_API_KEY` - For energy/diesel data

Both are free to obtain:
- **FRED**: https://fred.stlouisfed.org/docs/api/api_key.html
- **EIA**: https://www.eia.gov/opendata/register.php

---

## 🎯 Usage in Portal

All this data flows into:
- **📰 News Intelligence** - Browse and analyze news
- **📈 Historical Analysis** - Visualize trends and correlations
- **🏠 Market Overview** (coming) - Current state snapshot

The portal automatically:
- Caches data for performance
- Shows data source attribution
- Indicates data freshness
- Handles missing data gracefully
