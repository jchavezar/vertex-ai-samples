import React from 'react';

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
    `Bond Market Update for ${ticker}`
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
    <div className={`p-0 overflow-hidden hover:bg-[var(--bg-panel)] transition-all duration-300 group bg-[var(--bg-card)] h-full flex flex-col ${c.border}`}>
      <div className="px-3 py-2 flex justify-between items-center border-b border-[var(--border-subtle)]">
        <span className={`font-black ${c.text} text-[9px] uppercase tracking-[0.2em] flex items-center gap-2`}>
          <div className={`w-1 h-1 rounded-full ${c.dot}`}></div>
          {data.title}
        </span>
        <span className="text-[8px] text-[var(--text-muted)] font-black uppercase tracking-widest">{data.time}</span>
      </div>
      <div className="p-4 flex-1 flex flex-col justify-center gap-1.5">
        <h4 className="text-[14px] text-[var(--text-primary)] font-bold tracking-tight leading-snug group-hover:text-[var(--brand)] transition-colors line-clamp-1">{data.headline}</h4>
        <p className="text-[12px] text-[var(--text-secondary)] leading-relaxed line-clamp-2">{data.summary}</p>
      </div>
    </div>
  );
};

export const SuggestedActionsCard: React.FC<{ actions: string[]; color?: 'blue' | 'gray' }> = ({ actions, color = 'gray' }) => {
  const isGray = color === 'gray';

  return (
    <div className={`p-0 overflow-hidden hover:bg-[var(--bg-panel)] transition-all duration-300 flex flex-col bg-[var(--bg-card)] h-full border-l-2 ${isGray ? 'border-l-[var(--text-primary)]' : 'border-l-blue-500'}`}>
      <div className="px-3 py-2 border-b border-[var(--border-subtle)]">
        <span className={`font-black ${isGray ? 'text-[var(--text-primary)]' : 'text-blue-500'} text-[9px] uppercase tracking-[0.2em] flex items-center gap-2`}>
          <div className={`w-1 h-1 rounded-full ${isGray ? 'bg-[var(--text-primary)]' : 'bg-blue-500'}`}></div>
          SUGGESTED ACTIONS
        </span>
      </div>
      <div className="p-2 flex-1">
        <ul className="list-none space-y-0.5">
          {actions.map((item, i) => (
            <li key={i} className="text-[11px] font-bold text-[var(--text-secondary)] cursor-pointer transition-colors hover:text-[var(--text-primary)] hover:bg-[var(--bg-panel)] px-3 py-1.5 rounded-md flex items-center gap-2.5 group">
              <span className={`w-1 h-1 rounded-full ${isGray ? 'bg-[var(--text-primary)]' : 'bg-blue-500'} opacity-30 group-hover:opacity-100 transition-opacity`}></span>
              <span className="truncate">{item}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};

// Legacy Component Wrapper for compatibility if needed elsewhere
export const AgentInsights: React.FC<{ ticker: string }> = ({ ticker }) => {
  const { insights, suggestedActions } = useAgentInsights(ticker);
  return (
    <div className="flex flex-col gap-3 h-full overflow-auto pr-2">
      {insights.map((insight, idx) => (
        <React.Fragment key={idx}>
          <InsightCard data={insight} />
        </React.Fragment>
      ))}
      <SuggestedActionsCard actions={suggestedActions} />
    </div>
  );
};
