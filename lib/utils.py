"""
Utility functions for the Freight Intelligence Portal
"""

from datetime import datetime, timedelta
from typing import List, Dict
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def get_env(key: str, default: str = None) -> str:
    """Get environment variable with optional default"""
    return os.getenv(key, default)


def format_date(date_str: str) -> str:
    """Format ISO date string to readable format"""
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M')
    except:
        return date_str


def days_ago(days: int) -> datetime:
    """Get datetime N days ago"""
    return datetime.now() - timedelta(days=days)


def get_all_tags_from_db(db) -> List[str]:
    """Extract all unique tags from news articles"""
    from lib.database import NewsArticle

    articles = db.query(NewsArticle.tags).filter(NewsArticle.tags.isnot(None)).all()

    all_tags = set()
    for (tags_str,) in articles:
        if tags_str:
            tags = [t.strip() for t in tags_str.split(',')]
            all_tags.update(tags)

    return sorted(list(all_tags))


def calculate_percent_change(old_value: float, new_value: float) -> float:
    """Calculate percentage change"""
    if old_value == 0:
        return 0
    return ((new_value - old_value) / old_value) * 100
