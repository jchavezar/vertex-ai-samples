// Vertex Cowork - Enterprise AI Platform with Chat & Workflow Builder
// Google Cloud themed UI

import { useState, useRef, useEffect, useCallback, CSSProperties } from "react";
import { motion, AnimatePresence } from "framer-motion";
import ReactMarkdown from "react-markdown";
import {
  Send, Plus, Menu, X, Trash2, Sparkles, Copy, Check, Zap,
  MessageSquare, Settings, GitBranch, Play, Square, Circle,
  ArrowRight, Bot, Cpu, Database, Globe, ChevronDown, Link,
  Server, Github, FileText, Brain, Search, Chrome, MessageCircle,
  HardDrive, Plug,
} from "lucide-react";
import { useStore } from "./hooks/useStore";
import { agentsApi, modelsApi, mcpApi, quickChatApi } from "./utils/api";
import type { Agent, ChatMessage, Model, MCPServer } from "./types";

// Google Cloud Theme
const theme = {
  // Google Cloud colors
  bg: "#F8F9FA",
  bgSecondary: "#E8EAED",
  bgTertiary: "#DADCE0",
  surface: "#FFFFFF",
  border: "rgba(0,0,0,0.08)",
  borderHover: "rgba(0,0,0,0.15)",
  text: "#202124",
  textSecondary: "#5F6368",
  textTertiary: "#80868B",
  // Google Blue
  primary: "#1A73E8",
  primaryLight: "#E8F0FE",
  primaryDark: "#1557B0",
  // Accent colors
  green: "#34A853",
  yellow: "#FBBC04",
  red: "#EA4335",
  // Chat
  userBg: "#1A73E8",
  userText: "#FFFFFF",
  aiBg: "#E8F0FE",
  aiText: "#202124",
  // Shadows
  shadow: "0 1px 3px rgba(60,64,67,0.15)",
  shadowLg: "0 4px 12px rgba(60,64,67,0.2)",
};

type ViewMode = "chat" | "workflow";

interface WorkflowNode {
  id: string;
  type: "agent" | "input" | "output" | "condition" | "tool" | "mcp";
  label: string;
  x: number;
  y: number;
  config?: Record<string, any>;
}

interface WorkflowConnection {
  id: string;
  from: string;
  to: string;
  label?: string;
}

// Pre-configured MCP servers with required env vars
interface MCPTemplate {
  id: string;
  name: string;
  command: string;
  icon: string;
  description: string;
  envVars?: { key: string; label: string; placeholder: string; required?: boolean }[];
  args?: { key: string; label: string; placeholder: string; required?: boolean }[];
}

const POPULAR_MCP_SERVERS: MCPTemplate[] = [
  { id: "github", name: "GitHub", command: "npx -y @modelcontextprotocol/server-github", icon: "github", description: "GitHub repos, issues, PRs", envVars: [{ key: "GITHUB_PERSONAL_ACCESS_TOKEN", label: "GitHub Token", placeholder: "ghp_xxxx...", required: true }] },
  { id: "filesystem", name: "Filesystem", command: "npx -y @modelcontextprotocol/server-filesystem", icon: "file", description: "Local file access", args: [{ key: "path", label: "Allowed Path", placeholder: "/home/user/projects", required: true }] },
  { id: "postgres", name: "PostgreSQL", command: "npx -y @modelcontextprotocol/server-postgres", icon: "database", description: "Database queries", envVars: [{ key: "POSTGRES_CONNECTION_STRING", label: "Connection String", placeholder: "postgresql://user:pass@host:5432/db", required: true }] },
  { id: "memory", name: "Memory", command: "npx -y @modelcontextprotocol/server-memory", icon: "brain", description: "Knowledge storage" },
  { id: "brave-search", name: "Brave Search", command: "npx -y @modelcontextprotocol/server-brave-search", icon: "search", description: "Web search", envVars: [{ key: "BRAVE_API_KEY", label: "Brave API Key", placeholder: "BSA...", required: true }] },
  { id: "puppeteer", name: "Puppeteer", command: "npx -y @modelcontextprotocol/server-puppeteer", icon: "chrome", description: "Browser automation" },
  { id: "slack", name: "Slack", command: "npx -y @modelcontextprotocol/server-slack", icon: "message", description: "Slack integration", envVars: [{ key: "SLACK_BOT_TOKEN", label: "Slack Bot Token", placeholder: "xoxb-...", required: true }, { key: "SLACK_TEAM_ID", label: "Team ID", placeholder: "T01234567" }] },
  { id: "sequential-thinking", name: "Sequential Thinking", command: "npx -y @modelcontextprotocol/server-sequential-thinking", icon: "brain", description: "Step-by-step reasoning" },
];

function App() {
  const {
    agents, setAgents, selectedAgent, setSelectedAgent, addAgent,
    models, setModels, chatMessages, addChatMessage,
  } = useStore();

  const [viewMode, setViewMode] = useState<ViewMode>("chat");
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId] = useState(() => `session_${Date.now()}`);
  const [showNewAgent, setShowNewAgent] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [showMcpPanel, setShowMcpPanel] = useState(false);
  const [mcpServers, setMcpServers] = useState<MCPServer[]>([]);
  const [copiedIdx, setCopiedIdx] = useState<number | null>(null);
  const [mcpConfiguring, setMcpConfiguring] = useState<MCPTemplate | null>(null);
  const [mcpFormValues, setMcpFormValues] = useState<Record<string, string>>({});
  const [showCustomMcp, setShowCustomMcp] = useState(false);
  const [mcpConnecting, setMcpConnecting] = useState<string | null>(null);

  // Quick chat state
  const [quickModel, setQuickModel] = useState("gemini-2.5-flash");
  const [quickMessages, setQuickMessages] = useState<ChatMessage[]>([]);
  const [quickMcpEnabled, setQuickMcpEnabled] = useState(false);
  const [quickMcpServers, setQuickMcpServers] = useState<string[]>([]);
  const [githubUser, setGithubUser] = useState<{ login: string; name: string } | null>(null);
  const [githubRepos, setGithubRepos] = useState<Array<{ name: string; full_name: string; description: string; language: string; stars: number }>>([]);

  // Workflow state
  const [nodes, setNodes] = useState<WorkflowNode[]>([]);
  const [connections, setConnections] = useState<WorkflowConnection[]>([]);
  const [selectedNode, setSelectedNode] = useState<string | null>(null);
  const [draggingNode, setDraggingNode] = useState<string | null>(null);
  const [connecting, setConnecting] = useState<string | null>(null);
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const canvasRef = useRef<HTMLDivElement>(null);

  const messages = selectedAgent
    ? chatMessages[selectedAgent.agent_id] || []
    : quickMessages;

  useEffect(() => { loadData(); }, []);
  useEffect(() => { messagesEndRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages]);
  useEffect(() => { inputRef.current?.focus(); }, [selectedAgent, viewMode]);

  // Fetch GitHub context (user + repos) when GitHub MCP is connected
  useEffect(() => {
    const connectedCount = mcpServers.filter(s => s.connected).length;

    // Auto-disable MCP if no servers connected
    if (connectedCount === 0 && quickMcpEnabled) {
      setQuickMcpEnabled(false);
    }

    const fetchGithubContext = async () => {
      const githubServer = mcpServers.find(s => s.server_id === "github" && s.connected);
      if (githubServer) {
        try {
          const context = await mcpApi.getContext("github");
          if (context.user) {
            setGithubUser({ login: context.user.login, name: context.user.name });
          }
          if (context.repos) {
            setGithubRepos(context.repos);
          }
        } catch (e) {
          console.debug("Could not fetch GitHub context:", e);
        }
      } else {
        setGithubUser(null);
        setGithubRepos([]);
      }
    };
    fetchGithubContext();
  }, [mcpServers]);

  const loadData = async () => {
    try {
      const [agentsList, modelsList, serversList] = await Promise.all([
        agentsApi.list(),
        modelsApi.list(),
        mcpApi.list().catch(() => []),
      ]);
      setAgents(agentsList);
      setModels(modelsList);
      setMcpServers(serversList);
    } catch (e) { console.error(e); }
  };

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;
    const msg = input.trim();
    const newMsg: ChatMessage = { role: "user", content: msg, timestamp: new Date() };

    if (selectedAgent) {
      addChatMessage(selectedAgent.agent_id, newMsg);
    } else {
      setQuickMessages(prev => [...prev, newMsg]);
    }

    setInput("");
    setIsLoading(true);

    try {
      let response;
      if (selectedAgent) {
        response = await agentsApi.chat(selectedAgent.agent_id, msg, sessionId);
      } else {
        const connectedMcp = quickMcpEnabled ? mcpServers.filter(s => s.connected).map(s => s.server_id) : [];
        let systemPrompt: string;
        if (quickMcpEnabled && connectedMcp.length > 0) {
          const tools = connectedMcp.map(id => {
            if (id === "github") return "GitHub (repos, issues, PRs, code search)";
            if (id === "memory") return "Memory (persistent storage)";
            return id;
          }).join(", ");

          // Build repos context
          const reposContext = githubRepos.length > 0
            ? `\n**Your Repositories (${githubRepos.length}):**\n${githubRepos.map(r =>
                `- **${r.name}**${r.language ? ` (${r.language})` : ""}${r.description ? `: ${r.description}` : ""}`
              ).join("\n")}`
            : "";

          systemPrompt = `You are an intelligent, autonomous AI assistant with access to external tools via MCP.

**Available tools:** ${tools}
${githubUser ? `
**User Identity:** Authenticated as **@${githubUser.login}**${githubUser.name ? ` (${githubUser.name})` : ""}
${reposContext}

**CRITICAL - Smart Repo Matching:**
- You KNOW the user's repos listed above. Use this knowledge!
- If user asks about something matching one of THEIR repos, recognize it immediately
- Example: "tell me about vertex-ai-samples" → "You have **vertex-ai-samples** - here's what's in YOUR repo..."
- For queries like "my AI projects", filter/match against the repos you know they own
- When unsure, clarify: "You have X and Y repos - which one?"
` : ""}

**Behavior:**
- Be PROACTIVE and INTELLIGENT - analyze, don't just list
- MATCH queries against user's known repos first
- Lead with the most relevant answer
- Use tools automatically, format cleanly with markdown`;
        } else {
          systemPrompt = `You are a helpful AI assistant. You do NOT have access to external tools, APIs, or real-time data.

If the user asks for something that requires external access (like GitHub repos, files, current weather, or live data), explain clearly:
- "I don't have access to external tools right now."
- "To use GitHub/external services, enable MCP tools using the toggle button above."

Offer to help with questions you can answer from your training data instead.`;
        }
        // Send conversation history for context
        const history = quickMessages.map(m => ({ role: m.role, content: m.content }));
        response = await quickChatApi.send(msg, quickModel, systemPrompt, sessionId, connectedMcp, history);
      }

      const assistantMsg: ChatMessage = {
        role: "assistant",
        content: response.content,
        tool_calls: response.tool_calls,
        timestamp: new Date()
      };

      if (selectedAgent) {
        addChatMessage(selectedAgent.agent_id, assistantMsg);
      } else {
        setQuickMessages(prev => [...prev, assistantMsg]);
      }
    } catch (e: any) {
      const errorMsg: ChatMessage = { role: "assistant", content: `Error: ${e.message}`, timestamp: new Date() };
      if (selectedAgent) {
        addChatMessage(selectedAgent.agent_id, errorMsg);
      } else {
        setQuickMessages(prev => [...prev, errorMsg]);
      }
    } finally {
      setIsLoading(false);
      inputRef.current?.focus();
    }
  };

  const copy = (text: string, i: number) => {
    navigator.clipboard.writeText(text);
    setCopiedIdx(i);
    setTimeout(() => setCopiedIdx(null), 2000);
  };

  const deleteAgent = async (id: string) => {
    await agentsApi.delete(id);
    const updated = agents.filter(a => a.agent_id !== id);
    setAgents(updated);
    if (selectedAgent?.agent_id === id) setSelectedAgent(null);
  };

  // Workflow functions
  const addNode = (type: WorkflowNode["type"]) => {
    const labels: Record<string, string> = {
      agent: "Agent", input: "Input", output: "Output",
      condition: "Condition", tool: "Tool", mcp: "MCP Server",
    };
    const newNode: WorkflowNode = {
      id: `node_${Date.now()}`,
      type,
      label: labels[type],
      x: 150 + Math.random() * 300,
      y: 100 + Math.random() * 200,
    };
    setNodes(prev => [...prev, newNode]);
  };

  const handleNodeMouseDown = (e: React.MouseEvent, nodeId: string) => {
    e.stopPropagation();
    if (connecting) {
      if (connecting !== nodeId) {
        const newConn: WorkflowConnection = {
          id: `conn_${Date.now()}`,
          from: connecting,
          to: nodeId,
        };
        setConnections(prev => [...prev, newConn]);
      }
      setConnecting(null); setConnectingMouse(null);
    } else {
      const node = nodes.find(n => n.id === nodeId);
      if (node && canvasRef.current) {
        const rect = canvasRef.current.getBoundingClientRect();
        setDragOffset({
          x: e.clientX - rect.left - node.x,
          y: e.clientY - rect.top - node.y,
        });
      }
      setDraggingNode(nodeId);
      setSelectedNode(nodeId);
    }
  };

  const [connectingMouse, setConnectingMouse] = useState<{ x: number; y: number } | null>(null);

  const handleCanvasMouseMove = (e: React.MouseEvent) => {
    if (canvasRef.current) {
      const rect = canvasRef.current.getBoundingClientRect();

      // Track mouse for connection line
      if (connecting) {
        setConnectingMouse({
          x: e.clientX - rect.left,
          y: e.clientY - rect.top,
        });
      }

      // Handle node dragging
      if (draggingNode) {
        const x = e.clientX - rect.left - dragOffset.x;
        const y = e.clientY - rect.top - dragOffset.y;
        setNodes(prev => prev.map(n =>
          n.id === draggingNode ? { ...n, x: Math.max(0, x), y: Math.max(0, y) } : n
        ));
      }
    }
  };

  const handleCanvasMouseUp = () => {
    setDraggingNode(null);
    // Cancel connection if released on empty canvas (not on input port)
    if (connecting) {
      setConnecting(null); setConnectingMouse(null);
    }
  };

  const deleteNode = (nodeId: string) => {
    setNodes(prev => prev.filter(n => n.id !== nodeId));
    setConnections(prev => prev.filter(c => c.from !== nodeId && c.to !== nodeId));
    setSelectedNode(null);
  };

  const deleteConnection = (connId: string) => {
    setConnections(prev => prev.filter(c => c.id !== connId));
  };

  const startConnecting = (e: React.MouseEvent, nodeId: string) => {
    e.stopPropagation();
    setConnecting(nodeId);
  };

  // Start MCP server configuration
  const startMcpConfig = (server: MCPTemplate) => {
    if (server.envVars || server.args) {
      setMcpConfiguring(server);
      setMcpFormValues({});
    } else {
      // No config needed, add directly
      addMcpServerDirect(server, {});
    }
  };

  // Add MCP server with config and auto-connect
  const addMcpServerDirect = async (server: MCPTemplate, config: Record<string, string>) => {
    try {
      // Build command with args if any
      let command = server.command;
      if (server.args) {
        const argValues = server.args.map(a => config[a.key] || "").filter(Boolean);
        if (argValues.length > 0) {
          command = `${server.command} ${argValues.join(" ")}`;
        }
      }

      // Register the server
      await mcpApi.register({
        server_id: server.id,
        name: server.name,
        transport: "stdio",
        command,
        config: server.envVars ? { env: Object.fromEntries(server.envVars.map(e => [e.key, config[e.key] || ""])) } : {},
      });

      // Auto-connect after registration
      setMcpConnecting(server.id);
      try {
        const connected = await mcpApi.connect(server.id);
        alert(`✓ ${server.name} connected with ${connected.tools?.length || 0} tools!`);
      } catch (connectErr: any) {
        alert(`Registered but failed to connect: ${connectErr.response?.data?.detail || connectErr.message}`);
      } finally {
        setMcpConnecting(null);
      }

      setMcpConfiguring(null);
      setMcpFormValues({});
      await loadData();
    } catch (e: any) {
      alert(`Failed to register server: ${e.response?.data?.detail || e.message}`);
      console.error(e);
    }
  };

  const submitMcpConfig = () => {
    if (!mcpConfiguring) return;
    // Validate required fields
    const allRequired = [
      ...(mcpConfiguring.envVars?.filter(e => e.required) || []),
      ...(mcpConfiguring.args?.filter(a => a.required) || []),
    ];
    const missing = allRequired.filter(f => !mcpFormValues[f.key]?.trim());
    if (missing.length > 0) {
      alert(`Please fill required fields: ${missing.map(f => f.label).join(", ")}`);
      return;
    }
    addMcpServerDirect(mcpConfiguring, mcpFormValues);
  };

  return (
    <div style={styles.app}>
      {/* Desktop Sidebar */}
      <aside style={styles.desktopSidebar}>
        <div style={styles.sidebarHeader}>
          <div style={styles.logo}>
            <div style={styles.logoIcon}>
              <Zap size={18} color="#fff" />
            </div>
            <span style={{ fontWeight: 600, fontSize: 15 }}>Vertex Cowork</span>
          </div>
        </div>

        {/* View Mode Tabs */}
        <div style={styles.viewTabs}>
          <button
            style={{ ...styles.viewTab, ...(viewMode === "chat" ? styles.viewTabActive : {}) }}
            onClick={() => setViewMode("chat")}
          >
            <MessageSquare size={16} />
            <span>Chat</span>
          </button>
          <button
            style={{ ...styles.viewTab, ...(viewMode === "workflow" ? styles.viewTabActive : {}) }}
            onClick={() => setViewMode("workflow")}
          >
            <GitBranch size={16} />
            <span>Workflow</span>
          </button>
        </div>

        {viewMode === "chat" && (
          <>
            <button
              style={{ ...styles.quickChatBtn, ...(!selectedAgent ? styles.quickChatBtnActive : {}) }}
              onClick={() => setSelectedAgent(null)}
            >
              <Sparkles size={16} color={!selectedAgent ? theme.primary : theme.textTertiary} />
              <span>Quick Chat</span>
              {!selectedAgent && <span style={styles.activeDot} />}
            </button>

            <div style={styles.sectionLabel}>Agents</div>

            <button style={styles.newAgentBtn} onClick={() => setShowNewAgent(true)}>
              <Plus size={16} />
              <span>New Agent</span>
            </button>

            <div style={styles.agentsList}>
              {agents.length === 0 ? (
                <div style={styles.emptyList}>No agents yet</div>
              ) : (
                agents.map(agent => (
                  <button
                    key={agent.agent_id}
                    onClick={() => setSelectedAgent(agent)}
                    style={{
                      ...styles.agentItem,
                      ...(selectedAgent?.agent_id === agent.agent_id ? styles.agentItemActive : {}),
                    }}
                  >
                    <Bot size={16} style={{ opacity: 0.6, flexShrink: 0 }} />
                    <span style={styles.agentName}>{agent.name}</span>
                    <button
                      onClick={(e) => { e.stopPropagation(); deleteAgent(agent.agent_id); }}
                      style={styles.deleteBtn}
                    >
                      <Trash2 size={14} />
                    </button>
                  </button>
                ))
              )}
            </div>
          </>
        )}

        {viewMode === "workflow" && (
          <>
            <div style={styles.sectionLabel}>Add Nodes</div>
            <div style={styles.nodeButtons}>
              {[
                { type: "input" as const, icon: <Circle size={14} />, color: theme.green },
                { type: "agent" as const, icon: <Bot size={14} />, color: theme.primary },
                { type: "mcp" as const, icon: <Plug size={14} />, color: "#9C27B0" },
                { type: "tool" as const, icon: <Cpu size={14} />, color: theme.yellow },
                { type: "condition" as const, icon: <GitBranch size={14} />, color: "#FF9800" },
                { type: "output" as const, icon: <Square size={14} />, color: theme.red },
              ].map(({ type, icon, color }) => (
                <button key={type} style={styles.nodeBtn} onClick={() => addNode(type)}>
                  <span style={{ color }}>{icon}</span>
                  <span style={{ textTransform: "capitalize" }}>{type}</span>
                </button>
              ))}
            </div>

            {selectedNode && (
              <div style={styles.nodeConfig}>
                <div style={styles.sectionLabel}>Selected: {nodes.find(n => n.id === selectedNode)?.label}</div>
                <button style={{ ...styles.nodeBtn, color: theme.red }} onClick={() => deleteNode(selectedNode)}>
                  <Trash2 size={14} />
                  <span>Delete Node</span>
                </button>
              </div>
            )}

            {connections.length > 0 && (
              <div style={styles.nodeConfig}>
                <div style={styles.sectionLabel}>Connections ({connections.length})</div>
                {connections.map(c => (
                  <div key={c.id} style={{ display: "flex", alignItems: "center", padding: "4px 12px", fontSize: 12 }}>
                    <span style={{ flex: 1, color: theme.textSecondary }}>
                      {nodes.find(n => n.id === c.from)?.label} → {nodes.find(n => n.id === c.to)?.label}
                    </span>
                    <button style={{ ...styles.iconBtn, padding: 2 }} onClick={() => deleteConnection(c.id)}>
                      <X size={12} />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </>
        )}

        <div style={styles.sidebarFooter}>
          <button style={styles.footerBtn} onClick={() => setShowMcpPanel(true)}>
            <Plug size={16} />
            <span>MCP Servers</span>
            {mcpServers.length > 0 && <span style={styles.badge}>{mcpServers.length}</span>}
          </button>
          <button style={styles.footerBtn} onClick={() => setShowSettings(true)}>
            <Settings size={16} />
            <span>Settings</span>
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main style={styles.main}>
        {viewMode === "chat" ? (
          <>
            <header style={styles.header}>
              <div style={styles.headerCenter}>
                {selectedAgent ? (
                  <>
                    <Bot size={18} color={theme.primary} />
                    <span style={styles.headerTitle}>{selectedAgent.name}</span>
                    <span style={styles.headerBadge}>{selectedAgent.model_id}</span>
                  </>
                ) : (
                  <>
                    <Sparkles size={18} color={theme.primary} />
                    <span style={styles.headerTitle}>Quick Chat</span>
                    <select style={styles.modelSelect} value={quickModel} onChange={e => setQuickModel(e.target.value)}>
                      {models.map(m => (
                        <option key={m.model_id} value={m.model_id}>{m.display_name}</option>
                      ))}
                    </select>
                    {mcpServers.filter(s => s.connected).length > 0 && (
                      <button
                        style={{
                          ...styles.smallBtn,
                          background: quickMcpEnabled ? theme.primary : theme.bgSecondary,
                          color: quickMcpEnabled ? "#fff" : theme.textSecondary,
                          display: "flex",
                          alignItems: "center",
                          gap: 4,
                          marginLeft: 8,
                        }}
                        onClick={() => setQuickMcpEnabled(!quickMcpEnabled)}
                        title={quickMcpEnabled ? "MCP tools enabled - click to disable" : "Click to enable MCP tools"}
                      >
                        <Plug size={14} />
                        <span>MCP {quickMcpEnabled ? "ON" : "OFF"}</span>
                        {quickMcpEnabled && (
                          <span style={{ background: theme.green, color: "#fff", borderRadius: 10, padding: "0 6px", fontSize: 11, marginLeft: 2 }}>
                            {mcpServers.filter(s => s.connected).length}
                          </span>
                        )}
                      </button>
                    )}
                  </>
                )}
              </div>
              <div style={{ display: "flex", gap: 8 }}>
                <button style={styles.iconBtn} onClick={() => setShowMcpPanel(true)} title="MCP Servers">
                  <Plug size={18} />
                </button>
                <button style={styles.iconBtn} onClick={() => setShowNewAgent(true)}>
                  <Plus size={18} />
                </button>
              </div>
            </header>

            <div style={styles.chat}>
              {messages.length === 0 ? (
                <div style={styles.welcome}>
                  <div style={styles.welcomeIcon}>
                    {selectedAgent ? <Bot size={32} color={theme.primary} /> : <Sparkles size={32} color={theme.primary} />}
                  </div>
                  <h1 style={styles.welcomeTitle}>{selectedAgent ? selectedAgent.name : "Quick Chat"}</h1>
                  <p style={styles.welcomeText}>
                    {selectedAgent ? `Powered by ${selectedAgent.model_id}` : "Chat instantly with AI - no agent setup required"}
                  </p>
                  <div style={styles.suggestions}>
                    {["Explain quantum computing", "Write a Python function", "Help me brainstorm"].map(s => (
                      <button key={s} style={styles.suggestionBtn} onClick={() => setInput(s)}>{s}</button>
                    ))}
                  </div>
                </div>
              ) : (
                <div style={styles.messages}>
                  {messages.map((m, i) => (
                    <motion.div key={i} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} style={m.role === "user" ? styles.userRow : styles.aiRow}>
                      <div style={m.role === "user" ? styles.userBubble : styles.aiBubble}>
                        {m.role === "assistant" && (
                          <div style={styles.aiHeader}>
                            <Sparkles size={14} color={theme.primary} />
                            <span style={{ fontSize: 12, fontWeight: 600, color: theme.primary }}>{selectedAgent?.name || "Assistant"}</span>
                          </div>
                        )}
                        {m.role === "user" ? (
                          <p style={styles.messageText}>{m.content}</p>
                        ) : (
                          <div className="markdown-content" style={{ lineHeight: 1.7 }}>
                            <ReactMarkdown
                              components={{
                                p: ({ children }) => <p style={{ margin: "0 0 12px 0" }}>{children}</p>,
                                ul: ({ children }) => <ul style={{ margin: "8px 0", paddingLeft: 24 }}>{children}</ul>,
                                ol: ({ children }) => <ol style={{ margin: "8px 0", paddingLeft: 24 }}>{children}</ol>,
                                li: ({ children }) => <li style={{ marginBottom: 4 }}>{children}</li>,
                                code: ({ children, className }) => className?.includes("language-")
                                  ? <code style={{ display: "block" }}>{children}</code>
                                  : <code style={{ background: theme.bgSecondary, padding: "2px 6px", borderRadius: 4, fontSize: 13, fontFamily: "monospace" }}>{children}</code>,
                                pre: ({ children }) => <pre style={{ background: theme.bgSecondary, padding: 12, borderRadius: 8, overflow: "auto", margin: "12px 0", fontSize: 13, fontFamily: "monospace" }}>{children}</pre>,
                                a: ({ children, href }) => <a href={href} target="_blank" rel="noopener noreferrer" style={{ color: theme.primary }}>{children}</a>,
                                strong: ({ children }) => <strong style={{ fontWeight: 600 }}>{children}</strong>,
                                h1: ({ children }) => <h1 style={{ fontSize: 20, fontWeight: 600, margin: "16px 0 8px" }}>{children}</h1>,
                                h2: ({ children }) => <h2 style={{ fontSize: 18, fontWeight: 600, margin: "14px 0 8px" }}>{children}</h2>,
                                h3: ({ children }) => <h3 style={{ fontSize: 16, fontWeight: 600, margin: "12px 0 6px" }}>{children}</h3>,
                              }}
                            >{m.content}</ReactMarkdown>
                          </div>
                        )}
                        {m.role === "assistant" && (
                          <button style={styles.copyBtn} onClick={() => copy(m.content, i)}>
                            {copiedIdx === i ? <Check size={14} color={theme.green} /> : <Copy size={14} />}
                          </button>
                        )}
                      </div>
                    </motion.div>
                  ))}
                  {isLoading && (
                    <div style={styles.aiRow}>
                      <div style={styles.aiBubble}>
                        <div style={styles.typing}>
                          {[0, 1, 2].map(i => (
                            <motion.span key={i} style={styles.dot} animate={{ opacity: [0.3, 1, 0.3] }} transition={{ duration: 1, repeat: Infinity, delay: i * 0.2 }} />
                          ))}
                        </div>
                      </div>
                    </div>
                  )}
                  <div ref={messagesEndRef} />
                </div>
              )}
            </div>

            <div style={styles.inputArea}>
              <div style={styles.inputContainer}>
                <textarea
                  ref={inputRef}
                  value={input}
                  onChange={e => setInput(e.target.value)}
                  onKeyDown={e => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); handleSend(); } }}
                  placeholder="Message..."
                  style={styles.input}
                  rows={1}
                  onInput={e => {
                    const t = e.target as HTMLTextAreaElement;
                    t.style.height = "auto";
                    t.style.height = Math.min(t.scrollHeight, 150) + "px";
                  }}
                />
                <button onClick={handleSend} disabled={!input.trim() || isLoading} style={{ ...styles.sendBtn, ...(!input.trim() || isLoading ? styles.sendBtnDisabled : {}) }}>
                  <Send size={18} />
                </button>
              </div>
            </div>
          </>
        ) : (
          <>
            <header style={styles.header}>
              <div style={styles.headerCenter}>
                <GitBranch size={18} color={theme.primary} />
                <span style={styles.headerTitle}>Workflow Builder</span>
                <span style={styles.headerBadge}>{nodes.length} nodes · {connections.length} connections</span>
              </div>
              <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
                {connecting && (
                  <span style={{ fontSize: 12, color: theme.primary, padding: "6px 12px", background: theme.primaryLight, borderRadius: 6 }}>
                    Click target node to connect
                  </span>
                )}
                <button style={{ ...styles.iconBtn, background: theme.green, color: "#fff", borderRadius: 8 }}>
                  <Play size={18} />
                </button>
              </div>
            </header>

            <div
              ref={canvasRef}
              style={styles.canvas}
              onMouseMove={handleCanvasMouseMove}
              onMouseUp={handleCanvasMouseUp}
              onMouseLeave={handleCanvasMouseUp}
              onClick={() => { setSelectedNode(null); setConnecting(null); setConnectingMouse(null); }}
            >
              <svg style={styles.connectionsSvg}>
                {/* Draw existing connections */}
                {connections.map((conn) => {
                  const fromNode = nodes.find(n => n.id === conn.from);
                  const toNode = nodes.find(n => n.id === conn.to);
                  if (!fromNode || !toNode) return null;

                  // Calculate node widths based on label length (approx 8px per char + padding)
                  const fromWidth = Math.max(120, fromNode.label.length * 8 + 80);
                  const toWidth = Math.max(120, toNode.label.length * 8 + 80);
                  const nodeHeight = 52;

                  // Output port (right edge) to Input port (left edge)
                  const x1 = fromNode.x + fromWidth;
                  const y1 = fromNode.y + nodeHeight / 2;
                  const x2 = toNode.x;
                  const y2 = toNode.y + nodeHeight / 2;
                  const ctrlOffset = Math.max(Math.abs(x2 - x1) / 2, 50);

                  return (
                    <g key={conn.id}>
                      <path
                        d={`M ${x1} ${y1} C ${x1 + ctrlOffset} ${y1}, ${x2 - ctrlOffset} ${y2}, ${x2} ${y2}`}
                        fill="none"
                        stroke={theme.primary}
                        strokeWidth={2}
                        strokeLinecap="round"
                      />
                      {/* Connection endpoint dots */}
                      <circle cx={x1} cy={y1} r={4} fill={theme.primary} />
                      <circle cx={x2} cy={y2} r={4} fill={theme.primary} />
                    </g>
                  );
                })}
                {/* Draw temporary connection line while dragging */}
                {connecting && connectingMouse && (() => {
                  const fromNode = nodes.find(n => n.id === connecting);
                  if (!fromNode) return null;
                  const fromWidth = Math.max(120, fromNode.label.length * 8 + 80);
                  const x1 = fromNode.x + fromWidth;
                  const y1 = fromNode.y + 26;
                  const x2 = connectingMouse.x;
                  const y2 = connectingMouse.y;
                  const ctrlOffset = Math.max(Math.abs(x2 - x1) / 2, 50);
                  return (
                    <g>
                      <path
                        d={`M ${x1} ${y1} C ${x1 + ctrlOffset} ${y1}, ${x2 - ctrlOffset} ${y2}, ${x2} ${y2}`}
                        fill="none"
                        stroke={theme.primary}
                        strokeWidth={2}
                        strokeDasharray="6,4"
                        opacity={0.7}
                      />
                      <circle cx={x1} cy={y1} r={4} fill={theme.primary} />
                    </g>
                  );
                })()}
              </svg>

              {nodes.map(node => {
                const colors: Record<string, string> = {
                  input: theme.green, agent: theme.primary, tool: theme.yellow,
                  condition: "#FF9800", output: theme.red, mcp: "#9C27B0",
                };
                const icons: Record<string, JSX.Element> = {
                  input: <Circle size={16} />, agent: <Bot size={16} />, tool: <Cpu size={16} />,
                  condition: <GitBranch size={16} />, output: <Square size={16} />, mcp: <Plug size={16} />,
                };
                const nodeColor = colors[node.type];
                return (
                  <div
                    key={node.id}
                    style={{
                      ...styles.workflowNode,
                      left: node.x, top: node.y,
                      borderColor: selectedNode === node.id ? nodeColor : (connecting ? theme.primary : theme.border),
                      boxShadow: selectedNode === node.id ? `0 0 0 2px ${nodeColor}40` : theme.shadow,
                    }}
                    onMouseDown={(e) => handleNodeMouseDown(e, node.id)}
                    onMouseUp={(e) => {
                      // Allow dropping connection on the whole node (easier target)
                      if (connecting && connecting !== node.id && node.type !== "input") {
                        e.stopPropagation();
                        const newConn: WorkflowConnection = {
                          id: `conn_${Date.now()}`,
                          from: connecting,
                          to: node.id,
                        };
                        setConnections(prev => [...prev, newConn]);
                        setConnecting(null); setConnectingMouse(null);
                      }
                    }}
                  >
                    {/* Input port (left side) - not for input nodes */}
                    {node.type !== "input" && (
                      <div
                        style={{
                          position: "absolute",
                          left: -8,
                          top: "50%",
                          transform: "translateY(-50%)",
                          width: 16,
                          height: 16,
                          borderRadius: "50%",
                          background: connecting ? theme.primary : theme.surface,
                          border: `3px solid ${nodeColor}`,
                          cursor: "pointer",
                          zIndex: 20,
                          transition: "transform 0.15s, background 0.15s",
                        }}
                        onMouseUp={(e) => {
                          e.stopPropagation();
                          e.preventDefault();
                          if (connecting && connecting !== node.id) {
                            const newConn: WorkflowConnection = {
                              id: `conn_${Date.now()}`,
                              from: connecting,
                              to: node.id,
                            };
                            setConnections(prev => [...prev, newConn]);
                            setConnecting(null); setConnectingMouse(null);
                          }
                        }}
                        onMouseEnter={(e) => {
                          if (connecting) {
                            (e.target as HTMLDivElement).style.transform = "translateY(-50%) scale(1.3)";
                            (e.target as HTMLDivElement).style.background = theme.primary;
                          }
                        }}
                        onMouseLeave={(e) => {
                          (e.target as HTMLDivElement).style.transform = "translateY(-50%) scale(1)";
                          (e.target as HTMLDivElement).style.background = connecting ? theme.primary : theme.surface;
                        }}
                        title="Drop here to connect"
                      />
                    )}

                    <div style={{ ...styles.nodeIcon, background: `${nodeColor}20`, color: nodeColor }}>
                      {icons[node.type]}
                    </div>
                    <span style={styles.nodeLabel}>{node.label}</span>

                    {/* Output port (right side) - not for output nodes */}
                    {node.type !== "output" && (
                      <div
                        style={{
                          position: "absolute",
                          right: -8,
                          top: "50%",
                          transform: "translateY(-50%)",
                          width: 16,
                          height: 16,
                          borderRadius: "50%",
                          background: connecting === node.id ? theme.primary : theme.surface,
                          border: `3px solid ${nodeColor}`,
                          cursor: "crosshair",
                          zIndex: 20,
                          transition: "transform 0.15s",
                        }}
                        onMouseDown={(e) => {
                          e.stopPropagation();
                          e.preventDefault();
                          setConnecting(node.id);
                        }}
                        onMouseEnter={(e) => {
                          if (!connecting) {
                            (e.target as HTMLDivElement).style.transform = "translateY(-50%) scale(1.2)";
                          }
                        }}
                        onMouseLeave={(e) => {
                          (e.target as HTMLDivElement).style.transform = "translateY(-50%) scale(1)";
                        }}
                        title="Drag to connect"
                      />
                    )}
                  </div>
                );
              })}

              {nodes.length === 0 && (
                <div style={styles.canvasEmpty}>
                  <GitBranch size={48} color={theme.textTertiary} />
                  <p>Add nodes from the sidebar to build your workflow</p>
                  <p style={{ fontSize: 12, marginTop: 8 }}>Drag from output port (right) to input port (left) to connect</p>
                </div>
              )}
            </div>
          </>
        )}
      </main>

      {/* MCP Servers Panel */}
      <AnimatePresence>
        {showMcpPanel && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} style={styles.modalOverlay} onClick={() => setShowMcpPanel(false)}>
            <motion.div
              initial={{ opacity: 0, x: 300 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 300 }}
              style={styles.sidePanel}
              onClick={e => e.stopPropagation()}
              onAnimationComplete={() => loadData()}
            >
              <div style={styles.panelHeader}>
                <h2 style={{ fontSize: 16, fontWeight: 600 }}>MCP Servers</h2>
                <div style={{ display: "flex", gap: 4 }}>
                  <button style={styles.iconBtn} onClick={loadData} title="Refresh"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 12a9 9 0 11-9-9c2.52 0 4.93 1 6.74 2.74L21 8"/><path d="M21 3v5h-5"/></svg></button>
                  <button style={styles.iconBtn} onClick={() => setShowMcpPanel(false)}><X size={18} /></button>
                </div>
              </div>

              <div style={styles.panelBody}>
                <div style={styles.sectionLabel}>Registered ({mcpServers.length})</div>
                {mcpServers.length > 0 ? (
                  <div style={{ display: "flex", flexDirection: "column", gap: 8, marginBottom: 16 }}>
                    {mcpServers.map(s => (
                      <div key={s.server_id} style={styles.mcpCard}>
                        <div style={{ ...styles.mcpDot, background: s.connected ? theme.green : theme.textTertiary }} />
                        <div style={{ flex: 1 }}>
                          <div style={{ fontWeight: 500, fontSize: 14 }}>{s.name}</div>
                          <div style={{ fontSize: 11, color: s.connected ? theme.green : theme.textTertiary }}>
                            {s.connected ? `${s.tools.length} tools connected` : "Not connected"}
                          </div>
                        </div>
                        <button
                          style={{ ...styles.smallBtn, background: s.connected ? theme.bgSecondary : theme.primary, color: s.connected ? theme.text : "#fff", opacity: mcpConnecting === s.server_id ? 0.7 : 1 }}
                          disabled={mcpConnecting === s.server_id}
                          onClick={async () => {
                            setMcpConnecting(s.server_id);
                            try {
                              if (s.connected) {
                                await mcpApi.disconnect(s.server_id);
                              } else {
                                await mcpApi.connect(s.server_id);
                              }
                              await loadData();
                            } catch (e: any) {
                              alert(`Failed to ${s.connected ? 'disconnect' : 'connect'}: ${e.message}`);
                            } finally {
                              setMcpConnecting(null);
                            }
                          }}
                        >
                          {mcpConnecting === s.server_id ? "..." : s.connected ? "Disconnect" : "Connect"}
                        </button>
                        <button
                          style={{ ...styles.iconBtn, padding: 6, color: theme.red }}
                          onClick={async () => {
                            if (confirm(`Delete ${s.name}?`)) {
                              try {
                                await fetch(`http://localhost:8080/api/mcp-servers/${s.server_id}`, { method: "DELETE" });
                                loadData();
                              } catch (e) { console.error(e); }
                            }
                          }}
                          title="Delete server"
                        >
                          <Trash2 size={14} />
                        </button>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p style={{ color: theme.textTertiary, fontSize: 13, marginBottom: 16 }}>No servers registered</p>
                )}

                <div style={styles.sectionLabel}>Popular Servers</div>
                <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                  {POPULAR_MCP_SERVERS.map(s => {
                    const isAdded = mcpServers.some(ms => ms.server_id === s.id);
                    const needsConfig = s.envVars || s.args;
                    return (
                      <div key={s.id} style={styles.mcpCard}>
                        <Server size={16} color={theme.primary} />
                        <div style={{ flex: 1 }}>
                          <div style={{ fontWeight: 500, fontSize: 14 }}>{s.name}</div>
                          <div style={{ fontSize: 11, color: theme.textTertiary }}>{s.description}</div>
                          {needsConfig && <div style={{ fontSize: 10, color: theme.yellow, marginTop: 2 }}>Requires configuration</div>}
                        </div>
                        <button
                          style={{ ...styles.smallBtn, background: isAdded ? theme.bgSecondary : theme.primaryLight, color: isAdded ? theme.textTertiary : theme.primary }}
                          onClick={() => !isAdded && startMcpConfig(s)}
                          disabled={isAdded}
                        >
                          {isAdded ? "Added" : needsConfig ? "Configure" : "Add"}
                        </button>
                      </div>
                    );
                  })}
                </div>

                <button style={{ ...styles.createBtn, width: "100%", marginTop: 16 }} onClick={() => setShowCustomMcp(true)}>
                  <Plus size={16} style={{ marginRight: 6 }} />
                  Add Custom Server
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* MCP Configuration Modal */}
      <AnimatePresence>
        {mcpConfiguring && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} style={styles.modalOverlay} onClick={() => setMcpConfiguring(null)}>
            <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0, scale: 0.95 }} style={styles.modal} onClick={e => e.stopPropagation()}>
              <div style={styles.modalHeader}>
                <h2 style={{ fontSize: 18, fontWeight: 600 }}>Configure {mcpConfiguring.name}</h2>
                <button style={styles.iconBtn} onClick={() => setMcpConfiguring(null)}><X size={18} /></button>
              </div>
              <div style={styles.modalBody}>
                <p style={{ fontSize: 13, color: theme.textSecondary, marginBottom: 16 }}>{mcpConfiguring.description}</p>

                {mcpConfiguring.envVars && (
                  <>
                    <div style={{ fontSize: 12, fontWeight: 600, color: theme.textTertiary, marginBottom: 8 }}>ENVIRONMENT VARIABLES</div>
                    {mcpConfiguring.envVars.map(env => (
                      <div key={env.key} style={{ marginBottom: 12 }}>
                        <label style={styles.label}>
                          {env.label} {env.required && <span style={{ color: theme.red }}>*</span>}
                        </label>
                        <input
                          style={styles.textInput}
                          type={env.key.includes("TOKEN") || env.key.includes("KEY") || env.key.includes("SECRET") ? "password" : "text"}
                          placeholder={env.placeholder}
                          value={mcpFormValues[env.key] || ""}
                          onChange={e => setMcpFormValues(prev => ({ ...prev, [env.key]: e.target.value }))}
                        />
                      </div>
                    ))}
                  </>
                )}

                {mcpConfiguring.args && (
                  <>
                    <div style={{ fontSize: 12, fontWeight: 600, color: theme.textTertiary, marginBottom: 8, marginTop: mcpConfiguring.envVars ? 16 : 0 }}>ARGUMENTS</div>
                    {mcpConfiguring.args.map(arg => (
                      <div key={arg.key} style={{ marginBottom: 12 }}>
                        <label style={styles.label}>
                          {arg.label} {arg.required && <span style={{ color: theme.red }}>*</span>}
                        </label>
                        <input
                          style={styles.textInput}
                          placeholder={arg.placeholder}
                          value={mcpFormValues[arg.key] || ""}
                          onChange={e => setMcpFormValues(prev => ({ ...prev, [arg.key]: e.target.value }))}
                        />
                      </div>
                    ))}
                  </>
                )}

                <div style={{ marginTop: 16, padding: 12, background: theme.bgSecondary, borderRadius: 8, fontSize: 12 }}>
                  <div style={{ fontWeight: 600, marginBottom: 4 }}>Command:</div>
                  <code style={{ color: theme.textSecondary, wordBreak: "break-all" as const }}>{mcpConfiguring.command}</code>
                </div>
              </div>
              <div style={styles.modalFooter}>
                <button style={styles.cancelBtn} onClick={() => setMcpConfiguring(null)}>Cancel</button>
                <button style={styles.createBtn} onClick={submitMcpConfig}>Add Server</button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Custom MCP Server Modal */}
      <AnimatePresence>
        {showCustomMcp && (
          <CustomMcpModal onClose={() => setShowCustomMcp(false)} onRefresh={loadData} />
        )}
      </AnimatePresence>

      {/* New Agent Modal */}
      <AnimatePresence>
        {showNewAgent && (
          <NewAgentModal
            models={models}
            mcpServers={mcpServers}
            onClose={() => setShowNewAgent(false)}
            onCreate={agent => { addAgent(agent); setSelectedAgent(agent); setShowNewAgent(false); }}
          />
        )}
      </AnimatePresence>

      {/* Settings Modal */}
      <AnimatePresence>
        {showSettings && (
          <SettingsModal mcpServers={mcpServers} onClose={() => setShowSettings(false)} onRefresh={loadData} />
        )}
      </AnimatePresence>
    </div>
  );
}

// New Agent Modal
function NewAgentModal({ models, mcpServers, onClose, onCreate }: { models: Model[]; mcpServers: MCPServer[]; onClose: () => void; onCreate: (a: Agent) => void }) {
  const [name, setName] = useState("");
  const [model, setModel] = useState("gemini-2.5-flash");
  const [framework, setFramework] = useState<"adk" | "langgraph">("adk");
  const [selectedMcp, setSelectedMcp] = useState<string[]>([]);
  const [systemPrompt, setSystemPrompt] = useState("");
  const [loading, setLoading] = useState(false);

  const create = async () => {
    if (!name.trim()) return;
    setLoading(true);
    try {
      const agent = await agentsApi.create({
        agent_id: name.toLowerCase().replace(/\s+/g, "-"),
        name: name.trim(),
        model_id: model,
        framework,
        agent_type: "llm",
        system_prompt: systemPrompt || "You are a helpful AI assistant.",
        description: "",
        tools: [],
        mcp_servers: selectedMcp,
        subagents: [],
        max_iterations: 10,
        temperature: 0.7,
      });
      onCreate(agent);
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  };

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} style={styles.modalOverlay} onClick={onClose}>
      <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0, scale: 0.95 }} style={styles.modal} onClick={e => e.stopPropagation()}>
        <div style={styles.modalHeader}>
          <h2 style={{ fontSize: 18, fontWeight: 600 }}>Create Agent</h2>
          <button style={styles.iconBtn} onClick={onClose}><X size={18} /></button>
        </div>
        <div style={styles.modalBody}>
          <label style={styles.label}>Name</label>
          <input style={styles.textInput} placeholder="My Assistant" value={name} onChange={e => setName(e.target.value)} />

          <label style={styles.label}>Framework</label>
          <div style={styles.radioGroup}>
            {(["adk", "langgraph"] as const).map(f => (
              <button key={f} style={{ ...styles.radioBtn, ...(framework === f ? styles.radioBtnActive : {}) }} onClick={() => setFramework(f)}>
                {f === "adk" ? "Google ADK" : "LangGraph"}
              </button>
            ))}
          </div>

          <label style={styles.label}>Model</label>
          <select style={styles.select} value={model} onChange={e => setModel(e.target.value)}>
            {models.map(m => <option key={m.model_id} value={m.model_id}>{m.display_name}</option>)}
          </select>

          <label style={styles.label}>System Prompt</label>
          <textarea style={{ ...styles.textInput, minHeight: 60 }} placeholder="You are a helpful AI assistant..." value={systemPrompt} onChange={e => setSystemPrompt(e.target.value)} />

          {mcpServers.length > 0 && (
            <>
              <label style={styles.label}>MCP Servers</label>
              <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
                {mcpServers.map(s => (
                  <button
                    key={s.server_id}
                    style={{ ...styles.chipBtn, ...(selectedMcp.includes(s.server_id) ? styles.chipBtnActive : {}) }}
                    onClick={() => setSelectedMcp(prev => prev.includes(s.server_id) ? prev.filter(x => x !== s.server_id) : [...prev, s.server_id])}
                  >
                    {s.name}
                  </button>
                ))}
              </div>
            </>
          )}
        </div>
        <div style={styles.modalFooter}>
          <button style={styles.cancelBtn} onClick={onClose}>Cancel</button>
          <button style={{ ...styles.createBtn, ...(!name.trim() || loading ? styles.createBtnDisabled : {}) }} onClick={create} disabled={!name.trim() || loading}>
            {loading ? "Creating..." : "Create"}
          </button>
        </div>
      </motion.div>
    </motion.div>
  );
}

// Custom MCP Server Modal
function CustomMcpModal({ onClose, onRefresh }: { onClose: () => void; onRefresh: () => void }) {
  const [newServer, setNewServer] = useState({ server_id: "", name: "", transport: "stdio", command: "", url: "" });
  const [loading, setLoading] = useState(false);

  const addServer = async () => {
    if (!newServer.server_id || !newServer.name) return;
    setLoading(true);
    try {
      await mcpApi.register({
        server_id: newServer.server_id,
        name: newServer.name,
        transport: newServer.transport,
        command: newServer.transport === "stdio" ? newServer.command : undefined,
        url: newServer.transport !== "stdio" ? newServer.url : undefined,
      });
      onRefresh();
      onClose();
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  };

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} style={styles.modalOverlay} onClick={onClose}>
      <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0, scale: 0.95 }} style={styles.modal} onClick={e => e.stopPropagation()}>
        <div style={styles.modalHeader}>
          <h2 style={{ fontSize: 18, fontWeight: 600 }}>Add Custom MCP Server</h2>
          <button style={styles.iconBtn} onClick={onClose}><X size={18} /></button>
        </div>
        <div style={styles.modalBody}>
          <label style={styles.label}>Server ID <span style={{ color: theme.red }}>*</span></label>
          <input style={styles.textInput} placeholder="my-server" value={newServer.server_id} onChange={e => setNewServer(p => ({ ...p, server_id: e.target.value }))} />

          <label style={styles.label}>Display Name <span style={{ color: theme.red }}>*</span></label>
          <input style={styles.textInput} placeholder="My Server" value={newServer.name} onChange={e => setNewServer(p => ({ ...p, name: e.target.value }))} />

          <label style={styles.label}>Transport</label>
          <div style={{ ...styles.radioGroup, marginTop: 4 }}>
            {["stdio", "sse", "http"].map(t => (
              <button key={t} style={{ ...styles.radioBtn, ...(newServer.transport === t ? styles.radioBtnActive : {}) }} onClick={() => setNewServer(p => ({ ...p, transport: t }))}>
                {t.toUpperCase()}
              </button>
            ))}
          </div>

          <label style={styles.label}>{newServer.transport === "stdio" ? "Command" : "URL"} <span style={{ color: theme.red }}>*</span></label>
          <input
            style={styles.textInput}
            placeholder={newServer.transport === "stdio" ? "npx -y @modelcontextprotocol/server-xxx" : "http://localhost:3001/sse"}
            value={newServer.transport === "stdio" ? newServer.command : newServer.url}
            onChange={e => setNewServer(p => newServer.transport === "stdio" ? { ...p, command: e.target.value } : { ...p, url: e.target.value })}
          />

          <div style={{ marginTop: 16, padding: 12, background: theme.bgSecondary, borderRadius: 8, fontSize: 12, color: theme.textSecondary }}>
            <strong>Tip:</strong> For stdio servers, use npx commands like:<br />
            <code>npx -y @modelcontextprotocol/server-github</code>
          </div>
        </div>
        <div style={styles.modalFooter}>
          <button style={styles.cancelBtn} onClick={onClose}>Cancel</button>
          <button
            style={{ ...styles.createBtn, ...(!newServer.server_id || !newServer.name || (!newServer.command && !newServer.url) || loading ? styles.createBtnDisabled : {}) }}
            onClick={addServer}
            disabled={!newServer.server_id || !newServer.name || (!newServer.command && !newServer.url) || loading}
          >
            {loading ? "Adding..." : "Add Server"}
          </button>
        </div>
      </motion.div>
    </motion.div>
  );
}

// Settings Modal
function SettingsModal({ mcpServers, onClose, onRefresh }: { mcpServers: MCPServer[]; onClose: () => void; onRefresh: () => void }) {
  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} style={styles.modalOverlay} onClick={onClose}>
      <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0, scale: 0.95 }} style={{ ...styles.modal, maxWidth: 500 }} onClick={e => e.stopPropagation()}>
        <div style={styles.modalHeader}>
          <h2 style={{ fontSize: 18, fontWeight: 600 }}>Settings</h2>
          <button style={styles.iconBtn} onClick={onClose}><X size={18} /></button>
        </div>
        <div style={{ ...styles.modalBody, maxHeight: 400, overflow: "auto" }}>
          <div style={styles.sectionLabel}>Registered MCP Servers ({mcpServers.length})</div>
          {mcpServers.length > 0 ? (
            <div style={{ display: "flex", flexDirection: "column", gap: 8, marginTop: 8 }}>
              {mcpServers.map(s => (
                <div key={s.server_id} style={{ padding: 12, background: theme.bg, borderRadius: 8, fontSize: 13 }}>
                  <div style={{ fontWeight: 600 }}>{s.name}</div>
                  <div style={{ color: theme.textTertiary, marginTop: 2 }}>ID: {s.server_id} · {s.tools.length} tools</div>
                </div>
              ))}
            </div>
          ) : (
            <p style={{ color: theme.textTertiary, fontSize: 13, marginTop: 8 }}>No MCP servers registered yet.</p>
          )}
        </div>
      </motion.div>
    </motion.div>
  );
}

// Styles
const styles: Record<string, CSSProperties> = {
  app: { display: "flex", height: "100vh", background: theme.bg, color: theme.text, fontFamily: "'Google Sans', 'Roboto', sans-serif" },
  desktopSidebar: { width: 260, minWidth: 260, background: theme.surface, borderRight: `1px solid ${theme.border}`, display: "flex", flexDirection: "column" },
  sidebarHeader: { padding: "16px", borderBottom: `1px solid ${theme.border}` },
  logo: { display: "flex", alignItems: "center", gap: 10 },
  logoIcon: { width: 32, height: 32, borderRadius: 8, background: theme.primary, display: "flex", alignItems: "center", justifyContent: "center" },
  viewTabs: { display: "flex", padding: "12px", gap: 6 },
  viewTab: { flex: 1, display: "flex", alignItems: "center", justifyContent: "center", gap: 6, padding: "10px", border: "none", borderRadius: 8, background: "transparent", cursor: "pointer", fontSize: 13, fontWeight: 500, color: theme.textSecondary },
  viewTabActive: { background: theme.primaryLight, color: theme.primary },
  quickChatBtn: { display: "flex", alignItems: "center", gap: 10, margin: "0 12px", padding: "12px", border: `1px solid ${theme.border}`, borderRadius: 10, background: theme.surface, cursor: "pointer", fontSize: 14, fontWeight: 500, position: "relative" as const },
  quickChatBtnActive: { borderColor: theme.primary, background: theme.primaryLight },
  activeDot: { position: "absolute" as const, right: 12, width: 8, height: 8, borderRadius: "50%", background: theme.primary },
  sectionLabel: { fontSize: 11, fontWeight: 600, color: theme.textTertiary, textTransform: "uppercase" as const, letterSpacing: "0.5px", padding: "16px 16px 8px" },
  newAgentBtn: { display: "flex", alignItems: "center", gap: 8, margin: "0 12px 8px", padding: "10px 14px", border: `1px dashed ${theme.border}`, borderRadius: 8, background: "transparent", cursor: "pointer", fontSize: 13, color: theme.textSecondary },
  agentsList: { flex: 1, overflow: "auto", padding: "0 8px" },
  emptyList: { padding: "20px 12px", textAlign: "center" as const, color: theme.textTertiary, fontSize: 13 },
  agentItem: { display: "flex", alignItems: "center", gap: 10, width: "100%", padding: "10px 12px", border: "none", borderRadius: 8, background: "transparent", cursor: "pointer", fontSize: 14, textAlign: "left" as const, color: theme.textSecondary },
  agentItemActive: { background: theme.primaryLight, color: theme.primary },
  agentName: { flex: 1, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" as const },
  deleteBtn: { opacity: 0, padding: 4, border: "none", background: "transparent", cursor: "pointer", borderRadius: 4, color: theme.textTertiary },
  nodeButtons: { display: "flex", flexDirection: "column", gap: 2, padding: "0 12px" },
  nodeBtn: { display: "flex", alignItems: "center", gap: 8, padding: "8px 12px", border: "none", borderRadius: 6, background: "transparent", cursor: "pointer", fontSize: 13, color: theme.textSecondary },
  nodeConfig: { borderTop: `1px solid ${theme.border}`, marginTop: 8, paddingTop: 8 },
  sidebarFooter: { padding: "8px 12px", borderTop: `1px solid ${theme.border}` },
  footerBtn: { display: "flex", alignItems: "center", gap: 8, width: "100%", padding: "10px 12px", border: "none", borderRadius: 8, background: "transparent", cursor: "pointer", fontSize: 13, color: theme.textSecondary },
  badge: { marginLeft: "auto", background: theme.primary, color: "#fff", fontSize: 11, padding: "2px 6px", borderRadius: 10 },
  main: { flex: 1, display: "flex", flexDirection: "column", minWidth: 0 },
  header: { display: "flex", alignItems: "center", justifyContent: "space-between", padding: "12px 20px", borderBottom: `1px solid ${theme.border}`, background: theme.surface },
  headerCenter: { display: "flex", alignItems: "center", gap: 10 },
  headerTitle: { fontWeight: 600, fontSize: 15 },
  headerBadge: { fontSize: 12, padding: "4px 10px", background: theme.bgSecondary, borderRadius: 6, color: theme.textSecondary },
  modelSelect: { fontSize: 12, padding: "4px 8px", border: `1px solid ${theme.border}`, borderRadius: 6, background: theme.bg },
  iconBtn: { padding: 8, border: "none", background: "transparent", cursor: "pointer", borderRadius: 8, color: theme.textSecondary, display: "flex", alignItems: "center", justifyContent: "center" },
  chat: { flex: 1, overflow: "auto" },
  messages: { maxWidth: 720, margin: "0 auto", padding: "24px 20px" },
  userRow: { display: "flex", justifyContent: "flex-end", marginBottom: 16 },
  aiRow: { display: "flex", justifyContent: "flex-start", marginBottom: 16 },
  userBubble: { maxWidth: "75%", padding: "12px 16px", borderRadius: 18, borderBottomRightRadius: 4, background: theme.userBg, color: theme.userText },
  aiBubble: { maxWidth: "85%", padding: "14px 16px", borderRadius: 18, borderBottomLeftRadius: 4, background: theme.aiBg, position: "relative" as const },
  aiHeader: { display: "flex", alignItems: "center", gap: 6, marginBottom: 6 },
  messageText: { margin: 0, lineHeight: 1.6, whiteSpace: "pre-wrap" as const },
  copyBtn: { position: "absolute" as const, top: 10, right: 10, padding: 4, border: "none", background: "transparent", cursor: "pointer", borderRadius: 4, color: theme.textTertiary, opacity: 0.6 },
  typing: { display: "flex", gap: 4 },
  dot: { width: 8, height: 8, borderRadius: "50%", background: theme.primary },
  inputArea: { padding: "16px 20px 24px", borderTop: `1px solid ${theme.border}`, background: theme.surface },
  inputContainer: { maxWidth: 720, margin: "0 auto", position: "relative" as const },
  input: { width: "100%", padding: "14px 52px 14px 18px", border: `1px solid ${theme.border}`, borderRadius: 24, background: theme.bg, fontSize: 15, resize: "none" as const, outline: "none", fontFamily: "inherit", lineHeight: 1.5 },
  sendBtn: { position: "absolute" as const, right: 6, bottom: 6, width: 38, height: 38, borderRadius: "50%", border: "none", background: theme.primary, color: "#fff", cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "center" },
  sendBtnDisabled: { background: theme.bgTertiary, color: theme.textTertiary, cursor: "not-allowed" },
  welcome: { display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", height: "100%", padding: 40, textAlign: "center" as const },
  welcomeIcon: { width: 64, height: 64, borderRadius: 16, background: theme.primaryLight, display: "flex", alignItems: "center", justifyContent: "center", marginBottom: 20 },
  welcomeTitle: { fontSize: 26, fontWeight: 600, marginBottom: 10 },
  welcomeText: { fontSize: 15, color: theme.textSecondary, maxWidth: 400, lineHeight: 1.6, marginBottom: 24 },
  suggestions: { display: "flex", flexWrap: "wrap" as const, gap: 8, justifyContent: "center" },
  suggestionBtn: { padding: "10px 16px", border: `1px solid ${theme.border}`, borderRadius: 20, background: theme.surface, fontSize: 14, cursor: "pointer", color: theme.textSecondary },
  canvas: { flex: 1, position: "relative" as const, background: `radial-gradient(circle, ${theme.bgSecondary} 1px, transparent 1px)`, backgroundSize: "20px 20px", overflow: "hidden" },
  connectionsSvg: { position: "absolute" as const, top: 0, left: 0, width: "100%", height: "100%", pointerEvents: "none" as const },
  workflowNode: { position: "absolute" as const, display: "flex", alignItems: "center", gap: 8, padding: "10px 14px", background: theme.surface, border: `2px solid ${theme.border}`, borderRadius: 10, cursor: "grab", userSelect: "none" as const, minWidth: 120 },
  nodeIcon: { width: 32, height: 32, borderRadius: 8, display: "flex", alignItems: "center", justifyContent: "center" },
  nodeLabel: { fontSize: 13, fontWeight: 500 },
  connectBtn: { marginLeft: "auto", padding: 6, border: "none", background: theme.bgSecondary, borderRadius: 6, cursor: "pointer", color: theme.textSecondary, display: "flex" },
  canvasEmpty: { position: "absolute" as const, top: "50%", left: "50%", transform: "translate(-50%, -50%)", textAlign: "center" as const, color: theme.textTertiary },
  modalOverlay: { position: "fixed" as const, inset: 0, background: "rgba(0,0,0,0.5)", display: "flex", alignItems: "center", justifyContent: "center", padding: 20, zIndex: 100 },
  modal: { width: "100%", maxWidth: 420, background: theme.surface, borderRadius: 12, boxShadow: theme.shadowLg, overflow: "hidden" },
  modalHeader: { display: "flex", alignItems: "center", justifyContent: "space-between", padding: "16px 20px", borderBottom: `1px solid ${theme.border}` },
  modalBody: { padding: 20 },
  modalFooter: { display: "flex", justifyContent: "flex-end", gap: 10, padding: "14px 20px", borderTop: `1px solid ${theme.border}` },
  label: { display: "block", fontSize: 13, fontWeight: 500, color: theme.textSecondary, marginBottom: 6, marginTop: 14 },
  textInput: { width: "100%", padding: "10px 12px", border: `1px solid ${theme.border}`, borderRadius: 8, fontSize: 14, outline: "none", background: theme.bg },
  radioGroup: { display: "flex", gap: 8 },
  radioBtn: { flex: 1, padding: "10px", border: `1px solid ${theme.border}`, borderRadius: 8, background: theme.bg, fontSize: 13, cursor: "pointer", fontWeight: 500, textAlign: "center" as const },
  radioBtnActive: { borderColor: theme.primary, background: theme.primaryLight, color: theme.primary },
  select: { width: "100%", padding: "10px 12px", border: `1px solid ${theme.border}`, borderRadius: 8, fontSize: 14, outline: "none", background: theme.bg },
  chipBtn: { padding: "6px 12px", border: `1px solid ${theme.border}`, borderRadius: 16, background: theme.bg, fontSize: 12, cursor: "pointer" },
  chipBtnActive: { borderColor: theme.primary, background: theme.primaryLight, color: theme.primary },
  cancelBtn: { padding: "10px 16px", border: "none", background: "transparent", fontSize: 14, fontWeight: 500, cursor: "pointer", color: theme.textSecondary },
  createBtn: { padding: "10px 20px", border: "none", borderRadius: 8, background: theme.primary, color: "#fff", fontSize: 14, fontWeight: 500, cursor: "pointer" },
  createBtnDisabled: { background: theme.bgTertiary, color: theme.textTertiary, cursor: "not-allowed" },
  sidePanel: { position: "fixed" as const, right: 0, top: 0, bottom: 0, width: 360, background: theme.surface, boxShadow: theme.shadowLg, display: "flex", flexDirection: "column" },
  panelHeader: { display: "flex", alignItems: "center", justifyContent: "space-between", padding: "16px 20px", borderBottom: `1px solid ${theme.border}` },
  panelBody: { flex: 1, padding: 16, overflow: "auto" },
  mcpCard: { display: "flex", alignItems: "center", gap: 12, padding: "12px", background: theme.bg, borderRadius: 10, border: `1px solid ${theme.border}` },
  mcpDot: { width: 10, height: 10, borderRadius: "50%" },
  smallBtn: { padding: "6px 12px", border: "none", borderRadius: 6, fontSize: 12, fontWeight: 500, cursor: "pointer" },
};

export default App;
