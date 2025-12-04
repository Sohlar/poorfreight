"""
Historical Analysis
Trend analysis with multi-metric correlations and leading/lagging indicators
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
from scipy import stats
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.database import SessionLocal, DailyMetric, MacroMetric

st.set_page_config(
    page_title="Historical Analysis - Freight Intelligence",
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
        font-size: 1.75rem !important;
        margin-bottom: 0.25rem !important;
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
        padding: 0.5rem;
        border-radius: 0.25rem;
        border-left: 3px solid #1c83e1;
    }
    .stMetric label {
        font-size: 0.75rem !important;
    }
    .stMetric [data-testid="stMetricValue"] {
        font-size: 1.25rem !important;
    }
    div[data-testid="stHorizontalBlock"] {
        gap: 0.5rem;
    }
    .stCheckbox {
        margin-bottom: 0.25rem !important;
    }
</style>
""", unsafe_allow_html=True)

# === FUNCTIONS ===

@st.cache_data(ttl=600)
def load_daily_metrics(days_back=365):
    """Load daily metrics"""
    db = SessionLocal()
    try:
        cutoff_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
        metrics = db.query(DailyMetric).filter(
            DailyMetric.date >= cutoff_date
        ).order_by(DailyMetric.date).all()

        if not metrics:
            return pd.DataFrame()

        data = [{
            'date': m.date,
            'diesel': m.diesel_usd_per_gal,
            'gas_price': m.gas_price,
            'oil_price': m.oil_price,
            'van_rate': m.van_spot_index,
            'reefer_rate': m.reefer_spot_index,
            'flatbed_rate': m.flatbed_spot_index
        } for m in metrics]

        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'])
        return df
    finally:
        db.close()


@st.cache_data(ttl=600)
def load_macro_metrics(months_back=24):
    """Load macro metrics"""
    db = SessionLocal()
    try:
        cutoff_month = (datetime.now() - timedelta(days=months_back*30)).strftime('%Y-%m')
        metrics = db.query(MacroMetric).filter(
            MacroMetric.month >= cutoff_month
        ).order_by(MacroMetric.month).all()

        if not metrics:
            return pd.DataFrame()

        data = [{
            'month': m.month,
            'cass_shipments': m.cass_shipments_index,
            'cass_expenditures': m.cass_expenditures_index,
            'ata_tonnage': m.ata_tonnage_index,
            'industrial_production': m.industrial_production,
            'ism_pmi': m.ism_pmi,
            'retail_sales': m.retail_sales,
            'consumer_sentiment': m.consumer_sentiment
        } for m in metrics]

        df = pd.DataFrame(data)
        df['month'] = pd.to_datetime(df['month'])
        return df
    finally:
        db.close()


def calculate_trend(series):
    """Calculate % change from start to end"""
    if len(series) < 2 or series.isna().all():
        return 0
    start = series.dropna().iloc[0] if len(series.dropna()) > 0 else 0
    end = series.dropna().iloc[-1] if len(series.dropna()) > 0 else 0
    if start == 0:
        return 0
    return ((end - start) / start) * 100


# === HEADER ===
col1, col2 = st.columns([3, 1])
with col1:
    st.title("Historical Analysis")
with col2:
    st.caption("Freight Intelligence Portal")

# === LOAD DATA ===
daily_df = load_daily_metrics(days_back=365)
macro_df = load_macro_metrics(months_back=24)

has_daily = len(daily_df) > 0
has_macro = len(macro_df) > 0

if not has_daily and not has_macro:
    st.error("No historical data available. Run scrapers to collect data.")
    st.stop()

# === COMPACT CONTROLS ===
st.markdown("---")
col1, col2, col3, col4 = st.columns([1, 1, 2, 2])

with col1:
    days_back = st.selectbox(
        "Period (days)",
        [30, 60, 90, 180, 365],
        index=2,
        label_visibility="visible"
    )

with col2:
    months_back = st.selectbox(
        "Macro (months)",
        [6, 12, 18, 24],
        index=1,
        label_visibility="visible"
    )

# Reload with selected range
if has_daily:
    daily_df = load_daily_metrics(days_back=days_back)
if has_macro:
    macro_df = load_macro_metrics(months_back=months_back)

# Metric selection in columns 3 and 4
available_daily = []
available_macro = []

with col3:
    st.caption("DAILY METRICS")
    dcols = st.columns(3)

    with dcols[0]:
        if 'diesel' in daily_df.columns and daily_df['diesel'].notna().any():
            if st.checkbox("Diesel", value=True, key="d1"):
                available_daily.append('diesel')
        if 'gas_price' in daily_df.columns and daily_df['gas_price'].notna().any():
            if st.checkbox("Gasoline", value=True, key="d2"):
                available_daily.append('gas_price')

    with dcols[1]:
        if 'oil_price' in daily_df.columns and daily_df['oil_price'].notna().any():
            if st.checkbox("Crude Oil", value=True, key="d3"):
                available_daily.append('oil_price')
        if 'van_rate' in daily_df.columns and daily_df['van_rate'].notna().any():
            if st.checkbox("Van Rate", key="d4"):
                available_daily.append('van_rate')

    with dcols[2]:
        if 'reefer_rate' in daily_df.columns and daily_df['reefer_rate'].notna().any():
            if st.checkbox("Reefer", key="d5"):
                available_daily.append('reefer_rate')
        if 'flatbed_rate' in daily_df.columns and daily_df['flatbed_rate'].notna().any():
            if st.checkbox("Flatbed", key="d6"):
                available_daily.append('flatbed_rate')

with col4:
    st.caption("MACRO INDICATORS")
    mcols = st.columns(3)

    with mcols[0]:
        if 'cass_shipments' in macro_df.columns and macro_df['cass_shipments'].notna().any():
            if st.checkbox("Cass Ship.", key="m1"):
                available_macro.append('cass_shipments')
        if 'cass_expenditures' in macro_df.columns and macro_df['cass_expenditures'].notna().any():
            if st.checkbox("Cass Exp.", key="m2"):
                available_macro.append('cass_expenditures')

    with mcols[1]:
        if 'ata_tonnage' in macro_df.columns and macro_df['ata_tonnage'].notna().any():
            if st.checkbox("ATA Ton.", key="m3"):
                available_macro.append('ata_tonnage')
        if 'industrial_production' in macro_df.columns and macro_df['industrial_production'].notna().any():
            if st.checkbox("Ind. Prod.", key="m4"):
                available_macro.append('industrial_production')

    with mcols[2]:
        if 'ism_pmi' in macro_df.columns and macro_df['ism_pmi'].notna().any():
            if st.checkbox("ISM PMI", key="m5"):
                available_macro.append('ism_pmi')
        if 'consumer_sentiment' in macro_df.columns and macro_df['consumer_sentiment'].notna().any():
            if st.checkbox("Consumer", key="m6"):
                available_macro.append('consumer_sentiment')

st.markdown("---")

# === CHART ===
if available_daily or available_macro:
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Daily metrics
    colors_daily = {
        'diesel': '#f59e0b',
        'gas_price': '#fbbf24',
        'oil_price': '#92400e',
        'van_rate': '#3b82f6',
        'reefer_rate': '#10b981',
        'flatbed_rate': '#8b5cf6'
    }

    for metric in available_daily:
        if metric in daily_df.columns and daily_df[metric].notna().any():
            use_secondary = (metric == 'oil_price')
            mode = 'lines+markers' if metric in ['diesel', 'gas_price'] else 'lines'

            fig.add_trace(
                go.Scatter(
                    x=daily_df['date'],
                    y=daily_df[metric],
                    name=metric.replace('_', ' ').title(),
                    line=dict(color=colors_daily.get(metric, '#888'), width=2),
                    marker=dict(size=6) if 'markers' in mode else None,
                    mode=mode,
                    connectgaps=True
                ),
                secondary_y=use_secondary
            )

    # Macro metrics
    colors_macro = {
        'cass_shipments': '#ec4899',
        'cass_expenditures': '#f472b6',
        'ata_tonnage': '#8b5cf6',
        'industrial_production': '#14b8a6',
        'ism_pmi': '#0ea5e9',
        'retail_sales': '#f97316',
        'consumer_sentiment': '#eab308'
    }

    for metric in available_macro:
        if metric in macro_df.columns and macro_df[metric].notna().any():
            fig.add_trace(
                go.Scatter(
                    x=macro_df['month'],
                    y=macro_df[metric],
                    name=metric.replace('_', ' ').title(),
                    line=dict(color=colors_macro.get(metric, '#888'), width=2, dash='dash'),
                    mode='lines+markers'
                ),
                secondary_y=True
            )

    fig.update_layout(
        template='plotly_dark',
        height=400,
        margin=dict(l=50, r=50, t=30, b=50),
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.15,
            xanchor="center",
            x=0.5,
            font=dict(size=10)
        ),
        xaxis_title="",
        font=dict(size=11)
    )

    fig.update_yaxes(title_text="Fuel Prices ($/gal)", secondary_y=False, title_font=dict(size=11))
    fig.update_yaxes(title_text="Oil ($/bbl) & Indices", secondary_y=True, title_font=dict(size=11))

    st.plotly_chart(fig, use_container_width=True)

    # Compact stats
    st.markdown("---")
    st.caption("CURRENT METRICS")

    all_metrics = available_daily + available_macro
    if all_metrics:
        cols = st.columns(len(all_metrics))

        for idx, metric in enumerate(available_daily):
            if metric in daily_df.columns and daily_df[metric].notna().any():
                with cols[idx]:
                    series = daily_df[metric].dropna()
                    current = series.iloc[-1] if len(series) > 0 else 0
                    trend = calculate_trend(series)

                    st.metric(
                        label=metric.replace('_', ' ').title(),
                        value=f"${current:.2f}" if 'price' in metric or 'diesel' in metric else f"{current:.1f}",
                        delta=f"{trend:+.1f}%"
                    )

        for idx, metric in enumerate(available_macro):
            if metric in macro_df.columns and macro_df[metric].notna().any():
                with cols[len(available_daily) + idx]:
                    series = macro_df[metric].dropna()
                    current = series.iloc[-1] if len(series) > 0 else 0
                    trend = calculate_trend(series)

                    st.metric(
                        label=metric.replace('_', ' ').title(),
                        value=f"{current:.1f}",
                        delta=f"{trend:+.1f}%"
                    )

else:
    st.info("Select metrics above to display trends")
