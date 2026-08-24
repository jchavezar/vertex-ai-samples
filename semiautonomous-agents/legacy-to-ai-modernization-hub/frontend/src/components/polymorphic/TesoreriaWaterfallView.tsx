import React, { useState } from 'react';
import {
  DollarSign,
  ShieldCheck,
  TrendingDown,
  Zap,
  CheckCircle2,
  ArrowRight,
} from 'lucide-react';
import { GroundedTableData, HedgingAction } from '../../types';

interface TesoreriaWaterfallViewProps {
  tableData?: GroundedTableData;
  onExecuteHedge?: (hedge: HedgingAction) => void;
}

export const TesoreriaWaterfallView: React.FC<TesoreriaWaterfallViewProps> = ({
  tableData,
  onExecuteHedge,
}) => {
  const [activeTab, setActiveTab] = useState<'waterfall' | 'table'>('waterfall');
  const [hedgeExecuted, setHedgeExecuted] = useState(false);

  const handleAuthorizeHedge = () => {
    setHedgeExecuted(true);
    if (onExecuteHedge) {
      onExecuteHedge({
        action: 'Execute $63M Receiver Swaption Collar',
        hedged_risk: 'Neutraliza el 74% del Slippage USD/TWD',
        cost_basis_k: 450,
        projected_savings_m: 3.4,
        urgency: 'CRITICAL',
      });
    }
  };

  return (
    <div className="space-y-6 animate-zoom-entrance">
      {/* Top Banner: Domain-Specific Heading & View Switcher */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 bg-gradient-to-r from-purple-950/90 via-slate-900 to-indigo-950/90 p-5 rounded-2xl border-2 border-purple-500/50 shadow-xl">
        <div className="flex items-center gap-3.5">
          <div className="h-12 w-12 rounded-xl bg-purple-500/20 border-2 border-purple-400 flex items-center justify-center shadow-lg shadow-purple-500/30">
            <DollarSign className="h-6 w-6 text-purple-300 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-base sm:text-lg font-black text-slate-100 font-sans tracking-wide">
                GRÁFICO WATERFALL DE P&L & BLINDAJE CON DERIVADOS FX
              </h3>
              <span className="text-[10px] font-mono px-2.5 py-0.5 rounded-full bg-purple-900 text-purple-200 border border-purple-600 font-bold">
                BIGQUERY LIVE
              </span>
            </div>
            <p className="text-xs sm:text-sm text-slate-300">
              Análisis de pérdida cambiaria por $3.85M en forwards USD/TWD y recuperación de $3.40M vía Swaption Collar.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 bg-slate-950/90 p-1.5 rounded-xl border border-slate-800 self-stretch sm:self-auto justify-center">
          <button
            type="button"
            onClick={() => setActiveTab('waterfall')}
            className={`px-4 py-2 rounded-lg font-mono text-xs font-bold transition-all cursor-pointer ${
              activeTab === 'waterfall'
                ? 'bg-purple-600 text-white shadow-md shadow-purple-600/30'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Cascada Financiera (Waterfall)
          </button>
          <button
            type="button"
            onClick={() => setActiveTab('table')}
            className={`px-4 py-2 rounded-lg font-mono text-xs font-bold transition-all cursor-pointer ${
              activeTab === 'table'
                ? 'bg-purple-600 text-white shadow-md shadow-purple-600/30'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Tabla de Forwards BigQuery ({tableData?.total_rows || 24})
          </button>
        </div>
      </div>

      {/* Interactive Visual Metaphor: Financial Waterfall Chart */}
      {activeTab === 'waterfall' && (
        <div className="space-y-6">
          <div className="bg-slate-950/90 rounded-3xl p-6 sm:p-8 border-2 border-purple-500/40 shadow-2xl space-y-6 relative overflow-hidden">
            <div className="flex items-center justify-between border-b border-slate-800 pb-4">
              <span className="text-xs sm:text-sm font-mono font-bold text-purple-300 uppercase tracking-wider flex items-center gap-2">
                <TrendingDown className="h-4 w-4 text-rose-400" />
                Puente de Transmisión de Pérdida Cambiaria & Cobertura
              </span>
              <span className="text-xs font-mono text-slate-400">
                Ahorro Neto Estimado: <strong className="text-emerald-400 font-bold">+$3.40M USD (ROI 7.5x)</strong>
              </span>
            </div>

            {/* Financial Waterfall Steps Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3.5">
              {/* Step 1: Notional Exposed */}
              <div className="bg-slate-900/90 p-4 rounded-2xl border-2 border-slate-700 space-y-2 flex flex-col justify-between">
                <div>
                  <span className="text-[11px] font-mono text-slate-400 font-bold block">1. Exposición Base</span>
                  <div className="text-xl font-mono font-black text-slate-100">$14.20M</div>
                  <p className="text-xs text-slate-400 mt-1">2 contratos forwards USD/TWD descubiertos en Q3.</p>
                </div>
                <div className="h-2 w-full bg-slate-800 rounded-full overflow-hidden">
                  <div className="h-full bg-slate-400 w-full" />
                </div>
              </div>

              {/* Step 2: FX Slippage Devaluation */}
              <div className="bg-slate-900/90 p-4 rounded-2xl border-2 border-rose-500/50 space-y-2 flex flex-col justify-between">
                <div>
                  <span className="text-[11px] font-mono text-rose-300 font-bold block">2. Devaluación TWD (+12%)</span>
                  <div className="text-xl font-mono font-black text-rose-400">-$3.85M</div>
                  <p className="text-xs text-slate-400 mt-1">Pérdida por deslizamiento cambiario en DBS y Standard Chartered.</p>
                </div>
                <div className="h-2 w-full bg-slate-800 rounded-full overflow-hidden">
                  <div className="h-full bg-rose-500 w-[70%]" />
                </div>
              </div>

              {/* Step 3: Swaption Collar Cost */}
              <div className="bg-slate-900/90 p-4 rounded-2xl border-2 border-amber-500/50 space-y-2 flex flex-col justify-between">
                <div>
                  <span className="text-[11px] font-mono text-amber-300 font-bold block">3. Prima de Cobertura</span>
                  <div className="text-xl font-mono font-black text-amber-400">-$0.45M</div>
                  <p className="text-xs text-slate-400 mt-1">Costo de estructura Receiver Swaption Collar ($63M).</p>
                </div>
                <div className="h-2 w-full bg-slate-800 rounded-full overflow-hidden">
                  <div className="h-full bg-amber-500 w-[15%]" />
                </div>
              </div>

              {/* Step 4: Protected Recovery */}
              <div className="bg-slate-900/90 p-4 rounded-2xl border-2 border-emerald-500/50 space-y-2 flex flex-col justify-between">
                <div>
                  <span className="text-[11px] font-mono text-emerald-300 font-bold block">4. Recuperación Cobertura</span>
                  <div className="text-xl font-mono font-black text-emerald-400">+$3.40M</div>
                  <p className="text-xs text-slate-400 mt-1">74% de la pérdida neutralizada por el strike de piso.</p>
                </div>
                <div className="h-2 w-full bg-slate-800 rounded-full overflow-hidden">
                  <div className="h-full bg-emerald-500 w-[88%]" />
                </div>
              </div>

              {/* Step 5: Net Final Position */}
              <div className={`p-4 rounded-2xl border-2 transition-all space-y-2 flex flex-col justify-between ${
                hedgeExecuted
                  ? 'bg-emerald-950/80 border-emerald-400 shadow-xl shadow-emerald-950/50'
                  : 'bg-slate-900/90 border-purple-500/60'
              }`}>
                <div>
                  <span className="text-[11px] font-mono text-cyan-300 font-bold block">5. Impacto Neto Final</span>
                  <div className="text-xl font-mono font-black text-slate-100">
                    {hedgeExecuted ? '-$0.45M' : '-$3.85M'}
                  </div>
                  <p className="text-xs text-slate-300 mt-1">
                    {hedgeExecuted ? 'Portafolio 100% blindado contra colapso de TWD.' : 'Exposición no cubierta activa.'}
                  </p>
                </div>
                <div className="h-2 w-full bg-slate-800 rounded-full overflow-hidden">
                  <div className={`h-full ${hedgeExecuted ? 'bg-emerald-400 w-full' : 'bg-rose-500 w-[30%]'}`} />
                </div>
              </div>
            </div>

            {/* Derivative Structure Breakdown & 1-Click Authorization */}
            <div className="bg-gradient-to-r from-purple-950/80 via-slate-900 to-indigo-950/80 rounded-2xl p-6 border-2 border-purple-500/50 space-y-4">
              <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <ShieldCheck className="h-5 w-5 text-emerald-400" />
                    <span className="font-extrabold text-sm sm:text-base text-slate-100 font-mono uppercase">
                      Estructura Recomendada: Receiver Swaption Collar ($63.0M Notional)
                    </span>
                  </div>
                  <p className="text-xs sm:text-sm text-slate-300">
                    Fija piso de protección en 31.80 USD/TWD y financia el costo con venta de call out-of-the-money en 33.50 USD/TWD.
                  </p>
                </div>

                <button
                  type="button"
                  disabled={hedgeExecuted}
                  onClick={handleAuthorizeHedge}
                  className={`px-6 py-3.5 rounded-xl font-mono text-xs sm:text-sm font-black flex items-center gap-2 transition-all cursor-pointer shrink-0 ${
                    hedgeExecuted
                      ? 'bg-slate-800 text-emerald-400 border border-emerald-600 cursor-default'
                      : 'bg-gradient-to-r from-purple-500 to-indigo-500 hover:from-purple-400 hover:to-indigo-400 text-slate-950 shadow-xl shadow-purple-500/30'
                  }`}
                >
                  {hedgeExecuted ? (
                    <>
                      <CheckCircle2 className="h-4 w-4 text-emerald-400" />
                      <span>Swaption Collar Ejecutado</span>
                    </>
                  ) : (
                    <>
                      <Zap className="h-4 w-4" />
                      <span>Autorizar Cobertura ($63M)</span>
                      <ArrowRight className="h-4 w-4" />
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
        <div className="bg-slate-950/90 rounded-2xl border-2 border-purple-500/40 overflow-hidden shadow-2xl">
          <div className="bg-gradient-to-r from-slate-900 to-purple-950/60 px-5 py-3.5 flex items-center justify-between border-b border-slate-800">
            <span className="font-bold text-sm text-purple-300 font-mono uppercase">
              {tableData.title}
            </span>
            <span className="text-xs font-mono bg-purple-950 text-purple-300 px-3 py-1 rounded-lg border border-purple-700 font-bold">
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
