"""
Market Overview Dashboard
Executive view with current market snapshot and KPIs
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta, timezone
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.database import SessionLocal, DailyMetric, MacroMetric, NewsArticle, Lane, Rate

st.set_page_config(
    page_title="Market Overview - Freight Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for professional, compact layout
st.markdown("""
<style>
    .block-container {
        padding-top: 1rem;
        padding-bottom: 0rem;
        max-width: 100%;
    }
    h1 {
        font-size: 1.3rem !important;
        margin-bottom: 0rem !important;
        margin-top: 0rem !important;
        font-weight: 600 !important;
    }
    h2, h3 {
        font-size: 1.1rem !important;
        margin-top: 0.5rem !important;
        margin-bottom: 0.25rem !important;
        font-weight: 500 !important;
    }
    .stMetric {
        background-color: rgba(28, 131, 225, 0.05);
        padding: 0.3rem;
        border-radius: 0.25rem;
        border-left: 3px solid #1c83e1;
    }
    .stMetric label {
        font-size: 0.7rem !important;
    }
    .stMetric [data-testid="stMetricValue"] {
        font-size: 0.9rem !important;
    }
    .stMetric [data-testid="stMetricDelta"] {
        font-size: 0.7rem !important;
    }
    div[data-testid="stHorizontalBlock"] {
        gap: 0.5rem;
    }
    .sentiment-box {
        background-color: rgba(28, 131, 225, 0.1);
        padding: 0.5rem 1rem;
        border-radius: 0.25rem;
        border-left: 4px solid #1c83e1;
        margin-bottom: 0.5rem;
    }
    .insight-item {
        font-size: 0.85rem;
        padding: 0.25rem 0;
        border-left: 2px solid #3b82f6;
        padding-left: 0.5rem;
        margin-bottom: 0.25rem;
    }
    .news-item {
        font-size: 0.85rem;
        padding: 0.25rem 0;
        margin-bottom: 0.25rem;
    }
</style>
""", unsafe_allow_html=True)

# === FUNCTIONS ===

@st.cache_data(ttl=300)
def get_latest_metrics():
    """Get most recent metrics for all indicators"""
    db = SessionLocal()
    try:
        latest_daily = db.query(DailyMetric).order_by(
            DailyMetric.date.desc()
        ).first()

        if latest_daily:
            prev_daily = db.query(DailyMetric).filter(
                DailyMetric.date < latest_daily.date
            ).order_by(DailyMetric.date.desc()).first()
        else:
            prev_daily = None

        latest_macro = db.query(MacroMetric).order_by(
            MacroMetric.month.desc()
        ).first()

        if latest_macro:
            prev_macro = db.query(MacroMetric).filter(
                MacroMetric.month < latest_macro.month
            ).order_by(MacroMetric.month.desc()).first()
        else:
            prev_macro = None

        return {
            'daily': latest_daily,
            'daily_prev': prev_daily,
            'macro': latest_macro,
            'macro_prev': prev_macro
        }
    finally:
        db.close()


@st.cache_data(ttl=300)
def get_trend_data(days=30):
    """Get recent trend data for sparklines"""
    db = SessionLocal()
    try:
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).strftime('%Y-%m-%d')

        daily_metrics = db.query(DailyMetric).filter(
            DailyMetric.date >= cutoff
        ).order_by(DailyMetric.date).all()

        return pd.DataFrame([{
            'date': m.date,
            'diesel': m.diesel_usd_per_gal,
            'gas_price': m.gas_price,
            'oil_price': m.oil_price
        } for m in daily_metrics])
    finally:
        db.close()


@st.cache_data(ttl=300)
def get_macro_trend_data(months=6):
    """Get recent macro trend data"""
    db = SessionLocal()
    try:
        cutoff = (datetime.now(timezone.utc) - timedelta(days=months*30)).strftime('%Y-%m')

        macro_metrics = db.query(MacroMetric).filter(
            MacroMetric.month >= cutoff
        ).order_by(MacroMetric.month).all()

        return pd.DataFrame([{
            'month': m.month,
            'cass_shipments': m.cass_shipments_index,
            'cass_expenditures': m.cass_expenditures_index,
            'ata_tonnage': m.ata_tonnage_index,
            'industrial_production': m.industrial_production,
            'ism_pmi': m.ism_pmi
        } for m in macro_metrics])
    finally:
        db.close()


@st.cache_data(ttl=300)
def get_recent_news(limit=5):
    """Get most recent high-importance news"""
    db = SessionLocal()
    try:
        articles = db.query(NewsArticle).filter(
            NewsArticle.importance >= 3
        ).order_by(NewsArticle.published_at.desc()).limit(limit).all()

        return articles
    finally:
        db.close()


@st.cache_data(ttl=600)
def get_state_freight_data():
    """Aggregate freight activity by state"""
    db = SessionLocal()
    try:
        from sqlalchemy import func

        # Get lane activity by origin state
        origin_stats = db.query(
            Lane.origin,
            func.count(Lane.id).label('lane_count'),
            func.avg(Lane.volume_rank).label('avg_volume_rank')
        ).group_by(Lane.origin).all()

        # Get lane activity by destination state
        dest_stats = db.query(
            Lane.destination,
            func.count(Lane.id).label('lane_count'),
            func.avg(Lane.volume_rank).label('avg_volume_rank')
        ).group_by(Lane.destination).all()

        # Combine origin and destination activity
        state_data = {}

        for state, count, avg_rank in origin_stats:
            if state and state != 'Unknown' and len(state) == 2:  # Valid state code
                state_data[state] = {
                    'outbound_lanes': count,
                    'inbound_lanes': 0,
                    'total_lanes': count,
                    'avg_volume_rank': avg_rank or 0
                }

        for state, count, avg_rank in dest_stats:
            if state and state != 'Unknown' and len(state) == 2:  # Valid state code
                if state in state_data:
                    state_data[state]['inbound_lanes'] = count
                    state_data[state]['total_lanes'] += count
                else:
                    state_data[state] = {
                        'outbound_lanes': 0,
                        'inbound_lanes': count,
                        'total_lanes': count,
                        'avg_volume_rank': avg_rank or 0
                    }

        # Convert to DataFrame
        df = pd.DataFrame([
            {
                'state': state,
                'outbound': data['outbound_lanes'],
                'inbound': data['inbound_lanes'],
                'total': data['total_lanes'],
                'volume_rank': data['avg_volume_rank']
            }
            for state, data in state_data.items()
        ])

        return df

    finally:
        db.close()


def create_choropleth_map(state_data, metric='total', title='Freight Activity by State'):
    """Create interactive choropleth map of US states"""

    if state_data.empty:
        return None

    # Metric configuration
    metric_configs = {
        'total': {
            'column': 'total',
            'colorscale': 'Blues',
            'label': 'Total Lanes',
            'hover_label': 'Total Lanes'
        },
        'outbound': {
            'column': 'outbound',
            'colorscale': 'Greens',
            'label': 'Outbound Lanes',
            'hover_label': 'Outbound'
        },
        'inbound': {
            'column': 'inbound',
            'colorscale': 'Oranges',
            'label': 'Inbound Lanes',
            'hover_label': 'Inbound'
        },
        'volume': {
            'column': 'volume_rank',
            'colorscale': 'Viridis',
            'label': 'Avg Volume Rank',
            'hover_label': 'Volume Rank'
        }
    }

    config = metric_configs.get(metric, metric_configs['total'])

    fig = go.Figure(data=go.Choropleth(
        locations=state_data['state'],
        z=state_data[config['column']],
        locationmode='USA-states',
        colorscale=config['colorscale'],
        autocolorscale=False,
        text=state_data['state'],
        marker_line_color='white',
        marker_line_width=0.5,
        colorbar=dict(
            title=config['label'],
            thickness=15,
            len=0.7,
            bgcolor='rgba(255,255,255,0.1)',
            tick0=0,
            dtick=max(state_data[config['column']].max() / 5, 1) if not state_data[config['column']].empty else 1
        ),
        hovertemplate='<b>%{text}</b><br>' +
                     f'{config["hover_label"]}: ' + '%{z}<br>' +
                     '<extra></extra>'
    ))

    fig.update_layout(
        template='plotly_dark',
        geo=dict(
            scope='usa',
            projection=go.layout.geo.Projection(type='albers usa'),
            showlakes=True,
            lakecolor='rgb(17, 24, 39)',
            bgcolor='rgba(0,0,0,0)',
            landcolor='rgb(31, 41, 55)',
            showland=True,
            showcountries=False,
            showcoastlines=False,
            showframe=False
        ),
        margin=dict(l=0, r=0, t=20, b=0),
        height=550,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )

    return fig


def calculate_change(current, previous):
    """Calculate percentage change"""
    if current is None or previous is None:
        return None
    if previous == 0:
        return 0
    return ((current - previous) / previous) * 100


def get_market_sentiment(metrics):
    """Determine overall market sentiment from metrics"""
    scores = []

    if metrics['macro'] and metrics['macro_prev']:
        if metrics['macro'].cass_shipments_index and metrics['macro_prev'].cass_shipments_index:
            change = calculate_change(
                metrics['macro'].cass_shipments_index,
                metrics['macro_prev'].cass_shipments_index
            )
            if change is not None:
                scores.append(1 if change > 0 else -1 if change < 0 else 0)

        if metrics['macro'].ata_tonnage_index and metrics['macro_prev'].ata_tonnage_index:
            change = calculate_change(
                metrics['macro'].ata_tonnage_index,
                metrics['macro_prev'].ata_tonnage_index
            )
            if change is not None:
                scores.append(1 if change > 0 else -1 if change < 0 else 0)

    if metrics['daily'] and metrics['daily_prev']:
        if metrics['daily'].diesel_usd_per_gal and metrics['daily_prev'].diesel_usd_per_gal:
            change = calculate_change(
                metrics['daily'].diesel_usd_per_gal,
                metrics['daily_prev'].diesel_usd_per_gal
            )
            if change is not None:
                scores.append(-1 if change > 2 else 1 if change < -2 else 0)

    if not scores:
        return "NEUTRAL", "#94a3b8"

    avg_score = sum(scores) / len(scores)

    if avg_score > 0.3:
        return "STRONG", "#10b981"
    elif avg_score > 0:
        return "MODERATE", "#f59e0b"
    elif avg_score < -0.3:
        return "WEAK", "#ef4444"
    else:
        return "NEUTRAL", "#94a3b8"


def create_sparkline(data, column):
    """Create a simple sparkline chart"""
    if data.empty or column not in data.columns:
        return None

    clean_data = data[column].dropna()
    if len(clean_data) == 0:
        return None

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        y=clean_data.values,
        mode='lines',
        line=dict(color='#3b82f6', width=1.5),
        fill='tozeroy',
        fillcolor='rgba(59, 130, 246, 0.1)',
        hovertemplate='%{y:.2f}<extra></extra>'
    ))

    fig.update_layout(
        showlegend=False,
        margin=dict(l=0, r=0, t=0, b=0),
        height=40,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        hovermode='x'
    )

    return fig


# === MAIN PAGE ===

# Load data
metrics = get_latest_metrics()
trend_data = get_trend_data(days=30)
macro_trend_data = get_macro_trend_data(months=6)
recent_news = get_recent_news(limit=5)

# Check if we have data
if not metrics['daily'] and not metrics['macro']:
    st.error("No market data available. Run scrapers to collect data.")
    st.stop()

# === COMPACT HEADER ===
col1, col2 = st.columns([3, 1])
with col1:
    st.title("Market Overview")
with col2:
    if metrics['daily']:
        st.caption(f"Data as of: {metrics['daily'].date}")

# === SENTIMENT | MACRO | FUEL (ALL IN ONE ROW, EQUAL HEIGHT) ===
sentiment, sentiment_color = get_market_sentiment(metrics)

col_sent, col_macro_label, col_m1, col_m2, col_m3, col_m4, col_fuel_label, col_f1, col_f2, col_f3, col_refresh = st.columns([1.5, 0.6, 1, 1, 1, 1, 0.6, 1, 1, 1, 0.6])

with col_sent:
    st.markdown(f'<div style="background-color: rgba(28, 131, 225, 0.1); padding: 0.5rem 0.5rem; border-radius: 0.25rem; border-left: 4px solid {sentiment_color}; font-size: 0.75rem; height: 100%; display: flex; align-items: center;">'
                f'<div><b>Sentiment</b><br><span style="color: {sentiment_color}; font-size: 1rem;">{sentiment}</span></div>'
                f'</div>', unsafe_allow_html=True)

with col_macro_label:
    st.markdown('<div style="padding: 0.5rem 0rem; font-size: 0.65rem; color: #94a3b8; text-align: center; height: 100%; display: flex; align-items: center; justify-content: center;"><b>MACRO<br>(MoM)</b></div>', unsafe_allow_html=True)

if metrics['macro']:
    with col_m1:
        current_cass_ship = metrics['macro'].cass_shipments_index
        prev_cass_ship = metrics['macro_prev'].cass_shipments_index if metrics['macro_prev'] else None
        change = calculate_change(current_cass_ship, prev_cass_ship)
        st.metric("Cass Ship", f"{current_cass_ship:.1f}" if current_cass_ship else "N/A",
                 f"{change:+.1f}%" if change is not None else None)

    with col_m2:
        current_cass_exp = metrics['macro'].cass_expenditures_index
        prev_cass_exp = metrics['macro_prev'].cass_expenditures_index if metrics['macro_prev'] else None
        change = calculate_change(current_cass_exp, prev_cass_exp)
        st.metric("Cass Exp", f"{current_cass_exp:.1f}" if current_cass_exp else "N/A",
                 f"{change:+.1f}%" if change is not None else None)

    with col_m3:
        current_ata = metrics['macro'].ata_tonnage_index
        prev_ata = metrics['macro_prev'].ata_tonnage_index if metrics['macro_prev'] else None
        change = calculate_change(current_ata, prev_ata)
        st.metric("ATA", f"{current_ata:.1f}" if current_ata else "N/A",
                 f"{change:+.1f}%" if change is not None else None)

    with col_m4:
        current_ism = metrics['macro'].ism_pmi
        prev_ism = metrics['macro_prev'].ism_pmi if metrics['macro_prev'] else None
        change = calculate_change(current_ism, prev_ism)
        st.metric("ISM PMI", f"{current_ism:.1f}" if current_ism else "N/A",
                 f"{change:+.1f}%" if change is not None else None)

with col_fuel_label:
    st.markdown('<div style="padding: 0.5rem 0rem; font-size: 0.65rem; color: #94a3b8; text-align: center; height: 100%; display: flex; align-items: center; justify-content: center;"><b>FUEL<br>(DoD)</b></div>', unsafe_allow_html=True)

if metrics['daily']:
    with col_f1:
        current_oil = metrics['daily'].oil_price
        prev_oil = metrics['daily_prev'].oil_price if metrics['daily_prev'] else None
        change = calculate_change(current_oil, prev_oil)
        st.metric("Oil", f"${current_oil:.2f}" if current_oil else "N/A",
                 f"{change:+.1f}%" if change is not None else None, delta_color="inverse")

    with col_f2:
        current_diesel = metrics['daily'].diesel_usd_per_gal
        prev_diesel = metrics['daily_prev'].diesel_usd_per_gal if metrics['daily_prev'] else None
        change = calculate_change(current_diesel, prev_diesel)
        st.metric("Diesel", f"${current_diesel:.2f}" if current_diesel else "N/A",
                 f"{change:+.1f}%" if change is not None else None, delta_color="inverse")

    with col_f3:
        current_gas = metrics['daily'].gas_price
        prev_gas = metrics['daily_prev'].gas_price if metrics['daily_prev'] else None
        change = calculate_change(current_gas, prev_gas)
        st.metric("Gas", f"${current_gas:.2f}" if current_gas else "N/A",
                 f"{change:+.1f}%" if change is not None else None, delta_color="inverse")

with col_refresh:
    st.markdown('<div style="padding: 0.5rem 0rem; height: 100%; display: flex; align-items: center;"></div>', unsafe_allow_html=True)
    if st.button("↻", help="Refresh", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# === MARKET INSIGHTS & NEWS ===
st.markdown("---")

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("**Market Insights**")

    insights = []

    if metrics['macro'] and metrics['macro_prev']:
        if metrics['macro'].cass_shipments_index and metrics['macro_prev'].cass_shipments_index:
            change = calculate_change(
                metrics['macro'].cass_shipments_index,
                metrics['macro_prev'].cass_shipments_index
            )
            if change is not None and abs(change) > 2:
                direction = "increased" if change > 0 else "decreased"
                insights.append(
                    f"Freight volumes {direction} by {abs(change):.1f}% MoM (Cass Shipments)"
                )

        if metrics['macro'].ata_tonnage_index and metrics['macro_prev'].ata_tonnage_index:
            change = calculate_change(
                metrics['macro'].ata_tonnage_index,
                metrics['macro_prev'].ata_tonnage_index
            )
            if change is not None and abs(change) > 2:
                direction = "rose" if change > 0 else "fell"
                insights.append(
                    f"Truck tonnage {direction} {abs(change):.1f}% (ATA Index)"
                )

    if metrics['daily'] and metrics['daily_prev']:
        if metrics['daily'].diesel_usd_per_gal and metrics['daily_prev'].diesel_usd_per_gal:
            change = calculate_change(
                metrics['daily'].diesel_usd_per_gal,
                metrics['daily_prev'].diesel_usd_per_gal
            )
            if change is not None and abs(change) > 1:
                direction = "up" if change > 0 else "down"
                insights.append(
                    f"Diesel prices moved {direction} {abs(change):.1f}% to ${metrics['daily'].diesel_usd_per_gal:.2f}/gal"
                )

    if metrics['macro'] and metrics['macro'].ism_pmi:
        if metrics['macro'].ism_pmi > 50:
            insights.append(
                f"Manufacturing expanding - ISM PMI at {metrics['macro'].ism_pmi:.1f} (above 50)"
            )
        elif metrics['macro'].ism_pmi < 50:
            insights.append(
                f"Manufacturing contracting - ISM PMI at {metrics['macro'].ism_pmi:.1f} (below 50)"
            )

    if insights:
        for insight in insights[:3]:
            st.markdown(f'<div class="insight-item" style="font-size: 0.85rem; padding: 0.2rem 0; border-left: 2px solid #3b82f6; padding-left: 0.5rem; margin-bottom: 0.2rem;">{insight}</div>', unsafe_allow_html=True)
    else:
        st.caption("Run scrapers to generate market insights")

with col2:
    st.markdown("**Latest News**")

    if recent_news:
        for article in recent_news[:3]:
            importance_label = "HIGH" if article.importance >= 4 else "MED"
            st.markdown(f'<div style="font-size: 0.8rem; padding: 0.2rem 0; margin-bottom: 0.2rem;"><b>[{importance_label}]</b> '
                       f'<a href="{article.url}" target="_blank">{article.title[:50]}...</a><br>'
                       f'<small style="color: #94a3b8;">{article.source} • {article.published_at.strftime("%m/%d/%Y")}</small></div>',
                       unsafe_allow_html=True)
    else:
        st.caption("No recent news available")

# === FREIGHT HEATMAP (MAIN FOCUS) ===
st.markdown("---")

state_data = get_state_freight_data()

if not state_data.empty:
    col1, col2 = st.columns([1, 10])

    with col1:
        st.caption("MAP VIEW")
        map_metric = st.selectbox(
            "Type",
            ["total", "outbound", "inbound", "volume"],
            format_func=lambda x: {
                "total": "Total",
                "outbound": "Outbound",
                "inbound": "Inbound",
                "volume": "Volume"
            }[x],
            label_visibility="collapsed"
        )

    with col2:
        map_fig = create_choropleth_map(state_data, metric=map_metric, title="")
        if map_fig:
            st.plotly_chart(map_fig, use_container_width=True)
else:
    st.info("No geographic data available. Run USASpending scraper to populate map.")
