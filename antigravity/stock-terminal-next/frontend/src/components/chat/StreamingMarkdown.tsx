import React, { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { MacroPerspectiveCard } from './MacroPerspectiveCard';
import { useDashboardStore } from '../../store/dashboardStore';
import { Zap } from 'lucide-react';
import { clsx } from "clsx";

interface StreamingMarkdownProps {
  content: string;
  isStreaming: boolean;
  className?: string;
}

const SCRAMBLE_CHARS = "ABCDEF0123456789!@#$%^&*()_+";

export const StreamingMarkdown: React.FC<StreamingMarkdownProps> = ({ content, isStreaming, className }) => {
  const [displayedContent, setDisplayedContent] = useState(isStreaming ? '' : content);
  const [scrambleSuffix, setScrambleSuffix] = useState('');

  // Use a ref to track the animation loop state
  const stateRef = useRef({
    displayedContent: isStreaming ? '' : content,
    targetContent: content,
    lastFrameTime: 0,
  });

  // Memoize extraction to prevent re-render loops
  const { cleanTargetContent, structuredData } = React.useMemo(() => {
    let clean = content;
    let extractedStructured = null;

    // 1. Chart Extraction REMOVED (Charts only on Dashboard now)
    // We still strip [CHART] tags if they appear to keep chat clean
    clean = clean.replace(/\[CHART\][\s\S]*?\[\/CHART\]/g, '');
    clean = clean.replace(/\[CHART\][\s\S]*/g, '');

    // 2. Extract Structured Data (keep in text? or remove? logic says remove for display)
    // The previous code extracted it from 'displayStr' later, but doing it here is cleaner for dependencies.
    // However, existing logic extracted it from 'displayedContent' during render.
    // Let's stick to the 'content' prop for extraction to be stable.
    const structuredMatch = clean.match(/\[STRUCTURED_DATA:\s*(\{.*?\})\]/);
    if (structuredMatch && structuredMatch[1]) {
      try {
        extractedStructured = JSON.parse(structuredMatch[1]);
        clean = clean.replace(/\[STRUCTURED_DATA:.*?\]/g, '');
      } catch (e) { console.error(e); }
    }

    clean = clean.replace(/\[PEER_PACK:.*?\]/g, '');
    clean = clean.replace(/\[UI_COMMAND:.*?\]/g, '');

    return { cleanTargetContent: clean, structuredData: extractedStructured };
  }, [content]);

  // Sync ref with props
  useEffect(() => {
    stateRef.current.targetContent = cleanTargetContent;

    // If not streaming, align immediately
    if (!isStreaming) {
      setDisplayedContent(cleanTargetContent);
      stateRef.current.displayedContent = cleanTargetContent;
      setScrambleSuffix('');
    }
  }, [isStreaming, cleanTargetContent]); 

  // Streaming Animation
  useEffect(() => {
    if (!isStreaming) return;

    let animationFrameId: number;

    const animate = (time: number) => {
      const state = stateRef.current;
      const { displayedContent, targetContent } = state;

      if (displayedContent.length < targetContent.length) {
        const remaining = targetContent.length - displayedContent.length;

        let charsToAdd = 1;
        if (remaining > 50) charsToAdd = 3;
        else if (remaining > 20) charsToAdd = 2;

        const nextContent = targetContent.substring(0, displayedContent.length + charsToAdd);
        state.displayedContent = nextContent;
        setDisplayedContent(nextContent);

        let suffix = "";
        const suffixLen = Math.min(2, remaining);
        for (let i = 0; i < suffixLen; i++) {
          suffix += SCRAMBLE_CHARS[Math.floor(Math.random() * SCRAMBLE_CHARS.length)];
        }
        setScrambleSuffix(suffix);

      } else {
        setScrambleSuffix('');
      }

      state.lastFrameTime = time;
      animationFrameId = requestAnimationFrame(animate);
    };

    animationFrameId = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(animationFrameId);
  }, [isStreaming]); // stable dependency

  const { theme, setAnalysisData, activeAnalysisData, setIsChatMaximized, isChatMaximized } = useDashboardStore();

  const isAnalystCopilot = content.includes('[ANALYST COPILOT]');

  // Clean final display string (remove markers that might still be there if not caught by regex)
  let displayStr = displayedContent.replace('[ANALYST COPILOT]', '').trim();

  // PROACTIVE UI: Auto-maximize
  useEffect(() => {
    if (!isStreaming && structuredData?.layout === 'fullscreen' && !isChatMaximized) {
      setIsChatMaximized(true);
    }
  }, [isStreaming, structuredData, isChatMaximized, setIsChatMaximized]);

  const handlePulseClick = () => {
    if (structuredData) {
      setAnalysisData(structuredData);
    }
  };

  const renderContent = () => (
    <div className="relative group">
      <ReactMarkdown remarkPlugins={[remarkGfm]}>
        {displayStr}
      </ReactMarkdown>

      {/* INLINE CHART REMOVED PER USER REQUEST - Charts now only appear on Dashboard */}

      {structuredData && !isStreaming && (
        <div className="flex justify-start mt-4">
          <button
            onClick={handlePulseClick}
            className={clsx(
              "flex items-center gap-2 px-4 py-2.5 rounded-xl border font-black text-xs transition-all duration-300 transform active:scale-95 group/pulse",
              theme === 'dark'
                ? "bg-amber-500/10 border-amber-500/20 text-amber-500 hover:bg-amber-500/20 hover:border-amber-500/40"
                : "bg-amber-50 border-amber-200 text-amber-600 hover:bg-amber-100 hover:border-amber-300 shadow-sm"
            )}
          >
            <Zap size={14} className={clsx("transition-transform duration-500 group-hover/pulse:scale-125", activeAnalysisData ? "animate-pulse" : "")} fill="currentColor" />
            <span className="uppercase tracking-widest">
              {activeAnalysisData ? "Viewing Analysis" : "Expand Intelligent Pulse"}
            </span>
          </button>
        </div>
      )}

      {isStreaming && displayedContent.length < cleanTargetContent.length && (
        <span className="inline-flex items-center ml-0.5 align-baseline">
          {scrambleSuffix && (
            <span className="text-cyan-400 opacity-80 font-mono text-xs mr-0.5 select-none blur-[0.5px]">
              {scrambleSuffix}
            </span>
          )}
          <span
            className="w-2.5 h-5 bg-[var(--brand)] inline-block align-middle animate-pulse shadow-[0_0_10px_var(--brand)]"
            style={{ borderRadius: '1px' }}
          />
        </span>
      )}
    </div>
  );

  return (
    <div className={`markdown-content relative leading-relaxed ${className || ''}`}>
      {isAnalystCopilot ? (
        <MacroPerspectiveCard theme={theme}>
          {renderContent()}
        </MacroPerspectiveCard>
      ) : (
        renderContent()
      )}
    </div>
  );
};

