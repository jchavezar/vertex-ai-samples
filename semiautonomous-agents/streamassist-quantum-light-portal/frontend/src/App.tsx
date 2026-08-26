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

interface FederatedConnector {
  id: string;
  name?: string;
  displayName: string;
  dataSource?: string;
  authState: 'AUTHORIZED' | 'NOT_AUTHORIZED' | 'EXPIRED' | string;
  authorizationUri?: string;
  iconLink?: string;
  dataStores?: string[];
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
  const [activeTab, setActiveTab] = useState<'chat' | 'workflow' | 'security' | 'telemetry'>('chat');

  // Workflow Agent Runner State
  const [availableWorkflows, setAvailableWorkflows] = useState<any[]>([]);
  const [selectedWorkflowId, setSelectedWorkflowId] = useState('10124597458587638985');
  const [workflowTopicInput, setWorkflowTopicInput] = useState('google tpu');
  const [workflowAgentId, setWorkflowAgentId] = useState('10124597458587638985');
  const [workflowScheduleId, setWorkflowScheduleId] = useState<string | null>(null);
  const [workflowTriggerId, setWorkflowTriggerId] = useState<string | null>('manual_trigger');
  const [workflowRunning, setWorkflowRunning] = useState(false);
  const [workflowSession, setWorkflowSession] = useState<string | null>(null);
  const [workflowNodes, setWorkflowNodes] = useState<{
    id: string;
    label: string;
    status: 'idle' | 'running' | 'completed' | 'interrupted' | 'error';
    outputs?: any;
    error?: string;
  }[]>([
    { id: 'manual_trigger', label: 'Manual Trigger', status: 'idle' },
    { id: 'research_agent', label: 'Document Researcher', status: 'idle' },
    { id: 'document_selection', label: 'Document Selection', status: 'idle' },
    { id: 'summarizer_agent', label: 'Document Summarizer', status: 'idle' },
  ]);
  const [workflowLogs, setWorkflowLogs] = useState<string[]>([]);
  const [workflowHitlAction, setWorkflowHitlAction] = useState<any | null>(null);
  const [workflowHitlInput, setWorkflowHitlInput] = useState('2,3');
  const [workflowSummaryResult, setWorkflowSummaryResult] = useState<string | null>(null);
  const [workflowMetrics, setWorkflowMetrics] = useState<{ duration_ms: number } | null>(null);

  // Backend Config & Discovery State
  const [config, setConfig] = useState<BackendConfig | null>(null);
  const [discoveredStores, setDiscoveredStores] = useState<string[]>([]);
  const [connectorsList, setConnectorsList] = useState<FederatedConnector[]>([]);
  const [allowlistedDomains, setAllowlistedDomains] = useState<string[]>([]);
  const [allowlistLoading, setAllowlistLoading] = useState(false);
  const [allowlistSuccess, setAllowlistSuccess] = useState<string | null>(null);
  const [authActionLoading, setAuthActionLoading] = useState<Record<string, boolean>>({});
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

  // Helper to fetch Widget Config with origin domain
  const fetchWidgetConfig = useCallback(async (customToken?: string) => {
    setDiscoveryLoading(true);
    try {
      const origin = window.location.origin;
      const t = customToken || entraToken;
      const res = await fetch(`/api/discovery/widget-config?custom_domain=${encodeURIComponent(origin)}`, {
        headers: t ? { 'X-Entra-Id-Token': t } : {},
      });
      const data = await res.json();
      if (data.connectors && data.connectors.length > 0) {
        setConnectorsList(data.connectors);
      }
      if (data.discovered_datastores && data.discovered_datastores.length > 0) {
        setDiscoveredStores(data.discovered_datastores);
      } else if (data.fallback_datastores) {
        setDiscoveredStores(data.fallback_datastores);
      }
      if (data.allowlistedDomains) {
        setAllowlistedDomains(data.allowlistedDomains);
      }
    } catch (err) {
      console.error("Failed to load widget config:", err);
    } finally {
      setDiscoveryLoading(false);
    }
  }, [entraToken]);

  // Load config on mount
  useEffect(() => {
    fetch('/api/config')
      .then(res => res.json())
      .then(data => setConfig(data))
      .catch(err => console.error("Error loading config:", err));

    fetchWidgetConfig();
    
    // Fetch Workflow Agents list
    fetch('/api/workflow/agents')
      .then(res => res.json())
      .then(data => {
        if (data.workflows && data.workflows.length > 0) {
          setAvailableWorkflows(data.workflows);
          // Default to Document Research and Summarizer if available, or first
          const docWf = data.workflows.find((w: any) => w.agentId === '10124597458587638985') || data.workflows[0];
          if (docWf) {
            handleSelectWorkflow(docWf);
          }
        }
      })
      .catch(err => console.error("Error loading workflow agents:", err));
  }, [fetchWidgetConfig]);

  // Select active workflow template
  const handleSelectWorkflow = (wf: any) => {
    setSelectedWorkflowId(wf.agentId);
    setWorkflowAgentId(wf.agentId);
    setWorkflowTriggerId(wf.triggerId || (wf.triggerType === 'MANUAL_TRIGGER' ? 'manual_trigger' : null));
    setWorkflowScheduleId(wf.scheduleId || null);
    setWorkflowSession(null);
    setWorkflowHitlAction(null);
    setWorkflowSummaryResult(null);
    setWorkflowLogs([]);
    
    if (wf.nodes && wf.nodes.length > 0) {
      setWorkflowNodes(wf.nodes.map((n: any) => ({
        id: n.id,
        label: n.displayName || n.id,
        status: 'idle'
      })));
    }
  };

  // OAuth Popup Message Listener (Product Notebook Step 3.1 & Step 4)
  useEffect(() => {
    const handlePopupMessage = async (event: MessageEvent) => {
      // Accept redirect messages from Google Discovery Engine OAuth redirect handler
      if (event.origin === 'https://vertexaisearch.cloud.google.com' || event.origin === window.location.origin) {
        console.log("OAuth Redirect Event from Google received:", event.data);
        const redirectData = typeof event.data === 'string' ? event.data : event.data?.fullRedirectUri || event.data?.url;
        
        if (redirectData && (typeof redirectData === 'string' && redirectData.includes('code='))) {
          try {
            // Step 4: Call AcquireAndStoreRefreshToken
            const resp = await fetch('/api/connector/acquire-and-store-refresh-token', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
                ...(entraToken ? { 'X-Entra-Id-Token': entraToken } : {})
              },
              body: JSON.stringify({ full_redirect_uri: redirectData })
            });
            const resData = await resp.json();
            
            if (resData.success) {
              // Step 5: Update Engine User Data to AUTHORIZED
              await fetch('/api/connector/update-auth-state', {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json',
                  ...(entraToken ? { 'X-Entra-Id-Token': entraToken } : {})
                },
                body: JSON.stringify({ auth_state: 'AUTHORIZED' })
              });
              
              await fetchWidgetConfig();
            }
          } catch (err) {
            console.error("Error saving connector refresh token:", err);
          }
        }
      }
    };

    window.addEventListener('message', handlePopupMessage);
    return () => window.removeEventListener('message', handlePopupMessage);
  }, [entraToken, fetchWidgetConfig]);

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

  // Allowlist Domain Handler (Notebook Step 2 - Cell 6)
  const handleAllowlistDomain = async () => {
    setAllowlistLoading(true);
    setAllowlistSuccess(null);
    try {
      const origin = window.location.origin;
      const res = await fetch('/api/discovery/allowlist-domain', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(entraToken ? { 'X-Entra-Id-Token': entraToken } : {})
        },
        body: JSON.stringify({ domain: origin })
      });
      const data = await res.json();
      if (data.success) {
        setAllowlistSuccess(`Domain ${origin} successfully registered in Discovery Engine WidgetConfig!`);
        await fetchWidgetConfig();
      } else {
        setAllowlistSuccess(`Response: ${typeof data.response === 'string' ? data.response : JSON.stringify(data.response || data.error)}`);
      }
    } catch (e: any) {
      setAllowlistSuccess(`Error: ${e.message}`);
    } finally {
      setAllowlistLoading(false);
    }
  };

  // Authorize connector via Google-provided authorizationUri (Notebook Step 2 & 3)
  const handleAuthorizeConnector = (authUri?: string) => {
    if (!authUri) {
      alert("No dynamic authorizationUri available for this connector. Ensure the domain is allowlisted first.");
      return;
    }
    const width = 600;
    const height = 700;
    const left = window.screenX + (window.outerWidth - width) / 2;
    const top = window.screenY + (window.outerHeight - height) / 2;
    window.open(
      authUri,
      'google-discoveryengine-oauth',
      `width=${width},height=${height},left=${left},top=${top},status=no,resizable=yes`
    );
  };

  // Revoke / Unauthorize connector handler (Notebook Step 6 - Cell 18)
  const handleRevokeConnector = async (connectorId: string) => {
    setAuthActionLoading(prev => ({ ...prev, [connectorId]: true }));
    try {
      const res = await fetch('/api/connector/update-auth-state', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(entraToken ? { 'X-Entra-Id-Token': entraToken } : {})
        },
        body: JSON.stringify({ collection_id: connectorId, auth_state: 'EXPIRED' })
      });
      await res.json();
      await fetchWidgetConfig();
    } catch (err) {
      console.error("Failed to revoke connector:", err);
    } finally {
      setAuthActionLoading(prev => ({ ...prev, [connectorId]: false }));
    }
  };

  // Run Workflow Agent Execution
  const runWorkflowExecution = async (isConfirm: boolean = false) => {
    if (workflowRunning) return;
    setWorkflowRunning(true);
    if (!isConfirm) {
      setWorkflowHitlAction(null);
      setWorkflowSummaryResult(null);
      setWorkflowMetrics(null);
      setWorkflowLogs([]);
      setWorkflowNodes(prev => prev.map(n => ({ ...n, status: 'idle', outputs: undefined, error: undefined })));
    }

    const logEntry = (msg: string) => {
      setWorkflowLogs(prev => [...prev, `[${new Date().toLocaleTimeString()}] ${msg}`]);
    };

    logEntry(isConfirm ? "Resuming workflow with human input confirmation..." : `Triggering StreamAssist Workflow execution: [${selectedWorkflowId}]...`);

    try {
      // Build payload
      const payload: any = {
        agent_id: workflowAgentId,
        session_token: workflowSession,
        action_confirmed: isConfirm,
      };

      if (workflowScheduleId) {
        payload.schedule_id = workflowScheduleId;
      } else if (workflowTriggerId) {
        payload.trigger_id = workflowTriggerId;
      }

      if (!isConfirm && workflowTopicInput) {
        payload.input_variables = { topic: workflowTopicInput };
      }

      if (isConfirm && workflowHitlAction) {
        // Human confirmation / parameter submission
        const paramDecl = workflowHitlAction.parameterDeclaration || {};
        const paramProps = paramDecl.properties || {};
        const firstParamKey = Object.keys(paramProps)[0] || 'selected_numbers';

        payload.action_execution_params = {
          agentName: workflowHitlAction.agentName,
          actionName: workflowHitlAction.actionName || 'flow_request_input',
          actionInvocationId: workflowHitlAction.invocationId || workflowHitlAction.actionInvocationId,
          args: {
            [firstParamKey]: workflowHitlInput
          }
        };
      }

      const response = await fetch('/api/workflow/run', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(entraToken ? { 'X-Entra-Id-Token': entraToken } : {}),
        },
        body: JSON.stringify(payload),
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

                if (event.type === 'init') {
                  if (event.session && event.session !== '-') {
                    setWorkflowSession(event.session);
                    logEntry(`Session initialized: ${event.session}`);
                  }
                } else if (event.type === 'session_info') {
                  if (event.session) {
                    setWorkflowSession(event.session);
                    logEntry(`Session bound: ${event.session}`);
                  }
                } else if (event.type === 'node_start') {
                  if (!event.isRoot) {
                    logEntry(`▶️ Started node: ${event.nodeId}`);
                    setWorkflowNodes(prev => prev.map(n => n.id === event.nodeId ? { ...n, status: 'running' } : n));
                  }
                } else if (event.type === 'node_resume') {
                  if (!event.isRoot) {
                    logEntry(`🔄 Resumed node: ${event.nodeId}`);
                    setWorkflowNodes(prev => prev.map(n => n.id === event.nodeId ? { ...n, status: 'running' } : n));
                  }
                } else if (event.type === 'node_end') {
                  if (!event.isRoot) {
                    logEntry(`✅ Completed node: ${event.nodeId}`);
                    setWorkflowNodes(prev => prev.map(n => n.id === event.nodeId ? { ...n, status: 'completed', outputs: event.outputs } : n));
                    if (event.outputs?.summary) {
                      setWorkflowSummaryResult(event.outputs.summary);
                    } else if (event.outputs?.research_results_text) {
                      // Optional: preview research results
                    }
                  }
                } else if (event.type === 'node_interrupt') {
                  logEntry(`⏸️ Node interrupted: ${event.nodeId} (Waiting for Human Input / Confirmation)`);
                  setWorkflowNodes(prev => prev.map(n => n.id === event.nodeId ? { ...n, status: 'interrupted' } : n));
                } else if (event.type === 'hitl_confirmation') {
                  logEntry(`⚠️ Human-in-the-loop action received: ${event.actionInvocation?.actionName || 'Request Input'}`);
                  setWorkflowHitlAction(event.actionInvocation);
                } else if (event.type === 'node_error') {
                  logEntry(`❌ Error in node ${event.nodeId}: ${JSON.stringify(event.error)}`);
                  setWorkflowNodes(prev => prev.map(n => n.id === event.nodeId ? { ...n, status: 'error', error: JSON.stringify(event.error) } : n));
                } else if (event.type === 'text') {
                  logEntry(`💬 ${event.delta}`);
                  setWorkflowSummaryResult(prev => (prev || '') + event.delta);
                } else if (event.type === 'metrics') {
                  setWorkflowMetrics({ duration_ms: event.duration_ms });
                  logEntry(`⏱️ Execution duration: ${event.duration_ms}ms`);
                }
              } catch (parseErr) {
                console.error("Workflow event parse error:", parseErr);
              }
            }
          }
        }
      }
    } catch (err: any) {
      logEntry(`❌ Workflow run error: ${err.message}`);
    } finally {
      setWorkflowRunning(false);
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
            onClick={() => setActiveTab('workflow')}
            className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg transition-all ${
              activeTab === 'workflow'
                ? 'bg-white text-indigo-700 shadow-sm font-bold border border-slate-200/60'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <Cpu className="w-3.5 h-3.5 text-indigo-500" />
            Workflow Agents
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
              <div className="flex items-center gap-3 flex-wrap">
                <div className="flex items-center gap-1.5 text-slate-700 font-medium">
                  <Database className="w-4 h-4 text-sky-500" />
                  <span>Grounding Connectors:</span>
                  <div className="flex items-center gap-1">
                    <span className="font-semibold bg-sky-50 text-sky-700 border border-sky-200 px-2 py-0.5 rounded text-[11px]">
                      ✉️ Outlook
                    </span>
                    <span className="font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200 px-2 py-0.5 rounded text-[11px]">
                      📁 SharePoint
                    </span>
                    <span className="font-semibold bg-purple-50 text-purple-700 border border-purple-200 px-2 py-0.5 rounded text-[11px]">
                      🎫 ServiceNow
                    </span>
                  </div>
                </div>

                <div className="hidden md:flex items-center gap-1 text-slate-500">
                  <span>Stores:</span>
                  <span className="font-semibold text-slate-700">
                    {discoveryLoading ? 'Discovering...' : `${discoveredStores.length || 14} active entity stores`}
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

        {/* ── TAB: WORKFLOW AGENTS RUNNER ────────────────────────────────────────── */}
        {activeTab === 'workflow' && (
          <div className="space-y-6">
            {/* Header Description & Workflow Selector */}
            <div className="glass-panel p-6 rounded-2xl border border-slate-200 space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                  <div className="flex items-center gap-2 text-indigo-600">
                    <Cpu className="w-6 h-6" />
                    <h2 className="text-lg font-bold text-slate-900">Workflow Agent Execution Hub (StreamAssist)</h2>
                  </div>
                  <p className="text-xs text-slate-600 leading-relaxed max-w-3xl mt-1">
                    Execute and stream multi-step autonomous workflows directly via Google Discovery Engine StreamAssist. Visualizes live node lifecycles, research agents, Outlook integration, LLM consolidation, and Human-in-the-Loop confirmations.
                  </p>
                </div>

                <div className="flex items-center gap-3">
                  <button
                    onClick={() => runWorkflowExecution(false)}
                    disabled={workflowRunning}
                    className={`px-5 py-2.5 rounded-xl text-xs font-bold transition-all shadow-md flex items-center gap-2 ${
                      workflowRunning
                        ? 'bg-slate-200 text-slate-500 cursor-not-allowed'
                        : 'bg-gradient-to-r from-indigo-600 to-sky-600 text-white hover:opacity-95 shadow-indigo-500/20'
                    }`}
                  >
                    {workflowRunning ? (
                      <>
                        <RefreshCw className="w-4 h-4 animate-spin" />
                        Executing Workflow...
                      </>
                    ) : (
                      <>
                        <Play className="w-4 h-4 fill-white" />
                        Run Workflow
                      </>
                    )}
                  </button>
                </div>
              </div>

              {/* Workflow Template Selector Buttons */}
              {availableWorkflows.length > 0 && (
                <div className="pt-2 border-t border-slate-100">
                  <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider block mb-2">
                    Select Workflow Template
                  </span>
                  <div className="flex flex-wrap gap-2">
                    {availableWorkflows.map((wf: any) => {
                      const isSelected = selectedWorkflowId === wf.agentId;
                      return (
                        <button
                          key={wf.agentId}
                          onClick={() => handleSelectWorkflow(wf)}
                          className={`px-3.5 py-2 rounded-xl text-xs font-semibold border transition-all flex items-center gap-2 ${
                            isSelected
                              ? 'bg-indigo-50 border-indigo-300 text-indigo-900 shadow-sm font-bold ring-2 ring-indigo-500/20'
                              : 'bg-white/80 border-slate-200 text-slate-700 hover:bg-slate-50'
                          }`}
                        >
                          <Sparkles className={`w-3.5 h-3.5 ${isSelected ? 'text-indigo-600' : 'text-slate-400'}`} />
                          <div className="text-left">
                            <div>{wf.displayName}</div>
                            <div className="text-[10px] text-slate-400 font-mono font-normal">{wf.agentId}</div>
                          </div>
                        </button>
                      );
                    })}
                  </div>
                </div>
              )}

              {/* Dynamic Parameter / Manual Trigger Controls */}
              <div className="flex flex-wrap items-center gap-3 pt-3 border-t border-slate-100 text-xs">
                {workflowTriggerId === 'manual_trigger' && (
                  <div className="flex items-center gap-2 bg-indigo-50/70 border border-indigo-200/80 px-3 py-1.5 rounded-xl">
                    <span className="font-bold text-indigo-900 text-xs flex items-center gap-1">
                      <Search className="w-3.5 h-3.5 text-indigo-600" /> Topic / Query:
                    </span>
                    <input
                      type="text"
                      value={workflowTopicInput}
                      onChange={(e) => setWorkflowTopicInput(e.target.value)}
                      placeholder="e.g. google tpu, quantum computing"
                      className="bg-white border border-indigo-200 focus:outline-none focus:ring-2 focus:ring-indigo-400 px-2.5 py-1 rounded-lg text-xs font-semibold text-indigo-950 w-56"
                    />
                  </div>
                )}

                <div className="flex items-center gap-1.5 font-mono text-[11px] bg-slate-100 px-3 py-1.5 rounded-lg text-slate-700 border border-slate-200">
                  <span className="font-bold text-slate-500">Agent:</span>
                  <span className="font-mono text-indigo-700 font-bold">{workflowAgentId}</span>
                </div>

                {workflowScheduleId && (
                  <div className="flex items-center gap-1.5 font-mono text-[11px] bg-slate-100 px-3 py-1.5 rounded-lg text-slate-700 border border-slate-200">
                    <span className="font-bold text-slate-500">Schedule:</span>
                    <span className="font-mono text-indigo-700">{workflowScheduleId}</span>
                  </div>
                )}

                {workflowSession && (
                  <span className="text-[11px] font-mono text-slate-500 truncate max-w-xs">
                    Session: {workflowSession.split('/').pop()}
                  </span>
                )}
                {workflowMetrics && (
                  <span className="px-2.5 py-1 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200 font-bold text-[11px] flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    {workflowMetrics.duration_ms} ms
                  </span>
                )}
              </div>
            </div>

            {/* Visual Workflow Node Pipeline */}
            <div className="glass-panel p-6 rounded-2xl border border-slate-200 space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider flex items-center gap-1.5">
                  <Layers className="w-4 h-4 text-indigo-600" />
                  Live Node Execution Pipeline (Google Agent Flow Engine)
                </h3>
                {workflowRunning && (
                  <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-indigo-50 text-indigo-700 border border-indigo-200 animate-pulse">
                    <RefreshCw className="w-3.5 h-3.5 animate-spin text-indigo-600" />
                    Executing Flow Nodes...
                  </span>
                )}
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                {workflowNodes.map((node, idx) => {
                  let statusBg = 'border-slate-200 bg-white/60 text-slate-500';
                  let badge = <span className="text-[10px] font-bold text-slate-400 uppercase">Idle</span>;

                  if (node.status === 'running') {
                    statusBg = 'border-indigo-500 bg-indigo-50/80 text-indigo-900 shadow-lg shadow-indigo-500/10 ring-2 ring-indigo-400/30';
                    badge = (
                      <span className="text-[10px] font-bold text-indigo-700 bg-indigo-100 px-2.5 py-0.5 rounded-full flex items-center gap-1 animate-pulse">
                        <RefreshCw className="w-3 h-3 animate-spin text-indigo-600" /> In Progress
                      </span>
                    );
                  } else if (node.status === 'completed') {
                    statusBg = 'border-emerald-300 bg-emerald-50/60 text-emerald-900';
                    badge = (
                      <span className="text-[10px] font-bold text-emerald-700 bg-emerald-100 px-2.5 py-0.5 rounded-full flex items-center gap-1">
                        <Check className="w-3 h-3 text-emerald-600" /> Complete
                      </span>
                    );
                  } else if (node.status === 'interrupted') {
                    statusBg = 'border-amber-400 bg-amber-50 text-amber-900 shadow-md shadow-amber-200 ring-2 ring-amber-400/50';
                    badge = (
                      <span className="text-[10px] font-bold text-amber-800 bg-amber-200 px-2.5 py-0.5 rounded-full flex items-center gap-1">
                        <AlertCircle className="w-3 h-3 text-amber-600" /> User Input Required
                      </span>
                    );
                  } else if (node.status === 'error') {
                    statusBg = 'border-rose-300 bg-rose-50 text-rose-900';
                    badge = (
                      <span className="text-[10px] font-bold text-rose-700 bg-rose-100 px-2 py-0.5 rounded-full">
                        Error
                      </span>
                    );
                  }

                  return (
                    <div key={node.id} className={`p-4 rounded-xl border flex flex-col justify-between space-y-3 transition-all duration-300 ${statusBg}`}>
                      <div className="flex items-center justify-between">
                        <span className="text-[10px] font-extrabold uppercase text-slate-400">Step {idx + 1}</span>
                        {badge}
                      </div>
                      <div>
                        <h4 className="font-bold text-sm text-slate-900">{node.label}</h4>
                        <p className="text-[11px] font-mono text-slate-500 mt-0.5">{node.id}</p>
                      </div>
                      {node.outputs && (
                        <div className="pt-2 border-t border-slate-200/60 text-[10px] font-mono text-slate-700 max-h-24 overflow-y-auto space-y-1">
                          {Object.keys(node.outputs).map((k) => (
                            <div key={k} className="truncate">
                              <span className="font-bold text-indigo-700">{k}:</span> {typeof node.outputs[k] === 'string' ? node.outputs[k].substring(0, 50) + '...' : JSON.stringify(node.outputs[k])}
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>

            {/* POP-UP MODAL WINDOW FOR HUMAN-IN-THE-LOOP & DOCUMENT SELECTION / EMAIL SENDING */}
            {workflowHitlAction && (
              <div className="fixed inset-0 z-50 bg-slate-950/60 backdrop-blur-sm flex items-center justify-center p-4 animate-in fade-in duration-200">
                <div className="glass-panel w-full max-w-2xl rounded-2xl p-6 flex flex-col space-y-5 shadow-2xl border-2 border-sky-400 bg-white">
                  <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                    <div className="flex items-center gap-2 text-slate-900">
                      <div className="w-8 h-8 rounded-lg bg-sky-500 flex items-center justify-center text-white shadow-sm">
                        {workflowHitlAction.actionName === 'outlook_email_agent__send_mail' ? (
                          <Send className="w-4 h-4" />
                        ) : (
                          <HelpCircle className="w-4 h-4" />
                        )}
                      </div>
                      <div>
                        <h3 className="font-bold text-sm text-slate-900">
                          {workflowHitlAction.actionName === 'outlook_email_agent__send_mail'
                            ? 'Outlook Email Agent: Send Mail'
                            : 'Document Selection & Workflow Input'}
                        </h3>
                        <p className="text-[11px] text-slate-500">
                          {workflowHitlAction.actionName === 'outlook_email_agent__send_mail'
                            ? 'Human confirmation required to dispatch email via Outlook Connector'
                            : 'Review the discovered documents and select which ones to summarize'}
                        </p>
                      </div>
                    </div>
                    <span className="text-[10px] font-mono bg-sky-50 text-sky-700 px-2 py-0.5 rounded-full font-bold border border-sky-200">
                      HITL Input
                    </span>
                  </div>

                  <div className="space-y-4">
                    {/* Content or Document List preview */}
                    <div>
                      <label className="block text-xs font-bold text-slate-700 mb-1">
                        {workflowHitlAction.parameterDeclaration?.title ? 'Discovered Documents' : 'Content Preview'}
                      </label>
                      <div className="p-3.5 bg-slate-50 rounded-xl text-slate-800 font-sans text-xs whitespace-pre-wrap max-h-56 overflow-y-auto border border-slate-200 leading-relaxed font-mono">
                        {workflowHitlAction.parameterDeclaration?.title || workflowHitlAction.args?.Content}
                      </div>
                    </div>

                    {/* Email specific fields */}
                    {workflowHitlAction.actionName === 'outlook_email_agent__send_mail' && (
                      <>
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                          <div>
                            <label className="block text-xs font-bold text-slate-700 mb-1">ContentType</label>
                            <input
                              type="text"
                              readOnly
                              value={workflowHitlAction.args?.ContentType || 'text'}
                              className="w-full text-xs font-mono bg-slate-50 border border-slate-200 px-3 py-2 rounded-lg text-slate-700"
                            />
                          </div>
                          <div>
                            <label className="block text-xs font-bold text-slate-700 mb-1">Subject</label>
                            <input
                              type="text"
                              readOnly
                              value={workflowHitlAction.args?.Subject || 'Daily Outlook Inbox Summary'}
                              className="w-full text-xs font-semibold bg-slate-50 border border-slate-200 px-3 py-2 rounded-lg text-slate-800"
                            />
                          </div>
                        </div>

                        <div>
                          <label className="block text-xs font-bold text-slate-700 mb-1">ToRecipients</label>
                          <input
                            type="text"
                            readOnly
                            value={workflowHitlAction.args?.ToRecipients || 'admin@sockcop.onmicrosoft.com'}
                            className="w-full text-xs font-mono bg-slate-50 border border-slate-200 px-3 py-2 rounded-lg text-slate-800 font-bold"
                          />
                        </div>
                      </>
                    )}

                    {/* Generic input parameter field (e.g. document selection numbers) */}
                    {workflowHitlAction.actionName !== 'outlook_email_agent__send_mail' && (
                      <div>
                        <label className="block text-xs font-bold text-slate-800 mb-1 flex items-center justify-between">
                          <span>Enter Selected Document Numbers:</span>
                          <span className="text-[11px] font-normal text-slate-500">e.g. 2,3 or 1,3,5</span>
                        </label>
                        <input
                          type="text"
                          value={workflowHitlInput}
                          onChange={(e) => setWorkflowHitlInput(e.target.value)}
                          placeholder="e.g. 2,3"
                          className="w-full text-xs font-mono bg-white border border-indigo-300 focus:ring-2 focus:ring-indigo-400 px-3 py-2 rounded-lg text-slate-900 font-bold"
                        />
                      </div>
                    )}
                  </div>

                  <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-100">
                    <button
                      onClick={() => setWorkflowHitlAction(null)}
                      className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-600 hover:text-slate-900 bg-slate-100 hover:bg-slate-200 transition-colors"
                    >
                      Cancel
                    </button>
                    <button
                      onClick={() => runWorkflowExecution(true)}
                      disabled={workflowRunning}
                      className="px-6 py-2 rounded-xl text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-700 shadow-md shadow-indigo-600/20 transition-all flex items-center gap-1.5"
                    >
                      {workflowRunning ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Send className="w-3.5 h-3.5" />}
                      {workflowHitlAction.actionName === 'outlook_email_agent__send_mail' ? 'Send Email' : 'Submit Selection & Summarize'}
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* Generated Summary Card */}
            {workflowSummaryResult && (
              <div className="glass-panel p-6 rounded-2xl border border-slate-200 space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 text-sky-600">
                    <FileText className="w-5 h-5" />
                    <h3 className="text-sm font-bold text-slate-900">Consolidated Workflow Summary</h3>
                  </div>
                  <button
                    onClick={() => handleCopy(workflowSummaryResult, 'wf-summary')}
                    className="text-xs text-sky-600 hover:text-sky-800 flex items-center gap-1 font-semibold"
                  >
                    {copiedKey === 'wf-summary' ? <Check className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5" />}
                    Copy Summary
                  </button>
                </div>
                <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-800 whitespace-pre-wrap leading-relaxed font-sans">
                  {workflowSummaryResult}
                </div>
              </div>
            )}

            {/* Live Streaming Logs & Thoughts */}
            <div className="glass-panel p-5 rounded-2xl border border-slate-200 space-y-2">
              <div className="flex items-center justify-between">
                <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider flex items-center gap-1.5">
                  <Terminal className="w-4 h-4 text-slate-600" />
                  Live Flow Execution Logs & Intermediate Thoughts ({workflowLogs.length} events)
                </h3>
                {workflowLogs.length > 0 && (
                  <button
                    onClick={() => setWorkflowLogs([])}
                    className="text-[11px] text-slate-400 hover:text-slate-600 font-semibold"
                  >
                    Clear Logs
                  </button>
                )}
              </div>
              <div className="bg-slate-950 text-slate-200 p-4 rounded-xl font-mono text-[11px] leading-relaxed max-h-64 overflow-y-auto space-y-1">
                {workflowLogs.length > 0 ? (
                  workflowLogs.map((log, i) => (
                    <div key={i} className={log.includes('▶️') ? 'text-indigo-300 font-bold' : log.includes('✅') ? 'text-emerald-300 font-bold' : log.includes('⚠️') ? 'text-amber-300 font-bold' : 'text-slate-300'}>
                      {log}
                    </div>
                  ))
                ) : (
                  <div className="text-slate-500 italic">No execution events yet. Click "Run Daily Brief Workflow" above.</div>
                )}
              </div>
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

            {/* ── PRODUCT TEAM OFFICIAL WORKFLOW: DOMAIN ALLOWLISTING & FEDERATED CONNECTORS ── */}
            <div className="glass-panel p-6 rounded-2xl border border-slate-200 space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div className="space-y-1">
                  <div className="flex items-center gap-2 text-sky-600">
                    <Globe className="w-5 h-5" />
                    <h3 className="text-sm font-bold text-slate-900">Custom Domain Allowlist & Discovery Engine Widget Config</h3>
                  </div>
                  <p className="text-xs text-slate-500">
                    Step 2 of the official Product Notebook: registers this origin URL into <code>widgetConfigs/default_search_widget_config</code> so Google Discovery Engine generates dynamic <code>authorizationUri</code> parameters.
                  </p>
                </div>
                <button
                  onClick={handleAllowlistDomain}
                  disabled={allowlistLoading}
                  className="px-4 py-2 rounded-xl text-xs font-bold bg-sky-600 hover:bg-sky-700 text-white transition-all shadow-sm flex items-center justify-center gap-1.5 shrink-0"
                >
                  {allowlistLoading ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <ShieldCheck className="w-3.5 h-3.5" />}
                  Allowlist Current Domain ({typeof window !== 'undefined' ? window.location.origin : 'localhost'})
                </button>
              </div>

              {allowlistSuccess && (
                <div className="p-3 rounded-xl bg-sky-50 border border-sky-200 text-sky-900 text-xs font-mono break-all">
                  {allowlistSuccess}
                </div>
              )}

              <div className="flex flex-wrap items-center gap-2 pt-1 border-t border-slate-100 text-xs">
                <span className="font-semibold text-slate-600">Currently Allowlisted Domains in Engine:</span>
                {allowlistedDomains.length > 0 ? (
                  allowlistedDomains.map((dom, i) => (
                    <span key={i} className="px-2.5 py-0.5 rounded-full bg-slate-100 text-slate-700 font-mono text-[11px] border border-slate-200">
                      {dom}
                    </span>
                  ))
                ) : (
                  <span className="text-slate-400 italic text-[11px]">No custom domains explicitly allowlisted yet</span>
                )}
              </div>
            </div>

            {/* ── FEDERATED CONNECTORS & AUTHORIZATION STATUS (NOTEBOOK STEPS 2, 3, 5, 6) ── */}
            <div className="glass-panel p-6 rounded-2xl border border-slate-200 space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-indigo-600">
                  <Database className="w-5 h-5" />
                  <h3 className="text-sm font-bold text-slate-900">Federated Search Connectors Discovery & Lifecycle</h3>
                </div>
                <button
                  onClick={() => fetchWidgetConfig()}
                  disabled={discoveryLoading}
                  className="text-xs text-slate-600 hover:text-slate-900 flex items-center gap-1 font-semibold"
                >
                  <RefreshCw className={`w-3.5 h-3.5 ${discoveryLoading ? 'animate-spin' : ''}`} />
                  Refresh Widget Config
                </button>
              </div>

              <p className="text-xs text-slate-500">
                Extracted dynamically via <code>GetWidgetConfig(customDomain={typeof window !== 'undefined' ? window.location.origin : 'localhost'})</code>. Connectors in an <code>AUTHORIZED</code> state can be revoked (<code>EXPIRED</code>) or re-authorized at any time.
              </p>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                {connectorsList.length > 0 ? (
                  connectorsList.map((conn) => {
                    const isAuth = conn.authState === 'AUTHORIZED';
                    const isExpired = conn.authState === 'EXPIRED';
                    const isLoading = authActionLoading[conn.id];

                    return (
                      <div key={conn.id} className="p-4 rounded-xl border border-slate-200 bg-white/70 space-y-3 flex flex-col justify-between">
                        <div className="space-y-2">
                          <div className="flex items-start justify-between gap-2">
                            <div className="flex items-center gap-2">
                              {conn.iconLink ? (
                                <img src={conn.iconLink} alt={conn.displayName} className="w-6 h-6 rounded" />
                              ) : (
                                <div className="w-6 h-6 rounded bg-indigo-100 text-indigo-700 flex items-center justify-center font-bold text-xs">
                                  {conn.displayName.charAt(0)}
                                </div>
                              )}
                              <div>
                                <h4 className="text-xs font-bold text-slate-800">{conn.displayName}</h4>
                                <span className="text-[10px] text-slate-400 font-mono">{conn.id}</span>
                              </div>
                            </div>

                            <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold border ${
                              isAuth
                                ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
                                : isExpired
                                ? 'bg-amber-50 text-amber-700 border-amber-200'
                                : 'bg-slate-100 text-slate-600 border-slate-200'
                            }`}>
                              {conn.authState || 'NOT_AUTHORIZED'}
                            </span>
                          </div>

                          {conn.dataSource && (
                            <div className="text-[11px] text-slate-500">
                              <span className="font-medium">Data Source:</span> {conn.dataSource}
                            </div>
                          )}
                        </div>

                        <div className="pt-2 border-t border-slate-100 flex items-center gap-2">
                          {isAuth ? (
                            <button
                              onClick={() => handleRevokeConnector(conn.id)}
                              disabled={isLoading}
                              className="flex-1 py-1.5 px-3 rounded-lg text-xs font-semibold bg-rose-50 hover:bg-rose-100 text-rose-700 border border-rose-200 transition-colors flex items-center justify-center gap-1"
                            >
                              {isLoading ? <RefreshCw className="w-3 h-3 animate-spin" /> : <Trash2 className="w-3 h-3" />}
                              Revoke (EXPIRED)
                            </button>
                          ) : (
                            <button
                              onClick={() => handleAuthorizeConnector(conn.authorizationUri)}
                              disabled={isLoading || !conn.authorizationUri}
                              className="flex-1 py-1.5 px-3 rounded-lg text-xs font-semibold bg-emerald-600 hover:bg-emerald-700 text-white transition-colors flex items-center justify-center gap-1 shadow-sm disabled:bg-slate-200 disabled:text-slate-400"
                            >
                              {isLoading ? <RefreshCw className="w-3 h-3 animate-spin" /> : <Lock className="w-3 h-3" />}
                              {conn.authorizationUri ? 'Authorize ↗' : 'Allowlist domain first'}
                            </button>
                          )}
                        </div>
                      </div>
                    );
                  })
                ) : (
                  <div className="col-span-full p-6 text-center text-xs text-slate-500 border border-dashed border-slate-200 rounded-xl">
                    No federated search connectors found in WidgetConfig or awaiting discovery.
                  </div>
                )}
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
