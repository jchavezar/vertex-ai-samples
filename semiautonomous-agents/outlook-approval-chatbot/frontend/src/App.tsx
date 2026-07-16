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
  latency_ms?: number;
}

interface ApprovalItem {
  id: string;
  label: string;
  context: {
    category: 'approval' | 'email_reply' | string;
    source: string;
    requester: string;
    from: string;
    subject: string;
    dueDate: string;
    summary: string;
    requested_action: string;
    link: string;
  };
  status?: 'approved' | 'rejected'; // local state flag
}

function parseDraft(text: string) {
  const toMatch = text.match(/\*\*To:\*\*\s*([^\n\r]+)/i);
  const subjectMatch = text.match(/\*\*Subject:\*\*\s*([^\n\r]+)/i);
  if (toMatch && subjectMatch) {
    const to_address = toMatch[1].trim();
    const subject = subjectMatch[1].trim();
    
    // Attempt to extract body (the block starting after Subject line, up to ***)
    const idxSub = text.indexOf(subjectMatch[0]);
    let body = text.substring(idxSub + subjectMatch[0].length).trim();
    
    // strip out leading asterisks or lines
    if (body.startsWith('***')) {
      body = body.substring(3).trim();
    }
    const idxEnd = body.indexOf('***');
    if (idxEnd !== -1) {
      body = body.substring(0, idxEnd).trim();
    }
    
    // Also remove the footer message if any (like "Let me know if you'd like me to send this")
    const idxLetMeKnow = body.toLowerCase().indexOf("let me know");
    if (idxLetMeKnow !== -1) {
      body = body.substring(0, idxLetMeKnow).trim();
    }
    
  }
  return null;
}

function renderMarkdown(text: string) {
  if (!text) return null;

  // Split into paragraphs or block items
  const blocks = text.split('\n\n');

  return blocks.map((block, blockIdx) => {
    const trimmed = block.trim();
    if (!trimmed) return null;

    // Check if it's a list
    if (trimmed.startsWith('- ') || trimmed.startsWith('* ') || trimmed.match(/^\d+\.\s/)) {
      const items = block.split('\n');
      return (
        <ul key={blockIdx} style={{ paddingLeft: '1.25rem', margin: '8px 0', lineHeight: '1.5' }}>
          {items.map((item, itemIdx) => {
            const cleanItem = item.replace(/^[-*\d\.]+\s+/, '');
            return (
              <li key={itemIdx} style={{ marginBottom: '4px' }}>
                {renderInlineMarkdown(cleanItem)}
              </li>
            );
          })}
        </ul>
      );
    }

    // Default paragraph
    return (
      <p key={blockIdx} style={{ margin: '0 0 12px 0', lineHeight: '1.6' }}>
        {renderInlineMarkdown(trimmed)}
      </p>
    );
  });
}

function renderInlineMarkdown(text: string) {
  const parts = [];
  let remaining = text;
  
  while (remaining) {
    const boldIdx = remaining.indexOf('**');
    const italicIdx = remaining.indexOf('*');
    const codeIdx = remaining.indexOf('`');
    
    const indices = [
      { type: 'bold', index: boldIdx },
      { type: 'italic', index: italicIdx },
      { type: 'code', index: codeIdx }
    ].filter(x => x.index !== -1).sort((a, b) => a.index - b.index);
    
    if (indices.length === 0) {
      parts.push(remaining);
      break;
    }
    
    const nextToken = indices[0];
    
    if (nextToken.index > 0) {
      parts.push(remaining.substring(0, nextToken.index));
    }
    
    remaining = remaining.substring(nextToken.index);
    
    if (nextToken.type === 'bold') {
      const closingIdx = remaining.indexOf('**', 2);
      if (closingIdx !== -1) {
        parts.push(<strong key={remaining + closingIdx} style={{ fontWeight: 600, color: 'var(--text)' }}>{remaining.substring(2, closingIdx)}</strong>);
        remaining = remaining.substring(closingIdx + 2);
      } else {
        parts.push('**');
        remaining = remaining.substring(2);
      }
    } else if (nextToken.type === 'italic') {
      const closingIdx = remaining.indexOf('*', 1);
      if (closingIdx !== -1) {
        parts.push(<em key={remaining + closingIdx} style={{ fontStyle: 'italic' }}>{remaining.substring(1, closingIdx)}</em>);
        remaining = remaining.substring(closingIdx + 1);
      } else {
        parts.push('*');
        remaining = remaining.substring(1);
      }
    } else if (nextToken.type === 'code') {
      const closingIdx = remaining.indexOf('`', 1);
      if (closingIdx !== -1) {
        parts.push(
          <code key={remaining + closingIdx} style={{ 
            fontFamily: 'monospace', 
            background: 'var(--bg-card, #f1f5f9)', 
            padding: '2px 6px', 
            borderRadius: '4px',
            fontSize: '0.85em',
            border: '1px solid var(--border)'
          }}>
            {remaining.substring(1, closingIdx)}
          </code>
        );
        remaining = remaining.substring(closingIdx + 1);
      } else {
        parts.push('`');
        remaining = remaining.substring(1);
      }
    }
  }
  
  return parts;
}


export default function App() {
  const { instance, accounts } = useMsal();
  const isAuthenticated = useIsAuthenticated();
  const username = accounts[0]?.username || '';
  const olKey = `outlook_connected_${username}`;

  // State
  const [olConnected, setOlConnected] = useState(false);
  const [connectionChecked, setConnectionChecked] = useState(false);
  const [authInProgress, setAuthInProgress] = useState(false);
  const [authStatus, setAuthStatus] = useState('');

  // Chat chatbot states
  const [messages, setMessages] = useState<Message[]>([]);
  const [chatInput, setChatInput] = useState('');
  const [loadingChat, setLoadingChat] = useState(false);
  const [sessionToken, setSessionToken] = useState<string | null>(null);

  // Approvals states
  const [approvals, setApprovals] = useState<ApprovalItem[]>([]);
  const [loadingApprovals, setLoadingApprovals] = useState(false);
  const [actioningIds, setActioningIds] = useState<Record<string, boolean>>({});

  // Chat email confirmation states
  const [sentEmailIndexes, setSentEmailIndexes] = useState<Record<number, boolean>>({});
  const [sendingEmailIndexes, setSendingEmailIndexes] = useState<Record<number, boolean>>({});

  const consentPopupRef = useRef<Window | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loadingChat]);

  // MSAL token getter
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
    try {
      await instance.loginPopup(loginRequest);
    } catch (err: any) {
      console.error("Login failed:", err.message);
    }
  };

  // Check Outlook Connection status
  const checkConnection = useCallback(async () => {
    const token = await getToken();
    if (!token) {
      setConnectionChecked(true);
      return;
    }
    try {
      const resp = await fetch('/api/outlook/check-connection', {
        headers: { 'X-Entra-Id-Token': token },
      });
      const data = await resp.json();
      setOlConnected(data.connected);
      if (data.connected) {
        localStorage.setItem(olKey, '1');
      } else {
        localStorage.removeItem(olKey);
      }
    } catch (err) {
      console.error("Connection check error:", err);
      setOlConnected(false);
    } finally {
      setConnectionChecked(true);
    }
  }, [getToken, olKey]);

  useEffect(() => {
    if (isAuthenticated) {
      checkConnection();
    }
  }, [isAuthenticated, checkConnection]);

  // Poll for popup closure (fallback consent handshake)
  useEffect(() => {
    if (!authInProgress || !consentPopupRef.current) return;
    const interval = setInterval(async () => {
      const popup = consentPopupRef.current;
      let closed = !popup;
      if (popup) {
        try { closed = popup.closed; } catch { closed = true; }
      }
      if (closed) {
        clearInterval(interval);
        consentPopupRef.current = null;
        await new Promise(r => setTimeout(r, 1500));
        await checkConnection();
        setAuthInProgress(false);
        setAuthStatus('');
      }
    }, 2000);
    return () => clearInterval(interval);
  }, [authInProgress, checkConnection]);

  // Trigger MS Consent
  const handleConsent = async () => {
    setAuthInProgress(true);
    setAuthStatus('Opening consent window...');
    const popup = window.open('about:blank', 'ol_consent', 'width=600,height=700,left=200,top=100');
    consentPopupRef.current = popup;
    if (!popup) {
      setAuthStatus('Popup blocked. Please enable popups.');
      setAuthInProgress(false);
      return;
    }
    try {
      const token = await getToken();
      const hint = username ? `?login_hint=${encodeURIComponent(username)}` : '';
      const resp = await fetch(`/api/outlook/auth-url${hint}`, {
        headers: token ? { 'X-Entra-Id-Token': token } : {},
      });
      const data = await resp.json();
      popup.location.href = data.auth_url;
      setAuthStatus('Please complete consent in the window...');
    } catch (err: any) {
      popup.close();
      setAuthStatus(`Authorization failed: ${err.message}`);
      setAuthInProgress(false);
    }
  };

  // Listen for callback page messages
  useEffect(() => {
    const handler = async (event: MessageEvent) => {
      if (event.data?.fullRedirectUrl) {
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
            setOlConnected(true);
            localStorage.setItem(olKey, '1');
          } else {
            setAuthStatus(`Exchange failed: ${data.error}`);
          }
        } catch (err: any) {
          setAuthStatus(`Callback error: ${err.message}`);
        }
        setAuthInProgress(false);
      }
    };
    window.addEventListener('message', handler);
    return () => window.removeEventListener('message', handler);
  }, [getToken, olKey]);

  const sendEmailFromChat = async (idx: number, to: string, subject: string, body: string) => {
    const token = await getToken();
    if (!token) return;

    setSendingEmailIndexes(prev => ({ ...prev, [idx]: true }));
    try {
      const resp = await fetch('/api/send-email', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Entra-Id-Token': token,
        },
        body: JSON.stringify({ to_address: to, subject, body }),
      });
      const data = await resp.json();
      if (data.success) {
        setSentEmailIndexes(prev => ({ ...prev, [idx]: true }));
      } else {
        alert(`Failed to send email: ${data.error || 'Unknown error'}`);
      }
    } catch (err: any) {
      alert(`Network error: ${err.message}`);
    } finally {
      setSendingEmailIndexes(prev => ({ ...prev, [idx]: false }));
    }
  };

  // Chat chatbot handler
  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    const q = chatInput.trim();
    if (!q || loadingChat) return;

    const token = await getToken();
    if (!token) return;

    setMessages(prev => [...prev, { role: 'user', text: q }]);
    setChatInput('');
    setLoadingChat(true);

    const startTime = Date.now();
    try {
      const resp = await fetch('/api/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Entra-Id-Token': token,
        },
        body: JSON.stringify({ query: q, session_token: sessionToken }),
      });
      const data = await resp.json();
      if (data.error) {
        setMessages(prev => [...prev, { role: 'assistant', text: `Error: ${data.error}` }]);
      } else {
        setMessages(prev => [...prev, {
          role: 'assistant',
          text: data.answer || 'No answer returned.',
          sources: data.sources,
          latency_ms: Date.now() - startTime,
        }]);
        if (data.session_token) {
          setSessionToken(data.session_token);
        }
      }
    } catch (err: any) {
      setMessages(prev => [...prev, { role: 'assistant', text: `Network Error: ${err.message}` }]);
    } finally {
      setLoadingChat(false);
    }
  };

  // Scan Approvals from Outlook Inbox
  const scanApprovals = async () => {
    const token = await getToken();
    if (!token) return;

    setLoadingApprovals(true);
    try {
      // scan inbox items
      const resp = await fetch('/api/approvals?lookback_hours=48', {
        headers: { 'X-Entra-Id-Token': token }
      });
      const data = await resp.json();
      if (data.items) {
        setApprovals(data.items);
      } else if (data.error) {
        console.error("Scan error:", data.error);
        alert(`Error scanning inbox: ${data.error}`);
      }
    } catch (err: any) {
      console.error("Scan network error:", err);
    } finally {
      setLoadingApprovals(false);
    }
  };

  // Perform Approve/Reject Reply Action
  const handleApprovalAction = async (id: string, action: 'approve' | 'reject') => {
    const token = await getToken();
    if (!token) return;

    setActioningIds(prev => ({ ...prev, [id]: true }));
    try {
      const commentText = action === 'approve'
        ? 'Decision finalized. Approved.'
        : 'Decision finalized. Rejected.';

      const resp = await fetch(`/api/approvals/${id}/action`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Entra-Id-Token': token
        },
        body: JSON.stringify({ action, comment: commentText })
      });
      const data = await resp.json();
      if (data.success) {
        // Update local approvals state to update UI
        setApprovals(prev => prev.map(item =>
          item.id === id ? { ...item, status: action === 'approve' ? 'approved' : 'rejected' } : item
        ));
      } else {
        alert(`Action failed: ${data.error || 'Unknown error'}`);
      }
    } catch (err: any) {
      alert(`Network error: ${err.message}`);
    } finally {
      setActioningIds(prev => ({ ...prev, [id]: false }));
    }
  };

  if (!isAuthenticated) {
    return (
      <div className="login-screen">
        <div className="login-card">
          <h2>Sign in Required</h2>
          <p>Please authenticate with your Microsoft account to load the Executive Assistant workspace.</p>
          <button className="btn-tech" onClick={handleLogin}>
            Login via MSAL
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="app-container">
      <header>
        <div style={{ display: 'flex', alignItems: 'baseline' }}>
          <h1>Executive Assistant</h1>
          <span className="subtitle">Outlook Command Console</span>
        </div>
        <div className="header-meta">
          <span className="user-display">{username}</span>
          {connectionChecked && (
            <>
              {olConnected ? (
                <span className="status-indicator connected">
                  [OUTLOOK CONNECTED]
                </span>
              ) : (
                <span className="status-indicator disconnected">
                  [OUTLOOK DISCONNECTED]
                </span>
              )}
            </>
          )}
          {!olConnected && (
            <button className="btn-tech btn-small" onClick={handleConsent} disabled={authInProgress}>
              {authInProgress ? 'CONNECTING...' : 'CONNECT'}
            </button>
          )}
          <button className="btn-tech-outline btn-small" onClick={() => instance.logoutPopup()}>
            LOGOUT
          </button>
        </div>
      </header>

      {authStatus && (
        <div className="auth-banner">
          <div className="auth-banner-content">
            <span>{authStatus}</span>
          </div>
        </div>
      )}

      <div className="main-content">
        {/* Chat / Chatbot Area */}
        <div className="chat-section">
          <div className="chat-header">
            <h2>Gemini Chat Console</h2>
            {sessionToken && <span style={{ fontSize: '0.65rem', fontFamily: 'monospace', color: 'var(--text-muted)' }}>[SESSION: {sessionToken.substring(sessionToken.lastIndexOf('/') + 1)}]</span>}
          </div>

          <div className="chat-messages">
            {messages.length === 0 && !loadingChat && (
              <div className="empty-state">
                <p>Chatbot Active</p>
                <span>Ask questions about your emails, schedule, or request task updates.</span>
              </div>
            )}

            {messages.map((msg, idx) => (
              <div key={idx} className={`msg-block msg-block-${msg.role}`}>
                <span className="msg-label">{msg.role === 'user' ? 'USER' : 'GEMINI ENTERPRISE'}</span>
                <div className="msg-content">
                  {renderMarkdown(msg.text)}

                  {msg.sources && msg.sources.length > 0 && (
                    <div style={{ marginTop: '12px', borderTop: '1px dotted var(--border)', paddingTop: '8px' }}>
                      <span style={{ fontSize: '0.65rem', fontWeight: 600, color: 'var(--text-muted)' }}>SOURCES:</span>
                      <ul style={{ listStyle: 'none', paddingLeft: 0, marginTop: '4px' }}>
                        {msg.sources.map((src, sIdx) => (
                          <li key={sIdx} style={{ fontSize: '0.75rem', marginBottom: '4px' }}>
                            <a href={src.url} target="_blank" rel="noopener noreferrer" style={{ color: 'var(--text)', textDecoration: 'underline' }}>
                              [{src.entity_type || 'Email'}] {src.title}
                            </a>
                            {src.description && <span style={{ color: 'var(--text-muted)' }}> - {src.description}</span>}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* If this is an assistant response containing a drafted email template, render an interactive action confirmation card */}
                  {msg.role === 'assistant' && parseDraft(msg.text) && (
                    (() => {
                      const d = parseDraft(msg.text)!;
                      const isSent = sentEmailIndexes[idx];
                      const isSending = sendingEmailIndexes[idx];
                      return (
                        <div className="draft-approval-card" style={{
                          marginTop: '16px',
                          background: 'rgba(52, 211, 153, 0.04)',
                          border: '1px solid var(--border)',
                          borderRadius: '8px',
                          padding: '16px',
                          boxShadow: '0 4px 12px rgba(0,0,0,0.15)'
                        }}>
                          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
                            <span style={{ fontSize: '0.65rem', letterSpacing: '1px', fontWeight: 700, color: 'var(--text)', background: 'rgba(52, 211, 153, 0.15)', padding: '4px 8px', borderRadius: '4px' }}>
                              DRAFTED EMAIL ACTION REQUIRED
                            </span>
                            {isSent && <span style={{ fontSize: '0.75rem', color: '#10b981', fontWeight: 700 }}>✓ SENT</span>}
                          </div>
                          <div style={{ fontSize: '0.8rem', marginBottom: '8px' }}>
                            <strong>To:</strong> <span style={{ color: 'var(--text-muted)' }}>{d.to_address}</span>
                          </div>
                          <div style={{ fontSize: '0.8rem', marginBottom: '12px' }}>
                            <strong>Subject:</strong> <span style={{ color: 'var(--text-muted)' }}>{d.subject}</span>
                          </div>
                          <div style={{
                            background: 'var(--bg-card, #f8fafc)',
                            padding: '14px',
                            borderRadius: '6px',
                            fontSize: '0.85rem',
                            color: '#1e293b',
                            lineHeight: '1.5',
                            whiteSpace: 'pre-wrap',
                            maxHeight: '200px',
                            overflowY: 'auto',
                            marginBottom: '16px',
                            border: '1px solid var(--border)',
                            boxShadow: 'inset 0 1px 2px rgba(0,0,0,0.02)'
                          }}>
                            {d.body}
                          </div>
                          <div style={{ display: 'flex', gap: '12px' }}>
                            <button
                              className="btn-tech btn-small"
                              style={{ background: isSent ? '#10b981' : '#10b981', color: '#fff', flex: 1 }}
                              disabled={isSent || isSending}
                              onClick={() => sendEmailFromChat(idx, d.to_address, d.subject, d.body)}
                            >
                              {isSending ? 'SENDING...' : isSent ? '✓ EMAIL SENT' : 'APPROVE & SEND EMAIL'}
                            </button>
                          </div>
                        </div>
                      );
                    })()
                  )}

                  {msg.latency_ms && (
                    <div className="msg-meta-footer">
                      <span>[LATENCY: {(msg.latency_ms / 1000).toFixed(2)}s]</span>
                      <span>[MODEL: GEMINI ENTERPRISE]</span>
                    </div>
                  )}
                </div>
              </div>
            ))}

            {loadingChat && (
              <div className="msg-block msg-block-ai">
                <span className="msg-label">GEMINI ENTERPRISE</span>
                <div className="msg-thinking">
                  Thinking... <span className="cursor-blink">█</span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <div className="chat-input-area">
            <form className="chat-input-form" onSubmit={handleSearch}>
              <input
                type="text"
                value={chatInput}
                onChange={e => setChatInput(e.target.value)}
                placeholder="Query mailbox contents or ask follow-ups..."
                disabled={loadingChat || !olConnected}
              />
              <button className="btn-tech" type="submit" disabled={loadingChat || !chatInput.trim() || !olConnected}>
                SEND
              </button>
            </form>
          </div>
        </div>

        {/* Inbox approvals action items */}
        <div className="approvals-section">
          <div className="approvals-header">
            <h2>Executive Action Items</h2>
            <button className="btn-tech btn-small" onClick={scanApprovals} disabled={loadingApprovals || !olConnected}>
              {loadingApprovals ? 'SCANNING...' : 'SCAN INBOX'}
            </button>
          </div>

          <div className="approvals-list">
            {loadingApprovals && (
              <div className="empty-state">
                <div className="spinning-indicator" />
                <p style={{ marginTop: '8px' }}>Scanning Inbox...</p>
                <span>Analyzing recent emails for requested approvals and decisions.</span>
              </div>
            )}

            {!loadingApprovals && approvals.length === 0 && (
              <div className="empty-state">
                <p>No Actions Scanned</p>
                <span>Click "SCAN INBOX" to run Gemini Enterprise search filters over your Outlook mailbox.</span>
              </div>
            )}

            {!loadingApprovals && approvals.map((item) => (
              <div key={item.id} className="approval-card">
                <div className="approval-card-header">
                  <span className="card-category-tag">{item.context.category || 'Approval'}</span>
                  {item.context.dueDate && (
                    <span className="card-due-tag">DUE: {item.context.dueDate}</span>
                  )}
                </div>

                <h3>{item.label}</h3>

                <div className="approval-card-meta">
                  <span>FROM: {item.context.from || item.context.requester}</span>
                  <span>SOURCE: {item.context.source}</span>
                </div>

                {item.context.summary && (
                  <p className="approval-card-summary">{item.context.summary}</p>
                )}

                {item.context.requested_action && (
                  <div className="approval-card-action-text">
                    <strong>ACTION:</strong> {item.context.requested_action}
                  </div>
                )}

                {item.context.link && (
                  <a href={item.context.link} target="_blank" rel="noopener noreferrer" className="approval-card-link">
                    Open email in Outlook
                  </a>
                )}

                {item.status ? (
                  <div className={`card-status-overlay ${item.status}`}>
                    {item.status === 'approved' ? '✓ APPROVED' : '✗ REJECTED'}
                  </div>
                ) : (
                  <div className="approval-card-actions">
                    <button
                      className="btn-tech-outline btn-small btn-approve"
                      onClick={() => handleApprovalAction(item.id, 'approve')}
                      disabled={actioningIds[item.id]}
                    >
                      {actioningIds[item.id] ? 'WAIT...' : 'APPROVE'}
                    </button>
                    <button
                      className="btn-tech-outline btn-small btn-reject"
                      onClick={() => handleApprovalAction(item.id, 'reject')}
                      disabled={actioningIds[item.id]}
                    >
                      {actioningIds[item.id] ? 'WAIT...' : 'REJECT'}
                    </button>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
