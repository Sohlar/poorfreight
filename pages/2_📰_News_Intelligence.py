"""
News Intelligence
Curated news analysis with filtering, tagging, and annotations
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, timezone
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.database import SessionLocal, NewsArticle
from lib.utils import get_all_tags_from_db, format_date

st.set_page_config(
    page_title="News Intelligence - Freight Intelligence",
    page_icon="📰",
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
        font-size: 1.1rem !important;
    }
    div[data-testid="stHorizontalBlock"] {
        gap: 0.5rem;
    }
    .article-card {
        background-color: rgba(28, 131, 225, 0.03);
        padding: 0.75rem;
        border-radius: 0.25rem;
        border-left: 3px solid #3b82f6;
        margin-bottom: 0.5rem;
    }
    .article-title {
        font-size: 0.95rem;
        font-weight: 600;
        margin-bottom: 0.25rem;
    }
    .article-meta {
        font-size: 0.75rem;
        color: #94a3b8;
    }
    .tag-badge {
        display: inline-block;
        background-color: rgba(59, 130, 246, 0.15);
        padding: 0.1rem 0.4rem;
        border-radius: 0.2rem;
        font-size: 0.7rem;
        margin-right: 0.25rem;
        font-family: monospace;
    }
    .importance-high {
        border-left-color: #ef4444;
    }
    .importance-medium {
        border-left-color: #f59e0b;
    }
    .importance-low {
        border-left-color: #94a3b8;
    }
    .unread-indicator {
        width: 8px;
        height: 8px;
        background-color: #ef4444;
        border-radius: 50%;
        display: inline-block;
        margin-right: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# === FUNCTIONS ===

@st.cache_data(ttl=300)
def load_news(sources=None, days_back=7, min_importance=1, search_query="", selected_tags=None):
    """Load and filter news articles"""
    db = SessionLocal()

    try:
        query = db.query(NewsArticle)

        if sources:
            query = query.filter(NewsArticle.source.in_(sources))

        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_back)
        query = query.filter(NewsArticle.published_at >= cutoff_date)

        query = query.filter(NewsArticle.importance >= min_importance)

        if search_query:
            search_pattern = f"%{search_query}%"
            query = query.filter(
                (NewsArticle.title.like(search_pattern)) |
                (NewsArticle.summary.like(search_pattern))
            )

        if selected_tags:
            for tag in selected_tags:
                query = query.filter(NewsArticle.tags.like(f"%{tag}%"))

        articles = query.order_by(NewsArticle.published_at.desc()).all()

        return articles

    finally:
        db.close()


def update_article(article_id, importance, tags, notes):
    """Update article metadata"""
    db = SessionLocal()
    try:
        article = db.query(NewsArticle).filter_by(id=article_id).first()
        if article:
            article.importance = importance
            article.tags = tags
            article.notes = notes
            article.updated_at = datetime.now(timezone.utc)
            db.commit()
    finally:
        db.close()


def mark_as_read(article_id):
    """Mark article as read"""
    db = SessionLocal()
    try:
        article = db.query(NewsArticle).filter_by(id=article_id).first()
        if article:
            article.read = True
            db.commit()
    finally:
        db.close()


@st.cache_data(ttl=600)
def get_available_sources():
    """Get list of sources with article counts"""
    db = SessionLocal()
    try:
        from sqlalchemy import func
        results = db.query(
            NewsArticle.source,
            func.count(NewsArticle.id).label('count')
        ).group_by(NewsArticle.source).all()

        return {source: count for source, count in results}
    finally:
        db.close()


@st.cache_data(ttl=600)
def get_all_tags():
    """Get all unique tags"""
    db = SessionLocal()
    try:
        return get_all_tags_from_db(db)
    finally:
        db.close()


def display_article_compact(article):
    """Display article in compact professional format"""
    # Determine importance class
    if article.importance >= 4:
        importance_class = "importance-high"
        importance_label = "HIGH"
    elif article.importance >= 3:
        importance_class = "importance-medium"
        importance_label = "MED"
    else:
        importance_class = "importance-low"
        importance_label = "LOW"

    # Unread indicator
    unread_indicator = '●' if not article.read else ''

    # Tags display
    tags_html = ""
    if article.tags:
        tags_list = [t.strip() for t in article.tags.split(',')]
        tags_html = " ".join([f'<span class="tag-badge">{tag}</span>' for tag in tags_list[:5]])

    # Summary (escape HTML)
    summary_text = ""
    if article.summary:
        import html
        summary_text = f'<div style="font-size: 0.85rem; margin-top: 0.25rem; color: #cbd5e1;">{html.escape(article.summary[:150])}...</div>'

    # Build HTML
    html_content = f'''<div class="article-card {importance_class}">
<div class="article-title">{unread_indicator} <a href="{article.url}" target="_blank">{html.escape(article.title)}</a> <span style="float: right; font-size: 0.75rem; color: #94a3b8;">[{importance_label}]</span></div>
<div class="article-meta">{article.source} • {article.published_at.strftime('%Y-%m-%d %H:%M')} UTC {' • ' + tags_html if tags_html else ''}</div>
{summary_text}
</div>'''

    st.markdown(html_content, unsafe_allow_html=True)


def display_article_full(article):
    """Display article with edit capabilities"""
    # Determine importance class
    if article.importance >= 4:
        importance_class = "importance-high"
    elif article.importance >= 3:
        importance_class = "importance-medium"
    else:
        importance_class = "importance-low"

    # Unread indicator
    unread_html = '<span class="unread-indicator"></span>' if not article.read else ''

    with st.expander(
        f"{unread_html} [{article.importance}★] {article.title} - {article.source}",
        expanded=False
    ):
        col1, col2 = st.columns([3, 1])

        with col1:
            if article.summary:
                st.caption("Summary")
                st.write(article.summary)

            if article.tags:
                tags_list = [t.strip() for t in article.tags.split(',')]
                tag_badges = " ".join([f"`{tag}`" for tag in tags_list])
                st.markdown(f"**Tags:** {tag_badges}")

            st.caption(f"Published: {article.published_at.strftime('%Y-%m-%d %H:%M')} UTC")
            st.markdown(f"[Read original]({article.url})")

        with col2:
            st.caption("EDIT")

            importance = st.select_slider(
                "Importance",
                options=[1, 2, 3, 4, 5],
                value=article.importance,
                key=f"imp_{article.id}"
            )

            tags_input = st.text_input(
                "Tags",
                value=article.tags or "",
                placeholder="capacity,rates,diesel",
                key=f"tags_{article.id}"
            )

            notes = st.text_area(
                "Notes",
                value=article.notes or "",
                placeholder="Analysis notes...",
                key=f"notes_{article.id}",
                height=80
            )

            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("Save", key=f"save_{article.id}"):
                    update_article(article.id, importance, tags_input, notes)
                    st.success("Saved!")
                    st.cache_data.clear()

            with col_b:
                if not article.read:
                    if st.button("Read", key=f"read_{article.id}"):
                        mark_as_read(article.id)
                        st.cache_data.clear()
                        st.rerun()


# === MAIN PAGE ===

col1, col2 = st.columns([3, 1])
with col1:
    st.title("News Intelligence")
with col2:
    st.caption("Freight Intelligence Portal")

# === FILTERS & CONTROLS ===
st.markdown("---")

# Single compact row for all filters and controls
col1, col2, col3, col4, col5, col6, col7 = st.columns([2, 1, 1, 1, 1, 1, 1])

with col1:
    search_query = st.text_input(
        "Search",
        placeholder="Search articles...",
        label_visibility="collapsed"
    )

with col2:
    sources_dict = get_available_sources()
    source_options = list(sources_dict.keys())
    sources = st.multiselect(
        "Src",
        source_options,
        default=source_options,
        label_visibility="visible"
    )

with col3:
    all_tags = get_all_tags()
    if all_tags:
        selected_tags = st.multiselect(
            "Tags",
            all_tags,
            label_visibility="visible"
        )
    else:
        selected_tags = []
        st.caption("No tags")

with col4:
    days_back = st.selectbox(
        "Days",
        [1, 7, 14, 30, 90],
        index=1
    )

with col5:
    importance_filter = st.selectbox(
        "Min★",
        [1, 2, 3, 4, 5],
        index=0
    )

with col6:
    view_mode = st.selectbox(
        "View",
        ["Compact", "Detailed"],
        index=0
    )

with col7:
    if st.button("Refresh"):
        st.cache_data.clear()
        st.rerun()

# === LOAD NEWS ===
articles = load_news(
    sources=sources if sources else None,
    days_back=days_back,
    min_importance=importance_filter,
    search_query=search_query,
    selected_tags=selected_tags if selected_tags else None
)

# === COMPACT STATS ===
st.markdown("---")
col1, col2, col3, col4, col5, col6 = st.columns([1, 1, 1, 1, 1, 2])

today_count = len([a for a in articles if a.published_at.date() == datetime.now(timezone.utc).date()])
important_count = len([a for a in articles if a.importance >= 4])
unread_count = len([a for a in articles if not a.read])

col1.metric("Total", len(articles))
col2.metric("Today", today_count)
col3.metric("High", important_count)
col4.metric("Unread", unread_count)

with col6:
    if st.button("Export CSV", use_container_width=True):
        df = pd.DataFrame([{
            'title': a.title,
            'source': a.source,
            'published': a.published_at,
            'url': a.url,
            'tags': a.tags,
            'importance': a.importance,
            'notes': a.notes
        } for a in articles])

        csv = df.to_csv(index=False)
        st.download_button(
            "Download CSV",
            csv,
            f"news_{datetime.now().strftime('%Y%m%d')}.csv",
            "text/csv",
            use_container_width=True
        )

# === DISPLAY ARTICLES ===
st.markdown("---")

if not articles:
    st.info("No articles found. Adjust filters or run news scraper.")
else:
    if view_mode == "Compact":
        for article in articles[:50]:  # Limit to 50 for performance
            display_article_compact(article)
    else:  # Detailed
        for article in articles[:30]:  # Limit to 30 for performance
            display_article_full(article)

    if len(articles) > 50:
        st.caption(f"Showing first {50 if view_mode == 'Compact' else 30} of {len(articles)} articles. Refine filters to see more.")
