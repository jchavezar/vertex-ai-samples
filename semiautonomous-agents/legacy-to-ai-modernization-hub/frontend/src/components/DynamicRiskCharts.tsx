import React from 'react';
import {
  TrendingUp,
  Activity,
  Globe2,
  ShieldAlert,
  Zap,
} from 'lucide-react';
import { ShockImpactData } from '../types';

interface DynamicRiskChartsProps {
  impact: ShockImpactData;
  queryContext?: string;
}

export const DynamicRiskCharts: React.FC<DynamicRiskChartsProps> = ({ impact, queryContext = '' }) => {
  const isCollarQuery = queryContext.toLowerCase().includes('collar') || queryContext.toLowerCase().includes('hedge');
  const isSupplierQuery = queryContext.toLowerCase().includes('supplier') || queryContext.toLowerCase().includes('default');
  const isFedRateQuery = queryContext.toLowerCase().includes('rate') || queryContext.toLowerCase().includes('fed') || queryContext.toLowerCase().includes('bps');

  // SVG distribution curve calculation
  const meanX = 180;
  const stdDev = 40 + (impact.risk_score_index / 100) * 25;
  const shockShift = (impact.value_at_risk_99_m - 84.5) * 1.5;

  const generateBellPoints = (shift = 0, spread = 40) => {
    const points = [];
    for (let x = 20; x <= 340; x += 5) {
      const z = (x - (meanX + shift)) / spread;
      const y = 140 - Math.exp(-0.5 * z * z) * 110;
      points.push(`${x},${y.toFixed(1)}`);
    }
    return points.join(' ');
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Chart 1: Value at Risk (99% VaR) Tail Distribution Curve */}
      <div className="cyber-glass rounded-2xl p-5 border border-cyan-500/30 flex flex-col justify-between transition-all">
        <div>
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <Activity className="h-4 w-4 text-cyan-400" />
              <h4 className="font-bold text-sm text-slate-100 uppercase tracking-wide">
                99% Value-at-Risk (VaR) Distribution
              </h4>
            </div>
            <span className="text-xs font-mono font-bold px-2 py-0.5 rounded bg-cyan-950 text-cyan-300 border border-cyan-800">
              VaR: ${impact.value_at_risk_99_m}M ({impact.var_delta_pct > 0 ? `+${impact.var_delta_pct}%` : `${impact.var_delta_pct}%`})
            </span>
          </div>

          <p className="text-xs text-slate-400 mb-4">
            Parametric 10-day 99% confidence interval reflecting real-time duration and volatility shocks.
          </p>

          {/* SVG Canvas */}
          <div className="bg-slate-950/80 rounded-xl p-3 border border-slate-800 relative">
            <svg viewBox="0 0 360 160" className="w-full h-44 overflow-visible">
              <defs>
                <linearGradient id="baselineGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#38bdf8" stopOpacity="0.2" />
                  <stop offset="100%" stopColor="#38bdf8" stopOpacity="0.0" />
                </linearGradient>
                <linearGradient id="shockedGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#f43f5e" stopOpacity="0.35" />
                  <stop offset="100%" stopColor="#f43f5e" stopOpacity="0.0" />
                </linearGradient>
              </defs>

              {/* Grid lines */}
              <line x1="20" y1="140" x2="340" y2="140" stroke="#334155" strokeWidth="1" />
              <line x1="180" y1="20" x2="180" y2="140" stroke="#334155" strokeDasharray="3 3" />

              {/* Baseline Curve */}
              <polyline
                fill="url(#baselineGrad)"
                stroke="#38bdf8"
                strokeWidth="2"
                strokeDasharray="4 2"
                points={`20,140 ${generateBellPoints(0, 40)} 340,140`}
              />

              {/* Shocked Curve */}
              <polyline
                fill="url(#shockedGrad)"
                stroke="#f43f5e"
                strokeWidth="2.5"
                points={`20,140 ${generateBellPoints(shockShift, stdDev)} 340,140`}
              />

              {/* Tail Risk Cutoff Line */}
              <line
                x1={Math.min(330, 240 + shockShift * 0.7)}
                y1="10"
                x2={Math.min(330, 240 + shockShift * 0.7)}
                y2="140"
                stroke="#fb7185"
                strokeWidth="2"
              />
              <text
                x={Math.min(320, 245 + shockShift * 0.7)}
                y="25"
                fill="#fb7185"
                fontSize="10"
                fontFamily="monospace"
                fontWeight="bold"
              >
                99% VaR: ${impact.value_at_risk_99_m}M
              </text>
            </svg>

            {/* Legend */}
            <div className="flex items-center justify-between text-[11px] font-mono text-slate-400 mt-2 px-2">
              <div className="flex items-center gap-2">
                <span className="h-2 w-2 rounded-full bg-sky-400" />
                <span>Baseline ($84.5M)</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="h-2 w-2 rounded-full bg-rose-500 animate-pulse" />
                <span className="text-rose-400 font-bold">Shocked (${impact.value_at_risk_99_m}M)</span>
              </div>
            </div>
          </div>
        </div>

        {/* Dynamic Metric Bar */}
        <div className="grid grid-cols-3 gap-2 mt-4 pt-3 border-t border-slate-800 text-center font-mono">
          <div className="bg-slate-950/60 p-2 rounded-lg border border-slate-800">
            <span className="text-[10px] text-slate-400 block">EBITDA Exposure</span>
            <span className="text-xs font-bold text-rose-400">-${impact.ebitda_impact_m}M</span>
          </div>
          <div className="bg-slate-950/60 p-2 rounded-lg border border-slate-800">
            <span className="text-[10px] text-slate-400 block">Liquidity Buffer</span>
            <span
              className={`text-xs font-bold ${
                impact.liquidity_buffer_status === 'STABLE'
                  ? 'text-emerald-400'
                  : impact.liquidity_buffer_status === 'VULNERABLE'
                  ? 'text-amber-400'
                  : 'text-rose-400'
              }`}
            >
              {impact.liquidity_buffer_status}
            </span>
          </div>
          <div className="bg-slate-950/60 p-2 rounded-lg border border-slate-800">
            <span className="text-[10px] text-slate-400 block">Risk Index</span>
            <span className="text-xs font-bold text-amber-400">{impact.risk_score_index} / 100</span>
          </div>
        </div>
      </div>

      {/* Chart 2: Dynamic Contextual Chart (Morphs based on Conversation) */}
      <div className="cyber-glass rounded-2xl p-5 border border-cyan-500/30 flex flex-col justify-between transition-all">
        {isCollarQuery ? (
          /* Dynamic Collar Hedge Payoff Diagram (Synthesized when discussing hedges) */
          <div>
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <Zap className="h-4 w-4 text-cyan-400" />
                <h4 className="font-bold text-sm text-slate-100 uppercase tracking-wide">
                  Dynamic Collar Hedge Payoff Profile
                </h4>
              </div>
              <span className="text-xs font-mono font-bold px-2 py-0.5 rounded bg-blue-950 text-cyan-300 border border-blue-800">
                Zero-Cost Collar Structure
              </span>
            </div>
            <p className="text-xs text-slate-400 mb-4">
              Real-time derivative collar: Caps rate downside while protecting against 74% of tail liquidity risk.
            </p>

            <div className="bg-slate-950/80 rounded-xl p-3 border border-slate-800 relative">
              <svg viewBox="0 0 360 140" className="w-full h-40">
                {/* Axes */}
                <line x1="20" y1="70" x2="340" y2="70" stroke="#475569" strokeWidth="1" strokeDasharray="2 2" />
                <line x1="180" y1="10" x2="180" y2="130" stroke="#475569" strokeWidth="1" />

                {/* Collar Payoff Line */}
                <polyline
                  fill="none"
                  stroke="#38bdf8"
                  strokeWidth="3"
                  points="20,110 100,110 260,30 340,30"
                />

                {/* Shaded Protection Zone */}
                <rect x="20" y="10" width="80" height="120" fill="#0284c7" fillOpacity="0.15" />
                <text x="30" y="30" fill="#38bdf8" fontSize="10" fontFamily="monospace" fontWeight="bold">
                  Protected Zone
                </text>

                {/* Shaded Cap Zone */}
                <rect x="260" y="10" width="80" height="120" fill="#a855f7" fillOpacity="0.15" />
                <text x="270" y="125" fill="#c084fc" fontSize="10" fontFamily="monospace" fontWeight="bold">
                  Capped Zone
                </text>
              </svg>

              <div className="flex items-center justify-between text-[11px] font-mono text-slate-300 mt-2 px-1">
                <span>Floor: <strong>-50 bps</strong></span>
                <span className="text-cyan-400 font-bold">Protected Delta: $63.0M</span>
                <span>Cap: <strong>+150 bps</strong></span>
              </div>
            </div>
          </div>
        ) : (
          /* Default: Quarterly Cash Flow Sensitivity */
          <div>
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <TrendingUp className="h-4 w-4 text-cyan-400" />
                <h4 className="font-bold text-sm text-slate-100 uppercase tracking-wide">
                  2026 Quarterly Cash Flow Sensitivity
                </h4>
              </div>
              <span className="text-xs font-mono font-bold px-2 py-0.5 rounded bg-cyan-950 text-cyan-300 border border-cyan-800">
                4-Quarter Trajectory
              </span>
            </div>

            <p className="text-xs text-slate-400 mb-4">
              Comparison of baseline quarterly free cash flow versus shocked trajectory with margin compression.
            </p>

            {/* Bars */}
            <div className="space-y-3 bg-slate-950/80 rounded-xl p-4 border border-slate-800">
              {impact.cash_flow_timeline.map((q) => {
                const shockedPct = Math.max(10, Math.min(100, (q.shocked_m / q.baseline_m) * 100));

                return (
                  <div key={q.quarter} className="space-y-1">
                    <div className="flex items-center justify-between text-xs font-mono">
                      <span className="font-bold text-slate-200">{q.quarter}</span>
                      <div className="flex items-center gap-3">
                        <span className="text-slate-400">${q.baseline_m}M base</span>
                        <span className="font-bold text-rose-400">
                          ${q.shocked_m.toFixed(1)}M ({q.delta_pct > 0 ? `+${q.delta_pct}%` : `${q.delta_pct}%`})
                        </span>
                      </div>
                    </div>

                    <div className="h-3 w-full bg-slate-900 rounded-full overflow-hidden flex relative">
                      <div
                        className="h-full bg-gradient-to-r from-cyan-500 to-blue-500 rounded-full transition-all duration-300"
                        style={{ width: `${shockedPct}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Cash Flow Summary Footer */}
        <div className="mt-4 pt-3 border-t border-slate-800 flex items-center justify-between text-xs font-mono">
          <span className="text-slate-400">Net Full-Year Capital Drag:</span>
          <span className="font-bold text-rose-400">
            -${impact.cash_flow_timeline.reduce((acc, q) => acc + Math.abs(q.delta_m), 0).toFixed(1)}M Total
          </span>
        </div>
      </div>

      {/* Chart 3: Regional Exposure Breakdown */}
      <div className="cyber-glass rounded-2xl p-5 border border-cyan-500/30">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Globe2 className="h-4 w-4 text-cyan-400" />
            <h4 className="font-bold text-sm text-slate-100 uppercase tracking-wide">
              Regional Fragility & Exposure
            </h4>
          </div>
          <span className="text-xs font-mono text-slate-400">
            Total Notional: ${impact.total_portfolio_value_m}M
          </span>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {impact.regional_exposure.map((reg) => (
            <div
              key={reg.region}
              className={`bg-slate-950/80 p-3 rounded-xl border transition-all flex flex-col justify-between ${
                isFedRateQuery && reg.region === 'North America'
                  ? 'border-cyan-500/80 ring-1 ring-cyan-500/50 shadow-lg shadow-cyan-500/20'
                  : 'border-slate-800'
              }`}
            >
              <div>
                <div className="flex justify-between items-start mb-1">
                  <span className="font-bold text-xs text-slate-200">{reg.region}</span>
                  <span
                    className={`text-[9px] font-mono font-bold px-1.5 py-0.5 rounded ${
                      reg.status === 'CRITICAL'
                        ? 'bg-rose-950 text-rose-400 border border-rose-800'
                        : reg.status === 'ELEVATED'
                        ? 'bg-amber-950 text-amber-400 border border-amber-800'
                        : 'bg-slate-800 text-slate-400'
                    }`}
                  >
                    {reg.status}
                  </span>
                </div>
                <div className="text-[11px] font-mono text-slate-400">
                  Notional: <strong className="text-slate-200">${reg.notional_m}M</strong>
                </div>
              </div>
              <div className="mt-3 pt-2 border-t border-slate-800/80 text-[11px] font-mono">
                <span className="text-slate-500">VaR Exp: </span>
                <span className="text-cyan-300 font-bold">${reg.var_m}M</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Chart 4: Supplier Fragility Matrix */}
      <div className="cyber-glass rounded-2xl p-5 border border-cyan-500/30">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <ShieldAlert className="h-4 w-4 text-amber-400" />
            <h4 className="font-bold text-sm text-slate-100 uppercase tracking-wide">
              Critical Supplier Fragility Matrix
            </h4>
          </div>
          <span className="text-xs font-mono text-slate-400">
            Autonomous Risk Scoring
          </span>
        </div>

        <div className="space-y-2.5">
          {impact.supplier_fragility_matrix.map((sup) => (
            <div
              key={sup.name}
              className={`bg-slate-950/80 p-3 rounded-xl border flex flex-col sm:flex-row sm:items-center justify-between gap-2 transition-all ${
                isSupplierQuery && sup.location.includes('APAC')
                  ? 'border-amber-500/80 ring-1 ring-amber-500/50 shadow-lg shadow-amber-500/20'
                  : 'border-slate-800'
              }`}
            >
              <div>
                <div className="flex items-center gap-2">
                  <span className="font-bold text-xs text-slate-200">{sup.name}</span>
                  <span className="text-[10px] text-slate-500">({sup.category})</span>
                </div>
                <div className="text-[10px] font-mono text-slate-400 mt-0.5">
                  Location: {sup.location} &bull; Exposure: ${sup.exposure_m}M
                </div>
              </div>

              <div className="flex items-center gap-3">
                <div className="text-right">
                  <span className="text-[10px] text-slate-500 block font-mono">Fragility Score</span>
                  <span
                    className={`font-mono font-bold text-xs ${
                      sup.fragility_score > 60
                        ? 'text-rose-400'
                        : sup.fragility_score > 35
                        ? 'text-amber-400'
                        : 'text-emerald-400'
                    }`}
                  >
                    {sup.fragility_score}%
                  </span>
                </div>
                <div
                  className={`px-2 py-1 rounded text-[10px] font-mono font-bold ${
                    sup.tier === 'CRITICAL'
                      ? 'bg-rose-950 text-rose-300 border border-rose-800'
                      : sup.tier === 'WATCH'
                      ? 'bg-amber-950 text-amber-300 border border-amber-800'
                      : 'bg-emerald-950 text-emerald-300 border border-emerald-800'
                  }`}
                >
                  {sup.tier}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
