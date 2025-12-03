import db from './connection';

console.log('Initializing database schema...');

// News articles table
db.exec(`
  CREATE TABLE IF NOT EXISTS news_articles (
    id TEXT PRIMARY KEY,
    source TEXT NOT NULL,
    title TEXT NOT NULL,
    url TEXT NOT NULL UNIQUE,
    published_at TEXT NOT NULL,
    summary TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(source, title)
  );

  CREATE INDEX IF NOT EXISTS idx_news_source ON news_articles(source);
  CREATE INDEX IF NOT EXISTS idx_news_published ON news_articles(published_at DESC);
`);

// Daily metrics table
db.exec(`
  CREATE TABLE IF NOT EXISTS daily_metrics (
    date TEXT PRIMARY KEY,
    van_spot_index REAL,
    reefer_spot_index REAL,
    flatbed_spot_index REAL,
    diesel_usd_per_gal REAL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
  );

  CREATE INDEX IF NOT EXISTS idx_daily_date ON daily_metrics(date DESC);
`);

// Macro metrics table
db.exec(`
  CREATE TABLE IF NOT EXISTS macro_metrics (
    month TEXT PRIMARY KEY,
    cass_shipments_index REAL,
    ata_tonnage_index REAL,
    ftr_trucking_conditions_index REAL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
  );

  CREATE INDEX IF NOT EXISTS idx_macro_month ON macro_metrics(month DESC);
`);

console.log('Database schema initialized successfully!');

db.close();
