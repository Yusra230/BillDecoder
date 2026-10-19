import React from 'react';
import { Card } from '../ui/Card';
import { Landmark, Info } from 'lucide-react';

export function TaxesTable({ taxes = [], totalTaxes, currentBill }) {
  const getTaxLabel = (type) => {
    const map = {
      gst: 'General Sales Tax (GST)',
      electricity_duty: 'Electricity Duty (ED)',
      income_tax: 'Advance Income Tax',
      municipal_tax: 'Municipal / TV License Fee',
      other_tax: 'Other Government Levies',
    };
    return map[type] || type.replace('_', ' ');
  };

  const taxPercentage =
    totalTaxes && currentBill && currentBill > 0
      ? ((totalTaxes / currentBill) * 100).toFixed(1)
      : null;

  return (
    <Card className="p-0 overflow-hidden">
      <div className="px-5 py-4 border-b border-ink-200/80 flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center space-x-2">
          <Landmark className="w-4 h-4 text-ink-700" />
          <h3 className="text-xs font-semibold uppercase tracking-wider text-ink-900">
            Government Taxes & Statutory Duties
          </h3>
        </div>

        {totalTaxes != null && (
          <div className="text-right flex items-baseline space-x-2">
            <span className="text-[11px] text-ink-500 uppercase tracking-wider font-semibold">
              Total Taxes {taxPercentage && `(${taxPercentage}% of net bill)`}:
            </span>
            <span className="text-sm font-bold text-ink-950 font-mono tabular-numbers">
              Rs. {Number(totalTaxes).toLocaleString()}
            </span>
          </div>
        )}
      </div>

      {taxes.length === 0 ? (
        <div className="p-5 text-xs text-ink-500 flex items-start space-x-2.5 bg-canvas/40">
          <Info className="w-4 h-4 text-ink-400 shrink-0 mt-0.5" />
          <p className="leading-relaxed">
            Consolidated tax total printed without individual tariff breakdown (standard for select LESCO / IESCO statements). Official printed total taxes:{' '}
            <strong className="text-ink-900 font-mono">
              {totalTaxes != null ? `Rs. ${Number(totalTaxes).toLocaleString()}` : 'Not printed'}
            </strong>.
          </p>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-ink-200/80 bg-canvas text-ink-500 font-semibold uppercase tracking-wider text-[10px]">
                <th className="py-2.5 px-4">Tax Head</th>
                <th className="py-2.5 px-4">Statutory Description</th>
                <th className="py-2.5 px-4 text-right">Amount (PKR)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-ink-100 font-sans">
              {taxes.map((t, i) => (
                <tr key={i} className="hover:bg-canvas/50 transition-colors">
                  <td className="py-2.5 px-4">
                    <span className="inline-block px-2 py-0.5 rounded text-[10px] font-mono uppercase tracking-wider bg-canvas border border-ink-200 text-ink-700 font-medium">
                      {t.type}
                    </span>
                  </td>
                  <td className="py-2.5 px-4 text-ink-800 font-medium">
                    {getTaxLabel(t.type)}
                  </td>
                  <td className="py-2.5 px-4 text-right font-mono tabular-numbers font-semibold text-ink-900">
                    Rs. {Number(t.amount).toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
            {totalTaxes != null && (
              <tfoot>
                <tr className="border-t border-ink-200 bg-canvas/70 font-semibold text-xs">
                  <td colSpan={2} className="py-2.5 px-4 text-ink-700 text-right uppercase tracking-wider text-[11px]">
                    Total Taxes & Surcharges:
                  </td>
                  <td className="py-2.5 px-4 text-right font-mono tabular-numbers text-ink-950 font-bold">
                    Rs. {Number(totalTaxes).toLocaleString()}
                  </td>
                </tr>
              </tfoot>
            )}
          </table>
        </div>
      )}
    </Card>
  );
}
