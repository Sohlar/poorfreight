import useSWR from 'swr';
import {
  NewsResponse,
  DailyMetricsResponse,
  MacroMetricsResponse,
  LatestMetrics,
  SourcesResponse
} from './types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3001';

async function fetcher<T>(url: string): Promise<T> {
  const res = await fetch(url);
  if (!res.ok) {
    throw new Error('API request failed');
  }
  return res.json();
}

export function useNews(params?: {
  source?: string;
  q?: string;
  days?: number;
  limit?: number;
  offset?: number;
}) {
  const queryParams = new URLSearchParams();
  if (params?.source) queryParams.set('source', params.source);
  if (params?.q) queryParams.set('q', params.q);
  if (params?.days) queryParams.set('days', params.days.toString());
  if (params?.limit) queryParams.set('limit', params.limit.toString());
  if (params?.offset) queryParams.set('offset', params.offset.toString());

  const url = `${API_BASE}/api/news?${queryParams.toString()}`;

  const { data, error, isLoading, mutate } = useSWR<NewsResponse>(url, fetcher, {
    refreshInterval: 60000, // Refresh every minute
    revalidateOnFocus: false
  });

  return {
    news: data?.data || [],
    total: data?.total || 0,
    isLoading,
    isError: error,
    mutate
  };
}

export function useSources() {
  const url = `${API_BASE}/api/news/sources`;

  const { data, error, isLoading } = useSWR<SourcesResponse>(url, fetcher);

  return {
    sources: data?.data || [],
    isLoading,
    isError: error
  };
}

export function useDailyMetrics(params?: { from?: string; to?: string }) {
  const queryParams = new URLSearchParams();
  if (params?.from) queryParams.set('from', params.from);
  if (params?.to) queryParams.set('to', params.to);

  const url = `${API_BASE}/api/metrics/daily?${queryParams.toString()}`;

  const { data, error, isLoading } = useSWR<DailyMetricsResponse>(url, fetcher, {
    refreshInterval: 300000, // Refresh every 5 minutes
    revalidateOnFocus: false
  });

  return {
    metrics: data?.data || [],
    isLoading,
    isError: error
  };
}

export function useLatestMetrics() {
  const url = `${API_BASE}/api/metrics/daily/latest`;

  const { data, error, isLoading } = useSWR<LatestMetrics>(url, fetcher, {
    refreshInterval: 300000, // Refresh every 5 minutes
    revalidateOnFocus: false
  });

  return {
    latest: data?.data,
    previous: data?.previous,
    changes: data?.changes,
    isLoading,
    isError: error
  };
}

export function useMacroMetrics(params?: { from?: string; to?: string }) {
  const queryParams = new URLSearchParams();
  if (params?.from) queryParams.set('from', params.from);
  if (params?.to) queryParams.set('to', params.to);

  const url = `${API_BASE}/api/metrics/macro?${queryParams.toString()}`;

  const { data, error, isLoading } = useSWR<MacroMetricsResponse>(url, fetcher, {
    refreshInterval: 3600000, // Refresh every hour
    revalidateOnFocus: false
  });

  return {
    metrics: data?.data || [],
    isLoading,
    isError: error
  };
}
