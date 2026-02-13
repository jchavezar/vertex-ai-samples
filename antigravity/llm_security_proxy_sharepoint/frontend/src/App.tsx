import { useRef, useEffect } from 'react';
import { useTerminalChat } from './hooks/useTerminalChat';
import { useDashboardStore } from './store/dashboardStore';
import { Search, Cpu } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

function App() {
  const { messages, input, handleInputChange, handleSubmit, isLoading, hasData } = useTerminalChat();
  const projectCards = useDashboardStore(s => s.projectCards);
  const endOfMessagesRef = useRef<HTMLDivElement>(null);
  const dataSectionRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endOfMessagesRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className="pwc-app">
      {/* PwC Style Header */}
      <header className="pwc-header">
        <div className="pwc-logo-container">
          <span className="pwc-logo">pwc</span>
        </div>
        <nav className="pwc-nav">
          <a href="#">Featured insights</a>
          <a href="#">Capabilities</a>
          <a href="#">Industries</a>
          <a href="#">Technology</a>
          <a href="#">About us</a>
          <a href="#">Careers</a>
        </nav>
        <div className="pwc-search">
          <Search size={18} /> <span>Search</span>
        </div>
      </header>

      {/* Main Content Split */}
      <main className="pwc-main-wrapper">

        {/* Left Side: Chat Interface */}
        <section className="pwc-chat-sidebar">
          <div className="chat-header">
            <h2>Secure Enterprise Proxy</h2>
            <p>Zero-Leak Protocol Active</p>
          </div>

          <div className="chat-messages">
            {messages.length === 0 && (
              <div className="message assistant welcome-msg">
                Welcome. I am ready to securely query internal PwC SharePoint indices.
              </div>
            )}
            {messages.map((m: any) => (
              <div key={m.id} className={`message ${m.role}`}>
                <ReactMarkdown>{m.content}</ReactMarkdown>
              </div>
            ))}
            {isLoading && !hasData && (
              <div className="message assistant loading-msg">
                Scanning securely...
              </div>
            )}
            <div ref={endOfMessagesRef} />
          </div>

          <div className="chat-input-area">
            <form onSubmit={handleSubmit}>
              <input
                className="pwc-input"
                value={input}
                onChange={handleInputChange}
                placeholder="Ask a question..."
              />
              <button type="submit" className="pwc-btn" disabled={isLoading}>Send</button>
            </form>
          </div>
        </section>

        {/* Right Side: Data & Results */}
        <section className="pwc-data-panel" ref={dataSectionRef}>
          {!isLoading && projectCards.length === 0 && (
            <div className="pwc-empty-hero">
              <div className="hero-text-box">
                <h1>Go way beyond traditional query tools</h1>
                <p>
                  It's not just about searching documents — it's what you extract securely. With proven zero-leak architecture and AI-driven insights, we help you leverage SharePoint data safely.
                </p>
              </div>
              <div className="hero-image-placeholder">
                {/* This represents the large image in the PwC screenshot */}
                <div className="image-overlay"></div>
              </div>
            </div>
          )}

          {isLoading && projectCards.length === 0 && (
            <div className="pwc-loading-state">
              <div className="spinner"></div>
              <h3>Synthesizing insights...</h3>
            </div>
          )}

          <div className="pwc-cards-grid">
            {projectCards.map((card, idx) => (
              <article key={idx} className="pwc-card">
                <header className="card-header">
                  <span className="industry-tag">{card.industry || 'Internal Data'}</span>
                  <span className="doc-id">Ref: {card.document_name}</span>
                </header>

                <h2 className="card-title">{card.title}</h2>

                <section className="card-body">
                  <div className="info-block">
                    <h3>Factual Information</h3>
                    <p>{card.factual_information}</p>
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
                </section>

                {card.key_metrics && card.key_metrics.length > 0 && (
                  <footer className="card-footer metrics">
                    {card.key_metrics.map((metric, i) => (
                      <span key={i} className="metric-pill"><Cpu size={14} /> {metric}</span>
                    ))}
                  </footer>
                )}
              </article>
            ))}
          </div>
        </section>

      </main>
    </div>
  );
}

export default App;
