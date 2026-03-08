import { useRef, useEffect, useState } from "react";
import { useTerminalChat } from "./hooks/useTerminalChat";
import { useDashboardStore } from "./store/dashboardStore";
import {
  Cpu,
  User,
  LogOut,
  Server,
  Database,
  ShieldAlert,
  Terminal,
  Download,
  CheckCircle,
  Globe,
  Search,
  ChevronUp,
  Maximize2,
  PanelLeft
} from "lucide-react";
import { MarkdownRenderer } from "./components/MarkdownRenderer";
import html2canvas from "html2canvas";
import { jsPDF } from "jspdf";
import { useMsal, useIsAuthenticated } from "@azure/msal-react";
import { loginRequest } from "./authConfig";
import { InteractionRequiredAuthError } from "@azure/msal-browser";
import { PromptGallery } from "./components/PromptGallery";
import { ProjectCardWidget } from "./components/ProjectCardWidget";
import { McpInspector } from "./components/McpInspector";
import { TelemetryTab } from "./components/TelemetryTab";
import { DocumentWorkspaceV2 } from "./components/DocumentWorkspaceV2";
import "./PromptGallery.css";

const GeminiSparkleIcon = ({ className = "" }: { className?: string }) => (
  <svg
    className={`gemini-sparkle-icon ${className}`}
    width="22"
    height="22"
    viewBox="0 0 24 24"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
  >
    <defs>
      <linearGradient id="gemini-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stopColor="#5eaefd" />
        <stop offset="50%" stopColor="#b47dff" />
        <stop offset="100%" stopColor="#f36c5b" />
      </linearGradient>
    </defs>
    <path
      d="M12 0C12 6.627 6.627 12 0 12C6.627 12 12 17.373 12 24C12 17.373 17.373 12 24 12C17.373 12 12 6.627 12 0Z"
      fill="url(#gemini-gradient)"
    />
  </svg>
);


function App() {
  const { instance, accounts } = useMsal();
  const isAuthenticated = useIsAuthenticated();
  const [token, setToken] = useState<string | null>(null);

  useEffect(() => {
    if (isAuthenticated && accounts[0]) {
      const request = {
        ...loginRequest,
        account: accounts[0],
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
    instance
      .logoutRedirect({ postLogoutRedirectUri: "/" })
      .catch(console.error);
  };

  const [selectedModel, setSelectedModel] = useState("gemini-3-flash-preview");
  const [showTopology, setShowTopology] = useState(false);
  const [activeAppTab, setActiveAppTab] = useState("proxy");
  const [chatMode, setChatMode] = useState<'default'|'wide'|'overlay'>('default');
  const {
    messages,
    input,
    handleInputChange,
    handleSubmit,
    isLoading,
    thoughtStatus,
    usedSharePoint,
    telemetry,
    reasoningSteps,
    tokenUsage,
    publicInsight
  } = useTerminalChat(token, selectedModel);
  const projectCards = useDashboardStore((s) => s.projectCards);
  const [isPublicInsightExpanded, setIsPublicInsightExpanded] = useState(true);
  const [hasCollapsedForQuery, setHasCollapsedForQuery] = useState(false);

  useEffect(() => {
    if (messages.length === 0) {
      setIsPublicInsightExpanded(true);
      setHasCollapsedForQuery(false);
    }
  }, [messages.length]);

  useEffect(() => {
    if (projectCards.length > 0 && !hasCollapsedForQuery) {
      setIsPublicInsightExpanded(false);
      setHasCollapsedForQuery(true);
    }
  }, [projectCards.length, hasCollapsedForQuery]);

  const endOfMessagesRef = useRef<HTMLDivElement>(null);
  const dataSectionRef = useRef<HTMLDivElement>(null);

  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      // Max height to prevent taking up too much screen space, enable scroll if larger
      const scrollHeight = textareaRef.current.scrollHeight;
      textareaRef.current.style.height = Math.min(scrollHeight, 150) + "px";
    }
  }, [input]);

  useEffect(() => {
    endOfMessagesRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const [isExporting, setIsExporting] = useState(false);

  const exportToPDF = async () => {
    if (!dataSectionRef.current || projectCards.length === 0) return;
    setIsExporting(true);

    try {
      // Find the grid container to capture
      const gridElement = dataSectionRef.current.querySelector(
        ".pwc-cards-grid",
      ) as HTMLElement;
      if (!gridElement) return;

      const canvas = await html2canvas(gridElement, {
        scale: 2, // High resolution
        useCORS: true,
        backgroundColor: "#1E1E1E", // Match the dark theme background
      });

      const imgData = canvas.toDataURL("image/png");
      const pdf = new jsPDF("p", "mm", "a4");
      const pdfWidth = pdf.internal.pageSize.getWidth();
      const pdfHeight = (canvas.height * pdfWidth) / canvas.width;

      // Add a header
      pdf.setFillColor(208, 74, 2); // PwC Orange
      pdf.rect(0, 0, pdfWidth, 20, "F");
      pdf.setTextColor(255, 255, 255);
      pdf.setFontSize(16);
      pdf.text("PwC Secure Intelligence Briefing", 14, 13);

      pdf.setTextColor(100, 100, 100);
      pdf.setFontSize(10);
      pdf.text(`Generated: ${new Date().toLocaleDateString()}`, 14, 28);

      pdf.addImage(imgData, "PNG", 0, 35, pdfWidth, pdfHeight);
      pdf.save("PwC_Intelligence_Briefing.pdf");
    } catch (error) {
      console.error("Failed to export PDF:", error);
      alert("Failed to generate the PDF briefing.");
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <div className="pwc-app">
      {/* PwC Style Header */}
      <header className="pwc-header pwc-header-vibrant">
        <div className="pwc-logo-container">
          <span className="pwc-logo">pwc</span>
        </div>
        <nav className="pwc-nav">
          <a
            href="#"
            className={
              activeAppTab === "proxy" && !showTopology ? "active" : ""
            }
            onClick={(e) => {
              e.preventDefault();
              setActiveAppTab("proxy");
              setShowTopology(false);
            }}
          >
            Secure Enterprise Proxy
          </a>
          <a
            href="#"
            className={
              activeAppTab === "workspace" && !showTopology ? "active" : ""
            }
            onClick={(e) => {
              e.preventDefault();
              setActiveAppTab("workspace");
              setShowTopology(false);
            }}
          >
            Document Workspace
          </a>
          <a
            href="#"
            className={
              activeAppTab === "inspector" && !showTopology ? "active" : ""
            }
            onClick={(e) => {
              e.preventDefault();
              setActiveAppTab("inspector");
              setShowTopology(false);
            }}
          >
            MCP Inspector
          </a>
          <a
            href="#"
            className={showTopology ? "active" : ""}
            onClick={(e) => {
              e.preventDefault();
              setShowTopology(true);
            }}
          >
            Zero-Leak Topology
          </a>
          <a
            href="#"
            className={
              activeAppTab === "telemetry" && !showTopology ? "active" : ""
            }
            onClick={(e) => {
              e.preventDefault();
              setActiveAppTab("telemetry");
              setShowTopology(false);
            }}
          >
            Execution Latency
          </a>
        </nav>
        <div className="pwc-header-right">
          {projectCards.length > 0 &&
            !showTopology &&
            activeAppTab === "proxy" && (
              <button
                onClick={exportToPDF}
                disabled={isExporting}
                className="pwc-btn"
              style={{
                padding: "6px 16px",
                display: "flex",
                alignItems: "center",
                gap: "8px",
                fontSize: "0.85rem",
              }}
              title="Export as Executive Briefing PDF"
            >
              <Download size={16} />
                {isExporting ? "Exporting..." : "Export Briefing"}
              </button>
            )}

          <div className="pwc-auth">
            {isAuthenticated ? (
              <div className="auth-symbol">
                <div
                  className="status-indicator active"
                  title="Active Ping (Token Refreshed)"
                ></div>
                <User size={18} />
                <span className="user-name">
                  {accounts[0]?.name?.split(" ")[0]}
                </span>
                <button
                  onClick={handleLogout}
                  className="logout-btn"
                  title="Log Out"
                >
                  <LogOut size={16} />
                </button>
              </div>
            ) : (
              <button onClick={handleLogin} className="login-btn">
                <User size={18} /> Sign In
              </button>
            )}
          </div>
        </div>
      </header>

      {/* Main Content Split */}
      {showTopology ? (
        <div className="pwc-topology-wrapper" style={{ overflowX: "auto" }}>
          <h2>Zero-Leak Architecture Topology</h2>
          <div
            className="topology-container"
            style={{
              width: "max-content",
              minWidth: "100%",
              paddingBottom: "40px",
            }}
          >
            <div className="flow-row">
              <div className="topology-node blue" style={{ width: "250px" }}>
                <User className="icon" size={32} />
                <h4>End User</h4>
                <p>React SPA (Vite)</p>
                <div className="node-detail">useTerminalChat()</div>
              </div>
              <div
                className="flow-edge flow-edge-horizontal"
                style={{ width: "120px" }}
              >
                SSE / HTTP
                <div className="line"></div>
              </div>
              <div className="topology-node secure" style={{ width: "320px" }}>
                <ShieldAlert
                  className="icon"
                  size={32}
                  color="var(--pwc-red)"
                />
                <h4>Security Proxy</h4>
                <p>Google ADK / FastAPI</p>
                <div className="node-detail">LlmAgent / Session</div>
              </div>
              <div
                className="flow-edge flow-edge-horizontal"
                style={{ width: "120px" }}
              >
                Vertex API
                <div className="line"></div>
              </div>
              <div className="topology-node" style={{ width: "250px" }}>
                <Cpu className="icon" size={32} />
                <h4>LLM</h4>
                <p>Gemini 3 Pro / Flash</p>
                <div className="node-detail">{selectedModel}</div>
              </div>
              <div style={{ width: "370px" }}></div>
            </div>

            <div className="flow-row">
              <div style={{ width: "370px" }}></div>
              <div
                className="flow-edge flow-edge-vertical"
                style={{
                  width: "320px",
                  justifyContent: "center",
                  position: "relative",
                }}
              >
                <div className="line" style={{ margin: 0 }}></div>
                <div
                  style={{
                    position: "absolute",
                    marginLeft: "30px",
                    background: "var(--pwc-bg-main)",
                    padding: "0 8px",
                    fontSize: "0.75rem",
                    color: "#888",
                    fontWeight: 600,
                  }}
                >
                  MCP TOOL CALL
                </div>
              </div>
              <div style={{ width: "740px" }}></div>
            </div>

            <div className="flow-row">
              <div style={{ width: "370px" }}></div>
              <div
                className="topology-node"
                style={{
                  borderColor: "#2e7d32",
                  borderTopColor: "#2e7d32",
                  width: "320px",
                }}
              >
                <Terminal className="icon" size={32} color="#2e7d32" />
                <h4>MCP Server</h4>
                <p>Python MCP SDK</p>
                <div className="node-detail">search_documents()</div>
              </div>
              <div
                className="flow-edge flow-edge-horizontal"
                style={{ width: "120px" }}
              >
                REST
                <div className="line"></div>
              </div>
              <div className="topology-node blue" style={{ width: "250px" }}>
                <Server className="icon" size={32} />
                <h4>Microsoft Graph</h4>
                <p>Entra ID / OAuth 2.0</p>
                <div className="node-detail">Client Credentials</div>
              </div>
              <div
                className="flow-edge flow-edge-horizontal"
                style={{ width: "120px" }}
              >
                Graph API
                <div className="line"></div>
              </div>
              <div className="topology-node" style={{ width: "250px" }}>
                <Database className="icon" size={32} color="#0078D4" />
                <h4>SharePoint</h4>
                <p>Protected Indices</p>
                <div className="node-detail">sites/FinancialDoc</div>
              </div>
            </div>
          </div>
        </div>
      ) : activeAppTab === "workspace" ? (
        <DocumentWorkspaceV2 token={token || undefined} />
      ) : activeAppTab === "inspector" ? (
        <McpInspector
          goHome={() => {
            setActiveAppTab("proxy");
            setShowTopology(false);
          }}
          token={token || undefined}
        />
        ) : activeAppTab === "telemetry" ? (
          <TelemetryTab telemetry={telemetry} reasoningSteps={reasoningSteps} tokenUsage={tokenUsage} />
      ) : (
            <main className="pwc-main-wrapper">
              {/* Left Side: Chat Interface */}
              <section className={`pwc-chat-sidebar ${chatMode !== 'default' ? chatMode : ''}`}>
                <div className="chat-header">
                  <div className="chat-header-top">
                    <h2>Secure Enterprise Proxy</h2>
                    <div className="chat-mode-controls">
                      <button 
                        className={`chat-mode-btn ${chatMode === 'default' ? 'active' : ''}`} 
                        onClick={() => setChatMode('default')}
                        title="Default Width"
                      >
                        <PanelLeft size={18} />
                      </button>
                      <button 
                        className={`chat-mode-btn ${chatMode === 'wide' ? 'active' : ''}`} 
                        onClick={() => setChatMode('wide')}
                        title="Wide Mode"
                      >
                        <Maximize2 size={18} />
                      </button>
                      <button 
                        className={`chat-mode-btn ${chatMode === 'overlay' ? 'active' : ''}`} 
                        onClick={() => setChatMode('overlay')}
                        title="Fullscreen Overlay"
                      >
                        <Terminal size={18} />
                      </button>
                    </div>
                  </div>
                  <p
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: "8px",
                      marginBottom: "10px",
                    }}
                  >
                    Zero-Leak Protocol Active
                    <span
                      className="status-indicator active"
                      style={{
                        width: "6px",
                        height: "6px",
                        display: "inline-block",
                      }}
                    ></span>
                  </p>
                  <select
                    value={selectedModel}
                    onChange={(e) => setSelectedModel(e.target.value)}
                    style={{
                      background: "transparent",
                      border: "1px solid rgba(208, 74, 2, 0.3)",
                      borderRadius: "4px",
                      color: "var(--pwc-orange)",
                      padding: "4px 8px",
                      outline: "none",
                      cursor: "pointer",
                      fontWeight: "bold",
                      fontSize: "11px",
                      fontFamily: "monospace",
                    }}
                  >
                    <option value="gemini-3.1-flash-lite" style={{ color: "black" }}>
                      gemini-3.1-flash-lite
                    </option>
                    <option value="gemini-3-pro-preview" style={{ color: "black" }}>
                      gemini-3-pro-preview
                    </option>
                    <option value="gemini-3-flash-preview" style={{ color: "black" }}>
                      gemini-3-flash-preview
                    </option>
                    <option value="gemini-2.5-flash" style={{ color: "black" }}>
                      gemini-2.5-flash
                    </option>
                  </select>
                </div>

                <div className="chat-messages">
                  {messages.length === 0 && (
                    <div className="message assistant welcome-msg">
                      Welcome. I am ready to securely query internal PwC SharePoint
                      indices.
                    </div>
                  )}
                    {messages.map((m: any, index: number) => m.content ? (
                    <div key={m.id} className={`message ${m.role}`}>
                      <MarkdownRenderer content={m.content} />
                      
                      {/* Card Relationship Visualization */}
                      {m.role === 'assistant' && 
                       index === messages.length - 1 && 
                       projectCards.length > 0 && (
                        <div style={{
                          marginTop: '16px',
                          display: 'inline-flex',
                          alignItems: 'center',
                          gap: '6px',
                          background: 'rgba(208, 74, 2, 0.08)',
                          color: 'var(--pwc-orange)',
                          padding: '6px 12px',
                          borderRadius: '16px',
                          fontSize: '0.8rem',
                          fontWeight: 600,
                          border: '1px solid rgba(208, 74, 2, 0.2)'
                        }}>
                          <Database size={14} /> 
                          Related: {projectCards.length} Data Card{projectCards.length > 1 ? 's' : ''} Generated &#8594;
                        </div>
                      )}
                    </div>
                    ) : null)}



                    {(isLoading || thoughtStatus) && (
                    <div className="gemini-loading-wrapper">
                      <div className="gemini-search-pill">
                          {usedSharePoint && <img src="/sharepoint-logo.svg" className="sharepoint-used-badge" alt="SharePoint Used" title="SharePoint indices searched" />}
                        <div className="sharepoint-icon-wrapper">
                            {thoughtStatus ? (
                              thoughtStatus.icon === 'search' || thoughtStatus.icon === 'database' || thoughtStatus.icon === 'file-search' ? <img src="/sharepoint-logo.svg" alt="SharePoint" className="sharepoint-logo" /> :
                                thoughtStatus.icon === 'shield-alert' ? <ShieldAlert color="var(--pwc-orange)" size={20} /> :
                                  thoughtStatus.icon === 'check-circle' ? <CheckCircle color="var(--pwc-orange)" size={20} /> :
                                    <GeminiSparkleIcon />
                            ) : <GeminiSparkleIcon />}
                        </div>
                        <div className="gemini-loading-text">
                            <div className="gemini-loading-title">Google ADK</div>
                            <div className={`gemini-loading-subtitle ${thoughtStatus?.pulse ? 'pulsing-text' : ''}`}>{thoughtStatus ? thoughtStatus.message : 'Synthesizing...'}</div>
                        </div>
                      </div>
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
                        if (e.key === "Enter" && !e.shiftKey) {
                          e.preventDefault();
                          if (!isLoading && input.trim()) {
                            e.currentTarget.form?.requestSubmit();
                          }
                        }
                      }}
                      rows={1}
                      placeholder="Ask a question..."
                    />
                    <button
                      type="submit"
                      className="pwc-btn"
                      disabled={isLoading || !input.trim()}
                    >
                      Send
                    </button>
                  </form>
                </div>
              </section>

              {/* Right Side: Data & Results */}
              <section className="pwc-data-panel" ref={dataSectionRef}>
                    {/* Initial Suggestion Gallery: Keep visible until we have ACTUAL assistant content or project cards */}
                    {messages.filter(m => m.role === 'assistant' && m.content.trim().length > 0).length === 0 && projectCards.length === 0 && (
                  <PromptGallery
                    onSelectPrompt={(prompt) => {
                      const syntheticEvent = {
                        target: { value: prompt },
                      } as React.ChangeEvent<HTMLTextAreaElement>;
                      handleInputChange(syntheticEvent);
                      setTimeout(() => {
                        if (textareaRef.current && textareaRef.current.form) {
                          textareaRef.current.form.requestSubmit();
                        }
                      }, 100);
                        }}
                  />
                )}


                    {/* Discovery Status during loading */}
                    {isLoading && (
                      <div className="gemini-loading-wrapper" style={{ marginBottom: '20px', display: 'flex', justifyContent: 'center' }}>
                        <div className={`gemini-search-pill ${usedSharePoint ? 'active' : ''}`}
                          style={{
                            background: '#fff',
                            border: '1px solid var(--pwc-border)',
                            padding: '12px 24px',
                            borderRadius: '30px',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '12px',
                            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.05)'
                          }}>
                          <div className="sharepoint-icon-wrapper" style={{
                            background: usedSharePoint ? 'var(--pwc-orange)' : '#f0f0f0',
                            padding: '8px',
                            borderRadius: '50%',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center'
                          }}>
                            {usedSharePoint ? <img src="/sharepoint-logo.svg" alt="SharePoint" style={{ width: '16px', height: '16px', filter: 'brightness(0) invert(1)' }} /> : <Search size={16} color="#666" />}
                          </div>
                          <div style={{ display: 'flex', flexDirection: 'column' }}>
                            <span style={{ fontSize: '10px', fontWeight: 700, color: 'var(--pwc-orange)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                              {usedSharePoint ? 'SECURE INDEX HIT' : 'SCANNING ECOSYSTEM'}
                            </span>
                            <span style={{ fontSize: '14px', color: '#333', fontWeight: 500 }}>
                              {thoughtStatus?.message || 'Synthesizing Intelligence...'}
                            </span>
                          </div>
                        </div>
                      </div>
                    )}

                <div style={{ marginBottom: projectCards.length > 0 && publicInsight ? '24px' : '0' }}>
                    {publicInsight && (
                      <div className="pwc-card" style={{ 
                          background: 'linear-gradient(135deg, #1E1E1E 0%, #2A2A2A 100%)', 
                          border: '1px solid rgba(94, 174, 253, 0.3)',
                          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.15)',
                          borderRadius: '16px',
                          overflow: 'hidden',
                          cursor: 'pointer', 
                          transition: 'all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1)'
                        }} 
                        onClick={() => setIsPublicInsightExpanded(!isPublicInsightExpanded)}
                        onMouseEnter={(e) => {
                          e.currentTarget.style.transform = 'translateY(-2px)';
                          e.currentTarget.style.boxShadow = '0 12px 40px rgba(94, 174, 253, 0.2)';
                        }}
                        onMouseLeave={(e) => {
                          e.currentTarget.style.transform = 'translateY(0)';
                          e.currentTarget.style.boxShadow = '0 8px 32px rgba(0, 0, 0, 0.15)';
                        }}
                      >
                        <div className="card-header" style={{ 
                            marginBottom: isPublicInsightExpanded ? '16px' : '0', 
                            display: 'flex', 
                            justifyContent: 'space-between', 
                            alignItems: 'center', 
                            transition: 'margin-bottom 0.3s ease',
                            padding: '16px 24px',
                            background: 'rgba(255, 255, 255, 0.03)',
                            borderBottom: isPublicInsightExpanded ? '1px solid rgba(255, 255, 255, 0.08)' : 'none'
                          }}>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', color: '#fff', fontSize: '13px', fontWeight: '800', textTransform: 'uppercase', letterSpacing: '0.1em' }}>
                            <div style={{ 
                              background: 'linear-gradient(135deg, #5eaefd 0%, #b47dff 100%)', 
                              WebkitBackgroundClip: 'text',
                              WebkitTextFillColor: 'transparent',
                              display: 'flex',
                              alignItems: 'center',
                              gap: '8px'
                            }}>
                              <Globe size={18} color="#5eaefd" /> PUBLIC WEB CONSENSUS
                            </div>
                            <span style={{ 
                              background: 'rgba(94, 174, 253, 0.15)', 
                              color: '#5eaefd', 
                              padding: '2px 8px', 
                              borderRadius: '12px', 
                              fontSize: '10px',
                            }}>
                              gemini-3.1-flash-lite-preview
                            </span>
                          </div>
                          <div style={{ 
                            color: 'rgba(255, 255, 255, 0.6)', 
                            display: 'flex', 
                            alignItems: 'center', 
                            gap: '6px', 
                            fontSize: '11px', 
                            fontWeight: '600',
                            letterSpacing: '0.05em'
                          }}>
                            {isPublicInsightExpanded ? 'COLLAPSE' : 'EXPAND'}
                            <div style={{ 
                              background: 'rgba(255, 255, 255, 0.1)', 
                              borderRadius: '50%', 
                              padding: '4px',
                              display: 'flex',
                              transition: 'transform 0.3s ease',
                              transform: isPublicInsightExpanded ? 'rotate(0deg)' : 'rotate(180deg)'
                            }}>
                              <ChevronUp size={14} />
                            </div>
                          </div>
                        </div>
                        {isPublicInsightExpanded && (
                          <div className="card-content" style={{ 
                              fontSize: '15px', 
                              lineHeight: '1.7', 
                              color: '#E0E0E0', 
                              padding: '0 24px 24px 24px',
                              fontWeight: '400'
                            }}>
                            <MarkdownRenderer content={publicInsight} chatMode={chatMode} />
                          </div>
                        )}
                      </div>
                    )}
                </div>

                <div className="pwc-cards-grid">
                  {projectCards.map((card, idx) => (
                    <ProjectCardWidget key={idx} card={card as any} />
                  ))}
                </div>
              </section>
            </main>
      )}
    </div>
  );
}

export default App;
