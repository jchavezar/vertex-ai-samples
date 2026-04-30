import { useState, useEffect, useRef, useMemo } from 'react';
import { flushSync } from 'react-dom';
import { useMsal, useIsAuthenticated } from '@azure/msal-react';
import { loginRequest } from './authConfig';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import {
  MessageSquare, Plus, FileText, ChevronRight,
  Shield, Sparkles, Send, ExternalLink, LogIn, LogOut, Clock, Globe, Database, User, Bot, Trash2, Zap,
  Brain, ChevronDown
} from 'lucide-react';
import SourceDrawer, { type DrawerSource } from './SourceDrawer';
import AuthFlowOverlay, { type ConnectorInfo } from './AuthFlowOverlay';
import './index.css';

interface Source {
  title: string;
  url: string;
  snippet: string;
  page?: number;
}

interface GroundingSupport {
  startIndex: number;
  endIndex: number;
  sourceIndices: number[];
}

interface Thought {
  text: string;
  createTime?: string;
}

interface Timings {
  sts_ms: number;
  retrieval_ms: number;
  generation_ms: number;
}

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources: Source[];
  supports?: GroundingSupport[];
  thoughts?: Thought[];
  timings?: Timings;
  latencyMs?: number;
  timestamp: Date;
  isQuick?: boolean;  // /btw quick response
  isLoading?: boolean;
}

interface WhoAmI {
  authenticated: boolean;
  username: string | null;
  sts_valid_seconds: number;
  doc_scope_count: number;
  tenant?: string;
  jwt_iat?: number; // epoch seconds
  jwt_exp?: number; // epoch seconds
}

// 13 product names for quick-chip suggestions
const PRODUCTS = [
  'aimovig', 'blincyto', 'enbrel', 'evenity', 'kyprolis', 'lumakras',
  'neulasta', 'nplate', 'otezla', 'prolia', 'repatha', 'vectibix', 'xgeva'
];

function detectProducts(text: string): string[] {
  if (!text) return [];
  const lower = text.toLowerCase();
  const found: string[] = [];
  for (const p of PRODUCTS) {
    if (lower.includes(p) && !found.includes(p)) found.push(p);
  }
  return found;
}

function buildChipsForProducts(products: string[]): { label: string; query: string }[] {
  const chips: { label: string; query: string }[] = [];
  const templates = [
    (p: string) => ({ label: `How is ${cap(p)} stored?`, query: `How is ${cap(p)} stored?` }),
    (p: string) => ({ label: `Who shouldn't take ${cap(p)}?`, query: `Who shouldn't take ${cap(p)}?` }),
    (p: string) => ({ label: `Common side effects of ${cap(p)}`, query: `What are the common side effects of ${cap(p)}?` }),
  ];
  for (const p of products) {
    for (const t of templates) {
      if (chips.length >= 3) return chips;
      chips.push(t(p));
    }
  }
  return chips.slice(0, 3);
}

const cap = (s: string) => s.charAt(0).toUpperCase() + s.slice(1).toLowerCase();

interface Conversation {
  id: string;
  sessionId: string | null;
  title: string;
  messages: Message[];
  createdAt: Date;
}

// Claude Code style random thinking words
const THINKING_WORDS = [
  'Incubating',
  'Ideating',
  'Pondering',
  'Reflecting',
  'Synthesizing',
  'Connecting',
  'Exploring',
  'Analyzing',
  'Reasoning',
  'Contemplating',
  'Processing',
  'Searching',
  'Grounding',
  'Discovering',
  'Weaving',
  'Assembling',
  'Crystallizing'
];

function App() {
  const { instance, accounts } = useMsal();
  const isAuthenticated = useIsAuthenticated();
  const [tokens, setTokens] = useState<{ accessToken: string; idToken: string } | null>(null);

  const [query, setQuery] = useState('');
  const [mounted, setMounted] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [elapsedMs, setElapsedMs] = useState<number>(0);
  const [thinkingWord, setThinkingWord] = useState(THINKING_WORDS[0]);
  const [sharepointOnly, setSharepointOnly] = useState(true);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeConversationId, setActiveConversationId] = useState<string | null>(null);
  const [whoami, setWhoami] = useState<WhoAmI | null>(null);
  const [stsValidUntil, setStsValidUntil] = useState<number | null>(null); // epoch ms
  const [stsCountdown, setStsCountdown] = useState<string>('');
  const [drawerSource, setDrawerSource] = useState<DrawerSource | null>(null);
  const [highlightedSource, setHighlightedSource] = useState<{ msgId: string; idx: number } | null>(null);
  const [showAuthFlow, setShowAuthFlow] = useState(false);
  const [connectorInfo, setConnectorInfo] = useState<ConnectorInfo | null>(null);
  const startTimeRef = useRef<number>(0);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const sourceChipRefs = useRef<Map<string, HTMLAnchorElement>>(new Map());

  const activeConversation = conversations.find(c => c.id === activeConversationId);

  // Open drawer + highlight + scroll to chip
  const openSource = (msgId: string, src: Source, idx: number) => {
    setDrawerSource(src);
    setHighlightedSource({ msgId, idx });
    const key = `${msgId}::${idx}`;
    const el = sourceChipRefs.current.get(key);
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
    // Auto-clear highlight after 2s
    setTimeout(() => setHighlightedSource(prev => (prev?.msgId === msgId && prev?.idx === idx) ? null : prev), 2000);
  };

  useEffect(() => {
    setMounted(true);
    // Only create if no conversations exist (prevents StrictMode duplicate)
    setConversations(prev => {
      if (prev.length === 0) {
        const newConv: Conversation = {
          id: Date.now().toString(),
          sessionId: null,
          title: 'New Chat',
          messages: [],
          createdAt: new Date()
        };
        setActiveConversationId(newConv.id);
        return [newConv];
      }
      return prev;
    });
  }, []);

  // Elapsed time counter
  useEffect(() => {
    if (!isLoading) return;
    const interval = setInterval(() => {
      setElapsedMs(Math.round(performance.now() - startTimeRef.current));
    }, 100);
    return () => clearInterval(interval);
  }, [isLoading]);

  // Random thinking word rotation (Claude Code style)
  useEffect(() => {
    if (!isLoading) {
      setThinkingWord(THINKING_WORDS[0]);
      return;
    }
    // Change word every 2-4 seconds randomly
    const changeWord = () => {
      const randomIndex = Math.floor(Math.random() * THINKING_WORDS.length);
      setThinkingWord(THINKING_WORDS[randomIndex]);
    };
    changeWord(); // Initial word
    const interval = setInterval(changeWord, 2000 + Math.random() * 2000);
    return () => clearInterval(interval);
  }, [isLoading]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [activeConversation?.messages]);

  useEffect(() => {
    if (isAuthenticated && accounts[0]) {
      const request = { ...loginRequest, account: accounts[0] };
      const acquireTokens = async () => {
        try {
          const response = await instance.acquireTokenSilent(request);
          setTokens({ accessToken: response.accessToken, idToken: response.idToken || '' });
        } catch {
          try {
            const response = await instance.acquireTokenPopup(request);
            setTokens({ accessToken: response.accessToken, idToken: response.idToken || '' });
          } catch (popupError) {
            console.error('[Auth] Popup error:', popupError);
          }
        }
      };
      acquireTokens();
      const interval = setInterval(acquireTokens, 5 * 60 * 1000);
      return () => clearInterval(interval);
    } else {
      setTokens(null);
      setWhoami(null);
      setStsValidUntil(null);
    }
  }, [isAuthenticated, accounts, instance]);

  // /api/whoami — called ONCE per token refresh, NOT per chat
  useEffect(() => {
    if (!tokens?.accessToken) return;
    let cancelled = false;
    fetch('/api/whoami', { headers: { 'X-Entra-Id-Token': tokens.accessToken } })
      .then(r => r.json())
      .then((data: WhoAmI) => {
        if (cancelled) return;
        setWhoami(data);
        if (data.sts_valid_seconds > 0) {
          setStsValidUntil(Date.now() + data.sts_valid_seconds * 1000);
        }
      })
      .catch(e => console.error('[whoami] error:', e));
    return () => { cancelled = true; };
  }, [tokens?.accessToken]);

  // STS countdown ticker for the ACL strip (1Hz)
  useEffect(() => {
    if (!stsValidUntil) { setStsCountdown(''); return; }
    const tick = () => {
      const remaining = Math.max(0, Math.round((stsValidUntil - Date.now()) / 1000));
      if (remaining <= 0) { setStsCountdown('expired'); return; }
      const m = Math.floor(remaining / 60);
      const s = remaining % 60;
      setStsCountdown(m > 0 ? `${m}m ${s}s` : `${s}s`);
    };
    tick();
    const id = setInterval(tick, 1000);
    return () => clearInterval(id);
  }, [stsValidUntil]);

  // Lazy fetch /api/connector-info on first overlay open. Cache in state.
  useEffect(() => {
    if (!showAuthFlow || connectorInfo !== null || !tokens?.accessToken) return;
    let cancelled = false;
    fetch('/api/connector-info', { headers: { 'X-Entra-Id-Token': tokens.accessToken } })
      .then(r => r.json())
      .then((data: ConnectorInfo) => {
        if (cancelled) return;
        setConnectorInfo(data);
      })
      .catch(e => console.error('[connector-info] error:', e));
    return () => { cancelled = true; };
  }, [showAuthFlow, connectorInfo, tokens?.accessToken]);

  // Global Shift+S keybind to summon the auth-flow overlay from any focus state.
  // Intentionally ignores typing into inputs/textareas/contentEditable to avoid
  // hijacking the chat input.
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key !== 'S' || !e.shiftKey) return;
      if (e.metaKey || e.ctrlKey || e.altKey) return;
      const t = e.target as HTMLElement | null;
      if (t) {
        const tag = t.tagName;
        if (tag === 'INPUT' || tag === 'TEXTAREA' || t.isContentEditable) return;
      }
      e.preventDefault();
      setShowAuthFlow(s => !s);
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, []);

  const createNewConversation = () => {
    const newConv: Conversation = {
      id: Date.now().toString(),
      sessionId: null,
      title: 'New Chat',
      messages: [],
      createdAt: new Date()
    };
    setConversations(prev => [newConv, ...prev]);
    setActiveConversationId(newConv.id);
  };

  const deleteConversation = (id: string) => {
    setConversations(prev => prev.filter(c => c.id !== id));
    if (activeConversationId === id) {
      const remaining = conversations.filter(c => c.id !== id);
      if (remaining.length > 0) {
        setActiveConversationId(remaining[0].id);
      } else {
        createNewConversation();
      }
    }
  };

  const handleLogin = () => {
    instance.loginPopup(loginRequest).catch(e => console.error('[Auth] Login error:', e));
  };

  const handleLogout = () => {
    instance.logoutPopup().catch(e => console.error('[Auth] Logout error:', e));
  };


  // Handle /btw quick question - adds to conversation, backend now async with workers
  const handleQuickAsk = (question: string) => {
    const convId = activeConversationId;
    if (!convId) return;

    const msgId = `quick-${Date.now()}`;

    // Add user message + loading placeholder
    setConversations(prev => prev.map(conv => {
      if (conv.id === convId) {
        return {
          ...conv,
          messages: [
            ...conv.messages,
            {
              id: `${msgId}-user`,
              role: 'user' as const,
              content: `/btw ${question}`,
              sources: [],
              timestamp: new Date(),
              isQuick: true
            },
            {
              id: `${msgId}-response`,
              role: 'assistant' as const,
              content: '',
              sources: [],
              timestamp: new Date(),
              isQuick: true,
              isLoading: true
            }
          ]
        };
      }
      return conv;
    }));

    const quickStart = performance.now();

    fetch('/api/quick', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: question, context: '' })
    })
      .then(r => r.json())
      .then(data => {
        const latency = Math.round(performance.now() - quickStart);
        // Use flushSync to force IMMEDIATE render - don't wait for main chat
        flushSync(() => {
          setConversations(prev => prev.map(conv => {
            if (conv.id === convId) {
              return {
                ...conv,
                messages: conv.messages.map(m =>
                  m.id === `${msgId}-response`
                    ? { ...m, content: data.answer || 'No response', sources: data.sources || [], latencyMs: latency, isLoading: false }
                    : m
                )
              };
            }
            return conv;
          }));
        });
      })
      .catch(() => {
        flushSync(() => {
          setConversations(prev => prev.map(conv => {
            if (conv.id === convId) {
              return {
                ...conv,
                messages: conv.messages.map(m =>
                  m.id === `${msgId}-response`
                    ? { ...m, content: 'Quick response failed', isLoading: false }
                    : m
                )
              };
            }
            return conv;
          }));
        });
      });
  };

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim() || !activeConversationId) return;

    // Check for /btw command
    if (query.startsWith('/btw ')) {
      const question = query.slice(5).trim();
      setQuery('');
      handleQuickAsk(question);
      inputRef.current?.focus();
      return;
    }

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: query,
      sources: [],
      timestamp: new Date()
    };

    // Add loading placeholder
    const loadingMessage: Message = {
      id: (Date.now() + 1).toString(),
      role: 'assistant',
      content: '',
      sources: [],
      timestamp: new Date(),
      isLoading: true
    };

    setConversations(prev => prev.map(conv => {
      if (conv.id === activeConversationId) {
        const isFirstMessage = conv.messages.length === 0;
        return {
          ...conv,
          messages: [...conv.messages, userMessage, loadingMessage],
          title: isFirstMessage ? query.slice(0, 35) + (query.length > 35 ? '...' : '') : conv.title
        };
      }
      return conv;
    }));

    const currentQuery = query;
    const currentSessionId = activeConversation?.sessionId;
    setQuery('');  // Clear immediately - non-blocking
    setIsLoading(true);
    setElapsedMs(0);
    startTimeRef.current = performance.now();

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(tokens?.accessToken ? { 'X-Entra-Id-Token': tokens.accessToken } : {})
        },
        body: JSON.stringify({
          query: currentQuery,
          sharepoint_only: sharepointOnly,
          session_id: currentSessionId || null
        })
      });

      const elapsed = Math.round(performance.now() - startTimeRef.current);
      const data = await response.json();

      // Replace loading message with actual response (preserve /btw quick messages)
      setConversations(prev => prev.map(conv => {
        if (conv.id === activeConversationId) {
          // Only remove the main loading message, keep /btw quick loading messages
          const messages = conv.messages.filter(m => !m.isLoading || m.isQuick);
          const assistantMessage: Message = {
            id: (Date.now() + 2).toString(),
            role: 'assistant',
            content: data.answer || 'No response received.',
            sources: data.sources || [],
            supports: data.supports || [],
            thoughts: data.thoughts || [],
            timings: data.timings,
            latencyMs: elapsed,
            timestamp: new Date()
          };
          return {
            ...conv,
            messages: [...messages, assistantMessage],
            sessionId: data.session_id || conv.sessionId
          };
        }
        return conv;
      }));

    } catch (err) {
      setConversations(prev => prev.map(conv => {
        if (conv.id === activeConversationId) {
          const messages = conv.messages.filter(m => !m.isLoading || m.isQuick);
          const errorMessage: Message = {
            id: (Date.now() + 2).toString(),
            role: 'assistant',
            content: `Connection Error: ${err}`,
            sources: [],
            latencyMs: Math.round(performance.now() - startTimeRef.current),
            timestamp: new Date()
          };
          return { ...conv, messages: [...messages, errorMessage] };
        }
        return conv;
      }));
    } finally {
      setIsLoading(false);
      inputRef.current?.focus();
    }
  };

  const formatLatency = (ms: number) => ms >= 1000 ? `${(ms / 1000).toFixed(1)}s` : `${ms}ms`;

  /**
   * Inject [n] superscripts into the answer Markdown using support segments.
   * Supports come with byte offsets into the answer text. We sort them by
   * startIndex desc and splice "[n]" markers AFTER each segment's endIndex.
   * The resulting string still parses cleanly as Markdown; we then post-process
   * the rendered output via a custom renderer to make the bracketed numbers
   * clickable. To keep things simple we use a unicode-safe text replacement
   * combined with React-friendly text-node walking via a simple regex render
   * inside paragraphs/list items.
   */
  const annotateWithCitations = (text: string, supports?: GroundingSupport[]): string => {
    if (!supports || supports.length === 0 || !text) return text;
    // Group supports by endIndex to avoid duplicate markers; combine source indices
    type Marker = { at: number; sources: number[] };
    const byEnd = new Map<number, Set<number>>();
    for (const s of supports) {
      if (typeof s.endIndex !== 'number') continue;
      const set = byEnd.get(s.endIndex) || new Set<number>();
      s.sourceIndices.forEach(i => set.add(i));
      byEnd.set(s.endIndex, set);
    }
    const markers: Marker[] = Array.from(byEnd.entries())
      .map(([at, set]) => ({ at, sources: Array.from(set).sort((a, b) => a - b) }))
      .sort((a, b) => b.at - a.at);
    let out = text;
    for (const m of markers) {
      const at = Math.min(m.at, out.length);
      // Encode as ⟦n⟧ (unique sentinel) so Markdown won't eat it; we'll
      // post-process to clickable spans below.
      const tag = m.sources.map(i => `⟦${i + 1}⟧`).join('');
      out = out.slice(0, at) + tag + out.slice(at);
    }
    return out;
  };

  // Render text-with-citations: split on ⟦n⟧ sentinels into clickable spans.
  const renderWithCitations = (children: React.ReactNode, msgId: string, sources: Source[]): React.ReactNode => {
    if (typeof children === 'string') {
      const parts = children.split(/(⟦\d+⟧)/g);
      if (parts.length === 1) return children;
      return parts.map((part, i) => {
        const m = /^⟦(\d+)⟧$/.exec(part);
        if (!m) return part;
        const n = parseInt(m[1], 10);
        const idx = n - 1;
        const src = sources[idx];
        if (!src) return part;
        return (
          <sup
            key={i}
            className="inline-cite"
            onClick={(e) => { e.preventDefault(); openSource(msgId, src, idx); }}
            title={src.title}
          >
            [{n}]
          </sup>
        );
      });
    }
    if (Array.isArray(children)) {
      return children.map((c, i) => <span key={i}>{renderWithCitations(c, msgId, sources)}</span>);
    }
    return children;
  };

  if (!mounted) return null;

  return (
    <div className="workspace-container">
      {/* Login overlay - grays out everything until authenticated */}
      {!isAuthenticated && (
        <div className="auth-overlay">
          <div className="auth-modal glass-panel">
            <Shield size={48} className="auth-icon" />
            <h2>Authentication Required</h2>
            <p>Sign in with your Microsoft account to access Amgen Science Search</p>
            <button className="auth-login-btn" onClick={handleLogin}>
              <LogIn size={18} />
              Sign in with Microsoft
            </button>
          </div>
        </div>
      )}
      <aside className="sidebar glass-panel">
        <div className="brand">
          <img src="/amgen-logo.svg" alt="Amgen" className="brand-logo" />
          <div className="brand-info">
            <span className="brand-name">Science Search</span>
            <span className="brand-tagline">SharePoint + WIF</span>
          </div>
        </div>

        <div className="sidebar-actions">
          <button className="new-chat-btn" onClick={createNewConversation}>
            <Plus size={16} />
            <span>New Chat</span>
          </button>
        </div>

        <nav className="sidebar-nav">
          <div className="nav-group">
            <span className="nav-label">Conversations</span>
            {conversations.length === 0 ? (
              <div className="nav-sub-item" style={{ opacity: 0.5 }}>
                <span>No conversations yet</span>
              </div>
            ) : (
              conversations.map(conv => (
                <div
                  key={conv.id}
                  className={`conversation-item ${activeConversationId === conv.id ? 'active' : ''}`}
                >
                  <button
                    className="conversation-btn"
                    onClick={() => setActiveConversationId(conv.id)}
                  >
                    <MessageSquare size={14} />
                    <span className="truncate">{conv.title}</span>
                    <span className="msg-count">{conv.messages.filter(m => m.role === 'user').length}</span>
                  </button>
                  <button
                    className="delete-btn"
                    onClick={(e) => { e.stopPropagation(); deleteConversation(conv.id); }}
                    title="Delete conversation"
                  >
                    <Trash2 size={12} />
                  </button>
                </div>
              ))
            )}
          </div>
        </nav>

        <div className="sidebar-footer glass-panel">
          <span className="powered-by">Powered by Gemini Enterprise</span>
        </div>
      </aside>

      <main className="main-canvas">
        <SourceDrawer
          source={drawerSource}
          onClose={() => setDrawerSource(null)}
          entraToken={tokens?.accessToken || null}
        />
        <AuthFlowOverlay
          isOpen={showAuthFlow}
          onClose={() => setShowAuthFlow(false)}
          username={accounts[0]?.username || whoami?.username || ''}
          jwtIat={whoami?.jwt_iat ? new Date(whoami.jwt_iat * 1000) : null}
          jwtExp={whoami?.jwt_exp ? new Date(whoami.jwt_exp * 1000) : null}
          tenant={whoami?.tenant}
          sources={(() => {
            const lastA = [...(activeConversation?.messages || [])]
              .reverse()
              .find(m => m.role === 'assistant' && !m.isLoading && !m.isQuick);
            return lastA?.sources || [];
          })()}
          connectorInfo={connectorInfo}
        />
        <header className="canvas-header glass-panel">
          <div className="header-status">
            <div className="status-dot" style={{ background: isAuthenticated ? '#92BE43' : '#0063C3' }}></div>
            <span className="status-pill">
              {isAuthenticated ? `${accounts[0]?.username}` : 'Not authenticated'}
            </span>
          </div>
          <div className="header-actions">
            {isAuthenticated ? (
              <button className="action-btn-sm" onClick={handleLogout}>
                <LogOut size={14} />
                Logout
              </button>
            ) : (
              <button className="action-btn-sm premium" onClick={handleLogin}>
                <LogIn size={14} />
                Login with Microsoft
              </button>
            )}
            <button
              className={`action-btn-sm ${sharepointOnly ? 'active' : ''}`}
              onClick={() => setSharepointOnly(!sharepointOnly)}
              title={sharepointOnly ? 'SharePoint Only' : 'Google Search enabled'}
            >
              {sharepointOnly ? <Database size={14} /> : <Globe size={14} />}
              {sharepointOnly ? 'SharePoint Only' : '+ Google Search'}
            </button>
            <button className="action-btn-sm premium">
              <Shield size={14} />
              {isAuthenticated ? 'ACL Protected' : 'Public'}
            </button>
          </div>
        </header>

        {/* ACL Trust Strip */}
        {whoami?.authenticated && (
          <div className="acl-strip">
            <Shield size={11} className="acl-strip-icon" />
            <span className="acl-strip-text">
              Showing results for <strong>{whoami.username}</strong>
              <span className="acl-strip-sep">·</span>
              <strong>{whoami.doc_scope_count}</strong> connector{whoami.doc_scope_count === 1 ? '' : 's'} in scope
              <span className="acl-strip-sep">·</span>
              STS {stsCountdown === 'expired' ? <span className="acl-strip-expired">expired</span> : <>valid <strong>{stsCountdown}</strong></>}
            </span>
            <button
              type="button"
              className="acl-strip-flow-btn"
              onClick={() => setShowAuthFlow(true)}
              title="View auth flow (Shift+S)"
              aria-label="View auth flow"
            >
              <Shield size={11} />
              <span>flow</span>
            </button>
          </div>
        )}

        <div className="chat-container">
          {activeConversation?.messages.length === 0 ? (
            <div className="welcome-screen">
              <h1 className="hero-title">Amgen Science Search</h1>
              <p>Ask questions across Amgen's SharePoint — protocols, study reports, SOPs, pipeline updates — grounded with per-user ACLs. Use <code>/btw</code> for quick side questions while waiting.</p>
              <div className="quick-prompts">
                {['What is AIMOVIG?', 'How does Otezla work?', 'Compare Prolia and Xgeva dosing', 'Otezla renal impairment dose'].map((prompt, i) => (
                  <button key={i} className="quick-prompt" onClick={() => setQuery(prompt)}>
                    <ChevronRight size={14} />
                    {prompt}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div className="messages-container">
              {activeConversation?.messages.map((msg) => (
                <div key={msg.id} className={`message ${msg.role} ${msg.isQuick ? 'quick' : ''} ${msg.isLoading ? 'loading' : ''}`}>
                  <div className="message-avatar">
                    {msg.role === 'user' ? (
                      msg.isQuick ? <Zap size={18} /> : <User size={18} />
                    ) : (
                      <Bot size={18} />
                    )}
                  </div>
                  <div className="message-content">
                    {msg.isLoading && !msg.isQuick ? (
                      <div className="thinking-container">
                        <div className="thinking-indicator">
                          <div className="thinking-icon-wrapper">
                            <Sparkles size={16} className="thinking-icon" />
                          </div>
                          <span className="thinking-word">{thinkingWord}...</span>
                          <span className="thinking-status">(thinking)</span>
                        </div>
                        <div className="thinking-timer">
                          {formatLatency(elapsedMs)} elapsed
                        </div>
                      </div>
                    ) : msg.isLoading && msg.isQuick ? (
                      <div className="quick-loading">
                        <span className="claude-spinner"></span>
                        <span className="sweep-text">Answering...</span>
                      </div>
                    ) : (
                      <>
                        {msg.role === 'assistant' && msg.latencyMs && (
                          <div className="message-meta">
                            {msg.isQuick && <Zap size={10} className="quick-icon" />}
                            <Clock size={12} />
                            <span>{formatLatency(msg.latencyMs)}</span>
                            {msg.isQuick && <span className="quick-badge">quick</span>}
                            {!msg.isQuick && msg.timings && (
                              <LatencyBadge timings={msg.timings} totalMs={msg.latencyMs} />
                            )}
                          </div>
                        )}
                        <div className="message-text">
                          {msg.role === 'user' ? (
                            <p>{msg.content}</p>
                          ) : (
                            <ReactMarkdown
                              remarkPlugins={[remarkGfm]}
                              components={{
                                p: ({ children }) => <p>{renderWithCitations(children, msg.id, msg.sources)}</p>,
                                li: ({ children }) => <li>{renderWithCitations(children, msg.id, msg.sources)}</li>,
                                strong: ({ children }) => <strong>{renderWithCitations(children, msg.id, msg.sources)}</strong>,
                                em: ({ children }) => <em>{renderWithCitations(children, msg.id, msg.sources)}</em>,
                                td: ({ children }) => <td>{renderWithCitations(children, msg.id, msg.sources)}</td>,
                              }}
                            >
                              {annotateWithCitations(msg.content, msg.supports)}
                            </ReactMarkdown>
                          )}
                        </div>
                        {msg.role === 'assistant' && !msg.isQuick && msg.thoughts && msg.thoughts.length > 0 && (
                          <details className="thinking-trace">
                            <summary>
                              <ChevronDown size={12} className="thinking-trace-chevron" />
                              <Brain size={12} />
                              <span>Show thinking ({msg.thoughts.length} step{msg.thoughts.length === 1 ? '' : 's'})</span>
                            </summary>
                            <div className="thinking-trace-body">
                              {msg.thoughts.map((t, i) => (
                                <div key={i} className="thinking-trace-step">
                                  <span className="thinking-trace-marker">▸</span>
                                  <span className="thinking-trace-text">{t.text}</span>
                                </div>
                              ))}
                            </div>
                          </details>
                        )}
                        {msg.sources.length > 0 && (
                          <div className="message-sources">
                            {msg.sources.map((src, i) => {
                              const refKey = `${msg.id}::${i}`;
                              const isHl = highlightedSource?.msgId === msg.id && highlightedSource?.idx === i;
                              return (
                                <a
                                  key={i}
                                  ref={(el) => {
                                    if (el) sourceChipRefs.current.set(refKey, el);
                                    else sourceChipRefs.current.delete(refKey);
                                  }}
                                  href={src.url}
                                  onClick={(e) => { e.preventDefault(); openSource(msg.id, src, i); }}
                                  className={`source-chip ${isHl ? 'highlighted' : ''}`}
                                  title={src.title}
                                >
                                  <span className="source-chip-num">{i + 1}</span>
                                  <FileText size={12} />
                                  <span>{src.title}</span>
                                  <ExternalLink size={10} />
                                </a>
                              );
                            })}
                          </div>
                        )}
                        {msg.role === 'assistant' && !msg.isQuick && !msg.isLoading && (
                          <ProductChips
                            answer={msg.content}
                            onPick={(q) => { setQuery(q); inputRef.current?.focus(); }}
                          />
                        )}
                      </>
                    )}
                  </div>
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>
          )}

          <div className="input-container">
            <form onSubmit={handleSend} className="chat-form">
              <div className="input-wrapper">
                <input
                  ref={inputRef}
                  type="text"
                  placeholder={isLoading ? "Type /btw for a quick side question while waiting..." : "Ask about Amgen science, protocols, or pipeline..."}
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  className={`chat-input ${query.startsWith('/btw') ? 'has-command' : ''}`}
                />
                {/* Command indicator badge */}
                {query.startsWith('/btw') && (
                  <span className="cmd-badge">QUICK</span>
                )}
              </div>
              <button type="submit" className="send-btn" disabled={!query.trim()}>
                {query.startsWith('/btw ') ? <Zap size={18} /> : <Send size={18} />}
              </button>
            </form>

            {/* Autocomplete dropdown for /btw - shows below input */}
            {query === '/' || query === '/b' || query === '/bt' || query === '/btw' ? (
              <div className="autocomplete-dropdown">
                <div
                  className="autocomplete-item"
                  onClick={() => { setQuery('/btw '); inputRef.current?.focus(); }}
                >
                  <span className="autocomplete-cmd">/btw</span>
                  <span className="autocomplete-desc">Ask a quick side question without interrupting the main conversation</span>
                </div>
              </div>
            ) : (
              <div className={`input-hint ${isLoading ? 'visible' : ''}`}>
                <Zap size={12} style={{ display: 'inline', verticalAlign: 'middle', marginRight: 4 }} />
                <span>Type <kbd>/btw</kbd> for instant Gemini response</span>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

// ============ Helper components ============

function LatencyBadge({ timings, totalMs }: { timings: Timings; totalMs: number }) {
  const sum = Math.max(1, timings.sts_ms + timings.retrieval_ms + timings.generation_ms);
  const stsPct = (timings.sts_ms / sum) * 100;
  const retPct = (timings.retrieval_ms / sum) * 100;
  const genPct = (timings.generation_ms / sum) * 100;
  const fmt = (ms: number) => ms >= 1000 ? `${(ms / 1000).toFixed(1)}s` : `${ms}ms`;
  return (
    <span className="latency-breakdown" title={`STS ${fmt(timings.sts_ms)} · Retrieval ${fmt(timings.retrieval_ms)} · Gen ${fmt(timings.generation_ms)} · Total ${fmt(totalMs)}`}>
      <span className="latency-text">
        STS <strong>{fmt(timings.sts_ms)}</strong>
        <span className="latency-dot">·</span>
        DE <strong>{fmt(timings.retrieval_ms)}</strong>
        <span className="latency-dot">·</span>
        Gen <strong>{fmt(timings.generation_ms)}</strong>
      </span>
      <span className="latency-bar" aria-hidden="true">
        <span className="latency-bar-seg latency-bar-sts" style={{ width: `${stsPct}%` }} />
        <span className="latency-bar-seg latency-bar-ret" style={{ width: `${retPct}%` }} />
        <span className="latency-bar-seg latency-bar-gen" style={{ width: `${genPct}%` }} />
      </span>
    </span>
  );
}

function ProductChips({ answer, onPick }: { answer: string; onPick: (q: string) => void }) {
  const chips = useMemo(() => buildChipsForProducts(detectProducts(answer)), [answer]);
  if (chips.length === 0) return null;
  return (
    <div className="product-chips">
      {chips.map((c, i) => (
        <button key={i} className="quick-prompt product-chip" onClick={() => onPick(c.query)}>
          <ChevronRight size={12} />
          {c.label}
        </button>
      ))}
    </div>
  );
}

export default App;
