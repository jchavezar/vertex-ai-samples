import React from 'react';
import { Zap } from 'lucide-react';

export interface InsightData {
  type: string;
  title: string;
  time: string;
  headline: string;
  summary: string;
  suggestedActions?: string[];
}

export const useAgentInsights = (ticker: string) => {
  const insights: InsightData[] = [
    {
      type: "Meeting Prep",
      title: "FDS - MEETING PREP",
      time: "Now",
      headline: `${ticker} Strategic Shift Analysis`,
      summary: `Agent reviewed 57 news items and recent filings for ${ticker} to prepare this brief.`,
    },
    {
      type: "Earnings Context",
      title: "FDS - EARNINGS CONTEXT",
      time: "Current",
      headline: `${ticker} Sentiment Analysis and Key Questions`,
      summary: `Agent reviewed transcripts, earnings calls, and news to prepare comprehensive questions for ${ticker}.`,
    },
    {
      type: "Industry Comparison",
      title: "INDUSTRY COMPARISON",
      time: "Real-time",
      headline: `How ${ticker} stacks up against competitors`,
      summary: `Agent reviewed 121 news reports and industry data to prepare a comprehensive debrief.`,
    }
  ];

  const suggestedActions = [
    `10-K Insights for ${ticker}`,
    `Annual KPI Tracking for ${ticker}`,
    `Bond Market Update for ${ticker}`,
    `Insider Trading Activity for ${ticker}`,
    `Institutional Ownership Shift for ${ticker}`,
    `Sector Relative Value Analysis for ${ticker}`
  ];

  return { insights, suggestedActions };
};

export const InsightCard: React.FC<{ data: InsightData; color?: 'blue' | 'sky' | 'indigo' | 'gray' }> = ({ data, color = 'gray' }) => {
  // Map color to classes
  const colorMap = {
    blue: { border: 'border-l-2 border-l-blue-500', text: 'text-blue-500', dot: 'bg-blue-500' },
    sky: { border: 'border-l-2 border-l-sky-500', text: 'text-sky-500', dot: 'bg-sky-500' },
    indigo: { border: 'border-l-2 border-l-indigo-500', text: 'text-indigo-500', dot: 'bg-indigo-500' },
    gray: { border: 'border-l-2 border-l-[var(--text-primary)]', text: 'text-[var(--text-primary)]', dot: 'bg-[var(--text-primary)]' }
  };

  const c = colorMap[color];

  return (
    <div className={`p-0 overflow-hidden hover:bg-[var(--bg-panel)] transition-all duration-300 group bg-[var(--bg-card)] h-full flex flex-col border-b border-[var(--border-subtle)]/30 ${c.border}`}>
      <div className="px-4 py-2 border-b border-[var(--border-subtle)] bg-white/[0.03] backdrop-blur-md">
        <span className={`font-black ${c.text} text-[10px] uppercase tracking-[0.2em] flex items-center gap-2`}>
          <div className={`w-1.5 h-1.5 rounded-full ${c.dot} shadow-[0_0_8px_currentColor]`}></div>
          {data.title}
        </span>
        <span className="text-[9px] text-[var(--text-muted)] font-black uppercase tracking-widest opacity-60 group-hover:opacity-100 transition-opacity">{data.time}</span>
      </div>
      <div className="p-4 flex-1 overflow-hidden">
        <div className="flex flex-col gap-2">
          <h4 className="text-[14px] text-[var(--text-primary)] font-bold tracking-tight leading-snug group-hover:text-[var(--brand)] transition-colors">
            {data.headline}
          </h4>
          <p className="text-[12.5px] text-[var(--text-secondary)] leading-relaxed font-medium opacity-90">
            {data.summary}
          </p>
        </div>
      </div>
    </div>
  );
};

export const SuggestedActionsCard: React.FC<{ actions: string[]; color?: 'blue' | 'gray' }> = ({ actions, color = 'gray' }) => {
  const isGray = color === 'gray';

  return (
    <div className={`p-0 overflow-hidden hover:bg-[var(--bg-panel)] transition-all duration-300 flex flex-col bg-[var(--bg-card)] h-full border-l-2 ${isGray ? 'border-l-[var(--text-primary)]' : 'border-l-blue-500'}`}>
      <div className="px-4 py-2 border-b border-[var(--border-subtle)] bg-white/[0.01]">
        <span className={`font-black ${isGray ? 'text-[var(--text-primary)]' : 'text-blue-500'} text-[10px] uppercase tracking-[0.25em] flex items-center gap-2`}>
          <div className={`w-1.5 h-1.5 rounded-full ${isGray ? 'bg-[var(--text-primary)]' : 'bg-blue-500'} shadow-[0_0_8px_currentColor]`}></div>
          SUGGESTED ACTIONS
        </span>
      </div>
      <div className="p-3 flex-1 overflow-hidden">
        <ul className="flex flex-col gap-1.5">
          {actions.map((item, i) => (
            <li key={i} className="text-[11.5px] font-bold text-[var(--text-secondary)] cursor-pointer transition-all hover:text-[var(--text-primary)] hover:bg-white/5 px-3 py-1.5 rounded-lg flex items-center gap-3 group border border-transparent hover:border-white/10 hover:shadow-sm overflow-hidden shrink-0">
              <span className={`w-1.5 h-1.5 rounded-full flex-shrink-0 ${isGray ? 'bg-[var(--text-primary)]' : 'bg-blue-500'} opacity-30 group-hover:opacity-100 group-hover:scale-110 transition-all`}></span>
              <span className="leading-tight break-words">{item}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};

// New Consolidated Intelligence Feed
export const StrategicIntelligenceFeed: React.FC<{ ticker: string }> = ({ ticker }) => {
  const { insights } = useAgentInsights(ticker);
  return (
    <div className="flex flex-col h-full bg-[var(--bg-card)] rounded-2xl border border-[var(--border-subtle)] overflow-hidden shadow-sm">
      <div className="px-4 py-3 border-b border-[var(--border-subtle)] bg-white/[0.02] flex items-center justify-between">
        <span className="font-black text-[var(--text-primary)] text-[10px] uppercase tracking-[0.3em] flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-blue-500 shadow-[0_0_10px_rgba(59,130,246,0.6)]"></div>
          STRATEGIC INTELLIGENCE FEED
        </span>
        <span className="text-[9px] font-bold text-[var(--text-muted)] uppercase tracking-widest opacity-60">Real-time Analysis</span>
      </div>
      <div className="flex-1 overflow-y-auto no-scrollbar">
        {insights.map((insight, idx) => (
          <InsightCard key={idx} data={insight} color="blue" />
        ))}
      </div>
    </div>
  );
};

// New Quick Actions Panel (Static Buttons)
export const QuickActionsPanel: React.FC<{ ticker: string }> = ({ ticker }) => {
  const { suggestedActions } = useAgentInsights(ticker);
  return (
    <div className="flex flex-col h-full bg-[var(--bg-card)] rounded-2xl border border-[var(--border-subtle)] overflow-hidden shadow-sm">
      <div className="px-4 py-3 border-b border-[var(--border-subtle)] bg-white/[0.02]">
        <span className="font-black text-[var(--text-primary)] text-[10px] uppercase tracking-[0.3em] flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-emerald-500 shadow-[0_0_10px_rgba(16,185,129,0.6)]"></div>
          SUGGESTED ACTIONS
        </span>
      </div>
      <div className="p-2.5 flex-1 overflow-y-auto no-scrollbar">
        <div className="flex flex-col gap-2">
          {suggestedActions.map((action, i) => (
            <button key={i} className="group w-full text-left p-3 rounded-xl bg-white/[0.02] border border-white/10 hover:bg-white/[0.06] hover:border-blue-500/40 transition-all duration-300 flex items-center gap-3 shadow-md shadow-black/20 hover:shadow-lg hover:shadow-black/40">
              <div className="w-8 h-8 rounded-lg bg-white/5 flex items-center justify-center shrink-0 group-hover:bg-blue-500/10 transition-colors border border-white/5">
                <Zap size={14} className="text-[var(--text-muted)] group-hover:text-blue-400 transition-colors" />
              </div>
              <div className="flex flex-col min-w-0">
                <span className="text-[11.5px] font-bold text-[var(--text-primary)] leading-tight tracking-tight truncate">{action}</span>
                <span className="text-[8px] font-black text-[var(--text-muted)] uppercase tracking-widest opacity-40 group-hover:opacity-100 group-hover:text-blue-400 transition-all">Execute Workflow</span>
              </div>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

// Legacy Component Wrapper for compatibility if needed elsewhere
export const AgentInsights: React.FC<{ ticker: string }> = ({ ticker }) => {
  return (
    <div className="grid grid-cols-12 gap-5 h-full">
      <div className="col-span-12 lg:col-span-8 h-full">
        <StrategicIntelligenceFeed ticker={ticker} />
      </div>
      <div className="col-span-12 lg:col-span-4 h-full">
        <QuickActionsPanel ticker={ticker} />
      </div>
    </div>
  );
};
