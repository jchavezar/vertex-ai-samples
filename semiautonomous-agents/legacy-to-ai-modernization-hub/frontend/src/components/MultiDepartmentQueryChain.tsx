import React, { useState } from 'react';
import {
  Database,
  FileSpreadsheet,
  CheckCircle2,
  AlertTriangle,
  ArrowRight,
  Sparkles,
  Zap,
  RefreshCw,
} from 'lucide-react';

interface MultiDepartmentQueryChainProps {
  onTriggerRefactor: () => void;
}

export const MultiDepartmentQueryChain: React.FC<MultiDepartmentQueryChainProps> = ({
  onTriggerRefactor,
}) => {
  const [step1State, setStep1State] = useState<'idle' | 'running' | 'done'>('idle');
  const [step2State, setStep2State] = useState<'idle' | 'running' | 'done'>('idle');
  const [step3State, setStep3State] = useState<'idle' | 'running' | 'done'>('idle');
  const [step4State, setStep4State] = useState<'idle' | 'running' | 'done'>('idle');

  const [activeTab, setActiveTab] = useState<1 | 2 | 3 | 4>(1);

  const runStep1 = () => {
    setStep1State('running');
    setTimeout(() => {
      setStep1State('done');
      setActiveTab(2);
    }, 1400);
  };

  const runStep2 = () => {
    setStep2State('running');
    setTimeout(() => {
      setStep2State('done');
      setActiveTab(3);
    }, 1100);
  };

  const runStep3 = () => {
    setStep3State('running');
    setTimeout(() => {
      setStep3State('done');
      setActiveTab(4);
    }, 950);
  };

  const runStep4 = () => {
    setStep4State('running');
    setTimeout(() => {
      setStep4State('done');
    }, 1500);
  };

  const runAllSteps = () => {
    setStep1State('running');
    setTimeout(() => {
      setStep1State('done');
      setStep2State('running');
      setTimeout(() => {
        setStep2State('done');
        setStep3State('running');
        setTimeout(() => {
          setStep3State('done');
          setStep4State('running');
          setTimeout(() => {
            setStep4State('done');
            setActiveTab(4);
          }, 1500);
        }, 950);
      }, 1100);
    }, 1400);
  };

  const resetAll = () => {
    setStep1State('idle');
    setStep2State('idle');
    setStep3State('idle');
    setStep4State('idle');
    setActiveTab(1);
  };

  return (
    <div className="bg-[#f0f3f6] border-2 border-[#7f8c8d] rounded-lg p-4 mb-5 shadow-inner font-sans text-slate-800">
      {/* Top Scenario Banner */}
      <div className="bg-[#34495e] text-white p-3 rounded flex flex-col md:flex-row items-start md:items-center justify-between gap-3 shadow-md">
        <div className="flex items-center gap-2.5">
          <div className="p-1.5 bg-amber-500/20 border border-amber-400/40 rounded text-amber-300">
            <AlertTriangle className="h-5 w-5" />
          </div>
          <div>
            <h4 className="font-bold text-xs uppercase tracking-wider text-amber-300">
              Traditional 3-Day Enterprise Bottleneck: Multi-Department SQL & CSV Consolidation Chain
            </h4>
            <p className="text-[11px] text-slate-300 font-mono mt-0.5">
              Scenario: &ldquo;If Taiwan supplier bottlenecks expand 90 days, what is our total cash & FX exposure?&rdquo;
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={runAllSteps}
            className="bg-amber-600 hover:bg-amber-700 text-white text-[11px] font-bold px-3 py-1.5 rounded shadow flex items-center gap-1.5 transition-all"
          >
            <RefreshCw className="h-3.5 w-3.5" />
            <span>Simulate Full 3-Day Cycle</span>
          </button>
          <button
            type="button"
            onClick={resetAll}
            className="bg-slate-700 hover:bg-slate-600 text-slate-200 text-[11px] font-semibold px-2.5 py-1.5 rounded transition-all"
          >
            Reset
          </button>
        </div>
      </div>

      {/* 4-Step Chain Tabs */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-2 my-3">
        {/* Step 1 Tab */}
        <button
          type="button"
          onClick={() => setActiveTab(1)}
          className={`p-2.5 rounded border text-left transition-all ${
            activeTab === 1
              ? 'bg-white border-blue-600 shadow-md ring-1 ring-blue-500'
              : 'bg-[#e2e8f0] border-slate-300 hover:bg-slate-100'
          }`}
        >
          <div className="flex items-center justify-between text-[11px] font-bold">
            <span className="text-slate-700">1. Group A (Procurement)</span>
            {step1State === 'done' && <CheckCircle2 className="h-4 w-4 text-emerald-600" />}
            {step1State === 'running' && <RefreshCw className="h-4 w-4 text-amber-600 animate-spin" />}
          </div>
          <p className="text-[10px] text-slate-500 font-mono mt-1">Oracle RAC // Open POs</p>
        </button>

        {/* Step 2 Tab */}
        <button
          type="button"
          onClick={() => setActiveTab(2)}
          className={`p-2.5 rounded border text-left transition-all ${
            activeTab === 2
              ? 'bg-white border-blue-600 shadow-md ring-1 ring-blue-500'
              : 'bg-[#e2e8f0] border-slate-300 hover:bg-slate-100'
          }`}
        >
          <div className="flex items-center justify-between text-[11px] font-bold">
            <span className="text-slate-700">2. Group B (Warehouse)</span>
            {step2State === 'done' && <CheckCircle2 className="h-4 w-4 text-emerald-600" />}
            {step2State === 'running' && <RefreshCw className="h-4 w-4 text-amber-600 animate-spin" />}
          </div>
          <p className="text-[10px] text-slate-500 font-mono mt-1">SAP HANA // Safety Stock</p>
        </button>

        {/* Step 3 Tab */}
        <button
          type="button"
          onClick={() => setActiveTab(3)}
          className={`p-2.5 rounded border text-left transition-all ${
            activeTab === 3
              ? 'bg-white border-blue-600 shadow-md ring-1 ring-blue-500'
              : 'bg-[#e2e8f0] border-slate-300 hover:bg-slate-100'
          }`}
        >
          <div className="flex items-center justify-between text-[11px] font-bold">
            <span className="text-slate-700">3. Group C (Treasury)</span>
            {step3State === 'done' && <CheckCircle2 className="h-4 w-4 text-emerald-600" />}
            {step3State === 'running' && <RefreshCw className="h-4 w-4 text-amber-600 animate-spin" />}
          </div>
          <p className="text-[10px] text-slate-500 font-mono mt-1">SQL Server // FX Swaps</p>
        </button>

        {/* Step 4 Tab */}
        <button
          type="button"
          onClick={() => setActiveTab(4)}
          className={`p-2.5 rounded border text-left transition-all ${
            activeTab === 4
              ? 'bg-white border-amber-600 shadow-md ring-1 ring-amber-500'
              : 'bg-[#e2e8f0] border-slate-300 hover:bg-slate-100'
          }`}
        >
          <div className="flex items-center justify-between text-[11px] font-bold">
            <span className="text-slate-800">4. Human Excel Merge</span>
            {step4State === 'done' && <CheckCircle2 className="h-4 w-4 text-emerald-600" />}
            {step4State === 'running' && <RefreshCw className="h-4 w-4 text-amber-600 animate-spin" />}
          </div>
          <p className="text-[10px] text-amber-700 font-bold font-mono mt-1">VLOOKUP & Reconcile (3 Days)</p>
        </button>
      </div>

      {/* Active Step Panel */}
      <div className="bg-white border border-[#bdc3c7] rounded p-4 shadow-sm">
        {activeTab === 1 && (
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Database className="h-4 w-4 text-blue-700" />
                <span className="font-bold text-xs text-slate-800 uppercase">
                  Step 1: Query Group A — Procurement ERP (Oracle Database)
                </span>
              </div>
              <span className="text-[11px] font-mono text-slate-500">Host: erp-prod-db04.corp</span>
            </div>

            <div className="bg-[#1e272e] text-[#d2dae2] p-3 rounded font-mono text-[11px] leading-relaxed border border-slate-700 overflow-x-auto">
              <code>
                SELECT po.vendor_id, v.vendor_name, po.part_code, SUM(po.notional_usd) AS total_committed<br />
                FROM po_headers po JOIN vendor_master v ON po.vendor_id = v.vendor_id<br />
                WHERE v.country_code = 'TW' AND po.status = 'OPEN'<br />
                GROUP BY po.vendor_id, v.vendor_name, po.part_code;
              </code>
            </div>

            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pt-1">
              <button
                type="button"
                disabled={step1State === 'running'}
                onClick={runStep1}
                className="bg-blue-700 hover:bg-blue-800 text-white font-bold text-xs px-4 py-2 rounded shadow flex items-center gap-2 transition-all disabled:opacity-50"
              >
                {step1State === 'running' ? (
                  <RefreshCw className="h-3.5 w-3.5 animate-spin" />
                ) : (
                  <Database className="h-3.5 w-3.5" />
                )}
                <span>{step1State === 'running' ? 'Executing Query (1,400ms)...' : 'Execute SQL Query 1 (Oracle)'}</span>
              </button>

              {step1State === 'done' && (
                <div className="bg-emerald-50 border border-emerald-300 text-emerald-800 text-xs px-3 py-1.5 rounded flex items-center gap-2 font-mono">
                  <FileSpreadsheet className="h-4 w-4 text-emerald-600" />
                  <span>✓ Output: <strong>PO_Commitments_APAC.csv</strong> (1,240 rows, $320M open commitments across 12 vendors)</span>
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 2 && (
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Database className="h-4 w-4 text-indigo-700" />
                <span className="font-bold text-xs text-slate-800 uppercase">
                  Step 2: Query Group B — Supply Chain & Warehouse (SAP HANA)
                </span>
              </div>
              <span className="text-[11px] font-mono text-slate-500">Host: sap-hana-wh02.corp</span>
            </div>

            <div className="bg-[#1e272e] text-[#d2dae2] p-3 rounded font-mono text-[11px] leading-relaxed border border-slate-700 overflow-x-auto">
              <code>
                SELECT part_sku, safety_stock_days, daily_burn_rate, line_stoppage_risk<br />
                FROM inventory_positions<br />
                WHERE supplier_id IN ('V-8821', 'V-9942') AND safety_stock_days &lt; 90;
              </code>
            </div>

            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pt-1">
              <button
                type="button"
                disabled={step2State === 'running'}
                onClick={runStep2}
                className="bg-indigo-700 hover:bg-indigo-800 text-white font-bold text-xs px-4 py-2 rounded shadow flex items-center gap-2 transition-all disabled:opacity-50"
              >
                {step2State === 'running' ? (
                  <RefreshCw className="h-3.5 w-3.5 animate-spin" />
                ) : (
                  <Database className="h-3.5 w-3.5" />
                )}
                <span>{step2State === 'running' ? 'Executing Query (1,100ms)...' : 'Execute SQL Query 2 (SAP HANA)'}</span>
              </button>

              {step2State === 'done' && (
                <div className="bg-emerald-50 border border-emerald-300 text-emerald-800 text-xs px-3 py-1.5 rounded flex items-center gap-2 font-mono">
                  <FileSpreadsheet className="h-4 w-4 text-emerald-600" />
                  <span>✓ Output: <strong>Warehouse_Runout_Risk.csv</strong> (840 rows, only 42 days buffer before assembly halt)</span>
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 3 && (
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Database className="h-4 w-4 text-purple-700" />
                <span className="font-bold text-xs text-slate-800 uppercase">
                  Step 3: Query Group C — Treasury & Derivatives (SQL Server)
                </span>
              </div>
              <span className="text-[11px] font-mono text-slate-500">Host: treasury-mssql-01.corp</span>
            </div>

            <div className="bg-[#1e272e] text-[#d2dae2] p-3 rounded font-mono text-[11px] leading-relaxed border border-slate-700 overflow-x-auto">
              <code>
                SELECT deal_id, ccy_pair, notional_amount, maturity_date, hedge_status<br />
                FROM fx_forward_contracts<br />
                WHERE maturity_date BETWEEN '2026-06-01' AND '2026-09-01' AND hedge_status = 'UNHEDGED';
              </code>
            </div>

            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pt-1">
              <button
                type="button"
                disabled={step3State === 'running'}
                onClick={runStep3}
                className="bg-purple-700 hover:bg-purple-800 text-white font-bold text-xs px-4 py-2 rounded shadow flex items-center gap-2 transition-all disabled:opacity-50"
              >
                {step3State === 'running' ? (
                  <RefreshCw className="h-3.5 w-3.5 animate-spin" />
                ) : (
                  <Database className="h-3.5 w-3.5" />
                )}
                <span>{step3State === 'running' ? 'Executing Query (950ms)...' : 'Execute SQL Query 3 (SQL Server)'}</span>
              </button>

              {step3State === 'done' && (
                <div className="bg-emerald-50 border border-emerald-300 text-emerald-800 text-xs px-3 py-1.5 rounded flex items-center gap-2 font-mono">
                  <FileSpreadsheet className="h-4 w-4 text-emerald-600" />
                  <span>✓ Output: <strong>Treasury_FX_Exposure.csv</strong> (310 rows, 2 unhedged contracts, $14.2M unhedged)</span>
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 4 && (
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <FileSpreadsheet className="h-4 w-4 text-amber-700" />
                <span className="font-bold text-xs text-slate-800 uppercase">
                  Step 4: Manual Excel Consolidation (VLOOKUPs, Pivot Tables & Human Reconciliation)
                </span>
              </div>
              <span className="text-[11px] font-mono text-amber-700 font-bold bg-amber-100 px-2 py-0.5 rounded border border-amber-300">
                ⏳ Human Bottleneck: ~2.5 Business Days
              </span>
            </div>

            <div className="bg-amber-50/70 border border-amber-300 rounded p-3 text-xs text-slate-700 space-y-2">
              <div className="flex items-center gap-2 text-amber-800 font-bold">
                <AlertTriangle className="h-4 w-4 text-amber-600" />
                <span>The Human Friction Points in Traditional Systems:</span>
              </div>
              <ul className="list-disc list-inside space-y-1 text-[11px] font-mono text-slate-600">
                <li>Analyst must manually join 3 CSVs via <code>=XLOOKUP(A2, PO_Commitments!A:A, Inventory!C:C)</code>.</li>
                <li>Unmatched vendor SKU codes require 4 back-and-forth emails between Supply Chain and Treasury.</li>
                <li>CFO/Board presentation must be manually prepared as a 12-slide PowerPoint.</li>
              </ul>
            </div>

            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pt-1">
              <button
                type="button"
                disabled={step4State === 'running'}
                onClick={runStep4}
                className="bg-amber-600 hover:bg-amber-700 text-white font-bold text-xs px-4 py-2 rounded shadow flex items-center gap-2 transition-all disabled:opacity-50"
              >
                {step4State === 'running' ? (
                  <RefreshCw className="h-3.5 w-3.5 animate-spin" />
                ) : (
                  <FileSpreadsheet className="h-3.5 w-3.5" />
                )}
                <span>{step4State === 'running' ? 'Reconciling Spreadsheets in Excel...' : '📊 Consolidate & Join Spreadsheets (Takes 3 Days)'}</span>
              </button>

              {step4State === 'done' && (
                <div className="bg-emerald-100 border border-emerald-400 text-emerald-900 text-xs px-3 py-1.5 rounded font-mono font-bold">
                  ✓ Consolidated Result: $105.6M Net Cash at Risk &bull; -$100.8M EBITDA Impact (Calculated after 3 days)
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* The Antigravity Modernization Superpower CTA Banner */}
      <div className="mt-4 bg-gradient-to-r from-[#0f172a] via-[#1e1b4b] to-[#0f172a] text-white p-4 rounded-xl border border-cyan-500/50 flex flex-col md:flex-row items-start md:items-center justify-between gap-4 shadow-xl">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <Zap className="h-4 w-4 text-cyan-400 animate-pulse" />
            <span className="text-xs font-bold text-cyan-300 uppercase tracking-wider">
              The AI Agentic Transformation // Zero Human Friction
            </span>
          </div>
          <p className="text-xs text-slate-200 font-medium">
            Instead of 4 manual SQL queries and 3 days of Excel VLOOKUPs, <strong>Antigravity executes all tools concurrently in 35ms</strong> and compiles the live 2026 Interactive Boardroom Cockpit!
          </p>
        </div>

        <button
          type="button"
          onClick={onTriggerRefactor}
          className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-slate-950 font-extrabold text-xs shadow-lg shadow-cyan-500/30 flex items-center gap-2 shrink-0 transition-all cursor-pointer"
        >
          <Sparkles className="h-4 w-4 text-slate-950" />
          <span>Trigger Agentic Chain (3.5s)</span>
          <ArrowRight className="h-4 w-4 text-slate-950" />
        </button>
      </div>
    </div>
  );
};
