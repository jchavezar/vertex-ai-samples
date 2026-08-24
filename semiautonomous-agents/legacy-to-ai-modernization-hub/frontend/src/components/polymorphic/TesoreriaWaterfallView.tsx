import React, { useState } from 'react';
import {
  DollarSign,
  ArrowDownRight,
  ArrowUpRight,
  Zap,
  CheckCircle2,
  Lock,
  Building2,
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
  const [executed, setExecuted] = useState(false);

  // Financial bridge: $85.0M Compras USD -> -$4.20M Deval USD/MXN -> -$0.60M Prima Forward -> +$3.60M Ahorro Fix -> -$0.60M Neto Final
  const initialExposure = 85.0; // $85.0M USD
  const fxDevaluationLoss = -4.20; // -$4.20M USD
  const forwardPremiumCost = -0.60; // -$0.60M USD
  const forwardHedgeSavings = 3.60; // +$3.60M USD
  const netProtectedImpact = Number((fxDevaluationLoss + forwardPremiumCost + forwardHedgeSavings).toFixed(2)); // -$1.20M USD

  const handleExecute = () => {
    setExecuted(true);
    if (onExecuteHedge) {
      onExecuteHedge({
        action: 'Forward Cambiario USD/MXN Fix @ $19.40 ($60.0M USD)',
        hedged_risk: 'Volatilidad USD/MXN en Compras Retail',
        cost_basis_k: 600,
        projected_savings_m: forwardHedgeSavings,
        urgency: 'INMEDIATA (T+0)',
      });
    }
  };

  return (
    <div className="space-y-6 animate-zoom-entrance">
      {/* Top Banner: Domain-Specific Heading & View Switcher */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 bg-gradient-to-r from-purple-950/90 via-slate-900 to-indigo-950/90 p-5 rounded-2xl border-2 border-purple-500/50 shadow-xl">
        <div className="flex items-center gap-3.5">
          <div className="h-12 w-12 rounded-xl bg-purple-500/20 border-2 border-purple-400 flex items-center justify-center shadow-lg shadow-purple-500/30">
            <Building2 className="h-6 w-6 text-purple-300 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-base sm:text-lg font-black text-slate-100 font-sans tracking-wide">
                RETAIL, TIPO DE CAMBIO & BLINDAJE DE MARGEN EBITDA (BOXITO / MACROPAY)
              </h3>
              <span className="text-[10px] font-mono px-2.5 py-0.5 rounded-full bg-purple-900 text-purple-200 border border-purple-600 font-bold">
                BIGQUERY LIVE
              </span>
            </div>
            <p className="text-xs sm:text-sm text-slate-300">
              Evaluación de $85.0M USD en compras importadas expuestas a USD/MXN $20.80 y contratación de forward a $19.40.
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
            Cascada P&L y Cobertura
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
            Contratos FX BigQuery ({tableData?.total_rows || 24})
          </button>
        </div>
      </div>

      {/* Interactive Visual Metaphor: Financial P&L Waterfall Bridge */}
      {activeTab === 'waterfall' && (
        <div className="bg-slate-950/90 rounded-3xl p-6 sm:p-8 border-2 border-purple-500/40 shadow-2xl space-y-6 relative overflow-hidden">
          <div className="flex items-center justify-between border-b border-slate-800 pb-4">
            <span className="text-xs sm:text-sm font-mono font-bold text-purple-300 uppercase tracking-wider flex items-center gap-2">
              <DollarSign className="h-4 w-4" />
              Puente de P&L: Erosión por Tipo de Cambio USD/MXN vs Blindaje con Contrato Forward
            </span>
            <span className="text-xs font-mono text-slate-400">
              Margen Protegido: <strong className="text-emerald-400 font-bold">85.7% del Riesgo Neutralizado</strong>
            </span>
          </div>

          {/* 5-Column Visual Financial Waterfall Bridge */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3.5 items-stretch">
            {/* Step 1: Base Exposure */}
            <div className="bg-slate-900/90 p-4 rounded-2xl border-2 border-slate-700 flex flex-col justify-between space-y-2 shadow-md">
              <div>
                <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wider block font-bold">
                  1. Compras USD
                </span>
                <div className="text-xl sm:text-2xl font-mono font-black text-slate-100">
                  ${initialExposure}M USD
                </div>
              </div>
              <p className="text-[11px] text-slate-300 leading-snug">
                Volumen importado por Boxito ($28.5M), Macropay ($36.2M) y Cklass ($20.3M).
              </p>
              <div className="text-[10px] font-mono bg-slate-950 px-2 py-1 rounded text-slate-400">
                Línea Base: $18.50
              </div>
            </div>

            {/* Step 2: Unhedged Slippage Loss */}
            <div className="bg-rose-950/70 p-4 rounded-2xl border-2 border-rose-500/60 flex flex-col justify-between space-y-2 shadow-md">
              <div>
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-mono text-rose-300 uppercase tracking-wider font-bold">
                    2. Deval. USD/MXN
                  </span>
                  <ArrowDownRight className="h-4 w-4 text-rose-400" />
                </div>
                <div className="text-xl sm:text-2xl font-mono font-black text-rose-300">
                  {fxDevaluationLoss}M USD
                </div>
              </div>
              <p className="text-[11px] text-rose-200/90 leading-snug">
                Erosión de margen operativo si el dólar alcanza <strong>$20.80 MXN/USD</strong> sin cobertura.
              </p>
              <div className="text-[10px] font-mono bg-rose-950 px-2 py-1 rounded text-rose-300 font-bold">
                PÉRDIDA DESCUBIERTA
              </div>
            </div>

            {/* Step 3: Forward Premium Cost */}
            <div className="bg-amber-950/60 p-4 rounded-2xl border-2 border-amber-500/60 flex flex-col justify-between space-y-2 shadow-md">
              <div>
                <span className="text-[10px] font-mono text-amber-300 uppercase tracking-wider block font-bold">
                  3. Costo Forward
                </span>
                <div className="text-xl sm:text-2xl font-mono font-black text-amber-300">
                  {forwardPremiumCost}M USD
                </div>
              </div>
              <p className="text-[11px] text-amber-200/90 leading-snug">
                Costo de prima y comisión bancaria para contratar forward cambiario institucional.
              </p>
              <div className="text-[10px] font-mono bg-amber-950 px-2 py-1 rounded text-amber-300 font-bold">
                PRIMA FIJA (0.7%)
              </div>
            </div>

            {/* Step 4: Forward Hedge Savings */}
            <div className="bg-emerald-950/70 p-4 rounded-2xl border-2 border-emerald-500/60 flex flex-col justify-between space-y-2 shadow-md">
              <div>
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-mono text-emerald-300 uppercase tracking-wider font-bold">
                    4. Ahorro Cobertura
                  </span>
                  <ArrowUpRight className="h-4 w-4 text-emerald-400" />
                </div>
                <div className="text-xl sm:text-2xl font-mono font-black text-emerald-300">
                  +${forwardHedgeSavings}M USD
                </div>
              </div>
              <p className="text-[11px] text-emerald-200/90 leading-snug">
                Beneficio garantizado al liquidar a <strong>$19.40 MXN/USD</strong> en vez de $20.80 en ventanilla.
              </p>
              <div className="text-[10px] font-mono bg-emerald-950 px-2 py-1 rounded text-emerald-300 font-bold">
                AHORRO RECUPERADO
              </div>
            </div>

            {/* Step 5: Net Impact */}
            <div className="bg-gradient-to-br from-indigo-950 to-slate-900 p-4 rounded-2xl border-2 border-indigo-400 flex flex-col justify-between space-y-2 shadow-lg">
              <div>
                <span className="text-[10px] font-mono text-indigo-300 uppercase tracking-wider block font-bold">
                  5. Impacto Neto
                </span>
                <div className="text-xl sm:text-2xl font-mono font-black text-emerald-400">
                  {netProtectedImpact}M USD
                </div>
              </div>
              <p className="text-[11px] text-slate-300 leading-snug">
                Riesgo mitigado casi en su totalidad. EBITDA y márgenes comerciales de retail blindados.
              </p>
              <div className="text-[10px] font-mono bg-indigo-950 px-2 py-1 rounded text-indigo-300 font-black">
                ROI COBERTURA: 6.0x
              </div>
            </div>
          </div>

          {/* Interactive Hedge Execution Trigger Box */}
          <div className="bg-gradient-to-r from-purple-950/70 via-slate-900 to-indigo-950/70 p-5 rounded-2xl border-2 border-purple-500/50 flex flex-col sm:flex-row items-center justify-between gap-4 shadow-lg">
            <div className="space-y-1 text-center sm:text-left">
              <div className="flex items-center justify-center sm:justify-start gap-2">
                <Lock className="h-4 w-4 text-purple-400" />
                <span className="font-bold text-sm text-slate-100 font-mono">
                  Contrato Recomendado: Forward Cambiario USD/MXN Fix @ $19.40 ($60.0M USD)
                </span>
              </div>
              <p className="text-xs text-slate-300">
                Instituciones: <strong>Banorte, BBVA & Santander</strong> &bull; Ahorro neto estimado: <strong className="text-emerald-400 font-mono">+$3.60M USD</strong> en Q3/Q4.
              </p>
            </div>

            <button
              type="button"
              onClick={handleExecute}
              className={`px-6 py-3 rounded-xl font-mono text-xs sm:text-sm font-black flex items-center gap-2 transition-all cursor-pointer shrink-0 ${
                executed
                  ? 'bg-slate-800 text-emerald-400 border border-emerald-500 cursor-default'
                  : 'bg-gradient-to-r from-purple-500 to-emerald-400 hover:from-purple-400 hover:to-emerald-300 text-slate-950 shadow-xl shadow-purple-500/30'
              }`}
            >
              {executed ? (
                <>
                  <CheckCircle2 className="h-5 w-5 text-emerald-400" />
                  <span>Forward Ejecutado & Confirmado</span>
                </>
              ) : (
                <>
                  <Zap className="h-5 w-5 fill-slate-950" />
                  <span>Autorizar Forward Cambiario @ $19.40</span>
                </>
              )}
            </button>
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
              {tableData.total_rows} Contratos en BigQuery
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
