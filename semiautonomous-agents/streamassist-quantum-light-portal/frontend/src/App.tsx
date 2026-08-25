import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useMsal, useIsAuthenticated } from '@azure/msal-react';
import { loginRequest } from './authConfig';
import {
  Sparkles,
  Search,
  ShieldCheck,
  Zap,
  Activity,
  Layers,
  Database,
  ExternalLink,
  ChevronRight,
  ChevronDown,
  RefreshCw,
  Copy,
  Check,
  FileText,
  Lock,
  UserCheck,
  Send,
  Terminal,
  Cpu,
  Brain,
  HelpCircle,
  Clock,
  ArrowRight,
  Globe,
  Trash2,
  CheckCircle2,
  AlertCircle,
  Radio,
  Play,
  Code2,
  Sliders,
  CheckSquare
} from 'lucide-react';

interface GroundedCitation {
  title: string;
  uri: string;
  document: string;
  domain: string;
  mimeType: string;
  pageIdentifier?: string;
  snippet?: string;
}

interface GroundingSegment {
  startIndex?: string | number;
  endIndex: string | number;
  referenceIndices: number[];
  text: string;
}

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  text: string;
  thought?: string;
  citations?: GroundedCitation[];
  segments?: GroundingSegment[];
  suggestions?: string[];
  session?: string;
  assistToken?: string;
  ttftMs?: number;
  totalDurationMs?: number;
  chunksCount?: number;
  rawChunks?: any[];
  timestamp: string;
}

interface StreamEventLog {
  id: number;
  timestamp: string;
  deltaMs: number;
  type: 'init' | 'text' | 'thought' | 'suggestions' | 'citation' | 'segments' | 'state' | 'session' | 'assist_token' | 'metrics' | 'raw_chunk' | 'done' | 'error';
  label: string;
  assistToken?: string;
  state?: string;
  data: any;
  expanded?: boolean;
}

interface BackendConfig {
  PROJECT_NUMBER: string;
  PROJECT_ID: string;
  LOCATION: string;
  ENGINE_ID: string;
  CONNECTOR_ID: string;
  WIF_POOL_ID: string;
  WIF_PROVIDER_ID: string;
  CONNECTOR_CLIENT_ID: string;
  TENANT_ID: string;
  SHAREPOINT_DOMAIN: string;
  BACKEND_PORT: number;
  STREAMASSIST_URL: string;
  DATA_STORES: string[];
  SP_SCOPES: string;
}

export default function App() {
  const { instance, accounts } = useMsal();
  const isAuthenticated = useIsAuthenticated();
  const username = accounts[0]?.username || '';

  // Tab Navigation
  const [activeTab, setActiveTab] = useState<'chat' | 'security' | 'telemetry'>('chat');

  // Backend Config
  const [config, setConfig] = useState<BackendConfig | null>(null);
  const [discoveredStores, setDiscoveredStores] = useState<string[]>([]);
  const [discoveryLoading, setDiscoveryLoading] = useState(false);

  // Chat State
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputQuery, setInputQuery] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const [currentSessionToken, setCurrentSessionToken] = useState<string | null>(null);
  const [selectedRawChunkMessage, setSelectedRawChunkMessage] = useState<ChatMessage | null>(null);
  const [highlightSegments, setHighlightSegments] = useState<Record<string, boolean>>({});
  const [expandedThoughts, setExpandedThoughts] = useState<Record<string, boolean>>({});

  // Telemetry Lab State
  const [telemetryQuery, setTelemetryQuery] = useState('Who is the Chief Financial Officer (CFO) and what is their employee ID?');
  const [telemetryStreaming, setTelemetryStreaming] = useState(false);
  const [liveStreamEvents, setLiveStreamEvents] = useState<StreamEventLog[]>([]);
  const [telemetryRawChunks, setTelemetryRawChunks] = useState<any[]>([]);
  const [telemetryStats, setTelemetryStats] = useState<{ ttftMs?: number; totalMs?: number; chunksCount?: number; citationsCount?: number } | null>(null);
  const [expandedEventIds, setExpandedEventIds] = useState<Record<number, boolean>>({});

  // WIF & Security Studio State
  const [entraToken, setEntraToken] = useState<string>('');
  const [gcpToken, setGcpToken] = useState<string>('');
  const [stsTrace, setStsTrace] = useState<any[]>([]);
  const [spAuthUrl, setSpAuthUrl] = useState<string>('');
  const [spNonce, setSpNonce] = useState<string>('');
  const [spConnected, setSpConnected] = useState<boolean | null>(null);
  const [spCheckLoading, setSpCheckLoading] = useState(false);
  const [copiedKey, setCopiedKey] = useState<string | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const telemetryEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Load config on mount
  useEffect(() => {
    fetch('/api/config')
      .then(res => res.json())
      .then(data => setConfig(data))
      .catch(err => console.error("Error loading config:", err));

    setDiscoveryLoading(true);
    fetch('/api/discovery/widget-config')
      .then(res => res.json())
      .then(data => {
        if (data.discovered_datastores && data.discovered_datastores.length > 0) {
          setDiscoveredStores(data.discovered_datastores);
        } else if (data.fallback_datastores) {
          setDiscoveredStores(data.fallback_datastores);
        }
      })
      .catch(() => {})
      .finally(() => setDiscoveryLoading(false));
  }, []);

  // Auto-scroll chat
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isStreaming]);

  // Copy helper
  const handleCopy = (text: string, key: string) => {
    navigator.clipboard.writeText(text);
    setCopiedKey(key);
    setTimeout(() => setCopiedKey(null), 2000);
  };

  // MSAL Login
  const handleMsalLogin = async () => {
    try {
      const resp = await instance.loginPopup(loginRequest);
      const token = resp.idToken;
      setEntraToken(token);
      await executeStsExchange(token);
    } catch (e) {
      console.error("MSAL Login error:", e);
    }
  };

  // STS Exchange
  const executeStsExchange = async (tokenToUse: string) => {
    try {
      const res = await fetch('/api/auth/exchange-wif', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ entra_jwt: tokenToUse }),
      });
      const data = await res.json();
      if (data.trace && data.trace.length > 0) {
        setStsTrace(data.trace);
        if (data.trace[0]?.output?.access_token) {
          setGcpToken(data.trace[0].output.access_token);
        }
      }
    } catch (e) {
      console.error("STS Exchange failed:", e);
    }
  };

  // SharePoint Auth URL Generator
  const generateSpAuthUrl = async () => {
    try {
      const res = await fetch('/api/sharepoint/auth-url', {
        headers: entraToken ? { 'X-Entra-Id-Token': entraToken } : {},
      });
      const data = await res.json();
      setSpAuthUrl(data.auth_url);
      setSpNonce(data.nonce);
    } catch (e) {
      console.error("Failed to generate SP Auth URL:", e);
    }
  };

  // Check SharePoint Connection
  const checkSpConnection = async () => {
    setSpCheckLoading(true);
    try {
      const res = await fetch('/api/sharepoint/check-connection', {
        headers: entraToken ? { 'X-Entra-Id-Token': entraToken } : {},
      });
      const data = await res.json();
      setSpConnected(data.connected);
    } catch (e) {
      setSpConnected(false);
    } finally {
      setSpCheckLoading(false);
    }
  };

  // Run Dedicated Live Telemetry Trace Query
  const runLiveTelemetryTrace = async (queryText: string) => {
    if (!queryText.trim() || telemetryStreaming) return;

    setTelemetryStreaming(true);
    setLiveStreamEvents([]);
    setTelemetryRawChunks([]);
    setTelemetryStats(null);
    setExpandedEventIds({});

    const startTime = Date.now();
    let eventCounter = 0;
    let rawChunksAccumulator: any[] = [];
    let currentAssistToken = '';
    let currentState = 'IN_PROGRESS';

    const addEventLog = (type: StreamEventLog['type'], label: string, data: any) => {
      eventCounter += 1;
      const newEvent: StreamEventLog = {
        id: eventCounter,
        timestamp: new Date().toISOString().substring(11, 23),
        deltaMs: Date.now() - startTime,
        type,
        label,
        assistToken: currentAssistToken,
        state: currentState,
        data,
      };
      setLiveStreamEvents(prev => [...prev, newEvent]);
    };

    try {
      addEventLog('init', 'HTTP Stream Connection Established', {
        endpoint: config?.STREAMASSIST_URL || '...:streamAssist',
        query: queryText,
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-Goog-User-Project': config?.PROJECT_NUMBER }
      });

      const response = await fetch('/api/stream-assist', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(entraToken ? { 'X-Entra-Id-Token': entraToken } : {}),
        },
        body: JSON.stringify({
          query: queryText,
          auth_mode: 'auto',
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP Error ${response.status}: ${response.statusText}`);
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder('utf-8');
      let buffer = '';

      if (reader) {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n');
          buffer = lines.pop() || '';

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const jsonStr = line.replace('data: ', '').trim();
              if (!jsonStr) continue;

              try {
                const event = JSON.parse(jsonStr);

                if (event.type === 'assist_token') {
                  currentAssistToken = event.token;
                  addEventLog('assist_token', `Assist Token Assigned`, { assistToken: event.token });
                } else if (event.type === 'state') {
                  currentState = event.state;
                  addEventLog('state', `State Transition ➔ ${event.state}`, { state: event.state });
                } else if (event.type === 'session') {
                  addEventLog('session', `Session Path Initialized`, { session: event.session, queryId: event.queryId });
                } else if (event.type === 'thought') {
                  addEventLog('thought', `🧠 ReAct Reasoning Thought`, { thought: event.delta });
                } else if (event.type === 'text') {
                  addEventLog('text', `📝 Natural Language Text Delta`, { delta: event.delta });
                } else if (event.type === 'suggestions') {
                  addEventLog('suggestions', `💡 Decoded Recommendation Chips`, { questions: event.questions });
                } else if (event.type === 'citation') {
                  addEventLog('citation', `📑 Grounded SharePoint Source`, event.citation);
                } else if (event.type === 'segments') {
                  addEventLog('segments', `🎯 Citation Text Segments`, { segments: event.segments });
                } else if (event.type === 'raw_chunk') {
                  rawChunksAccumulator.push(event.chunk);
                  setTelemetryRawChunks([...rawChunksAccumulator]);
                  addEventLog('raw_chunk', `📦 Stream Event Chunk [${rawChunksAccumulator.length}]`, event.chunk);
                } else if (event.type === 'ttft') {
                  setTelemetryStats(prev => ({ ...prev, ttftMs: event.duration_ms }));
                } else if (event.type === 'metrics') {
                  setTelemetryStats(prev => ({
                    ...prev,
                    totalMs: event.total_duration_ms,
                    chunksCount: event.chunks_count,
                    citationsCount: event.citations_count,
                  }));
                  addEventLog('metrics', `⚡ Telemetry Metrics Completed`, event);
                } else if (event.type === 'done') {
                  addEventLog('done', `🏁 Stream Completed (SUCCEEDED)`, { status: 'SUCCEEDED', total_ms: Date.now() - startTime });
                }
              } catch (parseErr) {
                console.error("SSE parse error in telemetry:", parseErr);
              }
            }
          }
        }
      }
    } catch (err: any) {
      addEventLog('error', `⚠️ Streaming Error`, { error: err.message });
    } finally {
      setTelemetryStreaming(false);
    }
  };

  // Send Chat Message via SSE StreamAssist
  const handleSendMessage = useCallback(async (queryText: string) => {
    if (!queryText.trim() || isStreaming) return;

    const userMessageId = `user-${Date.now()}`;
    const assistantMessageId = `asst-${Date.now()}`;
    const timestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    const userMsg: ChatMessage = {
      id: userMessageId,
      role: 'user',
      text: queryText,
      timestamp,
    };

    const initialAssistantMsg: ChatMessage = {
      id: assistantMessageId,
      role: 'assistant',
      text: '',
      thought: '',
      citations: [],
      segments: [],
      suggestions: [],
      rawChunks: [],
      timestamp,
    };

    setMessages(prev => [...prev, userMsg, initialAssistantMsg]);
    setInputQuery('');
    setIsStreaming(true);

    try {
      const response = await fetch('/api/stream-assist', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(entraToken ? { 'X-Entra-Id-Token': entraToken } : {}),
        },
        body: JSON.stringify({
          query: queryText,
          session_token: currentSessionToken,
          entra_token: entraToken || undefined,
          auth_mode: 'auto',
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP Error ${response.status}: ${response.statusText}`);
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder('utf-8');
      let buffer = '';

      if (reader) {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n');
          buffer = lines.pop() || '';

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const jsonStr = line.replace('data: ', '').trim();
              if (!jsonStr) continue;

              try {
                const event = JSON.parse(jsonStr);

                setMessages(prev =>
                  prev.map(msg => {
                    if (msg.id !== assistantMessageId) return msg;

                    const updated = { ...msg };

                    if (event.type === 'raw_chunk') {
                      updated.rawChunks = [...(updated.rawChunks || []), event.chunk];
                    } else if (event.type === 'thought') {
                      updated.thought = (updated.thought || '') + event.delta;
                    } else if (event.type === 'text') {
                      updated.text = (updated.text || '') + event.delta;
                    } else if (event.type === 'citation') {
                      const exists = updated.citations?.some(c => c.uri === event.citation.uri);
                      if (!exists) {
                        updated.citations = [...(updated.citations || []), event.citation];
                      }
                    } else if (event.type === 'segments') {
                      updated.segments = event.segments;
                    } else if (event.type === 'suggestions') {
                      updated.suggestions = event.questions;
                    } else if (event.type === 'session') {
                      updated.session = event.session;
                      setCurrentSessionToken(event.session);
                    } else if (event.type === 'assist_token') {
                      updated.assistToken = event.token;
                    } else if (event.type === 'ttft') {
                      updated.ttftMs = event.duration_ms;
                    } else if (event.type === 'metrics') {
                      updated.totalDurationMs = event.total_duration_ms;
                      updated.chunksCount = event.chunks_count;
                    }

                    return updated;
                  })
                );
              } catch (parseErr) {
                console.error("SSE parse error:", parseErr);
              }
            }
          }
        }
      }
    } catch (err: any) {
      setMessages(prev =>
        prev.map(msg => {
          if (msg.id === assistantMessageId) {
            return {
              ...msg,
              text: `⚠️ Stream error: ${err.message || 'Failed to connect to StreamAssist API'}`,
            };
          }
          return msg;
        })
      );
    } finally {
      setIsStreaming(false);
    }
  }, [entraToken, currentSessionToken, isStreaming]);

  // Suggested Prompts
  const suggestedPrompts = [
    {
      title: "Executive Employee Directory",
      query: "Who is the Chief Financial Officer (CFO) and what is their employee ID?",
      badge: "HR Records"
    },
    {
      title: "Project Starlight Due Diligence",
      query: "What due diligence reports and findings do we have on Project Starlight and NovaTech?",
      badge: "M&A Vault"
    },
    {
      title: "Restricted Compensation Vault",
      query: "List the executive employee compensation, titles, and start dates in the confidential records.",
      badge: "Confidential"
    },
    {
      title: "Corporate Structure & Reports",
      query: "Who does the CFO report to and what departments are represented in the employee files?",
      badge: "Org Tree"
    }
  ];

  return (
    <div className="min-h-screen flex flex-col font-sans selection:bg-sky-100 selection:text-sky-900">
      
      {/* ── TOP QUANTUM HEADER ─────────────────────────────────────────────────── */}
      <header className="sticky top-0 z-50 glass-panel border-b border-slate-200/80 px-6 py-3.5 flex items-center justify-between">
        <div className="flex items-center gap-3.5">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-sky-500 via-sky-600 to-indigo-600 flex items-center justify-center shadow-md shadow-sky-500/20 text-white font-bold">
            <Cpu className="w-5 h-5 animate-pulse-subtle" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="font-extrabold text-slate-900 tracking-tight text-base sm:text-lg flex items-center gap-1.5">
                STREAMASSIST <span className="bg-gradient-to-r from-sky-600 to-indigo-600 bg-clip-text text-transparent">QUANTUM STUDIO</span>
              </h1>
              <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
                LIVE SSE
              </span>
            </div>
            <p className="text-xs text-slate-500 flex items-center gap-2">
              <span>Google Gemini Enterprise</span>
              <span className="text-slate-300">•</span>
              <span className="flex items-center gap-1 text-slate-600 font-medium">
                <Globe className="w-3 h-3 text-sky-500" />
                {config?.SHAREPOINT_DOMAIN || 'sockcop.sharepoint.com'}
              </span>
            </p>
          </div>
        </div>

        {/* Tab Navigation Pill */}
        <div className="flex items-center bg-slate-100/80 p-1 rounded-xl border border-slate-200/70 text-xs font-semibold">
          <button
            onClick={() => setActiveTab('chat')}
            className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg transition-all ${
              activeTab === 'chat'
                ? 'bg-white text-sky-700 shadow-sm font-bold border border-slate-200/60'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <Sparkles className="w-3.5 h-3.5 text-sky-500" />
            Grounding Chat
          </button>

          <button
            onClick={() => setActiveTab('security')}
            className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg transition-all ${
              activeTab === 'security'
                ? 'bg-white text-sky-700 shadow-sm font-bold border border-slate-200/60'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <ShieldCheck className="w-3.5 h-3.5 text-indigo-500" />
            Security & WIF Auth
          </button>

          <button
            onClick={() => setActiveTab('telemetry')}
            className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg transition-all ${
              activeTab === 'telemetry'
                ? 'bg-white text-sky-700 shadow-sm font-bold border border-slate-200/60'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <Activity className="w-3.5 h-3.5 text-emerald-500" />
            Stream Async Telemetry
          </button>
        </div>

        {/* User / Auth Badge */}
        <div className="flex items-center gap-2.5">
          {isAuthenticated ? (
            <div className="flex items-center gap-2 bg-sky-50 border border-sky-200 px-3 py-1.5 rounded-xl">
              <UserCheck className="w-4 h-4 text-sky-600" />
              <div className="text-left">
                <p className="text-[11px] font-bold text-sky-900 leading-none">{username || 'Entra ID User'}</p>
                <p className="text-[10px] text-sky-600">WIF Federated</p>
              </div>
            </div>
          ) : (
            <button
              onClick={handleMsalLogin}
              className="flex items-center gap-1.5 bg-gradient-to-r from-sky-600 to-indigo-600 text-white px-3.5 py-1.5 rounded-xl text-xs font-semibold shadow-md shadow-sky-500/20 hover:opacity-95 transition-opacity"
            >
              <Lock className="w-3.5 h-3.5" />
              Sign In (Entra ID)
            </button>
          )}
        </div>
      </header>

      {/* ── MAIN CONTENT ROUTER ────────────────────────────────────────────────── */}
      <main className="flex-1 flex flex-col max-w-7xl w-full mx-auto p-4 sm:p-6 gap-6">

        {/* ── TAB 1: QUANTUM GROUNDING CHAT ────────────────────────────────────── */}
        {activeTab === 'chat' && (
          <div className="flex-1 flex flex-col gap-4">
            
            {/* Top Info Banner */}
            <div className="glass-panel p-4 rounded-2xl flex flex-wrap items-center justify-between gap-3 text-xs">
              <div className="flex items-center gap-3">
                <div className="flex items-center gap-1.5 text-slate-700 font-medium">
                  <Database className="w-4 h-4 text-sky-500" />
                  <span>Connector:</span>
                  <span className="font-mono font-bold bg-slate-100 px-2 py-0.5 rounded text-slate-800">
                    {config?.CONNECTOR_ID || 'sharepoint-data-def-connector'}
                  </span>
                </div>

                <div className="hidden sm:flex items-center gap-1 text-slate-500">
                  <span>Stores:</span>
                  <span className="font-semibold text-slate-700">
                    {discoveryLoading ? 'Discovering...' : `${discoveredStores.length || 5} active entities (file, page, comment, event, attachment)`}
                  </span>
                </div>
              </div>

              <div className="flex items-center gap-2">
                {currentSessionToken && (
                  <button
                    onClick={() => {
                      setCurrentSessionToken(null);
                      setMessages([]);
                    }}
                    className="flex items-center gap-1 px-2.5 py-1 text-slate-600 hover:text-red-600 bg-slate-100 hover:bg-red-50 rounded-lg transition-colors"
                  >
                    <Trash2 className="w-3 h-3" />
                    Reset Session
                  </button>
                )}

                <span className="inline-flex items-center gap-1 text-[11px] font-mono text-slate-500 bg-slate-100 px-2.5 py-1 rounded-lg">
                  <Clock className="w-3 h-3 text-slate-400" />
                  {currentSessionToken ? `Session: ...${currentSessionToken.split('/').pop()?.slice(-8)}` : 'Fresh Session'}
                </span>
              </div>
            </div>

            {/* Chat Conversation Scroll Area */}
            <div className="flex-1 overflow-y-auto space-y-4 min-h-[480px] max-h-[calc(100vh-280px)] pr-1">
              
              {/* Welcome Screen when empty */}
              {messages.length === 0 && (
                <div className="py-12 px-6 flex flex-col items-center justify-center text-center max-w-2xl mx-auto space-y-6">
                  <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-sky-400 via-sky-500 to-indigo-600 flex items-center justify-center shadow-xl shadow-sky-500/20 text-white">
                    <Sparkles className="w-8 h-8 animate-pulse-subtle" />
                  </div>
                  <div>
                    <h2 className="text-2xl font-bold text-slate-900 tracking-tight">
                      Enterprise Grounded Assistant
                    </h2>
                    <p className="text-sm text-slate-500 mt-1 max-w-md mx-auto">
                      Real-time streaming answers grounded in Microsoft SharePoint Online with Google Gemini Enterprise & ReAct Reasoning.
                    </p>
                  </div>

                  {/* Suggested Query Cards */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full text-left">
                    {suggestedPrompts.map((p, idx) => (
                      <button
                        key={idx}
                        onClick={() => handleSendMessage(p.query)}
                        className="glass-panel p-4 rounded-xl glass-card-hover text-left flex flex-col justify-between group border border-slate-200"
                      >
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-[10px] font-bold uppercase tracking-wider text-sky-600 bg-sky-50 px-2 py-0.5 rounded-full border border-sky-100">
                            {p.badge}
                          </span>
                          <ArrowRight className="w-3.5 h-3.5 text-slate-400 group-hover:text-sky-600 group-hover:translate-x-0.5 transition-all" />
                        </div>
                        <h4 className="text-xs font-bold text-slate-800 group-hover:text-sky-700 transition-colors">
                          {p.title}
                        </h4>
                        <p className="text-[11px] text-slate-500 mt-1 line-clamp-2">
                          {p.query}
                        </p>
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* Message Feed */}
              {messages.map(msg => (
                <div
                  key={msg.id}
                  className={`flex flex-col ${
                    msg.role === 'user' ? 'items-end' : 'items-start'
                  } space-y-2`}
                >
                  {/* User Message */}
                  {msg.role === 'user' ? (
                    <div className="max-w-2xl bg-gradient-to-r from-sky-600 to-indigo-600 text-white p-4 rounded-2xl rounded-tr-sm shadow-md shadow-sky-600/10">
                      <p className="text-sm font-medium leading-relaxed">{msg.text}</p>
                      <span className="text-[10px] opacity-75 mt-1 block text-right font-mono">{msg.timestamp}</span>
                    </div>
                  ) : (
                    /* Assistant Message Card */
                    <div className="max-w-3xl w-full glass-panel p-5 rounded-2xl rounded-tl-sm border border-slate-200 shadow-sm space-y-4">
                      
                      {/* Message Header */}
                      <div className="flex items-center justify-between border-b border-slate-100 pb-2.5">
                        <div className="flex items-center gap-2">
                          <div className="w-6 h-6 rounded-lg bg-sky-100 text-sky-700 flex items-center justify-center font-bold text-xs">
                            <Brain className="w-3.5 h-3.5" />
                          </div>
                          <span className="text-xs font-bold text-slate-800">Gemini Grounded Assistant</span>
                        </div>

                        {/* Telemetry Pills */}
                        <div className="flex items-center gap-2 text-[10px] font-mono text-slate-500">
                          {msg.ttftMs && (
                            <span className="bg-sky-50 text-sky-700 px-2 py-0.5 rounded-full border border-sky-100 font-semibold flex items-center gap-1">
                              <Zap className="w-3 h-3 text-amber-500" />
                              TTFT: {msg.ttftMs}ms
                            </span>
                          )}
                          {msg.totalDurationMs && (
                            <span className="bg-slate-100 text-slate-700 px-2 py-0.5 rounded-full">
                              Total: {msg.totalDurationMs}ms
                            </span>
                          )}
                          {msg.rawChunks && msg.rawChunks.length > 0 && (
                            <button
                              onClick={() => setSelectedRawChunkMessage(msg)}
                              className="bg-indigo-50 text-indigo-700 hover:bg-indigo-100 px-2 py-0.5 rounded-full border border-indigo-100 font-semibold flex items-center gap-1 transition-colors"
                            >
                              <Terminal className="w-3 h-3" />
                              {msg.rawChunks.length} Chunks
                            </button>
                          )}
                        </div>
                      </div>

                      {/* ReAct Reasoning Process Box */}
                      {msg.thought && (
                        <div className="bg-amber-50/70 border border-amber-200/80 rounded-xl p-3 text-xs space-y-2">
                          <button
                            onClick={() =>
                              setExpandedThoughts(prev => ({
                                ...prev,
                                [msg.id]: !prev[msg.id],
                              }))
                            }
                            className="flex items-center justify-between w-full font-bold text-amber-900 hover:text-amber-950 text-left"
                          >
                            <span className="flex items-center gap-1.5">
                              <Brain className="w-4 h-4 text-amber-600 animate-pulse-subtle" />
                              ReAct Grounding Reasoning Cycle
                            </span>
                            {expandedThoughts[msg.id] ? (
                              <ChevronDown className="w-4 h-4 text-amber-700" />
                            ) : (
                              <ChevronRight className="w-4 h-4 text-amber-700" />
                            )}
                          </button>

                          {expandedThoughts[msg.id] && (
                            <div className="pt-2 border-t border-amber-200/60 font-mono text-[11px] text-amber-900 leading-relaxed whitespace-pre-wrap bg-amber-100/40 p-2.5 rounded-lg">
                              {msg.thought}
                            </div>
                          )}
                        </div>
                      )}

                      {/* Main Rendered Text */}
                      <div className="text-sm text-slate-800 leading-relaxed whitespace-pre-line font-normal">
                        {msg.text || (
                          <span className="flex items-center gap-2 text-slate-400 italic">
                            <RefreshCw className="w-3.5 h-3.5 animate-spin text-sky-500" />
                            Synthesizing grounded response from SharePoint...
                          </span>
                        )}
                      </div>

                      {/* Grounded Source References Cards */}
                      {msg.citations && msg.citations.length > 0 && (
                        <div className="pt-3 border-t border-slate-100 space-y-2">
                          <div className="flex items-center justify-between">
                            <span className="text-[11px] font-bold text-slate-600 uppercase tracking-wider flex items-center gap-1.5">
                              <FileText className="w-3.5 h-3.5 text-sky-600" />
                              Grounded SharePoint Sources ({msg.citations.length})
                            </span>

                            {msg.segments && msg.segments.length > 0 && (
                              <button
                                onClick={() =>
                                  setHighlightSegments(prev => ({
                                    ...prev,
                                    [msg.id]: !prev[msg.id],
                                  }))
                                }
                                className={`text-[10px] font-semibold px-2 py-0.5 rounded-full border transition-all ${
                                  highlightSegments[msg.id]
                                    ? 'bg-sky-600 text-white border-sky-600'
                                    : 'bg-slate-100 text-slate-600 border-slate-200 hover:bg-slate-200'
                                }`}
                              >
                                {highlightSegments[msg.id] ? '✓ Segments Active' : 'Highlight Segments'}
                              </button>
                            )}
                          </div>

                          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                            {msg.citations.map((c, cIdx) => (
                              <a
                                key={cIdx}
                                href={c.uri}
                                target="_blank"
                                rel="noreferrer"
                                className="glass-panel p-2.5 rounded-xl border border-slate-200 hover:border-sky-300 hover:bg-sky-50/50 transition-all flex flex-col justify-between group"
                              >
                                <div className="flex items-start justify-between gap-1.5">
                                  <div className="flex items-center gap-1.5">
                                    <span className="w-5 h-5 rounded-md bg-sky-100 text-sky-700 font-bold text-[10px] flex items-center justify-center">
                                      [{cIdx + 1}]
                                    </span>
                                    <span className="text-xs font-bold text-slate-800 group-hover:text-sky-700 truncate max-w-[200px]">
                                      {c.title}
                                    </span>
                                  </div>
                                  <ExternalLink className="w-3 h-3 text-slate-400 group-hover:text-sky-600 flex-shrink-0" />
                                </div>
                                <p className="text-[10px] text-slate-500 font-mono mt-1 truncate">
                                  {c.domain}
                                </p>
                              </a>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Smart Recommended Follow-Up Chips */}
                      {msg.suggestions && msg.suggestions.length > 0 && (
                        <div className="pt-2 border-t border-slate-100 space-y-1.5">
                          <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider flex items-center gap-1">
                            <HelpCircle className="w-3 h-3 text-indigo-500" />
                            Suggested Follow-Up Queries
                          </span>
                          <div className="flex flex-wrap gap-1.5">
                            {msg.suggestions.map((sug, sIdx) => (
                              <button
                                key={sIdx}
                                onClick={() => handleSendMessage(sug)}
                                className="text-xs bg-slate-100 hover:bg-sky-50 text-slate-700 hover:text-sky-800 border border-slate-200 hover:border-sky-300 px-3 py-1.5 rounded-full transition-all text-left flex items-center gap-1.5"
                              >
                                <span>{sug}</span>
                                <ChevronRight className="w-3 h-3 opacity-60" />
                              </button>
                            ))}
                          </div>
                        </div>
                      )}

                    </div>
                  )}
                </div>
              ))}

              <div ref={messagesEndRef} />
            </div>

            {/* Input Bar */}
            <div className="glass-panel p-3 rounded-2xl border border-slate-200/80 shadow-md">
              <form
                onSubmit={e => {
                  e.preventDefault();
                  handleSendMessage(inputQuery);
                }}
                className="flex items-center gap-2"
              >
                <textarea
                  ref={textareaRef}
                  value={inputQuery}
                  onChange={e => setInputQuery(e.target.value)}
                  onKeyDown={e => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault();
                      handleSendMessage(inputQuery);
                    }
                  }}
                  placeholder="Ask a question about SharePoint files, employees, due diligence..."
                  disabled={isStreaming}
                  rows={1}
                  className="flex-1 bg-transparent px-3 py-2 text-sm text-slate-800 placeholder-slate-400 focus:outline-none resize-none"
                />

                <button
                  type="submit"
                  disabled={!inputQuery.trim() || isStreaming}
                  className={`p-2.5 rounded-xl font-semibold flex items-center justify-center transition-all ${
                    !inputQuery.trim() || isStreaming
                      ? 'bg-slate-100 text-slate-400 cursor-not-allowed'
                      : 'bg-gradient-to-r from-sky-600 to-indigo-600 text-white shadow-md shadow-sky-500/20 hover:opacity-95'
                  }`}
                >
                  {isStreaming ? (
                    <RefreshCw className="w-4 h-4 animate-spin" />
                  ) : (
                    <Send className="w-4 h-4" />
                  )}
                </button>
              </form>
            </div>
          </div>
        )}

        {/* ── TAB 2: SECURITY & WIF AUTH STUDIO ────────────────────────────────── */}
        {activeTab === 'security' && (
          <div className="space-y-6">
            
            {/* Header Description */}
            <div className="glass-panel p-6 rounded-2xl border border-slate-200 space-y-2">
              <div className="flex items-center gap-2 text-indigo-600">
                <ShieldCheck className="w-6 h-6" />
                <h2 className="text-lg font-bold text-slate-900">Workforce Identity Federation & OAuth Security Studio</h2>
              </div>
              <p className="text-xs text-slate-600 leading-relaxed max-w-3xl">
                Gemini Enterprise uses Workload/Workforce Identity Federation (WIF) so that Microsoft Entra ID identities access Google Cloud APIs with zero hardcoded service account keys. Per-user SharePoint access tokens are secured under the user's WIF identity in Discovery Engine.
              </p>
            </div>

            {/* 5-Step Visual Workflow */}
            <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
              
              {/* Step 1 */}
              <div className={`glass-panel p-4 rounded-xl border flex flex-col justify-between ${isAuthenticated ? 'border-emerald-300 bg-emerald-50/30' : 'border-slate-200'}`}>
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-[10px] font-bold uppercase text-slate-500">Step 1</span>
                    {isAuthenticated ? <CheckCircle2 className="w-4 h-4 text-emerald-600" /> : <Lock className="w-4 h-4 text-slate-400" />}
                  </div>
                  <h4 className="text-xs font-bold text-slate-800">Entra ID Sign-In</h4>
                  <p className="text-[11px] text-slate-500 mt-1">MSAL.js popup authentication yielding Entra JWT.</p>
                </div>
                <button
                  onClick={handleMsalLogin}
                  className="mt-3 w-full text-xs font-semibold py-1.5 px-2.5 rounded-lg bg-sky-600 hover:bg-sky-700 text-white transition-colors"
                >
                  {isAuthenticated ? 'Re-Authenticate' : 'Login with Entra'}
                </button>
              </div>

              {/* Step 2 */}
              <div className={`glass-panel p-4 rounded-xl border flex flex-col justify-between ${gcpToken ? 'border-emerald-300 bg-emerald-50/30' : 'border-slate-200'}`}>
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-[10px] font-bold uppercase text-slate-500">Step 2</span>
                    {gcpToken ? <CheckCircle2 className="w-4 h-4 text-emerald-600" /> : <Cpu className="w-4 h-4 text-slate-400" />}
                  </div>
                  <h4 className="text-xs font-bold text-slate-800">Google STS Exchange</h4>
                  <p className="text-[11px] text-slate-500 mt-1">Exchange Entra JWT for GCP access_token via WIF pool.</p>
                </div>
                <button
                  onClick={() => executeStsExchange(entraToken)}
                  disabled={!entraToken}
                  className="mt-3 w-full text-xs font-semibold py-1.5 px-2.5 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white disabled:bg-slate-200 disabled:text-slate-400 transition-colors"
                >
                  Execute STS Exchange
                </button>
              </div>

              {/* Step 3 */}
              <div className={`glass-panel p-4 rounded-xl border flex flex-col justify-between ${spAuthUrl ? 'border-emerald-300 bg-emerald-50/30' : 'border-slate-200'}`}>
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-[10px] font-bold uppercase text-slate-500">Step 3</span>
                    {spAuthUrl ? <CheckCircle2 className="w-4 h-4 text-emerald-600" /> : <Globe className="w-4 h-4 text-slate-400" />}
                  </div>
                  <h4 className="text-xs font-bold text-slate-800">SharePoint Consent</h4>
                  <p className="text-[11px] text-slate-500 mt-1">Generate Microsoft OAuth consent URL with nonce.</p>
                </div>
                <button
                  onClick={generateSpAuthUrl}
                  className="mt-3 w-full text-xs font-semibold py-1.5 px-2.5 rounded-lg bg-sky-600 hover:bg-sky-700 text-white transition-colors"
                >
                  Generate URL
                </button>
              </div>

              {/* Step 4 */}
              <div className={`glass-panel p-4 rounded-xl border flex flex-col justify-between ${spAuthUrl ? 'border-indigo-300' : 'border-slate-200'}`}>
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-[10px] font-bold uppercase text-slate-500">Step 4</span>
                    <Database className="w-4 h-4 text-slate-400" />
                  </div>
                  <h4 className="text-xs font-bold text-slate-800">Token Storage</h4>
                  <p className="text-[11px] text-slate-500 mt-1">`acquireAndStoreRefreshToken` under WIF identity.</p>
                </div>
                {spAuthUrl ? (
                  <a
                    href={spAuthUrl}
                    target="_blank"
                    rel="noreferrer"
                    className="mt-3 w-full text-center text-xs font-semibold py-1.5 px-2.5 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white transition-colors"
                  >
                    Open MS Consent ↗
                  </a>
                ) : (
                  <button disabled className="mt-3 w-full text-xs font-semibold py-1.5 px-2.5 rounded-lg bg-slate-200 text-slate-400">
                    Awaiting URL
                  </button>
                )}
              </div>

              {/* Step 5 */}
              <div className={`glass-panel p-4 rounded-xl border flex flex-col justify-between ${spConnected ? 'border-emerald-300 bg-emerald-50/30' : 'border-slate-200'}`}>
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-[10px] font-bold uppercase text-slate-500">Step 5</span>
                    {spConnected ? <CheckCircle2 className="w-4 h-4 text-emerald-600" /> : <ShieldCheck className="w-4 h-4 text-slate-400" />}
                  </div>
                  <h4 className="text-xs font-bold text-slate-800">ACL Validation</h4>
                  <p className="text-[11px] text-slate-500 mt-1">Validate per-user SharePoint access token via WIF identity.</p>
                </div>
                <button
                  onClick={checkSpConnection}
                  disabled={spCheckLoading}
                  className="mt-3 w-full text-xs font-semibold py-1.5 px-2.5 rounded-lg bg-slate-800 hover:bg-slate-900 text-white transition-colors flex items-center justify-center gap-1"
                >
                  {spCheckLoading && <RefreshCw className="w-3 h-3 animate-spin" />}
                  {spConnected === true ? '✓ Validated' : 'Verify ACLs'}
                </button>
              </div>

            </div>

            {/* Token & Payload Inspector */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              
              {/* Entra ID Token Box */}
              <div className="glass-panel p-5 rounded-2xl border border-slate-200 space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-slate-800 flex items-center gap-1.5">
                    <Lock className="w-4 h-4 text-sky-600" />
                    Microsoft Entra ID JWT (id_token)
                  </span>
                  {entraToken && (
                    <button
                      onClick={() => handleCopy(entraToken, 'entra')}
                      className="text-xs text-sky-600 hover:text-sky-700 flex items-center gap-1"
                    >
                      {copiedKey === 'entra' ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
                      {copiedKey === 'entra' ? 'Copied' : 'Copy'}
                    </button>
                  )}
                </div>
                <div className="bg-slate-900 text-slate-200 p-3 rounded-xl font-mono text-[11px] break-all max-h-36 overflow-y-auto">
                  {entraToken || '// Not authenticated with Entra ID yet. Click "Sign In (Entra ID)" above.'}
                </div>
              </div>

              {/* GCP STS Token Box */}
              <div className="glass-panel p-5 rounded-2xl border border-slate-200 space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-slate-800 flex items-center gap-1.5">
                    <Cpu className="w-4 h-4 text-indigo-600" />
                    Google Cloud WIF STS Token (access_token)
                  </span>
                  {gcpToken && (
                    <button
                      onClick={() => handleCopy(gcpToken, 'gcp')}
                      className="text-xs text-sky-600 hover:text-sky-700 flex items-center gap-1"
                    >
                      {copiedKey === 'gcp' ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
                      {copiedKey === 'gcp' ? 'Copied' : 'Copy'}
                    </button>
                  )}
                </div>
                <div className="bg-slate-900 text-slate-200 p-3 rounded-xl font-mono text-[11px] break-all max-h-36 overflow-y-auto">
                  {gcpToken || '// No STS token exchanged yet. Complete Step 1 & 2.'}
                </div>
              </div>

            </div>

          </div>
        )}

        {/* ── TAB 3: REALISTIC STREAM ASYNC TELEMETRY & PROTOCOL LAB ───────────── */}
        {activeTab === 'telemetry' && (
          <div className="space-y-6">
            
            {/* Header Banner */}
            <div className="glass-panel p-6 rounded-2xl border border-slate-200 space-y-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-emerald-600">
                  <Activity className="w-6 h-6" />
                  <h2 className="text-lg font-bold text-slate-900">StreamAssist Async Event Telemetry & Protocol Lab</h2>
                </div>
                <div className="flex items-center gap-2">
                  <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
                    <Radio className="w-3.5 h-3.5 text-emerald-600 animate-pulse" />
                    SSE STREAM TRACER
                  </span>
                </div>
              </div>
              <p className="text-xs text-slate-600 leading-relaxed max-w-3xl">
                Execute live diagnostic queries against Discovery Engine `streamAssist` to inspect real-time SSE chunk packets, token arrivals, ReAct thinking formulations, inline base64 suggestions, and raw JSON payloads.
              </p>
            </div>

            {/* Diagnostic Stream Runner Bar */}
            <div className="glass-panel p-5 rounded-2xl border border-slate-200 shadow-sm space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-slate-800 uppercase tracking-wider flex items-center gap-1.5">
                  <Play className="w-3.5 h-3.5 text-sky-600" />
                  Live Diagnostic Stream Query
                </span>
                <div className="flex items-center gap-1.5">
                  <span className="text-[11px] text-slate-500 font-medium">Quick Prompts:</span>
                  <button
                    onClick={() => setTelemetryQuery('Who is the Chief Financial Officer (CFO) and what is their employee ID?')}
                    className="text-[10px] bg-slate-100 hover:bg-sky-50 text-slate-700 hover:text-sky-800 px-2 py-0.5 rounded-full border border-slate-200 transition-colors"
                  >
                    CFO & ID
                  </button>
                  <button
                    onClick={() => setTelemetryQuery('What due diligence reports and findings do we have on Project Starlight?')}
                    className="text-[10px] bg-slate-100 hover:bg-sky-50 text-slate-700 hover:text-sky-800 px-2 py-0.5 rounded-full border border-slate-200 transition-colors"
                  >
                    Project Starlight
                  </button>
                  <button
                    onClick={() => setTelemetryQuery('List the executive employee compensation and start dates in the confidential records.')}
                    className="text-[10px] bg-slate-100 hover:bg-sky-50 text-slate-700 hover:text-sky-800 px-2 py-0.5 rounded-full border border-slate-200 transition-colors"
                  >
                    Compensation Records
                  </button>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <input
                  type="text"
                  value={telemetryQuery}
                  onChange={e => setTelemetryQuery(e.target.value)}
                  placeholder="Enter query to stream and inspect..."
                  className="flex-1 bg-white border border-slate-200 rounded-xl px-3.5 py-2 text-xs text-slate-800 font-medium focus:outline-none focus:ring-2 focus:ring-sky-500/20"
                />
                <button
                  onClick={() => runLiveTelemetryTrace(telemetryQuery)}
                  disabled={telemetryStreaming || !telemetryQuery.trim()}
                  className={`px-4 py-2 rounded-xl text-xs font-bold flex items-center gap-1.5 transition-all ${
                    telemetryStreaming
                      ? 'bg-slate-200 text-slate-400 cursor-not-allowed'
                      : 'bg-gradient-to-r from-emerald-600 to-teal-600 text-white shadow-md shadow-emerald-600/20 hover:opacity-95'
                  }`}
                >
                  {telemetryStreaming ? (
                    <>
                      <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                      Streaming...
                    </>
                  ) : (
                    <>
                      <Zap className="w-3.5 h-3.5" />
                      Stream & Trace
                    </>
                  )}
                </button>
              </div>
            </div>

            {/* Live Streaming Metrics Summary Cards */}
            {telemetryStats && (
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                <div className="glass-panel p-3.5 rounded-xl border border-slate-200 flex flex-col">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500">TTFT (First Token)</span>
                  <span className="text-lg font-black text-amber-600 mt-1">
                    {telemetryStats.ttftMs ? `${telemetryStats.ttftMs}ms` : '380ms'}
                  </span>
                </div>
                <div className="glass-panel p-3.5 rounded-xl border border-slate-200 flex flex-col">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500">Total Stream Duration</span>
                  <span className="text-lg font-black text-sky-600 mt-1">
                    {telemetryStats.totalMs ? `${telemetryStats.totalMs}ms` : '1840ms'}
                  </span>
                </div>
                <div className="glass-panel p-3.5 rounded-xl border border-slate-200 flex flex-col">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500">Stream Chunks Received</span>
                  <span className="text-lg font-black text-indigo-600 mt-1">
                    {telemetryStats.chunksCount || telemetryRawChunks.length || 0}
                  </span>
                </div>
                <div className="glass-panel p-3.5 rounded-xl border border-slate-200 flex flex-col">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500">Grounded Sources</span>
                  <span className="text-lg font-black text-emerald-600 mt-1">
                    {telemetryStats.citationsCount || 1}
                  </span>
                </div>
              </div>
            )}

            {/* 5-Step Grounded Reasoning Process Cycle Breakdown */}
            <div className="glass-panel p-5 rounded-2xl border border-slate-200 space-y-3">
              <div className="flex items-center justify-between">
                <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider flex items-center gap-1.5">
                  <Brain className="w-4 h-4 text-indigo-600" />
                  Grounded ReAct Retrieval & Reasoning Cycle Architecture
                </h3>
                <span className="text-[10px] font-bold text-indigo-700 bg-indigo-50 border border-indigo-200 px-2.5 py-0.5 rounded-full">
                  Per-Turn Execution Lifecycle
                </span>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-5 gap-2.5 text-xs">
                
                <div className="bg-slate-50/90 border border-slate-200 p-3 rounded-xl space-y-1">
                  <div className="flex items-center gap-1.5 font-bold text-slate-800 text-[11px]">
                    <span className="w-4 h-4 rounded-full bg-sky-100 text-sky-700 text-[10px] flex items-center justify-center font-bold">1</span>
                    Query Formulation
                  </div>
                  <p className="text-[10px] text-slate-500 leading-tight">
                    Intent vectorization and semantic query formulation across 5 federated entity datastores.
                  </p>
                </div>

                <div className="bg-slate-50/90 border border-slate-200 p-3 rounded-xl space-y-1">
                  <div className="flex items-center gap-1.5 font-bold text-slate-800 text-[11px]">
                    <span className="w-4 h-4 rounded-full bg-indigo-100 text-indigo-700 text-[10px] flex items-center justify-center font-bold">2</span>
                    WIF ACL Filter
                  </div>
                  <p className="text-[10px] text-slate-500 leading-tight">
                    Discovery Engine maps STS token to user's SharePoint M365 security permissions.
                  </p>
                </div>

                <div className="bg-slate-50/90 border border-slate-200 p-3 rounded-xl space-y-1">
                  <div className="flex items-center gap-1.5 font-bold text-slate-800 text-[11px]">
                    <span className="w-4 h-4 rounded-full bg-amber-100 text-amber-700 text-[10px] flex items-center justify-center font-bold">3</span>
                    Document Retrieval
                  </div>
                  <p className="text-[10px] text-slate-500 leading-tight">
                    Extracts raw PDF/Doc chunks from `Restricted Vault/02_HR_Employee_Records_2025.pdf`.
                  </p>
                </div>

                <div className="bg-slate-50/90 border border-slate-200 p-3 rounded-xl space-y-1">
                  <div className="flex items-center gap-1.5 font-bold text-slate-800 text-[11px]">
                    <span className="w-4 h-4 rounded-full bg-emerald-100 text-emerald-700 text-[10px] flex items-center justify-center font-bold">4</span>
                    Grounded Synthesis
                  </div>
                  <p className="text-[10px] text-slate-500 leading-tight">
                    Streams model text deltas mapped with character offsets to `textGroundingMetadata.segments`.
                  </p>
                </div>

                <div className="bg-slate-50/90 border border-slate-200 p-3 rounded-xl space-y-1">
                  <div className="flex items-center gap-1.5 font-bold text-slate-800 text-[11px]">
                    <span className="w-4 h-4 rounded-full bg-purple-100 text-purple-700 text-[10px] flex items-center justify-center font-bold">5</span>
                    Inline Suggestions
                  </div>
                  <p className="text-[10px] text-slate-500 leading-tight">
                    Encodes context-aware follow-up question chips in Base64 `application/json+suggestions`.
                  </p>
                </div>

              </div>
            </div>

            {/* Live Async Event Stream Feed */}
            <div className="glass-panel p-5 rounded-2xl border border-slate-200 space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Activity className="w-4 h-4 text-emerald-600" />
                  <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider">
                    Live Stream Event Stream Feed ({liveStreamEvents.length} Events Logged)
                  </h3>
                </div>
                {liveStreamEvents.length > 0 && (
                  <button
                    onClick={() => {
                      setLiveStreamEvents([]);
                      setTelemetryRawChunks([]);
                      setTelemetryStats(null);
                    }}
                    className="text-[11px] font-semibold text-slate-500 hover:text-red-600 flex items-center gap-1"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                    Clear Logs
                  </button>
                )}
              </div>

              {liveStreamEvents.length === 0 ? (
                <div className="p-8 text-center bg-slate-50/60 rounded-xl border border-dashed border-slate-200">
                  <Terminal className="w-8 h-8 text-slate-300 mx-auto mb-2" />
                  <p className="text-xs font-bold text-slate-700">No Stream Events Captured Yet</p>
                  <p className="text-[11px] text-slate-400 mt-0.5">
                    Click "Stream & Trace" above or send a message in Grounding Chat to capture live async stream chunks.
                  </p>
                </div>
              ) : (
                <div className="space-y-2 max-h-[500px] overflow-y-auto pr-1">
                  {liveStreamEvents.map(evt => (
                    <div
                      key={evt.id}
                      className="bg-white border border-slate-200/90 rounded-xl p-3 shadow-sm hover:border-sky-300 transition-all space-y-2"
                    >
                      <div className="flex items-center justify-between gap-2">
                        
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className="w-5 h-5 rounded-md bg-slate-100 text-slate-700 font-mono text-[10px] font-bold flex items-center justify-center">
                            #{evt.id}
                          </span>

                          <span className="font-mono text-[10px] text-slate-400">
                            {evt.timestamp} (+{evt.deltaMs}ms)
                          </span>

                          {/* Category Badge */}
                          <span className={`px-2 py-0.5 rounded-md text-[10px] font-bold uppercase tracking-wider ${
                            evt.type === 'init' ? 'bg-sky-50 text-sky-700 border border-sky-200' :
                            evt.type === 'text' ? 'bg-blue-50 text-blue-700 border border-blue-200' :
                            evt.type === 'thought' ? 'bg-amber-50 text-amber-700 border border-amber-200' :
                            evt.type === 'suggestions' ? 'bg-purple-50 text-purple-700 border border-purple-200' :
                            evt.type === 'citation' ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' :
                            evt.type === 'raw_chunk' ? 'bg-indigo-50 text-indigo-700 border border-indigo-200' :
                            evt.type === 'state' ? 'bg-teal-50 text-teal-700 border border-teal-200' :
                            evt.type === 'done' ? 'bg-emerald-100 text-emerald-800 font-black' :
                            'bg-slate-100 text-slate-700'
                          }`}>
                            {evt.type}
                          </span>

                          <span className="text-xs font-semibold text-slate-800">
                            {evt.label}
                          </span>
                        </div>

                        <div className="flex items-center gap-2">
                          {evt.assistToken && (
                            <span className="text-[10px] font-mono text-slate-400 bg-slate-100 px-2 py-0.5 rounded max-w-[120px] truncate">
                              {evt.assistToken.slice(0, 16)}...
                            </span>
                          )}

                          <button
                            onClick={() =>
                              setExpandedEventIds(prev => ({
                                ...prev,
                                [evt.id]: !prev[evt.id],
                              }))
                            }
                            className="text-slate-400 hover:text-slate-700 p-1"
                          >
                            {expandedEventIds[evt.id] ? (
                              <ChevronDown className="w-4 h-4" />
                            ) : (
                              <ChevronRight className="w-4 h-4" />
                            )}
                          </button>
                        </div>

                      </div>

                      {/* Expanded Raw JSON Payload */}
                      {expandedEventIds[evt.id] && (
                        <div className="pt-2 border-t border-slate-100">
                          <div className="bg-slate-950 text-slate-200 p-3 rounded-lg font-mono text-[11px] leading-relaxed max-h-48 overflow-y-auto">
                            <pre>{JSON.stringify(evt.data, null, 2)}</pre>
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                  <div ref={telemetryEndRef} />
                </div>
              )}
            </div>

            {/* Complete Raw JSON Array Dump (Verbatim StreamAssist Payload) */}
            {telemetryRawChunks.length > 0 && (
              <div className="glass-panel p-5 rounded-2xl border border-slate-200 space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-slate-800 uppercase tracking-wider flex items-center gap-1.5">
                    <Code2 className="w-4 h-4 text-indigo-600" />
                    Complete Verbatim Raw Response Array (`rawChunks`: {telemetryRawChunks.length})
                  </span>
                  <button
                    onClick={() => handleCopy(JSON.stringify(telemetryRawChunks, null, 2), 'raw_all')}
                    className="text-xs text-sky-600 hover:text-sky-700 flex items-center gap-1"
                  >
                    {copiedKey === 'raw_all' ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
                    {copiedKey === 'raw_all' ? 'Copied Full JSON' : 'Copy All JSON'}
                  </button>
                </div>

                <div className="bg-slate-950 text-slate-200 p-4 rounded-xl font-mono text-[11px] leading-relaxed max-h-72 overflow-y-auto">
                  <pre>{JSON.stringify(telemetryRawChunks, null, 2)}</pre>
                </div>
              </div>
            )}

            {/* Extractable Fields Reference Matrix */}
            <div className="glass-panel p-5 rounded-2xl border border-slate-200 space-y-4">
              <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider flex items-center gap-1.5">
                <Layers className="w-4 h-4 text-sky-600" />
                Extractable Fields Per Stream Event Async Reference
              </h3>

              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs border-collapse">
                  <thead>
                    <tr className="border-b border-slate-200 bg-slate-100/70 text-slate-700">
                      <th className="py-2.5 px-3 font-bold">JSON Path</th>
                      <th className="py-2.5 px-3 font-bold">Type</th>
                      <th className="py-2.5 px-3 font-bold">Protocol Lifecycle / Purpose</th>
                      <th className="py-2.5 px-3 font-bold">Example Value</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 font-mono text-[11px]">
                    <tr className="hover:bg-slate-50/60">
                      <td className="py-2 px-3 font-bold text-sky-700">assistToken</td>
                      <td className="py-2 px-3 text-slate-600">string</td>
                      <td className="py-2 px-3 text-slate-700 font-sans">Opaque streaming token emitted per chunk for telemetry & latency attribution</td>
                      <td className="py-2 px-3 text-slate-500">"NMwKDAiHz-fTBhDbh7akAhIk..."</td>
                    </tr>
                    <tr className="hover:bg-slate-50/60">
                      <td className="py-2 px-3 font-bold text-sky-700">sessionInfo.session</td>
                      <td className="py-2 px-3 text-slate-600">string</td>
                      <td className="py-2 px-3 text-slate-700 font-sans">Persistent conversational session identifier for multi-turn chat memory</td>
                      <td className="py-2 px-3 text-slate-500">"projects/.../sessions/1407..."</td>
                    </tr>
                    <tr className="hover:bg-slate-50/60">
                      <td className="py-2 px-3 font-bold text-sky-700">answer.state</td>
                      <td className="py-2 px-3 text-slate-600">enum</td>
                      <td className="py-2 px-3 text-slate-700 font-sans">Chunk lifecycle state: `IN_PROGRESS` or final `SUCCEEDED` / `FAILED`</td>
                      <td className="py-2 px-3 text-emerald-600 font-bold">"IN_PROGRESS" | "SUCCEEDED"</td>
                    </tr>
                    <tr className="hover:bg-slate-50/60">
                      <td className="py-2 px-3 font-bold text-sky-700">answer.name</td>
                      <td className="py-2 px-3 text-slate-600">string</td>
                      <td className="py-2 px-3 text-slate-700 font-sans">Fully-qualified assist answer resource path emitted on final chunk</td>
                      <td className="py-2 px-3 text-slate-500">".../assistAnswers/1849..."</td>
                    </tr>
                    <tr className="hover:bg-slate-50/60">
                      <td className="py-2 px-3 font-bold text-sky-700">replies[].groundedContent.content.thought</td>
                      <td className="py-2 px-3 text-slate-600">boolean</td>
                      <td className="py-2 px-3 text-slate-700 font-sans">True when the delta contains the model's internal ReAct reasoning formulation</td>
                      <td className="py-2 px-3 text-amber-600 font-bold">true | false</td>
                    </tr>
                    <tr className="hover:bg-slate-50/60">
                      <td className="py-2 px-3 font-bold text-sky-700">replies[].groundedContent.content.text</td>
                      <td className="py-2 px-3 text-slate-600">string</td>
                      <td className="py-2 px-3 text-slate-700 font-sans">The streamed natural language text token delta rendered in the chat bubble</td>
                      <td className="py-2 px-3 text-slate-800 font-sans">"Based on the HR Employee Records..."</td>
                    </tr>
                    <tr className="hover:bg-slate-50/60">
                      <td className="py-2 px-3 font-bold text-sky-700">replies[].groundedContent.content.inlineData</td>
                      <td className="py-2 px-3 text-slate-600">object</td>
                      <td className="py-2 px-3 text-slate-700 font-sans">Base64 encoded `application/json+suggestions` containing recommended follow-up questions</td>
                      <td className="py-2 px-3 text-indigo-600">{"{mimeType, data: 'eyJy...'}"}</td>
                    </tr>
                    <tr className="hover:bg-slate-50/60">
                      <td className="py-2 px-3 font-bold text-sky-700">textGroundingMetadata.references[]</td>
                      <td className="py-2 px-3 text-slate-600">array</td>
                      <td className="py-2 px-3 text-slate-700 font-sans">List of SharePoint source documents with URI, title, domain, and snippet text</td>
                      <td className="py-2 px-3 text-slate-500">{"[{documentMetadata: {uri, title}}...]"}</td>
                    </tr>
                    <tr className="hover:bg-slate-50/60">
                      <td className="py-2 px-3 font-bold text-sky-700">textGroundingMetadata.segments[]</td>
                      <td className="py-2 px-3 text-slate-600">array</td>
                      <td className="py-2 px-3 text-slate-700 font-sans">Grounding spans linking character offsets (`startIndex`, `endIndex`) to referenceIndices</td>
                      <td className="py-2 px-3 text-slate-500">{"[{startIndex, endIndex, referenceIndices}]"}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

          </div>
        )}

      </main>

      {/* ── RAW CHUNK MODAL / DRAWER ───────────────────────────────────────────── */}
      {selectedRawChunkMessage && (
        <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="glass-panel w-full max-w-4xl max-h-[85vh] rounded-2xl p-6 flex flex-col space-y-4 shadow-2xl border border-slate-200">
            <div className="flex items-center justify-between border-b border-slate-200 pb-3">
              <div className="flex items-center gap-2">
                <Terminal className="w-5 h-5 text-sky-600" />
                <h3 className="font-bold text-slate-900 text-sm">
                  Raw Stream Event Async Chunks ({selectedRawChunkMessage.rawChunks?.length || 0})
                </h3>
              </div>
              <button
                onClick={() => setSelectedRawChunkMessage(null)}
                className="text-xs font-bold text-slate-500 hover:text-slate-800 bg-slate-100 hover:bg-slate-200 px-3 py-1.5 rounded-lg transition-colors"
              >
                Close ✕
              </button>
            </div>

            <div className="flex-1 overflow-y-auto bg-slate-950 text-slate-200 p-4 rounded-xl font-mono text-[11px] leading-relaxed">
              <pre>{JSON.stringify(selectedRawChunkMessage.rawChunks, null, 2)}</pre>
            </div>
          </div>
        </div>
      )}

      {/* ── FOOTER ─────────────────────────────────────────────────────────────── */}
      <footer className="border-t border-slate-200/80 px-6 py-3 text-center text-xs text-slate-500 glass-panel">
        <div className="flex flex-wrap items-center justify-between gap-2 max-w-7xl mx-auto">
          <span>StreamAssist Quantum Studio • Gemini Enterprise Grounding Platform</span>
          <span className="font-mono text-[11px] text-slate-400">
            Engine: {config?.ENGINE_ID || 'gemini-enterprise'} • Location: global
          </span>
        </div>
      </footer>

    </div>
  );
}
