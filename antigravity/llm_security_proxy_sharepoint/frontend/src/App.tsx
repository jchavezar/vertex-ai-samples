import { useRef, useEffect, useState } from 'react';
import { useTerminalChat } from './hooks/useTerminalChat';
import { useDashboardStore } from './store/dashboardStore';
import { Cpu, User, LogOut, Network, Server, Database, ShieldAlert, Terminal } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { useMsal, useIsAuthenticated } from '@azure/msal-react';
import { loginRequest } from './authConfig';
import { InteractionRequiredAuthError } from '@azure/msal-browser';

function App() {
  const { instance, accounts } = useMsal();
  const isAuthenticated = useIsAuthenticated();
  const [token, setToken] = useState<string | null>(null);

  useEffect(() => {
    if (isAuthenticated && accounts[0]) {
      const request = {
        ...loginRequest,
        account: accounts[0]
      };

      const pingToken = async () => {
        try {
          const response = await instance.acquireTokenSilent(request);
          setToken(response.accessToken);
        } catch (error) {
          if (error instanceof InteractionRequiredAuthError) {
            instance.acquireTokenRedirect(request).catch(console.error);
          }
        }
      };

      pingToken();
      // Setup ping alive every 5 minutes to refresh token
      const interval = setInterval(pingToken, 5 * 60 * 1000);
      return () => clearInterval(interval);
    } else {
      setToken(null);
    }
  }, [isAuthenticated, accounts, instance]);

  const handleLogin = () => {
    instance.loginRedirect(loginRequest).catch(console.error);
  };

  const handleLogout = () => {
    instance.logoutRedirect({ postLogoutRedirectUri: "/" }).catch(console.error);
  };

  const [selectedModel, setSelectedModel] = useState('gemini-3-pro-preview');
  const [showTopology, setShowTopology] = useState(false);
  const { messages, input, handleInputChange, handleSubmit, isLoading, hasData } = useTerminalChat(token, selectedModel);
  const projectCards = useDashboardStore(s => s.projectCards);
  const endOfMessagesRef = useRef<HTMLDivElement>(null);
  const dataSectionRef = useRef<HTMLDivElement>(null);

  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      // Max height to prevent taking up too much screen space, enable scroll if larger
      const scrollHeight = textareaRef.current.scrollHeight;
      textareaRef.current.style.height = Math.min(scrollHeight, 150) + 'px';
    }
  }, [input]);

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
        <div className="pwc-search" style={{ cursor: 'pointer' }} onClick={() => setShowTopology(!showTopology)}>
          <Network size={18} /> <span>{showTopology ? 'Close Topology' : 'Topology'}</span>
        </div>
        <div className="pwc-auth">
          {isAuthenticated ? (
            <div className="auth-symbol">
              <div className="status-indicator active" title="Active Ping (Token Refreshed)"></div>
              <User size={18} />
              <span className="user-name">{accounts[0]?.name?.split(' ')[0]}</span>
              <button onClick={handleLogout} className="logout-btn" title="Log Out">
                <LogOut size={16} />
              </button>
            </div>
          ) : (
            <button onClick={handleLogin} className="login-btn">
              <User size={18} /> Sign In
            </button>
          )}
        </div>
      </header>

      {/* Main Content Split */}
      {showTopology ? (
        <div className="pwc-topology-wrapper" style={{ overflowX: 'auto' }}>
          <h2>Zero-Leak Architecture Topology</h2>
          <div className="topology-container" style={{ width: 'max-content', minWidth: '100%', paddingBottom: '40px' }}>
            <div className="flow-row">
              <div className="topology-node blue" style={{ width: '250px' }}>
                <User className="icon" size={32} />
                <h4>End User</h4>
                <p>React SPA (Vite)</p>
                <div className="node-detail">useTerminalChat()</div>
              </div>
              <div className="flow-edge flow-edge-horizontal" style={{ width: '120px' }}>
                SSE / HTTP
                <div className="line"></div>
              </div>
              <div className="topology-node secure" style={{ width: '320px' }}>
                <ShieldAlert className="icon" size={32} color="var(--pwc-red)" />
                <h4>Security Proxy</h4>
                <p>Google ADK / FastAPI</p>
                <div className="node-detail">LlmAgent / Session</div>
              </div>
              <div className="flow-edge flow-edge-horizontal" style={{ width: '120px' }}>
                Vertex API
                <div className="line"></div>
              </div>
              <div className="topology-node" style={{ width: '250px' }}>
                <Cpu className="icon" size={32} />
                <h4>LLM</h4>
                <p>Gemini 3 Pro / Flash</p>
                <div className="node-detail">gemini-3-pro-preview</div>
              </div>
            </div>

            <div className="flow-row">
              <div style={{ width: '250px' }}></div>
              <div style={{ width: '120px' }}></div>
              <div className="flow-edge flow-edge-vertical" style={{ width: '320px', justifyContent: 'center', position: 'relative' }}>
                <div className="line" style={{ margin: 0 }}></div>
                <div style={{ position: 'absolute', marginLeft: '30px', background: 'var(--pwc-bg-main)', padding: '0 8px', fontSize: '0.75rem', color: '#888', fontWeight: 600 }}>MCP TOOL CALL</div>
              </div>
              <div style={{ width: '120px' }}></div>
              <div style={{ width: '250px' }}></div>
            </div>

            <div className="flow-row">
              <div className="topology-node" style={{ borderColor: '#2e7d32', borderTopColor: '#2e7d32', width: '250px' }}>
                <Terminal className="icon" size={32} color="#2e7d32" />
                <h4>MCP Server</h4>
                <p>Python MCP SDK</p>
                <div className="node-detail">search_documents()</div>
              </div>
              <div className="flow-edge flow-edge-horizontal" style={{ width: '120px' }}>
                REST
                <div className="line"></div>
              </div>
              <div className="topology-node blue" style={{ width: '320px' }}>
                <Server className="icon" size={32} />
                <h4>Microsoft Graph</h4>
                <p>Entra ID / OAuth 2.0</p>
                <div className="node-detail">Client Credentials</div>
              </div>
              <div className="flow-edge flow-edge-horizontal" style={{ width: '120px' }}>
                Graph API
                <div className="line"></div>
              </div>
              <div className="topology-node" style={{ width: '250px' }}>
                <Database className="icon" size={32} color="#0078D4" />
                <h4>SharePoint</h4>
                <p>Protected Indices</p>
                <div className="node-detail">sites/FinancialDoc</div>
              </div>
            </div>
          </div>
        </div>
      ) : (
          <main className="pwc-main-wrapper">

        {/* Left Side: Chat Interface */}
        <section className="pwc-chat-sidebar">
          <div className="chat-header">
            <h2>Secure Enterprise Proxy</h2>
                <p style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '10px' }}>
                  Zero-Leak Protocol Active
                  <span className="status-indicator active" style={{ width: '6px', height: '6px', display: 'inline-block' }}></span>
                </p>
                <select
                  value={selectedModel}
                  onChange={(e) => setSelectedModel(e.target.value)}
                  style={{ background: 'transparent', border: '1px solid rgba(208, 74, 2, 0.3)', borderRadius: '4px', color: 'var(--pwc-orange)', padding: '4px 8px', outline: 'none', cursor: 'pointer', fontWeight: 'bold', fontSize: '11px', fontFamily: 'monospace' }}
                >
                  <option value="gemini-3-pro-preview" style={{ color: 'black' }}>gemini-3-pro-preview</option>
                  <option value="gemini-3-flash-preview" style={{ color: 'black' }}>gemini-3-flash-preview</option>
                </select>
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
                  <textarea
                    ref={textareaRef}
                    className="pwc-input pwc-textarea"
                value={input}
                onChange={handleInputChange}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        if (!isLoading && input.trim()) {
                          e.currentTarget.form?.requestSubmit();
                        }
                      }
                    }}
                    rows={1}
                placeholder="Ask a question..."
              />
                  <button type="submit" className="pwc-btn" disabled={isLoading || !input.trim()}>Send</button>
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
                  <a
                    href={card.document_url || `https://sockcop.sharepoint.com/sites/FinancialDocument/Shared%20Documents/${encodeURIComponent(card.document_name)}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="doc-id"
                    title="View Secure Source Document"
                  >
                    Ref: {card.document_name}
                  </a></header>

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
      )}
    </div>
  );
}

export default App;
