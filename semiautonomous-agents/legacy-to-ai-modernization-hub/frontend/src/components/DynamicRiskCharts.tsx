import React from 'react';
import {
  TrendingUp,
  Activity,
  Globe2,
  ShieldAlert,
} from 'lucide-react';
import { ShockImpactData } from '../types';

interface DynamicRiskChartsProps {
  impact: ShockImpactData;
  queryContext?: string;
}

export const DynamicRiskCharts: React.FC<DynamicRiskChartsProps> = ({ impact, queryContext: _queryContext = '' }) => {
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
    <div className="space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Chart 1: Value at Risk (99% VaR) Tail Distribution Curve */}
        <div className="cyber-glass rounded-2xl p-5 border border-cyan-500/30 flex flex-col justify-between transition-all shadow-xl">
          <div>
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <Activity className="h-4 w-4 text-cyan-400" />
                <h4 className="font-bold text-sm text-slate-100 uppercase tracking-wide font-sans">
                  DISTRIBUCIÓN DE RIESGO DE PORTAFOLIO (VaR 99%)
                </h4>
              </div>
              <span className="text-xs font-mono font-bold px-2 py-0.5 rounded bg-cyan-950 text-cyan-300 border border-cyan-800">
                VaR: ${impact.value_at_risk_99_m}M ({impact.var_delta_pct > 0 ? `+${impact.var_delta_pct}%` : `${impact.var_delta_pct}%`})
              </span>
            </div>

            <p className="text-xs text-slate-400 mb-4 leading-relaxed">
              Intervalo paramétrico de confianza al 99% a 10 días para los $750M USD en activos consolidados de las empresas del EBC (Metodología HR Ratings).
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
                  99% VaR: ${impact.value_at_risk_99_m}M USD
                </text>
              </svg>

              {/* Legend */}
              <div className="flex items-center justify-between text-[11px] font-mono text-slate-400 mt-2 px-2">
                <div className="flex items-center gap-2">
                  <span className="h-2 w-2 rounded-full bg-sky-400" />
                  <span>Línea Base ($84.5M USD)</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="h-2 w-2 rounded-full bg-rose-500 animate-pulse" />
                  <span className="text-rose-400 font-bold">Con Choque (${impact.value_at_risk_99_m}M USD)</span>
                </div>
              </div>
            </div>
          </div>

          {/* Dynamic Metric Bar in Spanish */}
          <div className="grid grid-cols-3 gap-2 mt-4 pt-3 border-t border-slate-800 text-center font-mono">
            <div className="bg-slate-950/60 p-2 rounded-lg border border-slate-800">
              <span className="text-[10px] text-slate-400 block font-sans">Arrastre en EBITDA</span>
              <span className="text-xs font-bold text-rose-400">-${impact.ebitda_impact_m}M USD</span>
            </div>
            <div className="bg-slate-950/60 p-2 rounded-lg border border-slate-800">
              <span className="text-[10px] text-slate-400 block font-sans">Cojín de Liquidez</span>
              <span
                className={`text-xs font-bold ${
                  impact.liquidity_buffer_status === 'STABLE'
                    ? 'text-emerald-400'
                    : impact.liquidity_buffer_status === 'VULNERABLE'
                    ? 'text-amber-400'
                    : 'text-rose-400'
                }`}
              >
                {impact.liquidity_buffer_status === 'STABLE' ? 'SOLVENTE (AAA)' : impact.liquidity_buffer_status}
              </span>
            </div>
            <div className="bg-slate-950/60 p-2 rounded-lg border border-slate-800">
              <span className="text-[10px] text-slate-400 block font-sans">Índice de Riesgo</span>
              <span className="text-xs font-bold text-amber-400">{impact.risk_score_index} / 100</span>
            </div>
          </div>
        </div>

        {/* Chart 2: 2026 Quarterly Cash Flow Sensitivity */}
        <div className="cyber-glass rounded-2xl p-5 border border-cyan-500/30 flex flex-col justify-between transition-all shadow-xl">
          <div>
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <TrendingUp className="h-4 w-4 text-cyan-400" />
                <h4 className="font-bold text-sm text-slate-100 uppercase tracking-wide font-sans">
                  SENSIBILIDAD DE FLUJO DE CAJA TRIMESTRAL 2026
                </h4>
              </div>
              <span className="text-xs font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                Trayectoria 4 Trimestres
              </span>
            </div>

            <p className="text-xs text-slate-400 mb-4 leading-relaxed">
              Comparación de flujo de caja libre proyectado vs trayectoria con compresión de margen operativo por retrasos y volatilidad cambiaria.
            </p>

            {/* Quarterly Bars */}
            <div className="space-y-3.5 pt-1">
              {impact.cash_flow_timeline.map((q, idx) => (
                <div key={idx} className="space-y-1">
                  <div className="flex justify-between text-xs font-mono">
                    <span className="text-slate-300 font-bold">{q.quarter}</span>
                    <div className="flex gap-3">
                      <span className="text-slate-500">${q.baseline_m}M base</span>
                      <span className="text-cyan-300 font-bold">
                        ${q.shocked_m}M ({q.delta_pct > 0 ? `+${q.delta_pct}%` : `${q.delta_pct}%`})
                      </span>
                    </div>
                  </div>

                  <div className="h-3 bg-slate-950 rounded-full overflow-hidden border border-slate-800 p-0.5 relative">
                    <div
                      className="h-full bg-slate-700/60 rounded-full"
                      style={{ width: `${(q.baseline_m / 200) * 100}%` }}
                    />
                    <div
                      className="h-full bg-gradient-to-r from-blue-500 to-cyan-400 rounded-full absolute top-0.5 left-0.5 transition-all duration-300"
                      style={{ width: `${(q.shocked_m / 200) * 100}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="pt-3 border-t border-slate-800 flex justify-between items-center text-xs font-mono text-slate-400 mt-4">
            <span>Arrastre Total Anual de Capital:</span>
            <span className="text-rose-400 font-bold">
              -${impact.cash_flow_timeline.reduce((acc, q) => acc + Math.abs(q.delta_m), 0).toFixed(1)}M USD Total
            </span>
          </div>
        </div>
      </div>

      {/* Regional Exposure and Supplier Fragility Matrix tailored for Mexico */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Regional Exposure Grid (Mexican Logistics Corridors) */}
        <div className="cyber-glass rounded-2xl p-5 border border-cyan-500/30 space-y-3 shadow-xl">
          <div className="flex items-center justify-between border-b border-slate-800 pb-2.5">
            <span className="font-bold text-sm text-cyan-300 uppercase tracking-wide flex items-center gap-2 font-sans">
              <Globe2 className="h-4 w-4" />
              Exposición por Región & Hubs Logísticos en México
            </span>
            <span className="text-xs font-mono text-slate-400">Total: $750M USD</span>
          </div>

          <div className="grid grid-cols-2 gap-3 pt-1">
            <div className="bg-slate-900/80 p-3 rounded-xl border border-slate-800 space-y-1">
              <div className="flex justify-between items-center">
                <span className="text-xs font-bold text-slate-200">Golfo & Veracruz (CICE)</span>
                <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-rose-950 text-rose-300 border border-rose-800 font-bold">
                  840 TEUs
                </span>
              </div>
              <div className="text-xs font-mono text-slate-400">Exposición: $42.5M USD &bull; Muelles saturados</div>
            </div>

            <div className="bg-slate-900/80 p-3 rounded-xl border border-slate-800 space-y-1">
              <div className="flex justify-between items-center">
                <span className="text-xs font-bold text-slate-200">Pacífico & Manzanillo</span>
                <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-amber-950 text-amber-300 border border-amber-800 font-bold">
                  580 TEUs
                </span>
              </div>
              <div className="text-xs font-mono text-slate-400">Exposición: $38.2M USD &bull; Farma e Insumos</div>
            </div>

            <div className="bg-slate-900/80 p-3 rounded-xl border border-slate-800 space-y-1">
              <div className="flex justify-between items-center">
                <span className="text-xs font-bold text-slate-200">Centro & Bajío (Silanes/Gloria)</span>
                <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-blue-950 text-blue-300 border border-blue-800 font-bold">
                  21d BUFFER
                </span>
              </div>
              <div className="text-xs font-mono text-slate-400">Exposición: $85.0M USD &bull; Plantas Toluca/GDL</div>
            </div>

            <div className="bg-slate-900/80 p-3 rounded-xl border border-slate-800 space-y-1">
              <div className="flex justify-between items-center">
                <span className="text-xs font-bold text-slate-200">Norte (Senda / Ferromex)</span>
                <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-800 font-bold">
                  CORREDOR ACTIVO
                </span>
              </div>
              <div className="text-xs font-mono text-slate-400">Exposición: $65.0M USD &bull; Hub Monterrey</div>
            </div>
          </div>
        </div>

        {/* Supplier Fragility Matrix (Mexican Companies in the Room) */}
        <div className="cyber-glass rounded-2xl p-5 border border-cyan-500/30 space-y-3 shadow-xl">
          <div className="flex items-center justify-between border-b border-slate-800 pb-2.5">
            <span className="font-bold text-sm text-cyan-300 uppercase tracking-wide flex items-center gap-2 font-sans">
              <ShieldAlert className="h-4 w-4" />
              Matriz de Fragilidad de Proveedores & Operadores (Empresas en la Sala)
            </span>
            <span className="text-xs font-mono text-slate-400">Scoring en Vivo</span>
          </div>

          <div className="space-y-2 pt-1">
            <div className="bg-slate-900/80 p-2.5 rounded-xl border border-slate-800 flex items-center justify-between">
              <div>
                <div className="text-xs font-bold text-slate-200">Grupo CICE (Terminal Bahía Norte)</div>
                <div className="text-[10px] text-slate-400 font-mono">Puerto de Veracruz &bull; 840 TEUs demorados</div>
              </div>
              <div className="text-right font-mono">
                <span className="text-xs font-bold text-rose-400">$42.5M USD</span>
                <span className="text-[10px] block text-rose-400 font-bold">ALERTA PUERTO</span>
              </div>
            </div>

            <div className="bg-slate-900/80 p-2.5 rounded-xl border border-slate-800 flex items-center justify-between">
              <div>
                <div className="text-xs font-bold text-slate-200">Laboratorios Silanes & Cremería Gloria</div>
                <div className="text-[10px] text-slate-400 font-mono">Plantas Toluca y GDL &bull; APIs y Lácteos</div>
              </div>
              <div className="text-right font-mono">
                <span className="text-xs font-bold text-amber-400">$38.2M USD</span>
                <span className="text-[10px] block text-amber-400 font-bold">BUFFER 21 DÍAS</span>
              </div>
            </div>

            <div className="bg-slate-900/80 p-2.5 rounded-xl border border-slate-800 flex items-center justify-between">
              <div>
                <div className="text-xs font-bold text-slate-200">Boxito & Macropay (Retail & Electrónica)</div>
                <div className="text-[10px] text-slate-400 font-mono">Compras Importadas expuestas a USD/MXN $20.80</div>
              </div>
              <div className="text-right font-mono">
                <span className="text-xs font-bold text-purple-400">$85.0M USD</span>
                <span className="text-[10px] block text-purple-400 font-bold">FORWARD FIX @ 19.40</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
