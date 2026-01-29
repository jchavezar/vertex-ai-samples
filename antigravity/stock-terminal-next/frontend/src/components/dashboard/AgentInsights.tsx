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

export const InsightCard: React.FC<{ data: InsightData; color?: 'blue' | 'sky' | 'indigo' }> = ({ data, color = 'blue' }) => {
  // Map color to classes
  const colorMap = {
    blue: {
      border: 'border-l-4 border-l-blue-500',
      text: 'text-blue-500',
      bg: 'bg-blue-500',
      dot: 'bg-blue-500'
    },
    sky: {
      border: 'border-l-4 border-l-sky-500',
      text: 'text-sky-500',
      bg: 'bg-sky-500',
      dot: 'bg-sky-500'
    },
    indigo: {
      border: 'border-l-4 border-l-indigo-500',
      text: 'text-indigo-500',
      bg: 'bg-indigo-500',
      dot: 'bg-indigo-500'
    }
  };

  const c = colorMap[color];

  return (
    <div className={`card p-0 overflow-hidden hover:shadow-lg transition-all duration-300 group border-[var(--border)] bg-[var(--bg-card)] h-full flex flex-col ${c.border}`}>
      <div className="bg-[var(--bg-panel)]/50 px-4 py-3 flex justify-between items-center border-b border-[var(--border)]">
        <span className={`font-bold ${c.text} text-xs uppercase tracking-wide flex items-center gap-2`}>
          <div className={`w-2 h-2 rounded-full ${c.dot} animate-pulse`}></div>
          {data.title}
        </span>
        <span className="text-[10px] text-[var(--text-muted)] bg-[var(--bg-panel)] border border-[var(--border-subtle)] px-2 py-0.5 rounded-full font-mono">{data.time}</span>
      </div>
      <div className="p-5 flex-1 flex flex-col justify-center">
        <h4 className="text-base text-[var(--text-primary)] mb-3 font-bold leading-snug group-hover:text-[var(--accent)] transition-colors">{data.headline}</h4>
        <p className="text-sm text-[var(--text-secondary)] leading-relaxed">{data.summary}</p>
      </div>
    </div>
  );
};

export const SuggestedActionsCard: React.FC<{ actions: string[] }> = ({ actions }) => {
  return (
    <div className="card p-0 overflow-hidden hover:shadow-lg transition-all duration-300 flex flex-col border-[var(--border)] bg-[var(--bg-card)] h-full border-l-4 border-l-sky-500">
      <div className="bg-[var(--bg-panel)]/50 px-4 py-3 border-b border-[var(--border)]">
        <span className="font-bold text-sky-500 text-xs uppercase tracking-wide flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-sky-500"></div>
          SUGGESTED ACTIONS
        </span>
      </div>
      <div className="p-3 flex-1">
        <ul className="list-none space-y-1">
          {actions.map((item, i) => (
            <li key={i} className="text-xs font-medium text-[var(--text-secondary)] cursor-pointer transition-colors hover:text-sky-500 hover:bg-sky-500/5 px-3 py-2.5 rounded-md flex items-center gap-3 group">
              <span className="w-1.5 h-1.5 rounded-full bg-sky-500 opacity-30 group-hover:opacity-100 transition-opacity"></span>
              {item}
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
