import React from 'react';
import { Brain, Sparkles } from 'lucide-react';
import { clsx } from 'clsx';

interface MacroPerspectiveCardProps {
  children: React.ReactNode;
  theme?: 'light' | 'dark';
}

export const MacroPerspectiveCard: React.FC<MacroPerspectiveCardProps> = ({ children, theme = 'dark' }) => {
  const isDark = theme === 'dark';

  return (
    <div className={clsx(
      "relative overflow-hidden rounded-2xl border transition-all duration-500 animate-in fade-in slide-in-from-bottom-4",
      isDark 
        ? "bg-gradient-to-br from-blue-900/20 via-black/40 to-cyan-900/20 border-blue-500/30 shadow-[0_0_30px_rgba(56,189,248,0.1)]"
        : "bg-gradient-to-br from-blue-50 via-white to-cyan-50 border-blue-200 shadow-xl"
    )}>
      {/* Background Decorative Glow */}
      <div className="absolute top-0 right-0 -mr-16 -mt-16 w-48 h-48 bg-blue-500/10 blur-[60px] rounded-full" />
      <div className="absolute bottom-0 left-0 -ml-16 -mb-16 w-48 h-48 bg-cyan-500/10 blur-[60px] rounded-full" />

      {/* Header Badge */}
      <div className={clsx(
        "flex items-center gap-2 px-4 py-2 border-b",
        isDark ? "border-white/5 bg-white/5" : "border-blue-100 bg-blue-50/50"
      )}>
        <div className="flex -space-x-1">
          <Brain size={14} className="text-blue-400" />
          <Sparkles size={10} className="text-cyan-400 animate-pulse" />
        </div>
        <span className={clsx(
          "text-[10px] font-black uppercase tracking-[0.2em]",
          isDark ? "text-blue-400" : "text-blue-600"
        )}>
          Strategist Perspective
        </span>
      </div>

      {/* Content */}
      <div className="p-4 relative z-10">
        {children}
      </div>

      {/* Footer Decoration */}
      <div className="absolute bottom-1 right-3 opacity-20 pointer-events-none">
        <Sparkles size={12} className={isDark ? "text-blue-400" : "text-blue-600"} />
      </div>
    </div>
  );
};
