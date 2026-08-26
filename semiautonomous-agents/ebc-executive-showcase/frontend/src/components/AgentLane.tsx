import React from 'react';
import { AgentConfig, AgentState } from '../types';
import { Target, Sparkles, TrendingUp, ShieldCheck, Loader2, CheckCircle2, CircleDot } from 'lucide-react';

interface AgentLaneProps {
  config: AgentConfig;
  state: AgentState;
  isActive: boolean;
}

export const AgentLane: React.FC<AgentLaneProps> = ({ config, state, isActive }) => {
  const getIcon = () => {
    switch (config.avatar) {
      case 'Target':
        return <Target className="w-5 h-5" />;
      case 'Sparkles':
        return <Sparkles className="w-5 h-5" />;
      case 'TrendingUp':
        return <TrendingUp className="w-5 h-5" />;
      case 'ShieldCheck':
        return <ShieldCheck className="w-5 h-5" />;
      default:
        return <CircleDot className="w-5 h-5" />;
    }
  };

  const getBorderColor = () => {
    if (isActive || state.status === 'thinking' || state.status === 'working') {
      switch (config.color) {
        case 'indigo': return 'border-indigo-500 ring-2 ring-indigo-200 shadow-lg';
        case 'fuchsia': return 'border-fuchsia-500 ring-2 ring-fuchsia-200 shadow-lg';
        case 'emerald': return 'border-emerald-500 ring-2 ring-emerald-200 shadow-lg';
        case 'blue': return 'border-blue-500 ring-2 ring-blue-200 shadow-lg';
      }
    }
    if (state.status === 'completed') {
      return 'border-slate-300 bg-slate-50/70 shadow-sm';
    }
    return 'border-slate-200 bg-white shadow-sm';
  };

  const getBadgeColor = () => {
    switch (config.color) {
      case 'indigo': return 'bg-indigo-50 text-indigo-700 border-indigo-200';
      case 'fuchsia': return 'bg-fuchsia-50 text-fuchsia-700 border-fuchsia-200';
      case 'emerald': return 'bg-emerald-50 text-emerald-700 border-emerald-200';
      case 'blue': return 'bg-blue-50 text-blue-700 border-blue-200';
    }
  };

  return (
    <div className={`glass-panel p-5 rounded-3xl border transition-all duration-300 flex flex-col justify-between min-h-[420px] ${getBorderColor()}`}>
      
      {/* Top Header */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className={`p-2 rounded-xl border ${getBadgeColor()}`}>
              {getIcon()}
            </div>
            <div>
              <h4 className="text-base font-black text-slate-900 leading-tight">
                {config.name}
              </h4>
              <span className="text-xs font-bold text-slate-500 block">
                {config.role}
              </span>
            </div>
          </div>

          {/* Status Indicator */}
          <div>
            {state.status === 'thinking' && (
              <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-amber-50 text-amber-700 border border-amber-200 flex items-center gap-1 animate-pulse">
                <Loader2 className="w-3.5 h-3.5 animate-spin" /> Razonando
              </span>
            )}
            {state.status === 'working' && (
              <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-blue-50 text-blue-700 border border-blue-200 flex items-center gap-1 animate-pulse">
                <CircleDot className="w-3.5 h-3.5 animate-spin" /> Escribiendo
              </span>
            )}
            {state.status === 'completed' && (
              <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-emerald-50 text-emerald-700 border border-emerald-200 flex items-center gap-1">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" /> Completado
              </span>
            )}
            {state.status === 'idle' && (
              <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-slate-100 text-slate-500 border border-slate-200">
                En Espera
              </span>
            )}
          </div>
        </div>

        {/* Live Status Message */}
        {state.lastMessage && (
          <div className="text-xs font-semibold text-slate-600 bg-slate-100/90 px-3 py-1.5 rounded-lg">
            {state.lastMessage}
          </div>
        )}
      </div>

      {/* Center Token Reasoning Stream */}
      <div className="flex-1 my-3 p-3.5 rounded-2xl bg-slate-50/90 border border-slate-200 text-xs sm:text-sm font-mono text-slate-800 overflow-y-auto max-h-[220px] leading-relaxed whitespace-pre-wrap">
        {state.tokens ? (
          <div>{state.tokens}</div>
        ) : (
          <div className="text-slate-400 italic text-xs">
            Esperando turno en la cadena de razonamiento...
          </div>
        )}
      </div>

      {/* Bottom Completion Summary */}
      <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500 font-medium">
        <span>Gobernanza C-Suite</span>
        <span className="font-bold text-slate-700">Vertex AI Agent</span>
      </div>

    </div>
  );
};
