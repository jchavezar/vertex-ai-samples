import React from 'react';
import { ShieldAlert, Sparkles, Activity, Cloud, RefreshCw } from 'lucide-react';

interface HeaderProps {
  totalErrors: number;
  onRefreshAll: () => void;
  isLoading: boolean;
}

export const Header: React.FC<HeaderProps> = ({ totalErrors, onRefreshAll, isLoading }) => {
  return (
    <header className="h-16 border-b border-slate-800/80 bg-[#0a0d14]/90 backdrop-blur-md sticky top-0 z-50 px-6 flex items-center justify-between">
      {/* Left Branding */}
      <div className="flex items-center space-x-3">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-600 via-cyan-500 to-purple-600 flex items-center justify-center shadow-lg shadow-cyan-500/20 ring-1 ring-white/20">
          <Cloud className="w-5 h-5 text-white" />
        </div>
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="font-bold text-base tracking-tight text-white">Google Cloud</h1>
            <span className="text-xs px-2 py-0.5 rounded-full bg-gradient-to-r from-cyan-500/20 to-purple-500/20 border border-cyan-500/40 text-cyan-300 font-medium flex items-center gap-1">
              <Sparkles className="w-3 h-3 text-cyan-400" />
              Gemini Cloud Assist
            </span>
          </div>
          <p className="text-xs text-slate-400 font-medium">Agentic Error Remediation & Proactive Self-Healing Hub</p>
        </div>
      </div>

      {/* Center Status Banner */}
      <div className="hidden md:flex items-center space-x-4 bg-slate-900/80 border border-slate-800 px-4 py-1.5 rounded-full shadow-inner">
        <div className="flex items-center space-x-2">
          <span className="relative flex h-2.5 w-2.5">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
          </span>
          <span className="text-xs font-semibold text-slate-200">GCP Project: <code className="text-cyan-400 font-mono">vtxdemos</code></span>
        </div>
        <span className="text-slate-600">|</span>
        <div className="flex items-center space-x-1.5">
          <ShieldAlert className="w-3.5 h-3.5 text-rose-400" />
          <span className="text-xs text-slate-300">
            Active Issues: <strong className="text-rose-400 font-semibold">{totalErrors}</strong>
          </span>
        </div>
      </div>

      {/* Right Controls */}
      <div className="flex items-center space-x-3">
        <button
          onClick={onRefreshAll}
          disabled={isLoading}
          className="px-3.5 py-2 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-700/80 hover:border-cyan-500/50 text-xs font-medium text-slate-200 flex items-center gap-2 transition-all duration-200 shadow-sm"
        >
          <RefreshCw className={`w-3.5 h-3.5 text-cyan-400 ${isLoading ? 'animate-spin' : ''}`} />
          <span>Refresh Telemetry</span>
        </button>
      </div>
    </header>
  );
};
