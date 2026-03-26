import { useState, useEffect, useRef } from 'react'
import './App.css'
import { useMsal, useIsAuthenticated } from "@azure/msal-react";
import { loginRequest } from "./authConfig";
import { User } from "lucide-react";
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface Message {
  role: 'user' | 'model' | 'status';
  text: string;
  icon?: string;
  duration?: number;
}


function App() {
  const { instance, accounts } = useMsal();
  const isAuthenticated = useIsAuthenticated();
  const [tokens, setTokens] = useState<{accessToken: string, idToken: string} | null>(null);

  useEffect(() => {
    if (isAuthenticated && accounts[0]) {
      const request = {
        ...loginRequest,
        account: accounts[0],
      };

      const pingToken = async () => {
        try {
          const response = await instance.acquireTokenSilent(request);
          setTokens({ accessToken: response.accessToken, idToken: response.idToken });
        } catch (error) {
          console.error("Token acquisition error:", error);
        }
      };

      pingToken();
      const interval = setInterval(pingToken, 5 * 60 * 1000);
      return () => clearInterval(interval);
    } else {
      setTokens(null);
    }
  }, [isAuthenticated, accounts, instance]);

  const handleLogin = () => {
    instance.loginRedirect(loginRequest).catch(console.error);
  };

  const handleLogout = () => {
    instance.logoutPopup({ postLogoutRedirectUri: "/" }).catch(console.error);
  };

  const [messages, setMessages] = useState<Message[]>([
    { role: 'model', text: 'Hello! I am your Light Portal Assistant. I can help you with ServiceNow or Answer general questions. What is on your mind?' }
  ]);
  const [input, setInput] = useState('');
  const [sessionId] = useState<string>(`session-${Date.now()}`);
  const [isLoading, setIsLoading] = useState(false);
  const [timer, setTimer] = useState(0);
  const startTimeRef = useRef<number>(0);
  const lastStatusIndexRef = useRef<number>(-1);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    let interval: any;
    if (isLoading) {
      if (startTimeRef.current === 0) {
        startTimeRef.current = performance.now();
      }
      interval = setInterval(() => {
        setTimer(Math.floor(performance.now() - startTimeRef.current));
      }, 50); // Use 50ms for smoother UI without overloading
    } else {
      startTimeRef.current = 0;
    }
    return () => clearInterval(interval);
  }, [isLoading]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSend = async (overrideInput?: string) => {
    const textToSend = overrideInput || input;
    if (!textToSend.trim() || isLoading) return;

    const userMessage: Message = { role: 'user', text: textToSend };
    setMessages((prev) => [...prev, userMessage]);
    
    // Clear input if we used the main box, keep it if we used a quick button or just clear it always.
    // Clearing it always is usually cleaner.
    setInput('');
    setIsLoading(true);

    try {
      const headers: Record<string, string> = { 'Content-Type': 'application/json' };
      if (tokens && tokens.idToken) {
        headers['Authorization'] = `Bearer ${tokens.idToken}`;
      }

      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: headers,
        body: JSON.stringify({ prompt: textToSend, session_id: sessionId })
      });

      if (!response.ok) throw new Error('Failed to send message');

      const reader = response.body?.getReader();
      if (!reader) throw new Error('No readable stream');

      const decoder = new TextDecoder();
      let accumulatedText = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const dataStr = line.slice(6);
            if (dataStr === '[DONE]') continue;

            try {
              const data = JSON.parse(dataStr);
              if (data.type === 'text') {
                accumulatedText += data.content;
                setMessages((prev) => {
                  const updatedMessages = [...prev];
                  const lastIdx = updatedMessages.length - 1;
                  
                  // If we just started getting text, lock the duration of the previous status message
                  if (lastStatusIndexRef.current !== -1) {
                    const statusMsg = updatedMessages[lastStatusIndexRef.current];
                    if (statusMsg && statusMsg.role === 'status' && statusMsg.duration === undefined) {
                      statusMsg.duration = Math.floor(performance.now() - startTimeRef.current);
                    }
                    lastStatusIndexRef.current = -1;
                  }

                  const last = updatedMessages[lastIdx];
                  if (last && last.role === 'model' && !last.icon) {
                    updatedMessages[updatedMessages.length - 1] = { role: 'model', text: accumulatedText };
                    return updatedMessages;
                  } else {
                    return [...updatedMessages, { role: 'model', text: accumulatedText }];
                  }
                });
              } else if (data.type === 'status') {
                setMessages((prev) => {
                  const updatedMessages = [...prev];
                  // Lock previous status if it exists
                  if (lastStatusIndexRef.current !== -1) {
                    const prevStatus = updatedMessages[lastStatusIndexRef.current];
                    if (prevStatus && prevStatus.role === 'status' && prevStatus.duration === undefined) {
                      prevStatus.duration = Math.floor(performance.now() - startTimeRef.current);
                    }
                  }
                  
                  const newStatus: Message = { role: 'status', text: data.message, icon: data.icon };
                  lastStatusIndexRef.current = updatedMessages.length;
                  return [...updatedMessages, newStatus];
                });
              }
            } catch (e) {
              console.error('Failed to parse chunk:', dataStr, e);
            }
          }
        }
      }
    } catch (error) {
      console.error('Error in chat:', error);
      setMessages((prev) => [...prev, { role: 'model', text: 'Error: Could not reach the backend.' }]);
    } finally {
      const finalDuration = Math.floor(performance.now() - startTimeRef.current);
      setIsLoading(false);
      setMessages((prev) => {
        const updatedMessages = [...prev];
        if (lastStatusIndexRef.current !== -1) {
          const lastStatus = updatedMessages[lastStatusIndexRef.current];
          if (lastStatus && lastStatus.role === 'status' && lastStatus.duration === undefined) {
            lastStatus.duration = finalDuration; 
          }
          lastStatusIndexRef.current = -1;
        }
        return updatedMessages;
      });
      startTimeRef.current = 0;
    }
  };


  return (
    <div className="app-container">
      <div className="main-content">
        <div className="chat-header">
          <span className="header-icon">💻</span>
          <h1>Athena Technology Assistant</h1>
          <p>MCP ADK Agent - Device Management & IT Services</p>
          <div className="status-row">
            <div><span className="status-dot"></span> MCP Server</div>
            <div><span className="status-dot"></span> Auth Token</div>
          </div>
          <div className="auth-controls" style={{ position: 'absolute', top: '20px', right: '20px' }}>
              {isAuthenticated ? (
                <button onClick={handleLogout} className="logout-btn" style={{ background: 'transparent', border: 'none', color: '#fff', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '5px' }}>
                  <User size={16} /> Logout
                </button>
              ) : (
                <button onClick={handleLogin} className="login-btn" style={{ background: 'transparent', border: 'none', color: '#fff', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '5px' }}>
                  <User size={16} /> Login
                </button>
              )}
          </div>
        </div>

        <div className="token-section">
          <div className="token-title">
            <span>🔑</span> Bearer Token (MS Entra ID token - Auto-fetched on Login)
          </div>
          <div className="token-container">
            <div className="token-area">
              {tokens?.idToken ? (
                <span style={{wordBreak: 'break-all'}}>{tokens.idToken}</span>
              ) : (
                <div style={{ padding: '0', background: 'transparent', border: 'none', color: 'inherit', fontFamily: 'monospace' }}>
                  Please click the "Login" button at the top right to authenticate...
                </div>
              )}
            </div>
            <div className="valid-badge">Valid (62m)</div>
          </div>
        </div>

        <div className="message-list">
          {messages.map((msg, idx) => (
            <div key={idx} className={`message-wrapper ${msg.role}`}>
              {msg.role === 'status' ? (
                <div className="status-bar">
                  <span>{msg.icon === 'zap' ? '⚡' : msg.icon === 'search' ? '🔍' : '🛠️'}</span>
                  {msg.text}
                  {msg.duration !== undefined ? ` (${(msg.duration / 1000).toFixed(2)}s)` : (idx === messages.length - 1 && isLoading ? ` (${(timer / 1000).toFixed(2)}s)` : '')}
                </div>
              ) : (
                <>
                  <div className="message-label">{msg.role === 'user' ? 'You' : 'Assistant'}</div>
                  <div className={`message-bubble ${msg.role}`}>
                    <div className="text markdown-body">
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>
                        {msg.text}
                      </ReactMarkdown>
                    </div>
                  </div>
                </>
              )}
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>

        <div className="input-area-wrapper">
          <div className="quick-actions">
            <button className="quick-btn" onClick={() => { setInput("List my incidents"); handleSend("List my incidents"); }}>My Incidents</button>
            <button className="quick-btn" onClick={() => { setInput("Search SharePoint for laptop policy"); handleSend("Search SharePoint for laptop policy"); }}>Search SharePoint</button>
            <button className="quick-btn" onClick={() => { setInput("List active tasks"); handleSend("List active tasks"); }}>Active Tasks</button>
            <button className="quick-btn" onClick={() => { setInput("List my open tickets"); handleSend("List my open tickets"); }}>Open Tickets</button>
          </div>

          <div className="input-area">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSend()}
              placeholder="Ask me anything..."
              disabled={isLoading}
            />
            <button onClick={() => handleSend()} disabled={isLoading || !input.trim()}>
              {isLoading ? 'Sending...' : 'Send'}
            </button>
          </div>
        </div>
      </div>
    </div>
  )

}

export default App
