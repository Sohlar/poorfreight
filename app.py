"""
Freight Intelligence Portal - Main Entry Point

Multi-page Streamlit application for freight market intelligence.
Focus: News analysis + Historical trend analysis for LTL/TL markets.
"""

import streamlit as st

# Configure page
st.set_page_config(
    page_title="Freight Intelligence Portal",
    page_icon="🚛",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "Freight Intelligence Portal - Market intelligence for LTL/TL carriers"
    }
)

# Main landing page
st.title("🚛 Freight Intelligence Portal")
st.markdown("### Market Intelligence for LTL & TL Freight")

st.markdown("---")

# Quick stats on homepage
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="News Articles",
        value="Loading...",
        help="Total articles in database"
    )

with col2:
    st.metric(
        label="Data Sources",
        value="4+",
        help="Active data sources"
    )

with col3:
    st.metric(
        label="Lanes Tracked",
        value="TBD",
        help="Origin-destination pairs"
    )

with col4:
    st.metric(
        label="Last Update",
        value="Live",
        help="Data freshness"
    )

st.markdown("---")

# Navigation guide
st.subheader("🧭 Portal Navigation")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### 📊 Data & Analysis
    - **🏠 Market Overview** - Current market snapshot
    - **📈 Historical Analysis** - Deep trend analysis & correlations
    - **🚛 Lane Intelligence** - Specific O-D pair insights
    """)

with col2:
    st.markdown("""
    ### 📰 Intelligence & Reports
    - **📰 News Intelligence** - Curated news with filtering & tagging
    - **📊 Strategic Reports** - Generate insights & summaries
    - **⚙️ Data Quality** - Monitor scraper health
    """)

st.markdown("---")

# Quick start guide
with st.expander("🚀 Quick Start Guide"):
    st.markdown("""
    ### Getting Started

    1. **📰 News Intelligence** (Start Here!)
       - Browse latest freight industry news
       - Filter by source, tags, importance
       - Add your own notes and ratings
       - Track what matters to your strategy

    2. **📈 Historical Analysis**
       - Analyze rate trends over time
       - Find correlations between metrics
       - Discover leading/lagging indicators
       - Export data for deeper analysis

    3. **🏠 Market Overview**
       - Quick snapshot of current market
       - Key metrics at a glance
       - Today's important news

    ### Tips
    - Use the sidebar to navigate between pages
    - Most pages have filters - customize what you see
    - Data auto-refreshes (click "Rerun" to force update)
    - Export any data to CSV for offline analysis
    """)

# Status
st.markdown("---")
st.caption("🔴 Live | Data updates automatically via background scrapers")
