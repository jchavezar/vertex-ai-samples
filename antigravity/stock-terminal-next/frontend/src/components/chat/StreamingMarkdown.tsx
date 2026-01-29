import React, { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { MacroPerspectiveCard } from './MacroPerspectiveCard';
import { PeerPackGrid } from './PeerPackGrid';
import { useDashboardStore } from '../../store/dashboardStore';
import { Zap } from 'lucide-react';
import { clsx } from "clsx";
import { PerformanceChart } from '../dashboard/PerformanceChart';

interface StreamingMarkdownProps {
  content: string;
  isStreaming: boolean;
  className?: string;
}

const SCRAMBLE_CHARS = "ABCDEF0123456789!@#$%^&*()_+";

export const StreamingMarkdown: React.FC<StreamingMarkdownProps> = ({ content, isStreaming, className }) => {
  const [displayedContent, setDisplayedContent] = useState(isStreaming ? '' : content);
  const [scrambleSuffix, setScrambleSuffix] = useState('');
  
  // Chart extraction logic
  const [chartData, setChartData] = useState<any>(null);

  // Use a ref to track the animation loop state
  const stateRef = useRef({
    displayedContent: isStreaming ? '' : content,
    targetContent: content,
    lastFrameTime: 0,
  });

  // Extract Chart Data & Clean Content
  // We do this derived calculation to ensure targetContent is always "clean" (no JSON)
  const getCleanContentAndChart = (rawContent: string) => {
    let clean = rawContent;
    let extractedChart = null;

    // 1. Try to find complete block
    const chartMatch = rawContent.match(/\[CHART\]([\s\S]*?)\[\/CHART\]/);
    if (chartMatch && chartMatch[1]) {
      try {
        extractedChart = JSON.parse(chartMatch[1]);
        clean = rawContent.replace(chartMatch[0], ''); // Remove full block
      } catch (e) {
        console.error("Failed to parse chart data", e);
      }
    } else {
      // 2. If no complete block, check for partial to hide it while streaming
      const partialMatch = rawContent.match(/\[CHART\][\s\S]*/);
      if (partialMatch) {
        clean = rawContent.replace(partialMatch[0], ''); // Hide partial
      }
    }

    return { clean, extractedChart };
  };

  const { clean: cleanTargetContent, extractedChart: derivedChart } = getCleanContentAndChart(content);

  // Sync ref with props
  useEffect(() => {
    stateRef.current.targetContent = cleanTargetContent;

    if (derivedChart) {
      setChartData(derivedChart);
    }

    // If not streaming, align immediately
    if (!isStreaming) {
      setDisplayedContent(cleanTargetContent);
      stateRef.current.displayedContent = cleanTargetContent;
      setScrambleSuffix('');
    }
  }, [content, isStreaming, cleanTargetContent, derivedChart]); // Added dependencies

  useEffect(() => {
    if (!isStreaming) return;

    let animationFrameId: number;

    const animate = (time: number) => {
      const state = stateRef.current;
      const { displayedContent, targetContent } = state;

      // Calculate time delta
      
      // Target frame rate (e.g. 60fps -> 16ms)
      // We throttle slightly to create a "tech" feel, or just go smooth.
      // Let's go perfectly smooth but variable speed.
      
      if (displayedContent.length < targetContent.length) {
        // Determine catch-up speed
        const remaining = targetContent.length - displayedContent.length;
        
        // Dynamic Chunk Size: Faster if we are far behind
        // 1 char per frame if close
        // 3-5 chars per frame if far
        let charsToAdd = 1;
        if (remaining > 50) charsToAdd = 3;
        else if (remaining > 20) charsToAdd = 2;

        // Add text
        const nextContent = targetContent.substring(0, displayedContent.length + charsToAdd);
        state.displayedContent = nextContent;
        setDisplayedContent(nextContent);

        // Scramble Effect:
        // Generate 2-3 random chars to append
        let suffix = "";
        const suffixLen = Math.min(2, remaining);
        for (let i = 0; i < suffixLen; i++) {
          suffix += SCRAMBLE_CHARS[Math.floor(Math.random() * SCRAMBLE_CHARS.length)];
        }
        setScrambleSuffix(suffix);

      } else {
        // Done streaming
        setScrambleSuffix('');
      }

      state.lastFrameTime = time;
      animationFrameId = requestAnimationFrame(animate);
    };

    animationFrameId = requestAnimationFrame(animate);

    return () => cancelAnimationFrame(animationFrameId);
  }, [isStreaming]);

  const { theme } = useDashboardStore();

  // Note: content prop might contain [ANALYST COPILOT] but CleanContent might have stripped it?
  // Actually, getCleanContentAndChart only strips [CHART].
  // So [ANALYST COPILOT] remains in displayedContent if present.
  const isAnalystCopilot = content.includes('[ANALYST COPILOT]');

  // Clean content for display (remove tags)
  let displayStr = displayedContent;
  let peerPackData: any[] | null = null;

  // Detect and extract Structured Data
  let structuredData: any = null;
  const structuredDataMatch = displayStr.match(/\[STRUCTURED_DATA:\s*(\{.*?\})\]/);
  if (structuredDataMatch && structuredDataMatch[1]) {
    try {
      structuredData = JSON.parse(structuredDataMatch[1]);
    } catch (e) {
      console.error("Failed to parse structured data", e);
    }
  }

  // Detect and extract Peer Pack data (legacy support if needed, or just focus on structuredData)
  const peerPackMatch = displayStr.match(/\[PEER_PACK:\s*(\[.*?\])\]/);
  if (peerPackMatch && peerPackMatch[1] && !peerPackData) {
    try {
      peerPackData = JSON.parse(peerPackMatch[1]);
    } catch (e) {
      console.error("Failed to parse peer pack data", e);
    }
  }

  // Remove tags from the markdown display
  displayStr = displayStr.replace(/\[PEER_PACK:.*?\]/g, '');
  displayStr = displayStr.replace(/\[STRUCTURED_DATA:.*?\]/g, '');
  displayStr = displayStr.replace(/\[UI_COMMAND:.*?\]/g, '');

  // Remove the Analyst Copilot prefix if present
  displayStr = displayStr.replace('[ANALYST COPILOT]', '').trim();

  const { setAnalysisData, activeAnalysisData, setIsChatMaximized, isChatMaximized } = useDashboardStore();

  // PROACTIVE UI: Auto-maximize if the agent suggests a fullscreen layout (e.g. Peer Packs)
  useEffect(() => {
    if (!isStreaming && structuredData?.layout === 'fullscreen' && !isChatMaximized) {
      console.log("PROACTIVE UI: Auto-maximizing chat for high-density analysis...");
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

      {/* Render Chart if present */}
      {chartData && (
        <div className={clsx(
          "mt-4 mb-2 rounded-2xl overflow-hidden border shadow-sm transition-all animate-in fade-in slide-in-from-bottom-4 duration-700",
          theme === 'dark' ? "bg-white/5 border-white/10" : "bg-white border-slate-200"
        )}>
          <div className="h-[350px] w-full p-4 relative">
            <div className="absolute top-4 left-6 z-10 flex flex-col">
              <span className={clsx("text-lg font-bold", theme === 'dark' ? "text-white" : "text-slate-800")}>
                {chartData.title || "Market Data"}
              </span>
            </div>
            <PerformanceChart ticker={chartData.title?.split(' ')[0] || "Unknown"} externalData={chartData} />
          </div>
        </div>
      )}

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

      {peerPackData && !isAnalystCopilot && <PeerPackGrid peers={peerPackData} theme={theme} />}

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
