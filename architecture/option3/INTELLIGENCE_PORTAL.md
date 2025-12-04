# Freight Intelligence Portal - Streamlit Multi-Page Implementation

**For**: Personal strategic intelligence tool
**Focus**: News analysis + Historical trend analysis for LTL/TL freight market
**Philosophy**: Data speed > Design polish, continuous improvement from first principles

---

## Portal Structure

```
Freight Intelligence Portal
├── 🏠 Market Overview          # Current state snapshot
├── 📰 News Intelligence        # Primary: Curated news analysis
├── 📈 Historical Analysis      # Primary: Trend analysis & charts
├── 🚛 Lane Intelligence        # Specific O-D pair deep dives
├── 📊 Strategic Reports        # Insights generation
└── ⚙️ Data Quality Monitor     # Scraper health, data freshness
```

---

## Implementation Phases

### Phase 1: News Intelligence Foundation (Week 1)

**Goal**: Get all news flowing and make it searchable/filterable

#### Database Schema
```sql
CREATE TABLE news_articles (
    id TEXT PRIMARY KEY,
    source TEXT,
    title TEXT,
    url TEXT,
    published_at DATETIME,
    summary TEXT,
    full_content TEXT,  -- Scraped article body
    tags TEXT,  -- Comma-separated: "capacity,rates,diesel"
    importance INTEGER,  -- 1-5 user rating
    notes TEXT,  -- Your annotations
    created_at DATETIME
);

CREATE INDEX idx_news_published ON news_articles(published_at DESC);
CREATE INDEX idx_news_source ON news_articles(source);
CREATE INDEX idx_news_tags ON news_articles(tags);
```

#### News Intelligence Page Features

**`pages/2_📰_News_Intelligence.py`**
```python
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="News Intelligence", page_icon="📰", layout="wide")

st.title("📰 Freight News Intelligence")

# === FILTERS ===
col1, col2, col3, col4 = st.columns(4)

with col1:
    sources = st.multiselect(
        "Sources",
        ["FreightWaves", "Supply Chain Dive", "Transport Topics", "JOC"],
        default=["FreightWaves", "JOC"]
    )

with col2:
    days_back = st.slider("Last N days", 1, 90, 7)

with col3:
    importance_filter = st.select_slider(
        "Min Importance",
        options=[1, 2, 3, 4, 5],
        value=1
    )

with col4:
    search_query = st.text_input("🔍 Search", placeholder="capacity, rates, diesel")

# Tag filter
all_tags = get_all_tags()  # From database
selected_tags = st.multiselect("Filter by tags", all_tags)

# === LOAD & FILTER NEWS ===
news_df = load_news(
    sources=sources,
    days_back=days_back,
    min_importance=importance_filter,
    search_query=search_query,
    tags=selected_tags
)

# === STATS ===
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Articles", len(news_df))
col2.metric("Today", len(news_df[news_df['published_at'] > datetime.now() - timedelta(days=1)]))
col3.metric("Important (4-5)", len(news_df[news_df['importance'] >= 4]))
col4.metric("Unread", len(news_df[news_df['read'] == False]))

st.markdown("---")

# === DISPLAY OPTIONS ===
view_mode = st.radio("View mode", ["Timeline", "List", "Grid"], horizontal=True)

if view_mode == "Timeline":
    # Group by date
    for date in news_df['published_at'].dt.date.unique():
        st.subheader(f"📅 {date}")
        day_news = news_df[news_df['published_at'].dt.date == date]

        for _, article in day_news.iterrows():
            display_article_card(article)

elif view_mode == "List":
    for _, article in news_df.iterrows():
        display_article_row(article)

# === ARTICLE DISPLAY FUNCTIONS ===
def display_article_card(article):
    with st.expander(
        f"{'⭐' * article['importance']} {article['title']} - {article['source']}",
        expanded=False
    ):
        col1, col2 = st.columns([3, 1])

        with col1:
            st.write(article['summary'])

            # Show full content if available
            if article['full_content']:
                if st.button("Show full article", key=f"full_{article['id']}"):
                    st.markdown(article['full_content'])

            st.caption(f"Published: {article['published_at']}")

        with col2:
            # Quick actions
            importance = st.select_slider(
                "Importance",
                options=[1, 2, 3, 4, 5],
                value=article['importance'],
                key=f"imp_{article['id']}"
            )

            tags_input = st.text_input(
                "Tags",
                value=article['tags'] or "",
                placeholder="capacity,rates,diesel",
                key=f"tags_{article['id']}"
            )

            notes = st.text_area(
                "Notes",
                value=article['notes'] or "",
                placeholder="Why this matters...",
                key=f"notes_{article['id']}"
            )

            if st.button("Save", key=f"save_{article['id']}"):
                update_article(article['id'], importance, tags_input, notes)
                st.success("Saved!")

            st.markdown(f"[Read original]({article['url']})")

# === BULK ACTIONS ===
st.markdown("---")
st.subheader("Bulk Actions")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Mark all as read"):
        mark_all_read(news_df)
        st.rerun()

with col2:
    if st.button("Export filtered to CSV"):
        csv = news_df.to_csv(index=False)
        st.download_button("Download CSV", csv, "news_export.csv")

with col3:
    if st.button("Generate summary report"):
        st.session_state['generate_report'] = True

# === AI SUMMARY (Optional future enhancement) ===
if st.session_state.get('generate_report'):
    st.markdown("---")
    st.subheader("📋 Summary Report")

    summary = generate_news_summary(news_df)
    st.markdown(summary)

    # Key themes
    st.subheader("Key Themes")
    themes = extract_themes(news_df)
    for theme, count in themes.items():
        st.write(f"- **{theme}**: {count} articles")
```

#### Enhanced News Scraper
```python
# scrapers/news_scraper_enhanced.py
import requests
from bs4 import BeautifulSoup
from newspaper import Article  # For full article extraction

class EnhancedNewsScraper(BaseScraper):
    def __init__(self, source_name, rss_url):
        super().__init__(source_name)
        self.rss_url = rss_url

    def fetch(self):
        """Fetch RSS feed"""
        return parser.parseURL(self.rss_url)

    def parse(self, feed):
        """Parse RSS items and extract full content"""
        articles = []

        for item in feed.items:
            # Get full article content
            try:
                article = Article(item.link)
                article.download()
                article.parse()
                full_content = article.text
            except:
                full_content = None

            # Auto-tag based on keywords
            tags = self.auto_tag(item.title, item.summary, full_content)

            articles.append({
                'id': self.generate_id(item),
                'source': self.source,
                'title': item.title,
                'url': item.link,
                'published_at': item.pubDate,
                'summary': self.extract_summary(item),
                'full_content': full_content,
                'tags': ','.join(tags),
                'importance': self.auto_rate_importance(tags, item.title)
            })

        return articles

    def auto_tag(self, title, summary, content):
        """Auto-tag based on keywords"""
        text = f"{title} {summary} {content or ''}".lower()

        tags = []
        keyword_map = {
            'capacity': ['capacity', 'tight', 'shortage', 'availability'],
            'rates': ['rate', 'pricing', 'cost', 'price'],
            'diesel': ['diesel', 'fuel', 'energy'],
            'ltl': ['less-than-truckload', 'ltl'],
            'contracts': ['contract', 'bid', 'rfp'],
            'economy': ['economy', 'gdp', 'recession', 'demand'],
            'regulation': ['fmcsa', 'regulation', 'compliance', 'dot'],
        }

        for tag, keywords in keyword_map.items():
            if any(kw in text for kw in keywords):
                tags.append(tag)

        return tags

    def auto_rate_importance(self, tags, title):
        """Auto-rate importance 1-5"""
        score = 1

        # High-priority tags
        if 'capacity' in tags or 'rates' in tags:
            score += 1

        # Keywords in title
        important_words = ['shortage', 'spike', 'crisis', 'major', 'breaking']
        if any(word in title.lower() for word in important_words):
            score += 1

        return min(score, 5)
```

---

### Phase 2: Historical Analysis (Week 1-2)

**Goal**: Deep trend analysis with interactive charts

#### Historical Analysis Page

**`pages/3_📈_Historical_Analysis.py`**
```python
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy import stats

st.set_page_config(page_title="Historical Analysis", page_icon="📈", layout="wide")

st.title("📈 Historical Market Analysis")

# === DATE RANGE SELECTOR ===
col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("Start Date", datetime.now() - timedelta(days=365))
with col2:
    end_date = st.date_input("End Date", datetime.now())

# === METRIC SELECTION ===
st.subheader("Select Metrics to Analyze")

col1, col2 = st.columns(2)

with col1:
    st.write("**Spot Rates**")
    show_van = st.checkbox("Van Spot Rate", value=True)
    show_reefer = st.checkbox("Reefer Spot Rate", value=True)
    show_flatbed = st.checkbox("Flatbed Spot Rate", value=False)

with col2:
    st.write("**Macro Indicators**")
    show_diesel = st.checkbox("Diesel Price", value=True)
    show_cass = st.checkbox("Cass Freight Index", value=True)
    show_ata = st.checkbox("ATA Tonnage Index", value=False)

# === LOAD DATA ===
spot_rates_df = load_spot_rates(start_date, end_date)
macro_df = load_macro_metrics(start_date, end_date)

# === MULTI-METRIC CHART ===
st.subheader("Multi-Metric Trends")

fig = make_subplots(specs=[[{"secondary_y": True}]])

# Add spot rates (left y-axis)
if show_van:
    fig.add_trace(
        go.Scatter(x=spot_rates_df['date'], y=spot_rates_df['van_spot_index'],
                   name='Van Rate', line=dict(color='#3b82f6', width=2)),
        secondary_y=False
    )

if show_reefer:
    fig.add_trace(
        go.Scatter(x=spot_rates_df['date'], y=spot_rates_df['reefer_spot_index'],
                   name='Reefer Rate', line=dict(color='#10b981', width=2)),
        secondary_y=False
    )

# Add diesel (right y-axis)
if show_diesel:
    fig.add_trace(
        go.Scatter(x=spot_rates_df['date'], y=spot_rates_df['diesel_usd_per_gal'],
                   name='Diesel Price', line=dict(color='#f59e0b', width=2, dash='dash')),
        secondary_y=True
    )

fig.update_layout(
    template='plotly_dark',
    height=500,
    hovermode='x unified',
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

fig.update_xaxes(title_text="Date")
fig.update_yaxes(title_text="Rate ($/mile)", secondary_y=False)
fig.update_yaxes(title_text="Diesel ($/gal)", secondary_y=True)

st.plotly_chart(fig, use_container_width=True)

# === STATISTICAL ANALYSIS ===
st.markdown("---")
st.subheader("Statistical Analysis")

col1, col2, col3 = st.columns(3)

if show_van:
    with col1:
        van_stats = spot_rates_df['van_spot_index'].describe()
        st.metric("Van Avg", f"${van_stats['mean']:.2f}")
        st.caption(f"Min: ${van_stats['min']:.2f}, Max: ${van_stats['max']:.2f}")
        st.caption(f"Std Dev: ${van_stats['std']:.2f}")

        # Trend
        trend = calculate_trend(spot_rates_df['van_spot_index'])
        st.metric("Trend", f"{trend:+.1f}%", delta=f"{trend:+.1f}%")

# === CORRELATION ANALYSIS ===
st.markdown("---")
st.subheader("Correlation Analysis")

# Merge data for correlation
correlation_df = spot_rates_df.merge(macro_df, left_on='date', right_on='month', how='inner')

selected_metrics = []
if show_van: selected_metrics.append('van_spot_index')
if show_diesel: selected_metrics.append('diesel_usd_per_gal')
if show_cass: selected_metrics.append('cass_shipments_index')

if len(selected_metrics) > 1:
    corr_matrix = correlation_df[selected_metrics].corr()

    # Heatmap
    fig_corr = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=corr_matrix.columns,
        y=corr_matrix.columns,
        colorscale='RdBu',
        zmid=0
    ))
    fig_corr.update_layout(template='plotly_dark', height=400)
    st.plotly_chart(fig_corr, use_container_width=True)

# === LAG ANALYSIS ===
st.markdown("---")
st.subheader("Leading/Lagging Indicators")

st.write("Find which metrics lead or lag others:")

metric_1 = st.selectbox("Metric 1", selected_metrics, key='lag1')
metric_2 = st.selectbox("Metric 2", selected_metrics, key='lag2')

if metric_1 != metric_2:
    lags = range(-30, 31, 5)  # -30 to +30 days, step 5
    correlations = []

    for lag in lags:
        series1 = correlation_df[metric_1]
        series2 = correlation_df[metric_2].shift(lag)
        corr = series1.corr(series2)
        correlations.append(corr)

    # Plot lag correlation
    fig_lag = go.Figure()
    fig_lag.add_trace(go.Scatter(
        x=list(lags),
        y=correlations,
        mode='lines+markers',
        line=dict(color='#8b5cf6', width=2)
    ))
    fig_lag.update_layout(
        template='plotly_dark',
        xaxis_title="Lag (days)",
        yaxis_title="Correlation",
        height=400
    )
    st.plotly_chart(fig_lag, use_container_width=True)

    # Interpretation
    max_corr_lag = lags[correlations.index(max(correlations))]
    if max_corr_lag > 0:
        st.info(f"📊 {metric_1} leads {metric_2} by ~{max_corr_lag} days")
    elif max_corr_lag < 0:
        st.info(f"📊 {metric_2} leads {metric_1} by ~{abs(max_corr_lag)} days")
    else:
        st.info("📊 Metrics move together with no significant lag")

# === EXPORT ===
st.markdown("---")
if st.button("Export Analysis Data"):
    export_df = correlation_df[selected_metrics]
    csv = export_df.to_csv(index=False)
    st.download_button("Download CSV", csv, "historical_analysis.csv")
```

#### Helper Functions
```python
def calculate_trend(series):
    """Calculate % change from start to end"""
    return ((series.iloc[-1] - series.iloc[0]) / series.iloc[0]) * 100

def detect_anomalies(series, threshold=2):
    """Detect values > threshold std deviations from mean"""
    mean = series.mean()
    std = series.std()
    anomalies = series[abs(series - mean) > threshold * std]
    return anomalies
```

---

### Phase 3: Market Overview Dashboard (Week 2)

**Simple current state snapshot**

**`pages/1_🏠_Market_Overview.py`**
```python
st.title("🏠 Freight Market Overview")

# Current metrics
latest = get_latest_metrics()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Van Rate", f"${latest['van']:.2f}/mi", delta=f"{latest['van_change']:+.1f}%")
col2.metric("Diesel", f"${latest['diesel']:.2f}/gal", delta=f"{latest['diesel_change']:+.1f}%")
# etc...

# Recent trends (7-day sparklines)
st.subheader("7-Day Trends")
# Simple line charts

# Top news today
st.subheader("📰 Today's Key News")
today_news = load_news(days_back=1, min_importance=4)
for article in today_news[:5]:
    st.write(f"- [{article['title']}]({article['url']})")
```

---

### Phase 4: Lane Intelligence (Week 3)

**Deep dive into specific O-D pairs**

**`pages/4_🚛_Lane_Intelligence.py`**
```python
st.title("🚛 Lane Intelligence")

# Lane selector
col1, col2 = st.columns(2)
with col1:
    origin = st.selectbox("Origin", get_all_origins())
with col2:
    destination = st.selectbox("Destination", get_all_destinations())

if origin and destination:
    lane_data = get_lane_analysis(origin, destination)

    # Show historical rates
    st.line_chart(lane_data['rates'])

    # Show contract vs spot
    # Show seasonality
    # Show related news
```

---

### Phase 5: Strategic Reports (Week 4)

**Generate insights, weekly summaries**

**`pages/5_📊_Strategic_Reports.py`**
```python
st.title("📊 Strategic Reports")

report_type = st.selectbox("Report Type", [
    "Weekly Market Summary",
    "Monthly Trend Report",
    "News Digest",
    "Lane Analysis Report"
])

if st.button("Generate Report"):
    if report_type == "Weekly Market Summary":
        report = generate_weekly_summary()
        st.markdown(report)

        # Export to PDF
        pdf = markdown_to_pdf(report)
        st.download_button("Download PDF", pdf, "weekly_summary.pdf")
```

---

## Running the Intelligence Portal

```bash
# Install dependencies
pip install streamlit pandas plotly sqlalchemy beautifulsoup4 requests newspaper3k

# Run portal
streamlit run app.py

# Runs on http://localhost:8501
# Background scrapers run via cron, feed database
# You refresh browser to see new data
```

---

## Continuous Improvement Workflow

**Week 1**: News + Historical analysis working
**Week 2**: Add more data sources, refine charts
**Week 3**: Lane intelligence, better filtering
**Week 4**: Reports, exports
**Ongoing**: New scrapers, new metrics, new insights as you learn what matters

---

## Why This Works for You

✅ **All Python** - your preference
✅ **Fast to build** - working portal in days, not weeks
✅ **News-first** - primary focus on news curation
✅ **Historical analysis** - deep trend diving with Plotly
✅ **Always-on server** - just leave Streamlit running
✅ **Continuous improvement** - add features as you go
✅ **Data > Design** - functional over pretty

This is the fastest path to **actionable freight intelligence**.
