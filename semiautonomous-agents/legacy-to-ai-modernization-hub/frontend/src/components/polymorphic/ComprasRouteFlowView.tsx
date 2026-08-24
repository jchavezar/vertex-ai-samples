import React, { useState } from 'react';
import {
  Package,
  Truck,
  ArrowRight,
  ShieldCheck,
  AlertTriangle,
  RotateCcw,
  Sliders,
  CheckCircle2,
} from 'lucide-react';
import { GroundedTableData } from '../../types';

interface ComprasRouteFlowViewProps {
  tableData?: GroundedTableData;
}

export const ComprasRouteFlowView: React.FC<ComprasRouteFlowViewProps> = ({
  tableData,
}) => {
  const [divertPct, setDivertPct] = useState(30);
  const [activeTab, setActiveTab] = useState<'flow' | 'table'>('flow');
  const [appliedAlternative, setAppliedAlternative] = useState(false);

  // Dynamic calculations based on diversion slider
  const totalNotional = 320.6;
  const delayedNotional = Number((totalNotional * (1 - divertPct / 100)).toFixed(1));
  const divertedNotional = Number((totalNotional * (divertPct / 100)).toFixed(1));
  const originalDelayDays = 65;
  const mitigatedDelayDays = Math.max(15, Math.round(originalDelayDays * (1 - divertPct / 120)));

  return (
    <div className="space-y-6 animate-zoom-entrance">
      {/* Top Banner: Domain-Specific Heading & View Switcher */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 bg-gradient-to-r from-blue-950/90 via-slate-900 to-indigo-950/90 p-5 rounded-2xl border-2 border-blue-500/50 shadow-xl">
        <div className="flex items-center gap-3.5">
          <div className="h-12 w-12 rounded-xl bg-blue-500/20 border-2 border-blue-400 flex items-center justify-center shadow-lg shadow-blue-500/30">
            <Truck className="h-6 w-6 text-blue-300 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-base sm:text-lg font-black text-slate-100 font-sans tracking-wide">
                MAPA DE FLUJO LOGÍSTICO & ASIGNACIÓN DE PROVEEDORES
              </h3>
              <span className="text-[10px] font-mono px-2.5 py-0.5 rounded-full bg-blue-900 text-blue-200 border border-blue-600 font-bold">
                BIGQUERY LIVE
              </span>
            </div>
            <p className="text-xs sm:text-sm text-slate-300">
              Visualización topológica de los $320.6M USD comprometidos con proveedores en Taiwán y rutas de desvío.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 bg-slate-950/90 p-1.5 rounded-xl border border-slate-800 self-stretch sm:self-auto justify-center">
          <button
            type="button"
            onClick={() => setActiveTab('flow')}
            className={`px-4 py-2 rounded-lg font-mono text-xs font-bold transition-all cursor-pointer ${
              activeTab === 'flow'
                ? 'bg-blue-600 text-white shadow-md shadow-blue-600/30'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Diagrama de Nodos y Rutas
          </button>
          <button
            type="button"
            onClick={() => setActiveTab('table')}
            className={`px-4 py-2 rounded-lg font-mono text-xs font-bold transition-all cursor-pointer ${
              activeTab === 'table'
                ? 'bg-blue-600 text-white shadow-md shadow-blue-600/30'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Tabla de Órdenes BigQuery ({tableData?.total_rows || 12})
          </button>
        </div>
      </div>

      {/* Interactive Visual Metaphor: Supply Chain Route & Node Network */}
      {activeTab === 'flow' && (
        <div className="space-y-6">
          {/* Main Visual Flow Canvas */}
          <div className="bg-slate-950/90 rounded-3xl p-6 sm:p-8 border-2 border-blue-500/40 shadow-2xl space-y-6 relative overflow-hidden">
            <div className="flex items-center justify-between border-b border-slate-800 pb-4">
              <span className="text-xs sm:text-sm font-mono font-bold text-blue-300 uppercase tracking-wider flex items-center gap-2">
                <Package className="h-4 w-4" />
                Flujo de Cadena de Suministro: Origen Kaohsiung &rarr; Destino Austin TX
              </span>
              <span className="text-xs font-mono text-slate-400">
                Retraso Mitigado: <strong className="text-emerald-400 font-bold">{mitigatedDelayDays} Días</strong> (vs 65 días base)
              </span>
            </div>

            {/* Topographic Visual Nodes Flow */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 items-center">
              {/* Origin Node: Kaohsiung Chokepoint */}
              <div className="lg:col-span-3 bg-gradient-to-br from-rose-950/80 to-slate-900 p-5 rounded-2xl border-2 border-rose-500/60 shadow-lg space-y-2.5">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-mono font-bold text-rose-300 flex items-center gap-1.5">
                    <AlertTriangle className="h-4 w-4 text-rose-400" />
                    Origen (Cuello de Botella)
                  </span>
                  <span className="text-[10px] font-mono bg-rose-900 text-rose-200 px-2 py-0.5 rounded font-bold">
                    BLOQUEO
                  </span>
                </div>
                <div className="text-xl font-mono font-black text-slate-100">
                  Puerto de Kaohsiung
                </div>
                <p className="text-xs text-slate-300 leading-snug">
                  12 POs comprometidas por <strong>${totalNotional}M USD</strong>. Retraso estimado marítimo de +45 a 90 días.
                </p>
                <div className="pt-2 border-t border-rose-900/60 flex justify-between text-[11px] font-mono">
                  <span className="text-slate-400">Tránsito normal:</span>
                  <span className="text-rose-300 font-bold">+65 días retraso</span>
                </div>
              </div>

              {/* Connecting Channel Arrow */}
              <div className="lg:col-span-1 flex items-center justify-center py-2 lg:py-0">
                <div className="flex lg:flex-col items-center gap-1 text-cyan-400 animate-pulse">
                  <ArrowRight className="h-6 w-6 rotate-90 lg:rotate-0" />
                </div>
              </div>

              {/* Middle Suppliers Allocation Breakdown */}
              <div className="lg:col-span-4 bg-slate-900/90 p-5 rounded-2xl border-2 border-slate-700 shadow-lg space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-mono font-bold text-cyan-300">
                    Proveedores Clave Expuestos (Taiwán)
                  </span>
                  <span className="text-xs font-mono text-slate-400">3 Fábricas</span>
                </div>

                <div className="space-y-2">
                  <div className="bg-slate-950 p-2.5 rounded-xl border border-slate-800 flex items-center justify-between">
                    <div>
                      <div className="font-bold text-xs text-slate-200">TSMC (Hsinchu)</div>
                      <div className="text-[10px] text-slate-400 font-mono">Obleas 3nm SoC & FCBGA</div>
                    </div>
                    <div className="text-right font-mono">
                      <div className="text-xs font-black text-cyan-400">$107.5M</div>
                      <div className="text-[10px] text-slate-500">33.5% del total</div>
                    </div>
                  </div>

                  <div className="bg-slate-950 p-2.5 rounded-xl border border-slate-800 flex items-center justify-between">
                    <div>
                      <div className="font-bold text-xs text-slate-200">ASE Technology (Kaohsiung)</div>
                      <div className="text-[10px] text-slate-400 font-mono">Empaquetado HBM3e</div>
                    </div>
                    <div className="text-right font-mono">
                      <div className="text-xs font-black text-indigo-400">$85.5M</div>
                      <div className="text-[10px] text-slate-500">26.7% del total</div>
                    </div>
                  </div>

                  <div className="bg-slate-950 p-2.5 rounded-xl border border-slate-800 flex items-center justify-between">
                    <div>
                      <div className="font-bold text-xs text-slate-200">Foxconn (Taipei)</div>
                      <div className="text-[10px] text-slate-400 font-mono">Chasis Óptico y Sensores</div>
                    </div>
                    <div className="text-right font-mono">
                      <div className="text-xs font-black text-blue-400">$68.0M</div>
                      <div className="text-[10px] text-slate-500">21.2% del total</div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Connecting Channel Arrow */}
              <div className="lg:col-span-1 flex items-center justify-center py-2 lg:py-0">
                <div className="flex lg:flex-col items-center gap-1 text-emerald-400 animate-pulse">
                  <ArrowRight className="h-6 w-6 rotate-90 lg:rotate-0" />
                </div>
              </div>

              {/* Destination Node: Mitigated Allocation */}
              <div className="lg:col-span-3 bg-gradient-to-br from-emerald-950/80 to-slate-900 p-5 rounded-2xl border-2 border-emerald-500/60 shadow-lg space-y-2.5">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-mono font-bold text-emerald-300 flex items-center gap-1.5">
                    <ShieldCheck className="h-4 w-4 text-emerald-400" />
                    Destino & Desvío
                  </span>
                  <span className="text-[10px] font-mono bg-emerald-900 text-emerald-200 px-2 py-0.5 rounded font-bold">
                    ACTIVO
                  </span>
                </div>
                <div className="text-xl font-mono font-black text-slate-100">
                  Austin Assembly (TX)
                </div>
                <p className="text-xs text-slate-300 leading-snug">
                  Volumen asegurado: <strong>${divertedNotional}M USD</strong> vía plantas secundarias en Austin y Singapur.
                </p>
                <div className="pt-2 border-t border-emerald-900/60 flex justify-between text-[11px] font-mono">
                  <span className="text-slate-400">Retraso final:</span>
                  <span className="text-emerald-300 font-black">+{mitigatedDelayDays} días (Ahorro: {65 - mitigatedDelayDays}d)</span>
                </div>
              </div>
            </div>

            {/* Interactive Control: Dynamic Diversion Slider */}
            <div className="bg-slate-900/90 rounded-2xl p-5 border border-slate-800 space-y-4">
              <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2">
                <div className="flex items-center gap-2 text-xs sm:text-sm font-mono font-bold text-slate-200">
                  <Sliders className="h-4 w-4 text-cyan-400" />
                  <span>Simulador de Desvío a Plantas Secundarias (Austin, Dresden, Singapur):</span>
                </div>
                <span className="text-xs font-mono font-black text-cyan-300 bg-cyan-950 px-3 py-1 rounded-lg border border-cyan-800">
                  {divertPct}% Re-Asignado (${divertedNotional}M USD)
                </span>
              </div>

              <input
                type="range"
                min={0}
                max={70}
                step={5}
                value={divertPct}
                onChange={(e) => setDivertPct(Number(e.target.value))}
                className="w-full accent-cyan-400 h-2 bg-slate-800 rounded-lg cursor-pointer"
              />

              <div className="flex items-center justify-between text-xs font-mono text-slate-400">
                <span>0% (Todo en Kaohsiung &bull; +65 días retraso)</span>
                <span>35% (Óptimo de Capacidad Alterna)</span>
                <span>70% (Desvío Máximo de Emergencia)</span>
              </div>

              <div className="flex flex-col sm:flex-row items-center justify-between gap-3 pt-2 border-t border-slate-800">
                <div className="text-xs text-slate-300">
                  Volumen en riesgo remanente: <strong className="text-rose-400 font-mono">${delayedNotional}M USD</strong> &bull; Capacidad reasignada: <strong className="text-emerald-400 font-mono">${divertedNotional}M USD</strong>
                </div>

                <button
                  type="button"
                  onClick={() => setAppliedAlternative(true)}
                  className={`px-5 py-2.5 rounded-xl font-mono text-xs font-black flex items-center gap-2 transition-all cursor-pointer ${
                    appliedAlternative
                      ? 'bg-slate-800 text-emerald-400 border border-emerald-600 cursor-default'
                      : 'bg-gradient-to-r from-blue-500 to-cyan-500 hover:from-blue-400 hover:to-cyan-400 text-slate-950 shadow-lg shadow-cyan-500/20'
                  }`}
                >
                  {appliedAlternative ? (
                    <>
                      <CheckCircle2 className="h-4 w-4 text-emerald-400" />
                      <span>Ruta de Desvío Aplicada ({divertPct}%)</span>
                    </>
                  ) : (
                    <>
                      <RotateCcw className="h-4 w-4" />
                      <span>Aplicar Desvío Logístico</span>
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Raw BigQuery Data Table Tab */}
      {activeTab === 'table' && tableData && (
        <div className="bg-slate-950/90 rounded-2xl border-2 border-blue-500/40 overflow-hidden shadow-2xl">
          <div className="bg-gradient-to-r from-slate-900 to-blue-950/60 px-5 py-3.5 flex items-center justify-between border-b border-slate-800">
            <span className="font-bold text-sm text-cyan-300 font-mono uppercase">
              {tableData.title}
            </span>
            <span className="text-xs font-mono bg-blue-950 text-blue-300 px-3 py-1 rounded-lg border border-blue-700 font-bold">
              {tableData.total_rows} Registros en BigQuery
            </span>
          </div>

          <div className="overflow-x-auto max-h-80 overflow-y-auto">
            <table className="w-full text-left border-collapse whitespace-nowrap text-xs sm:text-sm font-mono">
              <thead>
                <tr className="bg-slate-900 text-slate-300 border-b border-slate-800 text-xs font-bold uppercase">
                  {tableData.headers.map((h: string, i: number) => (
                    <th key={i} className="p-3.5 border-r border-slate-800/80">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {tableData.rows.map((row: any, i: number) => (
                  <tr key={i} className={i % 2 === 0 ? 'bg-slate-950/60' : 'bg-slate-900/60'}>
                    {Object.values(row).map((val: any, cIdx: number) => (
                      <td key={cIdx} className="p-3.5 text-slate-200 border-r border-slate-800/60">
                        {typeof val === 'number' ? `$${val.toLocaleString()}` : String(val)}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
