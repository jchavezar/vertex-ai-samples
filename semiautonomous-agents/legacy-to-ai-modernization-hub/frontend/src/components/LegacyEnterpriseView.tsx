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
  X,
  Table,
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
  const [loading, setLoading] = useState<boolean>(false);
  const [page, setPage] = useState<number>(1);
  const [pageSize, setPageSize] = useState(12);
  const [search, setSearch] = useState('');
  const [currency, setCurrency] = useState('');
  const [riskRating, setRiskRating] = useState('');
  const [clearingHouse, setClearingHouse] = useState('');
  const [simulateSlowQuery, setSimulateSlowQuery] = useState(true);
  const [exportModalOpen, setExportModalOpen] = useState(false);
  const [exportInfo, setExportInfo] = useState<any>(null);
  const [stepQueryResult, setStepQueryResult] = useState<any>(null);

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
      console.error('Export failed:', err);
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
          <span className="bg-amber-500/20 text-amber-300 px-2 py-0.5 border border-amber-500/40 rounded font-mono">
            {stepQueryResult
              ? `LIVE GCP BIGQUERY // ${stepQueryResult.dataset}`
              : 'STATUS: SYNCHRONIZED (ORACLE RAC 11g)'}
          </span>
          <button
            onClick={onTriggerRefactor}
            className="bg-indigo-600 hover:bg-indigo-700 text-white font-bold px-3 py-1 rounded text-xs shadow flex items-center gap-1.5 transition-all cursor-pointer"
          >
            <span>Modernize to Agent-Native &rarr;</span>
          </button>
        </div>
      </div>

      {/* Interactive 3-Day Manual SQL & CSV Consolidation Chain Simulator */}
      <MultiDepartmentQueryChain
        onTriggerRefactor={onTriggerRefactor}
        onStepQueryResult={(res) => {
          setStepQueryResult(res);
          if (res?.query_latency_ms) onUpdateLatency(res.query_latency_ms);
        }}
      />

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

        <form onSubmit={handleSearchSubmit} className="grid grid-cols-1 md:grid-cols-4 gap-3 text-xs">
          <div>
            <label className="block text-slate-600 font-semibold mb-1">
              Transaction ID / Entity / BIC:
            </label>
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="e.g. TX-2015-000012 or BNP"
              className="w-full px-2.5 py-1.5 border border-[#8fa2b4] rounded bg-white text-slate-900 font-mono shadow-inner"
            />
          </div>

          <div>
            <label className="block text-slate-600 font-semibold mb-1">
              Currency ISO:
            </label>
            <select
              value={currency}
              onChange={(e) => setCurrency(e.target.value)}
              className="w-full px-2.5 py-1.5 border border-[#8fa2b4] rounded bg-white text-slate-900 shadow-inner"
            >
              <option value="">-- ALL CURRENCIES --</option>
              <option value="USD">USD - US Dollar</option>
              <option value="EUR">EUR - Euro</option>
              <option value="GBP">GBP - British Pound</option>
              <option value="JPY">JPY - Japanese Yen</option>
              <option value="MXN">MXN - Mexican Peso</option>
            </select>
          </div>

          <div>
            <label className="block text-slate-600 font-semibold mb-1">
              Credit Risk Grade:
            </label>
            <select
              value={riskRating}
              onChange={(e) => setRiskRating(e.target.value)}
              className="w-full px-2.5 py-1.5 border border-[#8fa2b4] rounded bg-white text-slate-900 shadow-inner"
            >
              <option value="">-- ALL RISK TIERS --</option>
              <option value="AAA">Tier 1: AAA / Prime Sovereign</option>
              <option value="AA">Tier 2: AA+ / High Quality</option>
              <option value="A">Tier 3: A- / Investment Grade</option>
              <option value="BBB">Tier 4: BBB / Watchlist</option>
            </select>
          </div>

          <div>
            <label className="block text-slate-600 font-semibold mb-1">
              Clearing Facility:
            </label>
            <select
              value={clearingHouse}
              onChange={(e) => setClearingHouse(e.target.value)}
              className="w-full px-2.5 py-1.5 border border-[#8fa2b4] rounded bg-white text-slate-900 shadow-inner"
            >
              <option value="">-- ALL CLEARING HOUSES --</option>
              <option value="CME Group">CME Group (Chicago)</option>
              <option value="LCH Clearnet">LCH Clearnet (London)</option>
              <option value="Eurex Clearing">Eurex Clearing (Frankfurt)</option>
              <option value="ICE Clear">ICE Clear Credit</option>
            </select>
          </div>

          <div className="md:col-span-4 flex items-center justify-end gap-2 pt-2 border-t border-slate-300">
            {stepQueryResult && (
              <button
                type="button"
                onClick={() => setStepQueryResult(null)}
                className="legacy-btn px-3 py-1.5 text-xs text-slate-700 font-semibold flex items-center gap-1.5 mr-auto cursor-pointer"
              >
                <Table className="h-3.5 w-3.5" />
                <span>Restaurar Vista de ERP Global (20 Columnas)</span>
              </button>
            )}

            <button
              type="submit"
              disabled={loading}
              className="legacy-btn px-4 py-1.5 font-bold flex items-center gap-1.5 text-xs cursor-pointer"
            >
              <RefreshCw className={`h-3.5 w-3.5 ${loading ? 'animate-spin' : ''}`} />
              <span>Run Query</span>
            </button>
            <button
              type="button"
              onClick={handleExportCsv}
              className="legacy-btn px-4 py-1.5 font-bold flex items-center gap-1.5 text-xs cursor-pointer"
            >
              <Download className="h-3.5 w-3.5 text-slate-700" />
              <span>Export CSV</span>
            </button>
          </div>
        </form>
      </div>

      {/* Query Status Bar */}
      <div className="bg-[#d2dbe3] px-4 py-1.5 border-t border-l border-r border-[#99a8b5] flex flex-wrap items-center justify-between text-xs text-slate-700 font-mono">
        <div className="flex items-center gap-3">
          <span>
            DB Host: <strong className="text-slate-900">{stepQueryResult ? stepQueryResult.db_engine : (data?.db_engine || 'erp-prod-db04.corp')}</strong>
          </span>
          |
          <span>
            Rows: <strong className="text-slate-900">{stepQueryResult ? stepQueryResult.total_rows : (data?.total_records || 0)}</strong>
          </span>
          {stepQueryResult && (
            <>
              |
              <span className="text-emerald-700 font-bold">
                Dataset: {stepQueryResult.dataset}
              </span>
            </>
          )}
        </div>
        <div className="flex items-center gap-2">
          <span className="text-slate-700">
            Query Latency: <strong className="text-amber-700 font-bold">{stepQueryResult ? stepQueryResult.query_latency_ms : (data?.query_latency_ms || 0)} ms</strong>
          </span>
        </div>
      </div>

      {/* Main Table Container */}
      <div className="bg-white border-2 border-[#7c8d9e] shadow-inner overflow-x-auto relative min-h-[380px]">
        {loading && (
          <div className="absolute inset-0 bg-white/70 backdrop-blur-[1px] flex flex-col items-center justify-center z-20">
            <div className="h-10 w-10 border-4 border-slate-300 border-t-amber-600 rounded-full animate-spin mb-3"></div>
            <span className="font-bold text-slate-800 text-xs tracking-wider">
              FETCHING RELATIONAL RECORDSET...
            </span>
          </div>
        )}

        {stepQueryResult ? (
          /* ========================================================================= */
          /* Dynamic BigQuery Result Table (Shows Exact Multi-Department Query Output) */
          /* ========================================================================= */
          <div className="p-0">
            <div className="bg-[#1e293b] text-white px-4 py-2 flex items-center justify-between text-xs font-mono border-b border-slate-700">
              <div className="flex items-center gap-2">
                <Database className="h-4 w-4 text-cyan-400" />
                <span className="font-bold text-cyan-300">
                  {stepQueryResult.title} ({stepQueryResult.csv_name})
                </span>
              </div>
              <div className="flex items-center gap-3 text-[11px]">
                <span className="bg-emerald-950 text-emerald-300 px-2 py-0.5 rounded border border-emerald-700">
                  BigQuery Latency: {stepQueryResult.query_latency_ms}ms
                </span>
                <button
                  type="button"
                  onClick={() => setStepQueryResult(null)}
                  className="bg-slate-700 hover:bg-slate-600 text-white px-2 py-0.5 rounded text-[10px] cursor-pointer"
                >
                  Cerrar Vista de Paso &times;
                </button>
              </div>
            </div>

            <table className="w-full text-left border-collapse whitespace-nowrap text-xs font-sans">
              <thead>
                <tr className="bg-[#334155] text-white">
                  {stepQueryResult.headers.map((h: string, idx: number) => (
                    <th key={idx} className="p-2.5 border-r border-b border-slate-600 font-bold">
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200">
                {stepQueryResult.data.map((row: any, idx: number) => {
                  const values = Object.values(row);
                  return (
                    <tr
                      key={idx}
                      className={`hover:bg-amber-50/80 transition-colors ${
                        idx % 2 === 0 ? 'bg-white' : 'bg-[#f8fafc]'
                      }`}
                    >
                      {values.map((val: any, cIdx: number) => (
                        <td key={cIdx} className="p-2.5 border-r border-slate-200 font-mono text-slate-800">
                          {typeof val === 'number'
                            ? val.toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 2 })
                            : String(val)}
                        </td>
                      ))}
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        ) : (
          /* ========================================================================= */
          /* Default Monolithic 20-Column Table Container                              */
          /* ========================================================================= */
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
                  <td className="p-2 text-slate-700 border-r border-slate-300">
                    {row.tax_jurisdiction}
                  </td>
                  <td className="p-2 font-mono text-slate-600 border-r border-slate-300">
                    {row.dodd_frank_tag}
                  </td>
                  <td className="p-2 font-mono text-right border-r border-slate-300">
                    {row.basel_risk_weight_pct.toFixed(2)}%
                  </td>
                  <td className="p-2 border-r border-slate-300">
                    <span
                      className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${
                        row.sla_status === 'COMPLIANT'
                          ? 'bg-emerald-100 text-emerald-800'
                          : 'bg-rose-100 text-rose-800'
                      }`}
                    >
                      {row.sla_status}
                    </span>
                  </td>
                  <td className="p-2 font-mono text-[10px] text-slate-500 border-r border-slate-300">
                    {row.audit_timestamp}
                  </td>
                  <td className="p-2 font-mono text-slate-600 border-r border-slate-300">
                    {row.batch_id}
                  </td>
                  <td className="p-2 text-center border-r border-slate-300">
                    <span
                      className={`px-1.5 py-0.5 rounded text-[10px] font-mono font-bold ${
                        row.reconciliation_flag === 'MATCHED'
                          ? 'bg-slate-200 text-slate-700'
                          : 'bg-amber-200 text-amber-900'
                      }`}
                    >
                      {row.reconciliation_flag}
                    </span>
                  </td>
                  <td className="p-2 text-slate-500 italic max-w-[200px] truncate">
                    {row.override_notes || 'None'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Pagination Footer */}
      {!stepQueryResult && (
        <div className="bg-[#e4ebf1] p-3 border-b border-l border-r border-[#99a8b5] flex flex-wrap items-center justify-between text-xs text-slate-700">
          <div className="flex items-center gap-2">
            <span>Show</span>
            <select
              value={pageSize}
              onChange={(e) => setPageSize(Number(e.target.value))}
              className="border border-[#8fa2b4] bg-white rounded px-2 py-1 text-xs"
            >
              <option value="12">12 records</option>
              <option value="25">25 records</option>
              <option value="50">50 records</option>
            </select>
            <span>per page</span>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => {
                if (page > 1) {
                  setPage(page - 1);
                  loadData(page - 1);
                }
              }}
              disabled={page <= 1}
              className="legacy-btn px-2 py-1 disabled:opacity-40"
            >
              <ChevronLeft className="h-4 w-4" />
            </button>
            <span className="font-mono font-bold">
              Page {data?.page || 1} of {data?.total_pages || 1}
            </span>
            <button
              onClick={() => {
                if (data && page < data.total_pages) {
                  setPage(page + 1);
                  loadData(page + 1);
                }
              }}
              disabled={!data || page >= data.total_pages}
              className="legacy-btn px-2 py-1 disabled:opacity-40"
            >
              <ChevronRight className="h-4 w-4" />
            </button>
          </div>
        </div>
      )}

      {/* Legacy Batch Export Modal */}
      {exportModalOpen && exportInfo && (
        <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-white border-2 border-slate-600 rounded shadow-2xl max-w-md w-full overflow-hidden">
            <div className="bg-[#2c3e50] text-white px-4 py-2 flex items-center justify-between font-bold text-xs">
              <div className="flex items-center gap-2">
                <Clock className="h-4 w-4 text-amber-400" />
                <span>EXPORT BATCH JOB QUEUED (LEGACY DAEMON)</span>
              </div>
              <button
                onClick={() => setExportModalOpen(false)}
                className="hover:bg-slate-700 p-1 rounded"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            <div className="p-4 text-xs space-y-3">
              <div className="p-3 bg-amber-50 border border-amber-200 rounded text-slate-800 space-y-1">
                <div className="font-bold text-amber-800 flex items-center gap-1.5">
                  <AlertTriangle className="h-4 w-4 text-amber-600" />
                  <span>{exportInfo.status}</span>
                </div>
                <p className="text-[11px] text-slate-600">{exportInfo.message}</p>
              </div>

              <div className="font-mono text-[11px] bg-slate-100 p-2.5 rounded border border-slate-300 space-y-1">
                <div>
                  Job ID: <strong>{exportInfo.job_id}</strong>
                </div>
                <div>
                  Queue Position: <strong>#{exportInfo.queue_position}</strong>
                </div>
                <div>
                  Estimated Wait Time: <strong>{exportInfo.estimated_wait_time}</strong>
                </div>
                <div>
                  Worker: <strong>{exportInfo.queue_server}</strong>
                </div>
              </div>
            </div>

            <div className="bg-slate-100 px-4 py-2.5 border-t border-slate-300 flex justify-end">
              <button
                onClick={() => setExportModalOpen(false)}
                className="legacy-btn px-4 py-1.5 text-xs font-bold"
              >
                Dismiss
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
