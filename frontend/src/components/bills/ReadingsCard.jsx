import React from 'react';
import { Card } from '../ui/Card';
import { Gauge, Zap, Activity, Tag, ArrowRight } from 'lucide-react';

export function ReadingsCard({ level1 }) {
  if (!level1) return null;

  return (
    <Card className="p-5 space-y-4">
      <div className="flex items-center justify-between pb-3 border-b border-ink-200/80">
        <div className="flex items-center space-x-2">
          <Zap className="w-4 h-4 text-emerald-800" />
          <h3 className="text-xs font-semibold uppercase tracking-wider text-ink-900">
            Metering & Tariff Specification
          </h3>
        </div>
        <span className="text-[11px] font-mono text-ink-400">
          Month: {level1.bill_month || 'N/A'}
        </span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        {/* Units Consumed */}
        <div className="p-3.5 rounded-lg bg-canvas border border-ink-200/70">
          <span className="text-[10px] uppercase font-semibold text-ink-400 block tracking-wider">
            Units Billed
          </span>
          <div className="text-xl font-bold text-ink-950 font-mono tabular-numbers mt-0.5">
            {level1.units_consumed != null ? `${level1.units_consumed}` : '—'}
            <span className="text-xs font-sans text-ink-400 font-normal ml-1">kWh</span>
          </div>
          <span className="text-[10px] text-ink-500 mt-1 block">
            Current billing cycle usage
          </span>
        </div>

        {/* Meter Readings */}
        <div className="p-3.5 rounded-lg bg-canvas border border-ink-200/70">
          <span className="text-[10px] uppercase font-semibold text-ink-400 block tracking-wider">
            Meter Reading Interval
          </span>
          <div className="text-sm font-semibold text-ink-900 font-mono tabular-numbers mt-1 flex items-center space-x-1.5">
            <span>{level1.previous_reading != null ? level1.previous_reading : '—'}</span>
            <ArrowRight className="w-3 h-3 text-ink-400 shrink-0" />
            <span className="text-ink-950 font-bold">
              {level1.current_reading != null ? level1.current_reading : '—'}
            </span>
          </div>
          <span className="text-[10px] text-ink-500 mt-1 block">
            Previous → Current index
          </span>
        </div>

        {/* Sanctioned Load */}
        <div className="p-3.5 rounded-lg bg-canvas border border-ink-200/70">
          <span className="text-[10px] uppercase font-semibold text-ink-400 block tracking-wider">
            Sanctioned Load
          </span>
          <div className="text-xl font-bold text-ink-900 font-mono tabular-numbers mt-0.5">
            {level1.sanctioned_load_kw != null ? `${level1.sanctioned_load_kw}` : '—'}
            <span className="text-xs font-sans text-ink-400 font-normal ml-1">kW</span>
          </div>
          <span className="text-[10px] text-ink-500 mt-1 block">
            Approved connected capacity
          </span>
        </div>

        {/* Tariff Code */}
        <div className="p-3.5 rounded-lg bg-canvas border border-ink-200/70">
          <span className="text-[10px] uppercase font-semibold text-ink-400 block tracking-wider">
            Tariff Category
          </span>
          <div className="text-sm font-bold text-ink-900 font-mono mt-1 truncate">
            {level1.tariff || 'Standard Consumer'}
          </div>
          <span className="text-[10px] text-ink-500 mt-1 block">
            Utility consumer classification
          </span>
        </div>
      </div>
    </Card>
  );
}
