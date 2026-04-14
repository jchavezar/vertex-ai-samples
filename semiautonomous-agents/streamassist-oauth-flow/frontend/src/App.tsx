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
}

interface TraceEntry {
  id: string;
  stage: string;
  status: 'pending' | 'success' | 'error';
  timestamp: number;
  duration_ms?: number;
  input?: any;
  output?: any;
}

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
  const consentPopupRef = useRef<Window | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const traceEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

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

  // ─── Listen for postMessage from OAuth callback ───────────
  useEffect(() => {
    const handler = (event: MessageEvent) => {
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
  }, [spKey]);

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
    setLoading(true);

    const traceId = addTrace('Search', {
      endpoint: 'POST /api/search',
      query: q,
      session_token: sessionToken,
      idToken: token.substring(0, 30) + '...',
    });
    const start = Date.now();

    try {
      const resp = await fetch('/api/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-Entra-Id-Token': token },
        body: JSON.stringify({ query: q, session_token: sessionToken }),
      });
      const data = await resp.json();

      if (data.error) {
        setMessages(prev => [...prev, { role: 'assistant', text: `Error: ${data.error}` }]);
        updateTrace(traceId, { status: 'error', duration_ms: Date.now() - start, output: { error: data.error } });
      } else {
        setMessages(prev => [...prev, {
          role: 'assistant', text: data.answer || 'No answer generated.', sources: data.sources,
        }]);
        updateTrace(traceId, {
          status: 'success',
          duration_ms: Date.now() - start,
          output: { answer_length: data.answer?.length, sources_count: data.sources?.length, session_token: data.session_token },
        });
        if (data.session_token) setSessionToken(data.session_token);
      }
      addBackendTraces(data._trace);
    } catch (err: any) {
      setMessages(prev => [...prev, { role: 'assistant', text: `Network error: ${err.message}` }]);
      updateTrace(traceId, { status: 'error', duration_ms: Date.now() - start, output: { error: err.message } });
    } finally {
      setLoading(false);
    }
  };

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
                          <div className="dot-pulse" /><span>Searching SharePoint...</span>
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
          {traces.length === 0 && (
            <div className="sidebar-empty">
              <p>No traces yet.</p>
              <p className="sidebar-hint">Sign in to see the auth pipeline in action.</p>
            </div>
          )}
          <div className="trace-list">
            {traces.map((trace) => (
              <div key={trace.id} className={`trace-entry trace-${trace.status}`} onClick={() => toggleTrace(trace.id)}>
                <div className="trace-header">
                  <span className={`trace-status-icon trace-icon-${trace.status}`}>{statusIcon(trace.status)}</span>
                  <span className="trace-stage">{trace.stage}</span>
                  {trace.duration_ms != null && <span className="trace-duration">{trace.duration_ms}ms</span>}
                  <span className="trace-chevron">{expandedTraces.has(trace.id) ? '\u25BC' : '\u25B6'}</span>
                </div>
                {expandedTraces.has(trace.id) && (
                  <div className="trace-body">
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
            ))}
            <div ref={traceEndRef} />
          </div>
        </aside>
      )}
    </div>
  );
}
