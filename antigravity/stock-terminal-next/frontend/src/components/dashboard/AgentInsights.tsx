import React from 'react';
import { Sparkles, ArrowRight } from 'lucide-react';

interface AgentInsightsProps {
  ticker: string;
}

export const AgentInsights: React.FC<AgentInsightsProps> = ({ ticker }) => {
  const insights = [
    {
      title: `${ticker} - Meeting Prep`,
      time: "Now",
      headline: `${ticker} Strategic Shift Analysis`,
      summary: `Agent reviewed 57 news items and recent filings for ${ticker} to prepare this brief.`,
    },
    {
      title: `${ticker} - Earnings Context`,
      time: "Current",
      headline: `${ticker} Sentiment Analysis and Key Questions`,
      summary: `Agent reviewed transcripts, earnings calls, and news to prepare comprehensive questions for ${ticker}.`,
    },
    {
      title: "Industry Comparison",
      time: "Real-time",
      headline: `How ${ticker} stacks up against competitors`,
      summary: `Agent reviewed 121 news reports and industry data to prepare a comprehensive debrief.`,
    }
  ];

  return (
    <div className="card bg-blue-500/5 border-blue-500/30 shadow-[0_0_20px_rgba(59,130,246,0.1)]">
      <div className="flex items-center justify-between mb-3 text-[13px] uppercase tracking-wide text-[var(--text-secondary)]">
        <div className="flex items-center gap-2">
          <Sparkles size={14} className="text-[var(--brand)]" />
          <span className="font-bold text-[var(--brand)]">AI Mercury Agent Insights - {ticker}</span>
          <ArrowRight size={14} />
        </div>
      </div>

      <div className="grid grid-cols-4 gap-5">
        {insights.map((insight, idx) => (
          <div key={idx} className="pr-5 border-r border-[var(--border)] last:border-r-0">
            <div className="flex justify-between text-[11px] text-[var(--text-muted)] mb-2">
              <span className="font-bold text-[var(--brand)] uppercase tracking-wide">{insight.title}</span>
              <span>{insight.time}</span>
            </div>
            <h4 className="text-sm text-[var(--text-primary)] mb-2 font-bold leading-tight">{insight.headline}</h4>
            <p className="text-[13px] text-[var(--text-secondary)]">{insight.summary}</p>
          </div>
        ))}

        <div className="bg-blue-500/5 p-4 rounded-xl border border-dashed border-blue-500/30">
          <p className="font-extrabold text-[11px] text-[var(--brand)] mb-3 uppercase">Suggested Follow Ups</p>
          <ul className="list-none space-y-2">
            {[
              `10-K Insights for ${ticker}`,
              `Annual KPI Tracking for ${ticker}`,
              `Bond Market Update for ${ticker}`
            ].map((item, i) => (
              <li key={i} className="text-xs text-[var(--text-secondary)] cursor-pointer transition-colors hover:text-[var(--brand)] hover:underline">
                {item}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
};
