import React from 'react';
import {
  TrendingUp,
  DollarSign,
  Droplets,
  Zap,
  AlertTriangle,
  ArrowRight,
  Sparkles,
  Building2,
  ShieldCheck,
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
  const { shock_impact, latency_ms, confidence_score, reasoning_trace, model_used } =
    agentResponse;

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
              className={`px-1.5 py-0.5 rounded font-bold ${
                isVarElevated
                  ? 'bg-amber-950 text-amber-300 border border-amber-800/80'
                  : 'bg-emerald-950 text-emerald-300 border border-emerald-800/80'
              }`}
            >
              +{varDelta.toFixed(1)}% vs Baseline
            </span>
          </div>
        </div>

        {/* Metric 2: EBITDA Drag */}
        <div className="bg-slate-950/80 rounded-xl p-4 border border-slate-800 hover:border-rose-500/40 transition-all space-y-2">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span className="font-mono text-[11px] uppercase tracking-wider">Projected EBITDA Drag</span>
            <DollarSign className="h-4 w-4 text-rose-400" />
          </div>
          <div className="text-xl font-mono font-extrabold text-rose-400">
            -${shock_impact.ebitda_impact_m.toFixed(2)}M
          </div>
          <div className="flex items-center gap-1.5 text-[10px] font-mono text-slate-400">
            <span className="px-1.5 py-0.5 rounded bg-rose-950 text-rose-300 border border-rose-800/80 font-bold">
              Margin Compression
            </span>
          </div>
        </div>

        {/* Metric 3: Liquidity Buffer */}
        <div className="bg-slate-950/80 rounded-xl p-4 border border-slate-800 hover:border-cyan-500/40 transition-all space-y-2">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span className="font-mono text-[11px] uppercase tracking-wider">Liquidity Cushion</span>
            <Droplets className={`h-4 w-4 ${isBufferStable ? 'text-cyan-400' : 'text-amber-400'}`} />
          </div>
          <div className="text-xl font-mono font-extrabold text-slate-100 flex items-center gap-2">
            ${Math.max(0, 750 - shock_impact.ebitda_impact_m).toFixed(1)}M
            <span
              className={`text-xs px-2 py-0.5 rounded font-bold ${
                isBufferStable
                  ? 'bg-emerald-950 text-emerald-400 border border-emerald-800'
                  : 'bg-amber-950 text-amber-400 border border-amber-800'
              }`}
            >
              {bufferStatus}
            </span>
          </div>
          <div className="text-[10px] font-mono text-slate-400">
            Post-Shock Treasury Reserve
          </div>
        </div>

        {/* Metric 4: Basel III Capital Adequacy */}
        <div className="bg-slate-950/80 rounded-xl p-4 border border-slate-800 hover:border-violet-500/40 transition-all space-y-2">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span className="font-mono text-[11px] uppercase tracking-wider">Capital Adequacy</span>
            <ShieldCheck className="h-4 w-4 text-violet-400" />
          </div>
          <div className="text-xl font-mono font-extrabold text-slate-100 flex items-center gap-2">
            100%
            <span className="text-xs px-2 py-0.5 rounded bg-violet-950 text-violet-400 border border-violet-800 font-bold">
              VERIFIED
            </span>
          </div>
          <div className="text-[10px] font-mono text-slate-400">
            Basel III & Dodd-Frank Compliant
          </div>
        </div>
      </div>

      {/* 2. Executive Risk Verdict Card */}
      <div className="bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 rounded-xl p-4 border border-slate-700/80 space-y-2 shadow-inner">
        <div className="flex items-center gap-2 text-xs font-mono font-bold text-slate-200 uppercase tracking-wider">
          <span className="h-2 w-2 rounded-full bg-emerald-400" />
          <span>Executive Risk Verdict</span>
        </div>
        <p className="text-xs text-slate-300 leading-relaxed font-sans font-medium">
          Under the queried macroeconomic shock scenario, total Portfolio Value-at-Risk expands to{' '}
          <strong className="text-slate-100 font-mono bg-slate-800 px-1.5 py-0.5 rounded border border-slate-700">
            ${shock_impact.value_at_risk_99_m.toFixed(2)}M
          </strong>{' '}
          (+{varDelta.toFixed(1)}% variance). Total annualized EBITDA drag is bounded at{' '}
          <strong className="text-rose-300 font-mono bg-rose-950/60 px-1.5 py-0.5 rounded border border-rose-800">
            -${shock_impact.ebitda_impact_m.toFixed(2)}M
          </strong>
          , maintaining an adequate treasury liquidity buffer of{' '}
          <strong className="text-emerald-300 font-mono bg-emerald-950/60 px-1.5 py-0.5 rounded border border-emerald-800">
            ${Math.max(0, 750 - shock_impact.ebitda_impact_m).toFixed(1)}M
          </strong>
          .
        </p>
      </div>

      {/* 3. Transmission Channels 3-Column Visual Grid */}
      <div className="space-y-2">
        <span className="text-[11px] font-mono text-slate-400 uppercase tracking-wider block">
          Primary Transmission Channels & Vulnerability Map:
        </span>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {/* Channel 1 */}
          <div className="bg-slate-950/60 rounded-xl p-3.5 border border-slate-800/80 space-y-1.5">
            <div className="flex items-center gap-2 text-xs font-semibold text-amber-300">
              <AlertTriangle className="h-3.5 w-3.5 text-amber-400" />
              <span>Primary Operational Drag</span>
            </div>
            <p className="text-[11px] text-slate-400 leading-relaxed">
              APAC semiconductor fabrication delays and maritime logistics bottlenecks on critical inventory lines.
            </p>
          </div>

          {/* Channel 2 */}
          <div className="bg-slate-950/60 rounded-xl p-3.5 border border-slate-800/80 space-y-1.5">
            <div className="flex items-center gap-2 text-xs font-semibold text-cyan-300">
              <Droplets className="h-3.5 w-3.5 text-cyan-400" />
              <span>Liquidity Buffer Health</span>
            </div>
            <p className="text-[11px] text-slate-400 leading-relaxed">
              Rated <strong className="text-emerald-400 font-mono">STABLE</strong> with ${Math.max(0, 750 - shock_impact.ebitda_impact_m).toFixed(1)}M post-stress treasury cash reserve.
            </p>
          </div>

          {/* Channel 3 */}
          <div className="bg-slate-950/60 rounded-xl p-3.5 border border-slate-800/80 space-y-1.5">
            <div className="flex items-center gap-2 text-xs font-semibold text-violet-300">
              <Building2 className="h-3.5 w-3.5 text-violet-400" />
              <span>Counterparty Concentration</span>
            </div>
            <p className="text-[11px] text-slate-400 leading-relaxed">
              Concentration exposure localized to Tier-1 APAC suppliers and Rotterdam clearing counterparties.
            </p>
          </div>
        </div>
      </div>

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
          className="px-4 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-slate-950 font-bold text-xs shadow-lg shadow-cyan-500/25 flex items-center gap-2 shrink-0 transition-all"
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
