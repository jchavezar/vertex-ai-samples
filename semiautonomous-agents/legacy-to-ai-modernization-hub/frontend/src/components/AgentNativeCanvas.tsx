import React, { useState, useEffect } from 'react';
import {
  Sparkles,
  Send,
  FileText,
  Zap,
  TrendingUp,
  RefreshCw,
  CheckCircle2,
} from 'lucide-react';
import {
  AgentQueryResponse,
  BoardMemoResponse,
  HedgingAction,
  ShockImpactData,
  ShockParameters,
} from '../types';
import { calculateShock, generateBoardMemo, queryAgent } from '../services/api';
import { ShockSimulatorSliders } from './ShockSimulatorSliders';
import { DynamicRiskCharts } from './DynamicRiskCharts';
import { ExecutiveMemoModal } from './ExecutiveMemoModal';
import { AgentSwarmStatus } from './AgentSwarmStatus';
import { ExecutiveSynthesisView } from './ExecutiveSynthesisView';

interface AgentNativeCanvasProps {
  onUpdateLatency: (latencyMs: number) => void;
}

export const AgentNativeCanvas: React.FC<AgentNativeCanvasProps> = ({ onUpdateLatency }) => {
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
    const queryText = customQuery || query;
    if (!queryText.trim()) return;

    setQueryLoading(true);
    try {
      const res = await queryAgent(queryText, params);
      setAgentResponse(res);
      setImpact(res.shock_impact);
      onUpdateLatency(res.latency_ms);
    } catch (err) {
      console.error('Agent query failed:', err);
    } finally {
      setQueryLoading(false);
    }
  };

  const handleGenerateMemo = async () => {
    setMemoLoading(true);
    try {
      const res = await generateBoardMemo(
        query || 'Multi-Factor Liquidity & Supply Chain Shock Assessment',
        params,
        'Strategic Liquidity & Supply Chain Shock Assessment (Boardroom Edition)'
      );
      setBoardMemo(res);
      setMemoModalOpen(true);
    } catch (err) {
      console.error('Memo generation failed:', err);
    } finally {
      setMemoLoading(false);
    }
  };

  const handleExecuteHedge = (hedge: HedgingAction) => {
    if (executedHedges.includes(hedge.action)) return;
    setExecutedHedges((prev) => [...prev, hedge.action]);
    setToastMessage(`Executed: "${hedge.action}" (Projected Savings: $${hedge.projected_savings_m}M)`);
    setTimeout(() => setToastMessage(null), 4000);
  };

  const samplePrompts = [
    'Si nuestro proveedor en Taiwán tiene un bloqueo de 90 días, ¿cuáles órdenes están comprometidas, cuántos días de inventario nos quedan antes de parar la línea y qué contratos FX están expuestos?',
    '¿Cuáles son las órdenes de compra abiertas y montos comprometidos con Taiwán?',
    '¿Cuántos días de inventario nos quedan antes del paro de planta en ensamble?',
    '¿Qué contratos forwards en USD/TWD están descubiertos y expuestos a pérdida cambiaria?',
  ];

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
      <div className="cyber-glass rounded-2xl p-5 border border-cyan-500/30 space-y-3">
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

        {/* Quick Chips */}
        <div className="space-y-1.5 pt-1">
          <span className="text-[11px] font-mono text-slate-400 block">Botones de Acceso Rápido (Quick Scenarios):</span>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
            {samplePrompts.map((p, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => {
                  setQuery(p);
                  handleQuerySubmit(undefined, p);
                }}
                className={`p-2.5 rounded-lg text-left text-xs transition-all border flex items-start gap-2 cursor-pointer ${
                  idx === 0
                    ? 'bg-cyan-950/60 hover:bg-cyan-900/70 text-cyan-200 border-cyan-500/40 shadow-sm'
                    : 'bg-slate-900/80 hover:bg-slate-800 text-slate-300 border-slate-800 hover:border-slate-700'
                }`}
              >
                <span className="h-4 w-4 rounded bg-cyan-500/20 text-cyan-400 font-mono text-[10px] font-bold flex items-center justify-center shrink-0 mt-0.5">
                  {idx + 1}
                </span>
                <span className="leading-snug">{p}</span>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Agent Reasoning & Executive Synthesis Card (if query executed) */}
      {agentResponse && (
        <ExecutiveSynthesisView
          agentResponse={agentResponse}
          onExecuteHedge={handleExecuteHedge}
          onOpenBoardMemo={handleGenerateMemo}
        />
      )}

      {/* What-If Shock Sliders */}
      <ShockSimulatorSliders
        params={params}
        onChange={setParams}
        latencyMs={impact?.calculation_latency_ms || 0}
      />

      {/* Dynamic SVG Risk Charts (Morphs dynamically based on query) */}
      {impact && <DynamicRiskCharts impact={impact} queryContext={query} />}

      {/* Suggested Hedging Actions Matrix */}
      {impact && (
        <div className="cyber-glass rounded-2xl p-5 border border-cyan-500/30 space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div className="flex items-center gap-2">
              <TrendingUp className="h-4 w-4 text-cyan-400" />
              <h3 className="font-extrabold text-sm text-slate-100 uppercase tracking-wide">
                Autonomous Hedging & Mitigation Directives
              </h3>
            </div>
            <span className="text-xs font-mono text-slate-400">
              Antigravity Strategy Optimization
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {impact.suggested_hedging_actions.map((h, idx) => {
              const isDone = executedHedges.includes(h.action);
              return (
                <div
                  key={idx}
                  className="bg-slate-950/80 p-4 rounded-xl border border-slate-800 flex flex-col justify-between"
                >
                  <div>
                    <div className="flex items-start justify-between gap-2 mb-2">
                      <span className="font-bold text-xs text-slate-200">{h.action}</span>
                      <span
                        className={`text-[9px] font-mono font-bold px-1.5 py-0.5 rounded ${
                          h.urgency === 'IMMEDIATE'
                            ? 'bg-rose-950 text-rose-300 border border-rose-800'
                            : h.urgency === 'HIGH'
                            ? 'bg-amber-950 text-amber-300 border border-amber-800'
                            : 'bg-slate-800 text-slate-400'
                        }`}
                      >
                        {h.urgency}
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-400">Target Risk: {h.hedged_risk}</p>
                    <div className="mt-2 text-[10px] font-mono text-slate-400">
                      Cost: ${h.cost_basis_k}K &bull; Exp Savings:{' '}
                      <strong className="text-emerald-400">${h.projected_savings_m}M</strong>
                    </div>
                  </div>

                  <button
                    onClick={() => handleExecuteHedge(h)}
                    disabled={isDone}
                    className={`mt-4 w-full py-1.5 rounded-lg text-xs font-bold transition-all flex items-center justify-center gap-1.5 ${
                      isDone
                        ? 'bg-emerald-950 text-emerald-400 border border-emerald-800 cursor-default'
                        : 'bg-cyan-500 hover:bg-cyan-400 text-slate-950 shadow-md shadow-cyan-500/20'
                    }`}
                  >
                    {isDone ? (
                      <>
                        <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />
                        <span>Hedge Executed</span>
                      </>
                    ) : (
                      <>
                        <Zap className="h-3.5 w-3.5" />
                        <span>Execute Strategy</span>
                      </>
                    )}
                  </button>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Background A2A Sentinel Swarm Status */}
      <AgentSwarmStatus />

      {/* Boardroom Memo Modal */}
      <ExecutiveMemoModal
        memo={boardMemo}
        isOpen={memoModalOpen}
        onClose={() => setMemoModalOpen(false)}
      />
    </div>
  );
};
