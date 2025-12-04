'use client';

import { useState, useEffect } from 'react';
import { format, subDays } from 'date-fns';

interface FiltersBarProps {
  sources: string[];
  onFilterChange: (filters: {
    selectedSources: string[];
    searchQuery: string;
    days: number;
  }) => void;
}

export default function FiltersBar({ sources, onFilterChange }: FiltersBarProps) {
  const [selectedSources, setSelectedSources] = useState<string[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [days, setDays] = useState(7);

  useEffect(() => {
    onFilterChange({ selectedSources, searchQuery, days });
  }, [selectedSources, searchQuery, days]);

  const toggleSource = (source: string) => {
    setSelectedSources((prev) =>
      prev.includes(source)
        ? prev.filter((s) => s !== source)
        : [...prev, source]
    );
  };

  const clearFilters = () => {
    setSelectedSources([]);
    setSearchQuery('');
    setDays(7);
  };

  const hasActiveFilters = selectedSources.length > 0 || searchQuery.length > 0;

  return (
    <div className="bg-gray-800 rounded-lg border border-gray-700 p-4 space-y-4">
      {/* Search input */}
      <div>
        <label htmlFor="search" className="block text-sm font-medium text-gray-300 mb-2">
          Search articles
        </label>
        <input
          type="text"
          id="search"
          placeholder="Enter keywords..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
        />
      </div>

      {/* Date range selector */}
      <div>
        <label className="block text-sm font-medium text-gray-300 mb-2">
          Date range
        </label>
        <div className="flex gap-2">
          {[7, 30, 90].map((d) => (
            <button
              key={d}
              onClick={() => setDays(d)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                days === d
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-900 text-gray-300 hover:bg-gray-700'
              }`}
            >
              {d} days
            </button>
          ))}
        </div>
      </div>

      {/* Source selector */}
      <div>
        <label className="block text-sm font-medium text-gray-300 mb-2">
          News sources
        </label>
        <div className="flex flex-wrap gap-2">
          {sources.map((source) => (
            <button
              key={source}
              onClick={() => toggleSource(source)}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                selectedSources.includes(source)
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-900 text-gray-300 hover:bg-gray-700'
              }`}
            >
              {source}
            </button>
          ))}
        </div>
      </div>

      {/* Clear filters button */}
      {hasActiveFilters && (
        <div className="pt-2">
          <button
            onClick={clearFilters}
            className="text-sm text-primary-400 hover:text-primary-300 font-medium"
          >
            Clear all filters
          </button>
        </div>
      )}
    </div>
  );
}
