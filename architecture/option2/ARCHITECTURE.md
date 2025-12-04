# Architecture Option 2: Python + FastAPI + Jinja2 Templates + HTMX

**Stack**: Traditional server-rendered web app with modern interactivity

---

## Overview

**Backend**: Python + FastAPI + SQLAlchemy + Jinja2 Templates
**Frontend**: HTML Templates + TailwindCSS + HTMX + Chart.js
**Communication**: Server renders HTML, HTMX for dynamic updates

### When to Choose This:
- ✅ You want to stay in Python as much as possible
- ✅ You prefer traditional web development (server-rendered pages)
- ✅ You want minimal JavaScript complexity
- ✅ You value simplicity over cutting-edge UI
- ✅ You're comfortable with template engines (like Django templates)

### Trade-offs:
- ⚠️ Less "SPA feel" than Option 1
- ⚠️ Charts are simpler (Chart.js vs Recharts)
- ⚠️ Harder to add very complex interactivity
- ⚠️ Page refreshes on some navigation
- ✅ But: Single codebase, mostly Python, simpler deployment

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                        Browser                          │
│  ┌───────────────────────────────────────────────────┐ │
│  │          HTML + TailwindCSS + Chart.js            │ │
│  │  - Server-rendered Jinja2 templates               │ │
│  │  - HTMX for dynamic updates (no page reload)      │ │
│  │  - Chart.js for visualizations                    │ │
│  │  - Alpine.js for small interactions               │ │
│  └───────────────────────────────────────────────────┘ │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP/HTML (HTMX uses AJAX)
                     │
┌────────────────────▼────────────────────────────────────┐
│              FastAPI Server (Python)                    │
│  ┌──────────────────────────────────────────────────┐  │
│  │           Template Routes                        │  │
│  │  - GET / → renders dashboard.html                │  │
│  │  - GET /lanes/{origin}/{dest} → lane.html        │  │
│  │  - Jinja2 template engine                        │  │
│  └──────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────┐  │
│  │           API Routes (for HTMX)                  │  │
│  │  - GET /api/rates → returns HTML fragment        │  │
│  │  - GET /api/metrics → returns chart data         │  │
│  └──────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────┐  │
│  │          Business Logic & ORM                    │  │
│  │  - SQLAlchemy models                             │  │
│  │  - Data aggregation                              │  │
│  └──────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                  SQLite Database                        │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│           Background Jobs (same as Option 1)            │
│  Python scraper scripts scheduled via cron              │
└─────────────────────────────────────────────────────────┘
```

---

## Tech Stack Details

### Backend: Python

```python
# requirements.txt
fastapi==0.104.1
uvicorn==0.24.0
sqlalchemy==2.0.23
jinja2==3.1.2
python-multipart==0.0.6  # For form handling

# Scraping (same as Option 1)
beautifulsoup4==4.12.2
requests==2.31.0
playwright==1.40.0

# Data processing
pandas==2.1.3
```

### Frontend: Templates + Minimal JS

**No npm/build process needed!** Just CDN links:

```html
<!-- TailwindCSS -->
<script src="https://cdn.tailwindcss.com"></script>

<!-- HTMX for dynamic updates -->
<script src="https://unpkg.com/htmx.org@1.9.10"></script>

<!-- Alpine.js for small interactions -->
<script src="https://cdn.jsdelivr.net/npm/alpinejs@3.13.3/dist/cdn.min.js"></script>

<!-- Chart.js for visualizations -->
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
```

---

## Project Structure

```
poorfreight/
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI app entry point
│   ├── config.py
│   ├── database.py
│   │
│   ├── models/                  # SQLAlchemy models (same as Option 1)
│   │   ├── __init__.py
│   │   ├── lane.py
│   │   ├── rate.py
│   │   └── ...
│   │
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── pages.py             # Template routes (GET /)
│   │   └── api.py               # API endpoints for HTMX
│   │
│   ├── services/                # Business logic
│   │   ├── rate_service.py
│   │   └── ...
│   │
│   ├── templates/               # Jinja2 HTML templates
│   │   ├── base.html            # Base layout
│   │   ├── dashboard.html       # Main dashboard
│   │   ├── lanes/
│   │   │   └── detail.html      # Lane detail page
│   │   ├── components/
│   │   │   ├── metric_card.html
│   │   │   ├── chart.html
│   │   │   └── table.html
│   │   └── partials/            # HTMX fragments
│   │       ├── rate_table.html
│   │       └── news_feed.html
│   │
│   └── static/                  # Static files
│       ├── css/
│       │   └── custom.css       # Custom styles
│       └── js/
│           ├── charts.js        # Chart.js configs
│           └── utils.js
│
├── scrapers/                    # Same as Option 1
│   ├── base_scraper.py
│   ├── cass_scraper.py
│   └── ...
│
├── data/
│   └── freight.db
│
├── requirements.txt
├── .env
└── Dockerfile
```

---

## Implementation Guide

### Step 1: FastAPI with Templates

**`app/main.py`**
```python
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.routers import pages, api
from app.database import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI()

# Serve static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="app/templates")

# Include routers
app.include_router(pages.router)  # Template pages
app.include_router(api.router, prefix="/api")  # HTMX endpoints

@app.get("/health")
def health():
    return {"status": "ok"}
```

**`app/routers/pages.py`**
```python
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.metric import Metric
from app.models.lane import Lane

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    # Fetch latest metrics
    latest_metrics = db.query(Metric).order_by(Metric.date.desc()).limit(90).all()
    top_lanes = db.query(Lane).limit(10).all()

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "metrics": latest_metrics,
        "lanes": top_lanes,
        "page_title": "Freight Dashboard"
    })

@router.get("/lanes/{origin}/{destination}", response_class=HTMLResponse)
async def lane_detail(
    request: Request,
    origin: str,
    destination: str,
    db: Session = Depends(get_db)
):
    lane = db.query(Lane).filter(
        Lane.origin == origin.upper(),
        Lane.destination == destination.upper()
    ).first()

    return templates.TemplateResponse("lanes/detail.html", {
        "request": request,
        "lane": lane,
        "origin": origin,
        "destination": destination
    })
```

**`app/routers/api.py`** (for HTMX updates)
```python
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.rate import Rate

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/rates", response_class=HTMLResponse)
async def get_rates_fragment(
    request: Request,
    origin: str = None,
    destination: str = None,
    db: Session = Depends(get_db)
):
    """Returns HTML fragment for HTMX to inject"""
    query = db.query(Rate)

    if origin:
        query = query.filter(Rate.lane.has(origin=origin.upper()))
    if destination:
        query = query.filter(Rate.lane.has(destination=destination.upper()))

    rates = query.order_by(Rate.date.desc()).limit(50).all()

    return templates.TemplateResponse("partials/rate_table.html", {
        "request": request,
        "rates": rates
    })
```

### Step 2: Templates

**`app/templates/base.html`**
```html
<!DOCTYPE html>
<html lang="en" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Freight Intelligence{% endblock %}</title>

    <!-- TailwindCSS -->
    <script src="https://cdn.tailwindcss.com"></script>

    <!-- HTMX -->
    <script src="https://unpkg.com/htmx.org@1.9.10"></script>

    <!-- Alpine.js -->
    <script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.13.3/dist/cdn.min.js"></script>

    <!-- Chart.js -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>

    <link rel="stylesheet" href="/static/css/custom.css">
</head>
<body class="bg-gray-900 text-gray-100">
    <div class="flex">
        <!-- Sidebar -->
        <aside class="w-64 bg-gray-800 min-h-screen p-4">
            <h1 class="text-xl font-bold mb-8">Freight Intel</h1>
            <nav>
                <a href="/" class="block py-2 px-4 hover:bg-gray-700 rounded">Dashboard</a>
                <a href="/lanes" class="block py-2 px-4 hover:bg-gray-700 rounded">Lanes</a>
                <a href="/capacity" class="block py-2 px-4 hover:bg-gray-700 rounded">Capacity</a>
                <a href="/news" class="block py-2 px-4 hover:bg-gray-700 rounded">News</a>
            </nav>
        </aside>

        <!-- Main content -->
        <main class="flex-1 p-8">
            {% block content %}{% endblock %}
        </main>
    </div>

    {% block scripts %}{% endblock %}
</body>
</html>
```

**`app/templates/dashboard.html`**
```html
{% extends "base.html" %}

{% block content %}
<h2 class="text-3xl font-bold mb-6">Freight Market Dashboard</h2>

<!-- KPI Cards -->
<div class="grid grid-cols-4 gap-4 mb-8">
    {% include "components/metric_card.html" with title="Avg Van Rate" value="$2.45" change="+3.2%" %}
    {% include "components/metric_card.html" with title="Diesel ($/gal)" value="$3.89" change="-1.5%" %}
    <!-- More cards... -->
</div>

<!-- Charts -->
<div class="grid grid-cols-2 gap-6 mb-8">
    <div class="bg-gray-800 p-6 rounded-lg">
        <h3 class="text-xl mb-4">National Spot Rates</h3>
        <canvas id="spotRatesChart"></canvas>
    </div>

    <div class="bg-gray-800 p-6 rounded-lg">
        <h3 class="text-xl mb-4">Capacity Indicators</h3>
        <canvas id="capacityChart"></canvas>
    </div>
</div>

<!-- Live Data Table (updates via HTMX) -->
<div class="bg-gray-800 p-6 rounded-lg">
    <h3 class="text-xl mb-4">Recent Rates</h3>

    <!-- This div will auto-refresh every 30 seconds -->
    <div hx-get="/api/rates" hx-trigger="load, every 30s" hx-swap="innerHTML">
        Loading rates...
    </div>
</div>
{% endblock %}

{% block scripts %}
<script>
// Chart.js configuration
const spotRatesData = {{ metrics | tojson }};

const ctx = document.getElementById('spotRatesChart').getContext('2d');
new Chart(ctx, {
    type: 'line',
    data: {
        labels: spotRatesData.map(m => m.date),
        datasets: [{
            label: 'Van',
            data: spotRatesData.map(m => m.van_rate),
            borderColor: '#3b82f6',
            tension: 0.1
        }, {
            label: 'Reefer',
            data: spotRatesData.map(m => m.reefer_rate),
            borderColor: '#10b981',
            tension: 0.1
        }]
    },
    options: {
        responsive: true,
        plugins: {
            legend: { labels: { color: '#fff' } }
        },
        scales: {
            x: { ticks: { color: '#888' }, grid: { color: '#444' } },
            y: { ticks: { color: '#888' }, grid: { color: '#444' } }
        }
    }
});
</script>
{% endblock %}
```

**`app/templates/components/metric_card.html`**
```html
<div class="bg-gray-800 p-6 rounded-lg">
    <p class="text-gray-400 text-sm">{{ title }}</p>
    <p class="text-3xl font-bold mt-2">{{ value }}</p>
    <p class="text-sm mt-2 {% if change.startswith('+') %}text-green-400{% else %}text-red-400{% endif %}">
        {{ change }}
    </p>
</div>
```

**`app/templates/partials/rate_table.html`** (HTMX fragment)
```html
<table class="w-full">
    <thead>
        <tr class="border-b border-gray-700">
            <th class="text-left py-2">Lane</th>
            <th class="text-left py-2">Rate/Mile</th>
            <th class="text-left py-2">Date</th>
            <th class="text-left py-2">Source</th>
        </tr>
    </thead>
    <tbody>
        {% for rate in rates %}
        <tr class="border-b border-gray-800 hover:bg-gray-700">
            <td class="py-3">{{ rate.lane.origin }} → {{ rate.lane.destination }}</td>
            <td class="py-3">${{ "%.2f"|format(rate.rate_per_mile) }}</td>
            <td class="py-3">{{ rate.date }}</td>
            <td class="py-3">
                <span class="px-2 py-1 bg-blue-900 text-blue-200 rounded text-xs">
                    {{ rate.source }}
                </span>
            </td>
        </tr>
        {% endfor %}
    </tbody>
</table>
```

### Step 3: HTMX Interactivity

HTMX allows dynamic updates without writing JavaScript:

```html
<!-- Search lane rates dynamically -->
<div x-data="{ origin: '', destination: '' }">
    <input
        type="text"
        placeholder="Origin"
        x-model="origin"
        hx-get="/api/rates"
        hx-trigger="keyup changed delay:500ms"
        hx-vals="js:{origin: document.querySelector('[x-model=origin]').value}"
        hx-target="#rate-results"
        hx-swap="innerHTML"
        class="px-4 py-2 bg-gray-700 rounded"
    />

    <input
        type="text"
        placeholder="Destination"
        x-model="destination"
        class="px-4 py-2 bg-gray-700 rounded ml-2"
    />

    <div id="rate-results" class="mt-4">
        <!-- Results appear here -->
    </div>
</div>
```

---

## Running the Application

### Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run server
uvicorn app.main:app --reload --port 8000

# Access at http://localhost:8000
```

### Production
```bash
# Simple Docker
docker build -t freight-app .
docker run -p 8000:8000 -v ./data:/app/data freight-app
```

---

## Pros & Cons

### Pros
✅ **Single codebase** - all Python (except minimal HTML/CSS)
✅ **Simple deployment** - one container, one process
✅ **No build process** - no npm, no webpack, no complexity
✅ **Fast development** - change template, refresh browser
✅ **SEO friendly** - server-rendered HTML
✅ **Works without JavaScript** (degrades gracefully)
✅ **Familiar** - if you know Django/Flask templates, this is similar

### Cons
❌ Less "app-like" feel than React SPA
❌ Some page refreshes on navigation
❌ Chart.js less powerful than Recharts
❌ Harder to build very complex interactions
❌ Can't easily build mobile app later (would need separate frontend)

---

## When to Choose This Option

Choose Option 2 if:
- You want to stay in Python as much as possible
- You prefer traditional web development patterns
- You value simplicity over cutting-edge UI
- You're comfortable with template engines
- You don't need complex client-side state management
- You want fast development iteration
- You're building for internal use (not external product)

**This is the "pragmatic Python developer" choice.**
