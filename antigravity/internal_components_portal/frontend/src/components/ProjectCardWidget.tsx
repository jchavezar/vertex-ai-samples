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
  pii_detected?: boolean;
  governance_recommendation?: string;
  id?: string; // item_id for actions
}

interface ProjectCardWidgetProps {
  card: ProjectCardData;
}

export const ProjectCardWidget: React.FC<ProjectCardWidgetProps> = ({ card }) => {
  const [showOriginal, setShowOriginal] = useState(false);
  const [isSecuring, setIsSecuring] = useState(false);

  // Helper to render original context with styled redactions
  const renderOriginalContext = (text: string) => {
    if (!text) return null;
    
    // Replace literal '\n' combinations with actual newline characters
    const normalizedText = text.replace(/\\n/g, '\n');
    const parts = normalizedText.split(/(<redact>.*?<\/redact>)/g);
    
    return (
      <p className="original-context-text" style={{ whiteSpace: 'pre-wrap' }}>
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

  const handleSecureDocument = async () => {
    if (!card.title) return;
    setIsSecuring(true);
    try {
      // We simulate a tool call here by sending a message to the agent
      // In a real ADK app, we might have a direct API for this.
      console.log(`GOVERNANCE ACTION: Securing ${card.document_name}`);
      alert(`Governance mandate initiated for ${card.document_name}. Moving to Restricted Vault.`);
    } finally {
      setIsSecuring(false);
    }
  };

  // ... (renderChart and getWeightColor logic stays same)
  // [KEEPING EXISTING RENDERCHART AND GETWEIGHTCOLOR LOGIC]
  const renderChart = (chartDataStr?: string) => {
    if (!chartDataStr) return null;
    try {
      const dataObj = JSON.parse(chartDataStr);
      const data = Object.keys(dataObj).map(key => ({ name: key, value: Number(dataObj[key]) }));
      const chartHeight = Math.max(200, data.length * 60);
      return (
        <div className="chart-container" style={{ width: '100%', marginTop: '1rem', background: 'rgba(0,0,0,0.05)', padding: '1rem', borderRadius: '8px', boxSizing: 'border-box' }}>
          <h4 style={{ marginBottom: '1rem', fontSize: '0.9rem', color: 'var(--deloitte-green)', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <BarChart2 size={16} /> Data Visualization
          </h4>
          <ResponsiveContainer width="100%" height={chartHeight}>
            <BarChart data={data} layout="vertical">
              <XAxis type="number" hide />
              <YAxis dataKey="name" type="category" axisLine={false} tickLine={false} tick={{ fill: 'var(--deloitte-black)', fontSize: 12 }} width={160} />
              <Tooltip cursor={{ fill: 'rgba(0,0,0,0.05)' }} contentStyle={{ backgroundColor: 'var(--deloitte-bg-main)', borderColor: 'var(--deloitte-border)', color: 'var(--deloitte-black)' }} />
              <Bar dataKey="value" fill="var(--deloitte-green)" radius={[0, 4, 4, 0]} barSize={20} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      );
    } catch (e) { return null; }
  };

  const getWeightColor = (weight: number = 100) => {
    if (weight >= 80) return 'var(--deloitte-green)';
    if (weight >= 50) return '#FFB600';
    return 'var(--deloitte-dark-gray)';
  };

  return (
    <article className={`deloitte-card ${card.pii_detected ? 'pii-alert' : ''}`}
      style={card.pii_detected ? { border: '2px solid #E0301E', boxShadow: '0 0 15px rgba(224, 48, 30, 0.2)' } : {}}>
      <header className="card-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <span className="industry-tag">{card.industry || 'Internal Data'}</span>
          {card.pii_detected && (
            <span className="pii-badge" style={{ background: '#E0301E', color: 'white', padding: '2px 8px', borderRadius: '4px', fontSize: '10px', fontWeight: 'bold' }}>
              PII DETECTED
            </span>
          )}
        </div>
        <div className="card-meta-right" style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div className="doc-weight-mini" style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
            <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: getWeightColor(card.document_weight) }}></div>
            <span style={{ fontSize: '11px', color: '#888', fontWeight: 'bold' }}>{card.document_weight || 100}%</span>
          </div>
          <a href={card.document_url || '#'} target="_blank" rel="noopener noreferrer" className="doc-id">
            Ref: {card.document_name}
          </a>
        </div>
      </header>

      <h2 className="card-title">{card.title}</h2>

      {card.governance_recommendation && card.governance_recommendation !== 'NONE' && (
        <div className="governance-banner" style={{ background: 'rgba(224, 48, 30, 0.1)', border: '1px solid #E0301E', padding: '10px', borderRadius: '6px', marginBottom: '15px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <div style={{ fontSize: '10px', fontWeight: 'bold', color: '#E0301E', textTransform: 'uppercase' }}>Governance Action Recommended</div>
            <div style={{ fontSize: '13px', color: 'var(--deloitte-black)' }}>{card.governance_recommendation}</div>
          </div>
          <button
            onClick={handleSecureDocument}
            disabled={isSecuring}
            className="deloitte-btn"
            style={{ background: '#E0301E', fontSize: '11px', padding: '4px 12px' }}
          >
            {isSecuring ? 'Securing...' : 'Secure Now'}
          </button>
        </div>
      )}

      <section className="card-body">
        <div className="info-block">
          <div className="info-block-header">
            <h3>{showOriginal ? 'Original Source Context' : 'Factual Information (Generalized)'}</h3>
            {card.original_context && (
              <button className="toggle-context-btn" onClick={() => setShowOriginal(!showOriginal)}>
                {showOriginal ? <EyeOff size={16} /> : <Eye size={16} />}
                <span>{showOriginal ? 'Hide Context' : 'View Source'}</span>
              </button>
            )}
          </div>
          <div className="context-container">
            {showOriginal && card.original_context ? renderOriginalContext(card.original_context) : <p>{card.factual_information}</p>}
          </div>
        </div>

        {card.insights && card.insights.length > 0 && (
          <div className="info-block">
            <h3>Key Insights</h3>
            <ul>{card.insights.map((insight, i) => <li key={i}>{insight}</li>)}</ul>
          </div>
        )}
        {card.chart_data && renderChart(card.chart_data)}
      </section>

      {card.key_metrics && card.key_metrics.length > 0 && (
        <footer className="card-footer metrics">
          {card.key_metrics.map((metric, i) => <span key={i} className="metric-pill"><Cpu size={14} /> {metric}</span>)}
        </footer>
      )}
    </article>
  );
};
