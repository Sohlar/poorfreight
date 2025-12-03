import db from './connection';
import { NewsArticle, DailyMetric, MacroMetric, NewsQuery, MetricsQuery } from '../types';
import { subDays, format } from 'date-fns';

export const NewsModel = {
  insert(article: NewsArticle): void {
    const stmt = db.prepare(`
      INSERT OR REPLACE INTO news_articles (id, source, title, url, published_at, summary)
      VALUES (?, ?, ?, ?, ?, ?)
    `);
    stmt.run(
      article.id,
      article.source,
      article.title,
      article.url,
      article.published_at,
      article.summary
    );
  },

  insertMany(articles: NewsArticle[]): number {
    const stmt = db.prepare(`
      INSERT OR REPLACE INTO news_articles (id, source, title, url, published_at, summary)
      VALUES (?, ?, ?, ?, ?, ?)
    `);

    const insertMany = db.transaction((articles: NewsArticle[]) => {
      for (const article of articles) {
        stmt.run(
          article.id,
          article.source,
          article.title,
          article.url,
          article.published_at,
          article.summary
        );
      }
    });

    insertMany(articles);
    return articles.length;
  },

  query(params: NewsQuery): NewsArticle[] {
    let sql = 'SELECT * FROM news_articles WHERE 1=1';
    const bindings: any[] = [];

    // Filter by source
    if (params.source) {
      const sources = params.source.split(',').map(s => s.trim());
      const placeholders = sources.map(() => '?').join(',');
      sql += ` AND source IN (${placeholders})`;
      bindings.push(...sources);
    }

    // Text search on title and summary
    if (params.q) {
      sql += ` AND (title LIKE ? OR summary LIKE ?)`;
      const searchTerm = `%${params.q}%`;
      bindings.push(searchTerm, searchTerm);
    }

    // Filter by days
    if (params.days) {
      const cutoffDate = format(subDays(new Date(), params.days), 'yyyy-MM-dd');
      sql += ` AND date(published_at) >= date(?)`;
      bindings.push(cutoffDate);
    }

    // Order and pagination
    sql += ' ORDER BY published_at DESC';

    if (params.limit) {
      sql += ' LIMIT ?';
      bindings.push(params.limit);
    }

    if (params.offset) {
      sql += ' OFFSET ?';
      bindings.push(params.offset);
    }

    const stmt = db.prepare(sql);
    return stmt.all(...bindings) as NewsArticle[];
  },

  count(params: NewsQuery): number {
    let sql = 'SELECT COUNT(*) as count FROM news_articles WHERE 1=1';
    const bindings: any[] = [];

    if (params.source) {
      const sources = params.source.split(',').map(s => s.trim());
      const placeholders = sources.map(() => '?').join(',');
      sql += ` AND source IN (${placeholders})`;
      bindings.push(...sources);
    }

    if (params.q) {
      sql += ` AND (title LIKE ? OR summary LIKE ?)`;
      const searchTerm = `%${params.q}%`;
      bindings.push(searchTerm, searchTerm);
    }

    if (params.days) {
      const cutoffDate = format(subDays(new Date(), params.days), 'yyyy-MM-dd');
      sql += ` AND date(published_at) >= date(?)`;
      bindings.push(cutoffDate);
    }

    const stmt = db.prepare(sql);
    const result = stmt.get(...bindings) as { count: number };
    return result.count;
  }
};

export const DailyMetricsModel = {
  upsert(metric: DailyMetric): void {
    const stmt = db.prepare(`
      INSERT INTO daily_metrics (date, van_spot_index, reefer_spot_index, flatbed_spot_index, diesel_usd_per_gal, updated_at)
      VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
      ON CONFLICT(date) DO UPDATE SET
        van_spot_index = COALESCE(excluded.van_spot_index, van_spot_index),
        reefer_spot_index = COALESCE(excluded.reefer_spot_index, reefer_spot_index),
        flatbed_spot_index = COALESCE(excluded.flatbed_spot_index, flatbed_spot_index),
        diesel_usd_per_gal = COALESCE(excluded.diesel_usd_per_gal, diesel_usd_per_gal),
        updated_at = CURRENT_TIMESTAMP
    `);
    stmt.run(
      metric.date,
      metric.van_spot_index,
      metric.reefer_spot_index,
      metric.flatbed_spot_index,
      metric.diesel_usd_per_gal
    );
  },

  query(params: MetricsQuery): DailyMetric[] {
    let sql = 'SELECT * FROM daily_metrics WHERE 1=1';
    const bindings: any[] = [];

    if (params.from) {
      sql += ' AND date >= ?';
      bindings.push(params.from);
    }

    if (params.to) {
      sql += ' AND date <= ?';
      bindings.push(params.to);
    }

    sql += ' ORDER BY date ASC';

    const stmt = db.prepare(sql);
    return stmt.all(...bindings) as DailyMetric[];
  },

  getLatest(): DailyMetric | undefined {
    const stmt = db.prepare('SELECT * FROM daily_metrics ORDER BY date DESC LIMIT 1');
    return stmt.get() as DailyMetric | undefined;
  },

  getPrevious(beforeDate: string): DailyMetric | undefined {
    const stmt = db.prepare('SELECT * FROM daily_metrics WHERE date < ? ORDER BY date DESC LIMIT 1');
    return stmt.get(beforeDate) as DailyMetric | undefined;
  }
};

export const MacroMetricsModel = {
  upsert(metric: MacroMetric): void {
    const stmt = db.prepare(`
      INSERT INTO macro_metrics (month, cass_shipments_index, ata_tonnage_index, ftr_trucking_conditions_index, updated_at)
      VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
      ON CONFLICT(month) DO UPDATE SET
        cass_shipments_index = COALESCE(excluded.cass_shipments_index, cass_shipments_index),
        ata_tonnage_index = COALESCE(excluded.ata_tonnage_index, ata_tonnage_index),
        ftr_trucking_conditions_index = COALESCE(excluded.ftr_trucking_conditions_index, ftr_trucking_conditions_index),
        updated_at = CURRENT_TIMESTAMP
    `);
    stmt.run(
      metric.month,
      metric.cass_shipments_index,
      metric.ata_tonnage_index,
      metric.ftr_trucking_conditions_index
    );
  },

  query(params: MetricsQuery): MacroMetric[] {
    let sql = 'SELECT * FROM macro_metrics WHERE 1=1';
    const bindings: any[] = [];

    if (params.from) {
      sql += ' AND month >= ?';
      bindings.push(params.from);
    }

    if (params.to) {
      sql += ' AND month <= ?';
      bindings.push(params.to);
    }

    sql += ' ORDER BY month ASC';

    const stmt = db.prepare(sql);
    return stmt.all(...bindings) as MacroMetric[];
  },

  getAll(): MacroMetric[] {
    const stmt = db.prepare('SELECT * FROM macro_metrics ORDER BY month DESC');
    return stmt.all() as MacroMetric[];
  }
};
