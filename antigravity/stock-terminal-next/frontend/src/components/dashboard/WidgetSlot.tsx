import React, { useState } from 'react';
import { Loader, X, Sparkles } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface WidgetSlotProps {
  section: string;
  override?: {
    loading: boolean;
    content: string | null;
    model?: string;
  };
  isAiMode: boolean;
  originalComponent: React.ReactNode;
  onGenerate: (section: string) => void;
  tickers: string[];
  variant?: 'card' | 'clean';
}

export const WidgetSlot: React.FC<WidgetSlotProps> = ({
  section,
  override,
  isAiMode,
  originalComponent,
  onGenerate,
  tickers,
  variant = 'card'
}) => {
  const [isModalOpen, setIsModalOpen] = useState(false);

  // Helper to determine base classes based on variant
  const getContainerClass = (baseClass: string) => {
    if (variant === 'clean') {
      return baseClass.replace('card', 'rounded-xl border border-white/5 bg-white/5 p-4'); // Clean look for grid items
    }
    return baseClass;
  };

  // 1. AI Content State
  if (override && (override.loading || override.content)) {
    if (override.loading) {
      return (
        <div className={getContainerClass("min-h-[220px] flex flex-col p-6 bg-[var(--bg-card)] border border-[var(--border-subtle)]")}>
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-2">
              <Sparkles size={12} className="text-[var(--text-primary)]" />
              <span className="font-black text-[9px] text-[var(--text-primary)] uppercase tracking-[0.25em]">{section} Analysis</span>
            </div>
            <Loader className="animate-spin text-[var(--text-muted)]" size={12} />
          </div>

          <div className="space-y-3">
            <div className="h-2 rounded bg-[var(--border-subtle)]/50 animate-pulse w-[90%]" />
            <div className="h-2 rounded bg-[var(--border-subtle)]/50 animate-pulse w-full" />
            <div className="h-2 rounded bg-[var(--border-subtle)]/50 animate-pulse w-[85%]" />
            <div className="h-2 rounded bg-[var(--border-subtle)]/50 animate-pulse w-[95%] mt-4" />
            <div className="h-2 rounded bg-[var(--border-subtle)]/50 animate-pulse w-[70%]" />
          </div>

          <div className="mt-auto text-[8px] text-[var(--text-muted)] font-black uppercase tracking-widest text-center opacity-50">
            INTELLIGENCE LINK ACTIVE
          </div>
        </div>
      );
    }



    const cleanFullContent = override.content?.replace(/[\[\/?WIDGET:[^\]\]]+/g, '').trim() || '';
    const isLongContent = cleanFullContent.length > 350;

    return (
      <>
        <div
          className={getContainerClass("min-h-[220px] max-h-[300px] overflow-hidden flex flex-col cursor-pointer transition-all duration-300 hover:bg-[var(--bg-panel)] bg-[var(--bg-card)] border border-[var(--border-subtle)] group p-6")}
          onClick={() => setIsModalOpen(true)}
        >
          <div className="flex justify-between items-center mb-4">
            <div className="flex flex-col gap-1">
              <div className="flex items-center gap-2">
                <Sparkles size={12} className="text-[var(--text-primary)]" />
                <span className="font-black text-[9px] text-[var(--text-primary)] uppercase tracking-[0.25em]">{section} Analysis</span>
              </div>
              {override.model && (
                <div className="text-[8px] text-[var(--text-muted)] font-bold tracking-widest uppercase ml-5 opacity-60">
                  {override.model}
                </div>
              )}
            </div>
            <div className="bg-[var(--text-primary)] text-[var(--bg-app)] px-2 py-0.5 rounded text-[8px] font-black uppercase tracking-widest opacity-0 group-hover:opacity-100 transition-all">
              EXPAND
            </div>
          </div>
          <div className="prose prose-invert prose-xs max-w-none text-[12px] leading-relaxed text-[var(--text-secondary)] font-medium tracking-tight">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{cleanFullContent}</ReactMarkdown>
          </div>
          {isLongContent && (
            <div className="mt-auto pt-4 text-center text-[8px] text-[var(--text-muted)] font-black border-t border-[var(--border-subtle)]/50 uppercase tracking-[0.2em] group-hover:text-[var(--text-primary)] transition-colors">
              CLICK TO REVEAL FULL BRIEF
            </div>
          )}
        </div>

        {/* Full View Modal */}
        {isModalOpen && (
          <div className="fixed inset-0 bg-black/80 backdrop-blur-md flex items-center justify-center z-[10000] animate-in fade-in duration-200" onClick={() => setIsModalOpen(false)}>
            <div className="bg-[var(--bg-card)] w-[95%] max-w-[900px] max-h-[90vh] rounded-2xl flex flex-col shadow-2xl overflow-hidden border border-[var(--border-subtle)] animate-in zoom-in-95 duration-200" onClick={e => e.stopPropagation()}>
              <div className="p-4 border-b border-[var(--border-subtle)] flex items-center justify-between bg-[var(--bg-app)]">
                <div className="flex items-center gap-3">
                  <Sparkles size={16} className="text-[var(--text-primary)]" />
                  <h2 className="text-[12px] font-black uppercase tracking-[0.3em] text-[var(--text-primary)]">{section} - AGENT DEBRIEF</h2>
                </div>
                <button onClick={() => setIsModalOpen(false)} className="p-2 hover:bg-white/5 rounded-full transition-colors">
                  <X size={20} className="text-[var(--text-muted)] hover:text-[var(--text-primary)]" />
                </button>
              </div>
              <div className="p-10 overflow-y-auto text-[14px] leading-relaxed text-[var(--text-primary)] prose prose-invert max-w-none selection:bg-white/10 no-scrollbar">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>{cleanFullContent}</ReactMarkdown>
              </div>
            </div>
          </div>
        )}
      </>
    );
  }

  // 2. AI Mode State (Empty State with Center Action)
  if (isAiMode) {
    const isComparison = tickers && tickers.length > 1;
    const buttonText = isComparison
      ? `Compare ${section}`
      : `Generate ${section} Analysis`;

    return (
      <div className="h-full w-full flex flex-col items-center justify-center p-8 bg-[var(--bg-app)]/40 border border-dashed border-[var(--border-subtle)] group transition-all duration-500 hover:bg-[var(--bg-app)]/60">
        <div className="flex flex-col items-center gap-5">
          <div className="w-14 h-14 rounded-full bg-[var(--text-primary)]/5 flex items-center justify-center border border-[var(--text-primary)]/10 group-hover:bg-[var(--brand)]/10 group-hover:border-[var(--brand)]/30 group-hover:scale-110 transition-all duration-500 shadow-inner">
            <Sparkles size={24} className="text-[var(--text-muted)] group-hover:text-[var(--brand)] transition-colors duration-500" />
          </div>

          <div className="text-center space-y-1.5">
            <h3 className="text-[11px] font-black uppercase tracking-[0.4em] text-[var(--text-primary)] translate-x-[0.2em]">{section}</h3>
            <p className="text-[9px] text-[var(--text-muted)] font-bold uppercase tracking-[0.2em] max-w-[180px] mx-auto opacity-50 group-hover:opacity-80 transition-opacity">
              Awaiting Agent Synthesis
            </p>
          </div>

          <button
            onClick={() => onGenerate(section)}
            className="mt-2 px-8 py-3 bg-[var(--text-primary)] text-[var(--bg-app)] text-[10px] font-black uppercase tracking-[0.25em] rounded-md hover:bg-[var(--brand)] hover:text-white transition-all shadow-xl hover:shadow-[var(--brand)]/30 active:scale-95 flex items-center gap-2"
          >
            <Sparkles size={11} />
            {buttonText}
          </button>
        </div>

        {/* Background Decorator */}
        <div className="absolute top-3 right-3 text-[8px] font-black text-[var(--text-muted)] opacity-20 uppercase tracking-widest pointer-events-none">
          Neural Slot {tickers[0]}
        </div>
      </div>
    );
  }

  // 3. Fallback: Standard Original Component
  return <>{originalComponent}</>;
};
