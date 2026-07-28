import React from 'react';
import { ShieldAlert, Sparkles, Activity, Cloud, RefreshCw, Zap } from 'lucide-react';

interface HeaderProps {
  totalErrors: number;
  onRefreshAll: () => void;
  isLoading: boolean;
  activeRemediationMessage?: string | null;
  onSelectActiveRemediation?: () => void;
  isLightMode?: boolean;
}

export const Header: React.FC<HeaderProps> = ({
  totalErrors,
  onRefreshAll,
  isLoading,
  activeRemediationMessage,
  onSelectActiveRemediation,
  isLightMode = false
}) => {
  return (
    <header className={`h-16 border-b sticky top-0 z-50 px-6 flex items-center justify-between transition-colors duration-300 ${
      isLightMode
        ? 'bg-white/95 border-slate-200 text-slate-900 shadow-sm'
        : 'bg-[#0a0d14]/90 border-slate-800/80 text-white backdrop-blur-md'
    }`}>
      {/* Left Branding */}
      <div className="flex items-center space-x-3">
        <div className={`w-10 h-10 rounded-xl flex items-center justify-center shadow-lg ring-1 ${
          isLightMode
            ? 'bg-slate-950 text-white ring-slate-900 shadow-slate-900/20'
            : 'bg-gradient-to-br from-blue-600 via-cyan-500 to-purple-600 ring-white/20 shadow-cyan-500/20'
        }`}>
          <Cloud className="w-5 h-5 text-white" />
        </div>
        <div>
          <div className="flex items-center space-x-2">
            <h1 className={`font-bold text-base tracking-tight ${isLightMode ? 'text-slate-950 font-mono' : 'text-white'}`}>
              Google Cloud
            </h1>
            <span className={`text-xs px-2.5 py-0.5 rounded-full border font-medium flex items-center gap-1 ${
              isLightMode
                ? 'bg-slate-100 border-slate-300 text-slate-900 font-mono font-bold'
                : 'bg-gradient-to-r from-cyan-500/20 to-purple-500/20 border-cyan-500/40 text-cyan-300'
            }`}>
              <Sparkles className={`w-3 h-3 ${isLightMode ? 'text-slate-900' : 'text-cyan-400'}`} />
              Gemini Cloud Assist
            </span>
          </div>
          <p className={`text-xs font-medium ${isLightMode ? 'text-slate-600 font-mono' : 'text-slate-400'}`}>
            Agentic Error Remediation & Proactive Self-Healing Hub
          </p>
        </div>
      </div>

      {/* Center Status Banner */}
      <div className={`hidden lg:flex items-center space-x-4 px-4 py-1.5 rounded-full shadow-inner border ${
        isLightMode
          ? 'bg-slate-100 border-slate-200 text-slate-800'
          : 'bg-slate-900/80 border-slate-800 text-slate-200'
      }`}>
        <div className="flex items-center space-x-2">
          <span className="relative flex h-2.5 w-2.5">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
          </span>
          <span className="text-xs font-semibold">
            GCP Project: <code className={isLightMode ? 'text-slate-950 font-mono font-bold' : 'text-cyan-400 font-mono'}>vtxdemos</code>
          </span>
        </div>
        <span className={isLightMode ? 'text-slate-300' : 'text-slate-600'}>|</span>
        <div className="flex items-center space-x-1.5">
          <ShieldAlert className="w-3.5 h-3.5 text-rose-500" />
          <span className="text-xs">
            Active Issues: <strong className="text-rose-600 font-bold">{totalErrors}</strong>
          </span>
        </div>
      </div>

      {/* Right Controls + Active Remediation Badge */}
      <div className="flex items-center space-x-3">
        {activeRemediationMessage && (
          <button
            onClick={onSelectActiveRemediation}
            className="px-3.5 py-1.5 rounded-full bg-gradient-to-r from-amber-500/20 to-emerald-500/20 border border-emerald-500/50 text-emerald-300 text-xs font-bold flex items-center gap-2 animate-pulse shadow-lg shadow-emerald-500/10 cursor-pointer hover:border-emerald-400 transition-all"
            title="Click to view live background auto-healing progress"
          >
            <Zap className="w-3.5 h-3.5 fill-amber-300 text-amber-300" />
            <span>{activeRemediationMessage}</span>
          </button>
        )}

        <button
          onClick={onRefreshAll}
          disabled={isLoading}
          className={`px-3.5 py-2 rounded-lg border text-xs font-medium flex items-center gap-2 transition-all duration-200 shadow-sm cursor-pointer ${
            isLightMode
              ? 'bg-slate-950 hover:bg-slate-800 text-white border-slate-900'
              : 'bg-slate-900 hover:bg-slate-800 border-slate-700/80 text-slate-200'
          }`}
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''} ${isLightMode ? 'text-white' : 'text-cyan-400'}`} />
          <span>Refresh Telemetry</span>
        </button>
      </div>
    </header>
  );
};
