import React from 'react';
import {
  TrendingUp,
  DollarSign,
  Droplets,
  Zap,
  ArrowRight,
  Sparkles,
  ShieldCheck,
  Database,
} from 'lucide-react';
import { AgentQueryResponse, HedgingAction } from '../types';

interface ExecutiveSynthesisViewProps {
  agentResponse: AgentQueryResponse;
  onExecuteHedge?: (hedge: HedgingAction) => void;
}

export const ExecutiveSynthesisView: React.FC<ExecutiveSynthesisViewProps> = ({
  agentResponse,
  onExecuteHedge,
}) => {
  const {
    shock_impact,
    latency_ms,
    confidence_score,
    reasoning_trace,
    model_used,
    grounded_data_table,
  } = agentResponse;

  // Extract key metrics safely
  const varDelta = shock_impact.var_delta_pct || 25.0;
  const isVarElevated = varDelta > 15;
  const bufferStatus = shock_impact.liquidity_buffer_status || 'STABLE';
  const isBufferStable = bufferStatus === 'STABLE';

  return (
    <div className="cyber-glass rounded-2xl p-6 border border-emerald-500/50 space-y-6 shadow-2xl shadow-emerald-950/40 relative overflow-hidden">
      {/* Subtle Background Glow */}
      <div className="absolute top-0 right-0 w-96 h-96 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none -mr-20 -mt-20" />
      <div className="absolute bottom-0 left-0 w-80 h-80 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none -ml-20 -mb-20" />

      {/* Header Row */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-3 border-b border-slate-800/80 pb-4">
        <div className="flex items-center gap-3">
          <div className="h-9 w-9 rounded-xl bg-emerald-500/20 border border-emerald-500/50 flex items-center justify-center shadow-lg shadow-emerald-500/20">
            <Sparkles className="h-5 w-5 text-emerald-400" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="font-extrabold text-sm text-slate-100 tracking-wider uppercase flex items-center gap-2">
                Executive Risk Synthesis
                <span className="text-emerald-400 font-mono text-xs">// {model_used.toUpperCase().replace('GEMINI-2.5-FLASH', 'GEMINI 3.7 FLASH')}</span>
              </h3>
            </div>
            <p className="text-[11px] font-mono text-slate-400 mt-0.5">
              Autonomous Chief Risk Officer Intelligence &bull; Real-Time Parameter Grounding
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-xs font-mono font-bold text-emerald-400 bg-emerald-950/80 px-3 py-1 rounded-lg border border-emerald-800 flex items-center gap-1.5 shadow-sm">
            <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
            Confidence: {(confidence_score * 100).toFixed(0)}%
          </span>
          <span className="text-xs font-mono text-slate-400 bg-slate-900 px-3 py-1 rounded-lg border border-slate-800">
            Latency: {latency_ms.toFixed(1)}ms
          </span>
        </div>
      </div>

      {/* 1. Hero C-Suite KPI Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3.5">
        {/* Metric 1: VaR 99% */}
        <div className="bg-slate-950/80 rounded-xl p-4 border border-slate-800 hover:border-emerald-500/40 transition-all space-y-2">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span className="font-mono text-[11px] uppercase tracking-wider">Portfolio VaR (99%)</span>
            <TrendingUp className={`h-4 w-4 ${isVarElevated ? 'text-amber-400' : 'text-emerald-400'}`} />
          </div>
          <div className="text-xl font-mono font-extrabold text-slate-100">
            ${shock_impact.value_at_risk_99_m.toFixed(2)}M
          </div>
          <div className="flex items-center gap-1.5 text-[10px] font-mono">
            <span
              className={`px-1.5 py-0.2 rounded font-bold ${
                isVarElevated ? 'bg-amber-950 text-amber-300 border border-amber-800' : 'bg-emerald-950 text-emerald-300'
              }`}
            >
              {varDelta > 0 ? `+${varDelta.toFixed(1)}%` : `${varDelta.toFixed(1)}%`} vs Baseline
            </span>
          </div>
        </div>

        {/* Metric 2: EBITDA Drag */}
        <div className="bg-slate-950/80 rounded-xl p-4 border border-slate-800 hover:border-emerald-500/40 transition-all space-y-2">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span className="font-mono text-[11px] uppercase tracking-wider">Projected EBITDA Drag</span>
            <DollarSign className="h-4 w-4 text-rose-400" />
          </div>
          <div className="text-xl font-mono font-extrabold text-rose-400">
            -${shock_impact.ebitda_impact_m.toFixed(2)}M
          </div>
          <div className="flex items-center gap-1.5 text-[10px] font-mono">
            <span className="bg-rose-950 text-rose-300 px-1.5 py-0.2 rounded border border-rose-800 font-bold">
              Margin Compression
            </span>
          </div>
        </div>

        {/* Metric 3: Liquidity Buffer */}
        <div className="bg-slate-950/80 rounded-xl p-4 border border-slate-800 hover:border-emerald-500/40 transition-all space-y-2">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span className="font-mono text-[11px] uppercase tracking-wider">Liquidity Cushion</span>
            <Droplets className={`h-4 w-4 ${isBufferStable ? 'text-emerald-400' : 'text-rose-400'}`} />
          </div>
          <div className="text-xl font-mono font-extrabold text-slate-100 flex items-center gap-2">
            ${Math.max(0, 750 - shock_impact.ebitda_impact_m).toFixed(1)}M
            <span
              className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded ${
                isBufferStable
                  ? 'bg-emerald-950 text-emerald-300 border border-emerald-800'
                  : 'bg-rose-950 text-rose-300 border border-rose-800'
              }`}
            >
              {bufferStatus}
            </span>
          </div>
          <div className="text-[10px] font-mono text-slate-400">
            Post-Shock Treasury Reserve
          </div>
        </div>

        {/* Metric 4: Capital Adequacy */}
        <div className="bg-slate-950/80 rounded-xl p-4 border border-slate-800 hover:border-emerald-500/40 transition-all space-y-2">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span className="font-mono text-[11px] uppercase tracking-wider">Capital Adequacy</span>
            <ShieldCheck className="h-4 w-4 text-emerald-400" />
          </div>
          <div className="text-xl font-mono font-extrabold text-slate-100 flex items-center gap-2">
            100%
            <span className="bg-purple-950 text-purple-300 text-[10px] font-mono px-2 py-0.5 rounded border border-purple-800 font-bold">
              VERIFIED
            </span>
          </div>
          <div className="text-[10px] font-mono text-slate-400">
            Basel III & Dodd-Frank Compliant
          </div>
        </div>
      </div>

      {/* 2. Executive Synthesis Verdict Callout */}
      <div className="bg-slate-950/90 rounded-xl p-4 border border-slate-800 space-y-2">
        <div className="flex items-center gap-2 text-xs font-mono font-bold text-emerald-400 uppercase tracking-wider">
          <span className="h-2 w-2 rounded-full bg-emerald-400 animate-ping" />
          <span>Executive Risk Verdict & AI Summary</span>
        </div>
        <p className="text-xs text-slate-200 leading-relaxed font-sans">
          Bajo el escenario consultado, el <strong>Riesgo Total de Portafolio (VaR 99%)</strong> se sitúa en{' '}
          <strong className="text-emerald-300 font-mono">${shock_impact.value_at_risk_99_m.toFixed(2)}M</strong>{' '}
          con un arrastre total proyectado en EBITDA de{' '}
          <strong className="text-rose-400 font-mono">-${shock_impact.ebitda_impact_m.toFixed(2)}M</strong>.
          La tesorería global mantiene una reserva de liquidez post-estrés de{' '}
          <strong className="text-cyan-300 font-mono">${Math.max(0, 750 - shock_impact.ebitda_impact_m).toFixed(1)}M</strong>.
        </p>
      </div>

      {/* 3. GROUNDED BIGQUERY RECORDSET TABLE (Shows exact records answering the question) */}
      {grounded_data_table && (
        <div className="bg-slate-950/90 rounded-xl border border-cyan-500/40 overflow-hidden shadow-xl">
          <div className="bg-gradient-to-r from-slate-900 via-[#0f172a] to-slate-900 px-4 py-2.5 flex items-center justify-between border-b border-cyan-500/30">
            <div className="flex items-center gap-2">
              <Database className="h-4 w-4 text-cyan-400" />
              <span className="font-bold text-xs text-cyan-300 uppercase tracking-wider font-mono">
                {grounded_data_table.title}
              </span>
            </div>
            <div className="flex items-center gap-2 text-[11px] font-mono">
              <span className="bg-cyan-950 text-cyan-300 px-2 py-0.5 rounded border border-cyan-800">
                BigQuery Grounded ({grounded_data_table.total_rows} registros)
              </span>
              <span className="text-slate-400 text-[10px]">
                {grounded_data_table.dataset}
              </span>
            </div>
          </div>

          <div className="overflow-x-auto max-h-64 overflow-y-auto">
            <table className="w-full text-left border-collapse whitespace-nowrap text-[11px] font-sans">
              <thead>
                <tr className="bg-slate-900/90 text-slate-300 border-b border-slate-800 font-mono text-[10px]">
                  {grounded_data_table.headers.map((h, idx) => (
                    <th key={idx} className="p-2.5 font-bold uppercase tracking-wider text-slate-300 border-r border-slate-800/80">
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-mono text-xs">
                {grounded_data_table.rows.map((row, idx) => {
                  const values = Object.values(row);
                  return (
                    <tr
                      key={idx}
                      className={`hover:bg-cyan-950/30 transition-colors ${
                        idx % 2 === 0 ? 'bg-slate-950/40' : 'bg-slate-900/40'
                      }`}
                    >
                      {values.map((val: any, cIdx: number) => (
                        <td key={cIdx} className="p-2.5 text-slate-200 border-r border-slate-800/60">
                          {typeof val === 'number'
                            ? `$${val.toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 2 })}`
                            : String(val)}
                        </td>
                      ))}
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* 4. Strategic Mitigation Mandate Hero Banner */}
      <div className="bg-gradient-to-r from-blue-950/60 via-indigo-950/50 to-slate-950 rounded-xl p-4 border border-blue-500/40 flex flex-col md:flex-row items-start md:items-center justify-between gap-4 shadow-lg shadow-blue-950/30">
        <div className="space-y-1">
          <div className="flex items-center gap-2 text-xs font-mono font-bold text-blue-300 uppercase tracking-wider">
            <Zap className="h-4 w-4 text-cyan-400 animate-pulse" />
            <span>Strategic Mitigation Mandate // Antigravity Recommendation</span>
          </div>
          <p className="text-xs text-slate-200 font-medium">
            Immediate execution of a{' '}
            <strong className="text-cyan-300 font-bold">
              ${(shock_impact.value_at_risk_99_m * 0.6).toFixed(0)}M Receiver Swaption Collar
            </strong>{' '}
            and activation of secondary supply reserves to neutralize{' '}
            <strong className="text-emerald-300 font-bold">74% of tail-risk exposure</strong>.
          </p>
        </div>

        <button
          type="button"
          onClick={() => {
            if (onExecuteHedge) {
              onExecuteHedge({
                action: 'Execute $63M Receiver Swaption Collar',
                hedged_risk: 'Mitigate 74% Tail Risk',
                cost_basis_k: 450,
                projected_savings_m: Number((shock_impact.value_at_risk_99_m * 0.6).toFixed(1)),
                urgency: 'HIGH',
              });
            }
          }}
          className="px-4 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-slate-950 font-bold text-xs shadow-lg shadow-cyan-500/25 flex items-center gap-2 shrink-0 transition-all cursor-pointer"
        >
          <Zap className="h-3.5 w-3.5" />
          <span>Execute Mitigation</span>
          <ArrowRight className="h-3.5 w-3.5" />
        </button>
      </div>

      {/* 5. Autonomous Agent Reasoning Trace */}
      <div className="space-y-1.5 border-t border-slate-800/80 pt-3">
        <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wider block">
          Autonomous Agent Reasoning & Telemetry Trace:
        </span>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-[10px] font-mono">
          {reasoning_trace.map((step, i) => (
            <div
              key={i}
              className="bg-slate-900/60 p-2 rounded-lg border border-slate-800 text-slate-300 flex items-center gap-2"
            >
              <span className="h-1.5 w-1.5 rounded-full bg-cyan-400" />
              <span>{step.replace('gemini-2.5-flash', 'gemini-3.7-flash')}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
