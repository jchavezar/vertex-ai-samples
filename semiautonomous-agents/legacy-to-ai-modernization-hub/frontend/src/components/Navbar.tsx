import React from 'react';
import { Sparkles, Database, Zap, Cpu } from 'lucide-react';

interface NavbarProps {
  currentView: 'legacy' | 'refactor' | 'agent';
  onViewChange: (view: 'legacy' | 'refactor' | 'agent') => void;
  onOpenRefactorModal: () => void;
  latencyMs: number;
}

export const Navbar: React.FC<NavbarProps> = ({
  currentView,
  onViewChange,
  onOpenRefactorModal,
  latencyMs,
}) => {
  return (
    <header className="sticky top-0 z-40 bg-[#090d16]/90 backdrop-blur-md border-b border-cyan-500/20 px-6 py-3.5">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        {/* Left Branding */}
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-cyan-500 via-blue-600 to-violet-600 p-0.5 shadow-lg shadow-cyan-500/20 flex items-center justify-center">
            <div className="h-full w-full bg-[#090d16] rounded-[10px] flex items-center justify-center">
              <Zap className="h-5 w-5 text-cyan-400 animate-pulse" />
            </div>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-extrabold tracking-wider text-base bg-gradient-to-r from-cyan-400 via-sky-300 to-indigo-300 bg-clip-text text-transparent">
                ANTIGRAVITY // EBC
              </span>
              <span className="px-2 py-0.5 text-[10px] font-mono font-bold bg-cyan-950/80 text-cyan-400 border border-cyan-800/60 rounded">
                v2026.4
              </span>
            </div>
            <p className="text-xs text-slate-400 font-medium">
              Legacy to AI-Native Modernization Hub
            </p>
          </div>
        </div>

        {/* Center View Selector */}
        <div className="flex items-center bg-slate-900/90 border border-slate-800 p-1 rounded-xl">
          <button
            onClick={() => onViewChange('legacy')}
            className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              currentView === 'legacy'
                ? 'bg-slate-700 text-amber-300 shadow'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Database className="h-3.5 w-3.5 text-amber-400" />
            <span>2015 Legacy ERP</span>
          </button>

          <button
            onClick={() => onViewChange('agent')}
            className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              currentView === 'agent'
                ? 'bg-gradient-to-r from-cyan-600 to-blue-600 text-white shadow-lg shadow-cyan-500/25'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Cpu className="h-3.5 w-3.5 text-cyan-300" />
            <span>2026 Agent Canvas</span>
          </button>
        </div>

        {/* Right CTA & Latency Meter */}
        <div className="flex items-center gap-4">
          <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-900/80 border border-slate-800 text-xs font-mono">
            <span className="text-slate-400">Response:</span>
            <span className={`font-bold ${currentView === 'legacy' ? 'text-amber-400' : 'text-emerald-400'}`}>
              {latencyMs > 0 ? `${latencyMs.toFixed(0)} ms` : '50 ms'}
            </span>
          </div>

          <button
            onClick={onOpenRefactorModal}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gradient-to-r from-cyan-500 to-violet-600 hover:from-cyan-400 hover:to-violet-500 text-slate-950 font-bold text-xs shadow-lg shadow-cyan-500/20 transition-all transform hover:scale-[1.02] active:scale-[0.98]"
          >
            <Sparkles className="h-4 w-4" />
            <span>Trigger Autonomous Refactor</span>
          </button>
        </div>
      </div>
    </header>
  );
};
