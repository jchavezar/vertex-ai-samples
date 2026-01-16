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
          background: linear-gradient(to bottom, #fcfdff, #ffffff);
          border: 1px solid #cce0ff;
        }
        .insights-grid {
          display: grid;
          grid-template-columns: repeat(4, 1fr);
          gap: 16px;
        }
        .insight-card {
          padding-right: 16px;
          border-right: 1px solid var(--border-light);
        }
        .insight-card:last-child {
          border-right: none;
        }
        .insight-header {
          display: flex;
          justify-content: space-between;
          font-size: 10px;
          color: var(--text-muted);
          margin-bottom: 8px;
        }
        .insight-type { font-weight: 700; color: var(--text-secondary); }
        .insight-headline {
          font-size: 13px;
          color: #004b87;
          margin-bottom: 8px;
          line-height: 1.3;
        }
        .insight-summary {
          font-size: 11px;
          color: var(--text-secondary);
        }
        .suggestions {
          background: #f8fbff;
          padding: 12px;
          border-radius: 4px;
          border: 1px dashed #cce0ff;
        }
        .suggestion-title {
          font-weight: 700;
          font-size: 10px;
          color: #004b87;
          margin-bottom: 8px;
        }
        .suggestion-list {
          list-style: none;
        }
        .suggestion-list li {
          font-size: 11px;
          color: #004b87;
          margin-bottom: 4px;
          text-decoration: underline;
          cursor: pointer;
        }
      `}</style>
    </div>
  );
};

export default AgentInsights;
