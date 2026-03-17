import { useRef, useEffect, useState } from "react";
import { useTerminalChat } from "./hooks/useTerminalChat";
import { useDashboardStore } from "./store/dashboardStore";
import {
  User,
  LogOut,
  Database,
  ShieldAlert,
  Terminal,
  Download,
  CheckCircle,
  Globe,
 
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
import { ProjectCardWidget } from "./components/ProjectCardWidget";
import type { ProjectCardData } from "./components/ProjectCardWidget";
import { McpInspector } from "./components/McpInspector";
import { TelemetryTab } from "./components/TelemetryTab";
import { DocumentWorkspaceV2 } from "./components/DocumentWorkspaceV2";
import { GeMcpFlow } from "./components/GeMcpFlow";
import { AuthRequestFlow } from "./components/AuthRequestFlow";
import type { Message } from "@ai-sdk/react";
import { TopologyView } from "./components/TopologyView";
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


const PROMPT_POOL = [
  "What is the salary of a CFO?",
  "What is a competitive compensation structure for a CFO?",
  "What equity vesting schedules are standard for C-suite?",
  "What bonus target percentages are typical for executives?",
  "How should we structure executive retention packages?",
  "What internal control weaknesses are common in tech?",
  "What SLA terms are standard in enterprise agreements?",
  "What are the most critical security vulnerabilities?",
  "What valuation multiples are appropriate for SaaS?",
  "How to structure retention during acquisitions?",
  "What is the true total cost of an acquisition?",
  "How does management turnover affect financial performance?"
];

function App() {
  const { instance, accounts } = useMsal();
  const isAuthenticated = useIsAuthenticated();
  const [tokens, setTokens] = useState<{accessToken: string, idToken: string} | null>(null);

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
      setTokens(null);
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
  const [routerMode, setRouterMode] = useState<'all_mcp'|'ge_mcp'>('all_mcp');

  const effectiveTokens = tokens;

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
    publicInsight,
    isPublicInsightStreaming
  } = useTerminalChat(effectiveTokens, selectedModel, routerMode);
  const projectCards = useDashboardStore((s) => s.projectCards);
  const [isPublicInsightExpanded, setIsPublicInsightExpanded] = useState(false);
  const [isProjectCardsExpanded, setIsProjectCardsExpanded] = useState(false);
  const [hasCollapsedForQuery, setHasCollapsedForQuery] = useState(false);
  const [suggestedPrompts, setSuggestedPrompts] = useState<string[]>([]);

  useEffect(() => {
    if (messages.length === 0) {
      setIsPublicInsightExpanded(false);
      setIsProjectCardsExpanded(false);
      setHasCollapsedForQuery(false);
    }
    // Update suggestions on each query
    const shuffled = [...PROMPT_POOL].sort(() => 0.5 - Math.random());
    setSuggestedPrompts(shuffled.slice(0, 3));
  }, [messages.length]);

  useEffect(() => {
    if (projectCards.length > 0 && !hasCollapsedForQuery) {
      setIsProjectCardsExpanded(false); // keep it closed by default as requested
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
        ".deloitte-cards-grid",
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
      pdf.setFillColor(134, 188, 37); // Deloitte Orange
      pdf.rect(0, 0, pdfWidth, 20, "F");
      pdf.setTextColor(255, 255, 255);
      pdf.setFontSize(16);
      pdf.text("Deloitte Enterprise Shield Briefing", 14, 13);

      pdf.setTextColor(100, 100, 100);
      pdf.setFontSize(10);
      pdf.text(`Generated: ${new Date().toLocaleDateString()}`, 14, 28);

      pdf.addImage(imgData, "PNG", 0, 35, pdfWidth, pdfHeight);
      pdf.save("Deloitte_Enterprise_Shield_Briefing.pdf");
    } catch (error) {
      console.error("Failed to export PDF:", error);
      alert("Failed to generate the PDF briefing.");
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <div className="deloitte-app">
      {/* Deloitte Style Header */}
      <header className="deloitte-header deloitte-header-vibrant">
        <div className="deloitte-logo-container">
          <span className="deloitte-logo" style={{color: "black", textTransform: "none", fontWeight: 800}}>Deloitte.</span>
        </div>
        <nav className="deloitte-nav">
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
            Deloitte Enterprise Shield
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
          <a
            href="#"
            className={
              activeAppTab === "ge_flow" && !showTopology ? "active" : ""
            }
            onClick={(e) => {
              e.preventDefault();
              setActiveAppTab("ge_flow");
              setShowTopology(false);
            }}
          >
            Chat Flow
          </a>
          <a
            href="#"
            className={
              activeAppTab === "auth_flow" && !showTopology ? "active" : ""
            }
            onClick={(e) => {
              e.preventDefault();
              setActiveAppTab("auth_flow");
              setShowTopology(false);
            }}
          >
            Auth Flow
          </a>
        </nav>
        <div className="deloitte-header-right">
          {projectCards.length > 0 &&
            !showTopology &&
            activeAppTab === "proxy" && (
              <button
                onClick={exportToPDF}
                disabled={isExporting}
                className="deloitte-btn"
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

          <div className="deloitte-auth" style={{ display: 'flex', alignItems: 'center' }}>
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
                  title="Log Out (Entra ID)"
                >
                  <LogOut size={16} />
                </button>
              </div>
            ) : (
              <button onClick={handleLogin} className="login-btn">
                <User size={18} /> Sign In with Microsoft
              </button>
            )}
          </div>
        </div>
      </header>

      {/* Main Content Split */}
      {showTopology ? (
        <div className="deloitte-topology-wrapper" style={{ overflowX: "auto" }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%', paddingRight: '24px' }}>
            <h2>Zero-Leak Architecture Topology</h2>
            <select
              value={routerMode}
              onChange={(e) => setRouterMode(e.target.value as 'all_mcp'|'ge_mcp')}
              style={{
                background: "transparent",
                border: "1px solid rgba(134, 188, 37, 0.3)",
                borderRadius: "4px",
                color: "var(--deloitte-green)",
                padding: "6px 12px",
                outline: "none",
                cursor: "pointer",
                fontWeight: "bold",
                fontSize: "12px",
                fontFamily: "monospace",
              }}
              title="Select Routing Architecture"
            >
              <option value="all_mcp" style={{ color: "black" }}>
                All MCP (Direct)
              </option>
              <option value="ge_mcp" style={{ color: "black" }}>
                GE + MCP (Router)
              </option>
            </select>
          </div>
          <div
            className="topology-container"
            style={{
              width: "100%",
              height: "calc(100vh - 120px)",
              paddingBottom: "40px",
            }}
          >
            <TopologyView routerMode={routerMode} />
          </div>
        </div>
      ) : activeAppTab === "workspace" ? (
        <DocumentWorkspaceV2 token={tokens?.accessToken || undefined} />
      ) : activeAppTab === "inspector" ? (
        <McpInspector
          goHome={() => {
            setActiveAppTab("proxy");
            setShowTopology(false);
          }}
          token={tokens?.accessToken || undefined}
        />
        ) : activeAppTab === "telemetry" ? (
          <TelemetryTab telemetry={telemetry} reasoningSteps={reasoningSteps} tokenUsage={tokenUsage} />
        ) : activeAppTab === "ge_flow" ? (
          <GeMcpFlow />
        ) : activeAppTab === "auth_flow" ? (
          <AuthRequestFlow onNavigateToChat={() => { setActiveAppTab("ge_flow"); setShowTopology(false); }} />
      ) : (
            <main className="deloitte-main-wrapper" style={{ flexDirection: 'column', height: '100%', overflow: 'hidden' }}>
              {/* Chat Interface filling the right pane */}
              <section className={`deloitte-chat-sidebar ${chatMode !== 'default' ? chatMode : ''} full-width`} style={{ margin: '0', maxWidth: '100%', width: '100%', borderLeft: 'none', height: '100%', display: 'flex', flexDirection: 'column' }}>
                <div className="chat-header">
                  <div className="chat-header-top">
                    <h2>Deloitte Enterprise Shield</h2>
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
                  <div style={{ display: 'flex', gap: '10px' }}>
                    <select
                      value={routerMode}
                      onChange={(e) => setRouterMode(e.target.value as 'all_mcp'|'ge_mcp')}
                      style={{
                        background: "transparent",
                        border: "1px solid rgba(134, 188, 37, 0.3)",
                        borderRadius: "4px",
                        color: "var(--deloitte-green)",
                        padding: "4px 8px",
                        outline: "none",
                        cursor: "pointer",
                        fontWeight: "bold",
                        fontSize: "11px",
                        fontFamily: "monospace",
                      }}
                      title="Select Routing Architecture"
                    >
                      <option value="all_mcp" style={{ color: "black" }}>
                        All MCP (Direct)
                      </option>
                      <option value="ge_mcp" style={{ color: "black" }}>
                        GE + MCP (Router)
                      </option>
                    </select>
                    <select
                      value={selectedModel}
                      onChange={(e) => setSelectedModel(e.target.value)}
                      style={{
                        background: "transparent",
                        border: "1px solid rgba(134, 188, 37, 0.3)",
                        borderRadius: "4px",
                        color: "var(--deloitte-green)",
                        padding: "4px 8px",
                        outline: "none",
                        cursor: "pointer",
                        fontWeight: "bold",
                        fontSize: "11px",
                        fontFamily: "monospace",
                      }}
                    >
                      <option value="gemini-3-flash-preview" style={{ color: "black" }}>
                        gemini-3-flash-preview
                      </option>
                      <option value="gemini-2.5-flash" style={{ color: "black" }}>
                        gemini-2.5-flash
                      </option>
                    </select>
                  </div>
                </div>

                <div className="chat-messages">
                    {messages.map((m: Message, index: number) => m.content ? (
                      <div key={index} style={{ width: '100%', display: 'flex', flexDirection: 'column' }}>
                        <div className={`message ${m.role}`} style={{ flexDirection: 'column', alignItems: 'flex-start' }}>
                          <MarkdownRenderer content={m.content} />
                          
                          {/* Integrated Widgets for Last Assistant Message */}
                          {m.role === 'assistant' && index === messages.length - 1 && routerMode === 'all_mcp' && (
                            <div style={{ width: '100%', display: 'flex', flexDirection: 'column', gap: '12px', marginTop: '16px' }}>
                              {/* Generated Data Cards Widget */}
                              {projectCards.length > 0 && (
                                <div style={{ 
                                    background: 'rgba(134, 188, 37, 0.05)', 
                                    border: '1px solid rgba(134, 188, 37, 0.3)',
                                    borderRadius: '12px',
                                    overflow: 'hidden',
                                    width: '100%',
                                    transition: 'all 0.3s ease'
                                  }} 
                                >
                                  <div className="card-header" style={{ 
                                      padding: '12px 16px',
                                      display: 'flex', 
                                      justifyContent: 'space-between', 
                                      alignItems: 'center', 
                                      cursor: 'pointer',
                                      borderBottom: isProjectCardsExpanded ? '1px solid rgba(134, 188, 37, 0.15)' : 'none',
                                      background: isProjectCardsExpanded ? 'rgba(134, 188, 37, 0.05)' : 'transparent'
                                    }}
                                    onClick={() => setIsProjectCardsExpanded(!isProjectCardsExpanded)}
                                  >
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#fff', fontSize: '12px', fontWeight: '800', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                                      <Database size={16} color="var(--deloitte-green)" /> 
                                      <span style={{ color: 'var(--deloitte-green)' }}>GENERATED DATA CARDS ({projectCards.length})</span>
                                    </div>
                                    <div style={{ 
                                      color: 'var(--deloitte-green)', 
                                      display: 'flex', 
                                      alignItems: 'center', 
                                      gap: '6px', 
                                      fontSize: '10px', 
                                      fontWeight: '600'
                                    }}>
                                      {isProjectCardsExpanded ? 'COLLAPSE' : 'EXPAND'}
                                      <ChevronUp size={14} style={{ transform: isProjectCardsExpanded ? 'rotate(0deg)' : 'rotate(180deg)', transition: 'transform 0.3s' }} />
                                    </div>
                                  </div>
                                  
                                  {isProjectCardsExpanded && (
                                    <div className="card-content" style={{ 
                                        padding: '16px',
                                        background: 'rgba(0,0,0,0.1)'
                                      }}>
                                      <div className="deloitte-cards-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px' }} ref={dataSectionRef}>
                                        {projectCards.map((card, idx) => (
                                          <ProjectCardWidget key={idx} card={card as ProjectCardData} />
                                        ))}
                                      </div>
                                    </div>
                                  )}
                                </div>
                              )}
                            </div>
                          )}
                        </div>

                        {/* Public Web Consensus Widget rendered AFTER User Message but BEFORE final assistant response */}
                        {m.role === 'user' && index === 0 && routerMode === 'all_mcp' && publicInsight && publicInsight.replace(/[█\s]/g, '').length > 0 && (
                          <div className={`message assistant deloitte-insight-inline ${isPublicInsightStreaming ? 'deloitte-insight-streaming' : 'deloitte-insight-settled'}`} style={{ 
                              background: '#1a1a1a', 
                              border: `1px solid ${isPublicInsightStreaming ? 'rgba(134, 188, 37, 0.5)' : 'rgba(255, 255, 255, 0.1)'}`,
                              borderRadius: '12px',
                              overflow: 'hidden',
                              width: '100%',
                              transition: 'all 0.4s cubic-bezier(0.16, 1, 0.3, 1)',
                              boxShadow: '0 8px 30px rgba(0, 0, 0, 0.3)',
                              marginBottom: '16px',
                              marginTop: '16px',
                              padding: '0', 
                              maxWidth: '100%',
                              animation: 'fadeIn 0.5s ease-out'
                            }} 
                          >
                            <div className="card-header" style={{ 
                                padding: '12px 16px',
                                display: 'flex', 
                                justifyContent: 'space-between', 
                                alignItems: 'center', 
                                cursor: 'pointer',
                                borderBottom: isPublicInsightExpanded ? '1px solid rgba(255, 255, 255, 0.1)' : 'none',
                                background: isPublicInsightExpanded ? 'rgba(255, 255, 255, 0.05)' : 'transparent',
                                transition: 'background 0.3s ease',
                                marginBottom: '0'
                              }}
                              onClick={() => setIsPublicInsightExpanded(!isPublicInsightExpanded)}
                            >
                              <div style={{ 
                                display: 'flex', 
                                alignItems: 'center', 
                                gap: '10px', 
                                color: '#ffffff',
                                fontSize: '11px', 
                                fontWeight: '900', 
                                textTransform: 'uppercase', 
                                letterSpacing: '0.12em',
                                textShadow: '0 0 10px rgba(94, 174, 253, 0.3)' 
                              }}>
                                <div style={{ 
                                  padding: '6px', 
                                  borderRadius: '6px', 
                                  background: 'rgba(134, 188, 37, 0.15)',
                                  border: '1px solid rgba(134, 188, 37, 0.3)',
                                  display: 'flex',
                                  alignItems: 'center',
                                  justifyContent: 'center'
                                }}>
                                  <Globe size={16} color="#86BC25" style={{ filter: 'drop-shadow(0 0 8px rgba(134, 188, 37, 0.8))' }} /> 
                                </div>
                                <span style={{ 
                                  fontWeight: 800, 
                                  letterSpacing: '0.1em', 
                                  fontSize: '11px',
                                  color: '#86BC25',
                                  textShadow: '0 0 10px rgba(134, 188, 37, 0.4)'
                                }}>
                                  PUBLIC WEB CONSENSUS
                                </span>
                                {isPublicInsightStreaming && (
                                  <div className="dw-typing-dots" style={{ marginLeft: '4px' }}>
                                    <span></span><span></span><span></span>
                                  </div>
                                )}
                              </div>
                              <div style={{ 
                                color: '#FFFFFF',
                                fontSize: '11px',
                                fontWeight: 600,
                                opacity: 0.8,
                                background: 'rgba(255,255,255,0.05)',
                                padding: '4px 10px',
                                borderRadius: '20px',
                                border: '1px solid rgba(255,255,255,0.1)',
                                display: chatMode === 'default' ? 'none' : 'block'
                              }}>
                                VIRTUAL ANALYST: FLASH-3.1-LITE
                              </div>
                              <div style={{ 
                                color: 'var(--deloitte-green)', 
                                display: 'flex', 
                                alignItems: 'center', 
                                gap: '6px', 
                                fontSize: '10px', 
                                fontWeight: '600'
                              }}>
                                {isPublicInsightExpanded ? 'COLLAPSE' : 'EXPAND'}
                                <ChevronUp size={14} style={{ transform: isPublicInsightExpanded ? 'rotate(0deg)' : 'rotate(180deg)', transition: 'transform 0.3s' }} />
                              </div>
                            </div>
                            
                            {isPublicInsightExpanded && (
                              <div style={{ 
                                padding: '20px 24px',
                                fontSize: '14px', 
                                color: '#F0F0F0',
                                background: 'linear-gradient(180deg, rgba(0,0,0,0) 0%, rgba(0,0,0,0.2) 100%)',
                                lineHeight: '1.6'
                              }}>
                                <div style={{ position: 'relative' }}>
                                  <MarkdownRenderer content={publicInsight} chatMode="default" />
                                  {isPublicInsightStreaming && <span className="streaming-chunk-cursor pulsing"></span>}
                                </div>
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    ) : null)}


                    {isLoading && (
                    <div className="gemini-loading-wrapper">
                      <div className="gemini-search-pill">
                          {usedSharePoint && <img src="/sharepoint-logo.svg" className="sharepoint-used-badge" alt="SharePoint Used" title="SharePoint indices searched" />}
                        <div className="sharepoint-icon-wrapper">
                            {thoughtStatus ? (
                              thoughtStatus.icon === 'search' || thoughtStatus.icon === 'database' || thoughtStatus.icon === 'file-search' ? <img src="/sharepoint-logo.svg" alt="SharePoint" className="sharepoint-logo" /> :
                                thoughtStatus.icon === 'shield-alert' ? <ShieldAlert color="var(--deloitte-green)" size={20} /> :
                                  thoughtStatus.icon === 'check-circle' ? <CheckCircle color="var(--deloitte-green)" size={20} /> :
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

                <div className="chat-input-area" style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', justifyContent: 'center', width: '100%', paddingBottom: '8px' }}>
                    {suggestedPrompts.map((prompt, idx) => (
                       <button
                         key={idx}
                         onClick={(e) => {
                           e.preventDefault();
                           const syntheticEvent = { target: { value: prompt } } as React.ChangeEvent<HTMLTextAreaElement>;
                           handleInputChange(syntheticEvent);
                           setTimeout(() => { if (textareaRef.current && textareaRef.current.form) textareaRef.current.form.requestSubmit(); }, 100);
                         }}
                         style={{
                           background: 'rgba(134, 188, 37, 0.1)',
                           border: '1px solid rgba(134, 188, 37, 0.3)',
                           color: 'var(--deloitte-green)',
                           padding: '6px 14px',
                           borderRadius: '16px',
                           fontSize: '0.8rem',
                           fontWeight: 500,
                           cursor: 'pointer',
                           transition: 'all 0.2s ease',
                           textAlign: 'center'
                         }}
                         onMouseEnter={(e) => {
                           e.currentTarget.style.background = 'rgba(134, 188, 37, 0.2)';
                         }}
                         onMouseLeave={(e) => {
                           e.currentTarget.style.background = 'rgba(134, 188, 37, 0.1)';
                         }}
                       >
                         {prompt}
                       </button>
                    ))}
                  </div>
                  <form onSubmit={handleSubmit}>
                    <textarea
                      ref={textareaRef}
                      className="deloitte-input deloitte-textarea"
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
                      className="deloitte-btn"
                      disabled={isLoading || !input.trim()}
                    >
                      Send
                    </button>
                  </form>
                </div>
              </section>
            </main>
      )}
    </div>
  );
}

export default App;
