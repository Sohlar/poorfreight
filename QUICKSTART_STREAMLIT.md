# Freight Intelligence Portal - Quick Start

## Setup (First Time Only)

```bash
# Run setup script
./setup.sh

# Or manually:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python lib/database.py  # Initialize database
```

## Running the Portal

```bash
# Activate virtual environment
source venv/bin/activate

# Run Streamlit app
streamlit run app.py

# Portal will open at http://localhost:8501
```

## Project Structure

```
poorfreight/
├── app.py                    # Main Streamlit app (homepage)
├── pages/                    # Multi-page app pages
│   ├── 1_🏠_Market_Overview.py
│   ├── 2_📰_News_Intelligence.py
│   ├── 3_📈_Historical_Analysis.py
│   ├── 4_🚛_Lane_Intelligence.py
│   ├── 5_📊_Strategic_Reports.py
│   └── 6_⚙️_Data_Quality.py
├── lib/                      # Core library
│   ├── database.py           # Database models & connection
│   └── utils.py              # Helper functions
├── scrapers/                 # Data ingestion
│   ├── base_scraper.py
│   ├── news_scraper.py
│   ├── cass_scraper.py
│   └── ...
├── data/                     # SQLite database
│   └── freight.db
├── requirements.txt
└── .streamlit/
    └── config.toml           # Dark theme config
```

## Next Steps

1. **Run scrapers to populate data**:
   ```bash
   python scrapers/news_scraper.py
   ```

2. **Open portal**: http://localhost:8501

3. **Navigate pages** using sidebar

4. **Schedule scrapers** with cron for auto-updates

## Development Workflow

1. Edit Python files
2. Streamlit auto-reloads on file save
3. Refresh browser to see changes
4. Iterate fast!

## Troubleshooting

**Port already in use**:
```bash
streamlit run app.py --server.port 8502
```

**Database errors**:
```bash
rm data/freight.db
python lib/database.py  # Reinitialize
```

**Missing dependencies**:
```bash
pip install -r requirements.txt
```
