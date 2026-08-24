import React, { useState } from 'react';
import {
  Factory,
  Clock,
  CheckCircle2,
  Sparkles,
} from 'lucide-react';
import { GroundedTableData } from '../../types';

interface AlmacenCountdownTimelineViewProps {
  tableData?: GroundedTableData;
}

export const AlmacenCountdownTimelineView: React.FC<AlmacenCountdownTimelineViewProps> = ({
  tableData,
}) => {
  const [burnRate, setBurnRate] = useState(1200); // Lotes/day
  const [enableQueretaroBuffer, setEnableQueretaroBuffer] = useState(false);
  const [activeTab, setActiveTab] = useState<'timeline' | 'table'>('timeline');

  // Baseline units: 25,200 lotes across critical pharma/food lines
  const totalStockUnits = 25200;
  const queretaroBufferUnits = enableQueretaroBuffer ? 16800 : 0;
  const totalAvailableStock = totalStockUnits + queretaroBufferUnits;

  // Days buffer calculation
  const remainingDays = Math.max(1, Math.round(totalAvailableStock / burnRate));
  
  // Calculate projected date
  const now = new Date(2026, 5, 25); // June 25, 2026 baseline
  const projectedShutdownDate = new Date(now.getTime() + remainingDays * 24 * 60 * 60 * 1000);
  const dateOptions: Intl.DateTimeFormatOptions = { day: 'numeric', month: 'long', year: 'numeric' };
  const formattedShutdownDate = projectedShutdownDate.toLocaleDateString('es-MX', dateOptions);

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
                CONTINUIDAD DE MANUFACTURA & BUFFER DE PARO (SILANES / GLORIA)
              </h3>
              <span className="text-[10px] font-mono px-2.5 py-0.5 rounded-full bg-amber-900 text-amber-200 border border-amber-600 font-bold">
                BIGQUERY LIVE
              </span>
            </div>
            <p className="text-xs sm:text-sm text-slate-300">
              Monitoreo de stock de seguridad para principios activos (Silanes) y grasa butírica (Cremería Gloria) ante retrasos portuarios.
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
            Línea de Tiempo & Buffer
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
            Inventario en Planta ({tableData?.total_rows || 88})
          </button>
        </div>
      </div>

      {/* Interactive Visual Metaphor: Countdown & Gantt Timeline */}
      {activeTab === 'timeline' && (
        <div className="bg-slate-950/90 rounded-3xl p-6 sm:p-8 border-2 border-amber-500/40 shadow-2xl space-y-6 relative overflow-hidden">
          {/* Big Prominent Countdown Hero Banner */}
          <div className="grid grid-cols-1 md:grid-cols-12 gap-6 items-center bg-gradient-to-br from-slate-900 to-amber-950/50 p-6 rounded-2xl border-2 border-amber-500/40">
            <div className="md:col-span-4 text-center md:text-left space-y-1">
              <span className="text-xs font-mono font-bold text-amber-300 uppercase tracking-wider flex items-center justify-center md:justify-start gap-1.5">
                <Clock className="h-4 w-4" />
                Cuenta Regresiva de Stock Crítico
              </span>
              <div className="text-4xl sm:text-5xl lg:text-6xl font-mono font-black text-amber-400">
                {remainingDays} <span className="text-2xl text-slate-300 font-sans">Días</span>
              </div>
              <p className="text-xs text-slate-400">
                Hasta agotamiento total de stock sin desvío
              </p>
            </div>

            <div className="md:col-span-8 space-y-3">
              <div className="flex items-center justify-between text-xs font-mono">
                <span className="text-slate-300 font-bold">Fecha Límite Proyectada de Paro de Envasado:</span>
                <span className={`px-3 py-1 rounded-lg font-bold ${
                  remainingDays < 25 ? 'bg-rose-950 text-rose-300 border border-rose-600' : 'bg-emerald-950 text-emerald-300 border border-emerald-600'
                }`}>
                  {formattedShutdownDate}
                </span>
              </div>

              {/* Progress Bar of Buffer Burn */}
              <div className="h-4 bg-slate-900 rounded-full overflow-hidden border border-slate-700 p-0.5 relative">
                <div
                  className={`h-full rounded-full transition-all duration-500 ${
                    remainingDays < 20
                      ? 'bg-gradient-to-r from-rose-600 to-rose-400'
                      : remainingDays < 35
                      ? 'bg-gradient-to-r from-amber-500 to-yellow-400'
                      : 'bg-gradient-to-r from-emerald-500 to-teal-400'
                  }`}
                  style={{ width: `${Math.min(100, (remainingDays / 60) * 100)}%` }}
                />
              </div>

              <div className="flex items-center justify-between text-[11px] font-mono text-slate-400">
                <span>0 Días (Paro Total de Envasado)</span>
                <span>21 Días (Buffer Silanes/Gloria)</span>
                <span>45+ Días (Operación Normal Segura)</span>
              </div>
            </div>
          </div>

          {/* Plantas y Almacenes Breakdown Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Planta 1: Lab Silanes Toluca */}
            <div className="bg-slate-900/90 p-5 rounded-2xl border-2 border-slate-700 space-y-2.5 shadow-md">
              <div className="flex items-center justify-between">
                <span className="font-bold text-xs text-slate-200">Planta Toluca (Lab. Silanes)</span>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-rose-950 text-rose-300 border border-rose-800 font-bold">
                  22 DÍAS BUFFER
                </span>
              </div>
              <div className="text-lg font-mono font-black text-slate-100">
                APIs Farma & Ampolletas
              </div>
              <p className="text-xs text-slate-300 leading-relaxed">
                Insumos para medicamentos metabólicos en contenedor demorado en Manzanillo. Consumo: <strong>600 lotes/día</strong>.
              </p>
              <div className="pt-2 border-t border-slate-800 flex justify-between text-xs font-mono text-slate-400">
                <span>Stock Restante:</span>
                <span className="text-amber-300 font-bold">13,200 Lotes</span>
              </div>
            </div>

            {/* Planta 2: Cremería Gloria GDL */}
            <div className="bg-slate-900/90 p-5 rounded-2xl border-2 border-slate-700 space-y-2.5 shadow-md">
              <div className="flex items-center justify-between">
                <span className="font-bold text-xs text-slate-200">Planta GDL (Cremería Gloria)</span>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-amber-950 text-amber-300 border border-amber-800 font-bold">
                  21 DÍAS BUFFER
                </span>
              </div>
              <div className="text-lg font-mono font-black text-slate-100">
                Grasa Butírica & Empaque
              </div>
              <p className="text-xs text-slate-300 leading-relaxed">
                Línea de envasado de Mantequilla Gloria. Materia prima láctea con cadena de frío garantizada. Consumo: <strong>600 lotes/día</strong>.
              </p>
              <div className="pt-2 border-t border-slate-800 flex justify-between text-xs font-mono text-slate-400">
                <span>Stock Restante:</span>
                <span className="text-amber-300 font-bold">12,000 Lotes</span>
              </div>
            </div>

            {/* Planta 3: Cedis Regulador Querétaro */}
            <div className="bg-slate-900/90 p-5 rounded-2xl border-2 border-emerald-500/60 space-y-2.5 shadow-md">
              <div className="flex items-center justify-between">
                <span className="font-bold text-xs text-emerald-300">Almacén Querétaro</span>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-800 font-bold">
                  STOCK REASIGNABLE
                </span>
              </div>
              <div className="text-lg font-mono font-black text-slate-100">
                +14 Días de Respaldo
              </div>
              <p className="text-xs text-slate-300 leading-relaxed">
                Reserva estratégica de materias primas e insumos secos lista para inyección inmediata a Toluca y Guadalajara.
              </p>
              <div className="pt-2 border-t border-slate-800 flex justify-between text-xs font-mono text-slate-400">
                <span>Capacidad Extra:</span>
                <span className="text-emerald-400 font-bold">+16,800 Lotes</span>
              </div>
            </div>
          </div>

          {/* Interactive Controls: Burn Rate & Queretaro Airbridge Toggle */}
          <div className="bg-slate-900/90 rounded-2xl p-5 border border-slate-800 space-y-4">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Slider: Assembly Burn Rate */}
              <div className="space-y-2">
                <div className="flex items-center justify-between text-xs sm:text-sm font-mono font-bold text-slate-200">
                  <span>Ritmo de Envasado en Plantas:</span>
                  <span className="text-amber-300 bg-amber-950 px-2.5 py-0.5 rounded border border-amber-800">
                    {burnRate} Lotes / Día
                  </span>
                </div>
                <input
                  type="range"
                  min={600}
                  max={1800}
                  step={100}
                  value={burnRate}
                  onChange={(e) => setBurnRate(Number(e.target.value))}
                  className="w-full accent-amber-400 h-2 bg-slate-800 rounded-lg cursor-pointer"
                />
                <div className="flex items-center justify-between text-[11px] font-mono text-slate-400">
                  <span>600 (Ritmo Mínimo de Crisis)</span>
                  <span>1,200 (Nominal)</span>
                  <span>1,800 (Pico Operativo)</span>
                </div>
              </div>

              {/* Action Button: Activate Queretaro Reserve */}
              <div className="flex flex-col justify-between gap-2">
                <span className="text-xs sm:text-sm font-mono font-bold text-slate-200">
                  Plan de Contingencia Inmediato:
                </span>
                <button
                  type="button"
                  onClick={() => setEnableQueretaroBuffer(!enableQueretaroBuffer)}
                  className={`w-full py-3 px-4 rounded-xl font-mono text-xs font-black flex items-center justify-center gap-2.5 transition-all cursor-pointer ${
                    enableQueretaroBuffer
                      ? 'bg-emerald-600 hover:bg-emerald-500 text-white shadow-lg shadow-emerald-600/30'
                      : 'bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-600'
                  }`}
                >
                  {enableQueretaroBuffer ? (
                    <>
                      <CheckCircle2 className="h-4 w-4 text-white" />
                      <span>Stock de Querétaro Activo (+14 Días Buffer Inyectados)</span>
                    </>
                  ) : (
                    <>
                      <Sparkles className="h-4 w-4 text-emerald-400" />
                      <span>Activar Transferencia desde Querétaro (+16,800 Lotes)</span>
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
        <div className="bg-slate-950/90 rounded-2xl border-2 border-amber-500/40 overflow-hidden shadow-2xl">
          <div className="bg-gradient-to-r from-slate-900 to-amber-950/60 px-5 py-3.5 flex items-center justify-between border-b border-slate-800">
            <span className="font-bold text-sm text-amber-300 font-mono uppercase">
              {tableData.title}
            </span>
            <span className="text-xs font-mono bg-amber-950 text-amber-300 px-3 py-1 rounded-lg border border-amber-700 font-bold">
              {tableData.total_rows} Líneas de Inventario en BigQuery
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
