import { useState, useCallback, useEffect, useRef } from 'react';
import { useMsal, useIsAuthenticated } from '@azure/msal-react';
import { loginRequest } from './authConfig';

interface GroundingSource {
  id: string;
  title: string;
  url: string;
}

interface ChatMessage {
  id: string;
  sender: 'user' | 'assistant';
  text: string;
  timestamp: string;
  sources?: GroundingSource[];
  latency?: number;
  thoughtSteps?: string[];
}

interface DashboardCard {
  id: string;
  icon: 'meeting' | 'calendar' | 'warning' | 'attention' | 'lotus' | 'burger' | 'coffee';
  text: string;
  prompt?: string;
}

interface DashboardData {
  summary: DashboardCard[];
  actions: DashboardCard[];
  well_being: DashboardCard[];
}

function parseDraft(text: string) {
  const toMatch = text.match(/\*\*To:\*\*\s*([^\n\r]+)/i);
  const subjectMatch = text.match(/\*\*Subject:\*\*\s*([^\n\r]+)/i);
  if (toMatch && subjectMatch) {
    const to_address = toMatch[1].trim();
    const subject = subjectMatch[1].trim();
    
    // Attempt to extract body (the block starting after Subject line, up to *** or end of message)
    const idxSub = text.indexOf(subjectMatch[0]);
    let body = text.substring(idxSub + subjectMatch[0].length).trim();
    
    if (body.startsWith('***')) {
      body = body.substring(3).trim();
    }
    const idxEnd = body.indexOf('***');
    if (idxEnd !== -1) {
      body = body.substring(0, idxEnd).trim();
    }
    
    const idxLetMeKnow = body.toLowerCase().indexOf("let me know");
    if (idxLetMeKnow !== -1) {
      body = body.substring(0, idxLetMeKnow).trim();
    }
    return { to_address, subject, body };
  }
  return null;
}

export default function App() {
  const { instance, accounts } = useMsal();
  const isAuthenticated = useIsAuthenticated();
  
  // Custom user name display
  const rawName = accounts[0]?.name || accounts[0]?.username || 'Jesus';
  const displayName = rawName.split(' ')[0]; // E.g., "Jesus"

  const [lastRefreshed, setLastRefreshed] = useState<string>('9:18 AM');
  const [loading, setLoading] = useState(false);
  const [loadingChat, setLoadingChat] = useState(false);
  const [showThought, setShowThought] = useState<boolean>(true);
  const [chatInput, setChatInput] = useState('');
  
  // Dashboard details state (Summary, Actions, Well Being)
  const [dashboard, setDashboard] = useState<DashboardData>({
    summary: [
      {
        id: 's1',
        icon: 'meeting',
        text: 'Your next meeting is at 11:00 AM',
        prompt: 'Tell me more about the PxE Transformation Office onboarding meeting at 11:00 AM'
      },
      {
        id: 's2',
        icon: 'calendar',
        text: 'You have 5 other meetings today',
        prompt: 'Summarize my full schedule for today and list conflicts'
      }
    ],
    actions: [
      {
        id: 'a1',
        icon: 'warning',
        text: 'You have 1 compliance item due soon',
        prompt: 'Show details on the compliance item or interview that needs attention'
      },
      {
        id: 'a2',
        icon: 'attention',
        text: '1 email requires attention',
        prompt: 'Which emails require my attention or immediate action?'
      }
    ],
    well_being: [
      {
        id: 'w1',
        icon: 'lotus',
        text: "You're free at 11:30 AM — consider a 15-min stretch to recharge"
      },
      {
        id: 'w2',
        icon: 'burger',
        text: 'Even though you have a meeting, consider taking a lunch break at 1:30 PM'
      }
    ]
  });

  const [hiddenWellBeingIds, setHiddenWellBeingIds] = useState<string[]>([]);
  const [selectedCardId, setSelectedCardId] = useState<string>('');

  // Active chat session
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 'init-photosynthesis',
      sender: 'user',
      text: 'what is photosynthesis',
      timestamp: '9:18 AM'
    },
    {
      id: 'init-photosynthesis-reply',
      sender: 'assistant',
      text: `Photosynthesis is the process that plants, algae, and some bacteria use to convert sunlight, carbon dioxide, and water into food (energy) and oxygen.

Here is a simple breakdown of how it works:

* **Light Absorption:** Chlorophyll, the green pigment in plant leaves, absorbs light energy from the sun.
* **Chemical Conversion:** The plant uses this light energy to convert water (absorbed from the soil) and carbon dioxide (taken from the air) into glucose, which is a sugar that provides energy for the plant's growth.
* **Oxygen Release:** As a byproduct of this chemical reaction, oxygen is created and released back into the atmosphere, which is essential for most life on Earth.`,
      timestamp: '9:19 AM',
      thoughtSteps: [
        'Recognized photosynthesis question',
        'Retrieved core botanical processes',
        'Structured light absorption phases',
        'Formulated biochemical formulas (CO2 + H2O -> C6H12O6 + O2)',
        'Drafted multi-stage clean markdown overview',
        'Verified readability',
        'Finalized natural user-friendly description'
      ],
      sources: [
        { id: 'src1', title: 'Biology Textbook - Core Photosynthesis', url: 'https://en.wikipedia.org/wiki/Photosynthesis' }
      ]
    }
  ]);

  const [sentEmailIndexes, setSentEmailIndexes] = useState<Record<string, boolean>>({});
  const [sendingEmailIndexes, setSendingEmailIndexes] = useState<Record<string, boolean>>({});
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Scroll to bottom of chat
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loadingChat]);

  // Token helper
  const getToken = useCallback(async (): Promise<string | null> => {
    let account = accounts[0];
    if (!account) {
      return "mock-token";
    }
    try {
      const resp = await instance.acquireTokenSilent({ ...loginRequest, account });
      return resp.idToken;
    } catch {
      try {
        await instance.loginRedirect(loginRequest);
        return null;
      } catch {
        return "mock-token";
      }
    }
  }, [instance, accounts]);

  const handleConnectOutlook = async () => {
    const token = await getToken();
    if (!token) return;
    try {
      const resp = await fetch('/api/outlook/auth-url', {
        headers: { 'X-Entra-Id-Token': token }
      });
      if (resp.ok) {
        const data = await resp.json();
        if (data.auth_url) {
          const width = 600;
          const height = 650;
          const left = window.screen.width / 2 - width / 2;
          const top = window.screen.height / 2 - height / 2;
          window.open(data.auth_url, 'OutlookAuth', `width=${width},height=${height},left=${left},top=${top}`);
        }
      }
    } catch (e) {
      console.error("Connect Outlook error:", e);
    }
  };

  useEffect(() => {
    const handleOAuthMessage = (event: MessageEvent) => {
      if (event.data && event.data.type === 'outlook-oauth-callback') {
        if (event.data.success) {
          triggerRefresh();
        }
      }
    };
    window.addEventListener('message', handleOAuthMessage);
    return () => window.removeEventListener('message', handleOAuthMessage);
  }, []);

  const triggerRefresh = () => {
    setLastRefreshed(new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }));
    fetchDashboard();
  };

  // Fetch Dashboard items (Summary, Actions, Well Being)
  const fetchDashboard = async () => {
    setLoading(true);
    const token = await getToken();
    try {
      const resp = await fetch('/api/dashboard?lookback_hours=48&timezone=EST', {
        headers: { 'X-Entra-Id-Token': token || 'mock-token' },
      });
      if (resp.ok) {
        const data = await resp.json();
        if (data.summary || data.actions || data.well_being) {
          setDashboard({
            summary: data.summary || [],
            actions: data.actions || [],
            well_being: data.well_being || []
          });
        }
      }
    } catch (e) {
      console.error("Failed to query live dashboard data:", e);
    } finally {
      setLoading(false);
    }
  };

  // Fetch dashboard on initial mount
  useEffect(() => {
    fetchDashboard();
  }, []);

  const handleDismissWellBeing = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setHiddenWellBeingIds(prev => [...prev, id]);
  };

  const handleSendChat = async (textToSend?: string) => {
    const query = textToSend || chatInput;
    if (!query.trim()) return;

    setMessages(prev => [...prev, {
      id: Date.now().toString(),
      sender: 'user',
      text: query,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }]);
    if (!textToSend) setChatInput('');
    setLoadingChat(true);

    const token = await getToken();
    try {
      const startSec = Date.now();
      const resp = await fetch('/api/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Entra-Id-Token': token || 'mock-token'
        },
        body: JSON.stringify({ query: query })
      });
      
      const latency = parseFloat(((Date.now() - startSec) / 1000).toFixed(2));

      if (resp.ok) {
        const data = await resp.json();
        setMessages(prev => [...prev, {
          id: Date.now().toString(),
          sender: 'assistant',
          text: data.answer,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          sources: data.sources,
          latency: latency,
          thoughtSteps: [
            'Understanding query scope',
            'Retrieving relevant mailbox nodes via Graph API',
            'Applying contextual priority layers',
            'Formulating natural, secure answer response'
          ]
        }]);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoadingChat(false);
    }
  };

  const handleCardClick = (card: DashboardCard) => {
    setSelectedCardId(card.id);
    if (card.prompt) {
      handleSendChat(card.prompt);
    }
  };

  const sendEmailFromChat = async (msgId: string, to: string, subject: string, body: string) => {
    const token = await getToken();
    setSendingEmailIndexes(prev => ({ ...prev, [msgId]: true }));
    try {
      const resp = await fetch('/api/send-email', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Entra-Id-Token': token || 'mock-token',
        },
        body: JSON.stringify({ to_address: to, subject, body }),
      });
      const data = await resp.json();
      if (resp.ok && data.success) {
        setSentEmailIndexes(prev => ({ ...prev, [msgId]: true }));
      } else {
        alert(`Failed to send email: ${data.error || 'Unknown error'}`);
      }
    } catch (err: any) {
      alert(`Network error: ${err.message}`);
    } finally {
      setSendingEmailIndexes(prev => ({ ...prev, [msgId]: false }));
    }
  };

  return (
    <div className="app-container">
      {/* ── FAR-LEFT SKINNY SIDEBAR ── */}
      <aside className="skinny-sidebar">
        <div className="sidebar-top">
          <div className="avatar-bubble">
            <span>{displayName ? displayName.substring(0, 2).toUpperCase() : 'JA'}</span>
            <span className="badge-dot"></span>
          </div>
        </div>
        <div className="sidebar-bottom">
          <button className="sidebar-icon-btn" title="Settings" onClick={handleConnectOutlook}>
            <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
              <path d="M19.14 12.94c.04-.3.06-.61.06-.94 0-.32-.02-.64-.07-.94l2.03-1.58a.5.5 0 0 0 .12-.63l-1.92-3.32a.5.5 0 0 0-.6-.22l-2.39.96c-.5-.38-1.03-.7-1.62-.94l-.36-2.54a.5.5 0 0 0-.5-.42h-3.84a.5.5 0 0 0-.5.42l-.36 2.54c-.59.24-1.13.57-1.62.94l-2.39-.96a.5.5 0 0 0-.6.22L2.84 8.27a.5.5 0 0 0 .12.63l2.03 1.58c-.05.3-.07.62-.07.94s.02.64.07.94l-2.03 1.58a.5.5 0 0 0-.12.63l1.92 3.32c.12.22.37.29.6.22l2.39-.96c.5.38 1.03.7 1.62.94l.36 2.54c.05.24.27.42.5.42h3.84c.24 0 .46-.17.5-.42l.36-2.54c.59-.24 1.13-.56 1.62-.94l2.39.96c.22.08.47.01.6-.22l1.92-3.32a.5.5 0 0 0-.12-.63l-2.03-1.58zM12 15.6c-1.98 0-3.6-1.62-3.6-3.6s1.62-3.6 3.6-3.6 3.6 1.62 3.6 3.6-1.62 3.6-3.6 3.6z" />
            </svg>
          </button>
          <button className="sidebar-icon-btn" title="Create" onClick={() => handleSendChat('Draft a new email')}>
            <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
              <path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z" />
            </svg>
          </button>
        </div>
      </aside>

      {/* ── MAIN DASHBOARD CONTAINER ── */}
      <div className="main-content-layout">
        
        {/* ── LEFT PANE: GORGEOUS DELOITTE DASHBOARD ── */}
        <section className="dashboard-pane">
          <div className="dashboard-header">
            <div className="refresh-status-pill" onClick={triggerRefresh}>
              <span className="refresh-dot"></span>
              Last refreshed at {lastRefreshed}
            </div>
          </div>

          <div className="dashboard-greeting-section">
            <h1 className="greeting-text">Good afternoon, {displayName}!</h1>
            <p className="greeting-sub">
              Looking at your inbox from the last 48 hours and today's calendar, here's what still needs your attention:
            </p>
          </div>

          <div className="dashboard-scrollable-content">
            {loading ? (
              <div className="dashboard-loading">
                <span className="shining-spinner"></span>
                <span>UPDATING PORTAL CONTROLLER...</span>
              </div>
            ) : (
              <>
                {/* 1. SCHEDULE SUMMARY */}
                <div className="dashboard-category-block">
                  <div className="category-title-header">
                    <h2>SCHEDULE SUMMARY</h2>
                  </div>
                  <div className="cards-stack">
                    {dashboard.summary.map(card => (
                      <div 
                        key={card.id} 
                        className={`deloitte-card ${selectedCardId === card.id ? 'active' : ''}`}
                        onClick={() => handleCardClick(card)}
                      >
                        <div className="card-left">
                          <div className="card-icon-circle theme-blue">
                            {card.icon === 'meeting' ? (
                              <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor">
                                <path d="M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5s-3 1.34-3 3 1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z" />
                              </svg>
                            ) : (
                              <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor">
                                <path d="M19 4h-1V2h-2v2H8V2H6v2H5c-1.11 0-1.99.9-1.99 2L3 20a2 2 0 0 0 2 2h14c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 16H5V10h14v10zm-7-3h5v-5h-5v5z" />
                              </svg>
                            )}
                          </div>
                          <span className="card-message">{card.text}</span>
                        </div>
                        <div className="card-right">
                          <span className="chevron-arrow">›</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* 2. ACTION NEEDED */}
                <div className="dashboard-category-block">
                  <div className="category-title-header">
                    <h2>ACTION NEEDED</h2>
                  </div>
                  <div className="cards-stack">
                    {dashboard.actions.map(card => (
                      <div 
                        key={card.id} 
                        className={`deloitte-card ${selectedCardId === card.id ? 'active' : ''}`}
                        onClick={() => handleCardClick(card)}
                      >
                        <div className="card-left">
                          <div className={`card-icon-circle ${card.icon === 'warning' ? 'theme-orange' : 'theme-teal'}`}>
                            {card.icon === 'warning' ? (
                              <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor">
                                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z" />
                              </svg>
                            ) : (
                              <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor">
                                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 11h-2V7h2v6zm0 4h-2v-2h2v2z" />
                              </svg>
                            )}
                          </div>
                          <span className="card-message">{card.text}</span>
                        </div>
                        <div className="card-right">
                          <span className="chevron-arrow">›</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* 3. WELL BEING */}
                <div className="dashboard-category-block">
                  <div className="category-title-header">
                    <h2>💖 DON'T FORGET TO FOCUS ON YOURSELF!</h2>
                  </div>
                  <div className="cards-stack">
                    {dashboard.well_being
                      .filter(card => !hiddenWellBeingIds.includes(card.id))
                      .map(card => (
                        <div key={card.id} className="deloitte-card no-hover">
                          <div className="card-left">
                            <div className="card-icon-circle theme-green">
                              {card.icon === 'lotus' ? (
                                <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor">
                                  <path d="M12 3s-3.5 3.5-3.5 8c0 3.5 3.5 3.5 3.5 3.5s3.5 0 3.5-3.5c0-4.5-3.5-8-3.5-8zm0 10.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5zm0-8.5s2.5 3.5 2.5 6c0 1-.5 2-1.5 2.5-.5.25-1 .5-1 .5s-.5-.25-1-.5c-1-.5-1.5-1.5-1.5-2.5 0-2.5 2.5-6 2.5-6z" />
                                </svg>
                              ) : (
                                <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor">
                                  <path d="M12 2C8.14 2 5 5.14 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.86-3.14-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z" />
                                </svg>
                              )}
                            </div>
                            <span className="card-message-wellbeing">{card.text}</span>
                          </div>
                          <div className="card-right">
                            <button className="dismiss-btn" onClick={(e) => handleDismissWellBeing(card.id, e)}>×</button>
                          </div>
                        </div>
                      ))}
                    {dashboard.well_being.filter(card => !hiddenWellBeingIds.includes(card.id)).length === 0 && (
                      <div className="empty-wellbeing-placeholder">
                        ✓ All caught up! Excellent focus on personal health today.
                      </div>
                    )}
                  </div>
                </div>
              </>
            )}
          </div>
        </section>

        {/* ── RIGHT PANE: ASK ATHENA ANYTHING (CHAT CONSOLE) ── */}
        <section className="athena-chat-pane">
          <div className="athena-chat-header">
            <div className="topic-title">
              {messages.length > 0 ? messages[messages.length - 1].text.substring(0, 45) + (messages[messages.length - 1].text.length > 45 ? '...' : '') : 'Athena Intelligence'}
            </div>
            <div className="header-actions-group">
              <button className="control-btn" title="Refreshed mode" onClick={triggerRefresh}>
                <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor"><path d="M17.65 6.35A7.958 7.958 0 0 0 12 4c-4.42 0-7.99 3.58-7.99 8s3.57 8 7.99 8c3.73 0 6.84-2.55 7.73-6h-2.08A5.99 5.99 0 0 1 12 18c-3.31 0-6-2.69-6-6s2.69-6 6-6c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35z"/></svg>
              </button>
              <button className="control-btn" title="Add focus">
                <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor"><path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/></svg>
              </button>
              <button className="control-btn" title="Collapse thoughts" onClick={() => setShowThought(!showThought)}>
                <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor"><path d="M12 8l-6 6 1.41 1.41L12 10.83l4.59 4.58L18 14z"/></svg>
              </button>
            </div>
          </div>

          <div className="athena-chat-scroller">
            {messages.map((msg) => (
              <div key={msg.id} className={`chat-row ${msg.sender === 'user' ? 'row-user' : 'row-ai'}`}>
                {msg.sender === 'assistant' && (
                  <div className="ai-avatar-badge">DS</div>
                )}
                
                <div className="chat-bubble-container">
                  <div className="chat-bubble-body">
                    {/* Collapsible Thoughts segment */}
                    {msg.sender === 'assistant' && msg.thoughtSteps && msg.thoughtSteps.length > 0 && (
                      <div className="collapsible-thoughts-block">
                        <div className="thoughts-title" onClick={() => setShowThought(!showThought)}>
                          <span>💡 Thought for {msg.thoughtSteps.length} steps</span>
                          <span>{showThought ? '▲' : '▼'}</span>
                        </div>
                        {showThought && (
                          <ul className="thoughts-steps-list">
                            {msg.thoughtSteps.map((step, sIdx) => (
                              <li key={sIdx}>
                                <span className="step-num">{sIdx + 1}.</span> {step}
                              </li>
                            ))}
                          </ul>
                        )}
                      </div>
                    )}

                    {/* Sources citation indicator */}
                    {msg.sender === 'assistant' && msg.sources && msg.sources.length > 0 && (
                      <div className="citations-pill-box">
                        <span className="chain-link-icon">🔗</span>
                        <span>{msg.sources.length} sources</span>
                        <div className="citations-tooltip">
                          {msg.sources.map((src, sIdx) => (
                            <a key={sIdx} href={src.url} target="_blank" rel="noopener noreferrer">
                              {src.title}
                            </a>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Render standard text cleanly formatted */}
                    <div className="markdown-render">
                      {msg.text.split('\n\n').map((para, pIdx) => {
                        if (para.trim().startsWith('* ')) {
                          return (
                            <ul key={pIdx}>
                              {para.split('\n').map((li, lIdx) => (
                                <li key={lIdx}>{li.replace(/^\*\s+/, '')}</li>
                              ))}
                            </ul>
                          );
                        }
                        return <p key={pIdx}>{para}</p>;
                      })}
                    </div>

                    {/* Embedded interactive email layout draft box */}
                    {msg.sender === 'assistant' && parseDraft(msg.text) && (
                      (() => {
                        const d = parseDraft(msg.text)!;
                        const isSent = sentEmailIndexes[msg.id];
                        const isSending = sendingEmailIndexes[msg.id];
                        return (
                          <div className="embedded-draft-container">
                            <div className="draft-header">
                              <span className="draft-category-badge">DRAFTED EMAIL ACTION REQUIRED</span>
                              {isSent && <span className="sent-indicator">✓ SENT</span>}
                            </div>
                            <div className="draft-meta">
                              <strong>To:</strong> <span>{d.to_address}</span><br />
                              <strong>Subject:</strong> <span>{d.subject}</span>
                            </div>
                            <pre className="draft-preview-body">{d.body}</pre>
                            <button
                              className="btn-approve-draft"
                              disabled={isSent || isSending}
                              onClick={() => sendEmailFromChat(msg.id, d.to_address, d.subject, d.body)}
                            >
                              {isSending ? 'SENDING...' : isSent ? '✓ EMAIL SENT' : 'APPROVE & SEND EMAIL'}
                            </button>
                          </div>
                        );
                      })()
                    )}
                  </div>

                  <div className="bubble-footer-meta">
                    <span>LATENCY: {msg.latency !== undefined ? `${msg.latency}s` : msg.sender === 'user' ? '0.01s' : '0.85s'}</span>
                    <span>MODEL: GEMINI 2.5 FLASH</span>
                  </div>
                </div>
              </div>
            ))}

            {loadingChat && (
              <div className="chat-row row-ai">
                <div className="ai-avatar-badge animated-glow">DS</div>
                <div className="chat-bubble-container">
                  <div className="chat-bubble-body flex-align">
                    <span className="shining-spinner mini"></span>
                    <span className="analyzing-text text-animated">Consulting Graph API connectors...</span>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* ── ATHENA CHAT FIELD INPUT AREA ── */}
          <div className="athena-input-form-box">
            <div className="input-group-field">
              <input
                type="text"
                className="premium-athena-input"
                placeholder="Ask Athena anything..."
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSendChat()}
              />
              <button className="submit-arrow-btn" onClick={() => handleSendChat()}>
                <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor">
                  <path d="M5 13h11.86l-5.43 5.43 1.42 1.42L21.14 12l-8.29-8.29-1.42 1.42L16.86 11H5v2z"/>
                </svg>
              </button>
            </div>
          </div>
        </section>

      </div>
    </div>
  );
}
