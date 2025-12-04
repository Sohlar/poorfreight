export interface NewsArticle {
  id: string;
  source: string;
  title: string;
  url: string;
  published_at: string;
  summary: string;
}

export interface DailyMetric {
  date: string;
  van_spot_index: number | null;
  reefer_spot_index: number | null;
  flatbed_spot_index: number | null;
  diesel_usd_per_gal: number | null;
}

export interface MacroMetric {
  month: string;
  cass_shipments_index: number | null;
  ata_tonnage_index: number | null;
  ftr_trucking_conditions_index: number | null;
}

export interface LatestMetrics {
  data: DailyMetric;
  previous: DailyMetric | null;
  changes: {
    van_spot_change: number | null;
    reefer_spot_change: number | null;
    flatbed_spot_change: number | null;
    diesel_change: number | null;
  } | null;
}

export interface NewsResponse {
  data: NewsArticle[];
  total: number;
  limit: number;
  offset: number;
}

export interface DailyMetricsResponse {
  data: DailyMetric[];
}

export interface MacroMetricsResponse {
  data: MacroMetric[];
}

export interface SourcesResponse {
  data: string[];
}
