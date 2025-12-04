# Freight Intelligence Platform - Pragmatic Roadmap

**Vision**: Internal freight intelligence tool with real data and actionable insights

**Engineering Philosophy**:
- ✅ **Build it right once** - Design data models and APIs that won't need refactoring
- ✅ **Appropriate complexity** - Internal tool, not enterprise SaaS. Keep it simple.
- ✅ **Quality over perfection** - Clean code, but pragmatic choices
- ✅ **Extensible by default** - Easy to add features without breaking existing code
- ⛔ **Refactors = Death** - Think through architecture before coding

---

## Phase 0: Smart Architecture (Week 1)

**Goal**: Design the foundation so we never have to refactor

**See `/architecture/` directory for detailed implementation options.**

### Database Design (Do It Right Once)
- [ ] **Design complete schema upfront**
  - Lanes table (origin, destination, equipment_type, service_type)
  - Rates table (lane_id, rate, date, source, confidence_score, is_spot vs is_contract)
  - Carriers table (name, mc_number, dot_number, status)
  - Metrics table (date/month, metric_type, value, source)
  - News table (existing, but review if complete)

- [ ] **Key architectural decisions**:
  - SQLite is fine for internal use (can handle millions of rows)
  - Add proper indexes on common queries (date ranges, lane lookups)
  - Use views for complex aggregations
  - JSON/JSONB columns for flexible metadata where needed
  - Decide on soft deletes vs hard deletes now

### API Design (Future-Proof Contracts)
- [ ] **Define URL structure** (won't change later)
  ```
  /api/lanes                          # List all lanes
  /api/lanes/:origin/:destination     # Specific lane
  /api/rates/spot                     # Spot rates (filterable by lane, date)
  /api/rates/contract                 # Contract rates
  /api/metrics/macro                  # Macro indices
  /api/metrics/capacity               # Capacity indicators
  /api/news                           # News feed
  ```

- [ ] **Query parameter standards**
  - Consistent filtering: ?origin=LAX&destination=ORD&from=2024-01-01&to=2024-12-31
  - Pagination: ?page=1&limit=50 (simple offset for internal tool)
  - Sorting: ?sort=date&order=desc

- [ ] **Response format standards**
  ```json
  {
    "data": [...],
    "meta": {
      "source": "DAT",
      "confidence": 0.85,
      "timestamp": "2024-12-03T10:00:00Z"
    }
  }
  ```

### Data Ingestion Framework
- [ ] **Build reusable scraper base class**
  - Standard interface: fetch() → parse() → store()
  - Common retry logic and error handling
  - Logging and monitoring hooks
  - Idempotency guarantees

- [ ] **Job scheduling setup**
  - Automated scheduling (cron or equivalent)
  - Separate scripts for different frequencies
  - Basic logging to file/console

### Frontend Component Architecture
- [ ] **Establish component patterns**
  - Chart wrapper component (handles all time-series charts)
  - Data table component (handles all tabular data)
  - Metric card component (KPIs)
  - Filter bar component (reusable across views)

- [ ] **State management decision**
  - Server state management approach
  - URL params for filter state (shareable links)
  - Local state where needed

### Success Criteria
- Can add any new lane without schema changes
- Can add new data sources without breaking existing
- API endpoints won't need versioning for foreseeable features
- Components are reusable across all planned views

---

## Phase 1: Remove Fake Data & Core Real Data (Week 2)

**Goal**: Replace all synthetic data with real free sources

### Immediate Cleanup
- [ ] Delete `backend/src/ingest/daily.ts:76-115` (synthetic spot rates)
- [ ] Delete `backend/src/ingest/macro.ts:16-57` (synthetic macro indices)
- [ ] Update UI to show "Data Unavailable" instead of fake data

### Real Macro Indices (All Free)
- [ ] **Cass Freight Index** scraper
  - https://www.cassinfo.com/freight-audit-indexes
  - Monthly press release (HTML scraping)
  - Extract: Shipments Index, Expenditures Index, commentary

- [ ] **ATA Truck Tonnage** scraper
  - https://www.trucking.org/news-insights/ata-truck-tonnage-index
  - Monthly press release
  - Extract: Tonnage Index, MoM %, YoY %

- [ ] **DAT Trendlines** scraper
  - https://www.dat.com/industry-trends/trendlines
  - Weekly updates with national averages
  - Extract: Van/Reefer/Flatbed rates, Load-to-truck ratios

### Economic Indicators
- [ ] **FRED API integration** (free, official API)
  - ISM Manufacturing PMI
  - Retail Sales
  - Industrial Production
  - Setup API key, rate limiting

### Enhanced Fuel Data
- [ ] **Regional diesel prices** (EIA has state-level data)
  - Expand existing scraper to capture state breakdowns
  - Store in metrics table with region dimension

### Automation
- [ ] **Setup cron jobs** (simple node-cron)
  - News: Every 30 minutes
  - Daily metrics: Once daily at 6am
  - Macro metrics: First of month + manual trigger

---

## Phase 2: Lane Intelligence (Weeks 3-4)

**Goal**: Add geographic granularity and lane-specific data

### Lane Framework
- [ ] **BTS Freight Analysis Framework** parser
  - Download FAF data (free Excel/CSV files)
  - One-time import of top lanes by volume
  - Identify top 50 lanes to prioritize

- [ ] **Implement lane-based data model**
  - Populate lanes table with top 50 O-D pairs
  - Add metro area reference table
  - Regional aggregation logic

### Government Contract Rates
- [ ] **USASpending.gov scraper**
  - API access (free, no key needed)
  - Filter for freight-related contracts
  - Extract: lane, rate, date, shipper
  - Store in rates table with source="USASpending"

### UI Updates
- [ ] **Lane selector component**
  - Dropdown with autocomplete
  - Recent/favorite lanes
  - Direct URL: `/lanes/LAX/ORD`

- [ ] **Geographic heat map**
  - US map with regional rate coloring
  - Click to drill into region
  - Simple SVG or Leaflet.js

---

## Phase 3: LTL Coverage (Weeks 5-6)

**Goal**: Add LTL rate intelligence

### LTL Quote Scrapers
- [ ] **Build quote scraper framework**
  - Puppeteer for JavaScript-heavy sites
  - Rate limiting per carrier
  - Sample quotes for top 50 lanes weekly

- [ ] **Carrier quote scrapers**
  - FedEx Freight instant quote tool
  - XPO LTL quote page
  - Estes Express Lines
  - (Start with top 3, expand as needed)

### LTL Data Model
- [ ] **Add LTL-specific fields**
  - Weight class (LTL vs FTL)
  - Per-CWT pricing
  - Minimum charge
  - Fuel surcharge component
  - Transit time estimates

### UI for LTL
- [ ] **LTL rate calculator**
  - Input: origin, destination, weight, class
  - Output: Rate estimates from multiple carriers
  - Show breakdown (base + FSC + accessorials)

---

## Phase 4: Capacity Indicators (Weeks 7-8)

**Goal**: Leading indicators for market tightness

### Free Capacity Data
- [ ] **FMCSA new authority tracker**
  - Scrape monthly "New Entrant" data
  - Track net new carriers vs revocations
  - Chart: Capacity trend (new - closed carriers)

- [ ] **Carrier closure monitor**
  - FMCSA revocation lists (public)
  - Bankruptcy news scraping (FreightWaves has this)
  - Store in carriers table with status updates

- [ ] **Driver demand proxy**
  - Scrape Indeed for "CDL driver" job postings by metro
  - Count as demand indicator
  - Run weekly, track trends

### FreightWaves Free Data
- [ ] **Scrape SONAR summaries**
  - Free articles mention OTVI/OTRI trends
  - Extract key numbers from text
  - Not precise, but directional signal

### Capacity Dashboard
- [ ] **Build capacity health dashboard**
  - Chart: New carriers vs closures (monthly)
  - Chart: Job posting volume (weekly)
  - Chart: Tender rejection trends (if available)
  - KPI cards: Current market tightness score

---

## Phase 5: Bloomberg-Style UI (Weeks 9-10)

**Goal**: Make it beautiful and information-dense

### Dark Theme Design
- [ ] **Terminal-style color scheme**
  - Dark background (#0a0a0a or similar)
  - Green for positive, red for negative
  - Blue/cyan for neutral data
  - High contrast for readability

- [ ] **Typography**
  - Monospace for numbers (alignment)
  - Clear hierarchy (large KPIs, small details)
  - Tight spacing (data density)

### Advanced Charts
- [ ] **Upgrade time-series charts**
  - Zoom on scroll
  - Pan on drag
  - Tooltip with all data points
  - Compare mode (overlay multiple metrics)
  - Export to PNG

- [ ] **Multi-metric dashboard**
  - 4-6 key charts on homepage
  - Spot rates + Capacity + Fuel + Macro
  - All auto-refreshing
  - Responsive grid layout

### Navigation
- [ ] **Quick navigation**
  - Sidebar with main sections
  - Search bar (Cmd+K) for lane lookup
  - Breadcrumbs for deep links
  - Recent views

### Data Tables
- [ ] **Build advanced data grid**
  - Sortable columns
  - Filterable inline
  - Export to CSV
  - Cell formatting (currency, %, dates)

---

## Phase 6: Contract Intelligence (Weeks 11-12)

**Goal**: Spot vs Contract analysis and decision support

### Spot-to-Contract Analysis
- [ ] **Build differential tracker**
  - Chart: Spot rate vs avg contract rate by lane
  - Historical spread analysis
  - Current market position (spot premium/discount)

### RFP Assistant
- [ ] **Simple RFP analysis tool**
  - Upload CSV of lanes
  - Get current spot rates for each
  - Get 90-day avg, min, max
  - Suggested bid targets (based on trends)
  - Export results

### Fuel Surcharge Tools
- [ ] **FSC calculator**
  - Input: base rate, current diesel price, FSC table
  - Output: Total rate with FSC
  - Common carrier FSC schedules pre-loaded

---

## Phase 7: Predictive Features (Weeks 13-14)

**Goal**: Forward-looking intelligence

### Simple Forecasting
- [ ] **7-day rate forecast**
  - Use linear regression on last 30 days
  - Show trend direction (up/down/flat)
  - Confidence interval
  - Not ML, just basic stats

### Seasonal Patterns
- [ ] **Historical pattern recognition**
  - Overlay last year's data
  - Identify seasonal peaks/troughs
  - "Typically rates increase in Q4" insights

### Economic Correlation
- [ ] **Leading indicator dashboard**
  - PMI vs freight rates (lag analysis)
  - Retail sales vs capacity (correlation)
  - Visual: When PMI rises, rates follow in X weeks

### Alerts (Simple)
- [ ] **Email alerts**
  - Lane rate threshold breach
  - Unusual rate spike (>2 std dev)
  - Macro index significant change
  - Simple Nodemailer setup

---

## Phase 8: Polish & Extras (Weeks 15-16)

### Data Quality
- [ ] **Add confidence scores**
  - Each rate has confidence (0-1)
  - Based on: data source, recency, sample size
  - Show in UI with visual indicator

- [ ] **Source attribution**
  - Every metric shows source
  - Link to original data
  - Last updated timestamp

### Exports
- [ ] **PDF reports**
  - Weekly market summary
  - Lane-specific analysis
  - Charts + commentary
  - Simple Puppeteer to PDF

- [ ] **CSV downloads**
  - Any table exportable
  - Historical data dumps
  - Custom date ranges

### Documentation
- [ ] **Internal wiki**
  - How to read each metric
  - Data source explanations
  - Methodology docs
  - Troubleshooting guide

---

## Key Architectural Principles

### Database
- SQLite is appropriate for internal tool with <10 concurrent users
- Design schema to handle all future data without changes
- Use migrations for schema evolution if needed
- Indexes on: date, lane_id, source, equipment_type

### API
- RESTful conventions - keep it simple
- Consistent query params across endpoints
- Always include data source in response
- Version only if breaking changes needed (hopefully never)

### Frontend
- Build reusable components from the start
- Keep state management simple
- Responsive by default (mobile-friendly grid)
- Fast > perfect (< 2 second page loads is fine)

### Data Pipeline
- Simple scheduled jobs - no need for complex queue systems
- Each scraper is independent script
- Log to files, review failures manually (internal tool)
- Retry logic in scraper base class

### Code Quality
- Type safety where possible
- Consistent code formatting
- Simple folder structure - easy to find things
- Comment the "why", not the "what"

---

## Non-Goals (Keep It Simple)

❌ User authentication (internal tool, single team)
❌ Multi-tenancy (one deployment, one team)
❌ Complex deployment orchestration (simple containerization is enough)
❌ Microservices (monolith is simpler)
❌ Real-time WebSockets (polling every 30s is fine)
❌ Mobile app (responsive web is enough)
❌ Advanced ML (simple stats is enough)
❌ 99.99% uptime (it can be down for 5 minutes)
❌ Sub-100ms API responses (sub-1s is fine)
❌ Advanced search engines (SQL full-text search is enough)

---

## Architecture Options

See the `/architecture/` directory for detailed implementation options:
- **Option 1**: Python Backend + React/Next.js Frontend (modern SPA)
- **Option 2**: Python Backend + Server-Side Templates (traditional web app)
- **Option 3**: Python + Streamlit (rapid prototyping, all-Python)

---

## Success Metrics

### Data Quality
- Zero synthetic data in production
- >90% of scrapers successful on each run
- <24hr data freshness for daily metrics
- >95% data source attribution

### User Experience
- <2 second page load times
- <5 clicks to any insight
- Charts update on data refresh without reload
- Zero broken links/charts

### Code Quality
- Zero "TODO: Refactor" comments in main branch
- Can add new data source in <4 hours
- Can add new dashboard view in <8 hours
- New team member can understand codebase in <1 day

### Business Value
- Team checks dashboard daily
- Informs actual freight procurement decisions
- Identifies cost-saving opportunities
- Faster decision-making vs manual research

---

## Timeline Summary

| Phase | Duration | Key Deliverable |
|-------|----------|-----------------|
| 0 | Week 1 | Schema design, API contracts, component patterns |
| 1 | Week 2 | All real data, zero synthetic data |
| 2 | Weeks 3-4 | Top 50 lanes with rate data |
| 3 | Weeks 5-6 | LTL rate intelligence |
| 4 | Weeks 7-8 | Capacity indicators |
| 5 | Weeks 9-10 | Bloomberg-style beautiful UI |
| 6 | Weeks 11-12 | Contract intelligence tools |
| 7 | Weeks 13-14 | Predictive features |
| 8 | Weeks 15-16 | Polish, exports, docs |

**Total**: 16 weeks to feature-complete internal tool

---

## The Big Picture

We're building an **internal freight intelligence platform** that:
1. Aggregates all free freight data into one place
2. Provides lane-specific rate intelligence
3. Offers spot vs contract decision support
4. Looks professional and information-dense
5. Updates automatically without manual work

We're NOT building:
- A product for external customers
- A real-time trading platform
- An enterprise SaaS with perfect uptime
- A platform that scales to millions of users

**Build for the team. Build it well. Build it once.**
