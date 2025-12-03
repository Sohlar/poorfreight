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

export interface NewsQuery {
  source?: string;
  q?: string;
  days?: number;
  limit?: number;
  offset?: number;
}

export interface MetricsQuery {
  from?: string;
  to?: string;
}
