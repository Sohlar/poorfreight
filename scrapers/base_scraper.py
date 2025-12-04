"""
Base Scraper Class
Provides common functionality for all scrapers with retry logic and error handling
"""

from abc import ABC, abstractmethod
import requests
from bs4 import BeautifulSoup
import time
import logging
from datetime import datetime
from sqlalchemy.orm import Session
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.database import SessionLocal, ScraperRun

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class BaseScraper(ABC):
    """Base class for all scrapers"""

    def __init__(self, scraper_name: str, max_retries: int = 3, retry_delay: int = 5):
        self.scraper_name = scraper_name
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.logger = logging.getLogger(scraper_name)

        # Setup HTTP session
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })

    @abstractmethod
    def fetch(self):
        """Fetch raw data from source - must be implemented by subclass"""
        pass

    @abstractmethod
    def parse(self, raw_data):
        """Parse raw data into structured format - must be implemented by subclass"""
        pass

    @abstractmethod
    def store(self, parsed_data):
        """Store parsed data in database - must be implemented by subclass"""
        pass

    def run(self) -> bool:
        """
        Main execution method with retry logic and error tracking
        Returns True if successful, False otherwise
        """
        db = SessionLocal()
        scraper_run = ScraperRun(
            scraper_name=self.scraper_name,
            started_at=datetime.utcnow(),
            status='running'
        )
        db.add(scraper_run)
        db.commit()

        try:
            for attempt in range(self.max_retries):
                try:
                    self.logger.info(f"[{self.scraper_name}] Starting (attempt {attempt + 1}/{self.max_retries})")

                    # Execute scraping pipeline
                    raw_data = self.fetch()
                    self.logger.info(f"[{self.scraper_name}] Fetch complete")

                    parsed_data = self.parse(raw_data)
                    self.logger.info(f"[{self.scraper_name}] Parse complete: {len(parsed_data)} records")

                    self.store(parsed_data)
                    self.logger.info(f"[{self.scraper_name}] Store complete")

                    # Mark as successful
                    scraper_run.completed_at = datetime.utcnow()
                    scraper_run.status = 'success'
                    scraper_run.records_scraped = len(parsed_data)
                    db.commit()

                    self.logger.info(f"✅ [{self.scraper_name}] Success! Scraped {len(parsed_data)} records")
                    return True

                except Exception as e:
                    self.logger.error(f"❌ [{self.scraper_name}] Error on attempt {attempt + 1}: {e}")

                    if attempt < self.max_retries - 1:
                        self.logger.info(f"⏳ Retrying in {self.retry_delay} seconds...")
                        time.sleep(self.retry_delay)
                    else:
                        # Final attempt failed
                        scraper_run.completed_at = datetime.utcnow()
                        scraper_run.status = 'failed'
                        scraper_run.error_message = str(e)
                        db.commit()

                        self.logger.error(f"💀 [{self.scraper_name}] Failed after {self.max_retries} attempts")
                        return False

        finally:
            db.close()

    def get(self, url: str, **kwargs) -> requests.Response:
        """Wrapper for requests.get with common settings"""
        return self.session.get(url, timeout=30, **kwargs)

    def post(self, url: str, **kwargs) -> requests.Response:
        """Wrapper for requests.post with common settings"""
        return self.session.post(url, timeout=30, **kwargs)

    def soup(self, html: str) -> BeautifulSoup:
        """Create BeautifulSoup object from HTML"""
        return BeautifulSoup(html, 'lxml')
