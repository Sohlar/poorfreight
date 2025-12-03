'use client';

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import { formatDate } from '@/lib/utils';

interface DataSeries {
  key: string;
  name: string;
  color: string;
}

interface TimeSeriesChartProps {
  data: any[];
  series: DataSeries[];
  xAxisKey: string;
  height?: number;
  yAxisLabel?: string;
  formatYAxis?: (value: number) => string;
}

export default function TimeSeriesChart({
  data,
  series,
  xAxisKey,
  height = 300,
  yAxisLabel,
  formatYAxis
}: TimeSeriesChartProps) {
  if (!data || data.length === 0) {
    return (
      <div
        className="flex items-center justify-center bg-gray-800 rounded-lg border border-gray-700"
        style={{ height }}
      >
        <p className="text-gray-400">No data available</p>
      </div>
    );
  }

  return (
    <div className="bg-gray-800 rounded-lg border border-gray-700 p-4">
      <ResponsiveContainer width="100%" height={height}>
        <LineChart
          data={data}
          margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
          <XAxis
            dataKey={xAxisKey}
            stroke="#9CA3AF"
            tick={{ fill: '#9CA3AF' }}
            tickFormatter={(value) => {
              if (xAxisKey === 'date') {
                return formatDate(value);
              }
              return value;
            }}
          />
          <YAxis
            stroke="#9CA3AF"
            tick={{ fill: '#9CA3AF' }}
            label={
              yAxisLabel
                ? {
                    value: yAxisLabel,
                    angle: -90,
                    position: 'insideLeft',
                    fill: '#9CA3AF'
                  }
                : undefined
            }
            tickFormatter={formatYAxis}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: '#1F2937',
              border: '1px solid #374151',
              borderRadius: '0.5rem',
              color: '#F3F4F6'
            }}
            labelFormatter={(value) => {
              if (xAxisKey === 'date') {
                return formatDate(value as string);
              }
              return value;
            }}
            formatter={(value: number) => {
              if (formatYAxis) {
                return formatYAxis(value);
              }
              return value.toFixed(2);
            }}
          />
          <Legend
            wrapperStyle={{ color: '#9CA3AF' }}
            iconType="line"
          />
          {series.map((s) => (
            <Line
              key={s.key}
              type="monotone"
              dataKey={s.key}
              stroke={s.color}
              name={s.name}
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 6 }}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
