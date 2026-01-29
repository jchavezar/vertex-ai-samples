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
    <div className="grid grid-cols-4 gap-4 mb-4">
      {insights.map((insight, idx) => (
        <div key={idx} className="card p-0 overflow-hidden hover:shadow-lg transition-all duration-300 group border-[var(--border)] bg-[var(--bg-card)]">
          <div className="bg-gradient-to-r from-blue-500/10 to-transparent px-4 py-2 flex justify-between items-center border-b border-[var(--border)]">
            <span className="font-bold text-[#2563eb] text-[10px] uppercase tracking-wide">{insight.title}</span>
            <span className="text-[10px] text-[#2563eb] bg-white/50 px-1.5 py-0.5 rounded">{insight.time}</span>
          </div>
          <div className="p-4">
            <h4 className="text-[13px] text-[var(--text-primary)] mb-2 font-bold leading-tight group-hover:text-blue-400 transition-colors">{insight.headline}</h4>
            <p className="text-[12px] text-[var(--text-secondary)] leading-relaxed">{insight.summary}</p>
          </div>
        </div>
      ))}

      <div className="card p-0 overflow-hidden hover:shadow-lg transition-all duration-300 flex flex-col border-[var(--border)] bg-[var(--bg-card)]">
        <div className="bg-gradient-to-r from-sky-500/10 to-transparent px-4 py-2 border-b border-[var(--border)] mb-3">
          <span className="font-bold text-[#0284c7] text-[10px] uppercase tracking-wide">SUGGESTED FOLLOW UPS</span>
        </div>
        <div className="px-4 pb-4 flex-1">
          <ul className="list-none space-y-2.5">
            {[
              `10-K Insights for ${ticker}`,
              `Annual KPI Tracking for ${ticker}`,
              `Bond Market Update for ${ticker}`
            ].map((item, i) => (
              <li key={i} className="text-[11px] text-[var(--text-secondary)] cursor-pointer transition-colors hover:text-[#0284c7] hover:bg-[#e0f2fe]/50 px-2 py-1.5 rounded -mx-2 flex items-center gap-2 group">
                <span className="w-1 h-1 rounded-full bg-[#0284c7] opacity-0 group-hover:opacity-100 transition-opacity"></span>
                {item}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
};
