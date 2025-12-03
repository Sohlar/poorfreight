# Freight Intelligence Dashboard

A live, single-page freight market Business Intelligence dashboard that aggregates freight news, spot rates, diesel prices, and macro freight indices from free public data sources.

![Dashboard Preview](https://img.shields.io/badge/Status-Ready-green)

## Features

- **Live News Feed**: Aggregates articles from FreightWaves, Supply Chain Dive, Transport Topics, and JOC
- **Spot Rate Tracking**: Van, Reefer, and Flatbed national spot rate indices
- **Fuel Prices**: DOE diesel price tracking
- **Macro Indices**: Cass Shipments, ATA Tonnage, and FTR Trucking Conditions indices
- **Interactive Charts**: Time-series visualization with Recharts
- **Advanced Filtering**: Filter news by source, keywords, and date range
- **Dark Theme**: Modern, professional UI built with TailwindCSS
- **Real-time Updates**: Auto-refreshing data with SWR

## Tech Stack

### Backend
- **Node.js + Express + TypeScript**
- **SQLite** for data storage
- **RSS Parser** for news ingestion
- **Cheerio** for web scraping
- **Better-SQLite3** for database operations

### Frontend
- **Next.js 14** (App Router)
- **React 18 + TypeScript**
- **TailwindCSS** for styling
- **Recharts** for data visualization
- **SWR** for data fetching and caching

## Project Structure

```
poorfreight/
├── backend/
│   ├── src/
│   │   ├── db/
│   │   │   ├── connection.ts    # Database connection
│   │   │   ├── init.ts          # Schema initialization
│   │   │   └── models.ts        # Data models
│   │   ├── ingest/
│   │   │   ├── news.ts          # RSS feed ingestion
│   │   │   ├── daily.ts         # Daily metrics ingestion
│   │   │   └── macro.ts         # Macro metrics ingestion
│   │   ├── routes/
│   │   │   ├── news.ts          # News API endpoints
│   │   │   └── metrics.ts       # Metrics API endpoints
│   │   ├── types/
│   │   │   └── index.ts         # TypeScript types
│   │   └── server.ts            # Express server
│   ├── data/                    # SQLite database (auto-created)
│   └── package.json
├── frontend/
│   ├── app/
│   │   ├── page.tsx             # Main dashboard
│   │   ├── layout.tsx           # Root layout
│   │   └── globals.css          # Global styles
│   ├── components/
│   │   ├── KpiCard.tsx          # Metric card component
│   │   ├── TimeSeriesChart.tsx  # Chart component
│   │   ├── NewsList.tsx         # News list component
│   │   └── FiltersBar.tsx       # Filters component
│   ├── lib/
│   │   ├── api.ts               # API client with SWR hooks
│   │   ├── types.ts             # TypeScript types
│   │   └── utils.ts             # Utility functions
│   └── package.json
└── README.md
```

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd poorfreight
   ```

2. **Set up the backend**
   ```bash
   cd backend
   npm install

   # Copy environment file
   cp .env.example .env

   # Initialize database
   npm run db:init

   # Run data ingestion
   npm run ingest:all
   ```

3. **Set up the frontend**
   ```bash
   cd ../frontend
   npm install

   # Copy environment file
   cp .env.example .env
   ```

### Running the Application

You'll need two terminal windows:

**Terminal 1 - Backend API Server:**
```bash
cd backend
npm run dev
```
The API will be available at `http://localhost:3001`

**Terminal 2 - Frontend Development Server:**
```bash
cd frontend
npm run dev
```
The dashboard will be available at `http://localhost:3000`

### Data Ingestion

The app requires data to be loaded into the database. You can run ingestion scripts manually:

```bash
cd backend

# Ingest all data sources
npm run ingest:all

# Or ingest individually
npm run ingest:news      # Fetch RSS feeds
npm run ingest:daily     # Fetch diesel prices and generate spot rates
npm run ingest:macro     # Generate macro metrics
```

**Recommended Schedule:**
- News: Every 15-30 minutes
- Daily metrics: Once per day
- Macro metrics: Once per month

You can set up cron jobs or use a task scheduler to automate this.

## API Endpoints

### News
- `GET /api/news` - Get news articles
  - Query params: `source`, `q`, `days`, `limit`, `offset`
- `GET /api/news/sources` - Get available news sources

### Metrics
- `GET /api/metrics/daily` - Get daily metrics (spot rates, diesel)
  - Query params: `from`, `to` (YYYY-MM-DD)
- `GET /api/metrics/daily/latest` - Get latest metrics with changes
- `GET /api/metrics/macro` - Get macro freight indices
  - Query params: `from`, `to` (YYYY-MM)

### Health
- `GET /health` - Health check endpoint

## Data Sources

### News (RSS Feeds)
- **FreightWaves**: https://www.freightwaves.com/feed
- **Supply Chain Dive**: https://www.supplychaindive.com/feeds/news/
- **Transport Topics**: https://www.ttnews.com/rss/feed/top-news
- **JOC**: https://www.joc.com/rss/all-categories

### Daily Metrics
- **Diesel Prices**: EIA (U.S. Energy Information Administration)
- **Spot Rates**: Currently using synthetic data for demonstration
  - For production, integrate with DAT, Truckstop.com, or similar APIs

### Macro Indices
- **Cass Freight Index**: Cass Information Systems
- **ATA Truck Tonnage Index**: American Trucking Associations
- **FTR Trucking Conditions Index**: FTR Transportation Intelligence
- Note: Currently using synthetic data for demonstration

## Configuration

### Backend Environment Variables
Create `backend/.env`:
```env
PORT=3001
NODE_ENV=development
DATABASE_PATH=./data/freight.db
EIA_API_KEY=optional_your_eia_api_key_here
```

### Frontend Environment Variables
Create `frontend/.env`:
```env
NEXT_PUBLIC_API_URL=http://localhost:3001
```

## Production Deployment

### Backend
```bash
cd backend
npm run build
npm start
```

### Frontend
```bash
cd frontend
npm run build
npm start
```

For production deployment, consider:
- Using a process manager like PM2 for the backend
- Deploying frontend to Vercel, Netlify, or similar
- Setting up a proper database (PostgreSQL) for production scale
- Implementing proper authentication if needed
- Setting up automated data ingestion with cron jobs or scheduled tasks
- Using environment-specific configuration

## Development Notes

### Replacing Synthetic Data

The current implementation uses synthetic data for spot rates and macro indices. To use real data:

1. **Spot Rates**:
   - Sign up for DAT or Truckstop.com API access
   - Update `backend/src/ingest/daily.ts` to fetch real data

2. **Macro Indices**:
   - Implement web scrapers for Cass, ATA, and FTR websites
   - Update `backend/src/ingest/macro.ts` with scraping logic

3. **Diesel Prices**:
   - Already scraping from EIA website
   - Optionally use EIA API with an API key for more reliable access

### Adding New Data Sources

To add a new RSS feed:
1. Add the source to `backend/src/ingest/news.ts` in the `RSS_SOURCES` array
2. Update the sources list in `backend/src/routes/news.ts`

### Customization

- **Colors**: Modify `frontend/tailwind.config.ts`
- **Chart styling**: Update `frontend/components/TimeSeriesChart.tsx`
- **Refresh intervals**: Adjust in `frontend/lib/api.ts` SWR configurations

## Troubleshooting

### Backend won't start
- Ensure port 3001 is available
- Check that SQLite database was initialized: `npm run db:init`
- Verify all dependencies are installed: `npm install`

### Frontend shows "No data available"
- Ensure backend is running on port 3001
- Run data ingestion: `npm run ingest:all` in backend directory
- Check browser console for API errors

### Charts not rendering
- Verify data is being returned from API endpoints
- Check browser console for JavaScript errors
- Ensure Recharts is properly installed: `npm install recharts`

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and questions, please open an issue on GitHub.
