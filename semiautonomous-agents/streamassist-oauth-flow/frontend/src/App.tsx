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
  const consentPopupRef = useRef<Window | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const getToken = useCallback(async (): Promise<string | null> => {
    if (!accounts[0]) return null;
    try {
      const resp = await instance.acquireTokenSilent({ ...loginRequest, account: accounts[0] });
      return resp.idToken;
    } catch {
      try {
        return (await instance.acquireTokenPopup(loginRequest)).idToken;
      } catch {
        return null;
      }
    }
  }, [instance, accounts]);

  // ─── Listen for postMessage from OAuth callback ─────────────
  useEffect(() => {
    const handler = (event: MessageEvent) => {
      if (event.data?.type !== 'sharepoint-oauth-callback') return;
      if (event.data.success) {
        setSpConnected(true);
        localStorage.setItem(spKey, '1');
      } else {
        setAuthStatus(`Authorization failed: ${event.data.error || 'Unknown'}`);
      }
      setAuthInProgress(false);
    };
    window.addEventListener('message', handler);
    return () => window.removeEventListener('message', handler);
  }, [spKey]);

  // ─── Check connection on mount ──────────────────────────────
  useEffect(() => {
    if (!isAuthenticated) return;
    (async () => {
      const token = await getToken();
      if (!token) { setConnectionChecked(true); return; }
      try {
        const resp = await fetch('/api/sharepoint/check-connection', {
          headers: { 'X-Entra-Id-Token': token },
        });
        const data = await resp.json();
        setSpConnected(data.connected);
        data.connected ? localStorage.setItem(spKey, '1') : localStorage.removeItem(spKey);
      } catch {
        setSpConnected(false);
        localStorage.removeItem(spKey);
      } finally {
        setConnectionChecked(true);
      }
    })();
  }, [isAuthenticated, getToken, spKey]);

  // ─── Poll for popup closure (fallback) ──────────────────────
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
      const resp = await fetch(`/api/sharepoint/auth-url${hint}`, {
        headers: token ? { 'X-Entra-Id-Token': token } : {},
      });
      const { auth_url } = await resp.json();
      popup.location.href = auth_url;
      setAuthStatus('Complete consent in the popup...');
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

    try {
      const resp = await fetch('/api/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-Entra-Id-Token': token },
        body: JSON.stringify({ query: q, session_token: sessionToken }),
      });
      const data = await resp.json();
      if (data.error) {
        setMessages(prev => [...prev, { role: 'assistant', text: `Error: ${data.error}` }]);
      } else {
        setMessages(prev => [...prev, {
          role: 'assistant', text: data.answer || 'No answer generated.', sources: data.sources,
        }]);
        if (data.session_token) setSessionToken(data.session_token);
      }
    } catch (err: any) {
      setMessages(prev => [...prev, { role: 'assistant', text: `Network error: ${err.message}` }]);
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

  return (
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
      </header>

      {!isAuthenticated && (
        <section className="card login-card">
          <h2>Sign in to get started</h2>
          <p>Sign in with your Microsoft account to search SharePoint documents.</p>
          <button className="btn-primary" onClick={() => instance.loginPopup(loginRequest)}>
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
  );
}
