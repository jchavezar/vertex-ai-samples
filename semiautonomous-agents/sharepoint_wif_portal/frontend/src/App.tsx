import { useState, useEffect, useRef } from 'react';
import { flushSync } from 'react-dom';
import { useMsal, useIsAuthenticated } from '@azure/msal-react';
import { loginRequest } from './authConfig';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import {
  MessageSquare, Plus, FileText, ChevronRight,
  Shield, Sparkles, Send, ExternalLink, Cloud, LogIn, LogOut, Clock, Globe, Database, User, Bot, Trash2, Zap
} from 'lucide-react';
import './index.css';

interface Source {
  title: string;
  url: string;
  snippet: string;
}

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources: Source[];
  latencyMs?: number;
  timestamp: Date;
  isQuick?: boolean;  // /btw quick response
  isLoading?: boolean;
}

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
  const startTimeRef = useRef<number>(0);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const activeConversation = conversations.find(c => c.id === activeConversationId);

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
    }
  }, [isAuthenticated, accounts, instance]);

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

  if (!mounted) return null;

  return (
    <div className="workspace-container">
      <aside className="sidebar glass-panel">
        <div className="brand">
          <Cloud className="brand-icon" />
          <div className="brand-info">
            <span className="brand-name">Enterprise Search</span>
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
        <header className="canvas-header glass-panel">
          <div className="header-status">
            <div className="status-dot" style={{ background: isAuthenticated ? '#00C389' : '#A100FF' }}></div>
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

        <div className="chat-container">
          {activeConversation?.messages.length === 0 ? (
            <div className="welcome-screen">
              <h1 className="hero-title">Enterprise Search Chat</h1>
              <p>Ask questions about your SharePoint documents. Use <code>/btw</code> for quick questions while waiting!</p>
              <div className="quick-prompts">
                {['Who is the CFO and what is their salary?', 'Summarize the financial audit report', 'List all employees in engineering'].map((prompt, i) => (
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
                          </div>
                        )}
                        <div className="message-text">
                          {msg.role === 'user' ? (
                            <p>{msg.content}</p>
                          ) : (
                            <ReactMarkdown remarkPlugins={[remarkGfm]}>{msg.content}</ReactMarkdown>
                          )}
                        </div>
                        {msg.sources.length > 0 && (
                          <div className="message-sources">
                            {msg.sources.map((src, i) => (
                              <a key={i} href={src.url} target="_blank" rel="noreferrer" className="source-chip">
                                <FileText size={12} />
                                <span>{src.title}</span>
                                <ExternalLink size={10} />
                              </a>
                            ))}
                          </div>
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
                  placeholder={isLoading ? "Type /btw for quick questions while waiting..." : "Ask about your SharePoint documents..."}
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

export default App;
