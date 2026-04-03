import { useState, useEffect } from 'react';
import { useMsal, useIsAuthenticated } from "@azure/msal-react";
import { loginRequest } from "./authConfig";
import { 
  Search, History, Folder, FileText, ChevronRight, Share2, 
  Shield, Settings, Sparkles, Send, Edit, Move, Check, 
  X, AlertTriangle, ExternalLink, RefreshCw, Layers
} from 'lucide-react';
import './App.css';

function App() {
  const { instance, accounts } = useMsal();
  const isAuthenticated = useIsAuthenticated();
  const [tokens, setTokens] = useState(null);

  useEffect(() => {
    if (isAuthenticated && accounts[0]) {
      const request = {
        ...loginRequest,
        account: accounts[0],
      };

      const pingToken = async () => {
        try {
          const response = await instance.acquireTokenSilent(request);
          setTokens({ accessToken: response.accessToken, idToken: response.idToken });
        } catch (error) {
          console.error("Token acquisition error:", error);
        }
      };

      pingToken();
      const interval = setInterval(pingToken, 5 * 60 * 1000);
      return () => clearInterval(interval);
    } else {
      setTokens(null);
    }
  }, [isAuthenticated, accounts, instance]);

  const [query, setQuery] = useState('');
  const [mounted, setMounted] = useState(false);
  const [activeTab, setActiveTab] = useState('search'); // 'search', 'sharepoint'
  const [isStreaming, setIsStreaming] = useState(false);
  const [answer, setAnswer] = useState('');
  const [sources, setSources] = useState([]);

  // Mock Data for aesthetics
  const historyItems = [
    { id: 1, title: 'Q1 ESG Assessment Rev 2', time: '2h ago' },
    { id: 2, title: 'Tax Risk Matrix LatAm', time: 'Yesterday' },
    { id: 3, title: 'Sustainability Vendor Audit', time: '3d ago' },
  ];

  const workspaceFolders = [
    { id: 'root', name: 'Strategic Portfolios', items: 12 },
    { id: 'f1', name: 'Compliance Vault', items: 5 },
    { id: 'f2', name: 'M&A Advisory temporary', items: 8 },
  ];

  useEffect(() => {
    setMounted(true);
  }, []);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query) return;
    
    setIsStreaming(true);
    setAnswer('');
    setSources([]);
    
    // Use fetch with body reader to support POST and custom headers (Auth)
    try {
      const response = await fetch('http://localhost:8000/api/search/stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(tokens?.idToken ? { 'X-Entra-Id-Token': tokens.idToken } : {})
        },
        body: JSON.stringify({ query })
      });

      if (!response.ok) {
         throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        
        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');
        for (const line of lines) {
          if (line.startsWith('data: ')) {
             const dataStr = line.substring(6);
             if (dataStr === '[DONE]') {
                setIsStreaming(false);
                break;
             }
             try {
               const data = JSON.parse(dataStr);
               if (data.text) {
                 setAnswer(prev => prev + data.text);
               }
             } catch (e) {
                // Skip partial JSON chunks
             }
          }
        }
      }
    } catch (err) {
      console.error("Stream failed:", err);
      setIsStreaming(false);
      setAnswer(prev => prev + `\n\n[Connection Error: ${err.message}]`);
    }
  };

  if (!mounted) return null;

  return (
    <div className="workspace-container">
      {/* Sidebar */}
      <aside className="sidebar glass-panel">
        <div className="brand">
          <Sparkles className="brand-icon text-glow" />
          <div className="brand-info">
            <span className="brand-name gradient-text">Synthesis</span>
            <span className="brand-tagline">By Accenture</span>
          </div>
        </div>

        <nav className="sidebar-nav">
          <div className="nav-group">
            <span className="nav-label">Navigation</span>
            <button 
              className={`nav-item ${activeTab === 'search' ? 'active' : ''}`}
              onClick={() => setActiveTab('search')}
            >
              <Search size={18} />
              <span>Synthesis Search</span>
            </button>
            <button 
              className={`nav-item ${activeTab === 'sharepoint' ? 'active' : ''}`}
              onClick={() => setActiveTab('sharepoint')}
            >
              <Folder size={18} />
              <span>SharePoint Vault</span>
            </button>
          </div>

          <div className="nav-group">
            <div className="nav-label-row">
              <span className="nav-label">Search History</span>
              <History size={14} className="text-muted" />
            </div>
            {historyItems.map(item => (
              <button key={item.id} className="nav-sub-item">
                <ChevronRight size={14} className="chevron" />
                <span className="truncate">{item.title}</span>
                <span className="sub-badge">{item.time}</span>
              </button>
            ))}
          </div>

          <div className="nav-group">
            <span className="nav-label">Secure Workspaces</span>
            {workspaceFolders.map(folder => (
              <button key={folder.id} className="nav-sub-item">
                <Folder size={14} className="text-muted" />
                <span className="truncate">{folder.name}</span>
                <span className="count-badge">{folder.items}</span>
              </button>
            ))}
          </div>
        </nav>

        <div className="sidebar-footer glass-panel">
          <div className="user-profile">
            <div className="avatar">SA</div>
            <div className="user-info">
              <span className="user-name">Strategic Advisor</span>
              <span className="user-role">Accenture Global</span>
            </div>
          </div>
          <button className="icon-btn" title="Settings">
            <Settings size={18} />
          </button>
        </div>
      </aside>

      {/* Main Content Pane */}
      <main className="main-canvas">
        <header className="canvas-header glass-panel">
          <div className="header-status">
            <div className="status-dot pulsed"></div>
            <span className="status-pill">Connected to SharePoint Governance Engine</span>
          </div>
          <div className="header-actions">
            {isAuthenticated ? (
              <button className="action-btn-sm" onClick={() => instance.logoutPopup()}>
                Logout ({accounts[0]?.username})
              </button>
            ) : (
              <button className="action-btn-sm premium" onClick={() => instance.loginRedirect(loginRequest)}>
                Login
              </button>
            )}
            <button className="action-btn-sm">
              <RefreshCw size={14} />
              Sync
            </button>
            <button className="action-btn-sm premium">
              <Shield size={14} />
              Compliance Shield
            </button>
          </div>
        </header>

        <div className="canvas-content">
          {activeTab === 'search' ? (
            <div className="search-workspace">
              <div className="welcome-banner">
                <h1 className="banner-title">SharePoint Synthesis Workspace</h1>
                <p className="banner-subtitle">Grounded discovery with integrated governance actions.</p>
              </div>

              {/* Chat/Search Area */}
              <div className="search-canvas">
                <div className="search-box-container glass-card">
                  <form onSubmit={handleSearch} className="search-form">
                    <div className="search-input-wrapper">
                      <Layers className="input-icon" />
                      <input 
                        type="text" 
                        placeholder="Search SharePoint documents, ask synthesis questions..." 
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        className="search-input"
                      />
                    </div>
                    <button type="submit" className="send-btn" disabled={!query || isStreaming}>
                      {isStreaming ? <RefreshCw size={18} className="spin" /> : <Send size={18} />}
                    </button>
                  </form>
                </div>

                {/* Simulated/Real Answers */}
                {(answer || isStreaming) && (
                  <div className="response-card glass-card">
                    <div className="response-header">
                      <div className="expert-badge">
                        <Sparkles size={14} />
                        <span>Executive Value Synth</span>
                      </div>
                      <span className="relevance-score">Grounding Score: 98%</span>
                    </div>
                    <div className="response-body">
                      <p>{answer}</p>
                      {isStreaming && <span className="cursor-blink">|</span>}
                    </div>

                    {sources.length > 0 && (
                      <div className="sources-section">
                        <span className="sources-title">Verified Sources:</span>
                        <div className="sources-list">
                          {sources.map((src, i) => (
                            <div key={i} className="source-chip glass-panel">
                              <FileText size={14} className="text-secondary" />
                              <span className="source-name truncate">{src.title}</span>
                              <span className="relevance-badge">{src.relevance}</span>
                              <ExternalLink size={14} className="source-link" />
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    <div className="governance-actions-strip">
                      <span className="action-strip-label">Direct Governance Actions:</span>
                      <button className="strip-action-btn">
                        <Edit size={14} />
                        Propose Change
                      </button>
                      <button className="strip-action-btn">
                        <Move size={14} />
                        Move to Vault
                      </button>
                      <button className="strip-action-btn danger">
                        <AlertTriangle size={14} />
                        Quarantine
                      </button>
                    </div>
                  </div>
                )}
              </div>

              {/* Quick Actions / Suggestions Grid */}
              {!answer && !isStreaming && (
                <div className="suggestions-grid">
                  <div className="suggestion-card glass-card">
                    <FileText className="suggest-icon" />
                    <h3>Synthesize Policy</h3>
                    <p>Compare tax policies across LatAm files.</p>
                  </div>
                  <div className="suggestion-card glass-card">
                    <Shield className="suggest-icon" />
                    <h3>Verify compliance</h3>
                    <p>Check ESG alignments in strategy vault.</p>
                  </div>
                  <div className="suggestion-card glass-card">
                    <Share2 className="suggest-icon" />
                    <h3>Actionable Summary</h3>
                    <p>Generate board compliance overview.</p>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="vault-workspace">
              {/* Vault workspace layout - simplified explorer */}
              <div className="explorer-header">
                <h2>SharePoint Vault Explorer</h2>
                <div className="explorer-path">
                  <span>Vault</span> / <span>Strategic Portfolios</span>
                </div>
              </div>
              <div className="explorer-grid">
                <div className="explorer-list glass-card">
                  <div className="list-item-header">
                    <span>Name</span>
                    <span>Action</span>
                  </div>
                  <div className="list-item">
                    <div className="item-name">
                      <FileText size={16} />
                      <span>Tax Policy Alignment 2026.pdf</span>
                    </div>
                    <div className="item-actions">
                      <button className="item-action-btn"><Edit size={14} /></button>
                      <button className="item-action-btn"><Move size={14} /></button>
                    </div>
                  </div>
                  <div className="list-item">
                    <div className="item-name">
                      <FileText size={16} />
                      <span>Sustainability Credit Matrix v3.xlsx</span>
                    </div>
                    <div className="item-actions">
                      <button className="item-action-btn"><Edit size={14} /></button>
                      <button className="item-action-btn"><Move size={14} /></button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

export default App;
