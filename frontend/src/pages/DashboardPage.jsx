import React, { useEffect, useState, useMemo } from 'react';
import { Link } from 'react-router-dom';
import { fetchBills, deleteBillRecord, getBillExportUrl } from '../api/client';
import { Card, StatCard } from '../components/ui/Card';
import { ProviderBadge, StatusBadge } from '../components/ui/Badge';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';
import { EmptyState } from '../components/ui/EmptyState';
import { 
  FileText, 
  UploadCloud, 
  Zap, 
  Wallet, 
  Building2, 
  Search, 
  MessageSquare, 
  Download, 
  Trash2,
  ArrowRight,
  Filter,
  CheckCircle2
} from 'lucide-react';

export function DashboardPage() {
  const [bills, setBills] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [providerFilter, setProviderFilter] = useState('ALL');
  const [deletingId, setDeletingId] = useState(null);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await fetchBills();
      setBills(data || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleDelete = async (e, billId) => {
    e.stopPropagation();
    if (!window.confirm('Are you sure you want to delete this bill record?')) return;
    try {
      setDeletingId(billId);
      await deleteBillRecord(billId);
      setBills((prev) => prev.filter((b) => b.bill_id !== billId));
    } catch (err) {
      alert(`Failed to delete: ${err.message}`);
    } finally {
      setDeletingId(null);
    }
  };

  // Filtered bills
  const filteredBills = useMemo(() => {
    return bills.filter((b) => {
      const matchProvider =
        providerFilter === 'ALL' ||
        (b.provider || '').toUpperCase() === providerFilter.toUpperCase();

      const query = searchQuery.toLowerCase().trim();
      const matchQuery =
        !query ||
        (b.bill_id || '').toLowerCase().includes(query) ||
        (b.original_filename || '').toLowerCase().includes(query) ||
        (b.bill_month || '').toLowerCase().includes(query) ||
        (b.provider || '').toLowerCase().includes(query);

      return matchProvider && matchQuery;
    });
  }, [bills, providerFilter, searchQuery]);

  // Aggregated analytics from verified data
  const totalBills = bills.length;
  const totalUnits = bills.reduce((acc, b) => acc + (Number(b.units_consumed) || 0), 0);
  const totalSpend = bills.reduce((acc, b) => acc + (Number(b.payable_within_due_date) || 0), 0);
  const activeProviders = new Set(bills.map((b) => b.provider).filter(Boolean)).size;

  if (loading) {
    return <LoadingSpinner text="Retrieving verified statements from store..." />;
  }

  if (error) {
    return (
      <div className="p-6 rounded-xl bg-white border border-rose-200 text-rose-900 shadow-card space-y-3">
        <h3 className="font-semibold text-sm">Failed to connect to backend service</h3>
        <p className="text-xs text-rose-700">{error}</p>
        <button
          onClick={loadData}
          className="px-3.5 py-1.5 rounded-lg bg-rose-700 hover:bg-rose-800 text-white font-medium text-xs transition"
        >
          Retry Connection
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Page Title & Action Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl sm:text-2xl font-bold tracking-tight text-ink-950">
            Billing Portfolio
          </h2>
          <p className="text-xs text-ink-500 mt-0.5">
            Audit-grade extraction and verified metrics from Pakistani electricity statements.
          </p>
        </div>

        <Link
          to="/upload"
          className="inline-flex items-center justify-center px-4 py-2.5 rounded-lg bg-ink-950 hover:bg-ink-900 text-white text-xs font-semibold tracking-wide transition shadow-subtle shrink-0"
        >
          <UploadCloud className="w-4 h-4 mr-2 text-emerald-400" />
          <span>Upload Statement</span>
        </Link>
      </div>

      {/* KPI Stats Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
        <StatCard
          title="Statements"
          value={totalBills}
          subtitle="Grounded & schema validated"
          icon={FileText}
        />
        <StatCard
          title="Total Billed"
          value={`${totalUnits.toLocaleString()}`}
          subtitle="Kilowatt-hours (kWh)"
          icon={Zap}
        />
        <StatCard
          title="Net Payable Dues"
          value={`Rs. ${totalSpend.toLocaleString()}`}
          subtitle="Within due date sums"
          icon={Wallet}
        />
        <StatCard
          title="Utilities Active"
          value={`${activeProviders} / 3`}
          subtitle="KE, LESCO, IESCO"
          icon={Building2}
        />
      </div>

      {/* Main Table or Empty State */}
      {bills.length === 0 ? (
        <EmptyState
          title="No statements processed yet"
          description="Upload an official bill photograph or scan from K-Electric, LESCO, or IESCO to extract line items and enable AI Q&A."
          actionLabel="Upload First Statement"
          actionTo="/upload"
        />
      ) : (
        <Card className="p-0 overflow-hidden">
          {/* Table Header: Search & Filter Controls */}
          <div className="p-4 sm:p-5 border-b border-ink-200/80 flex flex-col md:flex-row md:items-center justify-between gap-3 bg-canvas/40">
            {/* Search Input */}
            <div className="relative flex-1 max-w-sm">
              <Search className="w-3.5 h-3.5 text-ink-400 absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search by ID, month, or filename..."
                className="w-full bg-white border border-ink-200/90 rounded-lg pl-8 pr-3 py-1.5 text-xs text-ink-800 placeholder-ink-400 focus:outline-none focus:ring-1 focus:ring-ink-900 focus:border-ink-900 transition"
              />
            </div>

            {/* Provider Filter Tabs */}
            <div className="flex items-center space-x-1 overflow-x-auto pb-1 md:pb-0">
              <span className="text-[11px] font-semibold uppercase tracking-wider text-ink-400 mr-1.5 hidden sm:inline">
                Utility:
              </span>
              {['ALL', 'KE', 'LESCO', 'IESCO'].map((p) => (
                <button
                  key={p}
                  onClick={() => setProviderFilter(p)}
                  className={`px-2.5 py-1 rounded-md text-xs font-mono font-medium transition ${
                    providerFilter === p
                      ? 'bg-ink-950 text-white font-semibold shadow-subtle'
                      : 'bg-white text-ink-600 hover:text-ink-950 hover:bg-ink-100 border border-ink-200/80'
                  }`}
                >
                  {p}
                </button>
              ))}
            </div>
          </div>

          {/* Statement Table */}
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-ink-200/80 bg-canvas text-ink-500 font-semibold uppercase tracking-wider text-[10px]">
                  <th className="py-3 px-4">Provider / Document</th>
                  <th className="py-3 px-4">Billing Month</th>
                  <th className="py-3 px-4 text-right">Units (kWh)</th>
                  <th className="py-3 px-4 text-right">Amount Due</th>
                  <th className="py-3 px-4 hidden sm:table-cell">Due Date</th>
                  <th className="py-3 px-4 hidden md:table-cell">Status</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-ink-100 font-sans">
                {filteredBills.map((bill) => (
                  <tr
                    key={bill.bill_id}
                    className="hover:bg-canvas/60 transition cursor-pointer"
                    onClick={() => (window.location.hash = `/bills/${bill.bill_id}`)}
                  >
                    {/* Provider & Filename */}
                    <td className="py-3.5 px-4">
                      <ProviderBadge provider={bill.provider} size="sm" />
                      <span className="block text-[11px] text-ink-400 font-mono mt-1 truncate max-w-[150px] sm:max-w-[200px]">
                        {bill.original_filename || bill.bill_id}
                      </span>
                    </td>

                    {/* Month */}
                    <td className="py-3.5 px-4 font-mono font-semibold text-ink-800">
                      {bill.bill_month || '—'}
                    </td>

                    {/* Units */}
                    <td className="py-3.5 px-4 text-right font-mono tabular-numbers text-ink-800 font-semibold">
                      {bill.units_consumed != null ? `${bill.units_consumed}` : '—'}
                    </td>

                    {/* Amount */}
                    <td className="py-3.5 px-4 text-right font-mono tabular-numbers font-bold text-ink-950">
                      {bill.payable_within_due_date != null
                        ? `Rs. ${Number(bill.payable_within_due_date).toLocaleString()}`
                        : '—'}
                    </td>

                    {/* Due Date */}
                    <td className="py-3.5 px-4 hidden sm:table-cell font-mono text-ink-600">
                      {bill.due_date || '—'}
                    </td>

                    {/* Status */}
                    <td className="py-3.5 px-4 hidden md:table-cell">
                      <StatusBadge status={bill.status} />
                    </td>

                    {/* Actions */}
                    <td
                      className="py-3.5 px-4 text-right space-x-1"
                      onClick={(e) => e.stopPropagation()}
                    >
                      <Link
                        to={`/bills/${bill.bill_id}/ask`}
                        className="inline-flex items-center px-2 py-1 rounded-md bg-canvas hover:bg-ink-100 border border-ink-200 text-ink-700 text-xs font-medium transition"
                        title="Open Grounded Assistant"
                      >
                        <MessageSquare className="w-3 h-3 mr-1 text-emerald-700" />
                        <span className="hidden sm:inline">Q&A</span>
                      </Link>

                      <a
                        href={getBillExportUrl(bill.bill_id)}
                        download
                        className="inline-flex items-center p-1 rounded-md bg-canvas hover:bg-ink-100 border border-ink-200 text-ink-500 hover:text-ink-900 transition"
                        title="Download Level 1 JSON"
                      >
                        <Download className="w-3.5 h-3.5" />
                      </a>

                      <button
                        onClick={(e) => handleDelete(e, bill.bill_id)}
                        disabled={deletingId === bill.bill_id}
                        className="inline-flex items-center p-1 rounded-md bg-canvas hover:bg-rose-50 border border-ink-200 hover:border-rose-200 text-ink-400 hover:text-rose-700 transition"
                        title="Delete bill"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {filteredBills.length === 0 && (
            <div className="py-12 text-center text-xs text-ink-400">
              No statements matched your filter criteria.
            </div>
          )}
        </Card>
      )}
    </div>
  );
}
