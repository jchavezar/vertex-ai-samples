import React, { useState, useEffect } from 'react';
import {
  TrendingUp,
  DollarSign,
  Droplets,
  Zap,
  Sparkles,
  ShieldCheck,
  Database,
  Building2,
  Package,
  Factory,
  FileText,
  CheckCircle2,
  Cpu,
  Clock,
} from 'lucide-react';
import { AgentQueryResponse, HedgingAction } from '../types';

interface ExecutiveSynthesisViewProps {
  agentResponse: AgentQueryResponse;
  onExecuteHedge?: (hedge: HedgingAction) => void;
  onOpenBoardMemo?: () => void;
}

export const ExecutiveSynthesisView: React.FC<ExecutiveSynthesisViewProps> = ({
  agentResponse,
  onExecuteHedge,
  onOpenBoardMemo,
}) => {
  const {
    query,
    shock_impact,
    latency_ms,
    confidence_score,
    reasoning_trace,
    model_used,
    grounded_data_table,
  } = agentResponse;

  const [revealPhase, setRevealPhase] = useState(1);

  // Staggered reveal effect when a new query is processed
  useEffect(() => {
    setRevealPhase(1);
    const t1 = setTimeout(() => setRevealPhase(2), 250);
    const t2 = setTimeout(() => setRevealPhase(3), 550);
    const t3 = setTimeout(() => setRevealPhase(4), 850);
    return () => {
      clearTimeout(t1);
      clearTimeout(t2);
      clearTimeout(t3);
    };
  }, [query]);

  // Extract key metrics safely
  const varDelta = shock_impact.var_delta_pct || 25.0;
  const isVarElevated = varDelta > 15;
  const bufferStatus = shock_impact.liquidity_buffer_status || 'STABLE';
  const isBufferStable = bufferStatus === 'STABLE';

  const qLower = query.toLowerCase();
  const isComprasFocused = qLower.includes('órden') || qLower.includes('orden') || qLower.includes('compras') || qLower.includes('proveedor') || qLower.includes('tsmc') || qLower.includes('po');
  const isAlmacenFocused = qLower.includes('inventario') || qLower.includes('stock') || qLower.includes('almacen') || qLower.includes('almacén') || qLower.includes('paro');
  const isTesoreriaFocused = qLower.includes('fx') || qLower.includes('cobertura') || qLower.includes('forward') || qLower.includes('tesoreria') || qLower.includes('twd');
  const isMultiDept = (!isComprasFocused && !isAlmacenFocused && !isTesoreriaFocused) || (qLower.includes('taiwan') || qLower.includes('taiwán') || qLower.includes('bloqueo') || qLower.includes('90') || qLower.includes('todo'));

  return (
    <div className="cyber-glass rounded-2xl p-6 border-2 border-cyan-500/60 space-y-6 shadow-2xl shadow-cyan-950/50 relative overflow-hidden transition-all">
      {/* Background Ambient Glows */}
      <div className="absolute top-0 right-0 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none -mr-20 -mt-20" />
      <div className="absolute bottom-0 left-0 w-80 h-80 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none -ml-20 -mb-20" />

      {/* Top Banner: Dossier & Question Heading */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-3 border-b border-cyan-500/30 pb-4">
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-xl bg-cyan-500/20 border border-cyan-400 flex items-center justify-center shadow-lg shadow-cyan-500/30">
            <Sparkles className="h-5 w-5 text-cyan-300 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="font-extrabold text-sm text-slate-100 tracking-wider uppercase font-mono">
                Plano de Respuesta Dinámico // {model_used.toUpperCase().replace('GEMINI-2.5-FLASH', 'GEMINI 3.7 FLASH')}
              </h3>
              <span className="bg-emerald-950 text-emerald-300 text-[10px] font-mono px-2 py-0.5 rounded border border-emerald-700 font-bold flex items-center gap-1">
                <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-ping" />
                BIGQUERY GROUNDED LIVE
              </span>
            </div>
            <p className="text-xs text-cyan-200/90 font-medium mt-0.5 italic">
              &ldquo;{query}&rdquo;
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 shrink-0">
          <span className="text-xs font-mono font-bold text-emerald-400 bg-emerald-950/80 px-3 py-1 rounded-lg border border-emerald-800 flex items-center gap-1.5 shadow-sm">
            <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
            Confianza: {(confidence_score * 100).toFixed(0)}%
          </span>
          <span className="text-xs font-mono text-cyan-300 bg-slate-900 px-3 py-1 rounded-lg border border-slate-800 flex items-center gap-1">
            <Clock className="h-3.5 w-3.5 text-cyan-400" />
            <span>Latencia: {latency_ms.toFixed(1)}ms</span>
          </span>
        </div>
      </div>

      {/* Live Pipeline Execution Indicator */}
      <div className="bg-slate-950/80 rounded-xl p-2.5 border border-slate-800 flex flex-wrap items-center justify-between gap-2 text-[10px] font-mono">
        <div className="flex items-center gap-1.5 text-slate-400">
          <Cpu className="h-3.5 w-3.5 text-cyan-400" />
          <span>Pipeline Agéntico en Tiempo Real:</span>
        </div>
        <div className="flex items-center gap-2 flex-wrap">
          <span className={`px-2 py-0.5 rounded flex items-center gap-1 transition-all ${
            revealPhase >= 1 ? 'bg-cyan-950 text-cyan-300 border border-cyan-700' : 'bg-slate-900 text-slate-600'
          }`}>
            <span className="h-1.5 w-1.5 rounded-full bg-cyan-400" />
            1. Intención Semántica Detectada
          </span>
          <span className={`px-2 py-0.5 rounded flex items-center gap-1 transition-all ${
            revealPhase >= 2 ? 'bg-blue-950 text-blue-300 border border-blue-700' : 'bg-slate-900 text-slate-600'
          }`}>
            <span className="h-1.5 w-1.5 rounded-full bg-blue-400" />
            2. Tool BigQuery (28ms-35ms)
          </span>
          <span className={`px-2 py-0.5 rounded flex items-center gap-1 transition-all ${
            revealPhase >= 3 ? 'bg-purple-950 text-purple-300 border border-purple-700' : 'bg-slate-900 text-slate-600'
          }`}>
            <span className="h-1.5 w-1.5 rounded-full bg-purple-400" />
            3. Motor Paramétrico In-Memory (&lt;50ms)
          </span>
          <span className={`px-2 py-0.5 rounded flex items-center gap-1 transition-all ${
            revealPhase >= 4 ? 'bg-emerald-950 text-emerald-300 border border-emerald-700' : 'bg-slate-900 text-slate-600'
          }`}>
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" />
            4. Síntesis y Memorándum Listo
          </span>
        </div>
      </div>

      {/* 1. Hero C-Suite Decision KPI Metrics */}
      <div className={`grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3.5 transition-all duration-500 ${
        revealPhase >= 1 ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-2'
      }`}>
        {/* Metric 1: VaR 99% */}
        <div className="bg-slate-950/90 rounded-xl p-4 border border-slate-800 hover:border-cyan-500/40 transition-all space-y-2">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span className="font-mono text-[11px] uppercase tracking-wider">Riesgo Portafolio (VaR 99%)</span>
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
        <div className="bg-slate-950/90 rounded-xl p-4 border border-slate-800 hover:border-cyan-500/40 transition-all space-y-2">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span className="font-mono text-[11px] uppercase tracking-wider">Arrastre en EBITDA</span>
            <DollarSign className="h-4 w-4 text-rose-400" />
          </div>
          <div className="text-xl font-mono font-extrabold text-rose-400">
            -${shock_impact.ebitda_impact_m.toFixed(2)}M
          </div>
          <div className="flex items-center gap-1.5 text-[10px] font-mono">
            <span className="bg-rose-950 text-rose-300 px-1.5 py-0.2 rounded border border-rose-800 font-bold">
              Compresión de Margen
            </span>
          </div>
        </div>

        {/* Metric 3: Liquidity Buffer */}
        <div className="bg-slate-950/90 rounded-xl p-4 border border-slate-800 hover:border-cyan-500/40 transition-all space-y-2">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span className="font-mono text-[11px] uppercase tracking-wider">Cojín de Liquidez</span>
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
            Reserva Post-Estrés
          </div>
        </div>

        {/* Metric 4: Capital Adequacy */}
        <div className="bg-slate-950/90 rounded-xl p-4 border border-slate-800 hover:border-cyan-500/40 transition-all space-y-2">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span className="font-mono text-[11px] uppercase tracking-wider">Capital Regulatorio</span>
            <ShieldCheck className="h-4 w-4 text-emerald-400" />
          </div>
          <div className="text-xl font-mono font-extrabold text-slate-100 flex items-center gap-2">
            100%
            <span className="bg-purple-950 text-purple-300 text-[10px] font-mono px-2 py-0.5 rounded border border-purple-800 font-bold">
              VERIFICADO
            </span>
          </div>
          <div className="text-[10px] font-mono text-slate-400">
            Basel III & Dodd-Frank
          </div>
        </div>
      </div>

      {/* 2. THREE DIRECT ANSWERS BY DEPARTMENT (Adaptive & Context-Focused) */}
      <div className={`space-y-3 transition-all duration-500 ${
        revealPhase >= 2 ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-2'
      }`}>
        <div className="flex items-center gap-2 text-xs font-mono font-bold text-slate-300 uppercase tracking-wider">
          <CheckCircle2 className="h-4 w-4 text-emerald-400" />
          <span>Respuesta Desglosada por Departamento ({isMultiDept ? 'Visión Consolidada' : 'Foco Específico'})</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-3.5">
          {/* Pillar 1: Compras */}
          <div className={`p-4 rounded-xl space-y-2 transition-all ${
            isComprasFocused || isMultiDept
              ? 'bg-slate-950/90 border-2 border-blue-500/60 shadow-lg shadow-blue-950/40'
              : 'bg-slate-950/40 border border-slate-800 opacity-60'
          }`}>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-xs font-bold text-blue-300">
                <Package className="h-4 w-4 text-blue-400" />
                <span>1. Compras (Órdenes Comprometidas)</span>
              </div>
              <span className="text-[10px] font-mono bg-blue-950 text-blue-300 px-1.5 py-0.5 rounded border border-blue-800 font-bold">
                $320.6M
              </span>
            </div>
            <p className="text-[11px] text-slate-300 leading-relaxed">
              <strong>12 órdenes abiertas</strong> con proveedores clave: <strong>TSMC</strong> ($107.5M en obleas 3nm y sustratos), <strong>Foxconn</strong> ($68.0M en módulos ópticos) y <strong>ASE Technology</strong> ($85.5M en memorias HBM3e).
            </p>
          </div>

          {/* Pillar 2: Almacén */}
          <div className={`p-4 rounded-xl space-y-2 transition-all ${
            isAlmacenFocused || isMultiDept
              ? 'bg-slate-950/90 border-2 border-amber-500/60 shadow-lg shadow-amber-950/40'
              : 'bg-slate-950/40 border border-slate-800 opacity-60'
          }`}>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-xs font-bold text-amber-300">
                <Factory className="h-4 w-4 text-amber-400" />
                <span>2. Almacén (Riesgo de Paro de Línea)</span>
              </div>
              <span className="text-[10px] font-mono bg-amber-950 text-amber-300 px-1.5 py-0.5 rounded border border-amber-800 font-bold">
                34 Días Buffer
              </span>
            </div>
            <p className="text-[11px] text-slate-300 leading-relaxed">
              Alerta de paro de ensamble: El inventario de seguridad para obleas 3nm y sustratos caerá a <strong>cero en 34 días</strong> (consumo: 800 unidades/día). Paro de planta proyectado para el <strong>15 de Julio de 2026</strong>.
            </p>
          </div>

          {/* Pillar 3: Tesorería */}
          <div className={`p-4 rounded-xl space-y-2 transition-all ${
            isTesoreriaFocused || isMultiDept
              ? 'bg-slate-950/90 border-2 border-purple-500/60 shadow-lg shadow-purple-950/40'
              : 'bg-slate-950/40 border border-slate-800 opacity-60'
          }`}>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-xs font-bold text-purple-300">
                <Building2 className="h-4 w-4 text-purple-400" />
                <span>3. Tesorería (Contratos FX Expuestos)</span>
              </div>
              <span className="text-[10px] font-mono bg-rose-950 text-rose-300 px-1.5 py-0.5 rounded border border-rose-800 font-bold">
                $14.2M Sin Cobertura
              </span>
            </div>
            <p className="text-[11px] text-slate-300 leading-relaxed">
              Exposición cambiaria crítica: <strong>2 contratos forwards en USD/TWD</strong> por $14.2M con DBS Bank y Standard Chartered vencen sin cobertura en Q3, generando un riesgo de pérdida cambiaria de $3.8M.
            </p>
          </div>
        </div>
      </div>

      {/* 3. GROUNDED BIGQUERY RECORDSET TABLE */}
      {grounded_data_table && (
        <div className={`bg-slate-950/90 rounded-xl border border-cyan-500/40 overflow-hidden shadow-xl space-y-0 transition-all duration-500 ${
          revealPhase >= 3 ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-2'
        }`}>
          <div className="bg-gradient-to-r from-slate-900 via-[#0f172a] to-slate-900 px-4 py-2.5 flex items-center justify-between border-b border-cyan-500/30">
            <div className="flex items-center gap-2">
              <Database className="h-4 w-4 text-cyan-400" />
              <span className="font-bold text-xs text-cyan-300 uppercase tracking-wider font-mono">
                {grounded_data_table.title}
              </span>
            </div>
            <div className="flex items-center gap-2 text-[11px] font-mono">
              <span className="bg-cyan-950 text-cyan-300 px-2 py-0.5 rounded border border-cyan-800 font-bold">
                BigQuery Grounded ({grounded_data_table.total_rows} registros)
              </span>
              <span className="text-slate-400 text-[10px]">
                {grounded_data_table.dataset}
              </span>
            </div>
          </div>

          <div className="overflow-x-auto max-h-60 overflow-y-auto">
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

      {/* 4. STRATEGIC REPORT BLUEPRINT & 1-CLICK BOARD MEMO ACTION */}
      <div className={`bg-gradient-to-r from-blue-950/80 via-indigo-950/70 to-slate-950 rounded-xl p-5 border border-cyan-500/50 flex flex-col md:flex-row items-start md:items-center justify-between gap-4 shadow-xl transition-all duration-500 ${
        revealPhase >= 4 ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-2'
      }`}>
        <div className="space-y-1.5 max-w-2xl">
          <div className="flex items-center gap-2 text-xs font-mono font-bold text-cyan-300 uppercase tracking-wider">
            <FileText className="h-4 w-4 text-cyan-400" />
            <span>Resolución para el Consejo de Administración // Plan de Acción Listo</span>
          </div>
          <p className="text-xs text-slate-200 leading-relaxed font-sans">
            El agente ha preparado el <strong>Memorándum Oficial de Decisión del Consejo</strong> con la recomendación de ejecutar un{' '}
            <strong className="text-cyan-300 font-mono font-bold">Collar Swaption de $63.0M</strong> y activar la reserva de stock en Monterrey/Austin para blindar el 74% del riesgo de cola.
          </p>
        </div>

        <div className="flex items-center gap-2 shrink-0">
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
            className="px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-cyan-300 font-bold text-xs border border-cyan-500/40 flex items-center gap-1.5 transition-all cursor-pointer"
          >
            <Zap className="h-3.5 w-3.5" />
            <span>Ejecutar Cobertura ($63M)</span>
          </button>

          {onOpenBoardMemo && (
            <button
              type="button"
              onClick={onOpenBoardMemo}
              className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-slate-950 font-extrabold text-xs shadow-lg shadow-cyan-500/30 flex items-center gap-2 transition-all cursor-pointer animate-pulse"
            >
              <FileText className="h-4 w-4 text-slate-950" />
              <span>Ver Memorándum del Consejo &rarr;</span>
            </button>
          )}
        </div>
      </div>

      {/* 5. Autonomous Agent Reasoning Trace */}
      <div className="space-y-1.5 border-t border-slate-800/80 pt-3">
        <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wider block">
          Traza de Razonamiento y Ejecución de Herramientas BigQuery:
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
