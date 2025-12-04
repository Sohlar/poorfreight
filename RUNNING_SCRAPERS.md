# Running Data Scrapers

## Quick Start - Run All Scrapers

```bash
# Make sure you're in the virtual environment
source venv/bin/activate

# Run all scrapers at once
python scrapers/run_all_scrapers.py
```

This will run:
1. News scraper (FreightWaves, Supply Chain Dive, Transport Topics, JOC)
2. Cass Freight Index scraper
3. ATA Truck Tonnage Index scraper

---

## Running Individual Scrapers

### News Scraper
```bash
python scrapers/news_scraper.py
```
- Fetches latest freight news from 4 sources
- Auto-tags articles (capacity, rates, diesel, ltl, ftl, etc.)
- Auto-rates importance (1-5 stars)
- Extracts full article content when possible

### Cass Freight Index
```bash
python scrapers/cass_scraper.py
```
- Scrapes Cass Shipments & Expenditures indices
- Source: https://www.cassinfo.com/freight-audit-indexes
- ⚠️ May require manual verification

### ATA Truck Tonnage Index
```bash
python scrapers/ata_scraper.py
```
- Scrapes ATA Truck Tonnage Index from press releases
- Source: https://www.trucking.org/news-insights/ata-truck-tonnage-index
- ⚠️ May require manual verification

---

## Scraper Output

Each scraper will:
- Log progress to console
- Track execution in `scraper_runs` database table
- Store data in appropriate tables
- Retry 3 times on failure
- Report success/failure at end

---

## Automation

### Option 1: System Cron

Edit crontab:
```bash
crontab -e
```

Add these lines:
```cron
# Run news scraper every 30 minutes
*/30 * * * * cd /home/phus/dev/poorfreight && venv/bin/python scrapers/news_scraper.py

# Run macro scrapers once daily at 6am
0 6 * * * cd /home/phus/dev/poorfreight && venv/bin/python scrapers/cass_scraper.py
0 6 * * * cd /home/phus/dev/poorfreight && venv/bin/python scrapers/ata_scraper.py

# Or run all scrapers daily
0 6 * * * cd /home/phus/dev/poorfreight && venv/bin/python scrapers/run_all_scrapers.py
```

### Option 2: APScheduler (Future)

Will add Python-based scheduler for more control.

---

## Troubleshooting

### No data appearing

1. Check scraper logs - look for errors
2. Some scrapers may need manual verification (Cass, ATA websites change)
3. Check database: `sqlite3 data/freight.db`
   ```sql
   SELECT COUNT(*) FROM news_articles;
   SELECT COUNT(*) FROM macro_metrics;
   ```

### Scraper fails

- Check internet connection
- Website may have changed structure - needs manual update
- Check scraper_runs table for error messages
- Run with `-v` flag for verbose logging (if added)

### Data seems wrong

- Cass and ATA scrapers parse press releases - website changes may break parsing
- Manually verify data against source websites
- Update scraper parsing logic if needed

---

## Next Steps

After running scrapers:
1. Launch portal: `streamlit run app.py`
2. View News Intelligence page to see articles
3. Build Historical Analysis page to visualize macro data
4. Setup cron for automatic updates

---

## Scraper Status

| Scraper | Status | Data Source | Frequency |
|---------|--------|-------------|-----------|
| News | ✅ Working | RSS feeds | Every 30min |
| Cass | ⚠️ Needs verification | Press releases | Monthly |
| ATA | ⚠️ Needs verification | Press releases | Monthly |
| DAT | ❌ Not yet built | TBD | TBD |
| FRED | ❌ Not yet built | API | Daily |

