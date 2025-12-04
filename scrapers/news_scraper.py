"""
Enhanced News Scraper
Scrapes RSS feeds from freight industry sources with full article extraction and auto-tagging
"""

import feedparser
import hashlib
from datetime import datetime
from typing import List, Dict
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scrapers.base_scraper import BaseScraper
from lib.database import SessionLocal, NewsArticle

# Try to import newspaper3k for full article extraction
try:
    from newspaper import Article
    NEWSPAPER_AVAILABLE = True
except ImportError:
    NEWSPAPER_AVAILABLE = False
    print("⚠️  newspaper3k not available - will use RSS summaries only")


class NewsScraperConfig:
    """Configuration for news sources"""
    SOURCES = [
        {
            'name': 'FreightWaves',
            'url': 'https://www.freightwaves.com/feed',
            'priority': 'high'
        },
        {
            'name': 'Supply Chain Dive',
            'url': 'https://www.supplychaindive.com/feeds/news/',
            'priority': 'high'
        },
        {
            'name': 'Transport Topics',
            'url': 'https://www.ttnews.com/rss/feed/top-news',
            'priority': 'medium'
        },
        {
            'name': 'JOC',
            'url': 'https://www.joc.com/rss/all-categories',
            'priority': 'high'
        }
    ]

    # Keywords for auto-tagging
    TAG_KEYWORDS = {
        'capacity': ['capacity', 'tight', 'shortage', 'availability', 'surplus'],
        'rates': ['rate', 'pricing', 'cost', 'price', 'tariff'],
        'diesel': ['diesel', 'fuel', 'energy', 'gas'],
        'ltl': ['less-than-truckload', 'ltl', 'less than truckload'],
        'ftl': ['full-truckload', 'ftl', 'full truckload', 'truckload'],
        'contracts': ['contract', 'bid', 'rfp', 'agreement'],
        'economy': ['economy', 'gdp', 'recession', 'demand', 'growth'],
        'regulation': ['fmcsa', 'regulation', 'compliance', 'dot', 'law'],
        'technology': ['technology', 'digital', 'automation', 'software'],
        'labor': ['driver', 'labor', 'wage', 'employment', 'turnover'],
        'merger': ['merger', 'acquisition', 'bought', 'consolidation'],
        'bankruptcy': ['bankruptcy', 'closure', 'shutdown', 'failed'],
    }

    # Important keywords (boost importance score)
    IMPORTANT_KEYWORDS = [
        'breaking', 'major', 'crisis', 'shortage', 'spike',
        'record', 'unprecedented', 'significant', 'urgent'
    ]


class NewsScraper(BaseScraper):
    """Scrape freight news from RSS feeds"""

    def __init__(self):
        super().__init__('news_scraper')
        self.config = NewsScraperConfig()

    def fetch(self) -> List[feedparser.FeedParserDict]:
        """Fetch all RSS feeds"""
        all_feeds = []

        for source in self.config.SOURCES:
            try:
                self.logger.info(f"Fetching {source['name']}...")
                feed = feedparser.parse(source['url'])

                if feed.bozo:  # Feed parsing error
                    self.logger.warning(f"Feed parsing warning for {source['name']}: {feed.bozo_exception}")

                # Add source info to each entry
                for entry in feed.entries:
                    entry['_source_name'] = source['name']
                    entry['_source_priority'] = source['priority']

                all_feeds.extend(feed.entries)
                self.logger.info(f"  → {len(feed.entries)} articles from {source['name']}")

            except Exception as e:
                self.logger.error(f"Error fetching {source['name']}: {e}")

        return all_feeds

    def parse(self, feed_entries: List) -> List[Dict]:
        """Parse feed entries into structured articles"""
        articles = []

        for entry in feed_entries:
            try:
                # Generate unique ID
                article_id = self._generate_id(entry)

                # Extract basic info
                title = entry.get('title', 'Untitled')
                url = entry.get('link', '')
                source = entry.get('_source_name', 'Unknown')

                # Parse published date
                published_at = self._parse_date(entry)

                # Get summary
                summary = self._extract_summary(entry)

                # Extract full content if newspaper3k available
                full_content = None
                if NEWSPAPER_AVAILABLE and url:
                    full_content = self._extract_full_article(url)

                # Auto-tag the article
                tags = self._auto_tag(title, summary, full_content)

                # Auto-rate importance
                importance = self._auto_rate_importance(title, summary, tags)

                articles.append({
                    'id': article_id,
                    'source': source,
                    'title': title,
                    'url': url,
                    'published_at': published_at,
                    'summary': summary,
                    'full_content': full_content,
                    'tags': ','.join(tags),
                    'importance': importance,
                    'notes': None,
                    'read': False
                })

            except Exception as e:
                self.logger.warning(f"Error parsing entry: {e}")
                continue

        return articles

    def store(self, articles: List[Dict]) -> None:
        """Store articles in database"""
        db = SessionLocal()
        stored_count = 0
        updated_count = 0

        try:
            for article_data in articles:
                # Check if article already exists
                existing = db.query(NewsArticle).filter_by(id=article_data['id']).first()

                if existing:
                    # Update existing article (but preserve user annotations)
                    existing.summary = article_data['summary']
                    existing.full_content = article_data['full_content']
                    if not existing.tags:  # Only auto-tag if no tags yet
                        existing.tags = article_data['tags']
                    if existing.importance == 1:  # Only auto-rate if not rated by user
                        existing.importance = article_data['importance']
                    updated_count += 1
                else:
                    # Create new article
                    new_article = NewsArticle(**article_data)
                    db.add(new_article)
                    stored_count += 1

            db.commit()
            self.logger.info(f"Stored {stored_count} new articles, updated {updated_count} existing")

        except Exception as e:
            db.rollback()
            self.logger.error(f"Error storing articles: {e}")
            raise
        finally:
            db.close()

    # === Helper Methods ===

    def _generate_id(self, entry) -> str:
        """Generate unique ID for article"""
        url = entry.get('link', '')
        title = entry.get('title', '')
        unique_string = f"{url}{title}"
        return hashlib.md5(unique_string.encode()).hexdigest()

    def _parse_date(self, entry) -> datetime:
        """Parse published date from feed entry"""
        # Try different date fields
        date_str = entry.get('published') or entry.get('pubDate') or entry.get('updated')

        if date_str:
            try:
                # feedparser normalizes dates to time struct
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    from time import mktime
                    return datetime.fromtimestamp(mktime(entry.published_parsed))
            except:
                pass

        # Fallback to now
        return datetime.utcnow()

    def _extract_summary(self, entry) -> str:
        """Extract summary from feed entry"""
        # Try multiple fields
        content = entry.get('summary') or entry.get('description') or entry.get('content', [{}])[0].get('value', '')

        if not content:
            return ''

        # Strip HTML tags
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(content, 'html.parser')
        text = soup.get_text()

        # Clean up whitespace
        text = ' '.join(text.split())

        # Truncate to 500 chars
        if len(text) > 500:
            text = text[:500] + '...'

        return text

    def _extract_full_article(self, url: str) -> str:
        """Extract full article content using newspaper3k"""
        try:
            article = Article(url)
            article.download()
            article.parse()
            return article.text
        except Exception as e:
            self.logger.debug(f"Could not extract full article from {url}: {e}")
            return None

    def _auto_tag(self, title: str, summary: str, full_content: str = None) -> List[str]:
        """Auto-tag article based on keywords"""
        text = f"{title} {summary or ''} {full_content or ''}".lower()

        tags = []
        for tag, keywords in self.config.TAG_KEYWORDS.items():
            if any(keyword in text for keyword in keywords):
                tags.append(tag)

        return tags

    def _auto_rate_importance(self, title: str, summary: str, tags: List[str]) -> int:
        """Auto-rate article importance 1-5"""
        score = 1

        # High-priority tags
        priority_tags = ['capacity', 'rates', 'bankruptcy', 'merger']
        if any(tag in tags for tag in priority_tags):
            score += 1

        # Important keywords in title
        title_lower = title.lower()
        if any(keyword in title_lower for keyword in self.config.IMPORTANT_KEYWORDS):
            score += 1

        # Multiple relevant tags
        if len(tags) >= 3:
            score += 1

        return min(score, 5)  # Cap at 5


def main():
    """Run news scraper"""
    scraper = NewsScraper()
    success = scraper.run()

    if success:
        print("✅ News scraper completed successfully")
    else:
        print("❌ News scraper failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
