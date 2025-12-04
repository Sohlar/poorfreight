"""
Database connection and schema initialization
SQLite database for freight intelligence data
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import os

# Database path
DB_PATH = os.getenv("DATABASE_PATH", "data/freight.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False  # Set to True for SQL debugging
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


# === MODELS ===

class NewsArticle(Base):
    """News articles from freight industry sources"""
    __tablename__ = "news_articles"

    id = Column(String, primary_key=True)
    source = Column(String, nullable=False, index=True)
    title = Column(String, nullable=False)
    url = Column(String, nullable=False, unique=True)
    published_at = Column(DateTime, nullable=False, index=True)
    summary = Column(Text)
    full_content = Column(Text)  # Full article text
    tags = Column(String)  # Comma-separated: "capacity,rates,diesel"
    importance = Column(Integer, default=1)  # 1-5 rating
    notes = Column(Text)  # User annotations
    read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DailyMetric(Base):
    """Daily freight metrics (spot rates, diesel prices)"""
    __tablename__ = "daily_metrics"

    date = Column(String, primary_key=True)  # YYYY-MM-DD
    van_spot_index = Column(Float)
    reefer_spot_index = Column(Float)
    flatbed_spot_index = Column(Float)
    diesel_usd_per_gal = Column(Float)

    # FRED economic indicators (daily)
    gas_price = Column(Float)  # GASREGW
    oil_price = Column(Float)  # DCOILWTICO

    source = Column(String)
    confidence = Column(Float)  # 0.0 to 1.0
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DieselPrice(Base):
    """Regional diesel prices (national and PADD regions)"""
    __tablename__ = "diesel_prices"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(String, nullable=False, index=True)  # YYYY-MM-DD
    region_code = Column(String, nullable=False, index=True)  # NUS, R10, R20, R30, R40, R50
    region_name = Column(String)  # "U.S.", "East Coast (PADD 1)", etc.
    price = Column(Float, nullable=False)  # USD per gallon
    series_description = Column(Text)  # Full series description
    source = Column(String, default='EIA')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class MacroMetric(Base):
    """Monthly macro freight indices"""
    __tablename__ = "macro_metrics"

    month = Column(String, primary_key=True)  # YYYY-MM
    cass_shipments_index = Column(Float)
    cass_expenditures_index = Column(Float)
    ata_tonnage_index = Column(Float)
    ftr_trucking_conditions_index = Column(Float)

    # FRED economic indicators (monthly)
    industrial_production = Column(Float)  # IPMAN
    ism_pmi = Column(Float)  # ISM Manufacturing PMI
    retail_sales = Column(Float)  # RSXFS
    consumer_sentiment = Column(Float)  # UMCSENT
    truck_transport_index = Column(Float)  # TRUCKD11

    source = Column(String)
    confidence = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Lane(Base):
    """Freight lanes (origin-destination pairs)"""
    __tablename__ = "lanes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    origin = Column(String, nullable=False, index=True)
    destination = Column(String, nullable=False, index=True)
    equipment_type = Column(String, default="van")  # van, reefer, flatbed
    distance_miles = Column(Float)
    volume_rank = Column(Integer)  # From BTS FAF data
    created_at = Column(DateTime, default=datetime.utcnow)


class Rate(Base):
    """Spot and contract rates by lane"""
    __tablename__ = "rates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    lane_id = Column(Integer, nullable=False, index=True)
    date = Column(String, nullable=False, index=True)  # YYYY-MM-DD
    rate_per_mile = Column(Float, nullable=False)
    is_spot = Column(Boolean, default=True)
    is_contract = Column(Boolean, default=False)
    source = Column(String)
    confidence_score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)


class Carrier(Base):
    """Carrier information"""
    __tablename__ = "carriers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    mc_number = Column(String, unique=True)
    dot_number = Column(String, unique=True)
    status = Column(String)  # active, revoked, closed
    authority_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ScraperRun(Base):
    """Track scraper execution history"""
    __tablename__ = "scraper_runs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    scraper_name = Column(String, nullable=False, index=True)
    started_at = Column(DateTime, nullable=False)
    completed_at = Column(DateTime)
    status = Column(String)  # success, failed, running
    records_scraped = Column(Integer, default=0)
    error_message = Column(Text)


# === INITIALIZATION ===

def init_database():
    """Create all tables"""
    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)

    # Create tables
    Base.metadata.create_all(bind=engine)
    print(f"✅ Database initialized at {DB_PATH}")


def get_db():
    """Get database session (for dependency injection)"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


if __name__ == "__main__":
    # Initialize database when run directly
    init_database()
