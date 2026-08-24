import React, { useState } from 'react';
import {
  Factory,
  Plane,
  Flame,
  Calendar,
  Sliders,
} from 'lucide-react';
import { GroundedTableData } from '../../types';

interface AlmacenCountdownTimelineViewProps {
  tableData?: GroundedTableData;
}

export const AlmacenCountdownTimelineView: React.FC<AlmacenCountdownTimelineViewProps> = ({
  tableData,
}) => {
  const [burnRate, setBurnRate] = useState(800);
  const [enableAirbridge, setEnableAirbridge] = useState(false);
  const [activeTab, setActiveTab] = useState<'timeline' | 'table'>('timeline');

  // Baseline 34 days at 800 units/day = 27,200 units total stock
  const totalStockUnits = 27200;
  const airbridgeExtraUnits = enableAirbridge ? 9600 : 0; // +12 days at 800u/d
  const effectiveStock = totalStockUnits + airbridgeExtraUnits;
  const calculatedDaysRemaining = Math.round(effectiveStock / burnRate);

  // Projected stoppage date calculation
  const today = new Date();
  const stoppageDate = new Date(today.getTime() + calculatedDaysRemaining * 24 * 60 * 60 * 1000);
  const dateFormatted = stoppageDate.toLocaleDateString('es-ES', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  });

  return (
    <div className="space-y-6 animate-zoom-entrance">
      {/* Top Banner: Domain-Specific Heading & View Switcher */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 bg-gradient-to-r from-amber-950/90 via-slate-900 to-rose-950/90 p-5 rounded-2xl border-2 border-amber-500/50 shadow-xl">
        <div className="flex items-center gap-3.5">
          <div className="h-12 w-12 rounded-xl bg-amber-500/20 border-2 border-amber-400 flex items-center justify-center shadow-lg shadow-amber-500/30">
            <Factory className="h-6 w-6 text-amber-300 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-base sm:text-lg font-black text-slate-100 font-sans tracking-wide">
                LÍNEA DE TIEMPO GANTT & CUENTA REGRESIVA DE PARO DE PLANTA
              </h3>
              <span className="text-[10px] font-mono px-2.5 py-0.5 rounded-full bg-amber-900 text-amber-200 border border-amber-600 font-bold">
                BIGQUERY LIVE
              </span>
            </div>
            <p className="text-xs sm:text-sm text-slate-300">
              Análisis de inventario disponible para obleas 3nm y sustratos FCBGA en Austin, Monterrey y Frankfurt.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 bg-slate-950/90 p-1.5 rounded-xl border border-slate-800 self-stretch sm:self-auto justify-center">
          <button
            type="button"
            onClick={() => setActiveTab('timeline')}
            className={`px-4 py-2 rounded-lg font-mono text-xs font-bold transition-all cursor-pointer ${
              activeTab === 'timeline'
                ? 'bg-amber-600 text-white shadow-md shadow-amber-600/30'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Línea de Tiempo & Gantt
          </button>
          <button
            type="button"
            onClick={() => setActiveTab('table')}
            className={`px-4 py-2 rounded-lg font-mono text-xs font-bold transition-all cursor-pointer ${
              activeTab === 'table'
                ? 'bg-amber-600 text-white shadow-md shadow-amber-600/30'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Tabla de Stock BigQuery ({tableData?.total_rows || 81})
          </button>
        </div>
      </div>

      {/* Interactive Visual Metaphor: Countdown & Gantt Burn-Down Bar */}
      {activeTab === 'timeline' && (
        <div className="space-y-6">
          <div className="bg-slate-950/90 rounded-3xl p-6 sm:p-8 border-2 border-amber-500/40 shadow-2xl space-y-6 relative overflow-hidden">
            {/* Header Status & Countdown Date */}
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 border-b border-slate-800 pb-4">
              <div className="space-y-1">
                <span className="text-xs sm:text-sm font-mono font-bold text-amber-300 uppercase tracking-wider flex items-center gap-2">
                  <Flame className="h-4 w-4 text-rose-400" />
                  Horizonte Crítico de Agotamiento de Stock
                </span>
                <div className="text-2xl sm:text-3xl font-mono font-black text-slate-100 flex items-center gap-3">
                  <span>{calculatedDaysRemaining} Días Restantes</span>
                  <span className={`text-xs font-mono px-3 py-1 rounded-full font-bold uppercase ${
                    calculatedDaysRemaining <= 34 ? 'bg-rose-950 text-rose-300 border border-rose-700' : 'bg-emerald-950 text-emerald-300 border border-emerald-700'
                  }`}>
                    {calculatedDaysRemaining <= 34 ? 'PARO INMINENTE' : 'OPERACIÓN EXTENDIDA'}
                  </span>
                </div>
              </div>

              <div className="text-left sm:text-right bg-slate-900/80 p-3 rounded-xl border border-slate-800 font-mono">
                <div className="text-xs text-slate-400">Fecha Estimada de Paro:</div>
                <div className="text-sm sm:text-base font-black text-rose-400 flex items-center gap-1.5 justify-end">
                  <Calendar className="h-4 w-4" />
                  <span>{dateFormatted}</span>
                </div>
              </div>
            </div>

            {/* Visual Timeline Gantt Bar */}
            <div className="space-y-2 pt-2">
              <div className="flex justify-between text-xs font-mono text-slate-300">
                <span>Hoy (Día 0)</span>
                <span>Buffer Actual ({calculatedDaysRemaining} Días)</span>
                <span className="text-rose-400 font-bold">Límite Meta (90 Días)</span>
              </div>

              {/* Progress Track */}
              <div className="h-6 w-full bg-slate-900 rounded-2xl overflow-hidden p-1 border border-slate-800 flex relative">
                <div
                  className={`h-full rounded-xl transition-all duration-500 flex items-center justify-end pr-2 text-[10px] font-mono font-black text-slate-950 ${
                    calculatedDaysRemaining <= 34
                      ? 'bg-gradient-to-r from-rose-500 via-amber-400 to-rose-500 shadow-lg shadow-rose-500/30'
                      : 'bg-gradient-to-r from-emerald-500 via-teal-400 to-cyan-400 shadow-lg shadow-emerald-500/30'
                  }`}
                  style={{ width: `${Math.min(100, Math.max(15, (calculatedDaysRemaining / 90) * 100))}%` }}
                >
                  {calculatedDaysRemaining} DÍAS
                </div>
                {/* 90 Days Target Marker */}
                <div className="absolute right-0 top-0 bottom-0 w-1 bg-rose-500/60" />
              </div>
            </div>

            {/* Warehouse Facilities Status Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-2">
              {/* Austin Central */}
              <div className="bg-slate-900/90 p-4 rounded-2xl border-2 border-rose-500/40 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-xs text-slate-100">Austin Central (TX)</span>
                  <span className="text-xs font-mono text-rose-400 font-bold">18 Días Buffer</span>
                </div>
                <p className="text-xs text-slate-300">Línea de ensamble principal. Consumo nominal: 500 u/día. Agotamiento proyectado el 30 de Junio.</p>
                <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
                  <div className="h-full bg-rose-500 w-[20%]" />
                </div>
              </div>

              {/* Monterrey Hub */}
              <div className="bg-slate-900/90 p-4 rounded-2xl border-2 border-amber-500/40 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-xs text-slate-100">Monterrey Hub (MX)</span>
                  <span className="text-xs font-mono text-amber-400 font-bold">16 Días Buffer</span>
                </div>
                <p className="text-xs text-slate-300">Ensamblaje de tarjetas y periféricos. Consumo: 300 u/día. Agotamiento proyectado el 28 de Junio.</p>
                <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
                  <div className="h-full bg-amber-500 w-[18%]" />
                </div>
              </div>

              {/* Frankfurt Airbridge */}
              <div className={`p-4 rounded-2xl border-2 transition-all space-y-2 ${
                enableAirbridge
                  ? 'bg-emerald-950/70 border-emerald-500/80 shadow-lg shadow-emerald-950/40'
                  : 'bg-slate-900/90 border-slate-800'
              }`}>
                <div className="flex items-center justify-between">
                  <span className="font-bold text-xs text-slate-100 flex items-center gap-1.5">
                    <Plane className="h-3.5 w-3.5 text-cyan-400" />
                    Frankfurt Logistics (DE)
                  </span>
                  <span className="text-xs font-mono text-emerald-400 font-bold">+12 Días Extra</span>
                </div>
                <p className="text-xs text-slate-300">
                  Stock disponible: 9,600 unidades para reasignación aérea hacia Austin y Monterrey.
                </p>
                <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
                  <div className={`h-full ${enableAirbridge ? 'bg-emerald-400 w-full' : 'bg-slate-700 w-0'}`} />
                </div>
              </div>
            </div>

            {/* Interactive What-If Controls for Plant Operations */}
            <div className="bg-slate-900/90 rounded-2xl p-5 border border-slate-800 space-y-4">
              <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
                <div className="flex items-center gap-2 text-xs sm:text-sm font-mono font-bold text-slate-200">
                  <Sliders className="h-4 w-4 text-amber-400" />
                  <span>Simulador de Tasa de Consumo de Ensamble:</span>
                </div>
                <span className="text-xs font-mono font-black text-amber-300 bg-amber-950 px-3 py-1 rounded-lg border border-amber-800">
                  {burnRate} Unidades / Día
                </span>
              </div>

              <input
                type="range"
                min={400}
                max={1000}
                step={50}
                value={burnRate}
                onChange={(e) => setBurnRate(Number(e.target.value))}
                className="w-full accent-amber-400 h-2 bg-slate-800 rounded-lg cursor-pointer"
              />

              <div className="flex items-center justify-between text-xs font-mono text-slate-400">
                <span>400 U/D (Turno Mínimo Reducido)</span>
                <span>800 U/D (Operación Nominal 100%)</span>
                <span>1,000 U/D (Alta Demanda Pico)</span>
              </div>

              {/* Action Buttons: Toggle Airbridge & Executive Resolution */}
              <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-3 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setEnableAirbridge(!enableAirbridge)}
                  className={`px-5 py-2.5 rounded-xl font-mono text-xs font-black flex items-center gap-2 transition-all cursor-pointer ${
                    enableAirbridge
                      ? 'bg-emerald-500 text-slate-950 shadow-lg shadow-emerald-500/30'
                      : 'bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700'
                  }`}
                >
                  <Plane className="h-4 w-4" />
                  <span>{enableAirbridge ? 'Puente Aéreo Frankfurt Activado (+12 Días)' : 'Activar Puente Aéreo Frankfurt (+12 Días)'}</span>
                </button>

                <div className="text-xs text-slate-300 font-mono">
                  Impacto: <strong className="text-emerald-400">+{calculatedDaysRemaining - 34} días</strong> ganados sobre la línea base.
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Raw BigQuery Data Table Tab */}
      {activeTab === 'table' && tableData && (
        <div className="bg-slate-950/90 rounded-2xl border-2 border-amber-500/40 overflow-hidden shadow-2xl">
          <div className="bg-gradient-to-r from-slate-900 to-amber-950/60 px-5 py-3.5 flex items-center justify-between border-b border-slate-800">
            <span className="font-bold text-sm text-amber-300 font-mono uppercase">
              {tableData.title}
            </span>
            <span className="text-xs font-mono bg-amber-950 text-amber-300 px-3 py-1 rounded-lg border border-amber-700 font-bold">
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
