import { useRef, useEffect } from 'react';
import { useTerminalChat } from './hooks/useTerminalChat';
import { useDashboardStore } from './store/dashboardStore';
import { Terminal, ShieldAlert, Cpu } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

function App() {
  const { messages, input, handleInputChange, handleSubmit, isLoading, hasData } = useTerminalChat();
  const projectCards = useDashboardStore(s => s.projectCards);
  const endOfMessagesRef = useRef<HTMLDivElement>(null);
  const dataSectionRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endOfMessagesRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  useEffect(() => {
    if (dataSectionRef.current) {
      dataSectionRef.current.scrollLeft = dataSectionRef.current.scrollWidth;
    }
  }, [projectCards]);

  return (
    <div className="app-container">
      <div className="bg-shape" style={{ top: '-10%', right: '-5%', width: '800px', height: '800px', background: 'var(--accent-cyan)' }} />
      <div className="bg-shape" style={{ bottom: '-20%', left: '20%', width: '600px', height: '600px', background: 'var(--accent-orange)' }} />

      <section className="chat-section">
        <div className="chat-header">
          <h1><Terminal size={24} /> PWC Proxy</h1>
          <div className="subtitle">ZERO-LEAK PROTOCOL ACTIVE</div>
        </div>

        <div className="chat-messages">
          {messages.length === 0 && (
            <div className="message assistant" style={{ color: 'var(--accent-cyan)' }}>
              Awaiting query. Ready to securely scan SharePoint index...
            </div>
          )}
          {messages.map((m: any) => (
            <div key={m.id} className={`message ${m.role}`}>
              <ReactMarkdown>{m.content}</ReactMarkdown>
            </div>
          ))}
          {isLoading && !hasData && (
            <div className="message assistant" style={{ opacity: 0.7 }}>
              <span className="blink">_ Synthesizing intelligence...</span>
            </div>
          )}
          <div ref={endOfMessagesRef} />
        </div>

        <div className="chat-input-wrapper">
          <form onSubmit={handleSubmit} style={{ display: 'flex', gap: '16px' }}>
            <input
              className="chat-input"
              value={input}
              onChange={handleInputChange}
              placeholder="Query consulting intelligence..."
            />
            <button type="submit" className="submit-btn" disabled={isLoading}>SEND</button>
          </form>
        </div>
      </section>

      <section className="data-section" ref={dataSectionRef}>
        {!isLoading && projectCards.length === 0 && (
          <div className="empty-state-container">
            <div className="empty-state">
              <ShieldAlert size={80} strokeWidth={1} />
              <h2>SECURE ENTERPRISE PROXY</h2>
              <p>
                This is a Zero-Leak LLM architecture. All queries are processed securely. Sensitive PI/Financial data from connected SharePoint indices is automatically masked before rendering in the browser.
              </p>
            </div>

            <div className="use-case-grid">
              <div className="use-case-card">
                <div className="use-case-header">SAMPLE USE CASE</div>
                <h3 className="use-case-title">Audit & Compliance</h3>
                <p className="use-case-desc">
                  Analyze internal controls, SOD conflicts, and access governance across the organization's systems.
                </p>
                <div className="use-case-try">
                  Try: "What are common findings in IT general controls?"
                </div>
              </div>
              <div className="use-case-card">
                <div className="use-case-header">SAMPLE USE CASE</div>
                <h3 className="use-case-title">Executive Compensation</h3>
                <p className="use-case-desc">
                  Aggregate salary, equity, and bonus structures for key leadership roles against market benchmarks.
                </p>
                <div className="use-case-try">
                  Try: "How should we structure retention packages?"
                </div>
              </div>
            </div>
          </div>
        )}

        {isLoading && projectCards.length === 0 && (
          <div className="live-scanning">
            <div className="radar-spinner" />
            <h3 className="blink">Scanning SharePoint & Synthesizing Insights...</h3>
          </div>
        )}

        {projectCards.map((card, idx) => (
          <div key={idx} className="project-card">
            <div className="card-header">
              <span>{card.industry || 'CONFIDENTIAL'}</span>
              <span className="card-id">ID:{Math.random().toString(36).substr(2, 6).toUpperCase()}</span>
            </div>

            <h3 className="card-title">{card.title}</h3>

            <div className="card-section">
              <h4>FACTUAL INFORMATION (MASKED)</h4>
              <p className="card-text">{card.factual_information}</p>
            </div>

            <div className="card-section">
              <h4>INSIGHTS & RECOMMENDATIONS</h4>
              <ul className="insights-list">
                {card.insights && card.insights.map((insight, i) => (
                  <li key={i}>{insight}</li>
                ))}
              </ul>
            </div>

            <ul className="metrics-list">
              {card.key_metrics && card.key_metrics.map((metric, i) => (
                <li key={i} className="metric-item">
                  <Cpu size={18} strokeWidth={1.5} /> <span>{metric}</span>
                </li>
              ))}
            </ul>

            <div className="source-footer">
              SOURCE_ID: {card.document_name}
            </div>
          </div>
        ))}
      </section>
    </div>
  );
}

export default App;
