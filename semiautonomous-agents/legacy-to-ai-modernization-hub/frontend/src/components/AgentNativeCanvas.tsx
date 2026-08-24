import React, { useState, useEffect } from 'react';
import {
  Zap,
  RefreshCw,
  FileText,
  TrendingUp,
  Sparkles,
  Send,
  CheckCircle2,
  Database,
  ArrowRight,
  ShieldAlert,
  Package,
  Factory,
  Building2,
  Activity,
} from 'lucide-react';
import {
  ShockParameters,
  ShockImpactData,
  AgentQueryResponse,
  BoardMemoResponse,
  HedgingAction,
} from '../types';
import { calculateShock, queryAgent, generateBoardMemo } from '../services/api';
import { ShockSimulatorSliders } from './ShockSimulatorSliders';
import { DynamicRiskCharts } from './DynamicRiskCharts';
import { ExecutiveMemoModal } from './ExecutiveMemoModal';
import { ExecutiveSynthesisView } from './ExecutiveSynthesisView';

interface AgentNativeCanvasProps {
  onUpdateLatency: (ms: number) => void;
}

export const AgentNativeCanvas: React.FC<AgentNativeCanvasProps> = ({
  onUpdateLatency,
}) => {
  const [params, setParams] = useState<ShockParameters>({
    interest_rate_bps: 0,
    inflation_rate_pct: 2.5,
    supply_chain_stress_index: 25,
    tariff_volatility_pct: 5.0,
    supplier_default_risk_pct: 1.5,
  });

  const [impact, setImpact] = useState<ShockImpactData | null>(null);
  const [query, setQuery] = useState('');
  const [queryLoading, setQueryLoading] = useState(false);
  const [agentResponse, setAgentResponse] = useState<AgentQueryResponse | null>(null);
  const [boardMemo, setBoardMemo] = useState<BoardMemoResponse | null>(null);
  const [memoLoading, setMemoLoading] = useState(false);
  const [memoModalOpen, setMemoModalOpen] = useState(false);
  const [executedHedges, setExecutedHedges] = useState<string[]>([]);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  // Fast recalculation (<50ms)
  const refreshShockCalculations = async (updatedParams = params) => {
    try {
      const res = await calculateShock(updatedParams);
      setImpact(res);
      onUpdateLatency(res.calculation_latency_ms);
    } catch (err) {
      console.error('Failed shock calculation:', err);
    }
  };

  useEffect(() => {
    refreshShockCalculations(params);
  }, [params]);

  const handleQuerySubmit = async (e?: React.FormEvent, customQuery?: string) => {
    if (e) e.preventDefault();
    const q = customQuery || query;
    if (!q.trim()) return;

    setQueryLoading(true);
    try {
      const response = await queryAgent(q, params);
      setAgentResponse(response);
      setImpact(response.shock_impact);
      onUpdateLatency(response.latency_ms);
    } catch (err) {
      console.error('Agent query error:', err);
    } finally {
      setQueryLoading(false);
    }
  };

  const handleGenerateMemo = async () => {
    setMemoLoading(true);
    try {
      const memo = await generateBoardMemo(
        query || 'Evaluación de disrupción de cadena de suministro y cobertura de liquidez en BigQuery.',
        params,
        'Memorándum de Decisión Estratégica para el Consejo'
      );
      setBoardMemo(memo);
      setMemoModalOpen(true);
    } catch (err) {
      console.error('Memo generation error:', err);
    } finally {
      setMemoLoading(false);
    }
  };

  const handleExecuteHedge = (hedge: HedgingAction) => {
    setExecutedHedges((prev) => [...prev, hedge.action]);
    setToastMessage(`Ejecutado: "${hedge.action}" (Ahorro Proyectado: $${hedge.projected_savings_m}M USD)`);
    setTimeout(() => setToastMessage(null), 4000);
  };

  // High-Visibility EBC Scenario Cards (Engineered for 65"-100" Displays)
  const samplePrompts = [
    {
      id: 1,
      icon: ShieldAlert,
      title: '1. Análisis Multi-Departamento Consolidado',
      highlight: 'Bloqueo Taiwán 90 Días // Compras + Almacén + Tesorería',
      text: 'Si nuestro proveedor en Taiwán tiene un bloqueo de 90 días, ¿cuáles órdenes están comprometidas, cuántos días de inventario nos quedan antes de parar la línea y qué contratos FX están expuestos?',
      badge: 'ESCENARIO COMPLETO (TODO)',
      color: 'from-cyan-500/20 via-blue-500/20 to-indigo-500/20 border-cyan-400',
      badgeColor: 'bg-cyan-500 text-slate-950',
      span: 'md:col-span-2',
    },
    {
      id: 2,
      icon: Activity,
      title: '2. Choque Macroeconómico & Gráficas VaR 99%',
      highlight: 'Fed +125bps & Curvas de Sensibilidad Q1-Q4',
      text: 'Simula un choque macroeconómico con alza de tasas Fed +125bps, bloqueo en Taiwán y muestra las curvas de riesgo VaR y sensibilidad de flujo de caja.',
      badge: 'CHARTS & SLIDERS',
      color: 'from-purple-500/20 via-indigo-500/20 to-slate-900 border-purple-500/50',
      badgeColor: 'bg-purple-950 text-purple-300 border border-purple-700',
      span: 'md:col-span-1',
    },
    {
      id: 3,
      icon: Package,
      title: '3. Compras y Órdenes de Proveedores',
      highlight: 'TSMC ($107.5M), Foxconn ($68M) y ASE Tech ($85.5M)',
      text: '¿Cuáles son las órdenes de compra abiertas y montos comprometidos con Taiwán?',
      badge: 'COMPRAS',
      color: 'from-blue-500/20 via-slate-900 to-slate-900 border-blue-500/50',
      badgeColor: 'bg-blue-950 text-blue-300 border border-blue-700',
      span: 'md:col-span-1',
    },
    {
      id: 4,
      icon: Factory,
      title: '4. Almacén y Riesgo de Paro de Planta',
      highlight: 'Buffer de 34 Días // Paro Proyectado 15 de Julio 2026',
      text: '¿Cuántos días de inventario nos quedan antes del paro de planta en ensamble?',
      badge: 'ALMACÉN',
      color: 'from-amber-500/20 via-slate-900 to-slate-900 border-amber-500/50',
      badgeColor: 'bg-amber-950 text-amber-300 border border-amber-700',
      span: 'md:col-span-1',
    },
    {
      id: 5,
      icon: Building2,
      title: '5. Tesorería y Contratos Forwards FX',
      highlight: '$14.2M Descubiertos // Swaption Collar $63M',
      text: '¿Qué contratos forwards en USD/TWD están descubiertos y qué cobertura se recomienda?',
      badge: 'TESORERÍA',
      color: 'from-purple-500/20 via-slate-900 to-slate-900 border-purple-500/50',
      badgeColor: 'bg-purple-950 text-purple-300 border border-purple-700',
      span: 'md:col-span-1',
    },
  ];

  // Dynamic conditions for showing contextual sections
  const qLower = (query || '').toLowerCase();
  const queryFocus = agentResponse?.query_focus || 'MULTI_DEPT';

  const shouldShowMacroCharts =
    agentResponse &&
    (queryFocus === 'MULTI_DEPT' ||
      qLower.includes('shock') ||
      qLower.includes('estrés') ||
      qLower.includes('estres') ||
      qLower.includes('fed') ||
      qLower.includes('tasa') ||
      qLower.includes('var') ||
      qLower.includes('curva') ||
      qLower.includes('chart') ||
      qLower.includes('gráfic') ||
      qLower.includes('grafic') ||
      qLower.includes('sensibilidad') ||
      qLower.includes('bloqueo'));

  const shouldShowSliders = shouldShowMacroCharts;

  const shouldShowHedgingMatrix =
    agentResponse &&
    (queryFocus === 'TESORERIA' ||
      queryFocus === 'MULTI_DEPT' ||
      qLower.includes('cobertura') ||
      qLower.includes('swaption') ||
      qLower.includes('collar') ||
      qLower.includes('hedge') ||
      qLower.includes('mitigac'));

  return (
    <div className="p-4 sm:p-6 lg:p-8 space-y-8 max-w-7xl mx-auto">
      {/* Toast Notification */}
      {toastMessage && (
        <div className="fixed bottom-8 right-8 z-50 bg-emerald-900/95 text-emerald-100 border-2 border-emerald-400 px-6 py-4 rounded-2xl shadow-2xl backdrop-blur-lg flex items-center gap-3 text-sm font-mono animate-bounce">
          <CheckCircle2 className="h-5 w-5 text-emerald-400" />
          <span className="font-bold">{toastMessage}</span>
        </div>
      )}

      {/* Top Banner: EBC Command Canvas Header */}
      <div className="cyber-glass rounded-2xl p-6 border-2 border-cyan-500/40 flex flex-col md:flex-row items-start md:items-center justify-between gap-6 shadow-2xl">
        <div className="flex items-center gap-4">
          <div className="h-14 w-14 rounded-2xl bg-gradient-to-br from-cyan-500 via-blue-600 to-indigo-600 p-0.5 shadow-xl shadow-cyan-500/30 shrink-0">
            <div className="h-full w-full bg-[#090d16] rounded-[14px] flex items-center justify-center">
              <Zap className="h-8 w-8 text-cyan-400" />
            </div>
          </div>
          <div>
            <div className="flex items-center gap-3">
              <h2 className="font-black text-lg sm:text-xl lg:text-2xl text-slate-100 tracking-wide uppercase">
                AGENT-NATIVE EXECUTIVE COMMAND CANVAS (2026)
              </h2>
              <span className="px-3 py-1 text-xs font-mono bg-cyan-950 text-cyan-300 border border-cyan-700 rounded-full font-bold">
                GENERATIVE UI
              </span>
            </div>
            <p className="text-xs sm:text-sm text-slate-300 font-medium mt-1">
              Live multi-factor stress calculations in &lt;50ms &bull; Natural Language Grounding &bull; One-Click Boardroom Synthesis
            </p>
          </div>
        </div>

        <button
          onClick={handleGenerateMemo}
          disabled={memoLoading}
          className="px-6 py-4 rounded-2xl bg-gradient-to-r from-cyan-400 via-teal-400 to-emerald-400 hover:from-cyan-300 hover:to-emerald-300 text-slate-950 font-black text-sm shadow-2xl shadow-cyan-500/30 flex items-center gap-2.5 transition-all cursor-pointer shrink-0"
        >
          {memoLoading ? (
            <>
              <RefreshCw className="h-5 w-5 animate-spin text-slate-950" />
              <span>Sintetizando Memorándum...</span>
            </>
          ) : (
            <>
              <FileText className="h-5 w-5 text-slate-950" />
              <span>Generar Memorándum del Consejo</span>
            </>
          )}
        </button>
      </div>

      {/* Large-Display EBC Prompt Bar & Fast Scenario Selector */}
      <div className="cyber-glass rounded-3xl p-6 sm:p-8 border-2 border-cyan-500/40 space-y-6 shadow-2xl">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="h-8 w-8 rounded-lg bg-cyan-500/20 border border-cyan-400 flex items-center justify-center">
              <Sparkles className="h-5 w-5 text-cyan-300" />
            </div>
            <span className="font-extrabold text-sm sm:text-base text-slate-100 uppercase tracking-wider font-mono">
              Consulta Ejecutiva en Lenguaje Natural & What-If Prompt
            </span>
          </div>
          <span className="text-xs font-mono text-cyan-300 bg-cyan-950/80 px-3 py-1 rounded-lg border border-cyan-800 hidden sm:inline-block">
            Gemini 3.7 Flash &bull; BigQuery Grounded
          </span>
        </div>

        {/* Large Prominent Prompt Textarea for EBC */}
        <form onSubmit={handleQuerySubmit} className="flex flex-col sm:flex-row items-stretch gap-3">
          <div className="relative flex-1">
            <textarea
              rows={query.length > 100 ? 3 : query.length > 50 ? 2 : 1}
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleQuerySubmit();
                }
              }}
              placeholder="Escribe una pregunta para consultar BigQuery en vivo (ej. 'Si nuestro proveedor en Taiwán tiene un bloqueo de 90 días, ¿cuáles órdenes están comprometidas, cuántos días de inventario nos quedan y qué contratos FX están expuestos?')"
              className="w-full bg-slate-950/90 border-2 border-slate-700 hover:border-cyan-500/80 text-slate-100 placeholder-slate-400 text-sm sm:text-base p-4 sm:p-5 rounded-2xl focus:outline-none focus:border-cyan-400 shadow-inner font-medium resize-y min-h-[58px] leading-relaxed transition-all"
            />
          </div>
          <button
            type="submit"
            disabled={queryLoading}
            className="px-8 py-4 rounded-2xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-black text-sm sm:text-base shadow-xl shadow-cyan-500/30 flex items-center justify-center gap-2.5 transition-all disabled:opacity-50 cursor-pointer shrink-0 h-[58px]"
          >
            {queryLoading ? (
              <RefreshCw className="h-5 w-5 animate-spin" />
            ) : (
              <Send className="h-5 w-5" />
            )}
            <span>Analizar</span>
          </button>
        </form>

        {/* EBC High-Visibility Quick Scenario Cards (Engineered for 100" Displays) */}
        <div className="space-y-3 pt-2">
          <div className="flex items-center justify-between">
            <span className="text-xs sm:text-sm font-mono font-black text-cyan-300 uppercase tracking-wider block">
              ⚡ Escenarios Ejecutivos Pre-Configurados (Clic para Lanzar):
            </span>
            <span className="text-xs font-mono text-slate-400">
              Datos 100% Reales de BigQuery
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3.5">
            {samplePrompts.map((p) => {
              const IconComponent = p.icon;
              return (
                <button
                  key={p.id}
                  type="button"
                  onClick={() => {
                    setQuery(p.text);
                    handleQuerySubmit(undefined, p.text);
                  }}
                  className={`p-5 rounded-2xl text-left transition-all border-2 bg-gradient-to-br ${p.color} hover:scale-[1.01] active:scale-[0.99] flex flex-col justify-between gap-3 cursor-pointer shadow-lg hover:shadow-cyan-500/20 ${p.span}`}
                >
                  <div className="flex items-center justify-between gap-3">
                    <div className="flex items-center gap-2.5">
                      <div className="h-8 w-8 rounded-xl bg-slate-950/80 border border-slate-700 flex items-center justify-center shrink-0">
                        <IconComponent className="h-4 w-4 text-cyan-400" />
                      </div>
                      <h4 className="font-extrabold text-sm sm:text-base text-slate-100 font-sans">
                        {p.title}
                      </h4>
                    </div>
                    <span className={`text-[10px] font-mono px-2.5 py-1 rounded-full font-black uppercase tracking-wider shrink-0 ${p.badgeColor}`}>
                      {p.badge}
                    </span>
                  </div>

                  <div className="text-xs sm:text-sm font-bold text-cyan-300 font-mono">
                    &bull; {p.highlight}
                  </div>

                  <p className="text-xs sm:text-sm text-slate-300 leading-relaxed font-sans line-clamp-2">
                    &ldquo;{p.text}&rdquo;
                  </p>
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* INITIAL STATE HERO (Shown when NO query has been executed yet) */}
      {!agentResponse && (
        <div className="cyber-glass rounded-3xl p-10 border-2 border-slate-800 text-center space-y-6 shadow-2xl">
          <div className="h-16 w-16 rounded-3xl bg-cyan-500/10 border-2 border-cyan-500/40 flex items-center justify-center mx-auto shadow-2xl shadow-cyan-500/30">
            <Sparkles className="h-8 w-8 text-cyan-400 animate-pulse" />
          </div>
          <div className="space-y-2 max-w-2xl mx-auto">
            <h3 className="text-xl sm:text-2xl font-black text-slate-100 tracking-wide uppercase font-sans">
              Canvas Agéntico Generativo Listo para Presentación EBC
            </h3>
            <p className="text-sm sm:text-base text-slate-300 leading-relaxed">
              Selecciona uno de los escenarios ejecutivos arriba o escribe una pregunta en lenguaje natural. Los componentes, tablas y métricas aparecerán dinámicamente según la intención detectada.
            </p>
          </div>
          <div className="flex flex-wrap items-center justify-center gap-6 text-sm font-mono text-slate-400 pt-4 border-t border-slate-800/80 max-w-xl mx-auto">
            <span className="flex items-center gap-2">
              <Database className="h-4 w-4 text-cyan-400" />
              BigQuery: vtxdemos.ebc_modernization_demo
            </span>
            <span className="flex items-center gap-2">
              <Zap className="h-4 w-4 text-emerald-400" />
              Gemini 3.7 Flash Engine
            </span>
          </div>
        </div>
      )}

      {/* 1. AGENT SYNTHESIS & DYNAMIC KPI VIEW (Appears dynamically upon query) */}
      {agentResponse && (
        <ExecutiveSynthesisView
          agentResponse={agentResponse}
          onExecuteHedge={handleExecuteHedge}
          onOpenBoardMemo={handleGenerateMemo}
        />
      )}

      {/* 2. WHAT-IF SHOCK SLIDERS (ONLY shown if query is macro/stress related!) */}
      {shouldShowSliders && impact && (
        <ShockSimulatorSliders
          params={params}
          onChange={setParams}
          latencyMs={impact.calculation_latency_ms || 0}
        />
      )}

      {/* 3. DYNAMIC SVG RISK CHARTS (ONLY shown if query is macro/charts related!) */}
      {shouldShowMacroCharts && impact && (
        <DynamicRiskCharts impact={impact} queryContext={query} />
      )}

      {/* 4. SUGGESTED HEDGING ACTIONS MATRIX (ONLY shown if treasury/hedging related!) */}
      {shouldShowHedgingMatrix && impact && (
        <div className="cyber-glass rounded-3xl p-6 sm:p-8 border-2 border-cyan-500/40 space-y-6 shadow-2xl">
          <div className="flex items-center justify-between border-b border-slate-800 pb-4">
            <div className="flex items-center gap-3">
              <TrendingUp className="h-6 w-6 text-cyan-400" />
              <h3 className="font-black text-base sm:text-lg text-slate-100 uppercase tracking-wide font-mono">
                Directivas de Cobertura y Mitigación Cambiaria FX
              </h3>
            </div>
            <span className="text-xs sm:text-sm font-mono text-slate-400">
              Optimización de Portafolio Antigravity
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
            {impact.suggested_hedging_actions.map((h, idx) => {
              const isDone = executedHedges.includes(h.action);
              return (
                <div
                  key={idx}
                  className="bg-slate-950/90 p-5 rounded-2xl border-2 border-slate-800 flex flex-col justify-between space-y-4 shadow-lg"
                >
                  <div className="space-y-2">
                    <div className="flex items-start justify-between gap-2">
                      <span className="font-bold text-sm text-slate-200">{h.action}</span>
                      <span
                        className={`text-[10px] font-mono px-2.5 py-1 rounded font-black uppercase ${
                          h.urgency === 'CRITICAL'
                            ? 'bg-rose-950 text-rose-300 border border-rose-800'
                            : 'bg-amber-950 text-amber-300 border border-amber-800'
                        }`}
                      >
                        {h.urgency}
                      </span>
                    </div>
                    <p className="text-xs text-slate-400 leading-relaxed">{h.hedged_risk}</p>
                  </div>

                  <div className="pt-3 border-t border-slate-800/80 space-y-3">
                    <div className="flex items-center justify-between text-xs sm:text-sm font-mono">
                      <span className="text-slate-400">Costo: ${h.cost_basis_k}k</span>
                      <span className="text-emerald-400 font-bold">
                        Ahorro: +${h.projected_savings_m}M
                      </span>
                    </div>

                    <button
                      type="button"
                      disabled={isDone}
                      onClick={() => handleExecuteHedge(h)}
                      className={`w-full py-3 rounded-xl font-bold text-xs sm:text-sm flex items-center justify-center gap-2 transition-all cursor-pointer ${
                        isDone
                          ? 'bg-slate-800 text-slate-500 cursor-not-allowed'
                          : 'bg-cyan-500 hover:bg-cyan-400 text-slate-950 shadow-lg shadow-cyan-500/25'
                      }`}
                    >
                      {isDone ? (
                        <>
                          <CheckCircle2 className="h-4 w-4 text-emerald-400" />
                          <span>Ejecutado</span>
                        </>
                      ) : (
                        <>
                          <Zap className="h-4 w-4" />
                          <span>Ejecutar Cobertura</span>
                          <ArrowRight className="h-4 w-4" />
                        </>
                      )}
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Executive Boardroom Memo Modal (White Paper Light-Theme Format) */}
      <ExecutiveMemoModal
        memo={boardMemo}
        isOpen={memoModalOpen}
        onClose={() => setMemoModalOpen(false)}
      />
    </div>
  );
};
