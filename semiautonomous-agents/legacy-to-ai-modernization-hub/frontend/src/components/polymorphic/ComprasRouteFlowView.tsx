import React, { useState } from 'react';
import {
  Truck,
  ArrowRight,
  AlertTriangle,
  RotateCcw,
  Sliders,
  CheckCircle2,
  Train,
  Anchor,
} from 'lucide-react';
import { GroundedTableData } from '../../types';

interface ComprasRouteFlowViewProps {
  tableData?: GroundedTableData;
}

export const ComprasRouteFlowView: React.FC<ComprasRouteFlowViewProps> = ({
  tableData,
}) => {
  const [divertPct, setDivertPct] = useState(40);
  const [activeTab, setActiveTab] = useState<'flow' | 'table'>('flow');
  const [appliedAlternative, setAppliedAlternative] = useState(false);

  // Total TEUs = 1,420
  const totalTeus = 1420;
  const divertedTeus = Math.round(totalTeus * (divertPct / 100));
  const delayedTeus = totalTeus - divertedTeus;
  const originalDelayDays = 18;
  const mitigatedDelayDays = Math.max(5, Math.round(originalDelayDays * (1 - divertPct / 130)));
  const savedCostMillions = Number(((divertedTeus / totalTeus) * 4.85 * 0.75).toFixed(2));

  return (
    <div className="space-y-6 animate-zoom-entrance">
      {/* Top Banner: Domain-Specific Heading & View Switcher */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 bg-gradient-to-r from-blue-950/90 via-slate-900 to-indigo-950/90 p-5 rounded-2xl border-2 border-blue-500/50 shadow-xl">
        <div className="flex items-center gap-3.5">
          <div className="h-12 w-12 rounded-xl bg-blue-500/20 border-2 border-blue-400 flex items-center justify-center shadow-lg shadow-blue-500/30">
            <Anchor className="h-6 w-6 text-blue-300 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-base sm:text-lg font-black text-slate-100 font-sans tracking-wide">
                RED DE TERMINALES PORTUARIAS & DESVÍO INTERMODAL (CICE / MANZANILLO)
              </h3>
              <span className="text-[10px] font-mono px-2.5 py-0.5 rounded-full bg-blue-900 text-blue-200 border border-blue-600 font-bold">
                BIGQUERY LIVE
              </span>
            </div>
            <p className="text-xs sm:text-sm text-slate-300">
              Mapeo de 1,420 TEUs demorados en puertos mexicanos y activación del corredor ferroviario con Ferromex a Monterrey.
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
            Diagrama Intermodal y Rutas
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
            Tabla de Terminales BigQuery ({tableData?.total_rows || 142})
          </button>
        </div>
      </div>

      {/* Interactive Visual Metaphor: Supply Chain Route & Node Network */}
      {activeTab === 'flow' && (
        <div className="space-y-6">
          <div className="bg-slate-950/90 rounded-3xl p-6 sm:p-8 border-2 border-blue-500/40 shadow-2xl space-y-6 relative overflow-hidden">
            <div className="flex items-center justify-between border-b border-slate-800 pb-4">
              <span className="text-xs sm:text-sm font-mono font-bold text-blue-300 uppercase tracking-wider flex items-center gap-2">
                <Truck className="h-4 w-4" />
                Corredor Logístico: Terminales Veracruz & Manzanillo &rarr; Hub Intermodal Monterrey
              </span>
              <span className="text-xs font-mono text-slate-400">
                Retraso Mitigado: <strong className="text-emerald-400 font-bold">{mitigatedDelayDays} Días</strong> (vs 18 días base)
              </span>
            </div>

            {/* Topographic Visual Nodes Flow */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 items-center">
              {/* Origin Node: Maritime Port Terminals */}
              <div className="lg:col-span-3 bg-gradient-to-br from-rose-950/80 to-slate-900 p-5 rounded-2xl border-2 border-rose-500/60 shadow-lg space-y-2.5">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-mono font-bold text-rose-300 flex items-center gap-1.5">
                    <AlertTriangle className="h-4 w-4 text-rose-400" />
                    Puertos de Entrada
                  </span>
                  <span className="text-[10px] font-mono bg-rose-900 text-rose-200 px-2 py-0.5 rounded font-bold">
                    CONGESTIÓN
                  </span>
                </div>
                <div className="text-lg sm:text-xl font-mono font-black text-slate-100">
                  Veracruz & Manzanillo
                </div>
                <p className="text-xs text-slate-300 leading-snug">
                  <strong>1,420 TEUs varados</strong> en muelles. Retrasos de 16 a 22 días por saturación de atraque y aforo aduanal.
                </p>
                <div className="pt-2 border-t border-rose-900/60 flex justify-between text-[11px] font-mono">
                  <span className="text-slate-400">Sobrecosto estadías:</span>
                  <span className="text-rose-300 font-bold">$4.85M USD</span>
                </div>
              </div>

              {/* Connecting Channel Arrow */}
              <div className="lg:col-span-1 flex items-center justify-center py-2 lg:py-0">
                <div className="flex lg:flex-col items-center gap-1 text-cyan-400 animate-pulse">
                  <ArrowRight className="h-6 w-6 rotate-90 lg:rotate-0" />
                </div>
              </div>

              {/* Middle Terminals Breakdown */}
              <div className="lg:col-span-4 bg-slate-900/90 p-5 rounded-2xl border-2 border-slate-700 shadow-lg space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-mono font-bold text-cyan-300">
                    Terminales Portuarias Expuestas
                  </span>
                  <span className="text-xs font-mono text-slate-400">3 Operadores</span>
                </div>

                <div className="space-y-2">
                  <div className="bg-slate-950 p-2.5 rounded-xl border border-slate-800 flex items-center justify-between">
                    <div>
                      <div className="font-bold text-xs text-slate-200">Grupo CICE (Veracruz)</div>
                      <div className="text-[10px] text-slate-400 font-mono">Bahía Norte &bull; Carga Contenerizada</div>
                    </div>
                    <div className="text-right font-mono">
                      <div className="text-xs font-black text-cyan-400">840 TEUs</div>
                      <div className="text-[10px] text-rose-400 font-bold">+14 Días Retraso</div>
                    </div>
                  </div>

                  <div className="bg-slate-950 p-2.5 rounded-xl border border-slate-800 flex items-center justify-between">
                    <div>
                      <div className="font-bold text-xs text-slate-200">Contecon (Manzanillo)</div>
                      <div className="text-[10px] text-slate-400 font-mono">Cuenca Pacífico &bull; Farma e Insumos</div>
                    </div>
                    <div className="text-right font-mono">
                      <div className="text-xs font-black text-indigo-400">580 TEUs</div>
                      <div className="text-[10px] text-rose-400 font-bold">+18 Días Retraso</div>
                    </div>
                  </div>

                  <div className="bg-slate-950 p-2.5 rounded-xl border border-slate-800 flex items-center justify-between">
                    <div>
                      <div className="font-bold text-xs text-slate-200">Promologistics (Cedis Central)</div>
                      <div className="text-[10px] text-slate-400 font-mono">Hub Cross-Docking CDMX</div>
                    </div>
                    <div className="text-right font-mono">
                      <div className="text-xs font-black text-emerald-400">310 TEUs</div>
                      <div className="text-[10px] text-emerald-400 font-bold">Operación Activa</div>
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

              {/* Destination Node: Rail Intermodal Corridor */}
              <div className="lg:col-span-3 bg-gradient-to-br from-emerald-950/80 to-slate-900 p-5 rounded-2xl border-2 border-emerald-500/60 shadow-lg space-y-2.5">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-mono font-bold text-emerald-300 flex items-center gap-1.5">
                    <Train className="h-4 w-4 text-emerald-400" />
                    Corredor Ferroviario
                  </span>
                  <span className="text-[10px] font-mono bg-emerald-900 text-emerald-200 px-2 py-0.5 rounded font-bold">
                    FERROMEX / KCSM
                  </span>
                </div>
                <div className="text-lg sm:text-xl font-mono font-black text-slate-100">
                  Hub Monterrey (Senda)
                </div>
                <p className="text-xs text-slate-300 leading-snug">
                  Capacidad de desvío ferroviario: <strong>{divertedTeus} TEUs</strong> trasladados directamente a Monterrey.
                </p>
                <div className="pt-2 border-t border-emerald-900/60 flex justify-between text-[11px] font-mono">
                  <span className="text-slate-400">Ahorro en sobrecostos:</span>
                  <span className="text-emerald-300 font-black">+${savedCostMillions}M USD</span>
                </div>
              </div>
            </div>

            {/* Interactive Control: Dynamic Diversion Slider */}
            <div className="bg-slate-900/90 rounded-2xl p-5 border border-slate-800 space-y-4">
              <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2">
                <div className="flex items-center gap-2 text-xs sm:text-sm font-mono font-bold text-slate-200">
                  <Sliders className="h-4 w-4 text-cyan-400" />
                  <span>Simulador de Desvío Intermodal a Ferrocarril (Ferromex / Grupo Senda):</span>
                </div>
                <span className="text-xs font-mono font-black text-cyan-300 bg-cyan-950 px-3 py-1 rounded-lg border border-cyan-800">
                  {divertPct}% Desviado por Tren ({divertedTeus} TEUs)
                </span>
              </div>

              <input
                type="range"
                min={0}
                max={75}
                step={5}
                value={divertPct}
                onChange={(e) => setDivertPct(Number(e.target.value))}
                className="w-full accent-cyan-400 h-2 bg-slate-800 rounded-lg cursor-pointer"
              />

              <div className="flex items-center justify-between text-xs font-mono text-slate-400">
                <span>0% (Todo en Carretera &bull; +18 días retraso)</span>
                <span>40% (Capacidad Ferroviaria Óptima Ferromex)</span>
                <span>75% (Desvío Máximo Intermodal a Monterrey)</span>
              </div>

              <div className="flex flex-col sm:flex-row items-center justify-between gap-3 pt-2 border-t border-slate-800">
                <div className="text-xs text-slate-300">
                  TEUs en riesgo remanente en puerto: <strong className="text-rose-400 font-mono">{delayedTeus} TEUs</strong> &bull; TEUs desfogados por tren: <strong className="text-emerald-400 font-mono">{divertedTeus} TEUs</strong>
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
                      <span>Desvío Ferroviario Aplicado ({divertPct}%)</span>
                    </>
                  ) : (
                    <>
                      <RotateCcw className="h-4 w-4" />
                      <span>Autorizar Desvío Intermodal</span>
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
