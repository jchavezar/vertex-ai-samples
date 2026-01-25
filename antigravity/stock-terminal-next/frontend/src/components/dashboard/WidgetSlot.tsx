import React, { useState } from 'react';
import { Sparkles, Loader, Maximize2, X, Bot } from 'lucide-react';
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
}

export const WidgetSlot: React.FC<WidgetSlotProps> = ({
  section,
  override,
  isAiMode,
  originalComponent,
  onGenerate,
  tickers
}) => {
  const [isModalOpen, setIsModalOpen] = useState(false);

  // 1. AI Content State
  if (override && (override.loading || override.content)) {
    if (override.loading) {
      return (
        <div className="card min-h-[200px] flex flex-col p-4 shadow-[0_0_15px_var(--brand-light)] border-[var(--brand)]">
          <div className="flex items-center gap-2 mb-4 text-[var(--text-secondary)] uppercase tracking-wide text-[13px]">
            <div className="flex items-center gap-2">
              <Sparkles size={14} className="text-[var(--brand)] animate-pulse" />
              <span className="font-semibold">{section} Analysis</span>
            </div>
            <Loader className="animate-spin text-[var(--text-muted)]" size={12} />
          </div>

          <div className="h-3 rounded bg-gradient-to-r from-[var(--border-light)] via-[var(--border)] to-[var(--border-light)] bg-[length:800px_104px] animate-[shimmer_1.5s_infinite_linear] w-[90%] mb-2" />
          <div className="h-3 rounded bg-gradient-to-r from-[var(--border-light)] via-[var(--border)] to-[var(--border-light)] bg-[length:800px_104px] animate-[shimmer_1.5s_infinite_linear] w-full mb-2" />
          <div className="h-3 rounded bg-gradient-to-r from-[var(--border-light)] via-[var(--border)] to-[var(--border-light)] bg-[length:800px_104px] animate-[shimmer_1.5s_infinite_linear] w-[85%] mb-2" />
          <div className="h-3 rounded bg-gradient-to-r from-[var(--border-light)] via-[var(--border)] to-[var(--border-light)] bg-[length:800px_104px] animate-[shimmer_1.5s_infinite_linear] w-[95%] mt-3 mb-2" />
          <div className="h-3 rounded bg-gradient-to-r from-[var(--border-light)] via-[var(--border)] to-[var(--border-light)] bg-[length:800px_104px] animate-[shimmer_1.5s_infinite_linear] w-[70%]" />

          <div className="mt-auto text-[10px] text-[var(--text-muted)] italic text-center">
            Powering up Gemini analysts...
          </div>
        </div>
      );
    }

    // Extract only the first paragraph or block of text for the concise summary
    const getConciseSummary = (content: string) => {
      if (!content) return "";
      // Remove the specific widget tags if they leaked into the content
      const cleanContent = content.replace(/[\[\/?WIDGET:[^\]\]]+/g, '').trim();
      const lines = cleanContent.split('\n');
      const paragraph = [];
      for (const line of lines) {
        const trimmed = line.trim();
        if (!trimmed) {
          if (paragraph.length > 0) break;
          continue;
        }
        if (trimmed.startsWith('|') || trimmed.startsWith('-')) continue;
        paragraph.push(line);
        if (paragraph.length > 3) break;
      }
      return paragraph.join('\n');
    };

    const cleanFullContent = override.content?.replace(/[\[\/?WIDGET:[^\]\]]+/g, '').trim() || '';
    const summaryContent = getConciseSummary(cleanFullContent) || cleanFullContent.substring(0, 150) + '...';
    const isLongContent = cleanFullContent.length > 350;

    return (
      <>
        <div
          className="card min-h-[200px] max-h-[300px] overflow-hidden flex flex-col cursor-pointer transition-all duration-200 hover:border-[var(--brand)] hover:shadow-lg shadow-[0_0_15px_var(--brand-light)] border-[var(--brand)] group"
          onClick={() => setIsModalOpen(true)}
        >
          <div className="flex justify-between items-center gap-2 mb-2">
            <div className="flex items-center gap-2">
              <div className="flex flex-col">
                <div className="flex items-center gap-2">
                  <Sparkles size={12} className="text-[var(--brand)]" />
                  <span className="font-extrabold text-[11px] text-[var(--text-primary)] uppercase tracking-wide">{section} Analysis</span>
                </div>
                {override.model && (
                  <div className="flex items-center gap-1 text-[9px] text-[var(--text-muted)] ml-5 font-semibold">
                    <Bot size={10} />
                    {override.model}
                  </div>
                )}
              </div>
            </div>
            <div className="flex items-center gap-1 text-[10px] text-[var(--brand)] bg-[var(--brand-light)] px-1.5 py-0.5 rounded opacity-0 group-hover:opacity-100 transition-opacity">
              <Maximize2 size={10} />
              <span>Full Analysis</span>
            </div>
          </div>
          <div className="prose prose-invert prose-xs max-w-none text-[11px] leading-relaxed text-[var(--text-secondary)]">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{summaryContent}</ReactMarkdown>
          </div>
          {isLongContent && (
            <div className="mt-auto pt-2 text-center text-[10px] text-[var(--brand)] font-extrabold border-t border-[var(--border)] uppercase tracking-wide">
              Click to see full analysis
            </div>
          )}
        </div>

        {/* Full View Modal */}
        {isModalOpen && (
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-[10000] animate-in fade-in duration-150" onClick={() => setIsModalOpen(false)}>
            <div className="bg-[var(--bg-card)] w-[90%] max-w-[800px] max-h-[85vh] rounded-xl flex flex-col shadow-2xl overflow-hidden border border-[var(--border)] animate-in slide-in-from-bottom-4 duration-200" onClick={e => e.stopPropagation()}>
              <div className="p-3 border-b border-[var(--border)] flex items-center justify-between bg-[var(--border-light)]">
                <div className="flex items-center gap-2.5">
                  <Sparkles size={18} className="text-[var(--brand)]" />
                  <h2 className="text-base m-0 text-[var(--text-primary)] font-semibold">{section} - Full AI Analysis</h2>
                </div>
                <button onClick={() => setIsModalOpen(false)} className="text-[var(--text-muted)] bg-transparent border-none cursor-pointer hover:text-[var(--text-primary)]">
                  <X size={24} />
                </button>
              </div>
              <div className="p-6 overflow-y-auto text-[13px] leading-relaxed text-[var(--text-primary)] prose prose-invert max-w-none">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>{cleanFullContent}</ReactMarkdown>
              </div>
            </div>
          </div>
        )}
      </>
    );
  }

  // 2. AI Mode Empty State (Prompt to Generate)
  if (isAiMode) {
    const isComparison = tickers && tickers.length > 1;
    const buttonText = isComparison
      ? `Compare ${section} (${tickers.join(' vs ')})`
      : `Generate ${section} for ${tickers ? tickers[0] : '...'}`;

    return (
      <div className="card min-h-[200px] flex items-center justify-center bg-white/5 border-dashed border-[var(--border)] shadow-none backdrop-blur-md">
        <button
           onClick={() => onGenerate(section)}
           className="flex items-center gap-2.5 text-[var(--brand)] font-extrabold px-6 py-2.5 rounded-full border border-blue-500/30 transition-all duration-200 text-[11px] uppercase tracking-wide bg-gradient-to-br from-blue-500/15 to-blue-500/5 shadow-[0_4px_12px_rgba(0,0,0,0.2),inset_0_1px_0_rgba(255,255,255,0.1),inset_0_-1px_0_rgba(0,0,0,0.1)] hover:-translate-y-0.5 hover:from-blue-500/20 hover:to-blue-500/10 hover:shadow-[0_6px_16px_rgba(62,166,255,0.25),inset_0_1px_0_rgba(255,255,255,0.15),inset_0_-1px_0_rgba(0,0,0,0.15)] active:translate-y-0 active:from-blue-500/15 active:to-blue-500/5 active:shadow-[0_4px_12px_rgba(0,0,0,0.2),inset_0_1px_0_rgba(255,255,255,0.1),inset_0_-1px_0_rgba(0,0,0,0.1)]"
        >
          <Sparkles size={14} />
          {buttonText}
        </button>
      </div>
    );
  }

  // 3. Fallback: Standard Original Component
  return <>{originalComponent}</>;
};
