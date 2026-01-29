import React from 'react';

interface AgentInsightsProps {
  ticker: string;
}

export const AgentInsights: React.FC<AgentInsightsProps> = ({ ticker }) => {
  const insights = [
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

  return (
    <div className="flex flex-col gap-3 h-full overflow-auto pr-2">
      {insights.map((insight, idx) => (
        <div key={idx} className="card p-0 overflow-hidden hover:shadow-lg transition-all duration-300 group border-[var(--border)] bg-[var(--bg-card)] shrink-0">
          <div className="bg-gradient-to-r from-blue-500/10 to-transparent px-4 py-3 flex justify-between items-center border-b border-[var(--border)]">
            <span className="font-bold text-[#2563eb] text-xs uppercase tracking-wide flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-blue-500 animate-pulse"></div>
              {insight.title}
            </span>
            <span className="text-xs text-[var(--text-muted)] bg-[var(--bg-panel)] border border-[var(--border-subtle)] px-2 py-1 rounded-full font-mono">{insight.time}</span>
          </div>
          <div className="p-5">
            <h4 className="text-base text-[var(--text-primary)] mb-3 font-bold leading-snug group-hover:text-blue-500 transition-colors">{insight.headline}</h4>
            <p className="text-sm text-[var(--text-secondary)] leading-relaxed">{insight.summary}</p>
          </div>
        </div>
      ))}

      <div className="card p-0 overflow-hidden hover:shadow-lg transition-all duration-300 flex flex-col border-[var(--border)] bg-[var(--bg-card)] shrink-0 mt-2">
        <div className="bg-gradient-to-r from-sky-500/10 to-transparent px-4 py-3 border-b border-[var(--border)]">
          <span className="font-bold text-[#0284c7] text-xs uppercase tracking-wide flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-sky-500"></div>
            SUGGESTED ACTIONS
          </span>
        </div>
        <div className="p-2">
          <ul className="list-none space-y-1">
            {[
              `10-K Insights for ${ticker}`,
              `Annual KPI Tracking for ${ticker}`,
              `Bond Market Update for ${ticker}`
            ].map((item, i) => (
              <li key={i} className="text-xs font-medium text-[var(--text-secondary)] cursor-pointer transition-colors hover:text-[#0284c7] hover:bg-sky-500/5 px-3 py-2.5 rounded-md flex items-center gap-3 group">
                <span className="w-2 h-2 rounded-full bg-[#0284c7] opacity-30 group-hover:opacity-100 transition-opacity"></span>
                {item}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
};
