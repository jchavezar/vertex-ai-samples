import React, { useState, useEffect } from 'react';
import {
  Download,
  Filter,
  RefreshCw,
  AlertTriangle,
  Clock,
  ChevronLeft,
  ChevronRight,
  Database,
  FileSpreadsheet,
  X,
} from 'lucide-react';
import { LegacyQueryResponse } from '../types';
import { fetchLegacyData, exportLegacyCsv } from '../services/api';
import { MultiDepartmentQueryChain } from './MultiDepartmentQueryChain';

interface LegacyEnterpriseViewProps {
  onUpdateLatency: (latencyMs: number) => void;
  onTriggerRefactor: () => void;
}

export const LegacyEnterpriseView: React.FC<LegacyEnterpriseViewProps> = ({
  onUpdateLatency,
  onTriggerRefactor,
}) => {
  const [data, setData] = useState<LegacyQueryResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(12);
  const [search, setSearch] = useState('');
  const [currency, setCurrency] = useState('');
  const [riskRating, setRiskRating] = useState('');
  const [clearingHouse, setClearingHouse] = useState('');
  const [simulateSlowQuery, setSimulateSlowQuery] = useState(true);
  const [exportModalOpen, setExportModalOpen] = useState(false);
  const [exportInfo, setExportInfo] = useState<any>(null);

  const loadData = async (targetPage = page) => {
    setLoading(true);
    try {
      const resp = await fetchLegacyData({
        page: targetPage,
        page_size: pageSize,
        search: search || undefined,
        currency: currency || undefined,
        risk_rating: riskRating || undefined,
        clearing_house: clearingHouse || undefined,
        simulate_slow_query_ms: simulateSlowQuery ? 1400 : 50,
      });
      setData(resp);
      onUpdateLatency(resp.query_latency_ms);
    } catch (err) {
      console.error('Failed to load legacy data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData(1);
  }, [currency, riskRating, clearingHouse, pageSize, simulateSlowQuery]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    loadData(1);
  };

  const handleExportCsv = async () => {
    try {
      const resp = await exportLegacyCsv();
      setExportInfo(resp);
      setExportModalOpen(true);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="legacy-theme p-6 min-h-[calc(100vh-120px)] border-4 border-slate-400">
      {/* 2015 Windows / SAP Style Header Banner */}
      <div className="bg-[#2c3e50] text-white px-4 py-2 rounded-t flex items-center justify-between border-b-2 border-[#1a252f] shadow-md">
        <div className="flex items-center gap-2">
          <Database className="h-5 w-5 text-amber-400" />
          <span className="font-bold text-sm tracking-wide">
            GLOBAL TREASURY & LIQUIDITY OPERATIONS ERP // RELEASE 11.2 (BUILD 2015-06)
          </span>
        </div>
        <div className="flex items-center gap-4 text-xs">
          <span className="bg-amber-500/20 text-amber-300 px-2 py-0.5 border border-amber-500/40 rounded">
            STATUS: SYNCHRONIZED (ORACLE RAC 11g)
          </span>
          <button
            onClick={onTriggerRefactor}
            className="bg-indigo-600 hover:bg-indigo-700 text-white font-bold px-3 py-1 rounded text-xs shadow flex items-center gap-1.5 transition-all"
          >
            <span>Modernize to Agent-Native &rarr;</span>
          </button>
        </div>
      </div>

      {/* Interactive 3-Day Manual SQL & CSV Consolidation Chain Simulator */}
      <MultiDepartmentQueryChain onTriggerRefactor={onTriggerRefactor} />

      {/* Legacy Filter Bar */}
      <div className="legacy-panel p-4 mb-4 border border-[#99a8b5]">
        <div className="flex flex-wrap items-center justify-between gap-3 mb-3">
          <div className="flex items-center gap-2">
            <Filter className="h-4 w-4 text-slate-600" />
            <span className="text-xs font-bold uppercase text-slate-700">
              Query Parameter Filters (Manual SQL Execution)
            </span>
          </div>
          
          <div className="flex items-center gap-2 text-xs">
            <label className="flex items-center gap-1.5 font-semibold text-slate-700 cursor-pointer">
              <input
                type="checkbox"
                checked={simulateSlowQuery}
                onChange={(e) => setSimulateSlowQuery(e.target.checked)}
                className="rounded text-blue-600 focus:ring-0"
              />
              <span>Simulate Legacy Disk I/O Latency (1,400ms)</span>
            </label>
          </div>
        </div>

        <form onSubmit={handleSearchSubmit} className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-5 gap-3">
          {/* Search Box */}
          <div>
            <label className="block text-[11px] font-bold text-slate-700 mb-1">
              Transaction ID / Entity / BIC:
            </label>
            <div className="relative">
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="e.g. TX-2015-000012 or BNP"
                className="w-full bg-white text-slate-900 border border-slate-400 px-2.5 py-1 text-xs rounded shadow-inner focus:outline-none focus:border-blue-600"
              />
            </div>
          </div>

          {/* Currency Dropdown */}
          <div>
            <label className="block text-[11px] font-bold text-slate-700 mb-1">
              Currency ISO:
            </label>
            <select
              value={currency}
              onChange={(e) => {
                setCurrency(e.target.value);
                setPage(1);
              }}
              className="w-full bg-white text-slate-900 border border-slate-400 px-2 py-1 text-xs rounded shadow-inner"
            >
              <option value="">-- ALL CURRENCIES --</option>
              <option value="USD">USD - US Dollar</option>
              <option value="EUR">EUR - Euro</option>
              <option value="GBP">GBP - British Pound</option>
              <option value="JPY">JPY - Japanese Yen</option>
              <option value="CHF">CHF - Swiss Franc</option>
              <option value="BRL">BRL - Brazilian Real</option>
              <option value="CNY">CNY - Chinese Yuan</option>
            </select>
          </div>

          {/* Risk Rating */}
          <div>
            <label className="block text-[11px] font-bold text-slate-700 mb-1">
              Credit Risk Grade:
            </label>
            <select
              value={riskRating}
              onChange={(e) => {
                setRiskRating(e.target.value);
                setPage(1);
              }}
              className="w-full bg-white text-slate-900 border border-slate-400 px-2 py-1 text-xs rounded shadow-inner"
            >
              <option value="">-- ALL RISK TIERS --</option>
              <option value="AAA">AAA (Prime Sovereign / G-SIB)</option>
              <option value="AA">AA / AA+ / AA-</option>
              <option value="A+">A+ / A / A-</option>
              <option value="BBB+">BBB+ / BBB / BBB-</option>
            </select>
          </div>

          {/* Clearing House */}
          <div>
            <label className="block text-[11px] font-bold text-slate-700 mb-1">
              Clearing Facility:
            </label>
            <select
              value={clearingHouse}
              onChange={(e) => {
                setClearingHouse(e.target.value);
                setPage(1);
              }}
              className="w-full bg-white text-slate-900 border border-slate-400 px-2 py-1 text-xs rounded shadow-inner"
            >
              <option value="">-- ALL CLEARING HOUSES --</option>
              <option value="CME">CME Group</option>
              <option value="LCH">LCH Clearnet</option>
              <option value="Eurex">Eurex Clearing</option>
              <option value="SIX">SIX x-clear</option>
            </select>
          </div>

          {/* Buttons */}
          <div className="flex items-end gap-2">
            <button
              type="submit"
              disabled={loading}
              className="legacy-btn px-4 py-1.5 flex-1 flex items-center justify-center gap-1.5 text-xs text-slate-800 font-bold"
            >
              <RefreshCw className={`h-3.5 w-3.5 ${loading ? 'animate-spin' : ''}`} />
              <span>{loading ? 'Executing...' : 'Run Query'}</span>
            </button>

            <button
              type="button"
              onClick={handleExportCsv}
              className="legacy-btn px-3 py-1.5 bg-slate-200 text-slate-800 font-semibold flex items-center gap-1 text-xs"
              title="Queue Batch CSV Export"
            >
              <Download className="h-3.5 w-3.5 text-slate-700" />
              <span>Export CSV</span>
            </button>
          </div>
        </form>
      </div>

      {/* Query Status Bar */}
      <div className="flex items-center justify-between text-xs text-slate-600 mb-2 px-1 font-mono">
        <div>
          DB Host: <span className="font-semibold text-slate-800">erp-prod-db04.corp (Oracle RAC)</span> |
          Rows: <span className="font-semibold text-slate-800">{data?.total_records || 0}</span> |
          Page: <span className="font-semibold text-slate-800">{data?.page || 1} of {data?.total_pages || 1}</span>
        </div>
        <div className="flex items-center gap-2">
          {loading ? (
            <span className="text-amber-600 font-bold flex items-center gap-1 animate-pulse">
              <Clock className="h-3.5 w-3.5" />
              Executing Table Scan... ({data?.query_latency_ms || 1400}ms)
            </span>
          ) : (
            <span className="text-slate-700">
              Query Latency: <strong className="text-amber-700 font-bold">{data?.query_latency_ms || 0} ms</strong>
            </span>
          )}
        </div>
      </div>

      {/* Monolithic 20-Column Table Container */}
      <div className="bg-white border-2 border-[#7c8d9e] shadow-inner overflow-x-auto relative min-h-[380px]">
        {loading && (
          <div className="absolute inset-0 bg-white/70 backdrop-blur-[1px] flex flex-col items-center justify-center z-20">
            <div className="h-10 w-10 border-4 border-slate-300 border-t-amber-600 rounded-full animate-spin mb-3"></div>
            <span className="font-bold text-slate-800 text-xs tracking-wider">
              FETCHING RELATIONAL RECORDSET FROM ORACLE 11g...
            </span>
            <span className="text-[11px] text-slate-500 font-mono mt-1">
              Executing unindexed join across 160 entities...
            </span>
          </div>
        )}

        <table className="w-full text-left border-collapse whitespace-nowrap text-[11px] font-sans">
          <thead>
            <tr className="legacy-table-header">
              <th className="p-2 border-r border-b border-slate-400"># TX ID</th>
              <th className="p-2 border-r border-b border-slate-400">GL Account Code</th>
              <th className="p-2 border-r border-b border-slate-400">BIC / SWIFT</th>
              <th className="p-2 border-r border-b border-slate-400">Counterparty Entity</th>
              <th className="p-2 border-r border-b border-slate-400">Settle Date</th>
              <th className="p-2 border-r border-b border-slate-400">CCY</th>
              <th className="p-2 border-r border-b border-slate-400 text-right">Notional ($)</th>
              <th className="p-2 border-r border-b border-slate-400 text-right">Spread (bps)</th>
              <th className="p-2 border-r border-b border-slate-400">Clearing Facility</th>
              <th className="p-2 border-r border-b border-slate-400">Margin Tier</th>
              <th className="p-2 border-r border-b border-slate-400">Risk Grade</th>
              <th className="p-2 border-r border-b border-slate-400">Liquidity Horizon</th>
              <th className="p-2 border-r border-b border-slate-400">Tax Jur</th>
              <th className="p-2 border-r border-b border-slate-400">Dodd-Frank Tag</th>
              <th className="p-2 border-r border-b border-slate-400 text-right">Basel III %</th>
              <th className="p-2 border-r border-b border-slate-400">SLA Status</th>
              <th className="p-2 border-r border-b border-slate-400">Audit Timestamp</th>
              <th className="p-2 border-r border-b border-slate-400">Batch ID</th>
              <th className="p-2 border-r border-b border-slate-400">Recon Flag</th>
              <th className="p-2 border-b border-slate-400">Operator Override Notes</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-200">
            {data?.data.map((row, idx) => (
              <tr
                key={row.transaction_id}
                className={`hover:bg-amber-50/80 transition-colors ${
                  idx % 2 === 0 ? 'bg-white' : 'bg-[#f7f9fb]'
                }`}
              >
                <td className="p-2 font-mono font-bold text-blue-900 border-r border-slate-300">
                  {row.transaction_id}
                </td>
                <td className="p-2 border-r border-slate-300 text-slate-700">
                  {row.gl_code}
                </td>
                <td className="p-2 font-mono text-slate-800 border-r border-slate-300">
                  {row.counterparty_bic}
                </td>
                <td className="p-2 font-semibold text-slate-900 border-r border-slate-300">
                  {row.counterparty_name}
                </td>
                <td className="p-2 font-mono text-slate-700 border-r border-slate-300">
                  {row.settlement_date}
                </td>
                <td className="p-2 font-bold text-slate-800 border-r border-slate-300">
                  {row.currency}
                </td>
                <td className="p-2 font-mono font-bold text-slate-900 text-right border-r border-slate-300">
                  ${row.notional_amount.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                </td>
                <td className="p-2 font-mono text-slate-700 text-right border-r border-slate-300">
                  {row.fx_spread_bps.toFixed(2)}
                </td>
                <td className="p-2 text-slate-800 border-r border-slate-300">
                  {row.clearing_house}
                </td>
                <td className="p-2 text-slate-700 border-r border-slate-300">
                  <span className="px-1.5 py-0.5 bg-slate-200 rounded text-[10px] font-semibold">
                    {row.margin_tier}
                  </span>
                </td>
                <td className="p-2 font-bold border-r border-slate-300">
                  <span
                    className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${
                      row.risk_rating.startsWith('AAA') || row.risk_rating.startsWith('AA')
                        ? 'bg-emerald-100 text-emerald-800'
                        : row.risk_rating.startsWith('A')
                        ? 'bg-blue-100 text-blue-800'
                        : 'bg-amber-100 text-amber-900'
                    }`}
                  >
                    {row.risk_rating}
                  </span>
                </td>
                <td className="p-2 text-slate-700 border-r border-slate-300">
                  {row.liquidity_bucket}
                </td>
                <td className="p-2 font-mono font-semibold text-slate-800 border-r border-slate-300">
                  {row.tax_jurisdiction}
                </td>
                <td className="p-2 text-slate-600 text-[10px] font-mono border-r border-slate-300">
                  {row.dodd_frank_tag}
                </td>
                <td className="p-2 font-mono text-right border-r border-slate-300">
                  {row.basel_risk_weight_pct.toFixed(1)}%
                </td>
                <td className="p-2 border-r border-slate-300">
                  <span className="px-1.5 py-0.5 bg-slate-100 border border-slate-300 rounded text-[10px] text-slate-700 font-mono">
                    {row.sla_status}
                  </span>
                </td>
                <td className="p-2 font-mono text-[10px] text-slate-500 border-r border-slate-300">
                  {row.audit_timestamp}
                </td>
                <td className="p-2 font-mono text-[10px] text-slate-600 border-r border-slate-300">
                  {row.batch_id}
                </td>
                <td className="p-2 text-[10px] font-mono text-slate-700 border-r border-slate-300">
                  {row.reconciliation_flag}
                </td>
                <td className="p-2 text-[10px] text-slate-600 italic max-w-xs truncate">
                  {row.override_notes}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination & Control Bar */}
      <div className="legacy-panel p-3 mt-3 flex flex-wrap items-center justify-between gap-3 text-xs border border-[#99a8b5]">
        <div className="flex items-center gap-2">
          <span className="font-semibold text-slate-700">Display Rows:</span>
          <select
            value={pageSize}
            onChange={(e) => {
              setPageSize(Number(e.target.value));
              setPage(1);
            }}
            className="bg-white border border-slate-400 px-2 py-0.5 rounded text-xs"
          >
            <option value={10}>10 records</option>
            <option value={12}>12 records</option>
            <option value={20}>20 records</option>
            <option value={50}>50 records</option>
          </select>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => {
              const newPage = Math.max(1, page - 1);
              setPage(newPage);
              loadData(newPage);
            }}
            disabled={page <= 1 || loading}
            className="legacy-btn px-3 py-1 flex items-center gap-1 disabled:opacity-50"
          >
            <ChevronLeft className="h-3.5 w-3.5" />
            <span>Previous</span>
          </button>

          <span className="px-3 py-1 bg-white border border-slate-400 rounded font-mono font-bold text-slate-800">
            Page {page} of {data?.total_pages || 1}
          </span>

          <button
            onClick={() => {
              const newPage = Math.min(data?.total_pages || 1, page + 1);
              setPage(newPage);
              loadData(newPage);
            }}
            disabled={!data || page >= data.total_pages || loading}
            className="legacy-btn px-3 py-1 flex items-center gap-1 disabled:opacity-50"
          >
            <span>Next</span>
            <ChevronRight className="h-3.5 w-3.5" />
          </button>
        </div>
      </div>

      {/* CSV Export Pop-up Dialog Simulator */}
      {exportModalOpen && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-[#f0f3f6] border-2 border-slate-700 rounded shadow-2xl max-w-md w-full p-5 text-slate-900">
            <div className="flex items-center justify-between border-b border-slate-400 pb-2 mb-3">
              <div className="flex items-center gap-2">
                <FileSpreadsheet className="h-5 w-5 text-emerald-700" />
                <h3 className="font-bold text-sm">Oracle Batch Export Daemon</h3>
              </div>
              <button
                onClick={() => setExportModalOpen(false)}
                className="text-slate-500 hover:text-slate-800"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            <div className="space-y-3 text-xs">
              <div className="bg-amber-100 border border-amber-400 p-3 rounded text-amber-950 flex items-start gap-2">
                <AlertTriangle className="h-4 w-4 text-amber-700 shrink-0 mt-0.5" />
                <div>
                  <p className="font-bold">Overnight Export Batch Enqueued</p>
                  <p className="mt-0.5 text-[11px]">{exportInfo?.message}</p>
                </div>
              </div>

              <div className="bg-white border border-slate-300 p-3 rounded font-mono text-[11px] space-y-1">
                <div>Job ID: <span className="font-bold text-blue-800">{exportInfo?.job_id}</span></div>
                <div>Queue Position: <span className="font-bold text-slate-800">{exportInfo?.queue_position} of 120</span></div>
                <div>Estimated Wait: <span className="font-bold text-amber-700">{exportInfo?.estimated_wait_time}</span></div>
                <div>Worker Node: <span className="text-slate-600">{exportInfo?.queue_server}</span></div>
              </div>

              <p className="text-[11px] text-slate-600 italic">
                * In 2015, executives waited 3 days for Excel analysts to pivot this CSV dump.
              </p>
            </div>

            <div className="mt-4 flex justify-end gap-2">
              <button
                onClick={() => setExportModalOpen(false)}
                className="legacy-btn px-4 py-1.5 font-bold"
              >
                Dismiss
              </button>
              <button
                onClick={() => {
                  setExportModalOpen(false);
                  onTriggerRefactor();
                }}
                className="bg-indigo-600 hover:bg-indigo-700 text-white font-bold px-3 py-1.5 rounded text-xs shadow"
              >
                Refactor to Agent-Native &rarr;
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
