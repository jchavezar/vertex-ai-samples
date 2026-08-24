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
    setToastMessage(`Ejecutado con éxito: "${hedge.action}" (Ahorro Proyectado: $${hedge.projected_savings_m}M USD)`);
    setTimeout(() => setToastMessage(null), 4000);
  };

  const samplePrompts = [
    {
      title: 'Análisis Multi-Departamento Consolidado',
      text: 'Si nuestro proveedor en Taiwán tiene un bloqueo de 90 días, ¿cuáles órdenes están comprometidas, cuántos días de inventario nos quedan antes de parar la línea y qué contratos FX están expuestos?',
      badge: 'TODO (CROSS-TABLE)',
    },
    {
      title: 'Choque Macroeconómico y Gráficas de Estrés VaR 99%',
      text: 'Simula un choque macroeconómico con alza de tasas Fed +125bps, bloqueo en Taiwán y muestra las curvas de riesgo VaR y sensibilidad de flujo de caja.',
      badge: 'CHARTS & VAR 99%',
    },
    {
      title: 'Órdenes de Compra y Proveedores (Taiwán)',
      text: '¿Cuáles son las órdenes de compra abiertas y montos comprometidos con Taiwán?',
      badge: 'COMPRAS',
    },
    {
      title: 'Inventario de Seguridad y Riesgo de Paro',
      text: '¿Cuántos días de inventario nos quedan antes del paro de planta en ensamble?',
      badge: 'ALMACÉN',
    },
    {
      title: 'Contratos Forwards y Cobertura Cambiaria',
      text: '¿Qué contratos forwards en USD/TWD están descubiertos y qué cobertura se recomienda?',
      badge: 'TESORERÍA',
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
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      {/* Toast Notification */}
      {toastMessage && (
        <div className="fixed bottom-6 right-6 z-50 bg-emerald-900/90 text-emerald-200 border border-emerald-500/60 px-4 py-3 rounded-xl shadow-2xl backdrop-blur-md flex items-center gap-2 text-xs font-mono animate-bounce">
          <CheckCircle2 className="h-4 w-4 text-emerald-400" />
          <span>{toastMessage}</span>
        </div>
      )}

      {/* Top Banner: Agent-Native Overview */}
      <div className="cyber-glass rounded-2xl p-5 border border-cyan-500/30 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div className="flex items-center gap-3.5">
          <div className="h-11 w-11 rounded-xl bg-gradient-to-br from-cyan-500 via-blue-600 to-violet-600 p-0.5 shadow-lg shadow-cyan-500/30">
            <div className="h-full w-full bg-[#090d16] rounded-[10px] flex items-center justify-center">
              <Zap className="h-6 w-6 text-cyan-400" />
            </div>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="font-extrabold text-base text-slate-100 tracking-wide">
                AGENT-NATIVE EXECUTIVE COMMAND CANVAS (2026)
              </h2>
              <span className="px-2 py-0.5 text-[10px] font-mono bg-cyan-950 text-cyan-400 border border-cyan-800 rounded font-bold">
                GENERATIVE UI
              </span>
            </div>
            <p className="text-xs text-slate-400 font-medium mt-0.5">
              Live multi-factor stress calculations in &lt;50ms &bull; Natural Language Grounding &bull; One-Click Boardroom Synthesis
            </p>
          </div>
        </div>

        <button
          onClick={handleGenerateMemo}
          disabled={memoLoading}
          className="px-5 py-3 rounded-xl bg-gradient-to-r from-cyan-400 via-teal-400 to-emerald-400 hover:from-cyan-300 hover:to-emerald-300 text-slate-950 font-black text-xs shadow-xl shadow-cyan-500/25 flex items-center gap-2 transition-all cursor-pointer"
        >
          {memoLoading ? (
            <>
              <RefreshCw className="h-4 w-4 animate-spin text-slate-950" />
              <span>Synthesizing Board Memo...</span>
            </>
          ) : (
            <>
              <FileText className="h-4 w-4 text-slate-950" />
              <span>Generate Executive Board Memo</span>
            </>
          )}
        </button>
      </div>

      {/* Natural Language Query Bar with Auto-Expanding Multi-line Input & Chips */}
      <div className="cyber-glass rounded-2xl p-5 border border-cyan-500/30 space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Sparkles className="h-4 w-4 text-cyan-400" />
            <span className="font-bold text-xs text-slate-200 uppercase tracking-wide">
              Natural Language Executive Query & What-If Prompt
            </span>
          </div>
          <span className="text-[10px] font-mono text-cyan-400">
            Powered by Google GenAI (Gemini 3.7 Flash) &bull; BigQuery Grounded
          </span>
        </div>

        <form onSubmit={handleQuerySubmit} className="flex flex-col sm:flex-row items-stretch sm:items-start gap-2">
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
              className="w-full bg-slate-950/80 border border-slate-700 text-slate-100 placeholder-slate-500 text-xs p-3.5 rounded-xl focus:outline-none focus:border-cyan-500 shadow-inner font-medium resize-y min-h-[46px] leading-relaxed"
            />
          </div>
          <button
            type="submit"
            disabled={queryLoading}
            className="px-6 py-3.5 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold text-xs shadow-lg shadow-cyan-500/20 flex items-center justify-center gap-2 transition-all disabled:opacity-50 cursor-pointer shrink-0 h-[46px]"
          >
            {queryLoading ? (
              <RefreshCw className="h-4 w-4 animate-spin" />
            ) : (
              <Send className="h-4 w-4" />
            )}
            <span>Analyze</span>
          </button>
        </form>

        {/* Quick Scenario Selection Cards */}
        <div className="space-y-2 pt-1">
          <span className="text-[11px] font-mono text-slate-400 block font-bold uppercase tracking-wider">
            Escenarios de Decisión Ejecutiva (Acceso Rápido):
          </span>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2.5">
            {samplePrompts.map((p, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => {
                  setQuery(p.text);
                  handleQuerySubmit(undefined, p.text);
                }}
                className={`p-3 rounded-xl text-left text-xs transition-all border flex flex-col justify-between gap-1.5 cursor-pointer ${
                  idx === 0
                    ? 'bg-gradient-to-br from-cyan-950/80 to-blue-950/60 hover:from-cyan-900/90 hover:to-blue-900/80 text-cyan-100 border-cyan-500/50 shadow-md md:col-span-2'
                    : 'bg-slate-900/80 hover:bg-slate-800 text-slate-200 border-slate-800 hover:border-slate-700'
                }`}
              >
                <div className="flex items-center justify-between gap-2">
                  <span className="font-bold text-[11px] text-cyan-300 font-mono flex items-center gap-1.5">
                    <span className="h-4 w-4 rounded bg-cyan-500/20 text-cyan-400 text-[10px] font-bold flex items-center justify-center">
                      {idx + 1}
                    </span>
                    {p.title}
                  </span>
                  <span className={`text-[9px] font-mono px-1.5 py-0.2 rounded font-bold ${
                    idx === 0 ? 'bg-cyan-500 text-slate-950' : 'bg-slate-800 text-slate-400'
                  }`}>
                    {p.badge}
                  </span>
                </div>
                <p className="text-[11px] text-slate-300 leading-snug line-clamp-2">
                  &ldquo;{p.text}&rdquo;
                </p>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* INITIAL STATE HERO (Shown when NO query has been executed yet) */}
      {!agentResponse && (
        <div className="cyber-glass rounded-2xl p-8 border border-slate-800 text-center space-y-4 shadow-xl">
          <div className="h-14 w-14 rounded-2xl bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center mx-auto shadow-lg shadow-cyan-500/20">
            <Sparkles className="h-7 w-7 text-cyan-400" />
          </div>
          <div className="space-y-1.5 max-w-xl mx-auto">
            <h3 className="text-base font-extrabold text-slate-100 tracking-wide">
              Canvas Agéntico Generativo Listo para Consultas
            </h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Selecciona uno de los escenarios de acceso rápido arriba o escribe una pregunta en lenguaje natural. Los componentes, tablas y métricas aparecerán dinámicamente según la intención detectada.
            </p>
          </div>
          <div className="flex flex-wrap items-center justify-center gap-4 text-xs font-mono text-slate-500 pt-2 border-t border-slate-800/80 max-w-lg mx-auto">
            <span className="flex items-center gap-1.5">
              <Database className="h-3.5 w-3.5 text-cyan-400" />
              BigQuery: vtxdemos.ebc_modernization_demo
            </span>
            <span className="flex items-center gap-1.5">
              <Zap className="h-3.5 w-3.5 text-emerald-400" />
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
        <div className="cyber-glass rounded-2xl p-5 border border-cyan-500/30 space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div className="flex items-center gap-2">
              <TrendingUp className="h-4 w-4 text-cyan-400" />
              <h3 className="font-extrabold text-sm text-slate-100 uppercase tracking-wide font-mono">
                Directivas de Cobertura y Mitigación Cambiaria FX
              </h3>
            </div>
            <span className="text-xs font-mono text-slate-400">
              Optimización de Portafolio Antigravity
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {impact.suggested_hedging_actions.map((h, idx) => {
              const isDone = executedHedges.includes(h.action);
              return (
                <div
                  key={idx}
                  className="bg-slate-950/80 p-4 rounded-xl border border-slate-800 flex flex-col justify-between space-y-3"
                >
                  <div className="space-y-1.5">
                    <div className="flex items-start justify-between gap-2">
                      <span className="font-bold text-xs text-slate-200">{h.action}</span>
                      <span
                        className={`text-[9px] font-mono px-2 py-0.5 rounded font-bold shrink-0 ${
                          h.urgency === 'CRITICAL'
                            ? 'bg-rose-950 text-rose-300 border border-rose-800'
                            : 'bg-amber-950 text-amber-300 border border-amber-800'
                        }`}
                      >
                        {h.urgency}
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-400">{h.hedged_risk}</p>
                  </div>

                  <div className="pt-2 border-t border-slate-800/80 space-y-2">
                    <div className="flex items-center justify-between text-xs font-mono">
                      <span className="text-slate-500">Costo: ${h.cost_basis_k}k</span>
                      <span className="text-emerald-400 font-bold">
                        Ahorro: +${h.projected_savings_m}M
                      </span>
                    </div>

                    <button
                      type="button"
                      disabled={isDone}
                      onClick={() => handleExecuteHedge(h)}
                      className={`w-full py-2 rounded-lg font-bold text-xs flex items-center justify-center gap-1.5 transition-all cursor-pointer ${
                        isDone
                          ? 'bg-slate-800 text-slate-500 cursor-not-allowed'
                          : 'bg-cyan-500 hover:bg-cyan-400 text-slate-950 shadow-md shadow-cyan-500/20'
                      }`}
                    >
                      {isDone ? (
                        <>
                          <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />
                          <span>Ejecutado</span>
                        </>
                      ) : (
                        <>
                          <Zap className="h-3.5 w-3.5" />
                          <span>Ejecutar Cobertura</span>
                          <ArrowRight className="h-3.5 w-3.5" />
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
