# Quick Start Guide

Get the Freight Intelligence Dashboard running in 3 minutes.

## First Time Setup

```bash
# 1. Install backend dependencies
cd backend
npm install

# 2. Initialize database
npm run db:init

# 3. Load initial data
npm run ingest:all

# 4. Install frontend dependencies
cd ../frontend
npm install
```

## Running the App

Open two terminal windows:

**Terminal 1 - Backend:**
```bash
cd backend
npm run dev
```
Backend will be available at http://localhost:3001

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```
Frontend will be available at http://localhost:3000

## Updating Data

To refresh the data:

```bash
cd backend

# Refresh all data
npm run ingest:all

# Or individually
npm run ingest:news      # Refresh news articles
npm run ingest:daily     # Refresh spot rates and diesel prices
npm run ingest:macro     # Refresh macro indices
```

## Troubleshooting

**Backend won't start:**
- Check port 3001 is available: `lsof -i :3001`
- Verify database exists: `ls backend/data/`

**Frontend shows "No data":**
- Ensure backend is running: `curl http://localhost:3001/health`
- Verify data was loaded: `npm run ingest:all` in backend directory

**Build errors:**
- Clear node_modules: `rm -rf node_modules package-lock.json && npm install`
- Clear Next.js cache: `rm -rf .next`

## Production Build

```bash
# Backend
cd backend
npm run build
npm start

# Frontend
cd frontend
npm run build
npm start
```

## Features

- **Live News**: Aggregated freight industry news from multiple sources
- **Spot Rates**: Van, Reefer, and Flatbed rate tracking
- **Fuel Prices**: DOE diesel price monitoring
- **Macro Trends**: Cass, ATA, and FTR freight indices
- **Filtering**: Filter news by source, keyword, and date range
- **Charts**: Interactive time-series visualizations

## API Endpoints

- `GET /health` - Health check
- `GET /api/news?source=&q=&days=` - Get news articles
- `GET /api/news/sources` - Get available sources
- `GET /api/metrics/daily?from=&to=` - Get daily metrics
- `GET /api/metrics/daily/latest` - Get latest metrics with changes
- `GET /api/metrics/macro?from=&to=` - Get macro metrics

## Next Steps

1. Set up automated data ingestion (cron jobs)
2. Replace synthetic spot rate data with real DAT/Truckstop API
3. Implement proper web scraping for macro indices
4. Add authentication if deploying publicly
5. Set up monitoring and alerting

For more details, see [README.md](./README.md)
