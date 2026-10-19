import React from 'react';
import { Card } from '../ui/Card';
import { Receipt, Info } from 'lucide-react';

export function ChargesTable({ charges = [], totalCharges }) {
  const getChargeLabel = (type) => {
    const map = {
      energy: 'Energy Consumption (Variable Tariff)',
      fixed: 'Fixed Capacity Charges',
      fpa: 'Fuel Price Adjustment (FPA / FCA)',
      quarterly_adjustment: 'Quarterly Tariff Adjustment (QTA)',
      surcharge: 'Debt / Financing Surcharge',
      meter_rent: 'Meter Rent / Equipment Fee',
      subsidy: 'Government Tariff Subsidy',
      other: 'Other Electricity Charge',
    };
    return map[type] || type.replace('_', ' ');
  };

  return (
    <Card className="p-0 overflow-hidden">
      <div className="px-5 py-4 border-b border-ink-200/80 flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center space-x-2">
          <Receipt className="w-4 h-4 text-ink-700" />
          <h3 className="text-xs font-semibold uppercase tracking-wider text-ink-900">
            Itemized Electricity Charges
          </h3>
        </div>

        {totalCharges != null && (
          <div className="text-right flex items-baseline space-x-2">
            <span className="text-[11px] text-ink-500 uppercase tracking-wider font-semibold">
              Total Charges:
            </span>
            <span className="text-sm font-bold text-ink-950 font-mono tabular-numbers">
              Rs. {Number(totalCharges).toLocaleString()}
            </span>
          </div>
        )}
      </div>

      {charges.length === 0 ? (
        <div className="p-5 text-xs text-ink-500 flex items-start space-x-2.5 bg-canvas/40">
          <Info className="w-4 h-4 text-ink-400 shrink-0 mt-0.5" />
          <p className="leading-relaxed">
            Individual line item charges are not printed itemized on this bill (e.g. combined subtotal or covered barcode area). Official printed Total Charges:{' '}
            <strong className="text-ink-900 font-mono">
              {totalCharges != null ? `Rs. ${Number(totalCharges).toLocaleString()}` : 'Not printed'}
            </strong>.
          </p>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-ink-200/80 bg-canvas text-ink-500 font-semibold uppercase tracking-wider text-[10px]">
                <th className="py-2.5 px-4">Classification</th>
                <th className="py-2.5 px-4">Line Item Description</th>
                <th className="py-2.5 px-4 text-right">Amount (PKR)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-ink-100 font-sans">
              {charges.map((c, i) => {
                const isNegative = c.amount < 0;
                return (
                  <tr key={i} className="hover:bg-canvas/50 transition-colors">
                    <td className="py-2.5 px-4">
                      <span
                        className={`inline-block px-2 py-0.5 rounded text-[10px] font-mono uppercase tracking-wider border font-medium ${
                          isNegative
                            ? 'bg-emerald-50 text-emerald-800 border-emerald-200'
                            : 'bg-canvas text-ink-700 border-ink-200'
                        }`}
                      >
                        {c.type}
                      </span>
                    </td>
                    <td className="py-2.5 px-4 text-ink-800 font-medium">
                      {getChargeLabel(c.type)}
                    </td>
                    <td
                      className={`py-2.5 px-4 text-right font-mono tabular-numbers font-semibold ${
                        isNegative ? 'text-emerald-700' : 'text-ink-900'
                      }`}
                    >
                      {isNegative
                        ? `-(Rs. ${Math.abs(c.amount).toLocaleString()})`
                        : `Rs. ${Number(c.amount).toLocaleString()}`}
                    </td>
                  </tr>
                );
              })}
            </tbody>
            {totalCharges != null && (
              <tfoot>
                <tr className="border-t border-ink-200 bg-canvas/70 font-semibold text-xs">
                  <td colSpan={2} className="py-2.5 px-4 text-ink-700 text-right uppercase tracking-wider text-[11px]">
                    Net Electricity Charges Subtotal:
                  </td>
                  <td className="py-2.5 px-4 text-right font-mono tabular-numbers text-ink-950 font-bold">
                    Rs. {Number(totalCharges).toLocaleString()}
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
