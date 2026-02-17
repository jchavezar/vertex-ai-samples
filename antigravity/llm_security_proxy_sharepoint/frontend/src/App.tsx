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
} from "lucide-react";
import ReactMarkdown from "react-markdown";
import html2canvas from "html2canvas";
import { jsPDF } from "jspdf";
import { useMsal, useIsAuthenticated } from "@azure/msal-react";
import { loginRequest } from "./authConfig";
import { InteractionRequiredAuthError } from "@azure/msal-browser";
import { PromptGallery } from "./components/PromptGallery";
import { ProjectCardWidget } from "./components/ProjectCardWidget";
import { McpInspector } from "./components/McpInspector";
import { TelemetryTab } from "./components/TelemetryTab";
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

  const [selectedModel, setSelectedModel] = useState("gemini-3-pro-preview");
  const [showTopology, setShowTopology] = useState(false);
  const [activeAppTab, setActiveAppTab] = useState("proxy");
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
      <header className="pwc-header">
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
                <div className="node-detail">gemini-3-pro-preview</div>
              </div>
            </div>

            <div className="flow-row">
              <div style={{ width: "250px" }}></div>
              <div style={{ width: "120px" }}></div>
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
              <div style={{ width: "120px" }}></div>
              <div style={{ width: "250px" }}></div>
            </div>

            <div className="flow-row">
              <div
                className="topology-node"
                style={{
                  borderColor: "#2e7d32",
                  borderTopColor: "#2e7d32",
                  width: "250px",
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
              <div className="topology-node blue" style={{ width: "320px" }}>
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
              <section className="pwc-chat-sidebar">
                <div className="chat-header">
                  <h2>Secure Enterprise Proxy</h2>
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
                    <option value="gemini-3-pro-preview" style={{ color: "black" }}>
                      gemini-3-pro-preview
                    </option>
                    <option
                      value="gemini-3-flash-preview"
                      style={{ color: "black" }}
                >
                      gemini-3-flash-preview
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
                    {messages.map((m: any) => m.content ? (
                    <div key={m.id} className={`message ${m.role}`}>
                      <ReactMarkdown>{m.content}</ReactMarkdown>
                    </div>
                    ) : null)}

                    {publicInsight && (
                      <div className="message assistant" style={{ background: 'rgba(94, 174, 253, 0.05)', borderLeft: '3px solid #5eaefd' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px', color: '#5eaefd', fontSize: '11px', fontWeight: 'bold', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                          <Globe size={14} /> Public Web Consensus (Gemini 2.5 Flash)
                        </div>
                        <ReactMarkdown>{publicInsight}</ReactMarkdown>
                      </div>
                    )}

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
                {!isLoading && projectCards.length === 0 && (
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
                    isLoading={isLoading}
                  />
                )}

                {isLoading && projectCards.length === 0 && (
                  <div className="pwc-loading-state">
                    <div className="spinner"></div>
                      <h3>{thoughtStatus ? thoughtStatus.message : 'Synthesizing insights...'}</h3>
                  </div>
                )}

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
