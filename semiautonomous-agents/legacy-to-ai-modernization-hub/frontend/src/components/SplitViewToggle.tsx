import React from 'react';
import { ArrowRight, Sparkles, Clock, Zap, FileSpreadsheet } from 'lucide-react';

interface SplitViewToggleProps {
  currentView: 'legacy' | 'refactor' | 'agent';
  onViewChange: (view: 'legacy' | 'refactor' | 'agent') => void;
  onOpenRefactorModal: () => void;
}

export const SplitViewToggle: React.FC<SplitViewToggleProps> = ({
  currentView,
  onViewChange,
  onOpenRefactorModal,
}) => {
  return (
    <div className="bg-slate-900/60 border-b border-slate-800 px-6 py-3">
      <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
        {/* Left summary pill */}
        <div className="flex items-center gap-3">
          <span className="text-xs font-mono font-semibold text-slate-400">
            SHOWCASE TIMELINE:
          </span>
          <div className="flex items-center gap-2">
            <button
              onClick={() => onViewChange('legacy')}
              className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium border transition-all ${
                currentView === 'legacy'
                  ? 'bg-amber-950/40 text-amber-300 border-amber-500/50 shadow-sm'
                  : 'bg-slate-800/50 text-slate-400 border-slate-700 hover:text-slate-200'
              }`}
            >
              <FileSpreadsheet className="h-3.5 w-3.5 text-amber-400" />
              <span>Act I: 2015 Legacy ERP (Rigid & Paginated)</span>
            </button>

            <ArrowRight className="h-3.5 w-3.5 text-slate-600 hidden md:inline" />

            <button
              onClick={onOpenRefactorModal}
              className="flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium border bg-indigo-950/40 text-indigo-300 border-indigo-500/50 hover:bg-indigo-900/50 shadow-sm transition-all"
            >
              <Sparkles className="h-3.5 w-3.5 text-indigo-400 animate-spin" style={{ animationDuration: '6s' }} />
              <span>Act II: Antigravity Refactor (12s Live Synthesis)</span>
            </button>

            <ArrowRight className="h-3.5 w-3.5 text-slate-600 hidden md:inline" />

            <button
              onClick={() => onViewChange('agent')}
              className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium border transition-all ${
                currentView === 'agent'
                  ? 'bg-cyan-950/40 text-cyan-300 border-cyan-500/50 shadow-sm'
                  : 'bg-slate-800/50 text-slate-400 border-slate-700 hover:text-slate-200'
              }`}
            >
              <Zap className="h-3.5 w-3.5 text-cyan-400" />
              <span>Act III: 2026 Agent Canvas (50ms Reactive)</span>
            </button>
          </div>
        </div>

        {/* Right Metric Comparison */}
        <div className="flex items-center gap-4 text-xs font-mono">
          <div className="flex items-center gap-1.5 text-amber-400/90 bg-amber-950/30 px-2.5 py-1 rounded border border-amber-800/40">
            <Clock className="h-3.5 w-3.5" />
            <span>Legacy: ~4,200 ms</span>
          </div>
          <span className="text-slate-600">&rarr;</span>
          <div className="flex items-center gap-1.5 text-emerald-400 bg-emerald-950/30 px-2.5 py-1 rounded border border-emerald-800/40">
            <Zap className="h-3.5 w-3.5" />
            <span>Agent-Native: &lt;50 ms (93x Boost)</span>
          </div>
        </div>
      </div>
    </div>
  );
};
