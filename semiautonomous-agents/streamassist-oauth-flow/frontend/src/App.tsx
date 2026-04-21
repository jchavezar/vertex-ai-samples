import { useState, useCallback, useEffect, useRef } from 'react';
import { useMsal, useIsAuthenticated } from '@azure/msal-react';
import { loginRequest } from './authConfig';

interface Source {
  title: string;
  url: string;
  description: string;
  file_type: string;
  author: string;
  entity_type: string;
}

interface Message {
  role: 'user' | 'assistant';
  text: string;
  sources?: Source[];
  duration_ms?: number;
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

const STAGE_INFO: Record<string, { description: string; chain?: string; exampleInput?: any; exampleOutput?: any }> = {
  'MSAL Login': {
    description: 'Authenticates against the Portal App registration in Entra ID. The id_token\'s aud claim must match the WIF provider\'s audience (api://{client-id}). Requires oauth2AllowIdTokenImplicitFlow: true in the app manifest.',
    chain: 'A',
    exampleInput: { authority: 'https://login.microsoftonline.com/{tenant-id}', clientId: '{portal-app-client-id}', scopes: ['openid', 'profile', 'email'] },
    exampleOutput: { idToken: 'eyJ0eXAiOiJKV1Qi...', account: 'user@tenant.onmicrosoft.com' },
  },
  'Check Connection': {
    description: 'Calls acquireAccessToken via WIF to check if a stored SharePoint refresh token exists for this user\'s WIF identity. Returns 404 if no token is stored or if it was stored under a different identity (e.g., ADC).',
  },
  'STS Token Exchange': {
    description: 'Exchanges the Entra JWT for a GCP access token via Workforce Identity Federation (WIF). Maps the Entra sub claim to a GCP principal. This GCP token identifies the user to Discovery Engine — it is NOT a service account.',
    chain: 'A',
    exampleInput: { audience: '//iam.googleapis.com/locations/global/workforcePools/{pool}/providers/{provider}', subjectToken: 'eyJ0eXAiOiJKV1Qi...', subjectTokenType: 'urn:ietf:params:oauth:token-type:id_token' },
    exampleOutput: { access_token: 'ya29.d.b0AXv0zT...', token_type: 'Bearer', expires_in: 3600 },
  },
  'acquireAccessToken': {
    description: 'Discovery Engine checks if it holds a stored SharePoint refresh token for this WIF identity. If the token was stored using ADC instead of WIF, this returns 404 — identity mismatch.',
    chain: 'A',
    exampleInput: { connector: '{connector-id}/dataConnector:acquireAccessToken', body: '(empty — identity from GCP token)', gcpToken: 'ya29.d.b0AXv0zT...' },
    exampleOutput: { connected: true, hasAccessToken: true },
  },
  'Get Auth URL': {
    description: 'Generates the Microsoft OAuth consent URL using the Connector App (not Portal App). Stores the Entra JWT by nonce so the callback can retrieve it later. redirect_uri must be vertexaisearch.cloud.google.com/oauth-redirect — Discovery Engine hardcodes this.',
    chain: 'B',
    exampleInput: { client_id: '{connector-app-client-id}', redirect_uri: 'https://vertexaisearch.cloud.google.com/oauth-redirect', scope: 'openid offline_access https://{tenant}.sharepoint.com/AllSites.Read' },
    exampleOutput: { auth_url: 'https://login.microsoftonline.com/{tenant-id}/oauth2/v2.0/authorize?client_id=...&redirect_uri=https://vertexaisearch.cloud.google.com/oauth-redirect&...' },
  },
  'OAuth Consent Popup': {
    description: 'Opens Microsoft login for SharePoint consent using the Connector App. The redirect goes to Google\'s vertexaisearch.cloud.google.com/oauth-redirect page, which captures the auth code and sends it back via postMessage.',
    chain: 'B',
    exampleInput: { redirectTo: 'https://login.microsoftonline.com/{tenant-id}/oauth2/v2.0/authorize?...' },
    exampleOutput: { callback: 'https://vertexaisearch.cloud.google.com/oauth-redirect?code=0.AW8B_aFG...&state=eyJvcml...&session_state=003f0cba-...' },
  },
  'OAuth Redirect (postMessage)': {
    description: 'Google\'s redirect page receives the auth code from Microsoft and sends {fullRedirectUrl, code, state} back via postMessage. COOP caveat: if your app is NOT on the same origin as vertexaisearch.cloud.google.com, postMessage is blocked. Use the popup-closed fallback with check-connection polling.',
    chain: 'B',
    exampleInput: { fullRedirectUrl: 'https://vertexaisearch.cloud.google.com/oauth-redirect?code=0.AW8B...&state=eyJvcml...' },
    exampleOutput: { type: 'sharepoint-oauth-callback', success: true },
  },
  'acquireAndStoreRefreshToken': {
    description: 'CONVERGENCE POINT — Chain A (WIF identity from GCP token) meets Chain B (auth code from OAuth consent). Discovery Engine exchanges the auth code for a SharePoint refresh token and stores it mapped to this WIF identity. Future searches use this stored token for per-user ACLs.',
    chain: 'A+B',
    exampleInput: { endpoint: '{connector-id}/dataConnector:acquireAndStoreRefreshToken', fullRedirectUri: 'https://vertexaisearch.cloud.google.com/oauth-redirect?code=0.AW8B...', gcpToken: 'ya29.d.b0AXv0zT... (WIF token — NOT service account)' },
    exampleOutput: { success: true },
  },
  'Search': {
    description: 'Calls StreamAssist for federated real-time search. Uses the stored refresh token to query SharePoint with the user\'s ACLs. dataStoreSpecs is optional — StreamAssist searches all connected stores by default. Requires natural language queries — keywords are silently ignored.',
    exampleInput: { query: 'What are the latest financial reports?', session_token: null },
    exampleOutput: { answer_length: 1246, sources_count: 5, session_token: 'projects/.../sessions/178690...' },
  },
  'StreamAssist': {
    description: 'Discovery Engine StreamAssist API performs federated real-time search against SharePoint. Uses the stored refresh token (from acquireAndStoreRefreshToken) to enforce per-user ACLs. Requires natural language queries — keyword-only queries return NON_ASSIST_SEEKING_QUERY_IGNORED.',
    exampleInput: { query: 'What are the latest financial reports?', dataStoreSpecs: '(optional)' },
    exampleOutput: { answer: '...grounded response...', sources: ['sharepoint-file-1.pdf', 'sharepoint-page-2.aspx'], session: 'projects/.../sessions/...' },
  },
};

export default function App() {
  const { instance, accounts } = useMsal();
  const isAuthenticated = useIsAuthenticated();
  const username = accounts[0]?.username || '';
  const spKey = `sp_connected_${username}`;

  const [spConnected, setSpConnected] = useState(false);
  const [connectionChecked, setConnectionChecked] = useState(false);
  const [authInProgress, setAuthInProgress] = useState(false);
  const [authStatus, setAuthStatus] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessionToken, setSessionToken] = useState<string | null>(null);
  const [traces, setTraces] = useState<TraceEntry[]>([]);
  const [showDebug, setShowDebug] = useState(true);
  const [expandedTraces, setExpandedTraces] = useState<Set<string>>(new Set());
  const [elapsedMs, setElapsedMs] = useState(0);
  const consentPopupRef = useRef<Window | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const traceEndRef = useRef<HTMLDivElement>(null);
  const searchStartRef = useRef<number>(0);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  useEffect(() => {
    if (!loading) return;
    const id = setInterval(() => setElapsedMs(Date.now() - searchStartRef.current), 50);
    return () => clearInterval(id);
  }, [loading]);

  useEffect(() => {
    traceEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [traces]);

  // ─── Trace helpers ─────────────────────────────────────────
  const addTrace = useCallback((stage: string, input?: any): string => {
    const id = crypto.randomUUID();
    const entry: TraceEntry = { id, stage, status: 'pending', timestamp: Date.now(), input };
    setTraces(prev => [...prev, entry]);
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
      updateTrace(traceId, {
        status: 'error',
        duration_ms: Date.now() - start,
        output: { error: err.message },
      });
    }
  };

  // ─── Listen for postMessage from OAuth redirect page ──────
  useEffect(() => {
    const handler = async (event: MessageEvent) => {
      // Handle vertexaisearch.cloud.google.com/oauth-redirect postMessage
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
          if (data.success) {
            setSpConnected(true);
            localStorage.setItem(spKey, '1');
            updateTrace(traceId, { status: 'success', duration_ms: Date.now() - start, output: { success: true } });
          } else {
            setAuthStatus(`Authorization failed: ${data.error || 'Unknown'}`);
            updateTrace(traceId, { status: 'error', duration_ms: Date.now() - start, output: { error: data.error } });
          }
          addBackendTraces(data._trace);
        } catch (err: any) {
          setAuthStatus(`Exchange failed: ${err.message}`);
          updateTrace(traceId, { status: 'error', duration_ms: Date.now() - start, output: { error: err.message } });
        }
        setAuthInProgress(false);
        return;
      }

      // Legacy: handle our own callback page postMessage
      if (event.data?.type !== 'sharepoint-oauth-callback') return;
      if (event.data.success) {
        setSpConnected(true);
        localStorage.setItem(spKey, '1');
        setTraces(prev => [...prev, {
          id: crypto.randomUUID(), stage: 'OAuth Callback (postMessage)', status: 'success',
          timestamp: Date.now(), input: { type: event.data.type }, output: { success: true },
        }]);
      } else {
        setAuthStatus(`Authorization failed: ${event.data.error || 'Unknown'}`);
        setTraces(prev => [...prev, {
          id: crypto.randomUUID(), stage: 'OAuth Callback (postMessage)', status: 'error',
          timestamp: Date.now(), input: { type: event.data.type }, output: { error: event.data.error },
        }]);
      }
      setAuthInProgress(false);
    };
    window.addEventListener('message', handler);
    return () => window.removeEventListener('message', handler);
  }, [spKey, getToken, addTrace, updateTrace, addBackendTraces]);

  // ─── Check connection on mount ────────────────────────────
  useEffect(() => {
    if (!isAuthenticated) return;
    (async () => {
      const token = await getToken();
      if (!token) { setConnectionChecked(true); return; }

      const traceId = addTrace('Check Connection', { endpoint: '/api/sharepoint/check-connection', idToken: token.substring(0, 30) + '...' });
      const start = Date.now();
      try {
        const resp = await fetch('/api/sharepoint/check-connection', {
          headers: { 'X-Entra-Id-Token': token },
        });
        const data = await resp.json();
        setSpConnected(data.connected);
        data.connected ? localStorage.setItem(spKey, '1') : localStorage.removeItem(spKey);
        updateTrace(traceId, {
          status: data.connected ? 'success' : 'error',
          duration_ms: Date.now() - start,
          output: { connected: data.connected },
        });
        addBackendTraces(data._trace);
      } catch (err: any) {
        setSpConnected(false);
        localStorage.removeItem(spKey);
        updateTrace(traceId, { status: 'error', duration_ms: Date.now() - start, output: { error: err.message } });
      } finally {
        setConnectionChecked(true);
      }
    })();
  }, [isAuthenticated, getToken, spKey]);

  // ─── Poll for popup closure (fallback) ────────────────────
  useEffect(() => {
    if (!authInProgress || !consentPopupRef.current) return;
    const interval = setInterval(async () => {
      const popup = consentPopupRef.current;
      if (!popup || popup.closed) {
        clearInterval(interval);
        consentPopupRef.current = null;
        await new Promise(r => setTimeout(r, 1500));
        const token = await getToken();
        if (token) {
          const resp = await fetch('/api/sharepoint/check-connection', {
            headers: { 'X-Entra-Id-Token': token },
          });
          const data = await resp.json();
          if (data.connected) {
            setSpConnected(true);
            localStorage.setItem(spKey, '1');
          }
          addBackendTraces(data._trace);
        }
        setAuthInProgress(false);
        setAuthStatus('');
      }
    }, 500);
    return () => clearInterval(interval);
  }, [authInProgress, getToken, spKey]);

  const handleConsent = async () => {
    setAuthInProgress(true);
    setAuthStatus('Opening consent...');
    const popup = window.open('about:blank', 'sp_consent', 'width=600,height=700,left=200,top=100');
    consentPopupRef.current = popup;
    if (!popup) {
      setAuthStatus('Popup blocked. Please allow popups.');
      setAuthInProgress(false);
      return;
    }
    try {
      const token = await getToken();
      const hint = username ? `?login_hint=${encodeURIComponent(username)}` : '';

      const traceId = addTrace('Get Auth URL', { endpoint: `/api/sharepoint/auth-url${hint}`, idToken: token?.substring(0, 30) + '...' });
      const start = Date.now();
      const resp = await fetch(`/api/sharepoint/auth-url${hint}`, {
        headers: token ? { 'X-Entra-Id-Token': token } : {},
      });
      const data = await resp.json();
      updateTrace(traceId, {
        status: 'success',
        duration_ms: Date.now() - start,
        output: { auth_url: data.auth_url?.substring(0, 80) + '...' },
      });

      popup.location.href = data.auth_url;
      setAuthStatus('Complete consent in the popup...');

      addTrace('OAuth Consent Popup', { redirectTo: data.auth_url?.substring(0, 80) + '...' });
    } catch (err: any) {
      popup.close();
      setAuthStatus(`Failed: ${err.message}`);
      setAuthInProgress(false);
    }
  };

  const handleSearch = async () => {
    const q = query.trim();
    if (!q || loading) return;
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
      session_token: sessionToken,
      idToken: token.substring(0, 30) + '...',
    });
    const start = searchStartRef.current;

    try {
      const resp = await fetch('/api/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-Entra-Id-Token': token },
        body: JSON.stringify({ query: q, session_token: sessionToken }),
      });
      const data = await resp.json();
      const elapsed = Date.now() - start;

      if (data.error) {
        setMessages(prev => [...prev, { role: 'assistant', text: `Error: ${data.error}`, duration_ms: elapsed }]);
        updateTrace(traceId, { status: 'error', duration_ms: elapsed, output: { error: data.error } });
      } else {
        setMessages(prev => [...prev, {
          role: 'assistant', text: data.answer || 'No answer generated.', sources: data.sources, duration_ms: elapsed,
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

  const fmtElapsed = (ms: number) => (ms < 1000 ? `${ms} ms` : `${(ms / 1000).toFixed(2)} s`);

  const renderMarkdown = (text: string) => {
    const lines = text.split('\n');
    const elements: JSX.Element[] = [];
    let listItems: string[] = [];
    let listType: 'ul' | 'ol' | null = null;

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

    const fmt = (s: string) =>
      s.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.+?)\*/g, '<em>$1</em>')
        .replace(/`(.+?)`/g, '<code>$1</code>');

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

  const statusIcon = (s: TraceEntry['status']) =>
    s === 'success' ? '\u2713' : s === 'error' ? '\u2717' : '\u25CF';

  const formatJson = (obj: any) => JSON.stringify(obj, null, 2);

  return (
    <div className={`app-layout ${showDebug ? 'with-sidebar' : ''}`}>
      <div className="app">
        <header>
          <h1>SharePoint Portal</h1>
          <span className="subtitle">Powered by Gemini Enterprise StreamAssist</span>
          {isAuthenticated && (
            <div className="user-info">
              {username}
              {spConnected && (
                <button className="btn-small" onClick={() => { setSpConnected(false); localStorage.removeItem(spKey); }}>
                  Reconnect SP
                </button>
              )}
              <button className="btn-small" onClick={async () => {
                setSessionToken(null);
                setMessages([]);
                setTraces([]);
                setExpandedTraces(new Set());
                setConnectionChecked(false);
                localStorage.removeItem(spKey);

                // Force fresh MSAL token (interactive if silent fails)
                let token: string | null = null;
                try {
                  if (accounts[0]) {
                    await instance.acquireTokenSilent({ ...loginRequest, account: accounts[0], forceRefresh: true });
                    token = (await instance.acquireTokenSilent({ ...loginRequest, account: accounts[0] })).idToken;
                  }
                } catch {
                  try {
                    token = (await instance.acquireTokenPopup(loginRequest)).idToken;
                  } catch { /* user cancelled */ }
                }

                // Re-check SP connection with fresh token
                if (token) {
                  const resp = await fetch('/api/sharepoint/check-connection', { headers: { 'X-Entra-Id-Token': token } });
                  const data = await resp.json();
                  setSpConnected(data.connected);
                  data.connected ? localStorage.setItem(spKey, '1') : localStorage.removeItem(spKey);
                  addBackendTraces(data._trace);
                } else {
                  setSpConnected(false);
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
            {showDebug ? '\u00AB' : '\u00BB'} Pipeline
          </button>
        </header>

        {!isAuthenticated && (
          <section className="card login-card">
            <h2>Sign in to get started</h2>
            <p>Sign in with your Microsoft account to search SharePoint documents.</p>
            <button className="btn-primary" onClick={handleLogin}>
              Sign in with Microsoft
            </button>
          </section>
        )}

        {isAuthenticated && !connectionChecked && (
          <div className="empty-state" style={{ marginTop: 80 }}>
            <div className="dot-pulse" />
            <p>Checking SharePoint connection...</p>
          </div>
        )}

        {isAuthenticated && connectionChecked && (
          <>
            {!spConnected && (
              <div className="auth-banner">
                <div className="auth-banner-content">
                  <span>SharePoint requires a one-time authorization to access your documents.</span>
                  <button className="btn-primary btn-consent" onClick={handleConsent} disabled={authInProgress}>
                    {authInProgress ? 'Authorizing...' : 'Connect SharePoint'}
                  </button>
                </div>
                {authStatus && <div className="auth-status">{authStatus}</div>}
              </div>
            )}

            {spConnected && (
              <div className="search-container">
                <div className="messages-area">
                  {messages.length === 0 && !loading && (
                    <div className="empty-state">
                      <div className="empty-icon">
                        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                          <circle cx="11" cy="11" r="8" /><path d="m21 21-4.35-4.35" />
                        </svg>
                      </div>
                      <p>Search your SharePoint documents</p>
                      <span className="empty-hint">Ask questions about contracts, reports, or any document in your SharePoint site.</span>
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
                        <div className="message-text">{msg.role === 'assistant' ? renderMarkdown(msg.text) : msg.text}</div>
                        {msg.sources && msg.sources.length > 0 && (
                          <div className="sources">
                            <h4>Sources</h4>
                            <div className="source-cards">
                              {msg.sources.map((src, j) => (
                                <a key={j} href={src.url} target="_blank" rel="noopener noreferrer" className="source-card">
                                  <span className="source-icon">{fileIcon(src.file_type)}</span>
                                  <div className="source-info">
                                    <span className="source-title">{src.title}</span>
                                    {src.description && <span className="source-desc">{src.description}</span>}
                                    <span className="source-meta">
                                      SharePoint {src.entity_type && `\u00B7 ${src.entity_type}`} {src.file_type && `\u00B7 ${src.file_type.toUpperCase()}`}
                                    </span>
                                  </div>
                                </a>
                              ))}
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
                          <span>Searching SharePoint...</span>
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
                    placeholder="Ask about your SharePoint documents..." disabled={loading}
                  />
                  <button type="submit" className="btn-primary btn-search" disabled={loading || !query.trim()}>
                    {loading ? 'Searching...' : 'Search'}
                  </button>
                </form>
              </div>
            )}
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
MSAL Login                 Connect SharePoint
    │                           │
Entra id_token             OAuth popup
    │                       (Connector App)
STS Exchange                    │
(WIF Pool)                 Microsoft login
    │                       + consent
GCP access token                │
    │                      auth code via
    │                      redirect page
    │                           │
    └────────┐    ┌─────────────┘
             ▼    ▼
   acquireAndStoreRefreshToken
   (GCP token identifies user,
    auth code provides consent)
             │
     stored refresh token
             │
     StreamAssist Search
    (per-user SharePoint ACLs)`}</pre>
              <div className="flow-gotchas">
                <div className="gotcha"><span className="gotcha-icon">!</span> <strong>redirect_uri</strong> must be <code>vertexaisearch.cloud.google.com/oauth-redirect</code> — Discovery Engine hardcodes this</div>
                <div className="gotcha"><span className="gotcha-icon">!</span> <strong>WIF token, not ADC</strong> — using a service account token causes identity mismatch (acquireAccessToken returns 404)</div>
                <div className="gotcha"><span className="gotcha-icon">!</span> <strong>COOP blocks postMessage</strong> from cross-origin popups — use popup-closed polling as fallback</div>
                <div className="gotcha"><span className="gotcha-icon">!</span> <strong>oauth2AllowIdTokenImplicitFlow: true</strong> required in Portal App manifest for WIF</div>
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
                    <span className="trace-chevron">{expandedTraces.has(trace.id) ? '\u25BC' : '\u25B6'}</span>
                  </div>
                  {expandedTraces.has(trace.id) && (
                    <div className="trace-body">
                      {info?.description && (
                        <div className="trace-description">{info.description}</div>
                      )}
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
            {(() => {
              const firedStages = new Set(traces.map(t => t.stage));
              const ghostStages = Object.entries(STAGE_INFO).filter(([s]) => !firedStages.has(s));
              if (ghostStages.length === 0) return null;
              return (
                <>
                  {ghostStages.length > 0 && traces.length > 0 && (
                    <div className="ghost-divider">not yet triggered</div>
                  )}
                  {ghostStages.map(([stage, info]) => (
                    <div key={stage} className="trace-entry trace-ghost" onClick={() => {
                      setExpandedTraces(prev => {
                        const next = new Set(prev);
                        next.has(stage) ? next.delete(stage) : next.add(stage);
                        return next;
                      });
                    }}>
                      <div className="trace-header">
                        <span className="trace-status-icon trace-icon-ghost">{'\u25CB'}</span>
                        {info.chain && <span className={`trace-chain chain-${info.chain.replace('+', '')}`}>{info.chain}</span>}
                        <span className="trace-stage">{stage}</span>
                        <span className="trace-chevron">{expandedTraces.has(stage) ? '\u25BC' : '\u25B6'}</span>
                      </div>
                      {expandedTraces.has(stage) && (
                        <div className="trace-body">
                          <div className="trace-description">{info.description}</div>
                          {info.exampleInput && (
                            <div className="trace-section">
                              <div className="trace-label">INPUT</div>
                              <pre className="trace-json">{JSON.stringify(info.exampleInput, null, 2)}</pre>
                            </div>
                          )}
                          {info.exampleOutput && (
                            <div className="trace-section">
                              <div className="trace-label">OUTPUT</div>
                              <pre className="trace-json">{JSON.stringify(info.exampleOutput, null, 2)}</pre>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  ))}
                </>
              );
            })()}
            <div ref={traceEndRef} />
          </div>
        </aside>
      )}
    </div>
  );
}
