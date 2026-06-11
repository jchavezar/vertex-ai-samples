import { useState, useEffect, useRef } from "react";
import { PublicClientApplication } from "@azure/msal-browser";
import { MsalProvider, useMsal } from "@azure/msal-react";
import { msalConfig, loginRequest } from "./authConfig";
import { 
  Send, Database, Plus, Settings, 
  HelpCircle, CheckCircle, XCircle, FileText,
  Check, Globe, Link, ArrowRight, CornerDownRight, Loader,
  Menu, Search, Pin, MoreVertical, Shield,
  ThumbsUp, ThumbsDown, Copy, Star, Share2, Sun, Moon, Zap
} from "lucide-react";
import ReactMarkdown from "react-markdown";

// Custom official-style Gemini Sparkle Icon
const GeminiSparkle = ({ className = "w-5 h-5" }: { className?: string }) => (
  <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" className={className}>
    <path d="M12 3C12 3 12 12 21 12C21 12 12 12 12 21C12 21 12 12 3 12C3 12 12 12 12 3Z" fill="url(#gemini-sparkle-grad)" />
    <defs>
      <linearGradient id="gemini-sparkle-grad" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stopColor="#4285F4" />
        <stop offset="45%" stopColor="#9B72CB" />
        <stop offset="90%" stopColor="#D96570" />
      </linearGradient>
    </defs>
  </svg>
);

// Custom Google-style New Chat Icon (pencil writing in swirl)
const NewChatIcon = ({ className = "w-5 h-5" }: { className?: string }) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" className={className}>
    <path d="M12 20C6.48 20 2 15.52 2 10C2 4.48 6.48 2 12 2C16.5 2 20.2 5 21.5 9" />
    <path d="M12.5 13.5l8.5-8.5M20.5 4.5l-8.5 8.5-3.5 1 1-3.5 8.5-8.5c.6-.6 1.4-.6 2 0s.6 1.4 0 2z" />
  </svg>
);

// Custom Google-style Library Icon (geometric shapes: triangle, heart, circle, square)
const LibraryIcon = ({ className = "w-5 h-5" }: { className?: string }) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" className={className}>
    <path d="M 6.5 3.5 L 10 9.5 L 3 9.5 Z" />
    <path d="M 17.5 9.5 L 14.7 6.7 C 14.0 6.0 14.0 4.9 14.7 4.2 C 15.4 3.5 16.5 3.5 17.2 4.2 L 17.5 4.5 L 17.8 4.2 C 18.5 3.5 19.6 3.5 20.3 4.2 C 21.0 4.9 21.0 6.0 20.3 6.7 Z" />
    <circle cx="6.5" cy="16.5" r="3" />
    <rect x="14.5" y="13.5" width="6" height="6" rx="0.5" />
  </svg>
);

// 📊 Premium SVG Interactive Chart Component
interface ChartDataPoint {
  name: string;
  value: number;
  color?: string;
}

const InteractiveChart = ({ type, title, data }: { type: string; title: string; data: ChartDataPoint[] }) => {
  const [hoveredIdx, setHoveredIdx] = useState<number | null>(null);

  if (!data || data.length === 0) return null;

  const total = data.reduce((sum, item) => sum + item.value, 0);
  const colors = [
    "#4f46e5", "#06b6d4", "#10b981", "#f59e0b", "#ef4444", 
    "#ec4899", "#8b5cf6", "#6366f1"
  ];

  if (type === "pie") {
    let accumulatedAngle = 0;
    const slices = data.map((item, idx) => {
      const percentage = (item.value / total) * 100;
      const angle = (item.value / total) * 360;
      
      const x1 = Math.cos((accumulatedAngle - 90) * Math.PI / 180) * 80 + 100;
      const y1 = Math.sin((accumulatedAngle - 90) * Math.PI / 180) * 80 + 100;
      accumulatedAngle += angle;
      const x2 = Math.cos((accumulatedAngle - 90) * Math.PI / 180) * 80 + 100;
      const y2 = Math.sin((accumulatedAngle - 90) * Math.PI / 180) * 80 + 100;
      
      const largeArcFlag = angle > 180 ? 1 : 0;
      const pathData = `M 100 100 L ${x1} ${y1} A 80 80 0 ${largeArcFlag} 1 ${x2} ${y2} Z`;
      
      return {
        path: pathData,
        name: item.name,
        value: item.value,
        percentage,
        color: item.color || colors[idx % colors.length]
      };
    });

    return (
      <div className="my-4 p-5 rounded-2xl border bg-[#131314]/80 border-[#282a2d] shadow-lg backdrop-blur-md max-w-md select-none">
        <h4 className="text-xs font-bold text-[#e3e3e3] mb-4 flex items-center gap-2">
          <span className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-pulse"></span>
          {title}
        </h4>
        <div className="flex items-center justify-between gap-6">
          <svg className="w-36 h-36 transition-all duration-500" viewBox="0 0 200 200">
            {slices.map((slice, idx) => {
              const isHovered = hoveredIdx === idx;
              return (
                <path
                  key={idx}
                  d={slice.path}
                  fill={slice.color}
                  opacity={hoveredIdx !== null && !isHovered ? 0.6 : 1}
                  className="transition-all duration-300 cursor-pointer origin-center"
                  style={{
                    transform: isHovered ? "scale(1.05)" : "scale(1)",
                  }}
                  onMouseEnter={() => setHoveredIdx(idx)}
                  onMouseLeave={() => setHoveredIdx(null)}
                />
              );
            })}
            <circle cx="100" cy="100" r="45" fill="#131314" />
            <text x="100" y="104" textAnchor="middle" fill="#e3e3e3" className="text-[14px] font-bold font-sans">
              {hoveredIdx !== null ? `${slices[hoveredIdx].percentage.toFixed(0)}%` : total}
            </text>
            <text x="100" y="118" textAnchor="middle" fill="#8e918f" className="text-[8px] uppercase tracking-wider font-semibold">
              {hoveredIdx !== null ? slices[hoveredIdx].name : "Total items"}
            </text>
          </svg>
          
          <div className="flex-1 space-y-2">
            {slices.map((slice, idx) => (
              <div 
                key={idx} 
                className={`flex items-center justify-between p-1.5 rounded-lg transition-colors cursor-pointer ${
                  hoveredIdx === idx ? "bg-[#282a2d]" : ""
                }`}
                onMouseEnter={() => setHoveredIdx(idx)}
                onMouseLeave={() => setHoveredIdx(null)}
              >
                <div className="flex items-center gap-2">
                  <span className="w-3 h-3 rounded-full border border-black/20" style={{ backgroundColor: slice.color }}></span>
                  <span className="text-[11px] font-medium text-[#c4c7c5]">{slice.name}</span>
                </div>
                <span className="text-[11px] font-bold text-[#e3e3e3]">{slice.value}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (type === "bar") {
    const maxVal = Math.max(...data.map(item => item.value), 1);
    return (
      <div className="my-4 p-5 rounded-2xl border bg-[#131314]/80 border-[#282a2d] shadow-lg backdrop-blur-md max-w-lg select-none">
        <h4 className="text-xs font-bold text-[#e3e3e3] mb-4 flex items-center gap-2">
          <span className="w-1.5 h-1.5 rounded-full bg-blue-400 animate-pulse"></span>
          {title}
        </h4>
        <div className="space-y-3">
          {data.map((item, idx) => {
            const pct = (item.value / maxVal) * 100;
            const barColor = item.color || colors[idx % colors.length];
            return (
              <div key={idx} className="space-y-1">
                <div className="flex items-center justify-between text-[11px]">
                  <span className="font-semibold text-[#c4c7c5]">{item.name}</span>
                  <span className="font-bold text-[#e3e3e3]">{item.value}</span>
                </div>
                <div className="h-2.5 w-full bg-[#282a2d] rounded-full overflow-hidden relative">
                  <div 
                    className="h-full rounded-full transition-all duration-1000 ease-out shadow-sm"
                    style={{ 
                      width: `${pct}%`, 
                      backgroundColor: barColor,
                    }}
                  ></div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    );
  }

  if (type === "line") {
    const maxVal = Math.max(...data.map(item => item.value), 1);
    const minVal = Math.min(...data.map(item => item.value), 0);
    const valRange = maxVal - minVal || 1;
    
    const width = 360;
    const height = 120;
    const paddingX = 25;
    const paddingY = 15;
    
    const chartWidth = width - paddingX * 2;
    const chartHeight = height - paddingY * 2;
    
    const points = data.map((item, idx) => {
      const x = paddingX + (idx / (data.length - 1 || 1)) * chartWidth;
      const y = paddingY + chartHeight - ((item.value - minVal) / valRange) * chartHeight;
      return { x, y, name: item.name, value: item.value };
    });
    
    const linePath = points.reduce((path, p, idx) => {
      return idx === 0 ? `M ${p.x} ${p.y}` : `${path} L ${p.x} ${p.y}`;
    }, "");
    
    const areaPath = points.length > 0 
      ? `${linePath} L ${points[points.length - 1].x} ${height - paddingY} L ${points[0].x} ${height - paddingY} Z`
      : "";

    return (
      <div className="my-4 p-5 rounded-2xl border bg-[#131314]/80 border-[#282a2d] shadow-lg backdrop-blur-md max-w-lg select-none">
        <h4 className="text-xs font-bold text-[#e3e3e3] mb-4 flex items-center gap-2">
          <span className="w-1.5 h-1.5 rounded-full bg-indigo-400 animate-pulse"></span>
          {title}
        </h4>
        <div className="relative">
          <svg className="w-full h-32" viewBox={`0 0 ${width} ${height}`}>
            <defs>
              <linearGradient id="areaGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#6366f1" stopOpacity="0.4" />
                <stop offset="100%" stopColor="#6366f1" stopOpacity="0.0" />
              </linearGradient>
            </defs>
            <line x1={paddingX} y1={paddingY} x2={width - paddingX} y2={paddingY} stroke="#282a2d" strokeDasharray="3 3" />
            <line x1={paddingX} y1={paddingY + chartHeight / 2} x2={width - paddingX} y2={paddingY + chartHeight / 2} stroke="#282a2d" strokeDasharray="3 3" />
            <line x1={paddingX} y1={height - paddingY} x2={width - paddingX} y2={height - paddingY} stroke="#282a2d" />
            
            {points.length > 0 && (
              <path d={areaPath} fill="url(#areaGrad)" />
            )}
            
            {points.length > 0 && (
              <path d={linePath} fill="none" stroke="#6366f1" strokeWidth="2" />
            )}
            
            {points.map((p, idx) => {
              const isHovered = hoveredIdx === idx;
              return (
                <g key={idx}>
                  <circle 
                    cx={p.x} 
                    cy={p.y} 
                    r={isHovered ? 4.5 : 3} 
                    fill={isHovered ? "#ffffff" : "#6366f1"}
                    stroke="#131314"
                    strokeWidth="1.5"
                    className="cursor-pointer transition-all duration-200"
                    onMouseEnter={() => setHoveredIdx(idx)}
                    onMouseLeave={() => setHoveredIdx(null)}
                  />
                  {isHovered && (
                    <g>
                      <rect x={p.x - 22} y={p.y - 28} width="44" height="20" rx="4" fill="#1e1f20" stroke="#282a2d" strokeWidth="1" />
                      <text x={p.x} y={p.y - 15} textAnchor="middle" fill="#ffffff" className="text-[9px] font-bold font-sans">
                        {p.value}
                      </text>
                    </g>
                  )}
                  {(idx === 0 || idx === points.length - 1 || idx === Math.floor(points.length / 2)) && (
                    <text x={p.x} y={height - 2} textAnchor="middle" fill="#8e918f" className="text-[8px] font-semibold font-mono">
                      {p.name}
                    </text>
                  )}
                </g>
              );
            })}
          </svg>
        </div>
      </div>
    );
  }

  if (type === "stats") {
    return (
      <div className="my-4 p-4 rounded-2xl border bg-[#131314]/80 border-[#282a2d] shadow-lg backdrop-blur-md max-w-lg select-none">
        <h4 className="text-xs font-bold text-[#e3e3e3] mb-4 flex items-center gap-2">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
          {title}
        </h4>
        <div className="grid grid-cols-2 gap-3.5">
          {data.map((item, idx) => {
            const statusColor = 
              item.color || 
              (item.name.toLowerCase().includes("error") || item.name.toLowerCase().includes("block") || item.name.toLowerCase().includes("todo") ? "#f59e0b" : 
               item.name.toLowerCase().includes("done") || item.name.toLowerCase().includes("success") || item.name.toLowerCase().includes("resolved") ? "#10b981" : 
               "#a8c7fa");
               
            return (
              <div key={idx} className="p-3.5 rounded-xl border bg-[#1e1f20]/50 border-[#282a2d]/80 flex flex-col justify-between h-20 relative overflow-hidden">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-[#8e918f] truncate max-w-[110px]">{item.name}</span>
                  <span className="w-1.5 h-1.5 rounded-full border border-black/20" style={{ backgroundColor: statusColor }}></span>
                </div>
                <div className="flex items-baseline justify-between mt-2">
                  <span className="text-xl font-bold text-[#e3e3e3] tracking-tight">{item.value}</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    );
  }

  return null;
};

// Message Content Parser Helper to detect and render charts inline
const renderMessageContent = (content: string) => {
  const chartRegex = /<chart\s+type="([^"]+)"\s+title="([^"]+)">([\s\S]*?)<\/chart>/gi;
  const parts = [];
  let lastIndex = 0;
  let match;

  while ((match = chartRegex.exec(content)) !== null) {
    if (match.index > lastIndex) {
      parts.push({
        type: "text",
        content: content.substring(lastIndex, match.index)
      });
    }

    const type = match[1];
    const title = match[2];
    const rawData = match[3].trim();
    let data = [];
    try {
      data = JSON.parse(rawData);
    } catch (e) {
      try {
        const itemRegex = /{\s*"name"\s*:\s*"([^"]+)"\s*,\s*"value"\s*:\s*(\d+)\s*}/gi;
        let itemMatch;
        while ((itemMatch = itemRegex.exec(rawData)) !== null) {
          data.push({ name: itemMatch[1], value: parseInt(itemMatch[2], 10) });
        }
      } catch (innerErr) {
        console.error("Partial JSON extraction failed:", innerErr);
      }
    }

    parts.push({
      type: "chart",
      chartType: type,
      title: title,
      data: data
    });

    lastIndex = chartRegex.lastIndex;
  }

  if (lastIndex < content.length) {
    parts.push({
      type: "text",
      content: content.substring(lastIndex)
    });
  }

  if (parts.length === 0) {
    return <ReactMarkdown>{content}</ReactMarkdown>;
  }

  return (
    <div className="space-y-2">
      {parts.map((p, idx) => {
        if (p.type === "chart") {
          return <InteractiveChart key={idx} type={p.chartType || "pie"} title={p.title || "Chart"} data={p.data} />;
        }
        return <ReactMarkdown key={idx}>{p.content}</ReactMarkdown>;
      })}
    </div>
  );
};

// Helper to extract follow-up suggestions from XML-like tags in model output
const parseSuggestionsAndContent = (content: string): { cleanContent: string; suggestions: string[] } => {
  const suggestionsRegex = /<suggestions>([\s\S]*?)<\/suggestions>/i;
  const match = suggestionsRegex.exec(content);
  if (!match) {
    // If suggestions tag is still incomplete during streaming, filter out the raw open tag
    const openTagIndex = content.toLowerCase().indexOf("<suggestions>");
    if (openTagIndex !== -1) {
      return { cleanContent: content.substring(0, openTagIndex).trim(), suggestions: [] };
    }
    return { cleanContent: content, suggestions: [] };
  }
  
  const cleanContent = content.replace(suggestionsRegex, "").trim();
  const rawSuggestions = match[1];
  const suggestionRegex = /<suggestion>([\s\S]*?)<\/suggestion>/gi;
  const suggestions: string[] = [];
  let sugMatch;
  while ((sugMatch = suggestionRegex.exec(rawSuggestions)) !== null) {
    suggestions.push(sugMatch[1].trim());
  }
  
  return { cleanContent, suggestions };
};

// Custom Assistant Icon Resolver
const AssistantIcon = ({ title }: { title: string }) => {
  if (title === "SharePoint Assistant") {
    return (
      <div className="w-7 h-7 rounded-full bg-[#006064] flex items-center justify-center text-white shrink-0 shadow-sm">
        <Search size={14} className="stroke-[2.5]" />
      </div>
    );
  }
  if (title === "Jira Assistant") {
    return (
      <div className="w-7 h-7 rounded-full bg-[#0747a6] flex items-center justify-center text-white shrink-0 shadow-sm">
        <FileText size={14} className="stroke-[2.5]" />
      </div>
    );
  }
  return <GeminiSparkle className="w-5 h-5 shrink-0" />;
};

// Initialize MSAL Client
const pca = new PublicClientApplication(msalConfig);

interface Source {
  title: string;
  url: string;
  connector: string;
}

interface ToolLog {
  timestamp: string;
  type: "status" | "tool_call" | "tool_result" | "error";
  connector?: string;
  tool?: string;
  arguments?: any;
  result?: any;
  status?: string;
  error?: string;
}

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  statusEvents?: string[];
  sources?: Source[];
  toolLogs?: ToolLog[];
  latency?: number;
  llmLatency?: number;
  toolLatency?: number;
}

interface ConnectorConfig {
  enabled: boolean;
  connected: boolean;
  site_url?: string;
  email?: string;
  token?: string;
  auth_type?: "basic" | "oauth";
}

const getAssistantTitle = (msg: Message) => {
  if (msg.id === "welcome") return "Gemini Enterprise";
  const hasJira = msg.statusEvents?.some(e => e.toLowerCase().includes("jira")) || msg.toolLogs?.some(l => l.connector === "jira");
  const hasSP = msg.statusEvents?.some(e => e.toLowerCase().includes("sharepoint")) || msg.toolLogs?.some(l => l.connector === "sharepoint");
  if (hasJira) return "Jira Assistant";
  if (hasSP) return "SharePoint Assistant";
  return "Gemini Enterprise";
};

const getPlaceholder = (connectors: Record<string, ConnectorConfig>) => {
  if (connectors.jira.enabled && connectors.sharepoint.enabled) {
    return "Ask Jira & SharePoint Assistant";
  }
  if (connectors.jira.enabled) {
    return "Ask Jira Assistant";
  }
  if (connectors.sharepoint.enabled) {
    return "Ask SharePoint Assistant";
  }
  return "Ask a follow-up";
};

const getLogTypeBadgeClass = (type: string, isDarkMode: boolean) => {
  if (isDarkMode) {
    return type === "tool_call" ? "bg-purple-950 text-purple-300 border border-purple-900" :
           type === "tool_result" ? "bg-green-950 text-green-300 border border-green-900" :
           type === "error" ? "bg-red-950 text-red-300 border border-red-900" : "bg-[#282a2d] text-[#c4c7c5]";
  } else {
    return type === "tool_call" ? "bg-purple-900/60 text-purple-200" :
           type === "tool_result" ? "bg-green-900/60 text-green-200" :
           type === "error" ? "bg-red-900/60 text-red-200" : "bg-gray-800 text-gray-400";
  }
};

function MainApp() {
  const { instance } = useMsal();
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome",
      role: "assistant",
      content: "Hello! I am Gemini Enterprise. Connect your corporate tools like Jira and SharePoint using the database stack icon below to start querying your data.\n\n<suggestions>\n  <suggestion>Calculate cycle time for resolved tickets in SMP (excluding weekends)</suggestion>\n  <suggestion>Run a Monte Carlo simulation on remaining To Do tickets in SMP</suggestion>\n</suggestions>"
    }
  ]);
  const [inputText, setInputText] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [useReasoningEngine, setUseReasoningEngine] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [isDarkMode, setIsDarkMode] = useState(false);
  
  // Active streaming state
  const [streamingText, setStreamingText] = useState("");
  const [activeToolCalls, setActiveToolCalls] = useState<string[]>([]);
  const [activeStatus, setActiveStatus] = useState("");
  const [expandedLogs, setExpandedLogs] = useState<Record<string, boolean>>({});

  const [liveLatency, setLiveLatency] = useState(0);

  useEffect(() => {
    let interval: any;
    if (isStreaming) {
      const startTime = Date.now();
      setLiveLatency(0);
      interval = setInterval(() => {
        setLiveLatency(parseFloat(((Date.now() - startTime) / 1000).toFixed(1)));
      }, 100);
    } else {
      setLiveLatency(0);
    }
    return () => clearInterval(interval);
  }, [isStreaming]);

  // Connector configurations
  const [connectors, setConnectors] = useState<Record<string, ConnectorConfig>>(() => {
    const saved = localStorage.getItem("ge_mcp_connectors");
    if (saved) {
      try {
        return JSON.parse(saved);
      } catch (e) {
        console.error("Failed to parse saved connectors:", e);
      }
    }
    return {
      jira: {
        enabled: true,
        connected: true,
        site_url: "https://sockcop.atlassian.net",
        email: "demo@sockcop.net",
        token: "demo-token",
        auth_type: "basic"
      },
      sharepoint: {
        enabled: false,
        connected: false,
        token: ""
      },
      google_search: {
        enabled: false,
        connected: true
      }
    };
  });

  // Jira config input states
  const [jiraUrlInput, setJiraUrlInput] = useState(() => {
    return localStorage.getItem("jira_url_input") || "https://sockcop.atlassian.net";
  });
  const [jiraEmailInput, setJiraEmailInput] = useState(() => {
    return localStorage.getItem("jira_email_input") || "demo@sockcop.net";
  });
  const [jiraTokenInput, setJiraTokenInput] = useState(() => {
    return localStorage.getItem("jira_token_input") || "demo-token";
  });

  const chatEndRef = useRef<HTMLDivElement>(null);

  // Sync state to localStorage
  useEffect(() => {
    localStorage.setItem("ge_mcp_connectors", JSON.stringify(connectors));
  }, [connectors]);

  useEffect(() => {
    localStorage.setItem("jira_url_input", jiraUrlInput);
  }, [jiraUrlInput]);

  useEffect(() => {
    localStorage.setItem("jira_email_input", jiraEmailInput);
  }, [jiraEmailInput]);

  useEffect(() => {
    localStorage.setItem("jira_token_input", jiraTokenInput);
  }, [jiraTokenInput]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, streamingText, activeToolCalls, activeStatus]);

  // SharePoint OAuth Login
  const connectSharePoint = async () => {
    try {
      const loginResponse = await instance.loginPopup(loginRequest);
      if (loginResponse.accessToken) {
        setConnectors(prev => ({
          ...prev,
          sharepoint: {
            ...prev.sharepoint,
            connected: true,
            enabled: true,
            token: loginResponse.accessToken
          }
        }));
      }
    } catch (error) {
      console.error("Microsoft Login failed:", error);
      alert("Failed to connect to SharePoint. Verify app configuration.");
    }
  };

  const disconnectSharePoint = () => {
    setConnectors(prev => ({
      ...prev,
      sharepoint: {
        enabled: false,
        connected: false,
        token: ""
      }
    }));
  };

  const [isJiraOAuthConnecting, setIsJiraOAuthConnecting] = useState(false);
  const [showJiraBasicAuth, setShowJiraBasicAuth] = useState(false);

  // Jira Atlassian OAuth Login
  const connectJiraOAuth = async () => {
    setIsJiraOAuthConnecting(true);
    try {
      const response = await fetch("http://localhost:8005/api/auth/jira/url");
      if (!response.ok) {
        throw new Error(`HTTP Error ${response.status}`);
      }
      const data = await response.json();
      const authUrl = data.auth_url;
      
      const width = 600;
      const height = 700;
      const left = window.screen.width / 2 - width / 2;
      const top = window.screen.height / 2 - height / 2;
      const popup = window.open(authUrl, "atlassian-oauth", `width=${width},height=${height},left=${left},top=${top}`);

      const interval = setInterval(async () => {
        try {
          const tResp = await fetch("http://localhost:8005/api/auth/jira/token");
          if (tResp.ok) {
            const tData = await tResp.json();
            if (tData.token) {
              clearInterval(interval);
              popup?.close();
              setIsJiraOAuthConnecting(false);
              setConnectors(prev => ({
                ...prev,
                jira: {
                  ...prev.jira,
                  connected: true,
                  enabled: true,
                  auth_type: "oauth",
                  token: tData.token,
                  site_url: "Atlassian Cloud Site",
                  email: "Authorized Account"
                }
              }));
            }
          } else {
            const errData = await tResp.json();
            clearInterval(interval);
            popup?.close();
            setIsJiraOAuthConnecting(false);
            alert(`Authentication failed: ${errData.detail || "Unknown error"}`);
          }
        } catch (pollErr) {
          // Keep polling
        }
      }, 1000);

      // Check if popup closed manually
      const checkPopup = setInterval(() => {
        if (!popup || popup.closed) {
          clearInterval(checkPopup);
          clearInterval(interval);
          setIsJiraOAuthConnecting(false);
        }
      }, 1000);

    } catch (err) {
      console.error("Jira OAuth init failed:", err);
      setIsJiraOAuthConnecting(false);
      alert("Failed to initialize Atlassian OAuth.");
    }
  };

  // Jira Credentials Management
  const connectJira = () => {
    if (!jiraUrlInput || !jiraEmailInput || !jiraTokenInput) {
      alert("Please fill in all Jira credentials fields.");
      return;
    }
    setConnectors(prev => ({
      ...prev,
      jira: {
        ...prev.jira,
        connected: true,
        enabled: true,
        site_url: jiraUrlInput,
        email: jiraEmailInput,
        token: jiraTokenInput,
        auth_type: "basic"
      }
    }));
  };

  const disconnectJira = () => {
    setConnectors(prev => ({
      ...prev,
      jira: {
        ...prev.jira,
        connected: false,
        enabled: false,
        token: "",
        email: "",
        site_url: ""
      }
    }));
    setJiraUrlInput("");
    setJiraEmailInput("");
    setJiraTokenInput("");
  };

  // Toggle state helper
  const toggleConnector = (key: string) => {
    setConnectors(prev => ({
      ...prev,
      [key]: {
        ...prev[key],
        enabled: prev[key].connected ? !prev[key].enabled : false
      }
    }));
  };

  // Send message to Backend
  const handleSend = async (overrideText?: string) => {
    const targetText = overrideText !== undefined ? overrideText : inputText;
    if (!targetText.trim() || isStreaming) return;

    const startTime = Date.now();

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: targetText
    };

    setMessages(prev => [...prev, userMessage]);
    if (overrideText === undefined) {
      setInputText("");
    }
    setIsStreaming(true);
    setStreamingText("");
    setActiveToolCalls([]);
    setActiveStatus("Thinking... ");


    // Prepare API history
    const historyPayload = [...messages, userMessage].map(m => ({
      role: m.role,
      content: m.content
    }));

    let accumulatedText = "";
    let accumulatedSources: Source[] = [];
    const accumulatedToolCalls: string[] = [];
    const accumulatedLogs: ToolLog[] = [];
    let splitLlm = 0.0;
    let splitTool = 0.0;

    try {
      const response = await fetch("http://localhost:8005/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          messages: historyPayload,
          connectors: connectors,
          use_reasoning_engine: useReasoningEngine
        })
      });

      if (!response.body) {
        throw new Error("No response body from server");
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      let currentEvent = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";

        for (const line of lines) {
          if (!line.trim()) continue;

          if (line.startsWith("event: ")) {
            currentEvent = line.replace("event: ", "").trim();
          } else if (line.startsWith("data: ")) {
            const dataStr = line.replace("data: ", "").trim();
            try {
              const data = JSON.parse(dataStr);
              if (currentEvent === "status") {
                setActiveStatus(data.status);
                accumulatedLogs.push({
                  timestamp: new Date().toLocaleTimeString(),
                  type: "status",
                  status: data.status
                });
              } else if (currentEvent === "text") {
                accumulatedText += data.text;
                setStreamingText(accumulatedText);
              } else if (currentEvent === "tool_call") {
                const callMsg = `Executing ${data.connector} tool: ${data.tool}`;
                accumulatedToolCalls.push(callMsg);
                setActiveToolCalls([...accumulatedToolCalls]);
                setActiveStatus(`Executing tool on ${data.connector}...`);
                accumulatedLogs.push({
                  timestamp: new Date().toLocaleTimeString(),
                  type: "tool_call",
                  connector: data.connector,
                  tool: data.tool,
                  arguments: data.arguments
                });
              } else if (currentEvent === "tool_result") {
                accumulatedLogs.push({
                  timestamp: new Date().toLocaleTimeString(),
                  type: "tool_result",
                  connector: data.connector,
                  tool: data.tool,
                  status: data.status,
                  result: data.result
                });
              } else if (currentEvent === "sources") {
                if (data.sources) {
                  accumulatedSources = [...accumulatedSources, ...data.sources];
                }
              } else if (currentEvent === "latency_split") {
                splitLlm = data.llm_latency;
                splitTool = data.tool_latency;
              } else if (currentEvent === "error") {
                accumulatedText += `\n\n**Error:** ${data.error}\n\n<suggestions>\n  <suggestion>List all visible Jira projects</suggestion>\n  <suggestion>List document libraries in SharePoint</suggestion>\n</suggestions>`;
                setStreamingText(accumulatedText);
                accumulatedLogs.push({
                  timestamp: new Date().toLocaleTimeString(),
                  type: "error",
                  error: data.error
                });
              }
            } catch (err) {
              console.error("JSON parse error on line:", line, err);
            }
          }
        }
      }

      const latencySec = parseFloat(((Date.now() - startTime) / 1000).toFixed(1));

      // Commit the completed message to log
      setMessages(prev => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          role: "assistant",
          content: accumulatedText || "Failed to generate text.",
          sources: accumulatedSources,
           statusEvents: accumulatedToolCalls,
          toolLogs: accumulatedLogs,
          latency: latencySec,
          llmLatency: splitLlm,
          toolLatency: splitTool
        }
      ]);

    } catch (error: any) {
      console.error("Error sending message:", error);
      const latencySec = parseFloat(((Date.now() - startTime) / 1000).toFixed(1));
      setMessages(prev => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          role: "assistant",
          content: `Error connecting to backend: ${error.message || error}\n\n<suggestions>\n  <suggestion>List all visible Jira projects</suggestion>\n  <suggestion>List document libraries in SharePoint</suggestion>\n</suggestions>`,
          latency: latencySec
        }
      ]);
    } finally {
      setIsStreaming(false);
      setStreamingText("");
      setActiveToolCalls([]);
      setActiveStatus("");

    }
  };

  return (
    <div className={`flex h-screen w-full relative transition-colors duration-300 ${isDarkMode ? "bg-[#131314] text-[#e3e3e3]" : "bg-white text-gray-800"}`}>
      
      {/* 1. Left Collapsible Sidebar */}
      <div className={`border-r flex flex-col transition-all duration-300 ${sidebarOpen ? "w-64" : "w-16"} ${
        isDarkMode ? "border-[#282a2d] bg-[#1e1f20]" : "border-gray-200 bg-gray-50/50"
      } h-full`}>
        {/* Top Header Row with Hamburger */}
        <div className="p-4 flex items-center">
          <button 
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className={`p-1.5 rounded-lg transition-colors ${isDarkMode ? "hover:bg-[#282a2d] text-[#c4c7c5] hover:text-white" : "hover:bg-gray-200 text-gray-600"}`}
          >
            <Menu size={20} />
          </button>
        </div>

        {sidebarOpen ? (
          <>
            {/* New Chat Button */}
            <div className="px-3 mb-2">
              <button className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                isDarkMode ? "hover:bg-[#282a2d] text-[#e3e3e3]" : "hover:bg-gray-200/60 text-gray-700"
              }`}>
                <NewChatIcon className={`${isDarkMode ? "text-[#c4c7c5]" : "text-gray-500"} w-[18px] h-[18px]`} />
                <span>New chat</span>
              </button>
            </div>

            {/* Search Pill */}
            <div className="px-3 mb-4">
              <div className={`flex items-center gap-2 px-3 py-2 rounded-lg cursor-pointer transition-colors text-sm ${
                isDarkMode ? "bg-[#282a2d] hover:bg-[#303134] text-[#c4c7c5]" : "bg-gray-200/50 hover:bg-gray-200/80 text-gray-500"
              }`}>
                <Search size={16} />
                <span className="flex-1 text-xs">Search</span>
                <span className={`text-[10px] px-1.5 py-0.5 rounded font-mono ${isDarkMode ? "bg-[#1e1f20] text-[#8e918f]" : "bg-gray-300/60 text-gray-600"}`}>⌘K</span>
              </div>
            </div>

            {/* Library / Navigation */}
            <div className="px-3 mb-4 space-y-1">
              <button className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors ${
                isDarkMode ? "hover:bg-[#282a2d] text-[#e3e3e3]" : "hover:bg-gray-200/50 text-gray-700"
              }`}>
                <LibraryIcon className={`${isDarkMode ? "text-[#c4c7c5]" : "text-gray-500"} w-[18px] h-[18px]`} />
                <span>Library</span>
              </button>
            </div>

            {/* Agents Section */}
            <div className="mb-4">
              <div className={`px-6 py-1.5 text-[11px] font-bold uppercase tracking-wider flex items-center justify-between ${
                isDarkMode ? "text-[#8e918f]" : "text-gray-400"
              }`}>
                <span>Agents</span>
                <span className={`cursor-pointer ${isDarkMode ? "text-[#8e918f] hover:text-white" : "text-gray-300 hover:text-gray-500"}`}>›</span>
              </div>
              <div className="px-3 space-y-0.5">
                <button className={`w-full flex items-center justify-between px-3 py-2 rounded-lg text-xs font-medium transition-colors ${
                  isDarkMode ? "hover:bg-[#282a2d] text-[#e3e3e3]" : "hover:bg-gray-200/50 text-gray-700"
                }`}>
                  <div className="flex items-center gap-2.5">
                    <span className={`w-4 h-4 rounded-full flex items-center justify-center font-bold text-[8px] ${
                      isDarkMode ? "bg-[#3c2f2f] text-orange-400" : "bg-orange-100 text-orange-600"
                    }`}>N</span>
                    <span>NotebookLM</span>
                  </div>
                  <Pin size={12} className={`rotate-45 animate-none ${isDarkMode ? "text-[#8e918f]" : "text-gray-400"}`} />
                </button>
                <button className={`w-full flex items-center justify-between px-3 py-2 rounded-lg text-xs font-medium transition-colors ${
                  isDarkMode ? "hover:bg-[#282a2d] text-[#e3e3e3]" : "hover:bg-gray-200/50 text-gray-700"
                }`}>
                  <div className="flex items-center gap-2.5">
                    <span className={`w-4 h-4 rounded-full flex items-center justify-center font-bold text-[8px] ${
                      isDarkMode ? "bg-[#1b3a3a] text-teal-400" : "bg-teal-100 text-teal-600"
                    }`}>D</span>
                    <span>Deep Research</span>
                  </div>
                  <Pin size={12} className={`rotate-45 animate-none ${isDarkMode ? "text-[#8e918f]" : "text-gray-400"}`} />
                </button>
                <button className={`w-full flex items-center justify-between px-3 py-2 rounded-lg text-xs font-medium transition-colors ${
                  isDarkMode ? "hover:bg-[#282a2d] text-[#e3e3e3]" : "hover:bg-gray-200/50 text-gray-700"
                }`}>
                  <div className="flex items-center gap-2.5">
                    <span className={`w-4 h-4 rounded-full flex items-center justify-center font-bold text-[8px] ${
                      isDarkMode ? "bg-[#2a1b3d] text-purple-400" : "bg-purple-100 text-purple-600"
                    }`}>I</span>
                    <span>Idea Generation</span>
                    <span className={`scale-90 px-1 rounded text-[8px] font-bold ${
                      isDarkMode ? "bg-[#004a77] text-[#c2e7ff]" : "bg-blue-100 text-blue-700"
                    }`}>Preview</span>
                  </div>
                  <Pin size={12} className={`rotate-45 animate-none ${isDarkMode ? "text-[#8e918f]" : "text-gray-400"}`} />
                </button>
              </div>
            </div>

            {/* Chats Section */}
            <div className="flex-1 overflow-y-auto">
              <div className={`px-6 py-1.5 text-[11px] font-bold uppercase tracking-wider ${isDarkMode ? "text-[#8e918f]" : "text-gray-400"}`}>
                Chats
              </div>
              <div className="px-3 space-y-0.5">
                <button className={`w-full text-left px-3 py-2.5 rounded-full text-xs font-semibold transition-colors truncate block ${
                  isDarkMode ? "bg-[#004a77]/30 hover:bg-[#004a77]/50 text-[#c2e7ff]" : "bg-blue-100/70 hover:bg-blue-100 text-[#1a73e8]"
                }`}>
                  Alphabet document summary
                </button>
                <button className={`w-full text-left px-3 py-2.5 rounded-full text-xs transition-colors truncate block ${
                  isDarkMode ? "hover:bg-[#282a2d] text-[#c4c7c5] hover:text-white" : "hover:bg-gray-200/50 text-gray-600"
                }`}>
                  Greeting and well-being
                </button>
                <button className={`w-full text-left px-3 py-2.5 rounded-full text-xs transition-colors truncate block ${
                  isDarkMode ? "hover:bg-[#282a2d] text-[#c4c7c5] hover:text-white" : "hover:bg-gray-200/50 text-gray-600"
                }`}>
                  Financial highlights
                </button>
                <button className={`w-full text-left px-3 py-2.5 rounded-full text-xs transition-colors truncate block ${
                  isDarkMode ? "hover:bg-[#282a2d] text-[#c4c7c5] hover:text-white" : "hover:bg-gray-200/50 text-gray-600"
                }`}>
                  Financial highlights summary
                </button>
              </div>
            </div>

            {/* Footer Sidebar with Settings & Help */}
            <div className={`p-3 border-t ${isDarkMode ? "border-[#282a2d]" : "border-gray-200"}`}>
              <button className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors ${
                isDarkMode ? "hover:bg-[#282a2d] text-[#e3e3e3]" : "hover:bg-gray-200 text-gray-700"
              }`}>
                <Settings size={18} className={isDarkMode ? "text-[#c4c7c5]" : "text-gray-500"} />
                <span>Settings & help</span>
              </button>
            </div>
          </>
        ) : (
          /* Collapsed Sidebar Icons */
          <div className="flex-1 flex flex-col items-center py-4 space-y-6">
            <button className={`p-2 rounded-full ${isDarkMode ? "hover:bg-[#282a2d] text-[#c4c7c5] hover:text-white" : "hover:bg-gray-200 text-gray-600"}`} title="New chat">
              <NewChatIcon className={`w-5 h-5 ${isDarkMode ? "text-[#c4c7c5]" : "text-gray-600"}`} />
            </button>
            <button className={`p-2 rounded-full ${isDarkMode ? "hover:bg-[#282a2d] text-[#c4c7c5] hover:text-white" : "hover:bg-gray-200 text-gray-600"}`} title="Search">
              <Search size={20} className={isDarkMode ? "text-[#c4c7c5]" : "text-gray-600"} />
            </button>
            <button className={`p-2 rounded-full ${isDarkMode ? "hover:bg-[#282a2d] text-[#c4c7c5] hover:text-white" : "hover:bg-gray-200 text-gray-600"}`} title="Library">
              <LibraryIcon className={`w-5 h-5 ${isDarkMode ? "text-[#c4c7c5]" : "text-gray-600"}`} />
            </button>
            <div className={`w-8 h-[1px] ${isDarkMode ? "bg-[#282a2d]" : "bg-gray-200"}`} />
            <button className={`p-2 rounded-full ${isDarkMode ? "hover:bg-[#282a2d] text-[#c4c7c5] hover:text-white" : "hover:bg-gray-200 text-gray-600"}`} title="Settings & help">
              <Settings size={20} className={isDarkMode ? "text-[#c4c7c5]" : "text-gray-600"} />
            </button>
          </div>
        )}
      </div>

      {/* 2. Main Chat Area */}
      <div className={`flex-1 flex flex-col h-full overflow-hidden ${isDarkMode ? "bg-[#131314]" : "bg-white"}`}>
        
        {/* Header (Gemini Enterprise style) */}
        <div className={`h-16 border-b px-6 flex items-center justify-between ${
          isDarkMode ? "border-[#282a2d] bg-[#131314]" : "border-gray-100 bg-white"
        }`}>
          <div className="flex items-center gap-2">
            <span className={`font-semibold text-base ${isDarkMode ? "text-[#e3e3e3]" : "text-gray-800"}`}>
              Gemini Enterprise
            </span>
            <div className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider ${
              isDarkMode ? "border border-[#444746] text-[#c4c7c5]" : "bg-gray-100 text-gray-500"
            }`}>
              Plus
            </div>
          </div>
          
          {/* Active Chat Title in Center */}
          <div className={`hidden md:block font-medium text-sm ${isDarkMode ? "text-[#e3e3e3]" : "text-gray-700"}`}>
            Alphabet document summary
          </div>

          <div className={`flex items-center gap-3 ${isDarkMode ? "text-[#c4c7c5]" : "text-gray-500"}`}>
            <button 
              onClick={() => setIsDarkMode(!isDarkMode)} 
              className={`p-1.5 rounded-lg transition-colors ${isDarkMode ? "hover:bg-[#282a2d] text-[#c4c7c5] hover:text-white" : "hover:bg-gray-100 text-gray-500"}`}
              title={isDarkMode ? "Switch to Light Mode" : "Switch to Dark Mode"}
            >
              {isDarkMode ? <Sun size={18} /> : <Moon size={18} />}
            </button>
            <button className={`p-1.5 rounded-lg transition-colors ${isDarkMode ? "hover:bg-[#282a2d] text-[#c4c7c5] hover:text-white" : "hover:bg-gray-100 text-gray-500"}`} title="Star chat"><Star size={18} /></button>
            <button className={`p-1.5 rounded-lg transition-colors ${isDarkMode ? "hover:bg-[#282a2d] text-[#c4c7c5] hover:text-white" : "hover:bg-gray-100 text-gray-500"}`} title="Share chat"><Share2 size={18} /></button>
            <button 
              onClick={() => setDrawerOpen(!drawerOpen)}
              className={`p-1.5 rounded-lg flex items-center gap-1.5 border px-3 transition-colors bg-transparent ${
                isDarkMode ? "hover:bg-[#282a2d] text-[#e3e3e3] hover:text-white border-[#444746]" : "hover:bg-gray-100 text-gray-600 border-gray-200"
              }`}
            >
              <Database size={15} />
              <span className="text-xs font-medium">Connectors</span>
            </button>
            <button className={`p-1.5 rounded-lg transition-colors ${isDarkMode ? "hover:bg-[#282a2d] text-[#c4c7c5] hover:text-white" : "hover:bg-gray-100 text-gray-500"}`}><HelpCircle size={18} /></button>
            <button className={`p-1.5 rounded-lg transition-colors ${isDarkMode ? "hover:bg-[#282a2d] text-[#c4c7c5] hover:text-white" : "hover:bg-gray-100 text-gray-500"}`}><MoreVertical size={18} /></button>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-xs shadow-sm ml-1 select-none ${
              isDarkMode ? "bg-[#c2e7ff] text-[#001d35]" : "bg-blue-600 text-white"
            }`}>
              JA
            </div>
          </div>
        </div>

        {/* Chat Feed */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          <div className="max-w-3xl mx-auto space-y-6">
            
            {messages.map((msg) => (
              <div key={msg.id} className={`flex flex-col ${msg.role === "user" ? "items-end" : "items-start"} w-full`}>
                
                 {/* Message Identity */}
                {msg.role === "assistant" && (
                  <div className="flex items-center gap-2.5 mb-2 ml-1">
                    <AssistantIcon title={getAssistantTitle(msg)} />
                    <span className={`font-semibold text-[13px] tracking-wide select-none ${isDarkMode ? "text-[#e3e3e3]" : "text-gray-800"}`}>
                      {getAssistantTitle(msg)}
                    </span>
                  </div>
                )}
 
                {/* Message Bubble */}
                <div className={
                  msg.role === "user" 
                    ? (isDarkMode 
                        ? "px-6 py-4 rounded-[32px] max-w-[75%] bg-[#303134] text-[#e3e3e3] text-[15px] font-normal leading-relaxed" 
                        : "px-5 py-3.5 rounded-[24px] rounded-tr-[4px] max-w-[75%] bg-[#e9eef6] text-[#1f1f1f] text-[15px] font-normal leading-relaxed"
                      )
                    : (isDarkMode 
                        ? "text-[#e3e3e3] leading-relaxed prose prose-invert prose-sm pl-1 pr-4 mt-2 w-full" 
                        : "text-gray-800 leading-relaxed prose prose-sm pl-8 pr-4 -mt-1 w-full"
                      )
                }>
                  {msg.role === "user" ? (
                    msg.content
                  ) : (
                    (() => {
                      const { cleanContent, suggestions } = parseSuggestionsAndContent(msg.content);
                      return (
                        <div className="space-y-3">
                          {renderMessageContent(cleanContent)}
                          {suggestions.length > 0 && (
                            <div className="mt-4 flex flex-wrap gap-2 not-prose select-none">
                              {suggestions.map((sug, sIdx) => (
                                <button
                                  key={sIdx}
                                  onClick={() => handleSend(sug)}
                                  className={`px-3 py-1.5 rounded-2xl text-[11px] font-semibold transition-all border shadow-sm ${
                                    isDarkMode
                                      ? "bg-[#202124] hover:bg-[#3c4043] text-[#e8eaed] border-[#3c4043] hover:border-[#8ab4f8]/50"
                                      : "bg-white hover:bg-gray-50 text-gray-700 border-gray-200 hover:border-blue-500/50"
                                  }`}
                                >
                                  {sug}
                                </button>
                              ))}
                            </div>
                          )}
                        </div>
                      );
                    })()
                  )}
                </div>
 
                {/* Grounded Sources */}
                {msg.sources && msg.sources.length > 0 && (
                  isDarkMode ? (
                    <div className="mt-4 ml-1 w-full max-w-2xl text-[14px]">
                      <span className="text-[#e3e3e3] font-medium block mb-2">Sources:</span>
                      <ul className="list-disc pl-5 space-y-3 text-[#c4c7c5]">
                        {msg.sources.map((src, idx) => (
                          <li key={idx} className="leading-relaxed">
                            <span className="font-semibold text-[#e3e3e3]">{src.title}:</span>
                            <a 
                              href={src.url} 
                              target="_blank" 
                              rel="noreferrer"
                              className="block text-[#8ab4f8] hover:underline break-all pl-0 mt-0.5"
                            >
                              {src.url}
                            </a>
                          </li>
                        ))}
                      </ul>
                    </div>
                  ) : (
                    <div className="mt-2.5 ml-8 w-full max-w-xl">
                      <span className="text-[10px] font-bold text-gray-400 block mb-1.5 uppercase tracking-wider">Sources:</span>
                      <div className="flex flex-wrap gap-1.5">
                        {msg.sources.map((src, idx) => (
                          <a 
                            key={idx}
                            href={src.url} 
                            target="_blank" 
                            rel="noreferrer"
                            className="flex items-center gap-1 px-2.5 py-1 bg-gray-100 border border-gray-200 rounded-full hover:bg-gray-200/80 transition-colors text-[10px] text-gray-600 font-semibold"
                          >
                            <FileText size={10} className="text-gray-400" />
                            <span>{src.title}</span>
                            <Link size={8} className="text-gray-400 ml-0.5" />
                          </a>
                        ))}
                      </div>
                    </div>
                  )
                )}

                {msg.role === "assistant" && msg.toolLogs && msg.toolLogs.length > 0 && (
                  <div className={`mt-2 w-full max-w-2xl ${isDarkMode ? "ml-1" : "ml-8"}`}>
                    <button 
                      onClick={() => setExpandedLogs(prev => ({ ...prev, [msg.id]: !prev[msg.id] }))}
                      className={`flex items-center gap-1.5 text-[11px] font-semibold px-2.5 py-1 rounded-md transition-colors border ${
                        isDarkMode 
                          ? "text-[#8ab4f8] hover:text-[#a8c7fa] bg-[#004a77]/20 hover:bg-[#004a77]/30 border-[#004a77]/40" 
                          : "text-blue-600 hover:text-blue-700 bg-blue-50/50 hover:bg-blue-50 border-transparent"
                      }`}
                    >
                      <Database size={12} />
                      <span>{expandedLogs[msg.id] ? "Hide Assist Logs" : "Show Assist Logs"}</span>
                      <span className={`text-[9px] px-1.5 py-0.5 rounded-full leading-none font-bold ${
                        isDarkMode ? "bg-[#004a77] text-[#c2e7ff]" : "bg-blue-100 text-blue-800"
                      }`}>{msg.toolLogs.length}</span>
                    </button>
                    
                    {expandedLogs[msg.id] && (
                      <div className={`mt-2 rounded-xl p-4 font-mono text-[11px] overflow-x-auto shadow-inner space-y-3 border ${
                        isDarkMode 
                          ? "bg-[#1e1f20] text-gray-200 border-[#282a2d]" 
                          : "bg-gray-900 text-gray-200 border-gray-800"
                      }`}>
                        <div className={`text-[10px] font-bold border-b pb-1.5 uppercase tracking-wider flex items-center justify-between ${
                          isDarkMode ? "text-[#8e918f] border-[#282a2d]" : "text-gray-500 border-gray-800"
                        }`}>
                          <span>Query Execution Logs (Real-time)</span>
                          <span className="text-gray-600 font-normal">ID: {msg.id}</span>
                        </div>
                        {msg.toolLogs.map((log, lIdx) => (
                          <div key={lIdx} className="space-y-1">
                            <div className="flex items-center gap-2 text-gray-400">
                              <span className="text-[9px] text-gray-600">[{log.timestamp}]</span>
                              <span className={`font-semibold uppercase text-[9px] px-1 rounded ${getLogTypeBadgeClass(log.type, isDarkMode)}`}>
                                {log.type}
                              </span>
                              {log.connector && (
                                <span className="text-gray-500 font-semibold">{log.connector} › {log.tool}</span>
                              )}
                            </div>
                            
                            {log.type === "tool_call" && log.arguments && (
                              <div className={`pl-4 text-purple-300 p-2 rounded border-l-2 whitespace-pre overflow-x-auto max-w-full ${
                                isDarkMode ? "bg-purple-950/10 border-purple-900" : "bg-purple-950/20 border-purple-800"
                              }`}>
                                <strong>Args:</strong> {JSON.stringify(log.arguments, null, 2)}
                              </div>
                            )}
                            
                            {log.type === "tool_result" && log.result && (
                              <div className={`pl-4 text-green-300 p-2 rounded border-l-2 whitespace-pre overflow-x-auto max-h-40 overflow-y-auto max-w-full ${
                                isDarkMode ? "bg-green-950/10 border-green-900" : "bg-green-950/20 border-green-800"
                              }`}>
                                <strong>Result:</strong> {JSON.stringify(log.result, null, 2)}
                              </div>
                            )}
                            
                            {log.type === "error" && log.error && (
                              <div className={`pl-4 text-red-400 p-2 rounded border-l-2 ${
                                isDarkMode ? "bg-red-950/10 border-red-900" : "bg-red-950/20 border-red-800"
                              }`}>
                                <strong>Error Details:</strong> {log.error}
                              </div>
                            )}
                            
                            {log.type === "status" && log.status && (
                              <div className="pl-4 text-gray-400 italic">
                                Status: {log.status}
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}

                {msg.role === "assistant" && (
                  <div className={`flex items-center gap-4 mt-3 ${isDarkMode ? "ml-1 text-[#c4c7c5]" : "ml-8 text-gray-400"}`}>
                    {msg.latency !== undefined && (
                      <span className={`text-[10px] font-semibold font-mono px-2.5 py-0.5 rounded border select-none ${
                        isDarkMode ? "bg-[#1e1f20] border-[#282a2d] text-[#8e918f]" : "bg-gray-50 border-gray-150 text-gray-400"
                      }`} title={`LLM: ${msg.llmLatency}s | Tools: ${msg.toolLatency}s`}>
                        {msg.latency}s {msg.llmLatency !== undefined && msg.toolLatency !== undefined && `(LLM: ${msg.llmLatency}s | Tools: ${msg.toolLatency}s)`}
                      </span>
                    )}
                    <button className={`transition-colors p-0.5 rounded ${isDarkMode ? "hover:text-white" : "hover:text-gray-600"}`} title="Good response"><ThumbsUp size={isDarkMode ? 15 : 13} /></button>
                    <button className={`transition-colors p-0.5 rounded ${isDarkMode ? "hover:text-white" : "hover:text-gray-600"}`} title="Bad response"><ThumbsDown size={isDarkMode ? 15 : 13} /></button>
                    <button 
                      onClick={() => navigator.clipboard.writeText(msg.content)}
                      className={`transition-colors p-0.5 rounded ${isDarkMode ? "hover:text-white" : "hover:text-gray-600"}`}
                      title="Copy text"
                    >
                      <Copy size={isDarkMode ? 15 : 13} />
                    </button>
                    <button className={`transition-colors p-0.5 rounded ${isDarkMode ? "hover:text-white" : "hover:text-gray-600"}`} title="More"><MoreVertical size={isDarkMode ? 15 : 13} /></button>
                  </div>
                )}
              </div>
            ))}

            {/* In-Flight Response Feed */}
            {isStreaming && (
              <div className="flex flex-col items-start w-full">
                <div className="flex items-center gap-2.5 mb-2 ml-1">
                  <AssistantIcon title={
                    activeToolCalls.some(c => c.toLowerCase().includes("sharepoint")) ? "SharePoint Assistant" :
                    activeToolCalls.some(c => c.toLowerCase().includes("jira")) ? "Jira Assistant" : "Gemini Enterprise"
                  } />
                  <span className={`font-semibold text-[13px] tracking-wide select-none ${isDarkMode ? "text-[#e3e3e3]" : "text-gray-800"}`}>
                    {
                      activeToolCalls.some(c => c.toLowerCase().includes("sharepoint")) ? "SharePoint Assistant" :
                      activeToolCalls.some(c => c.toLowerCase().includes("jira")) ? "Jira Assistant" : "Gemini Enterprise"
                    }
                  </span>
                </div>
 
                {/* Running Tool Trace logs */}
                {activeToolCalls.length > 0 && (
                  <div className={`mb-3 p-3 rounded-xl space-y-1.5 text-xs w-full max-w-md border ${
                    isDarkMode ? "ml-1 bg-[#1e1f20] border-[#282a2d] text-[#c4c7c5]" : "ml-8 bg-gray-50 border-gray-100 text-gray-500"
                  }`}>
                    {activeToolCalls.map((call, idx) => (
                      <div key={idx} className="flex items-center gap-2">
                        <CornerDownRight size={12} className={isDarkMode ? "text-[#8ab4f8]" : "text-blue-500"} />
                        <span>{call}</span>
                        <Check size={12} className={`${isDarkMode ? "text-green-400" : "text-green-500"} ml-auto`} />
                      </div>
                    ))}
                  </div>
                )}
 
                {streamingText && (
                  <div className={isDarkMode ? "text-[#e3e3e3] leading-relaxed prose prose-invert prose-sm pl-1 pr-4 mt-2 w-full" : "text-gray-800 leading-relaxed prose prose-sm pl-8 pr-4 -mt-1 w-full"}>
                    {(() => {
                      const { cleanContent } = parseSuggestionsAndContent(streamingText);
                      return renderMessageContent(cleanContent);
                    })()}
                  </div>
                )}
 
                {/* Thinking / Running state */}
                {activeStatus && (
                  <div className={`flex items-center gap-2.5 text-xs mt-2 ${isDarkMode ? "ml-1 text-[#8e918f]" : "ml-8 text-gray-400"}`}>
                    <Loader size={12} className={`animate-spin ${isDarkMode ? "text-[#8e918f]" : "text-gray-400"}`} />
                    <span className="italic">{activeStatus}</span>
                    <span className={`text-[10px] font-semibold font-mono ml-2 px-1.5 py-0.5 rounded border select-none ${
                      isDarkMode ? "bg-[#1e1f20] border-[#282a2d] text-[#c4c7c5]" : "bg-gray-50 border-gray-150 text-gray-500"
                    }`}>
                      {liveLatency}s
                    </span>
                  </div>
                )}
              </div>
            )}

            <div ref={chatEndRef} />
          </div>
        </div>

        {/* Input Bar (Grounded Gemini two-row dark style) */}
        <div className={`p-4 flex flex-col items-center shrink-0 ${isDarkMode ? "bg-[#131314]" : "bg-white"}`}>
          <div className="max-w-3xl w-full mx-auto">
            {/* Input Card */}
            <div className={`flex flex-col rounded-2xl p-3 transition-all ${
              isDarkMode 
                ? "bg-[#1e1f20] border border-[#282a2d] hover:border-[#303134] focus-within:border-[#444746]" 
                : "bg-gray-50 border border-gray-200 hover:border-gray-300 focus-within:border-blue-500 focus-within:ring-2 focus-within:ring-blue-100"
            }`}>
              
              {/* Input Text Area Row */}
              <div className="flex items-center px-2 py-1">
                <Shield size={15} className={`${isDarkMode ? "text-[#c4c7c5] mr-2.5" : "text-gray-400 mr-2"}`} />
                <input 
                  type="text"
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && handleSend()}
                  placeholder={getPlaceholder(connectors)}
                  className={`flex-1 bg-transparent border-none outline-none text-sm py-1 ${
                    isDarkMode ? "text-[#e3e3e3] placeholder-[#8e918f]" : "text-gray-800 placeholder-gray-400"
                  }`}
                  disabled={isStreaming}
                />
              </div>

              {/* Bottom Actions Row */}
              <div className={`flex items-center justify-between border-t pt-2 mt-2 px-1 ${isDarkMode ? "border-[#282a2d]" : "border-gray-100"}`}>
                {/* Left Side Utilities */}
                <div className={`flex items-center gap-2 ${isDarkMode ? "text-[#c4c7c5]" : "text-gray-500"}`}>
                  <button 
                    title="Upload File"
                    className={`p-1.5 rounded-lg transition-colors ${
                      isDarkMode ? "hover:bg-[#282a2d] hover:text-white" : "hover:bg-gray-200 text-gray-500"
                    }`}
                  >
                    <Plus size={16} />
                  </button>
                  {/* Connectors Drawer Toggle */}
                  <button 
                    onClick={() => setDrawerOpen(!drawerOpen)}
                    title="Manage Connectors"
                    className={`p-1.5 rounded-lg transition-colors relative ${
                      isDarkMode ? "hover:bg-[#282a2d] hover:text-white" : "hover:bg-gray-200 text-gray-500"
                    } ${
                      Object.values(connectors).some(c => c.enabled) 
                        ? (isDarkMode ? "text-[#a8c7fa] bg-[#004a77]/30 hover:bg-[#004a77]/50" : "text-blue-600 bg-blue-50/50 hover:bg-blue-100/50") 
                        : ""
                    }`}
                  >
                    <Database size={16} />
                    {Object.values(connectors).some(c => c.enabled) && (
                      <span className={`absolute top-1 right-1 w-2 h-2 rounded-full border ${
                        isDarkMode ? "bg-[#3ddc84] border-[#1e1f20]" : "bg-green-500 border-white"
                      }`} />
                    )}
                  </button>
                </div>

                {/* Right Side Send Button */}
                <button 
                  onClick={() => handleSend()}
                  disabled={!inputText.trim() || isStreaming}
                  className={`p-1.5 transition-colors ${
                    inputText.trim() && !isStreaming
                      ? (isDarkMode 
                          ? "rounded-lg text-[#e3e3e3] hover:bg-[#282a2d]" 
                          : "rounded-full bg-blue-600 text-white hover:bg-blue-700 shadow-sm")
                      : (isDarkMode 
                          ? "rounded-lg text-[#444746] cursor-not-allowed" 
                          : "rounded-full bg-gray-200/80 text-gray-400 cursor-not-allowed")
                  }`}
                >
                  <Send size={isDarkMode ? 16 : 14} className="transform rotate-0" />
                </button>
              </div>
            </div>

            {/* Disclaimer Disclaimer */}
            <div className={`text-[11px] text-center mt-2.5 select-none ${isDarkMode ? "text-[#8e918f]" : "text-gray-400"}`}>
              Generative AI may display inaccurate information, including about people, so double-check its responses.
            </div>
          </div>
        </div>
      </div>

      {/* 3. Right Slide-out Integrations Drawer (Claude style) */}
      <div className={`fixed inset-y-0 right-0 w-96 border-l shadow-xl flex flex-col z-50 transform transition-transform duration-300 ${
        drawerOpen ? "translate-x-0" : "translate-x-full"
      } ${isDarkMode ? "bg-[#1e1f20] border-[#282a2d]" : "bg-white border-gray-200"}`}>
        
        {/* Header */}
        <div className={`p-4 border-b flex items-center justify-between ${isDarkMode ? "border-[#282a2d] bg-[#131314]" : "border-gray-100 bg-gray-50"}`}>
          <div className="flex items-center gap-2">
            <Settings size={18} className={isDarkMode ? "text-[#c4c7c5]" : "text-gray-500"} />
            <h3 className={`font-semibold ${isDarkMode ? "text-[#e3e3e3]" : "text-gray-700"}`}>Integrations & Tools</h3>
          </div>
          <button 
            onClick={() => setDrawerOpen(false)}
            className={`p-1.5 rounded-lg text-sm font-semibold transition-colors ${
              isDarkMode ? "hover:bg-[#282a2d] text-[#c4c7c5] hover:text-white" : "hover:bg-gray-200 text-gray-500"
            }`}
          >
            Close
          </button>
        </div>

        {/* Connectors List */}
        <div className="flex-1 overflow-y-auto p-4 space-y-6">

          {/* SharePoint Connector */}
          <div className={`rounded-xl p-4 shadow-sm space-y-4 border ${isDarkMode ? "bg-[#131314] border-[#282a2d]" : "bg-white border-gray-100"}`}>
            <div className="flex items-start justify-between">
              <div>
                <h4 className={`font-bold text-sm flex items-center gap-1.5 ${isDarkMode ? "text-[#e3e3e3]" : "text-gray-800"}`}>
                  <Database size={16} className={isDarkMode ? "text-[#a8c7fa]" : "text-blue-500"} />
                  Microsoft SharePoint
                </h4>
                <p className={`text-xs mt-1 leading-normal ${isDarkMode ? "text-[#8e918f]" : "text-gray-400"}`}>
                  Retrieve and query corporate documents and metadata via Graph API.
                </p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input 
                  type="checkbox" 
                  checked={connectors.sharepoint.enabled}
                  onChange={() => toggleConnector("sharepoint")}
                  disabled={!connectors.sharepoint.connected}
                  className="sr-only peer"
                />
                <div className={`w-9 h-5 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border after:rounded-full after:h-4 after:w-4 after:transition-all ${
                  isDarkMode ? "bg-[#282a2d] after:border-gray-300 peer-checked:bg-[#0b57d0]" : "bg-gray-200 after:border-gray-300 peer-checked:bg-blue-600"
                }`}></div>
              </label>
            </div>

            <div className={`flex items-center justify-between text-xs border-t pt-3 ${isDarkMode ? "border-[#282a2d]" : "border-gray-50"}`}>
              <span className={isDarkMode ? "text-[#8e918f]" : "text-gray-400"}>Status:</span>
              <div className="flex items-center gap-1.5 font-medium">
                {connectors.sharepoint.connected ? (
                  <>
                    <CheckCircle size={14} className={isDarkMode ? "text-green-400" : "text-green-500"} />
                    <span className={isDarkMode ? "text-green-400" : "text-green-600"}>Connected</span>
                  </>
                ) : (
                  <>
                    <XCircle size={14} className={isDarkMode ? "text-[#8e918f]" : "text-gray-400"} />
                    <span className={isDarkMode ? "text-[#8e918f]" : "text-gray-500"}>Disconnected</span>
                  </>
                )}
              </div>
            </div>

            {/* SharePoint Action */}
            {connectors.sharepoint.connected ? (
              <button 
                onClick={disconnectSharePoint}
                className={`w-full text-center py-2 border rounded-lg text-xs font-semibold transition-colors ${
                  isDarkMode ? "border-red-900/50 text-red-400 hover:bg-red-950/20" : "border-red-200 text-red-500 hover:bg-red-50"
                }`}
              >
                Disconnect SharePoint
              </button>
            ) : (
              <button 
                onClick={connectSharePoint}
                className={`w-full text-center py-2 rounded-lg text-xs font-semibold transition-colors flex items-center justify-center gap-1.5 ${
                  isDarkMode ? "bg-[#0b57d0] text-white hover:bg-[#0b57d0]/90" : "bg-blue-600 text-white hover:bg-blue-700"
                }`}
              >
                <ArrowRight size={12} />
                Connect via Entra ID
              </button>
            )}

            {/* SharePoint Tools Preview */}
            {connectors.sharepoint.connected && (
              <div className={`p-2.5 rounded-lg text-[11px] border ${isDarkMode ? "bg-[#1e1f20] text-[#c4c7c5] border-[#282a2d]" : "bg-gray-50 text-gray-500 border-gray-100"}`}>
                <span className={`font-semibold block mb-1 ${isDarkMode ? "text-[#e3e3e3]" : "text-gray-600"}`}>Exposed Tools (6):</span>
                <div className="space-y-1 font-mono text-[10px]">
                  {["search", "fetch", "list_sites", "list_libraries", "list_files", "read_file"].map((tool) => (
                    <div key={tool} className="flex items-center gap-1.5 py-0.5 px-1.5 rounded hover:bg-black/10 dark:hover:bg-white/5 transition-colors">
                      <span className="w-1 h-1 rounded-full bg-cyan-400"></span>
                      <span className="truncate">{tool}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Jira Connector */}
          <div className={`rounded-xl p-4 shadow-sm space-y-4 border ${isDarkMode ? "bg-[#131314] border-[#282a2d]" : "bg-white border-gray-100"}`}>
            <div className="flex items-start justify-between">
              <div>
                <h4 className={`font-bold text-sm flex items-center gap-1.5 ${isDarkMode ? "text-[#e3e3e3]" : "text-gray-800"}`}>
                  <Database size={16} className={isDarkMode ? "text-[#a8c7fa]" : "text-indigo-500"} />
                  Atlassian Jira
                </h4>
                <p className={`text-xs mt-1 leading-normal ${isDarkMode ? "text-[#8e918f]" : "text-gray-400"}`}>
                  Query issues, tickets, worklogs, and project states.
                </p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input 
                  type="checkbox" 
                  checked={connectors.jira.enabled}
                  onChange={() => toggleConnector("jira")}
                  disabled={!connectors.jira.connected}
                  className="sr-only peer"
                />
                <div className={`w-9 h-5 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border after:rounded-full after:h-4 after:w-4 after:transition-all ${
                  isDarkMode ? "bg-[#282a2d] after:border-gray-300 peer-checked:bg-[#0b57d0]" : "bg-gray-200 after:border-gray-300 peer-checked:bg-blue-600"
                }`}></div>
              </label>
            </div>

            <div className={`flex items-center justify-between text-xs border-t pt-3 ${isDarkMode ? "border-[#282a2d]" : "border-gray-50"}`}>
              <span className={isDarkMode ? "text-[#8e918f]" : "text-gray-400"}>Status:</span>
              <div className="flex items-center gap-1.5 font-medium">
                {connectors.jira.connected ? (
                  <>
                    <CheckCircle size={14} className={isDarkMode ? "text-green-400" : "text-green-500"} />
                    <span className={isDarkMode ? "text-green-400" : "text-green-600"}>Connected</span>
                  </>
                ) : (
                  <>
                    <XCircle size={14} className={isDarkMode ? "text-[#8e918f]" : "text-gray-400"} />
                    <span className={isDarkMode ? "text-[#8e918f]" : "text-gray-500"}>Disconnected</span>
                  </>
                )}
              </div>
            </div>

            {/* Jira configuration details */}
            {!connectors.jira.connected ? (
              <div className={`space-y-2 border-t pt-3 ${isDarkMode ? "border-[#282a2d]" : "border-gray-50"}`}>
                <button 
                  onClick={connectJiraOAuth}
                  disabled={isJiraOAuthConnecting}
                  className={`w-full text-center py-2 rounded-lg text-xs font-semibold transition-colors flex items-center justify-center gap-1.5 ${
                    isJiraOAuthConnecting 
                      ? "bg-gray-400 text-white cursor-not-allowed" 
                      : isDarkMode ? "bg-[#0b57d0] text-white hover:bg-[#0b57d0]/90" : "bg-blue-600 text-white hover:bg-blue-700"
                  }`}
                >
                  {isJiraOAuthConnecting ? (
                    <>
                      <Loader size={14} className="animate-spin" />
                      <span>Connecting...</span>
                    </>
                  ) : (
                    <span>Connect via Atlassian</span>
                  )}
                </button>

                {!showJiraBasicAuth ? (
                  <div className="text-center mt-1">
                    <button 
                      onClick={() => setShowJiraBasicAuth(true)} 
                      className={`text-[10px] hover:underline font-medium ${isDarkMode ? "text-[#8e918f]" : "text-gray-500"}`}
                    >
                      or use Jira basic auth (API Token)
                    </button>
                  </div>
                ) : (
                  <div className="space-y-2 pt-2 border-t border-dashed border-gray-200 mt-2">
                    <div className="space-y-1">
                      <label className={`text-[10px] font-semibold uppercase ${isDarkMode ? "text-[#8e918f]" : "text-gray-500"}`}>Jira URL</label>
                      <input 
                        type="text" 
                        placeholder="https://yoursite.atlassian.net"
                        value={jiraUrlInput}
                        onChange={(e) => setJiraUrlInput(e.target.value)}
                        className={`w-full text-xs px-2.5 py-2 rounded-lg outline-none transition-colors ${
                          isDarkMode ? "bg-[#1e1f20] border border-[#282a2d] text-[#e3e3e3] focus:border-[#0b57d0]" : "bg-white border border-gray-200 text-gray-800 focus:border-blue-500"
                        }`}
                      />
                    </div>
                    <div className="space-y-1">
                      <label className={`text-[10px] font-semibold uppercase ${isDarkMode ? "text-[#8e918f]" : "text-gray-500"}`}>Email</label>
                      <input 
                        type="email" 
                        placeholder="user@example.com"
                        value={jiraEmailInput}
                        onChange={(e) => setJiraEmailInput(e.target.value)}
                        className={`w-full text-xs px-2.5 py-2 rounded-lg outline-none transition-colors ${
                          isDarkMode ? "bg-[#1e1f20] border border-[#282a2d] text-[#e3e3e3] focus:border-[#0b57d0]" : "bg-white border border-gray-200 text-gray-800 focus:border-blue-500"
                        }`}
                      />
                    </div>
                    <div className="space-y-1">
                      <label className={`text-[10px] font-semibold uppercase ${isDarkMode ? "text-[#8e918f]" : "text-gray-500"}`}>API Token</label>
                      <input 
                        type="password" 
                        placeholder="ATATT3xFf..."
                        value={jiraTokenInput}
                        onChange={(e) => setJiraTokenInput(e.target.value)}
                        className={`w-full text-xs px-2.5 py-2 rounded-lg outline-none transition-colors ${
                          isDarkMode ? "bg-[#1e1f20] border border-[#282a2d] text-[#e3e3e3] focus:border-[#0b57d0]" : "bg-white border border-gray-200 text-gray-800 focus:border-blue-500"
                        }`}
                      />
                    </div>
                    <button 
                      onClick={connectJira}
                      className={`w-full text-center py-2 rounded-lg text-xs font-semibold transition-colors mt-2 ${
                        isDarkMode ? "bg-[#0b57d0] text-white hover:bg-[#0b57d0]/90" : "bg-blue-600 text-white hover:bg-blue-700"
                      }`}
                    >
                      Save & Connect Jira (Basic)
                    </button>
                    <div className="text-center mt-1">
                      <button 
                        onClick={() => setShowJiraBasicAuth(false)} 
                        className={`text-[10px] hover:underline font-medium ${isDarkMode ? "text-[#8e918f]" : "text-gray-500"}`}
                      >
                        Hide manual configuration
                      </button>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="space-y-2">
                <div className={`p-2.5 rounded-lg text-xs border ${isDarkMode ? "bg-[#1e1f20] text-[#c4c7c5] border-[#282a2d]" : "bg-gray-50 text-gray-500 border-gray-100"}`}>
                  <span className={`block font-semibold ${isDarkMode ? "text-[#e3e3e3]" : "text-gray-600"}`}>Connection:</span>
                  <span className="block truncate">{connectors.jira.site_url}</span>
                  <span className="block truncate">{connectors.jira.email}</span>
                </div>
                <button 
                  onClick={disconnectJira}
                  className={`w-full text-center py-2 border rounded-lg text-xs font-semibold transition-colors ${
                    isDarkMode ? "border-red-900/50 text-red-400 hover:bg-red-950/20" : "border-red-200 text-red-500 hover:bg-red-50"
                  }`}
                >
                  Disconnect Jira
                </button>

                {/* Jira Tools Preview */}
                <div className={`p-2.5 rounded-lg text-[11px] border ${isDarkMode ? "bg-[#1e1f20] text-[#c4c7c5] border-[#282a2d]" : "bg-gray-50 text-gray-500 border-gray-100"}`}>
                  <span className={`font-semibold block mb-1 ${isDarkMode ? "text-[#e3e3e3]" : "text-gray-600"}`}>Exposed Tools (9):</span>
                  <div className="space-y-1 font-mono text-[10px]">
                    {[
                      "search", 
                      "fetch", 
                      "searchJiraIssuesUsingJql", 
                      "summarizeJiraIssues", 
                      "getJiraIssuesReport", 
                      "getIssueComments", 
                      "getIssueWorklogs", 
                      "getIssueLinks"
                    ].map((tool) => (
                      <div key={tool} className="flex items-center gap-1.5 py-0.5 px-1.5 rounded hover:bg-black/10 dark:hover:bg-white/5 transition-colors">
                        <span className="w-1.5 h-1.5 rounded-full bg-blue-400"></span>
                        <span className="truncate">{tool}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Google Search (Built-in) */}
          <div className={`rounded-xl p-4 shadow-sm space-y-4 border ${isDarkMode ? "bg-[#131314] border-[#282a2d]" : "bg-white border-gray-100"}`}>
            <div className="flex items-start justify-between">
              <div>
                <h4 className={`font-bold text-sm flex items-center gap-1.5 ${isDarkMode ? "text-[#e3e3e3]" : "text-gray-800"}`}>
                  <Globe size={16} className={isDarkMode ? "text-[#a8c7fa]" : "text-teal-500"} />
                  Google Search Grounding
                </h4>
                <p className={`text-xs mt-1 leading-normal ${isDarkMode ? "text-[#8e918f]" : "text-gray-400"}`}>
                  Enable Google Search web-grounding for queries about public information.
                </p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input 
                  type="checkbox" 
                  checked={connectors.google_search.enabled}
                  onChange={() => toggleConnector("google_search")}
                  className="sr-only peer"
                />
                <div className={`w-9 h-5 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border after:rounded-full after:h-4 after:w-4 after:transition-all ${
                  isDarkMode ? "bg-[#282a2d] after:border-gray-300 peer-checked:bg-[#0b57d0]" : "bg-gray-200 after:border-gray-300 peer-checked:bg-blue-600"
                }`}></div>
              </label>
            </div>
            
            <div className={`flex items-center justify-between text-xs border-t pt-3 ${isDarkMode ? "border-[#282a2d]" : "border-gray-50"}`}>
              <span className={isDarkMode ? "text-[#8e918f]" : "text-gray-400"}>Status:</span>
              <div className={`flex items-center gap-1.5 font-medium ${isDarkMode ? "text-green-400" : "text-green-600"}`}>
                <CheckCircle size={14} className={isDarkMode ? "text-green-400" : "text-green-500"} />
                <span>Ready</span>
              </div>
            </div>
          </div>
          
          {/* Agent Engine / Reasoning Engine Mode */}
          <div className={`rounded-xl p-4 shadow-sm space-y-4 border ${isDarkMode ? "bg-[#131314] border-[#282a2d]" : "bg-white border-gray-100"}`}>
            <div className="flex items-start justify-between">
              <div>
                <h4 className={`font-bold text-sm flex items-center gap-1.5 ${isDarkMode ? "text-[#e3e3e3]" : "text-gray-800"}`}>
                  <Zap size={16} className={isDarkMode ? "text-amber-400" : "text-amber-500"} />
                  Vertex Agent Engine
                </h4>
                <p className={`text-xs mt-1 leading-normal ${isDarkMode ? "text-[#8e918f]" : "text-gray-400"}`}>
                  Route queries to the cloud Reasoning Engine instead of running optimized local calling loop.
                </p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input 
                  type="checkbox" 
                  checked={useReasoningEngine}
                  onChange={() => setUseReasoningEngine(!useReasoningEngine)}
                  className="sr-only peer"
                />
                <div className={`w-9 h-5 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border after:rounded-full after:h-4 after:w-4 after:transition-all ${
                  isDarkMode ? "bg-[#282a2d] after:border-gray-300 peer-checked:bg-amber-500" : "bg-gray-200 after:border-gray-300 peer-checked:bg-amber-500"
                }`}></div>
              </label>
            </div>
            
            <div className={`flex items-center justify-between text-xs border-t pt-3 ${isDarkMode ? "border-[#282a2d]" : "border-gray-50"}`}>
              <span className={isDarkMode ? "text-[#8e918f]" : "text-gray-400"}>Location:</span>
              <span className={`font-medium ${isDarkMode ? "text-amber-400" : "text-amber-600"}`}>
                {useReasoningEngine ? "Vertex Engine (us-central1)" : "Local Portal Backend"}
              </span>
            </div>
          </div>

        </div>
      </div>

    </div>
  );
}

export default function App() {
  const [msalReady, setMsalReady] = useState(false);

  useEffect(() => {
    pca.initialize().then(() => {
      setMsalReady(true);
    }).catch(err => {
      console.error("MSAL init error", err);
      // fallback to showing the application anyway (Jira will still work)
      setMsalReady(true);
    });
  }, []);

  if (!msalReady) {
    return (
      <div className="h-screen w-screen flex flex-col items-center justify-center bg-gray-50 text-gray-500">
        <Loader className="animate-spin mb-4 text-blue-500" size={32} />
        <span>Initializing authentication context...</span>
      </div>
    );
  }

  return (
    <MsalProvider instance={pca}>
      <MainApp />
    </MsalProvider>
  );
}
