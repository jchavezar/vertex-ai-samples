import React, { useState } from 'react';
import { Cpu, Eye, EyeOff, BarChart2 } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import '../ProjectCardWidget.css';

interface ProjectCardData {
  title: string;
  industry: string;
  factual_information: string;
  original_context?: string;
  insights?: string[];
  key_metrics?: string[];
  chart_data?: string;
  document_weight?: number;
  redacted_entities: string[];
  document_name: string;
  document_url?: string;
}

interface ProjectCardWidgetProps {
  card: ProjectCardData;
}

export const ProjectCardWidget: React.FC<ProjectCardWidgetProps> = ({ card }) => {
  const [showOriginal, setShowOriginal] = useState(false);

  // Helper to render original context with styled redactions
  const renderOriginalContext = (text: string) => {
    if (!text) return null;

    // Split by the <redact> tags
    const parts = text.split(/(<redact>.*?<\/redact>)/g);

    return (
      <p className="original-context-text">
        {parts.map((part, index) => {
          if (part.startsWith('<redact>') && part.endsWith('</redact>')) {
            const redactedContent = part.replace('<redact>', '').replace('</redact>', '');
            return (
              <span key={index} className="redacted-tape" title="Sensitive Data Masked">
                {redactedContent}
              </span>
            );
          }
          return <span key={index}>{part}</span>;
        })}
      </p>
    );
  };

  // Helper to parse and render chart data
  const renderChart = (chartDataStr?: string) => {
    if (!chartDataStr) return null;
    try {
      const dataObj = JSON.parse(chartDataStr);
      const data = Object.keys(dataObj).map(key => ({
        name: key,
        value: Number(dataObj[key])
      }));

      return (
        <div className="chart-container" style={{ height: '200px', marginTop: '1rem', background: 'rgba(0,0,0,0.2)', padding: '1rem', borderRadius: '8px' }}>
          <h4 style={{ marginBottom: '1rem', fontSize: '0.9rem', color: 'var(--pwc-orange)', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <BarChart2 size={16} /> Data Visualization
          </h4>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data} layout="vertical" margin={{ top: 5, right: 30, left: 10, bottom: 5 }}>
              <XAxis type="number" hide />
              <YAxis dataKey="name" type="category" axisLine={false} tickLine={false} tick={{ fill: 'var(--pwc-black)', fontSize: 12 }} width={160} />
              <Tooltip cursor={{ fill: 'rgba(0,0,0,0.05)' }} contentStyle={{ backgroundColor: 'var(--pwc-bg-main)', borderColor: 'var(--pwc-border)', color: 'var(--pwc-black)' }} />
              <Bar dataKey="value" fill="var(--pwc-orange)" radius={[0, 4, 4, 0]} barSize={20} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      );
    } catch (e) {
      console.error("Failed to parse chart data", e);
      return null;
    }
  };

  // Relevancy Heat Map Color Logic
  const getWeightColor = (weight: number = 100) => {
    if (weight >= 80) return 'var(--pwc-orange)'; // High relevance
    if (weight >= 50) return '#FFB600'; // Medium relevance (yellowish)
    return 'var(--pwc-dark-gray)'; // Low relevance
  };

  return (
    <article className="pwc-card">
      <header className="card-header">
        <span className="industry-tag">{card.industry || 'Internal Data'}</span>
        <div className="card-meta-right">
          {typeof card.document_weight === 'number' && (
            <div className="relevancy-badge" title={`Document Relevance: ${card.document_weight}%`} style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.8rem', color: 'var(--pwc-light-gray)' }}>
              <div style={{ width: '40px', height: '6px', backgroundColor: 'var(--pwc-dark-gray)', borderRadius: '3px', overflow: 'hidden' }}>
                <div style={{ width: `${card.document_weight}%`, height: '100%', backgroundColor: getWeightColor(card.document_weight) }}></div>
              </div>
              <span>{card.document_weight}% Match</span>
            </div>
          )}
          <a
            href={card.document_url || `https://sockcop.sharepoint.com/sites/FinancialDocument/Shared%20Documents/${encodeURIComponent(card.document_name)}`}
            target="_blank"
            rel="noopener noreferrer"
            className="doc-id"
            title="View Secure Source Document"
          >
            Ref: {card.document_name}
          </a>
        </div>
      </header>

      <h2 className="card-title">{card.title}</h2>

      <section className="card-body">
        <div className="info-block">
          <div className="info-block-header">
            <h3>{showOriginal ? 'Original Source Context' : 'Factual Information (Generalized)'}</h3>
            {card.original_context && (
              <button
                className="toggle-context-btn"
                onClick={() => setShowOriginal(!showOriginal)}
                title={showOriginal ? "Show generalized extraction" : "Show original source text"}
              >
                {showOriginal ? <EyeOff size={16} /> : <Eye size={16} />}
                <span>{showOriginal ? 'Hide Context' : 'View Source'}</span>
              </button>
            )}
          </div>

          <div className="context-container">
            {showOriginal && card.original_context ? (
              renderOriginalContext(card.original_context)
            ) : (
              <p>{card.factual_information}</p>
            )}
          </div>
        </div>

        {card.insights && card.insights.length > 0 && (
          <div className="info-block">
            <h3>Key Insights</h3>
            <ul>
              {card.insights.map((insight, i) => (
                <li key={i}>{insight}</li>
              ))}
            </ul>
          </div>
        )}

        {card.chart_data && renderChart(card.chart_data)}
      </section>

      {card.key_metrics && card.key_metrics.length > 0 && (
        <footer className="card-footer metrics">
          {card.key_metrics.map((metric, i) => (
            <span key={i} className="metric-pill"><Cpu size={14} /> {metric}</span>
          ))}
        </footer>
      )}
    </article>
  );
};
