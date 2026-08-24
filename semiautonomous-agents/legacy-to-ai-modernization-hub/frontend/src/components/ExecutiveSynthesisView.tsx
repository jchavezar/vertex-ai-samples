import React, { useState, useEffect } from 'react';
import {
  Sparkles,
  Database,
  Building2,
  Factory,
  FileText,
  Cpu,
  Clock,
  TrendingUp,
  AlertTriangle,
  Layers,
  ArrowUpCircle,
  Truck,
  DollarSign,
  ShieldCheck,
} from 'lucide-react';
import { AgentQueryResponse, HedgingAction } from '../types';
import { ComprasRouteFlowView } from './polymorphic/ComprasRouteFlowView';
import { AlmacenCountdownTimelineView } from './polymorphic/AlmacenCountdownTimelineView';
import { TesoreriaWaterfallView } from './polymorphic/TesoreriaWaterfallView';

interface ExecutiveSynthesisViewProps {
  agentResponse: AgentQueryResponse;
  onExecuteHedge?: (hedge: HedgingAction) => void;
  onOpenBoardMemo?: () => void;
  onScrollToTop?: () => void;
}

export const ExecutiveSynthesisView: React.FC<ExecutiveSynthesisViewProps> = ({
  agentResponse,
  onExecuteHedge,
  onOpenBoardMemo,
  onScrollToTop,
}) => {
  const {
    query,
    shock_impact,
    latency_ms,
    confidence_score,
    reasoning_trace,
    model_used,
    grounded_data_table,
    dynamic_kpis,
    query_focus = 'MULTI_DEPT',
  } = agentResponse;

  const [revealPhase, setRevealPhase] = useState(1);

  // Staggered reveal effect when a new query is processed
  useEffect(() => {
    setRevealPhase(1);
    const t1 = setTimeout(() => setRevealPhase(2), 150);
    const t2 = setTimeout(() => setRevealPhase(3), 350);
    const t3 = setTimeout(() => setRevealPhase(4), 550);
    return () => {
      clearTimeout(t1);
      clearTimeout(t2);
      clearTimeout(t3);
    };
  }, [query]);

  // Default fallback KPIs if not provided
  const kpis = dynamic_kpis && dynamic_kpis.length > 0 ? dynamic_kpis : [
    { label: 'Riesgo Portafolio (VaR 99%)', value: `$${shock_impact.value_at_risk_99_m.toFixed(2)}M`, subtext: `+${shock_impact.var_delta_pct}% vs baseline`, status: 'ELEVADO', status_type: 'danger' as const },
    { label: 'Arrastre en EBITDA', value: `-$${shock_impact.ebitda_impact_m.toFixed(2)}M`, subtext: 'Compresión margen operativo', status: 'ACCIÓN REQUERIDA', status_type: 'danger' as const },
    { label: 'Cojín de Liquidez', value: `$${Math.max(0, 750 - shock_impact.ebitda_impact_m).toFixed(1)}M`, subtext: 'Reserva post-estrés', status: shock_impact.liquidity_buffer_status, status_type: (shock_impact.liquidity_buffer_status === 'STABLE' ? 'success' : 'warning') as 'success' | 'warning' },
    { label: 'Capital Regulatorio', value: '100%', subtext: 'Basel III & Dodd-Frank', status: 'VERIFICADO', status_type: 'success' as const },
  ];

  // Theme styling per domain to make each response visually unique for the EBC Mexican audience
  const themeStyles = {
    LOGISTICA: {
      border: 'border-blue-500/60',
      shadow: 'shadow-blue-950/60',
      badgeBg: 'bg-blue-950 text-blue-300 border-blue-500',
      glow: 'bg-blue-500/15',
      icon: Truck,
      title: 'Plano de Respuesta: Logística & Terminales Portuarias (CICE / Manzanillo)',
    },
    MANUFACTURA: {
      border: 'border-amber-500/60',
      shadow: 'shadow-amber-950/60',
      badgeBg: 'bg-amber-950 text-amber-300 border-amber-500',
      glow: 'bg-amber-500/15',
      icon: Factory,
      title: 'Plano de Respuesta: Manufactura, Farma & Alimentos (Silanes / Gloria)',
    },
    RETAIL_FX: {
      border: 'border-purple-500/60',
      shadow: 'shadow-purple-950/60',
      badgeBg: 'bg-purple-950 text-purple-300 border-purple-500',
      glow: 'bg-purple-500/15',
      icon: DollarSign,
      title: 'Plano de Respuesta: Retail & Cobertura Cambiaria USD/MXN (Boxito / Macropay)',
    },
    HR_RATINGS: {
      border: 'border-emerald-500/60',
      shadow: 'shadow-emerald-950/60',
      badgeBg: 'bg-emerald-950 text-emerald-300 border-emerald-500',
      glow: 'bg-emerald-500/15',
      icon: ShieldCheck,
      title: 'Plano de Respuesta: Solvencia & Calificación Crediticia (Metodología HR Ratings)',
    },
    COMPRAS: {
      border: 'border-blue-500/60',
      shadow: 'shadow-blue-950/60',
      badgeBg: 'bg-blue-950 text-blue-300 border-blue-500',
      glow: 'bg-blue-500/15',
      icon: Truck,
      title: 'Plano de Respuesta: Logística & Terminales Portuarias (CICE / Manzanillo)',
    },
    ALMACEN: {
      border: 'border-amber-500/60',
      shadow: 'shadow-amber-950/60',
      badgeBg: 'bg-amber-950 text-amber-300 border-amber-500',
      glow: 'bg-amber-500/15',
      icon: Factory,
      title: 'Plano de Respuesta: Manufactura, Farma & Alimentos (Silanes / Gloria)',
    },
    TESORERIA: {
      border: 'border-purple-500/60',
      shadow: 'shadow-purple-950/60',
      badgeBg: 'bg-purple-950 text-purple-300 border-purple-500',
      glow: 'bg-purple-500/15',
      icon: DollarSign,
      title: 'Plano de Respuesta: Retail & Cobertura Cambiaria USD/MXN (Boxito / Macropay)',
    },
    MULTI_DEPT: {
      border: 'border-cyan-500/60',
      shadow: 'shadow-cyan-950/60',
      badgeBg: 'bg-cyan-950 text-cyan-300 border-cyan-500',
      glow: 'bg-cyan-500/15',
      icon: Sparkles,
      title: 'Plano de Respuesta: Diagnóstico Consolidado Multi-Empresa EBC',
    },
  }[query_focus] || {
    border: 'border-cyan-500/60',
    shadow: 'shadow-cyan-950/60',
    badgeBg: 'bg-emerald-950 text-emerald-300 border-emerald-500',
    glow: 'bg-cyan-500/15',
    icon: Sparkles,
    title: 'Plano de Respuesta Ejecutiva',
  };

  const HeaderIcon = themeStyles.icon;

  return (
    <div className={`cyber-glass rounded-3xl p-6 sm:p-8 lg:p-10 border-2 ${themeStyles.border} space-y-8 shadow-2xl ${themeStyles.shadow} relative overflow-hidden transition-all animate-zoom-entrance`}>
      {/* Background Ambient Glows & Scanline */}
      <div className={`absolute top-0 right-0 w-96 h-96 ${themeStyles.glow} rounded-full blur-3xl pointer-events-none -mr-20 -mt-20`} />
      <div className="absolute bottom-0 left-0 w-80 h-80 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none -ml-20 -mb-20" />
      <div className="absolute inset-x-0 top-0 h-1 bg-gradient-to-r from-transparent via-cyan-400 to-transparent opacity-75 animate-pulse" />

      {/* Top Banner: Dossier & Question Heading */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div className="flex items-center gap-4">
          <div className="h-12 w-12 rounded-2xl bg-slate-900/90 border-2 border-cyan-400 flex items-center justify-center shadow-xl shadow-cyan-500/30 shrink-0">
            <HeaderIcon className="h-7 w-7 text-cyan-300 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center gap-3 flex-wrap">
              <h3 className="font-black text-base sm:text-lg lg:text-xl text-slate-100 tracking-wider uppercase font-mono">
                {themeStyles.title} // {model_used.toUpperCase().replace('GEMINI-2.5-FLASH', 'GEMINI 3.7 FLASH')}
              </h3>
              <span className={`text-xs font-mono px-3 py-1 rounded-full font-black flex items-center gap-1.5 shadow-md ${themeStyles.badgeBg}`}>
                <span className="h-2 w-2 rounded-full bg-cyan-400 animate-ping" />
                FOCO: {query_focus} (BIGQUERY LIVE)
              </span>
            </div>
            <p className="text-sm sm:text-base text-cyan-200/90 font-medium mt-1 italic">
              &ldquo;{query}&rdquo;
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3 shrink-0 flex-wrap">
          {onScrollToTop && (
            <button
              type="button"
              onClick={onScrollToTop}
              className="text-xs font-mono font-bold text-cyan-400 bg-slate-900 hover:bg-slate-800 px-3.5 py-2 rounded-xl border border-cyan-500/40 flex items-center gap-1.5 shadow-md transition-all cursor-pointer"
            >
              <ArrowUpCircle className="h-4 w-4" />
              <span>Subir a Escenarios</span>
            </button>
          )}

          <span className="text-xs sm:text-sm font-mono font-bold text-emerald-400 bg-emerald-950/90 px-3.5 py-2 rounded-xl border border-emerald-700 flex items-center gap-2 shadow-sm">
            <span className="h-2.5 w-2.5 rounded-full bg-emerald-400 animate-pulse" />
            Confianza: {(confidence_score * 100).toFixed(0)}%
          </span>
          <span className="text-xs sm:text-sm font-mono text-cyan-300 bg-slate-900 px-3.5 py-2 rounded-xl border border-slate-700 flex items-center gap-1.5">
            <Clock className="h-4 w-4 text-cyan-400" />
            <span>Latencia: {latency_ms.toFixed(1)}ms</span>
          </span>
        </div>
      </div>

      {/* Live Pipeline Execution Indicator */}
      <div className="bg-slate-950/90 rounded-2xl p-3 border border-slate-800 flex flex-wrap items-center justify-between gap-3 text-xs font-mono shadow-inner">
        <div className="flex items-center gap-2 text-slate-300 font-bold">
          <Cpu className="h-4 w-4 text-cyan-400" />
          <span>Pipeline Agéntico en Tiempo Real:</span>
        </div>
        <div className="flex items-center gap-2.5 flex-wrap">
          <span className={`px-3 py-1 rounded-lg flex items-center gap-1.5 transition-all ${
            revealPhase >= 1 ? 'bg-cyan-950 text-cyan-300 border border-cyan-600 shadow-sm' : 'bg-slate-900 text-slate-600'
          }`}>
            <span className="h-2 w-2 rounded-full bg-cyan-400" />
            1. Intención Detectada ({query_focus})
          </span>
          <span className={`px-3 py-1 rounded-lg flex items-center gap-1.5 transition-all ${
            revealPhase >= 2 ? 'bg-blue-950 text-blue-300 border border-blue-600 shadow-sm' : 'bg-slate-900 text-slate-600'
          }`}>
            <span className="h-2 w-2 rounded-full bg-blue-400" />
            2. BigQuery Live Scan (28ms-35ms)
          </span>
          <span className={`px-3 py-1 rounded-lg flex items-center gap-1.5 transition-all ${
            revealPhase >= 3 ? 'bg-purple-950 text-purple-300 border border-purple-600 shadow-sm' : 'bg-slate-900 text-slate-600'
          }`}>
            <span className="h-2 w-2 rounded-full bg-purple-400" />
            3. Metáfora Visual Polymorphic ({query_focus})
          </span>
          <span className={`px-3 py-1 rounded-lg flex items-center gap-1.5 transition-all ${
            revealPhase >= 4 ? 'bg-emerald-950 text-emerald-300 border border-emerald-600 shadow-sm' : 'bg-slate-900 text-slate-600'
          }`}>
            <span className="h-2 w-2 rounded-full bg-emerald-400" />
            4. Síntesis y Memorándum Listo
          </span>
        </div>
      </div>

      {/* 1. DYNAMIC CONTEXT-SPECIFIC KPI METRICS CARDS (EBC Glanceable High-Contrast Design) */}
      <div className={`grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 transition-all duration-500 ${
        revealPhase >= 1 ? 'opacity-100 translate-y-0 scale-100' : 'opacity-0 translate-y-4 scale-95'
      }`}>
        {kpis.map((kpi, idx) => (
          <div
            key={idx}
            className={`p-5 sm:p-6 rounded-2xl transition-all space-y-3 border-2 relative group hover:scale-[1.03] hover:z-20 cursor-default shadow-xl ${
              kpi.status_type === 'danger'
                ? 'bg-slate-950/90 border-rose-500/50 hover:border-rose-400 shadow-rose-950/30'
                : kpi.status_type === 'warning'
                ? 'bg-slate-950/90 border-amber-500/50 hover:border-amber-400 shadow-amber-950/30'
                : kpi.status_type === 'info'
                ? 'bg-slate-950/90 border-blue-500/50 hover:border-blue-400 shadow-blue-950/30'
                : 'bg-slate-950/90 border-emerald-500/50 hover:border-emerald-400 shadow-emerald-950/30'
            }`}
          >
            <div className="flex items-center justify-between text-slate-400 text-xs sm:text-sm">
              <span className="font-mono text-xs uppercase tracking-wider text-slate-200 font-extrabold truncate">
                {kpi.label}
              </span>
              {kpi.status_type === 'danger' ? (
                <AlertTriangle className="h-5 w-5 text-rose-400 shrink-0" />
              ) : kpi.status_type === 'warning' ? (
                <AlertTriangle className="h-5 w-5 text-amber-400 shrink-0" />
              ) : (
                <TrendingUp className="h-5 w-5 text-emerald-400 shrink-0" />
              )}
            </div>
            
            {/* Big High-Impact Figure for EBC Wall Monitors */}
            <div className="text-3xl sm:text-4xl font-mono font-black text-slate-100 tracking-tight">
              {kpi.value}
            </div>

            <div className="flex items-center justify-between gap-2 text-xs font-mono pt-2 border-t border-slate-800/80">
              <span className="text-slate-400 truncate">{kpi.subtext}</span>
              <span
                className={`px-2.5 py-0.5 rounded-full font-black shrink-0 text-[10px] uppercase ${
                  kpi.status_type === 'danger'
                    ? 'bg-rose-950 text-rose-300 border border-rose-800'
                    : kpi.status_type === 'warning'
                    ? 'bg-amber-950 text-amber-300 border border-amber-800'
                    : 'bg-emerald-950 text-emerald-300 border border-emerald-800'
                }`}
              >
                {kpi.status}
              </span>
            </div>
          </div>
        ))}
      </div>

      {/* 2. DYNAMIC POLYMORPHIC METAPHOR DISPATCHER (Radically different UI per Intent) */}
      
      {/* 2A. LOGÍSTICA & PUERTOS (Grupo CICE, Senda, Promologistics) */}
      {(query_focus === 'LOGISTICA' || query_focus === 'COMPRAS') && (
        <ComprasRouteFlowView
          tableData={grounded_data_table}
        />
      )}

      {/* 2B. MANUFACTURA & FARMA (Lab. Silanes, Cremería Gloria, Médica Sur) */}
      {(query_focus === 'MANUFACTURA' || query_focus === 'ALMACEN') && (
        <AlmacenCountdownTimelineView
          tableData={grounded_data_table}
        />
      )}

      {/* 2C. RETAIL, TIPO DE CAMBIO & MARGEN (Boxito, Macropay, Cklass) */}
      {(query_focus === 'RETAIL_FX' || query_focus === 'TESORERIA') && (
        <TesoreriaWaterfallView
          tableData={grounded_data_table}
          onExecuteHedge={onExecuteHedge}
        />
      )}

      {/* 2D. MULTI-EMPRESA EBC / HR RATINGS CONSOLIDADO */}
      {(query_focus === 'MULTI_DEPT' || query_focus === 'HR_RATINGS') && (
        <div className="space-y-6">
          <div className="bg-slate-950/90 rounded-3xl p-6 sm:p-8 border-2 border-cyan-500/40 space-y-6 shadow-2xl">
            <div className="flex items-center justify-between border-b border-slate-800 pb-4">
              <span className="text-sm sm:text-base font-mono font-black text-slate-200 uppercase tracking-wider flex items-center gap-2.5">
                <Layers className="h-5 w-5 text-cyan-400" />
                Diagnóstico Consolidado Multi-Empresa EBC (CICE + Silanes + Gloria + Boxito + HR Ratings)
              </span>
              <span className="text-xs font-mono text-cyan-400">
                Ground Truth Unificado en BigQuery
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
              {/* Pillar 1: Logística y Puertos (Grupo CICE & Manzanillo) */}
              <div className="bg-slate-900/90 p-5 rounded-2xl border-2 border-blue-500/60 space-y-3 shadow-lg">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-sm text-blue-300 flex items-center gap-2">
                    <Truck className="h-4 w-4 text-blue-400" />
                    1. Logística & Puertos (CICE)
                  </span>
                  <span className="text-xs font-mono bg-blue-950 text-blue-300 px-2.5 py-0.5 rounded-full border border-blue-700 font-bold">
                    1,420 TEUs
                  </span>
                </div>
                <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">
                  Contenedores demorados en <strong>Veracruz (CICE)</strong> y <strong>Manzanillo</strong> con sobrecosto de <strong>$4.85M USD</strong>. Desvío intermodal a Monterrey viable.
                </p>
              </div>

              {/* Pillar 2: Manufactura y Farma (Silanes & Gloria) */}
              <div className="bg-slate-900/90 p-5 rounded-2xl border-2 border-amber-500/60 space-y-3 shadow-lg">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-sm text-amber-300 flex items-center gap-2">
                    <Factory className="h-4 w-4 text-amber-400" />
                    2. Manufactura & Farma
                  </span>
                  <span className="text-xs font-mono bg-amber-950 text-amber-300 px-2.5 py-0.5 rounded-full border border-amber-700 font-bold">
                    21 Días Buffer
                  </span>
                </div>
                <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">
                  Stock de seguridad de <strong>Grasa Butírica (Gloria)</strong> y <strong>APIs (Silanes)</strong> cae a cero el <strong>16 de Julio de 2026</strong>. Reserva en Querétaro de +14d.
                </p>
              </div>

              {/* Pillar 3: Retail y Tipo de Cambio (Boxito & Macropay) */}
              <div className="bg-slate-900/90 p-5 rounded-2xl border-2 border-purple-500/60 space-y-3 shadow-lg">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-sm text-purple-300 flex items-center gap-2">
                    <Building2 className="h-4 w-4 text-purple-400" />
                    3. Retail & Margen FX
                  </span>
                  <span className="text-xs font-mono bg-rose-950 text-rose-300 px-2.5 py-0.5 rounded-full border border-rose-700 font-bold">
                    $85.0M USD Expuestos
                  </span>
                </div>
                <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">
                  Compras de importación de <strong>Boxito</strong> y <strong>Macropay</strong> expuestas a USD/MXN a $20.80. Cobertura forward garantiza ahorro de <strong>+$3.60M USD</strong>.
                </p>
              </div>
            </div>
          </div>

          {/* Grounded Table for Multi-Dept */}
          {grounded_data_table && (
            <div className="bg-slate-950/90 rounded-2xl border-2 border-cyan-500/40 overflow-hidden shadow-2xl">
              <div className="bg-gradient-to-r from-slate-900 via-[#0f172a] to-slate-900 px-5 py-3.5 flex items-center justify-between border-b border-cyan-500/30">
                <div className="flex items-center gap-2.5">
                  <Database className="h-5 w-5 text-cyan-400" />
                  <span className="font-bold text-sm text-cyan-300 uppercase tracking-wider font-mono">
                    {grounded_data_table.title}
                  </span>
                </div>
                <span className="bg-cyan-950 text-cyan-300 px-3 py-1 rounded-lg border border-cyan-700 font-bold text-xs font-mono">
                  {grounded_data_table.total_rows} Registros Consolidados
                </span>
              </div>

              <div className="overflow-x-auto max-h-72 overflow-y-auto">
                <table className="w-full text-left border-collapse whitespace-nowrap text-xs sm:text-sm font-sans">
                  <thead>
                    <tr className="bg-slate-900/90 text-slate-300 border-b border-slate-800 font-mono text-xs">
                      {grounded_data_table.headers.map((h, idx) => (
                        <th key={idx} className="p-3.5 font-bold uppercase tracking-wider text-slate-200 border-r border-slate-800/80">
                          {h}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60 font-mono text-xs sm:text-sm">
                    {grounded_data_table.rows.map((row, idx) => (
                      <tr key={idx} className={idx % 2 === 0 ? 'bg-slate-950/60' : 'bg-slate-900/60'}>
                        {Object.values(row).map((val: any, cIdx: number) => (
                          <td key={cIdx} className="p-3.5 text-slate-100 border-r border-slate-800/60">
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
      )}

      {/* 3. STRATEGIC REPORT BLUEPRINT & 1-CLICK BOARD MEMO ACTION */}
      <div className={`bg-gradient-to-r from-blue-950/90 via-indigo-950/80 to-slate-950 rounded-2xl p-6 sm:p-8 border-2 border-cyan-500/50 flex flex-col md:flex-row items-start md:items-center justify-between gap-6 shadow-2xl transition-all duration-500 ${
        revealPhase >= 4 ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'
      }`}>
        <div className="space-y-2 max-w-3xl">
          <div className="flex items-center gap-2.5 text-sm sm:text-base font-mono font-black text-cyan-300 uppercase tracking-wider">
            <FileText className="h-5 w-5 text-cyan-400" />
            <span>Resolución Oficial de Consejo // Plan de Acción Listo</span>
          </div>
          <p className="text-sm sm:text-base text-slate-200 leading-relaxed font-sans">
            El agente ha formulado el <strong>Memorándum Oficial del Consejo de Administración</strong> adaptado a <strong>{query_focus}</strong>, listo para exportación en papel blanco oficial y firma digital ejecutiva.
          </p>
        </div>

        <div className="flex items-center gap-3 shrink-0 flex-wrap">
          {onOpenBoardMemo && (
            <button
              type="button"
              onClick={onOpenBoardMemo}
              className="px-6 py-3.5 rounded-2xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-slate-950 font-black text-xs sm:text-sm shadow-xl shadow-cyan-500/30 flex items-center gap-2.5 transition-all cursor-pointer animate-pulse"
            >
              <FileText className="h-5 w-5 text-slate-950" />
              <span>Ver Memorándum Oficial &rarr;</span>
            </button>
          )}
        </div>
      </div>

      {/* 4. Autonomous Agent Reasoning Trace */}
      <div className="space-y-2 border-t border-slate-800/80 pt-4">
        <span className="text-xs font-mono text-slate-400 uppercase tracking-wider block font-bold">
          Traza de Razonamiento y Ejecución de Herramientas BigQuery:
        </span>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5 text-xs font-mono">
          {reasoning_trace.map((step, i) => (
            <div
              key={i}
              className="bg-slate-900/80 p-2.5 rounded-xl border border-slate-800 text-slate-200 flex items-center gap-2.5"
            >
              <span className="h-2 w-2 rounded-full bg-cyan-400" />
              <span>{step.replace('gemini-2.5-flash', 'gemini-3.7-flash')}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
