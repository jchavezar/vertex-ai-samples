import React, { useState, useEffect, useRef } from 'react';
import {
  Network,
  Sparkles,
  Play,
  Square,
  ArrowRight,
  Loader2,
  Users,
  Activity
} from 'lucide-react';
import { AgentConfig, AgentState, SwarmMandate, ExecutiveDeliverable } from '../types';
import { fetchSwarmAgents, fetchSwarmMandates, streamSwarmExecution } from '../services/api';
import { AgentLane } from './AgentLane';
import { ExecutiveSynthesisCard } from './ExecutiveSynthesisCard';

export const AgentSwarmModule: React.FC = () => {
  const [agents, setAgents] = useState<AgentConfig[]>([]);
  const [mandates, setMandates] = useState<SwarmMandate[]>([]);
  const [selectedMandateId, setSelectedMandateId] = useState<string>('');
  const [mandateText, setMandateText] = useState<string>('');
  const [isRunning, setIsRunning] = useState<boolean>(false);
  const [activeLaneId, setActiveLaneId] = useState<string | null>(null);
  const [agentStates, setAgentStates] = useState<Record<string, AgentState>>({});
  const [synthesisMessage, setSynthesisMessage] = useState<string>('');
  const [deliverable, setDeliverable] = useState<ExecutiveDeliverable | null>(null);

  const abortStreamRef = useRef<(() => void) | null>(null);

  useEffect(() => {
    fetchSwarmAgents().then((agentList) => {
      setAgents(agentList);
      const initialStates: Record<string, AgentState> = {};
      agentList.forEach((ag) => {
        initialStates[ag.id] = { id: ag.id, status: 'idle', tokens: '' };
      });
      setAgentStates(initialStates);
    });

    fetchSwarmMandates().then((mandateList) => {
      setMandates(mandateList);
      if (mandateList.length > 0) {
        setSelectedMandateId(mandateList[0].id);
        setMandateText(mandateList[0].mandate);
      }
    });

    return () => {
      if (abortStreamRef.current) abortStreamRef.current();
    };
  }, []);

  const handleStartSwarm = async (mandateToRun?: string) => {
    const mandate = mandateToRun || mandateText;
    if (!mandate.trim() || isRunning) return;

    setIsRunning(true);
    setDeliverable(null);
    setSynthesisMessage('');

    // Reset agent states
    const resetStates: Record<string, AgentState> = {};
    agents.forEach((ag) => {
      resetStates[ag.id] = { id: ag.id, status: 'idle', tokens: '', lastMessage: '' };
    });
    setAgentStates(resetStates);

    const abortFn = await streamSwarmExecution(mandate, {
      onStart: () => {
        setSynthesisMessage('Iniciando coordinación de enjambre ejecutivo...');
      },
      onAgentStatus: (agentId, status, message) => {
        setActiveLaneId(agentId);
        setAgentStates((prev) => ({
          ...prev,
          [agentId]: {
            ...prev[agentId],
            status: status as any,
            lastMessage: message,
          },
        }));
      },
      onAgentToken: (agentId, token) => {
        setAgentStates((prev) => ({
          ...prev,
          [agentId]: {
            ...prev[agentId],
            status: 'working',
            tokens: (prev[agentId]?.tokens || '') + token,
          },
        }));
      },
      onAgentCompleted: (agentId, output) => {
        setAgentStates((prev) => ({
          ...prev,
          [agentId]: {
            ...prev[agentId],
            status: 'completed',
            output,
            lastMessage: 'Análisis validado con éxito',
          },
        }));
      },
      onSynthesisStart: (message) => {
        setActiveLaneId(null);
        setSynthesisMessage(message);
      },
      onSynthesisCompleted: (deliv) => {
        setDeliverable(deliv);
        setIsRunning(false);
      },
      onDone: () => {
        setIsRunning(false);
      },
      onError: (err) => {
        console.error('Swarm stream error:', err);
        setIsRunning(false);
      },
    });

    abortStreamRef.current = abortFn;
  };

  const handleStopSwarm = () => {
    if (abortStreamRef.current) {
      abortStreamRef.current();
      abortStreamRef.current = null;
    }
    setIsRunning(false);
  };

  const handleSelectMandate = (m: SwarmMandate) => {
    setSelectedMandateId(m.id);
    setMandateText(m.mandate);
    handleStartSwarm(m.mandate);
  };

  return (
    <div className="w-full max-w-[1720px] mx-auto px-6 py-6 space-y-8">
      
      {/* Title Banner */}
      <div className="glass-panel p-6 rounded-3xl border border-emerald-100 flex flex-col xl:flex-row xl:items-center justify-between gap-6 bg-gradient-to-r from-emerald-50/60 via-white to-blue-50/60">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <span className="px-3 py-1 rounded-full text-xs font-black uppercase tracking-wider bg-emerald-600 text-white shadow-sm">
              Módulo C • Orquestación Multi-Agente
            </span>
            <span className="text-sm font-semibold text-emerald-900">
              Enjambre C-Suite en Google Cloud Vertex AI
            </span>
          </div>
          <h2 className="text-3xl sm:text-4xl font-black text-slate-900 tracking-tight">
            Enjambre de Agentes Autónomos (4 Lanes)
          </h2>
          <p className="text-slate-600 text-lg font-medium max-w-3xl">
            Orquestación concurrente de 4 agentes especializados (Estrategia, Creatividad, Finanzas y Auditoría) con streaming en vivo de tokens de razonamiento y síntesis final directiva.
          </p>
        </div>

        {/* Swarm Controls */}
        <div className="flex items-center gap-3 shrink-0">
          {isRunning ? (
            <button
              onClick={handleStopSwarm}
              className="flex items-center gap-2 px-6 py-3.5 rounded-2xl bg-rose-600 hover:bg-rose-700 text-white font-bold text-base shadow-md transition-all"
            >
              <Square className="w-5 h-5 fill-current" />
              <span>Detener Enjambre</span>
            </button>
          ) : (
            <button
              onClick={() => handleStartSwarm()}
              disabled={!mandateText.trim()}
              className="flex items-center gap-2 px-6 py-3.5 rounded-2xl bg-emerald-700 hover:bg-emerald-800 text-white font-bold text-base shadow-md disabled:opacity-50 transition-all scale-100 hover:scale-105"
            >
              <Play className="w-5 h-5 fill-current" />
              <span>Lanzar Orquestación</span>
            </button>
          )}
        </div>
      </div>

      {/* Input Section & Mandates */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        {/* Left 5 cols: Mandate Config */}
        <div className="lg:col-span-5 space-y-6">
          <div className="glass-panel p-6 rounded-3xl border border-slate-200 space-y-4">
            <h3 className="text-lg font-black text-slate-900 flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-emerald-600" />
              Mandato Ejecutivo de la Junta Directiva
            </h3>

            <textarea
              rows={4}
              value={mandateText}
              onChange={(e) => setMandateText(e.target.value)}
              placeholder="Escriba el mandato o decisión estratégica de negocio a someter al enjambre..."
              className="w-full p-4 rounded-2xl border border-slate-200 bg-slate-50 text-slate-900 text-base font-medium focus:ring-2 focus:ring-emerald-500 focus:bg-white transition-all resize-none"
            />

            <div className="flex justify-end">
              <button
                onClick={() => handleStartSwarm()}
                disabled={isRunning || !mandateText.trim()}
                className="flex items-center gap-2 px-6 py-3 rounded-xl bg-emerald-700 hover:bg-emerald-800 text-white font-bold text-sm shadow-md disabled:opacity-50 transition-all"
              >
                {isRunning ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Ejecutando Enjambre...</span>
                  </>
                ) : (
                  <>
                    <Network className="w-4 h-4" />
                    <span>Iniciar Deliberación</span>
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Mandates Pre-Configured */}
          <div className="glass-panel p-6 rounded-3xl border border-slate-200 space-y-4">
            <h3 className="text-xs font-black text-slate-500 uppercase tracking-wider">
              Casos de Negocio & Mandatos Pre-Cargados
            </h3>
            <div className="space-y-3">
              {mandates.map((m) => (
                <button
                  key={m.id}
                  onClick={() => handleSelectMandate(m)}
                  className={`w-full text-left p-4 rounded-2xl border transition-all duration-200 flex items-center justify-between gap-3 ${
                    selectedMandateId === m.id
                      ? 'bg-emerald-50/80 border-emerald-300 shadow-sm ring-1 ring-emerald-300'
                      : 'bg-white hover:bg-slate-50 border-slate-200'
                  }`}
                >
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-black uppercase text-emerald-700 bg-emerald-100 px-2 py-0.5 rounded">
                        {m.complexity}
                      </span>
                      <span className="text-xs font-semibold text-slate-500">4 Lanes Activos</span>
                    </div>
                    <p className="text-base font-bold text-slate-900 leading-snug">
                      {m.title}
                    </p>
                  </div>
                  <ArrowRight className="w-5 h-5 text-slate-400 shrink-0" />
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Right 7 cols: Swarm Status & Active Overview */}
        <div className="lg:col-span-7 space-y-6">
          <div className="glass-panel p-6 rounded-3xl border border-slate-200 space-y-4 bg-gradient-to-br from-white via-slate-50 to-emerald-50/20">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Activity className="w-5 h-5 text-emerald-600 animate-pulse" />
                <h4 className="text-base font-black text-slate-900">
                  Estado de la Sesión Multi-Agente
                </h4>
              </div>
              <span className={`px-3 py-1 rounded-full text-xs font-bold ${
                isRunning
                  ? 'bg-emerald-100 text-emerald-800 border border-emerald-300 animate-pulse'
                  : deliverable
                  ? 'bg-blue-100 text-blue-800 border border-blue-300'
                  : 'bg-slate-100 text-slate-600'
              }`}>
                {isRunning ? 'Deliberación en Tiempo Real' : deliverable ? 'Resolución Emitida' : 'Listo para Lanzamiento'}
              </span>
            </div>

            {synthesisMessage && (
              <div className="p-4 rounded-2xl bg-white border border-emerald-200 text-slate-800 font-semibold text-sm sm:text-base shadow-sm flex items-center gap-2.5">
                <Loader2 className="w-5 h-5 text-emerald-600 animate-spin shrink-0" />
                <span>{synthesisMessage}</span>
              </div>
            )}

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-2">
              {agents.map((ag) => {
                const st = agentStates[ag.id];
                return (
                  <div key={ag.id} className="p-3 rounded-xl bg-white border border-slate-200 text-center shadow-xs">
                    <span className="text-xs font-bold text-slate-500 block truncate">{ag.name.replace('Agente de ', '')}</span>
                    <span className={`text-xs font-black uppercase mt-1 inline-block px-2 py-0.5 rounded-full ${
                      st?.status === 'completed'
                        ? 'bg-emerald-100 text-emerald-700'
                        : st?.status === 'working' || st?.status === 'thinking'
                        ? 'bg-amber-100 text-amber-700 animate-pulse'
                        : 'bg-slate-100 text-slate-400'
                    }`}>
                      {st?.status || 'idle'}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

      </div>

      {/* Visual 4-Lane Agent Orchestration Grid (Big Screen 100") */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-xl font-black text-slate-900 flex items-center gap-2">
            <Users className="w-5 h-5 text-emerald-600" />
            Flujo de Razonamiento Concurrente (4 Lanes Directivos)
          </h3>
          <span className="text-xs font-bold text-slate-500">
            Orquestado con Gemini 3.7 / 2.5
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-5">
          {agents.map((ag) => (
            <AgentLane
              key={ag.id}
              config={ag}
              state={agentStates[ag.id] || { id: ag.id, status: 'idle', tokens: '' }}
              isActive={activeLaneId === ag.id}
            />
          ))}
        </div>
      </div>

      {/* Final Executive Synthesis Card */}
      {deliverable && (
        <ExecutiveSynthesisCard deliverable={deliverable} />
      )}

    </div>
  );
};
