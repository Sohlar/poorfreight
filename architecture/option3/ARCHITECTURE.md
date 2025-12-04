# Architecture Option 3: Python + Streamlit

**Stack**: All-Python data dashboard framework

---

## Overview

**Backend + Frontend**: Python + Streamlit
**Database**: SQLite + SQLAlchemy (or direct SQL)
**Deployment**: Single Python process

### When to Choose This:
- ✅ You want **ALL Python** (literally zero HTML/CSS/JS)
- ✅ You want to prototype **very fast** (dashboard in hours, not days)
- ✅ You're comfortable sacrificing some UI polish for speed
- ✅ You're familiar with Pandas/data analysis workflows
- ✅ You want built-in caching and performance optimization

### Trade-offs:
- ⚠️ Less control over UI design (Streamlit's layout system)
- ⚠️ Can feel "app-like" but not as polished as custom React
- ⚠️ Reloads entire page on interactions (can be optimized with caching)
- ⚠️ Not ideal for very complex dashboards with many states
- ✅ But: **Ridiculously fast to build**

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                        Browser                          │
│  ┌───────────────────────────────────────────────────┐ │
│  │       Streamlit-generated React App               │ │
│  │  (You don't write this - Streamlit generates it)  │ │
│  └───────────────────────────────────────────────────┘ │
└────────────────────┬────────────────────────────────────┘
                     │ WebSocket
                     │
┌────────────────────▼────────────────────────────────────┐
│              Streamlit Server (Python)                  │
│  ┌──────────────────────────────────────────────────┐  │
│  │          Your Python Script                      │  │
│  │  app.py - defines UI with Python functions       │  │
│  │  st.title(), st.metric(), st.line_chart(), etc.  │  │
│  └──────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────┐  │
│  │       Data Layer (Your Python Code)              │  │
│  │  - SQLAlchemy queries                            │  │
│  │  - Pandas DataFrames                             │  │
│  │  - Business logic                                │  │
│  └──────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                  SQLite Database                        │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│      Background Jobs (separate Python scripts)          │
│  Run scrapers via cron (same as other options)          │
└─────────────────────────────────────────────────────────┘
```

---

## Tech Stack Details

### Everything is Python

```python
# requirements.txt
streamlit==1.29.0
pandas==2.1.3
plotly==5.18.0          # Better charts than Streamlit's built-in
sqlalchemy==2.0.23

# Scraping (same as other options)
beautifulsoup4==4.12.2
requests==2.31.0
playwright==1.40.0

# Optional: For advanced features
streamlit-aggrid==0.3.4  # Better data tables
streamlit-option-menu==0.3.6  # Better navigation
```

**That's it. No npm, no Node.js, no JavaScript.**

---

## Project Structure

```
poorfreight/
├── app.py                       # Main Streamlit app (THE ENTIRE UI)
├── pages/                       # Multi-page app
│   ├── 1_🏠_Dashboard.py
│   ├── 2_🚛_Lanes.py
│   ├── 3_📊_Capacity.py
│   └── 4_📰_News.py
│
├── lib/                         # Your helper functions
│   ├── __init__.py
│   ├── database.py              # DB connection
│   ├── queries.py               # SQL queries
│   └── charts.py                # Chart helpers
│
├── models/                      # SQLAlchemy models (same as other options)
│   ├── __init__.py
│   ├── lane.py
│   ├── rate.py
│   └── ...
│
├── scrapers/                    # Background jobs (same as other options)
│   ├── base_scraper.py
│   ├── cass_scraper.py
│   └── ...
│
├── data/
│   └── freight.db
│
├── requirements.txt
├── .streamlit/
│   └── config.toml              # Streamlit config (theme, etc.)
└── Dockerfile
```

---

## Implementation Guide

### Step 1: Main Dashboard (app.py)

**This is THE ENTIRE APP UI:**

```python
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from sqlalchemy import create_engine
from datetime import datetime, timedelta

# Page config
st.set_page_config(
    page_title="Freight Intelligence",
    page_icon="🚛",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Database connection (cached so it only runs once)
@st.cache_resource
def get_database_engine():
    return create_engine("sqlite:///data/freight.db")

# Load data (cached for 5 minutes)
@st.cache_data(ttl=300)
def load_spot_rates():
    engine = get_database_engine()
    query = """
        SELECT date, van_spot_index, reefer_spot_index, flatbed_spot_index
        FROM daily_metrics
        WHERE date >= date('now', '-90 days')
        ORDER BY date
    """
    return pd.read_sql(query, engine)

@st.cache_data(ttl=300)
def load_macro_metrics():
    engine = get_database_engine()
    query = """
        SELECT month, cass_shipments_index, ata_tonnage_index
        FROM macro_metrics
        WHERE month >= date('now', '-24 months')
        ORDER BY month
    """
    return pd.read_sql(query, engine)

@st.cache_data(ttl=300)
def get_latest_metrics():
    engine = get_database_engine()
    query = """
        SELECT *
        FROM daily_metrics
        ORDER BY date DESC
        LIMIT 1
    """
    return pd.read_sql(query, engine).iloc[0]

# --- MAIN APP ---

st.title("🚛 Freight Intelligence Dashboard")
st.markdown("Real-time freight market intelligence")

# Sidebar filters
with st.sidebar:
    st.header("Filters")
    date_range = st.slider(
        "Date Range (days)",
        min_value=7,
        max_value=365,
        value=90
    )

    equipment_type = st.multiselect(
        "Equipment Type",
        ["Van", "Reefer", "Flatbed"],
        default=["Van", "Reefer", "Flatbed"]
    )

    st.markdown("---")
    if st.button("Refresh Data"):
        st.cache_data.clear()
        st.rerun()

# Load data
latest = get_latest_metrics()
spot_rates_df = load_spot_rates()
macro_df = load_macro_metrics()

# KPI Cards
st.subheader("Key Metrics")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Van Spot Rate ($/mi)",
        value=f"${latest['van_spot_index']:.2f}",
        delta="+3.2%"  # Calculate actual delta from previous day
    )

with col2:
    st.metric(
        label="Reefer Spot Rate ($/mi)",
        value=f"${latest['reefer_spot_index']:.2f}",
        delta="+2.1%"
    )

with col3:
    st.metric(
        label="Flatbed Spot Rate ($/mi)",
        value=f"${latest['flatbed_spot_index']:.2f}",
        delta="-1.5%"
    )

with col4:
    st.metric(
        label="Diesel ($/gal)",
        value=f"${latest['diesel_usd_per_gal']:.2f}",
        delta="-0.8%"
    )

st.markdown("---")

# Charts
st.subheader("Spot Rate Trends")

# Plotly chart (interactive!)
fig = go.Figure()

if "Van" in equipment_type:
    fig.add_trace(go.Scatter(
        x=spot_rates_df['date'],
        y=spot_rates_df['van_spot_index'],
        mode='lines',
        name='Van',
        line=dict(color='#3b82f6', width=2)
    ))

if "Reefer" in equipment_type:
    fig.add_trace(go.Scatter(
        x=spot_rates_df['date'],
        y=spot_rates_df['reefer_spot_index'],
        mode='lines',
        name='Reefer',
        line=dict(color='#10b981', width=2)
    ))

if "Flatbed" in equipment_type:
    fig.add_trace(go.Scatter(
        x=spot_rates_df['date'],
        y=spot_rates_df['flatbed_spot_index'],
        mode='lines',
        name='Flatbed',
        line=dict(color='#f59e0b', width=2)
    ))

fig.update_layout(
    template='plotly_dark',
    height=400,
    hovermode='x unified',
    xaxis_title="Date",
    yaxis_title="Rate ($/mile)"
)

st.plotly_chart(fig, use_container_width=True)

# Two columns for more charts
col1, col2 = st.columns(2)

with col1:
    st.subheader("Macro Indices")

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=macro_df['month'],
        y=macro_df['cass_shipments_index'],
        mode='lines+markers',
        name='Cass Shipments',
        line=dict(color='#8b5cf6', width=2)
    ))
    fig2.add_trace(go.Scatter(
        x=macro_df['month'],
        y=macro_df['ata_tonnage_index'],
        mode='lines+markers',
        name='ATA Tonnage',
        line=dict(color='#ec4899', width=2)
    ))
    fig2.update_layout(template='plotly_dark', height=300)

    st.plotly_chart(fig2, use_container_width=True)

with col2:
    st.subheader("Diesel vs Spot Rates")

    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(
        x=spot_rates_df['date'],
        y=spot_rates_df['diesel_usd_per_gal'],
        mode='lines',
        name='Diesel Price',
        yaxis='y',
        line=dict(color='#f97316', width=2)
    ))
    fig3.add_trace(go.Scatter(
        x=spot_rates_df['date'],
        y=spot_rates_df['van_spot_index'],
        mode='lines',
        name='Van Rate',
        yaxis='y2',
        line=dict(color='#3b82f6', width=2)
    ))
    fig3.update_layout(
        template='plotly_dark',
        height=300,
        yaxis=dict(title="Diesel ($/gal)"),
        yaxis2=dict(title="Van Rate ($/mi)", overlaying='y', side='right')
    )

    st.plotly_chart(fig3, use_container_width=True)

st.markdown("---")

# Data Table
st.subheader("Recent Rate Data")

# Format and display table
display_df = spot_rates_df.tail(20).copy()
display_df['date'] = pd.to_datetime(display_df['date']).dt.strftime('%Y-%m-%d')

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "date": st.column_config.TextColumn("Date"),
        "van_spot_index": st.column_config.NumberColumn("Van ($/mi)", format="$%.2f"),
        "reefer_spot_index": st.column_config.NumberColumn("Reefer ($/mi)", format="$%.2f"),
        "flatbed_spot_index": st.column_config.NumberColumn("Flatbed ($/mi)", format="$%.2f"),
    }
)
```

**That's it. That's the entire dashboard.**

---

### Step 2: Multi-Page App

Streamlit supports multiple pages automatically:

**`pages/2_🚛_Lanes.py`**
```python
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

st.set_page_config(page_title="Lanes", page_icon="🚛", layout="wide")

st.title("🚛 Lane Analysis")

# Get database
@st.cache_resource
def get_engine():
    return create_engine("sqlite:///data/freight.db")

# Load lanes
@st.cache_data
def load_lanes():
    engine = get_engine()
    return pd.read_sql("SELECT * FROM lanes ORDER BY volume_rank", engine)

lanes_df = load_lanes()

# Lane selector
col1, col2 = st.columns(2)

with col1:
    origin = st.selectbox(
        "Origin",
        options=sorted(lanes_df['origin'].unique())
    )

with col2:
    destination = st.selectbox(
        "Destination",
        options=sorted(lanes_df['destination'].unique())
    )

# Load rates for this lane
@st.cache_data
def load_lane_rates(origin, destination):
    engine = get_engine()
    query = f"""
        SELECT r.date, r.rate_per_mile, r.source, r.confidence_score
        FROM rates r
        JOIN lanes l ON r.lane_id = l.id
        WHERE l.origin = '{origin}' AND l.destination = '{destination}'
        ORDER BY r.date DESC
        LIMIT 90
    """
    return pd.read_sql(query, engine)

if origin and destination:
    rates_df = load_lane_rates(origin, destination)

    if not rates_df.empty:
        st.subheader(f"{origin} → {destination}")

        # Show current rate
        current_rate = rates_df.iloc[0]
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Current Rate", f"${current_rate['rate_per_mile']:.2f}/mi")
        with col2:
            avg_rate = rates_df['rate_per_mile'].mean()
            st.metric("90-Day Avg", f"${avg_rate:.2f}/mi")
        with col3:
            st.metric("Data Source", current_rate['source'])

        # Chart
        st.line_chart(
            rates_df.set_index('date')['rate_per_mile'],
            use_container_width=True
        )

        # Table
        st.dataframe(rates_df, use_container_width=True)
    else:
        st.warning("No rate data available for this lane")
```

**`pages/3_📊_Capacity.py`**
```python
import streamlit as st

st.title("📊 Capacity Indicators")

st.info("Capacity analysis coming soon...")

# You'd build this similar to above
# Load capacity metrics, show charts, etc.
```

---

### Step 3: Dark Theme Configuration

**`.streamlit/config.toml`**
```toml
[theme]
primaryColor = "#3b82f6"
backgroundColor = "#0a0a0a"
secondaryBackgroundColor = "#1f2937"
textColor = "#ffffff"
font = "sans serif"

[server]
port = 8501
enableCORS = false
enableXsrfProtection = false
```

---

## Advanced Features

### Better Data Tables

```python
from st_aggrid import AgGrid, GridOptionsBuilder

# Instead of st.dataframe
gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_pagination(paginationAutoPageSize=True)
gb.configure_default_column(filterable=True, sortable=True)
grid_options = gb.build()

AgGrid(
    df,
    gridOptions=grid_options,
    theme='streamlit',  # or 'dark'
    height=400
)
```

### Custom Navigation

```python
from streamlit_option_menu import option_menu

selected = option_menu(
    menu_title=None,
    options=["Dashboard", "Lanes", "Capacity", "News"],
    icons=["house", "truck", "graph-up", "newspaper"],
    menu_icon="cast",
    default_index=0,
    orientation="horizontal"
)

if selected == "Dashboard":
    # Dashboard code
elif selected == "Lanes":
    # Lanes code
# etc.
```

### File Upload (for RFP analysis)

```python
st.subheader("RFP Analysis")

uploaded_file = st.file_uploader("Upload lanes CSV", type=['csv'])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.write(f"Loaded {len(df)} lanes")

    # Process and show results
    for _, row in df.iterrows():
        rate = get_rate_for_lane(row['origin'], row['destination'])
        st.write(f"{row['origin']} → {row['destination']}: ${rate:.2f}/mi")
```

---

## Running the Application

### Development
```bash
pip install -r requirements.txt
streamlit run app.py

# Opens browser automatically at http://localhost:8501
```

### Production
```bash
# Docker
docker build -t freight-streamlit .
docker run -p 8501:8501 freight-streamlit

# Or with Streamlit Cloud (free hosting!)
# Just push to GitHub and connect repo
```

---

## Pros & Cons

### Pros
✅ **100% Python** - zero HTML/CSS/JavaScript
✅ **Incredibly fast development** - dashboard in hours
✅ **Built-in features**: caching, file upload, forms, charts
✅ **Beautiful by default** - looks professional without effort
✅ **Easy deployment** - Streamlit Cloud is free
✅ **Great for data apps** - Pandas integration is seamless
✅ **Rapid iteration** - change code, auto-reloads browser
✅ **Interactive widgets** - sliders, selects, buttons built-in

### Cons
❌ Less control over UI layout (Streamlit's grid system)
❌ Page reloads on interactions (can be optimized with caching)
❌ Not ideal for very complex state management
❌ Feels like a "data app" not a "web app"
❌ Can't easily build very custom interactions
❌ Harder to make mobile-optimized
❌ Single-user by default (can scale but needs work)

---

## When to Choose This Option

Choose Option 3 (Streamlit) if:
- You want to build a dashboard **TODAY**
- You want 100% Python (no JavaScript at all)
- You're comfortable with Streamlit's opinionated design
- You value speed over perfect UI control
- You're familiar with Pandas/data workflows
- You're building for internal use with <10 concurrent users
- You want to prototype first, potentially rebuild later

**This is the "I want it working in 4 hours" choice.**

---

## Real-World Example Timeline

**Option 1 (FastAPI + Next.js)**: 2-3 weeks to feature-complete dashboard
**Option 2 (FastAPI + Templates)**: 1-2 weeks to feature-complete dashboard
**Option 3 (Streamlit)**: **2-3 days** to feature-complete dashboard

If you need to prove value quickly and iterate fast, Streamlit is unbeatable.

---

## Migration Path

Many teams start with Streamlit to prove the concept, then migrate to Option 1 or 2 when they need more control:

1. **Week 1**: Build in Streamlit, show stakeholders, get feedback
2. **Month 1-2**: Iterate in Streamlit, solidify requirements
3. **Month 3+**: Rebuild in React or Templates if needed

**Or:** Just stay with Streamlit if it works. Many production apps run on Streamlit.
