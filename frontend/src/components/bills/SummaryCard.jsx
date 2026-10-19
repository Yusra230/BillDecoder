import React from 'react';
import { Card } from '../ui/Card';
import { AlertCircle, Calendar, ShieldCheck, ArrowUpRight } from 'lucide-react';

export function SummaryCard({ level1 }) {
  if (!level1) return null;

  const withinDue = level1.payable_within_due_date;
  const afterDue = level1.payable_after_due_date;
  const arrears = level1.arrears;
  const currentBill = level1.current_bill;

  const surcharge =
    afterDue != null && withinDue != null && afterDue > withinDue
      ? afterDue - withinDue
      : null;

  const hasCredit = arrears != null && arrears < 0;

  return (
    <Card className="p-0 overflow-hidden border-ink-200">
      {/* Header Banner */}
      <div className="bg-canvas border-b border-ink-200/80 px-5 py-3.5 flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center space-x-2">
          <span className="text-[11px] font-semibold uppercase tracking-wider text-ink-500">
            Payment & Settlement Overview
          </span>
        </div>
        <div className="flex items-center space-x-1.5 text-xs text-ink-600">
          <Calendar className="w-3.5 h-3.5 text-ink-400" />
          <span>Due Date:</span>
          <span className="font-semibold text-ink-900 font-mono">
            {level1.due_date || 'N/A'}
          </span>
        </div>
      </div>

      {/* Primary Financial Numbers */}
      <div className="p-5 sm:p-6 grid grid-cols-1 sm:grid-cols-2 gap-5 sm:gap-8 divide-y sm:divide-y-0 sm:divide-x divide-ink-100">
        {/* Payable Within Due Date */}
        <div className="space-y-1.5">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-ink-500 uppercase tracking-wider">
              Payable Within Due Date
            </span>
            <span className="text-[10px] font-medium text-emerald-800 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200 font-mono">
              On Schedule
            </span>
          </div>

          <div className="flex items-baseline space-x-2">
            <span className="text-xs font-medium text-ink-400 font-mono">PKR</span>
            <span className="text-3xl sm:text-4xl font-extrabold text-ink-950 tracking-tight tabular-numbers">
              {withinDue != null ? Number(withinDue).toLocaleString() : '—'}
            </span>
          </div>
          <p className="text-[11px] text-ink-500">
            Settlement amount due before or on {level1.due_date || 'due date'}.
          </p>
        </div>

        {/* Payable After Due Date */}
        <div className="pt-4 sm:pt-0 sm:pl-8 space-y-1.5">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-ink-500 uppercase tracking-wider">
              Payable After Due Date
            </span>
            {surcharge != null && (
              <span className="text-[10px] font-medium text-amber-900 bg-amber-50 px-2 py-0.5 rounded border border-amber-200/90 font-mono">
                +Rs. {Number(surcharge).toLocaleString()} Late Fee
              </span>
            )}
          </div>

          <div className="flex items-baseline space-x-2">
            <span className="text-xs font-medium text-ink-400 font-mono">PKR</span>
            <span className="text-3xl sm:text-4xl font-extrabold text-ink-800 tracking-tight tabular-numbers">
              {afterDue != null ? Number(afterDue).toLocaleString() : '—'}
            </span>
          </div>
          <p className="text-[11px] text-ink-500">
            Includes late payment penalty if settled after {level1.due_date || 'due date'}.
          </p>
        </div>
      </div>

      {/* Secondary Metrics Strip */}
      <div className="bg-canvas/50 border-t border-ink-200/70 px-5 py-3.5 grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
        <div>
          <span className="text-[10px] uppercase font-semibold text-ink-400 block tracking-wider">
            Current Net Bill
          </span>
          <span className="font-semibold text-ink-900 font-mono tabular-numbers">
            {currentBill != null ? `Rs. ${Number(currentBill).toLocaleString()}` : '—'}
          </span>
        </div>

        <div>
          <span className="text-[10px] uppercase font-semibold text-ink-400 block tracking-wider">
            Arrears / Prior Balance
          </span>
          <span
            className={`font-semibold font-mono tabular-numbers ${
              hasCredit ? 'text-emerald-700' : 'text-ink-900'
            }`}
          >
            {arrears != null
              ? hasCredit
                ? `CR (-Rs. ${Math.abs(arrears).toLocaleString()})`
                : `Rs. ${Number(arrears).toLocaleString()}`
              : 'Rs. 0'}
          </span>
        </div>

        <div>
          <span className="text-[10px] uppercase font-semibold text-ink-400 block tracking-wider">
            Issue Date
          </span>
          <span className="font-semibold text-ink-700 font-mono">
            {level1.issue_date || '—'}
          </span>
        </div>

        <div>
          <span className="text-[10px] uppercase font-semibold text-ink-400 block tracking-wider">
            Reading Date
          </span>
          <span className="font-semibold text-ink-700 font-mono">
            {level1.reading_date || '—'}
          </span>
        </div>
      </div>
    </Card>
  );
}
