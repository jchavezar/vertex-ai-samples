import { useState, useEffect, useRef } from 'react'
import './App.css'
import { useMsal, useIsAuthenticated } from "@azure/msal-react";
import { loginRequest } from "./authConfig";
import { User } from "lucide-react";

interface Message {
  role: 'user' | 'model' | 'status';
  text: string;
  icon?: string;
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
  const [sessionId] = useState<string>(`session_${Date.now()}`);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = { role: 'user', text: input };
    setMessages((prev) => [...prev, userMessage]);
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
        body: JSON.stringify({ prompt: input, session_id: sessionId })
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
                  const last = prev[prev.length - 1];
                  if (last && last.role === 'model' && !last.icon) {
                    return [...prev.slice(0, -1), { role: 'model', text: accumulatedText }];
                  } else {
                    return [...prev, { role: 'model', text: accumulatedText }];
                  }
                });
              } else if (data.type === 'status') {
                setMessages((prev) => [...prev, { role: 'status', text: data.message, icon: data.icon }]);
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
      setIsLoading(false);
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
            <span>🔑</span> Bearer Token (paste your MS Entra ID token - without "Bearer " prefix)
          </div>
          <div className="token-container">
            <div className="token-area">
              {tokens?.idToken || 'Paste your token here to authenticate tools...'}
            </div>
            <div className="valid-badge">Valid (62m)</div>
          </div>
        </div>

        <div className="message-list">
          {messages.map((msg, idx) => (
            <div key={idx} className={`message-wrapper ${msg.role}`}>
              {msg.role === 'status' ? (
                <div className="status-bar">
                  <span>{msg.icon === 'zap' ? '⚡' : '🛠️'}</span>
                  {msg.text}
                </div>
              ) : (
                <>
                  <div className="message-label">{msg.role === 'user' ? 'You' : 'Assistant'}</div>
                  <div className={`message-bubble ${msg.role}`}>
                    <div className="text">{msg.text}</div>
                  </div>
                </>
              )}
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>

        <div className="input-area-wrapper">
          <div className="quick-actions">
            <button className="quick-btn">My Devices</button>
            <button className="quick-btn">Laptop Info</button>
            <button className="quick-btn">Phone Return</button>
            <button className="quick-btn">EOL Status</button>
            <button className="quick-btn">Available Tools</button>
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
            <button onClick={handleSend} disabled={isLoading || !input.trim()}>
              {isLoading ? 'Sending...' : 'Send'}
            </button>
          </div>
        </div>
      </div>
    </div>
  )

}

export default App
