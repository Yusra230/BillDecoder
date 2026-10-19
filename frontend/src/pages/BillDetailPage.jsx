import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { fetchBillDetail, getBillExportUrl } from '../api/client';
import { Card } from '../components/ui/Card';
import { ProviderBadge, StatusBadge } from '../components/ui/Badge';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';
import { ReadingsCard } from '../components/bills/ReadingsCard';
import { SummaryCard } from '../components/bills/SummaryCard';
import { ChargesTable } from '../components/bills/ChargesTable';
import { TaxesTable } from '../components/bills/TaxesTable';
import { HistoryChart } from '../components/bills/HistoryChart';
import { ImageViewer } from '../components/bills/ImageViewer';
import { 
  ArrowLeft, 
  MessageSquare, 
  Download, 
  Code, 
  Check, 
  Copy,
  Receipt,
  TrendingUp,
  FileImage,
  ExternalLink
} from 'lucide-react';

export function BillDetailPage() {
  const { id } = useParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('overview'); // 'overview' | 'history' | 'json'
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    async function loadBill() {
      try {
        setLoading(true);
        setError(null);
        const res = await fetchBillDetail(id);
        setData(res);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    loadBill();
  }, [id]);

  const handleCopyJson = () => {
    if (!data?.level1) return;
    navigator.clipboard.writeText(JSON.stringify(data.level1, null, 2));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (loading) {
    return <LoadingSpinner text="Retrieving statement details & line items..." />;
  }

  if (error || !data) {
    return (
      <div className="max-w-xl mx-auto space-y-4 my-8">
        <div className="p-5 rounded-xl bg-white border border-rose-200 text-rose-900 text-xs shadow-card space-y-2">
          <strong className="block text-sm">Statement Not Found</strong>
          <p>{error || 'The requested statement ID does not exist in local storage.'}</p>
        </div>
        <Link
          to="/"
          className="inline-flex items-center text-xs font-semibold text-ink-600 hover:text-ink-950"
        >
          <ArrowLeft className="w-3.5 h-3.5 mr-1" />
          Return to Dashboard
        </Link>
      </div>
    );
  }

  const { metadata, level1, history, qa_history } = data;

  return (
    <div className="space-y-6">
      {/* Top Breadcrumb & Executive Action Strip */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-ink-200/80">
        <div className="flex items-start sm:items-center space-x-3">
          <Link
            to="/"
            className="p-2 rounded-lg bg-white border border-ink-200 hover:bg-canvas text-ink-700 transition shadow-subtle shrink-0 mt-0.5 sm:mt-0"
            title="Back to Dashboard"
          >
            <ArrowLeft className="w-4 h-4" />
          </Link>
          <div>
            <div className="flex flex-wrap items-center gap-2">
              <ProviderBadge provider={level1?.provider} size="sm" />
              <StatusBadge status={metadata?.status} />
              <span className="text-[11px] font-mono text-ink-400">ID: {id}</span>
            </div>
            <h2 className="text-lg sm:text-xl font-bold text-ink-950 tracking-tight mt-1">
              {level1?.bill_month ? `Statement for ${level1.bill_month}` : 'Utility Statement'}
            </h2>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center space-x-2 shrink-0">
          <Link
            to={`/bills/${id}/ask`}
            className="inline-flex items-center px-3.5 py-2 rounded-lg bg-ink-950 hover:bg-ink-900 text-white text-xs font-semibold transition shadow-subtle"
          >
            <MessageSquare className="w-3.5 h-3.5 mr-1.5 text-emerald-400" />
            <span>Ask Q&A</span>
            {qa_history?.length > 0 && (
              <span className="ml-1.5 px-1.5 py-0.2 rounded-full bg-ink-800 text-[10px] font-mono text-ink-200">
                {qa_history.length}
              </span>
            )}
          </Link>

          <a
            href={getBillExportUrl(id)}
            download
            className="inline-flex items-center px-3 py-2 rounded-lg bg-white border border-ink-200 hover:bg-canvas text-ink-700 text-xs font-medium transition shadow-subtle"
            title="Download Level 1 Schema JSON"
          >
            <Download className="w-3.5 h-3.5 mr-1 text-ink-500" />
            <span className="hidden sm:inline">Export</span> JSON
          </a>
        </div>
      </div>

      {/* Tabs Navigation */}
      <div className="flex items-center space-x-1 border-b border-ink-200 overflow-x-auto pb-px">
        <button
          onClick={() => setActiveTab('overview')}
          className={`py-2 px-3 text-xs font-medium border-b-2 transition shrink-0 ${
            activeTab === 'overview'
              ? 'border-ink-950 text-ink-950 font-semibold'
              : 'border-transparent text-ink-500 hover:text-ink-800'
          }`}
        >
          <div className="flex items-center space-x-1.5">
            <Receipt className="w-3.5 h-3.5" />
            <span>Statement Breakdown</span>
          </div>
        </button>

        <button
          onClick={() => setActiveTab('history')}
          className={`py-2 px-3 text-xs font-medium border-b-2 transition shrink-0 ${
            activeTab === 'history'
              ? 'border-ink-950 text-ink-950 font-semibold'
              : 'border-transparent text-ink-500 hover:text-ink-800'
          }`}
        >
          <div className="flex items-center space-x-1.5">
            <TrendingUp className="w-3.5 h-3.5" />
            <span>12-Month Consumption ({history?.length || 0})</span>
          </div>
        </button>

        <button
          onClick={() => setActiveTab('json')}
          className={`py-2 px-3 text-xs font-medium border-b-2 transition shrink-0 ${
            activeTab === 'json'
              ? 'border-ink-950 text-ink-950 font-semibold'
              : 'border-transparent text-ink-500 hover:text-ink-800'
          }`}
        >
          <div className="flex items-center space-x-1.5">
            <Code className="w-3.5 h-3.5" />
            <span>Level 1 JSON Schema</span>
          </div>
        </button>
      </div>

      {/* Responsive Grid: Left Data Tables, Right Document Scanner */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left Column (Statement Line Items & Metrics) */}
        <div className="lg:col-span-7 space-y-6">
          {activeTab === 'overview' && (
            <>
              <SummaryCard level1={level1} />
              <ReadingsCard level1={level1} />
              <ChargesTable charges={level1?.charges} totalCharges={level1?.total_charges} />
              <TaxesTable
                taxes={level1?.taxes}
                totalTaxes={level1?.total_taxes}
                currentBill={level1?.current_bill}
              />
            </>
          )}

          {activeTab === 'history' && (
            <div className="space-y-6">
              <HistoryChart history={history} />

              {/* Data Table of Historical Cycles */}
              <Card className="p-0 overflow-hidden">
                <div className="p-4 border-b border-ink-200/80 bg-canvas">
                  <h4 className="text-xs font-semibold uppercase tracking-wider text-ink-900">
                    Billing Cycle Archive (Past 12 Months)
                  </h4>
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs">
                    <thead>
                      <tr className="border-b border-ink-200/80 bg-canvas/70 text-ink-500 font-semibold uppercase tracking-wider text-[10px]">
                        <th className="py-2.5 px-4">Cycle Month</th>
                        <th className="py-2.5 px-4 text-right">Units (kWh)</th>
                        <th className="py-2.5 px-4 text-right">Billed Amount (PKR)</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-ink-100 font-sans">
                      {history?.map((h, i) => (
                        <tr key={i} className="hover:bg-canvas/50 transition">
                          <td className="py-2.5 px-4 font-mono font-medium text-ink-800">
                            {h.month}
                          </td>
                          <td className="py-2.5 px-4 text-right font-mono tabular-numbers text-ink-900 font-semibold">
                            {h.units != null ? `${h.units}` : '—'}
                          </td>
                          <td className="py-2.5 px-4 text-right font-mono tabular-numbers text-ink-950 font-bold">
                            {h.bill != null ? `Rs. ${Number(h.bill).toLocaleString()}` : '—'}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </Card>
            </div>
          )}

          {activeTab === 'json' && (
            <Card className="p-5 space-y-3">
              <div className="flex items-center justify-between pb-3 border-b border-ink-200/80">
                <div className="flex items-center space-x-2">
                  <Code className="w-4 h-4 text-ink-700" />
                  <h4 className="text-xs font-semibold uppercase tracking-wider text-ink-900">
                    Competition Level 1 Standard JSON
                  </h4>
                </div>
                <button
                  onClick={handleCopyJson}
                  className="inline-flex items-center px-2.5 py-1 rounded-md bg-canvas hover:bg-ink-100 border border-ink-200 text-ink-700 text-xs font-medium transition cursor-pointer"
                >
                  {copied ? (
                    <>
                      <Check className="w-3.5 h-3.5 mr-1 text-emerald-700" />
                      <span>Copied</span>
                    </>
                  ) : (
                    <>
                      <Copy className="w-3.5 h-3.5 mr-1 text-ink-500" />
                      <span>Copy JSON</span>
                    </>
                  )}
                </button>
              </div>

              <pre className="p-4 rounded-lg bg-ink-950 text-emerald-400 font-mono text-xs overflow-x-auto max-h-[520px] leading-relaxed border border-ink-800">
                {JSON.stringify(level1, null, 2)}
              </pre>
            </Card>
          )}
        </div>

        {/* Right Column (Document Image Inspector) */}
        <div className="lg:col-span-5 space-y-6">
          <ImageViewer billId={id} filename={metadata?.original_filename} />
        </div>
      </div>
    </div>
  );
}
