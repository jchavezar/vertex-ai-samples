import React from 'react';
import { Sparkles, ArrowRight } from 'lucide-react';

const AgentInsights = ({ ticker }) => {
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
    <div className="card insights-container">
      <div className="section-title">
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <Sparkles size={14} color="#004b87" />
          <span style={{ fontWeight: 700, color: '#004b87' }}>AI Mercury Agent Insights - {ticker}</span>
          <ArrowRight size={14} />
        </div>
      </div>

      <div className="insights-grid">
        {insights.map((insight, idx) => (
          <div key={idx} className="insight-card">
            <div className="insight-header">
              <span className="insight-type">{insight.title}</span>
              <span className="insight-time">{insight.time}</span>
            </div>
            <h4 className="insight-headline">{insight.headline}</h4>
            <p className="insight-summary">{insight.summary}</p>
          </div>
        ))}

        <div className="insight-card suggestions">
          <p className="suggestion-title">Suggested Follow Ups</p>
          <ul className="suggestion-list">
            <li>10-K Insights for {ticker}</li>
            <li>Annual KPI Tracking for {ticker}</li>
            <li>Bond Market Update for {ticker}</li>
          </ul>
        </div>
      </div>

      <style jsx="true">{`
        .insights-container {
          background: rgba(59, 130, 246, 0.03);
          border: 1px solid rgba(59, 130, 246, 0.3);
          box-shadow: 0 0 20px rgba(59, 130, 246, 0.1);
        }
        .insights-grid {
          display: grid;
          grid-template-columns: repeat(4, 1fr);
          gap: 20px;
        }
        .insight-card {
          padding-right: 20px;
          border-right: 1px solid var(--border);
        }
        .insight-card:last-child {
          border-right: none;
        }
        .insight-header {
          display: flex;
          justify-content: space-between;
          font-size: 11px;
          color: var(--text-muted);
          margin-bottom: 8px;
        }
        .insight-type { font-weight: 700; color: var(--brand); text-transform: uppercase; letter-spacing: 0.5px; }
        .insight-headline {
          font-size: 14px;
          color: var(--text-primary);
          margin-bottom: 8px;
          line-height: 1.4;
          font-weight: 700;
        }
        .insight-summary {
          font-size: 13px;
          color: var(--text-secondary);
        }
        .suggestions {
          background: rgba(59, 130, 246, 0.05);
          padding: 16px;
          border-radius: 12px;
          border: 1px dashed rgba(59, 130, 246, 0.3);
        }
        .suggestion-title {
          font-weight: 800;
          font-size: 11px;
          color: var(--brand);
          margin-bottom: 12px;
          text-transform: uppercase;
        }
        .suggestion-list {
          list-style: none;
        }
        .suggestion-list li {
          font-size: 12px;
          color: var(--text-secondary);
          margin-bottom: 8px;
          cursor: pointer;
          transition: color 0.2s;
        }
        .suggestion-list li:hover {
          color: var(--brand);
          text-decoration: underline;
        }
      `}</style>
    </div>
  );
};

export default AgentInsights;
