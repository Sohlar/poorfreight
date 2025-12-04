# Architecture Option 1: Python + FastAPI + Next.js

**Stack**: Modern SPA with Python backend, React frontend

---

## Overview

**Backend**: Python + FastAPI + SQLAlchemy
**Frontend**: Next.js (JavaScript) + React + TailwindCSS
**Communication**: REST API (JSON)

### When to Choose This:
- ✅ You want a modern, responsive single-page application
- ✅ You want the best interactive charts and data visualizations
- ✅ You're okay with learning some JavaScript (or have someone who knows it)
- ✅ You want the most "professional" looking dashboard

### Trade-offs:
- ⚠️ Two separate codebases (Python backend, JS frontend)
- ⚠️ Need to understand React basics
- ⚠️ More complex deployment (two services)
- ⚠️ Frontend build process required

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                        Browser                          │
│  ┌───────────────────────────────────────────────────┐ │
│  │         Next.js Frontend (JavaScript)             │ │
│  │  - React components                               │ │
│  │  - TailwindCSS styling                            │ │
│  │  - Recharts for visualizations                    │ │
│  │  - SWR for data fetching                          │ │
│  └───────────────────────────────────────────────────┘ │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP/JSON
                     │
┌────────────────────▼────────────────────────────────────┐
│              FastAPI Server (Python)                    │
│  ┌──────────────────────────────────────────────────┐  │
│  │              API Routes                          │  │
│  │  /api/lanes, /api/rates, /api/metrics, etc.     │  │
│  └──────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────┐  │
│  │           Business Logic Layer                   │  │
│  │  - Data aggregation                              │  │
│  │  - Confidence scoring                            │  │
│  │  - Rate calculations                             │  │
│  └──────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────┐  │
│  │          SQLAlchemy ORM                          │  │
│  │  - Models: Lane, Rate, Carrier, Metric, News    │  │
│  │  - Relationships and queries                     │  │
│  └──────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                  SQLite Database                        │
│  Tables: lanes, rates, carriers, metrics, news         │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│           Background Jobs (Python Scripts)              │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Scrapers (BeautifulSoup + requests)             │  │
│  │  - scrape_cass.py                                │  │
│  │  - scrape_ata.py                                 │  │
│  │  - scrape_dat.py                                 │  │
│  │  - scrape_news.py                                │  │
│  └──────────────────────────────────────────────────┘  │
│         Scheduled via cron or APScheduler              │
└─────────────────────────────────────────────────────────┘
```

---

## Tech Stack Details

### Backend: Python

#### Core Framework
```python
# requirements.txt
fastapi==0.104.1
uvicorn==0.24.0
sqlalchemy==2.0.23
pydantic==2.5.0
python-dotenv==1.0.0
```

#### Web Scraping
```python
beautifulsoup4==4.12.2
requests==2.31.0
lxml==4.9.3
playwright==1.40.0  # For JS-heavy sites (LTL quotes)
```

#### Data Processing
```python
pandas==2.1.3
numpy==1.26.2
```

#### Job Scheduling
```python
APScheduler==3.10.4  # Or use system cron
```

#### API Documentation
```python
# FastAPI has built-in Swagger UI at /docs
```

### Frontend: Next.js (JavaScript)

#### Core Framework
```json
{
  "dependencies": {
    "next": "14.0.3",
    "react": "18.2.0",
    "react-dom": "18.2.0"
  }
}
```

#### Styling & UI
```json
{
  "dependencies": {
    "tailwindcss": "3.3.5",
    "autoprefixer": "10.4.16",
    "postcss": "8.4.32"
  }
}
```

#### Charts & Visualization
```json
{
  "dependencies": {
    "recharts": "2.10.3",
    "react-leaflet": "4.2.1",  // For maps
    "leaflet": "1.9.4"
  }
}
```

#### Data Fetching
```json
{
  "dependencies": {
    "swr": "2.2.4",
    "axios": "1.6.2"
  }
}
```

---

## Project Structure

```
poorfreight/
├── backend/                      # Python FastAPI backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app entry point
│   │   ├── config.py            # Configuration
│   │   ├── database.py          # SQLAlchemy setup
│   │   │
│   │   ├── models/              # SQLAlchemy models
│   │   │   ├── __init__.py
│   │   │   ├── lane.py
│   │   │   ├── rate.py
│   │   │   ├── carrier.py
│   │   │   ├── metric.py
│   │   │   └── news.py
│   │   │
│   │   ├── schemas/             # Pydantic schemas (validation)
│   │   │   ├── __init__.py
│   │   │   ├── lane.py
│   │   │   ├── rate.py
│   │   │   └── metric.py
│   │   │
│   │   ├── routers/             # API route handlers
│   │   │   ├── __init__.py
│   │   │   ├── lanes.py         # /api/lanes
│   │   │   ├── rates.py         # /api/rates
│   │   │   ├── metrics.py       # /api/metrics
│   │   │   └── news.py          # /api/news
│   │   │
│   │   └── services/            # Business logic
│   │       ├── __init__.py
│   │       ├── rate_service.py
│   │       └── metrics_service.py
│   │
│   ├── scrapers/                # Data ingestion scripts
│   │   ├── __init__.py
│   │   ├── base_scraper.py     # Base class
│   │   ├── cass_scraper.py
│   │   ├── ata_scraper.py
│   │   ├── dat_scraper.py
│   │   ├── news_scraper.py
│   │   └── run_all.py          # Run all scrapers
│   │
│   ├── jobs/                    # Scheduled jobs
│   │   ├── scheduler.py         # APScheduler config
│   │   └── job_definitions.py
│   │
│   ├── alembic/                 # Database migrations
│   │   └── versions/
│   │
│   ├── data/                    # SQLite database location
│   │   └── freight.db
│   │
│   ├── requirements.txt
│   ├── .env
│   └── Dockerfile
│
├── frontend/                    # Next.js frontend
│   ├── app/                     # Next.js 14 App Router
│   │   ├── layout.js
│   │   ├── page.js              # Dashboard homepage
│   │   ├── lanes/
│   │   │   └── [origin]/
│   │   │       └── [destination]/
│   │   │           └── page.js  # Lane detail page
│   │   └── globals.css
│   │
│   ├── components/              # React components
│   │   ├── charts/
│   │   │   ├── TimeSeriesChart.js
│   │   │   ├── LineChart.js
│   │   │   └── HeatMap.js
│   │   ├── ui/
│   │   │   ├── MetricCard.js
│   │   │   ├── DataTable.js
│   │   │   └── FilterBar.js
│   │   └── layout/
│   │       ├── Sidebar.js
│   │       └── Header.js
│   │
│   ├── lib/                     # Utilities
│   │   ├── api.js               # API client + SWR hooks
│   │   ├── utils.js
│   │   └── constants.js
│   │
│   ├── public/                  # Static assets
│   │   └── images/
│   │
│   ├── package.json
│   ├── next.config.js
│   ├── tailwind.config.js
│   ├── .env.local
│   └── Dockerfile
│
└── docker-compose.yml           # Run both services
```

---

## Implementation Guide

### Step 1: Backend Setup

#### 1.1 Create FastAPI App

**`backend/app/main.py`**
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import lanes, rates, metrics, news
from app.database import engine, Base

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Freight Intelligence API",
    version="1.0.0",
    docs_url="/api/docs"
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(lanes.router, prefix="/api/lanes", tags=["lanes"])
app.include_router(rates.router, prefix="/api/rates", tags=["rates"])
app.include_router(metrics.router, prefix="/api/metrics", tags=["metrics"])
app.include_router(news.router, prefix="/api/news", tags=["news"])

@app.get("/")
def root():
    return {"message": "Freight Intelligence API"}

@app.get("/health")
def health():
    return {"status": "ok"}
```

#### 1.2 Database Models

**`backend/app/database.py`**
```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/freight.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # SQLite specific
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency for routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**`backend/app/models/lane.py`**
```python
from sqlalchemy import Column, Integer, String, Float
from app.database import Base

class Lane(Base):
    __tablename__ = "lanes"

    id = Column(Integer, primary_key=True, index=True)
    origin = Column(String, index=True)
    destination = Column(String, index=True)
    equipment_type = Column(String)  # 'van', 'reefer', 'flatbed'
    distance_miles = Column(Float)
    volume_rank = Column(Integer)  # From BTS FAF data
```

**`backend/app/models/rate.py`**
```python
from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.database import Base

class Rate(Base):
    __tablename__ = "rates"

    id = Column(Integer, primary_key=True, index=True)
    lane_id = Column(Integer, ForeignKey("lanes.id"), index=True)
    date = Column(Date, index=True)
    rate_per_mile = Column(Float)
    is_spot = Column(Boolean, default=True)
    is_contract = Column(Boolean, default=False)
    source = Column(String)  # 'DAT', 'USASpending', etc.
    confidence_score = Column(Float)  # 0.0 to 1.0

    lane = relationship("Lane", backref="rates")
```

#### 1.3 API Routes Example

**`backend/app/routers/lanes.py`**
```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.lane import Lane
from typing import List

router = APIRouter()

@router.get("/{origin}/{destination}")
def get_lane(origin: str, destination: str, db: Session = Depends(get_db)):
    lane = db.query(Lane).filter(
        Lane.origin == origin.upper(),
        Lane.destination == destination.upper()
    ).first()

    if not lane:
        return {"error": "Lane not found"}

    return {
        "data": {
            "origin": lane.origin,
            "destination": lane.destination,
            "distance_miles": lane.distance_miles,
            "equipment_type": lane.equipment_type
        }
    }
```

#### 1.4 Scraper Base Class

**`backend/scrapers/base_scraper.py`**
```python
from abc import ABC, abstractmethod
import requests
from bs4 import BeautifulSoup
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseScraper(ABC):
    def __init__(self, source_name: str):
        self.source = source_name
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'
        })

    @abstractmethod
    def fetch(self):
        """Fetch raw data from source"""
        pass

    @abstractmethod
    def parse(self, raw_data):
        """Parse raw data into structured format"""
        pass

    @abstractmethod
    def store(self, parsed_data):
        """Store parsed data in database"""
        pass

    def run(self, max_retries=3):
        """Main execution with retry logic"""
        for attempt in range(max_retries):
            try:
                logger.info(f"[{self.source}] Starting scrape (attempt {attempt + 1})")
                raw_data = self.fetch()
                parsed_data = self.parse(raw_data)
                self.store(parsed_data)
                logger.info(f"[{self.source}] Success! Stored {len(parsed_data)} records")
                return True
            except Exception as e:
                logger.error(f"[{self.source}] Error: {e}")
                if attempt < max_retries - 1:
                    time.sleep(5)  # Wait before retry
                else:
                    logger.error(f"[{self.source}] Failed after {max_retries} attempts")
                    return False
```

### Step 2: Frontend Setup

#### 2.1 API Client

**`frontend/lib/api.js`**
```javascript
import useSWR from 'swr'
import axios from 'axios'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

const fetcher = (url) => axios.get(url).then(res => res.data)

export function useLanes() {
  const { data, error } = useSWR(`${API_BASE}/api/lanes`, fetcher, {
    refreshInterval: 60000  // Refresh every minute
  })

  return {
    lanes: data?.data,
    isLoading: !error && !data,
    error
  }
}

export function useLaneRates(origin, destination) {
  const { data, error } = useSWR(
    `${API_BASE}/api/rates/spot?origin=${origin}&destination=${destination}`,
    fetcher
  )

  return {
    rates: data?.data,
    meta: data?.meta,
    isLoading: !error && !data,
    error
  }
}
```

#### 2.2 Dashboard Page

**`frontend/app/page.js`**
```javascript
'use client'

import { useLanes, useMacroMetrics } from '@/lib/api'
import MetricCard from '@/components/ui/MetricCard'
import TimeSeriesChart from '@/components/charts/TimeSeriesChart'

export default function Dashboard() {
  const { lanes, isLoading } = useLanes()
  const { metrics } = useMacroMetrics()

  if (isLoading) return <div>Loading...</div>

  return (
    <div className="p-6 bg-gray-900 min-h-screen">
      <h1 className="text-3xl font-bold text-white mb-6">
        Freight Intelligence Dashboard
      </h1>

      {/* KPI Cards */}
      <div className="grid grid-cols-4 gap-4 mb-8">
        <MetricCard
          title="Avg Spot Rate (Van)"
          value="$2.45"
          change="+3.2%"
          trend="up"
        />
        {/* More cards... */}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-2 gap-6">
        <TimeSeriesChart
          title="National Spot Rates"
          data={metrics}
          lines={['van', 'reefer', 'flatbed']}
        />
        {/* More charts... */}
      </div>
    </div>
  )
}
```

#### 2.3 Chart Component

**`frontend/components/charts/TimeSeriesChart.js`**
```javascript
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts'

export default function TimeSeriesChart({ title, data, lines }) {
  return (
    <div className="bg-gray-800 p-6 rounded-lg">
      <h3 className="text-xl text-white mb-4">{title}</h3>
      <LineChart width={600} height={300} data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="#444" />
        <XAxis dataKey="date" stroke="#888" />
        <YAxis stroke="#888" />
        <Tooltip
          contentStyle={{ backgroundColor: '#1f2937', border: 'none' }}
        />
        <Legend />
        {lines.map(line => (
          <Line
            key={line}
            type="monotone"
            dataKey={line}
            stroke={getColor(line)}
            strokeWidth={2}
          />
        ))}
      </LineChart>
    </div>
  )
}

function getColor(line) {
  const colors = {
    van: '#3b82f6',
    reefer: '#10b981',
    flatbed: '#f59e0b'
  }
  return colors[line] || '#888'
}
```

---

## Running the Application

### Development

**Terminal 1: Backend**
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**Terminal 2: Frontend**
```bash
cd frontend
npm install
npm run dev
```

Access at: `http://localhost:3000`
API docs at: `http://localhost:8000/api/docs`

### Production (Docker)

**`docker-compose.yml`**
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    volumes:
      - ./backend/data:/app/data
    environment:
      - DATABASE_URL=sqlite:///./data/freight.db

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://backend:8000
    depends_on:
      - backend
```

```bash
docker-compose up -d
```

---

## Pros & Cons

### Pros
✅ Modern, responsive UI with excellent charts
✅ Python backend = easy scraping and data processing
✅ FastAPI = automatic API documentation
✅ Next.js = great developer experience
✅ Separation of concerns (API can be used by other tools)

### Cons
❌ Two codebases to maintain
❌ Need to know both Python and JavaScript
❌ More complex deployment
❌ Frontend build process required
❌ CORS complexity during development

---

## When to Choose This Option

Choose Option 1 if:
- You want the most professional, modern dashboard
- You're willing to learn some React/JavaScript basics
- You plan to expand with mobile apps or other frontends later
- You want interactive, real-time charts with zoom/pan
- You value separation between data layer and presentation layer
