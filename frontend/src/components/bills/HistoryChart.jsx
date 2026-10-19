import React, { useState } from 'react';
import { Card } from '../ui/Card';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';
import { TrendingUp, BarChart2 } from 'lucide-react';

export function HistoryChart({ history = [] }) {
  const [metric, setMetric] = useState('units'); // 'units' | 'bill'

  if (!history || history.length === 0) {
    return (
      <Card className="text-center py-10">
        <p className="text-xs text-ink-400">12-month billing history table was not available on this bill scan.</p>
      </Card>
    );
  }

  const chartData = history.map((item) => ({
    name: item.month || '—',
    units: item.units != null ? Number(item.units) : 0,
    bill: item.bill != null ? Number(item.bill) : 0,
  }));

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-ink-950 text-white text-xs p-2.5 rounded-lg shadow-elevated border border-ink-800">
          <p className="font-semibold text-ink-300 text-[11px] mb-1 font-mono uppercase tracking-wider">{label}</p>
          <p className="text-white font-bold font-mono text-sm">
            {metric === 'units'
              ? `${payload[0].value.toLocaleString()} kWh Units`
              : `Rs. ${Number(payload[0].value).toLocaleString()}`}
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <Card className="p-5 space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-ink-200/80">
        <div className="flex items-center space-x-2">
          <TrendingUp className="w-4 h-4 text-ink-700" />
          <h3 className="text-xs font-semibold uppercase tracking-wider text-ink-900">
            Historical Consumption Profile (12-Month)
          </h3>
        </div>

        <div className="inline-flex rounded-lg bg-canvas p-0.5 border border-ink-200/90 text-xs">
          <button
            onClick={() => setMetric('units')}
            className={`px-3 py-1 rounded-md text-xs font-medium transition-colors ${
              metric === 'units'
                ? 'bg-white text-ink-950 shadow-subtle font-semibold'
                : 'text-ink-500 hover:text-ink-900'
            }`}
          >
            Energy (kWh)
          </button>
          <button
            onClick={() => setMetric('bill')}
            className={`px-3 py-1 rounded-md text-xs font-medium transition-colors ${
              metric === 'bill'
                ? 'bg-white text-ink-950 shadow-subtle font-semibold'
                : 'text-ink-500 hover:text-ink-900'
            }`}
          >
            Billed Amount (PKR)
          </button>
        </div>
      </div>

      <div className="h-64 sm:h-72 w-full pt-2">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData} margin={{ top: 10, right: 10, left: -15, bottom: 25 }}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E5E7EB" />
            <XAxis
              dataKey="name"
              axisLine={false}
              tickLine={false}
              tick={{ fill: '#71717A', fontSize: 10, fontFamily: 'monospace' }}
              angle={-30}
              textAnchor="end"
              height={40}
            />
            <YAxis
              axisLine={false}
              tickLine={false}
              tick={{ fill: '#71717A', fontSize: 10, fontFamily: 'monospace' }}
              tickFormatter={(v) => (v >= 1000 ? `${(v / 1000).toFixed(0)}k` : v)}
            />
            <Tooltip content={<CustomTooltip />} />
            <Bar
              dataKey={metric}
              fill={metric === 'units' ? '#15803d' : '#18181b'}
              radius={[3, 3, 0, 0]}
              maxBarSize={36}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </Card>
  );
}
