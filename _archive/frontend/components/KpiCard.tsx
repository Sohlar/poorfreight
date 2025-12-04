'use client';

import { formatNumber, formatCurrency, formatChange } from '@/lib/utils';

interface KpiCardProps {
  title: string;
  value: number | null | undefined;
  change?: number | null;
  format?: 'number' | 'currency';
  decimals?: number;
  unit?: string;
}

export default function KpiCard({
  title,
  value,
  change,
  format = 'number',
  decimals = 2,
  unit
}: KpiCardProps) {
  const formattedValue =
    format === 'currency'
      ? formatCurrency(value)
      : formatNumber(value, decimals) + (unit ? ` ${unit}` : '');

  const changeInfo = change !== undefined ? formatChange(change) : null;

  return (
    <div className="bg-gray-800 rounded-lg border border-gray-700 p-6 hover:border-gray-600 transition-colors">
      <h3 className="text-gray-400 text-sm font-medium mb-2">{title}</h3>
      <div className="flex items-baseline justify-between">
        <div className="text-3xl font-bold text-white">{formattedValue}</div>
        {changeInfo && (
          <div
            className={`flex items-center text-sm font-medium ${
              changeInfo.isPositive
                ? 'text-green-400'
                : changeInfo.isNegative
                ? 'text-red-400'
                : 'text-gray-400'
            }`}
          >
            {changeInfo.isPositive && (
              <svg
                className="w-4 h-4 mr-1"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M5 10l7-7m0 0l7 7m-7-7v18"
                />
              </svg>
            )}
            {changeInfo.isNegative && (
              <svg
                className="w-4 h-4 mr-1"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M19 14l-7 7m0 0l-7-7m7 7V3"
                />
              </svg>
            )}
            <span>{changeInfo.text}</span>
          </div>
        )}
      </div>
    </div>
  );
}
