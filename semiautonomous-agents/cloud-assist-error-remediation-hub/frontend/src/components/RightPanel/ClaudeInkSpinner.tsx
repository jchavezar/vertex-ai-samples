import React from 'react';
import { Sparkles, Cpu } from 'lucide-react';

export const ClaudeInkSpinner: React.FC = () => {
  return (
    <div className="flex flex-col items-start p-3.5 rounded-2xl bg-slate-950/90 border border-purple-500/40 shadow-xl shadow-purple-500/10 space-y-2.5 max-w-[290px]">
      {/* Claude Code "Ink" Wave Bar Graphic */}
      <div className="flex items-center space-x-1.5 h-5">
        {[0, 1, 2, 3, 4, 5, 6, 7].map((bar) => (
          <div
            key={bar}
            className="w-1 bg-gradient-to-t from-purple-600 via-cyan-400 to-emerald-400 rounded-full animate-ink-wave shadow-sm shadow-cyan-400/40"
            style={{
              animationDelay: `${bar * 0.12}s`,
              height: '18px'
            }}
          ></div>
        ))}
      </div>

      <div className="flex items-center space-x-2 text-[11px] font-mono font-bold text-cyan-300">
        <Sparkles className="w-3.5 h-3.5 text-cyan-400 animate-spin flex-shrink-0" />
        <span className="animate-pulse">gemini-3.5-flash ADK Tool Router...</span>
      </div>
    </div>
  );
};
