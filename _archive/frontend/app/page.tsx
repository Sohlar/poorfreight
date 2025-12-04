'use client';

import { useState } from 'react';
import { format, subDays } from 'date-fns';
import KpiCard from '@/components/KpiCard';
import TimeSeriesChart from '@/components/TimeSeriesChart';
import NewsList from '@/components/NewsList';
import FiltersBar from '@/components/FiltersBar';
import {
  useLatestMetrics,
  useDailyMetrics,
  useMacroMetrics,
  useNews,
  useSources
} from '@/lib/api';

export default function Dashboard() {
  const [newsFilters, setNewsFilters] = useState({
    selectedSources: [] as string[],
    searchQuery: '',
    days: 7
  });

  const [metricsRange, setMetricsRange] = useState({
    from: format(subDays(new Date(), 90), 'yyyy-MM-dd'),
    to: format(new Date(), 'yyyy-MM-dd')
  });

  // Fetch data
  const { latest, changes, isLoading: latestLoading } = useLatestMetrics();
  const { metrics: dailyMetrics, isLoading: dailyLoading } = useDailyMetrics(metricsRange);
  const { metrics: macroMetrics, isLoading: macroLoading } = useMacroMetrics();
  const { sources } = useSources();
  const { news, total: newsTotal, isLoading: newsLoading } = useNews({
    source: newsFilters.selectedSources.length > 0
      ? newsFilters.selectedSources.join(',')
      : undefined,
    q: newsFilters.searchQuery || undefined,
    days: newsFilters.days,
    limit: 20
  });

  return (
    <div className="min-h-screen bg-gray-900">
      {/* Header */}
      <header className="bg-gray-800 border-b border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-white">
                Freight Intelligence Dashboard
              </h1>
              <p className="text-gray-400 mt-1">
                Live freight market data and news
              </p>
            </div>
            <div className="text-right">
              <div className="text-sm text-gray-400">Last updated</div>
              <div className="text-white font-medium">
                {latest?.date ? format(new Date(latest.date), 'MMM d, yyyy') : 'Loading...'}
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* KPI Cards */}
        <section className="mb-8">
          <h2 className="text-xl font-semibold text-white mb-4">
            Latest Spot Rates & Fuel
          </h2>
          {latestLoading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {[1, 2, 3, 4].map((i) => (
                <div
                  key={i}
                  className="bg-gray-800 rounded-lg border border-gray-700 p-6 animate-pulse"
                >
                  <div className="h-4 bg-gray-700 rounded w-1/2 mb-4"></div>
                  <div className="h-8 bg-gray-700 rounded w-3/4"></div>
                </div>
              ))}
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <KpiCard
                title="Van Spot Rate"
                value={latest?.van_spot_index}
                change={changes?.van_spot_change}
                format="currency"
                decimals={3}
                unit="/mi"
              />
              <KpiCard
                title="Reefer Spot Rate"
                value={latest?.reefer_spot_index}
                change={changes?.reefer_spot_change}
                format="currency"
                decimals={3}
                unit="/mi"
              />
              <KpiCard
                title="Flatbed Spot Rate"
                value={latest?.flatbed_spot_index}
                change={changes?.flatbed_spot_change}
                format="currency"
                decimals={3}
                unit="/mi"
              />
              <KpiCard
                title="Diesel Price"
                value={latest?.diesel_usd_per_gal}
                change={changes?.diesel_change}
                format="currency"
              />
            </div>
          )}
        </section>

        {/* Charts Section */}
        <section className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-white">
              Spot Rate Trends
            </h2>
            <div className="flex gap-2">
              {[30, 90].map((days) => (
                <button
                  key={days}
                  onClick={() =>
                    setMetricsRange({
                      from: format(subDays(new Date(), days), 'yyyy-MM-dd'),
                      to: format(new Date(), 'yyyy-MM-dd')
                    })
                  }
                  className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
                    metricsRange.from === format(subDays(new Date(), days), 'yyyy-MM-dd')
                      ? 'bg-primary-600 text-white'
                      : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
                  }`}
                >
                  {days}D
                </button>
              ))}
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <TimeSeriesChart
              data={dailyMetrics}
              series={[
                { key: 'van_spot_index', name: 'Van', color: '#3b82f6' },
                { key: 'reefer_spot_index', name: 'Reefer', color: '#10b981' },
                { key: 'flatbed_spot_index', name: 'Flatbed', color: '#f59e0b' }
              ]}
              xAxisKey="date"
              yAxisLabel="Rate ($/mi)"
              formatYAxis={(value) => `$${value.toFixed(2)}`}
            />
            <TimeSeriesChart
              data={dailyMetrics}
              series={[
                { key: 'diesel_usd_per_gal', name: 'Diesel', color: '#ef4444' }
              ]}
              xAxisKey="date"
              yAxisLabel="Price ($/gal)"
              formatYAxis={(value) => `$${value.toFixed(2)}`}
            />
          </div>
        </section>

        {/* Macro Metrics Chart */}
        <section className="mb-8">
          <h2 className="text-xl font-semibold text-white mb-4">
            Macro Freight Indices
          </h2>
          <TimeSeriesChart
            data={macroMetrics}
            series={[
              { key: 'cass_shipments_index', name: 'Cass Shipments', color: '#8b5cf6' },
              { key: 'ata_tonnage_index', name: 'ATA Tonnage', color: '#ec4899' },
              { key: 'ftr_trucking_conditions_index', name: 'FTR Conditions', color: '#06b6d4' }
            ]}
            xAxisKey="month"
            height={300}
          />
        </section>

        {/* News Section */}
        <section>
          <h2 className="text-xl font-semibold text-white mb-4">
            Freight News ({newsTotal})
          </h2>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-1">
              <FiltersBar sources={sources} onFilterChange={setNewsFilters} />
            </div>
            <div className="lg:col-span-2">
              <NewsList
                articles={news}
                searchQuery={newsFilters.searchQuery}
                isLoading={newsLoading}
              />
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="bg-gray-800 border-t border-gray-700 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <p className="text-center text-gray-400 text-sm">
            Data sources: FreightWaves, Supply Chain Dive, Transport Topics, JOC, DOE/EIA
          </p>
          <p className="text-center text-gray-500 text-xs mt-2">
            Spot rate data is for demonstration purposes. Replace with live DAT/Truckstop data for production.
          </p>
        </div>
      </footer>
    </div>
  );
}
