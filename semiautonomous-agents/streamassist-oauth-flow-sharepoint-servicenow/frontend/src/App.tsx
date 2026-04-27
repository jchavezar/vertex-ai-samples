import { useState, useCallback, useEffect, useRef } from 'react';
import { useMsal, useIsAuthenticated } from '@azure/msal-react';
import { loginRequest } from './authConfig';

type ConnectorName = 'sharepoint' | 'servicenow';

interface ConnectorMeta {
  enabled: boolean;
  label: string;
}

interface ConnectorState {
  connected: boolean;     // refresh token is stored in DE for this user
  active: boolean;        // include in search
  authInProgress: boolean;
  authStatus: string;
}

interface Source {
  title: string;
  url: string;
  description: string;
  file_type: string;
  author: string;
  entity_type: string;
  connector?: ConnectorName;
  snippets?: string[];
}

interface Message {
  role: 'user' | 'assistant';
  text: string;
  sources?: Source[];
  duration_ms?: number;
  ungrounded?: boolean;
}

interface TraceEntry {
  id: string;
  stage: string;
  status: 'pending' | 'success' | 'error';
  timestamp: number;
  duration_ms?: number;
  input?: any;
  output?: any;
  description?: string;
}

const CONNECTOR_LABEL: Record<ConnectorName, string> = {
  sharepoint: 'SharePoint',
  servicenow: 'ServiceNow',
};

const PLACEHOLDER: Record<ConnectorName, string> = {
  sharepoint: 'contracts, reports, or any document in your SharePoint site',
  servicenow: 'incidents, knowledge articles, or catalog items in your ServiceNow instance',
};

const STAGE_INFO: Record<string, { description: string; chain?: string }> = {
  'MSAL Login': {
    description: 'Authenticates against the Portal App registration in Entra ID. The id_token\'s aud claim must match the WIF provider\'s audience (api://{client-id}).',
    chain: 'A',
  },
  'List Connectors': {
    description: 'Asks the backend which connectors are enabled in this deployment (SharePoint, ServiceNow, or both).',
  },
  'Check Connection': {
    description: 'Calls acquireAccessToken via WIF to check if a stored refresh token exists for this user. 404 means no token, or it was stored under a different identity.',
  },
  'STS Token Exchange': {
    description: 'Exchanges the Entra JWT for a GCP access token via Workforce Identity Federation. Maps Entra sub → GCP principal.',
    chain: 'A',
  },
  'acquireAccessToken': {
    description: 'Discovery Engine checks if it holds a stored connector refresh token for this WIF identity.',
    chain: 'A',
  },
  'Get Auth URL': {
    description: 'Generates the IdP OAuth consent URL. Stores the Entra JWT by nonce so the callback can retrieve it.',
    chain: 'B',
  },
  'OAuth Consent Popup': {
    description: 'Opens the IdP login for connector consent. Redirect goes to vertexaisearch.cloud.google.com/oauth-redirect, which captures the auth code.',
    chain: 'B',
  },
  'OAuth Redirect (postMessage)': {
    description: 'Google\'s redirect page receives the auth code and posts {fullRedirectUrl} back to the opener via postMessage.',
    chain: 'B',
  },
  'acquireAndStoreRefreshToken': {
    description: 'CONVERGENCE — Chain A (WIF identity) meets Chain B (auth code). DE stores the connector refresh token mapped to this WIF identity.',
    chain: 'A+B',
  },
  'Search': {
    description: 'Calls StreamAssist with dataStoreSpecs from every active connector. Per-user ACLs are enforced via the stored refresh tokens.',
  },
  'StreamAssist': {
    description: 'Federated real-time search across the selected connectors\' data stores. Requires natural language queries.',
  },
};

export default function App() {
  const { instance, accounts } = useMsal();
  const isAuthenticated = useIsAuthenticated();
  const username = accounts[0]?.username || '';

  const [connectors, setConnectors] = useState<Record<string, ConnectorMeta>>({});
  const [connState, setConnState] = useState<Record<string, ConnectorState>>({});
  const [connectorsLoaded, setConnectorsLoaded] = useState(false);
  const [connectionChecked, setConnectionChecked] = useState(false);
  const [webGrounding, setWebGrounding] = useState(false);
  const [webGroundingBusy, setWebGroundingBusy] = useState(false);

  const [messages, setMessages] = useState<Message[]>([]);
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessionToken, setSessionToken] = useState<string | null>(null);
  const [traces, setTraces] = useState<TraceEntry[]>([]);
  const [showDebug, setShowDebug] = useState(true);
  const [expandedTraces, setExpandedTraces] = useState<Set<string>>(new Set());
  const [elapsedMs, setElapsedMs] = useState(0);

  const consentPopupRefs = useRef<Record<string, Window | null>>({});
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const traceEndRef = useRef<HTMLDivElement>(null);
  const searchStartRef = useRef<number>(0);

  useEffect(() => { messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [messages, loading]);
  useEffect(() => { traceEndRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [traces]);

  useEffect(() => {
    if (!loading) return;
    const id = setInterval(() => setElapsedMs(Date.now() - searchStartRef.current), 50);
    return () => clearInterval(id);
  }, [loading]);

  // ─── Trace helpers ─────────────────────────────────────────
  const addTrace = useCallback((stage: string, input?: any): string => {
    const id = crypto.randomUUID();
    setTraces(prev => [...prev, { id, stage, status: 'pending', timestamp: Date.now(), input }]);
    setExpandedTraces(prev => new Set(prev).add(id));
    return id;
  }, []);

  const updateTrace = useCallback((id: string, updates: Partial<TraceEntry>) => {
    setTraces(prev => prev.map(t => t.id === id ? { ...t, ...updates } : t));
  }, []);

  const addBackendTraces = useCallback((backendTrace: any[]) => {
    if (!backendTrace?.length) return;
    const newTraces: TraceEntry[] = backendTrace.map(t => ({
      id: crypto.randomUUID(),
      stage: t.stage,
      status: t.status < 300 ? 'success' : 'error',
      timestamp: Date.now(),
      duration_ms: t.duration_ms,
      input: t.input,
      output: t.output,
    }));
    setTraces(prev => [...prev, ...newTraces]);
  }, []);

  const toggleTrace = useCallback((id: string) => {
    setExpandedTraces(prev => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  }, []);

  // ─── Token acquisition ────────────────────────────────────
  const getToken = useCallback(async (silent = true): Promise<string | null> => {
    if (!accounts[0]) return null;
    try {
      const resp = await instance.acquireTokenSilent({ ...loginRequest, account: accounts[0] });
      return resp.idToken;
    } catch {
      if (silent) return null;
      try {
        return (await instance.acquireTokenPopup(loginRequest)).idToken;
      } catch {
        return null;
      }
    }
  }, [instance, accounts]);

  const handleLogin = async () => {
    const traceId = addTrace('MSAL Login', { scopes: loginRequest.scopes });
    const start = Date.now();
    try {
      const resp = await instance.loginPopup(loginRequest);
      updateTrace(traceId, {
        status: 'success',
        duration_ms: Date.now() - start,
        output: {
          account: resp.account?.name,
          username: resp.account?.username,
          idToken: resp.idToken.substring(0, 50) + '...',
          tenantId: resp.account?.tenantId,
        },
      });
    } catch (err: any) {
      updateTrace(traceId, { status: 'error', duration_ms: Date.now() - start, output: { error: err.message } });
    }
  };

  // ─── Per-connector localStorage keys ──────────────────────
  const connKey = (name: string) => `connected_${name}_${username}`;
  const activeKey = (name: string) => `active_${name}_${username}`;

  const setConn = (name: string, patch: Partial<ConnectorState>) => {
    setConnState(prev => ({ ...prev, [name]: { ...prev[name], ...patch } }));
  };

  // ─── Discover enabled connectors ──────────────────────────
  useEffect(() => {
    (async () => {
      const traceId = addTrace('List Connectors', { endpoint: 'GET /api/connectors' });
      const start = Date.now();
      try {
        const resp = await fetch('/api/connectors');
        const data: Record<string, ConnectorMeta> = await resp.json();
        setConnectors(data);
        const initial: Record<string, ConnectorState> = {};
        Object.keys(data).forEach(name => {
          initial[name] = {
            connected: false,
            active: localStorage.getItem(activeKey(name)) !== '0',  // default ON
            authInProgress: false,
            authStatus: '',
          };
        });
        setConnState(initial);
        setConnectorsLoaded(true);
        updateTrace(traceId, { status: 'success', duration_ms: Date.now() - start, output: data });
        // Fetch current web-grounding state too (no auth needed; backend uses ADC)
        try {
          const wgResp = await fetch('/api/grounding/web');
          const wg = await wgResp.json();
          setWebGrounding(!!wg.enabled);
        } catch { /* ignore */ }
      } catch (err: any) {
        setConnectorsLoaded(true);
        updateTrace(traceId, { status: 'error', duration_ms: Date.now() - start, output: { error: err.message } });
      }
    })();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // ─── postMessage handler (OAuth callback) ─────────────────
  useEffect(() => {
    const handler = async (event: MessageEvent) => {
      // Vertex's redirect page posts {fullRedirectUrl}
      if (event.data?.fullRedirectUrl) {
        const traceId = addTrace('OAuth Redirect (postMessage)', {
          fullRedirectUrl: event.data.fullRedirectUrl.substring(0, 80) + '...',
        });
        const start = Date.now();
        try {
          const token = await getToken();
          const resp = await fetch('/api/oauth/exchange', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              ...(token ? { 'X-Entra-Id-Token': token } : {}),
            },
            body: JSON.stringify({ fullRedirectUrl: event.data.fullRedirectUrl }),
          });
          const data = await resp.json();
          const connector: ConnectorName | undefined = data.connector;
          if (data.success && connector) {
            setConn(connector, { connected: true, authInProgress: false, authStatus: '' });
            localStorage.setItem(connKey(connector), '1');
            updateTrace(traceId, { status: 'success', duration_ms: Date.now() - start, output: { success: true, connector } });
          } else if (connector) {
            setConn(connector, { authInProgress: false, authStatus: `Authorization failed: ${data.error || 'Unknown'}` });
            updateTrace(traceId, { status: 'error', duration_ms: Date.now() - start, output: { error: data.error, connector } });
          } else {
            updateTrace(traceId, { status: 'error', duration_ms: Date.now() - start, output: { error: 'No connector returned' } });
          }
          addBackendTraces(data._trace);
        } catch (err: any) {
          updateTrace(traceId, { status: 'error', duration_ms: Date.now() - start, output: { error: err.message } });
        }
        return;
      }

      // Legacy callback page postMessage path
      const t: string = event.data?.type || '';
      if (t.endsWith('-oauth-callback')) {
        const connector = (event.data?.connector || t.replace('-oauth-callback', '')) as ConnectorName;
        if (event.data.success) {
          setConn(connector, { connected: true, authInProgress: false, authStatus: '' });
          localStorage.setItem(connKey(connector), '1');
          setTraces(prev => [...prev, {
            id: crypto.randomUUID(), stage: 'OAuth Callback (postMessage)', status: 'success',
            timestamp: Date.now(), input: { type: event.data.type }, output: { success: true, connector },
          }]);
        } else {
          setConn(connector, { authInProgress: false, authStatus: `Authorization failed: ${event.data.error || 'Unknown'}` });
          setTraces(prev => [...prev, {
            id: crypto.randomUUID(), stage: 'OAuth Callback (postMessage)', status: 'error',
            timestamp: Date.now(), input: { type: event.data.type }, output: { error: event.data.error, connector },
          }]);
        }
      }
    };
    window.addEventListener('message', handler);
    return () => window.removeEventListener('message', handler);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [username, getToken, addBackendTraces, updateTrace, addTrace]);

  // ─── Check connection on mount, per connector ─────────────
  useEffect(() => {
    if (!isAuthenticated || !connectorsLoaded) return;
    (async () => {
      const token = await getToken();
      if (!token) { setConnectionChecked(true); return; }

      await Promise.all(Object.keys(connectors).map(async (name) => {
        const traceId = addTrace('Check Connection', {
          endpoint: `/api/${name}/check-connection`,
          connector: name,
          idToken: token.substring(0, 30) + '...',
        });
        const start = Date.now();
        try {
          const resp = await fetch(`/api/${name}/check-connection`, { headers: { 'X-Entra-Id-Token': token } });
          const data = await resp.json();
          setConn(name, { connected: !!data.connected });
          data.connected ? localStorage.setItem(connKey(name), '1') : localStorage.removeItem(connKey(name));
          updateTrace(traceId, {
            status: data.connected ? 'success' : 'error',
            duration_ms: Date.now() - start,
            output: { connected: data.connected, connector: name },
          });
          addBackendTraces(data._trace);
        } catch (err: any) {
          setConn(name, { connected: false });
          updateTrace(traceId, { status: 'error', duration_ms: Date.now() - start, output: { error: err.message } });
        }
      }));
      setConnectionChecked(true);
    })();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAuthenticated, connectorsLoaded, username]);

  // ─── Poll for popup closure (per connector) ───────────────
  useEffect(() => {
    const intervals: Record<string, ReturnType<typeof setInterval>> = {};
    Object.keys(connState).forEach(name => {
      const st = connState[name];
      if (!st?.authInProgress || !consentPopupRefs.current[name]) return;
      intervals[name] = setInterval(async () => {
        const popup = consentPopupRefs.current[name];
        if (!popup || popup.closed) {
          clearInterval(intervals[name]);
          consentPopupRefs.current[name] = null;
          await new Promise(r => setTimeout(r, 1500));
          const token = await getToken();
          if (token) {
            const resp = await fetch(`/api/${name}/check-connection`, { headers: { 'X-Entra-Id-Token': token } });
            const data = await resp.json();
            if (data.connected) {
              setConn(name, { connected: true });
              localStorage.setItem(connKey(name), '1');
            }
            addBackendTraces(data._trace);
          }
          setConn(name, { authInProgress: false, authStatus: '' });
        }
      }, 500);
    });
    return () => { Object.values(intervals).forEach(clearInterval); };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [connState, getToken]);

  // ─── Connect a connector (open consent popup) ─────────────
  const handleConnect = async (name: string) => {
    setConn(name, { authInProgress: true, authStatus: 'Opening consent...' });
    const popup = window.open('about:blank', `${name}_consent`, 'width=600,height=700,left=200,top=100');
    consentPopupRefs.current[name] = popup;
    if (!popup) {
      setConn(name, { authInProgress: false, authStatus: 'Popup blocked. Please allow popups.' });
      return;
    }
    try {
      const token = await getToken();
      const hint = username ? `?login_hint=${encodeURIComponent(username)}` : '';
      const traceId = addTrace('Get Auth URL', {
        endpoint: `/api/${name}/auth-url${hint}`,
        connector: name,
        idToken: token?.substring(0, 30) + '...',
      });
      const start = Date.now();
      const resp = await fetch(`/api/${name}/auth-url${hint}`, { headers: token ? { 'X-Entra-Id-Token': token } : {} });
      const data = await resp.json();
      updateTrace(traceId, {
        status: data.auth_url ? 'success' : 'error',
        duration_ms: Date.now() - start,
        output: data.auth_url ? { auth_url: data.auth_url.substring(0, 80) + '...' } : { error: data.error },
      });

      if (data.auth_url) {
        popup.location.href = data.auth_url;
        setConn(name, { authStatus: 'Complete consent in the popup...' });
        addTrace('OAuth Consent Popup', { connector: name, redirectTo: data.auth_url.substring(0, 80) + '...' });
      } else {
        popup.close();
        setConn(name, { authInProgress: false, authStatus: data.error || 'Failed to get auth URL' });
      }
    } catch (err: any) {
      popup.close();
      setConn(name, { authInProgress: false, authStatus: `Failed: ${err.message}` });
    }
  };

  // ─── Toggle: include in search / open consent if needed ───
  const handleToggleActive = async (name: string) => {
    const st = connState[name];
    if (!st) return;

    // Turning ON
    if (!st.active) {
      setConn(name, { active: true });
      localStorage.removeItem(activeKey(name));
      if (!st.connected) await handleConnect(name);
      return;
    }
    // Turning OFF — keep stored token, just exclude from search
    setConn(name, { active: false });
    localStorage.setItem(activeKey(name), '0');
  };

  const handleReconnect = (name: string) => {
    setConn(name, { connected: false });
    localStorage.removeItem(connKey(name));
    handleConnect(name);
  };

  const handleToggleWebGrounding = async () => {
    const target = !webGrounding;
    setWebGroundingBusy(true);
    const traceId = addTrace('Web Grounding Toggle', { target_enabled: target });
    const start = Date.now();
    try {
      const resp = await fetch('/api/grounding/web', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ enabled: target }),
      });
      const data = await resp.json();
      if (data.error) {
        updateTrace(traceId, { status: 'error', duration_ms: Date.now() - start, output: { error: data.error } });
      } else {
        setWebGrounding(!!data.enabled);
        updateTrace(traceId, { status: 'success', duration_ms: Date.now() - start, output: { enabled: data.enabled } });
      }
    } catch (err: any) {
      updateTrace(traceId, { status: 'error', duration_ms: Date.now() - start, output: { error: err.message } });
    } finally {
      setWebGroundingBusy(false);
    }
  };

  // ─── Search across active+connected connectors ────────────
  const handleSearch = async () => {
    const q = query.trim();
    if (!q || loading) return;

    const selected = Object.keys(connState).filter(n => connState[n].active && connState[n].connected);
    if (selected.length === 0) {
      setMessages(prev => [...prev, { role: 'assistant', text: 'No connectors are active. Toggle SharePoint or ServiceNow on (and complete consent) to search.' }]);
      return;
    }

    const token = await getToken();
    if (!token) return;

    setMessages(prev => [...prev, { role: 'user', text: q }]);
    setQuery('');
    setElapsedMs(0);
    searchStartRef.current = Date.now();
    setLoading(true);

    const traceId = addTrace('Search', {
      endpoint: 'POST /api/search',
      query: q,
      connectors: selected,
      session_token: sessionToken,
      idToken: token.substring(0, 30) + '...',
    });
    const start = searchStartRef.current;

    try {
      const resp = await fetch('/api/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-Entra-Id-Token': token },
        body: JSON.stringify({ query: q, session_token: sessionToken, connectors: selected }),
      });
      const data = await resp.json();
      const elapsed = Date.now() - start;

      if (data.error) {
        setMessages(prev => [...prev, { role: 'assistant', text: `Error: ${data.error}`, duration_ms: elapsed }]);
        updateTrace(traceId, { status: 'error', duration_ms: elapsed, output: { error: data.error } });
      } else {
        setMessages(prev => [...prev, {
          role: 'assistant',
          text: data.answer || 'No answer generated.',
          sources: data.sources,
          duration_ms: elapsed,
          ungrounded: data.ungrounded,
        }]);
        updateTrace(traceId, {
          status: 'success',
          duration_ms: elapsed,
          output: { answer_length: data.answer?.length, sources_count: data.sources?.length, session_token: data.session_token },
        });
        if (data.session_token) setSessionToken(data.session_token);
      }
      addBackendTraces(data._trace);
    } catch (err: any) {
      const elapsed = Date.now() - start;
      setMessages(prev => [...prev, { role: 'assistant', text: `Network error: ${err.message}`, duration_ms: elapsed }]);
      updateTrace(traceId, { status: 'error', duration_ms: elapsed, output: { error: err.message } });
    } finally {
      setLoading(false);
    }
  };

  // ─── UI helpers ───────────────────────────────────────────
  const fmtElapsed = (ms: number) => (ms < 1000 ? `${ms} ms` : `${(ms / 1000).toFixed(2)} s`);

  const renderMarkdown = (text: string) => {
    const lines = text.split('\n');
    const elements: JSX.Element[] = [];
    let listItems: string[] = [];
    let listType: 'ul' | 'ol' | null = null;

    const fmt = (s: string) =>
      s.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.+?)\*/g, '<em>$1</em>')
        .replace(/`(.+?)`/g, '<code>$1</code>');

    const flushList = () => {
      if (listItems.length > 0 && listType) {
        const Tag = listType;
        elements.push(
          <Tag key={elements.length}>
            {listItems.map((item, i) => <li key={i} dangerouslySetInnerHTML={{ __html: fmt(item) }} />)}
          </Tag>
        );
        listItems = [];
        listType = null;
      }
    };

    for (const line of lines) {
      const t = line.trim();
      if (/^[-*]\s/.test(t)) {
        if (listType !== 'ul') flushList();
        listType = 'ul';
        listItems.push(t.replace(/^[-*]\s+/, ''));
      } else if (/^\d+\.\s/.test(t)) {
        if (listType !== 'ol') flushList();
        listType = 'ol';
        listItems.push(t.replace(/^\d+\.\s+/, ''));
      } else {
        flushList();
        if (!t) continue;
        if (t.startsWith('## '))
          elements.push(<h3 key={elements.length} dangerouslySetInnerHTML={{ __html: fmt(t.slice(3)) }} />);
        else if (t.startsWith('### '))
          elements.push(<h4 key={elements.length} dangerouslySetInnerHTML={{ __html: fmt(t.slice(4)) }} />);
        else
          elements.push(<p key={elements.length} dangerouslySetInnerHTML={{ __html: fmt(t) }} />);
      }
    }
    flushList();
    return elements;
  };

  const fileIcon = (type: string) =>
    ({ pdf: '\u{1F4C4}', docx: '\u{1F4DD}', pptx: '\u{1F4CA}', xlsx: '\u{1F4CA}' }[type] || '\u{1F4C1}');

  // Snippets come back with [[term]] markers around highlighted spans.
  const renderSnippet = (raw: string) => {
    const parts = raw.split(/\[\[(.+?)\]\]/g);
    return parts.map((p, i) =>
      i % 2 === 1
        ? <mark key={i}>{p}</mark>
        : <span key={i}>{p}</span>
    );
  };

  const statusIcon = (s: TraceEntry['status']) =>
    s === 'success' ? '✓' : s === 'error' ? '✗' : '●';

  const formatJson = (obj: any) => JSON.stringify(obj, null, 2);

  // ─── Computed labels ──────────────────────────────────────
  const activeConnected = Object.keys(connState).filter(n => connState[n].active && connState[n].connected);
  const activeNames = activeConnected.map(n => CONNECTOR_LABEL[n as ConnectorName] || n);
  const placeholderText = activeConnected.length === 1
    ? `Ask about ${PLACEHOLDER[activeConnected[0] as ConnectorName] || activeConnected[0]}...`
    : `Ask about ${activeNames.join(' & ')}...`;
  const emptyHeading = activeConnected.length === 0
    ? 'No connectors active'
    : `Search ${activeNames.join(' + ')}`;
  const emptyHint = activeConnected.length === 0
    ? 'Toggle SharePoint or ServiceNow on above to start searching.'
    : `Federated search across ${activeNames.join(' and ')} with per-user ACLs.`;
  const loadingLabel = activeConnected.length === 1
    ? `Searching ${activeNames[0]}...`
    : `Searching ${activeNames.join(' + ')}...`;

  return (
    <div className={`app-layout ${showDebug ? 'with-sidebar' : ''}`}>
      <div className="app">
        <header>
          <h1>Enterprise Portal</h1>
          <span className="subtitle">Powered by Gemini Enterprise StreamAssist</span>
          {isAuthenticated && (
            <div className="user-info">
              {username}
              <button className="btn-small" onClick={async () => {
                setSessionToken(null);
                setMessages([]);
                setTraces([]);
                setExpandedTraces(new Set());
                setConnectionChecked(false);
                Object.keys(connectors).forEach(n => localStorage.removeItem(connKey(n)));

                let token: string | null = null;
                try {
                  if (accounts[0]) {
                    await instance.acquireTokenSilent({ ...loginRequest, account: accounts[0], forceRefresh: true });
                    token = (await instance.acquireTokenSilent({ ...loginRequest, account: accounts[0] })).idToken;
                  }
                } catch {
                  try { token = (await instance.acquireTokenPopup(loginRequest)).idToken; } catch { /* cancelled */ }
                }

                if (token) {
                  await Promise.all(Object.keys(connectors).map(async (name) => {
                    const resp = await fetch(`/api/${name}/check-connection`, { headers: { 'X-Entra-Id-Token': token! } });
                    const data = await resp.json();
                    setConn(name, { connected: !!data.connected });
                    data.connected ? localStorage.setItem(connKey(name), '1') : localStorage.removeItem(connKey(name));
                    addBackendTraces(data._trace);
                  }));
                }
                setConnectionChecked(true);
              }}>Clear Session</button>
              <button className="btn-small" onClick={() => instance.logoutPopup()}>Logout</button>
            </div>
          )}
          <button
            className={`btn-debug ${showDebug ? 'active' : ''}`}
            onClick={() => setShowDebug(!showDebug)}
            title="Toggle debug sidebar"
          >
            {showDebug ? '«' : '»'} Pipeline
          </button>
        </header>

        {!isAuthenticated && (
          <section className="card login-card">
            <h2>Sign in to get started</h2>
            <p>Sign in with your Microsoft account to search SharePoint and ServiceNow.</p>
            <button className="btn-primary" onClick={handleLogin}>Sign in with Microsoft</button>
          </section>
        )}

        {isAuthenticated && (!connectorsLoaded || !connectionChecked) && (
          <div className="empty-state" style={{ marginTop: 80 }}>
            <div className="dot-pulse" />
            <p>Checking connectors...</p>
          </div>
        )}

        {isAuthenticated && connectorsLoaded && connectionChecked && (
          <>
            <div className="connector-bar">
              {Object.keys(connectors).map(name => {
                const st = connState[name];
                if (!st) return null;
                const label = connectors[name].label || CONNECTOR_LABEL[name as ConnectorName] || name;
                return (
                  <div key={name} className={`connector-chip ${st.active ? 'on' : 'off'} ${st.connected ? 'connected' : 'disconnected'}`}>
                    <label className="switch">
                      <input
                        type="checkbox"
                        checked={st.active}
                        onChange={() => handleToggleActive(name)}
                        disabled={st.authInProgress}
                      />
                      <span className="slider" />
                    </label>
                    <span className="connector-label">{label}</span>
                    <span className="connector-status">
                      {st.authInProgress ? 'Authorizing…'
                        : st.connected ? (st.active ? 'Active' : 'Standby')
                        : (st.active ? 'Needs consent' : 'Off')}
                    </span>
                    {st.connected ? (
                      <button className="btn-small" onClick={() => handleReconnect(name)} title="Re-authorize" disabled={st.authInProgress}>↻</button>
                    ) : (
                      <button className="btn-small btn-connect" onClick={() => handleConnect(name)} disabled={st.authInProgress}>
                        {st.authInProgress ? 'Authorizing…' : 'Connect'}
                      </button>
                    )}
                    {st.authStatus && <span className="auth-status">{st.authStatus}</span>}
                  </div>
                );
              })}

              <div className={`connector-chip web-grounding-chip ${webGrounding ? 'on connected' : 'off'}`}>
                <label className="switch">
                  <input
                    type="checkbox"
                    checked={webGrounding}
                    onChange={handleToggleWebGrounding}
                    disabled={webGroundingBusy}
                  />
                  <span className="slider" />
                </label>
                <span className="google-g" aria-hidden>
                  <svg viewBox="0 0 24 24" width="18" height="18">
                    <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                    <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.99.66-2.26 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                    <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                    <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                  </svg>
                </span>
                <span className="connector-label">Google Search</span>
                <span className="connector-status">
                  {webGroundingBusy ? 'Updating…' : webGrounding ? 'Augmenting' : 'Off'}
                </span>
              </div>
            </div>

            {Object.keys(connectors).some(n => connState[n]?.active && !connState[n]?.connected) && (
              <div className="auth-banner">
                <div className="auth-banner-content">
                  <span>One or more connectors require a one-time authorization to access your data.</span>
                  <span style={{ fontSize: '0.78rem', color: 'var(--text-dim)' }}>
                    Click <strong>Connect</strong> on each chip to start consent.
                  </span>
                </div>
              </div>
            )}

            <div className="search-container">
              <div className="messages-area">
                {messages.length === 0 && !loading && (
                  <div className="empty-state">
                    <div className="empty-icon">
                      <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                        <circle cx="11" cy="11" r="8" /><path d="m21 21-4.35-4.35" />
                      </svg>
                    </div>
                    <p>{emptyHeading}</p>
                    <span className="empty-hint">{emptyHint}</span>
                  </div>
                )}

                {messages.map((msg, i) => (
                  <div key={i} className={`message message-${msg.role}`}>
                    {msg.role === 'assistant' && <div className="avatar avatar-ai">G</div>}
                    <div className="message-bubble">
                      {msg.role === 'assistant' && msg.duration_ms !== undefined && (
                        <div style={{ fontSize: '0.72rem', color: '#8b95a8', marginBottom: '4px', fontFamily: 'monospace' }}>
                          ⏱ {fmtElapsed(msg.duration_ms)}
                        </div>
                      )}
                      {msg.role === 'assistant' && msg.ungrounded && (
                        <div className="ungrounded-warning">
                          ⚠ <strong>No matching documents</strong> in the active connector(s) ({activeNames.join(' + ')}).
                          The answer below is ungrounded (model fallback / training knowledge). Toggle the right connector or rephrase.
                        </div>
                      )}
                      <div className="message-text">{msg.role === 'assistant' ? renderMarkdown(msg.text) : msg.text}</div>
                      {msg.sources && msg.sources.length > 0 && (
                        <div className="sources">
                          <h4>Sources</h4>
                          <div className="source-cards">
                            {msg.sources.map((src, j) => {
                              const srcLabel = src.connector
                                ? CONNECTOR_LABEL[src.connector] || src.connector
                                : 'Source';
                              const connClass = src.connector ? `conn-${src.connector}` : '';
                              return (
                                <div key={j} className={`source-card ${connClass}`}>
                                  <a href={src.url} target="_blank" rel="noopener noreferrer" className="source-card-head">
                                    <span className="source-icon">{fileIcon(src.file_type)}</span>
                                    <div className="source-info">
                                      <span className="source-title">{src.title}</span>
                                      {src.description && <span className="source-desc">{src.description}</span>}
                                      <span className="source-meta">
                                        <span className={`conn-badge ${connClass}`}>{srcLabel}</span>
                                        {src.entity_type && <span className="meta-pill">{src.entity_type}</span>}
                                        {src.file_type && <span className="meta-pill">{src.file_type.toUpperCase()}</span>}
                                      </span>
                                    </div>
                                  </a>
                                  {src.snippets && src.snippets.length > 0 && (
                                    <div className="snippets">
                                      {src.snippets.map((snip, si) => (
                                        <div key={si} className="snippet-bubble">{renderSnippet(snip)}</div>
                                      ))}
                                    </div>
                                  )}
                                </div>
                              );
                            })}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                ))}

                {loading && (
                  <div className="message message-assistant">
                    <div className="avatar avatar-ai">G</div>
                    <div className="message-bubble">
                      <div className="loading-bubble">
                        <div className="dot-pulse" />
                        <span>{loadingLabel}</span>
                        <span style={{ marginLeft: 'auto', fontFamily: 'monospace', fontSize: '0.85rem', color: '#8b95a8' }}>
                          ⏱ {fmtElapsed(elapsedMs)}
                        </span>
                      </div>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>

              <form className="search-input" onSubmit={(e) => { e.preventDefault(); handleSearch(); }}>
                <input
                  type="text" value={query} onChange={(e) => setQuery(e.target.value)}
                  placeholder={placeholderText} disabled={loading || activeConnected.length === 0}
                />
                <button type="submit" className="btn-primary btn-search" disabled={loading || !query.trim() || activeConnected.length === 0}>
                  {loading ? 'Searching...' : 'Search'}
                </button>
              </form>
            </div>
          </>
        )}
      </div>

      {showDebug && (
        <aside className="debug-sidebar">
          <div className="sidebar-header">
            <h3>Auth Pipeline</h3>
            <button className="btn-small" onClick={() => { setTraces([]); setExpandedTraces(new Set()); }}>Clear</button>
          </div>
          <details className="flow-overview">
            <summary>How It Works — Two-Chain Convergence</summary>
            <div className="flow-content">
              <pre className="flow-ascii">{`Chain A (Identity)          Chain B (Consent)
─────────────────          ──────────────────
MSAL Login                 Connect SP / SN
    │                           │
Entra id_token             OAuth popup
    │                       (Connector App)
STS Exchange                    │
(WIF Pool)                 IdP login
    │                       + consent
GCP access token                │
    │                      auth code via
    │                      redirect page
    │                           │
    └────────┐    ┌─────────────┘
             ▼    ▼
   acquireAndStoreRefreshToken
   (per connector — token mapped
    to this WIF identity)
             │
     stored refresh token
             │
     StreamAssist Search
   (federated across active
    connectors, per-user ACLs)`}</pre>
              <div className="flow-gotchas">
                <div className="gotcha"><span className="gotcha-icon">!</span> <strong>redirect_uri</strong> must be <code>vertexaisearch.cloud.google.com/oauth-redirect</code></div>
                <div className="gotcha"><span className="gotcha-icon">!</span> <strong>WIF token, not ADC</strong> — ADC tokens cause identity mismatch (acquireAccessToken → 404)</div>
                <div className="gotcha"><span className="gotcha-icon">!</span> <strong>COOP blocks postMessage</strong> from cross-origin popups — use popup-closed polling as fallback</div>
                <div className="gotcha"><span className="gotcha-icon">!</span> <strong>Toggle OFF</strong> only excludes from search — the refresh token stays stored. Click ↻ to re-authorize.</div>
                <div className="gotcha"><span className="gotcha-icon">!</span> <strong>Natural language only</strong> — keyword queries return <code>NON_ASSIST_SEEKING_QUERY_IGNORED</code></div>
              </div>
            </div>
          </details>
          {traces.length === 0 && (
            <div className="sidebar-empty">
              <p>No traces yet.</p>
              <p className="sidebar-hint">Sign in to see the auth pipeline in action.</p>
            </div>
          )}
          <div className="trace-list">
            {traces.map((trace) => {
              const info = STAGE_INFO[trace.stage];
              return (
                <div key={trace.id} className={`trace-entry trace-${trace.status}`} onClick={() => toggleTrace(trace.id)}>
                  <div className="trace-header">
                    <span className={`trace-status-icon trace-icon-${trace.status}`}>{statusIcon(trace.status)}</span>
                    {info?.chain && <span className={`trace-chain chain-${info.chain.replace('+', '')}`}>{info.chain}</span>}
                    <span className="trace-stage">{trace.stage}</span>
                    {trace.duration_ms != null && <span className="trace-duration">{trace.duration_ms}ms</span>}
                    <span className="trace-chevron">{expandedTraces.has(trace.id) ? '▼' : '▶'}</span>
                  </div>
                  {expandedTraces.has(trace.id) && (
                    <div className="trace-body">
                      {info?.description && <div className="trace-description">{info.description}</div>}
                      {trace.input && (
                        <div className="trace-section">
                          <div className="trace-label">INPUT</div>
                          <pre className="trace-json">{formatJson(trace.input)}</pre>
                        </div>
                      )}
                      {trace.output && (
                        <div className="trace-section">
                          <div className="trace-label">OUTPUT</div>
                          <pre className="trace-json">{formatJson(trace.output)}</pre>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              );
            })}
            <div ref={traceEndRef} />
          </div>
        </aside>
      )}
    </div>
  );
}
