import { useState, useEffect, useRef } from 'react'
import ReactMarkdown from 'react-markdown'
import './App.css'

interface Message {
  role: 'user' | 'assistant';
  content: string;
  tools?: ToolCall[];
}

interface ToolCall {
  name: string;
  arguments: any;
  status: 'running' | 'completed' | 'failed';
  response?: string;
}

interface AuthInfo {
  authenticated: boolean;
  account?: {
    username: string;
    name: string;
    tenant_id: string;
  };
}

interface DeviceFlowInfo {
  user_code: string;
  verification_uri: string;
  message: string;
}

function App() {
  const [authInfo, setAuthInfo] = useState<AuthInfo | null>(null)
  const [deviceFlow, setDeviceFlow] = useState<DeviceFlowInfo | null>(null)
  const [authPolling, setAuthPolling] = useState(false)
  const [authError, setAuthError] = useState<string | null>(null)
  
  const [prompt, setPrompt] = useState('')
  const [messages, setMessages] = useState<Message[]>([])
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement | null>(null)

  const BACKEND_URL = 'http://localhost:8002'

  // Fetch current auth status
  const checkAuthStatus = async () => {
    try {
      const res = await fetch(`${BACKEND_URL}/api/auth/status`)
      if (res.ok) {
        const data = await res.json()
        setAuthInfo(data)
      }
    } catch (e) {
      console.error("Failed to check auth status:", e)
    }
  }

  useEffect(() => {
    checkAuthStatus()
  }, [])

  // Auto-scroll to bottom of chat
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  // Start Device Code Flow login
  const handleLogin = async () => {
    setAuthError(null)
    setDeviceFlow(null)
    try {
      const res = await fetch(`${BACKEND_URL}/api/auth/url`)
      if (!res.ok) throw new Error("Failed to initialize login flow")
      const data = await res.json()
      setDeviceFlow(data)
      setAuthPolling(true)
      startPolling(data.user_code)
    } catch (e: any) {
      setAuthError(e.message)
    }
  }

  // Poll for authentication completion
  const startPolling = (userCode: string) => {
    const interval = setInterval(async () => {
      try {
        const res = await fetch(`${BACKEND_URL}/api/auth/complete/${userCode}`)
        if (res.ok) {
          const data = await res.json()
          if (data.status === 'authenticated') {
            clearInterval(interval)
            setAuthPolling(false)
            setDeviceFlow(null)
            setAuthInfo({ authenticated: true, account: data.account })
          }
        } else {
          // If 400 or other bad response, stop polling
          clearInterval(interval)
          setAuthPolling(false)
          setAuthError("Authentication flow timed out or failed.")
        }
      } catch (e) {
        // network error, continue polling
      }
    }, 4000)

    // Cleanup after 15 minutes (to avoid infinite polling)
    setTimeout(() => {
      clearInterval(interval)
      setAuthPolling(false)
    }, 15 * 60 * 1000)
  }

  // Logout action
  const handleLogout = async () => {
    try {
      await fetch(`${BACKEND_URL}/api/auth/logout`, { method: 'POST' })
      setAuthInfo({ authenticated: false })
      setMessages([])
    } catch (e) {
      console.error("Logout failed:", e)
    }
  }

  // Send message and stream response
  const handleSend = async () => {
    if (!prompt.trim() || loading) return

    const userMessage: Message = { role: 'user', content: prompt }
    setMessages(prev => [...prev, userMessage])
    setPrompt('')
    setLoading(true)

    // Append initial assistant placeholder message
    const assistantMessage: Message = { role: 'assistant', content: '', tools: [] }
    setMessages(prev => [...prev, assistantMessage])

    try {
      const res = await fetch(`${BACKEND_URL}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: json_stringify_custom({ message: prompt })
      })

      if (!res.ok) {
        const errData = await res.json()
        throw new Error(errData.detail || "Server error running agent")
      }

      const reader = res.body?.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      while (reader) {
        const { done, value } = await reader.read()
        if (done) break
        
        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        
        // Save the last partial line back to buffer
        buffer = lines.pop() || ''
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const dataStr = line.slice(6).trim()
            if (!dataStr) continue
            
            try {
              const parsed = JSON.parse(dataStr)
              
              if (parsed.type === 'text') {
                setMessages(prev => {
                  const updated = [...prev]
                  const last = updated[updated.length - 1]
                  if (last && last.role === 'assistant') {
                    last.content += parsed.content
                  }
                  return updated
                })
              } else if (parsed.type === 'tool_start') {
                setMessages(prev => {
                  const updated = [...prev]
                  const last = updated[updated.length - 1]
                  if (last && last.role === 'assistant') {
                    const newTool: ToolCall = {
                      name: parsed.name,
                      arguments: parsed.arguments,
                      status: 'running'
                    }
                    last.tools = [...(last.tools || []), newTool]
                  }
                  return updated
                })
              } else if (parsed.type === 'tool_end') {
                setMessages(prev => {
                  const updated = [...prev]
                  const last = updated[updated.length - 1]
                  if (last && last.role === 'assistant' && last.tools) {
                    const toolIdx = last.tools.findIndex(t => t.name === parsed.name && t.status === 'running')
                    if (toolIdx !== -1) {
                      last.tools[toolIdx].status = 'completed'
                      last.tools[toolIdx].response = parsed.response
                    }
                  }
                  return updated
                })
              } else if (parsed.type === 'error') {
                setMessages(prev => {
                  const updated = [...prev]
                  const last = updated[updated.length - 1]
                  if (last && last.role === 'assistant') {
                    last.content += `\n\n**Error:** ${parsed.message}`
                  }
                  return updated
                })
              }
            } catch (jsonErr) {
              console.error("Failed to parse event data:", dataStr, jsonErr)
            }
          }
        }
      }
    } catch (error: any) {
      console.error('Error during chat:', error)
      setMessages(prev => {
        const updated = [...prev]
        const last = updated[updated.length - 1]
        if (last && last.role === 'assistant') {
          last.content = `Error: ${error.message}`
        }
        return updated
      })
    } finally {
      setLoading(false)
    }
  }

  // Simple stringify helper
  function json_stringify_custom(obj: any): string {
    return JSON.stringify(obj)
  }

  // Login view
  if (!authInfo || !authInfo.authenticated) {
    return (
      <div className="login-container dark-theme">
        <div className="login-card">
          <h2>SharePoint Hosted Explorer</h2>
          <p className="subtitle">Sign in to your Microsoft 365 Tenant to access Work IQ SharePoint tools via Google ADK</p>
          
          {authError && <div className="error-box">{authError}</div>}

          {!deviceFlow ? (
            <button className="login-btn" onClick={handleLogin}>
              <svg viewBox="0 0 23 23" width="20" height="20" className="ms-logo">
                <path fill="#f35325" d="M0 0h11v11H0z"/>
                <path fill="#81bc06" d="M12 0h11v11H12z"/>
                <path fill="#05a6f0" d="M0 12h11v11H0z"/>
                <path fill="#ffba08" d="M12 12h11v11H12z"/>
              </svg>
              Sign in with Microsoft
            </button>
          ) : (
            <div className="device-code-box">
              <p>Please open Microsoft's authentication portal in your browser:</p>
              <a href={deviceFlow.verification_uri} target="_blank" rel="noreferrer" className="auth-link">
                {deviceFlow.verification_uri}
              </a>
              <p className="code-label">And enter this verification code:</p>
              <div className="code-display">{deviceFlow.user_code}</div>
              
              {authPolling && (
                <div className="polling-status">
                  <div className="spinner"></div>
                  <span>Waiting for authentication...</span>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    )
  }

  // Main chat view
  return (
    <div className="claude-replica dark-theme">
      <div className="sidebar">
        <div className="sidebar-top">
          <div className="logo">SharePoint IQ</div>
          <div className="badge">Hosted MCP</div>
        </div>
        <div className="sidebar-connection">
          <div className="status-label">Active Connection</div>
          <div className="tenant-name">{authInfo.account?.username}</div>
          <div className="tenant-id">Tenant: {authInfo.account?.tenant_id.slice(0, 8)}...</div>
        </div>
        <div className="sidebar-nav">
          <button className="nav-item active">Explorer Agent</button>
        </div>
        <div className="sidebar-footer">
          <button className="logout-btn" onClick={handleLogout}>Disconnect</button>
        </div>
      </div>
      <div className="main-content">
        <div className="chat-area">
          {messages.length === 0 ? (
            <div className="welcome-screen">
              <h1>SharePoint Hosted Explorer</h1>
              <p>Ask queries about files, libraries, or sites in your tenant. Deployed on Google ADK backed by Microsoft's Work IQ MCP server.</p>
              <div className="input-box-container">
                <div className="input-box">
                  <textarea 
                    placeholder="Search SharePoint docs..." 
                    value={prompt}
                    onChange={e => setPrompt(e.target.value)}
                    onKeyDown={e => {
                      if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault()
                        handleSend()
                      }
                    }}
                  />
                  <button className="icon-btn send-btn" onClick={handleSend} disabled={loading || !prompt.trim()}>
                    <svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor">
                      <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"></path>
                    </svg>
                  </button>
                </div>
                <div className="suggestion-pills">
                  <button className="pill" onClick={() => setPrompt("Who is Jennifer Walsh?")}>Who is Jennifer Walsh?</button>
                  <button className="pill" onClick={() => setPrompt("Find contract agreements signed in 2025")}>Find contract agreements signed in 2025</button>
                </div>
              </div>
            </div>
          ) : (
            <div className="chat-history">
              <div className="messages-list">
                {messages.map((msg, idx) => (
                  <div key={idx} className={`message-item ${msg.role}`}>
                    <div className="message-avatar">
                      {msg.role === 'user' ? 'U' : 'AI'}
                    </div>
                    <div className="message-content-wrapper">
                      <div className="message-sender">{msg.role === 'user' ? 'You' : 'Hosted Agent'}</div>
                      
                      {/* Render active tool executions if any */}
                      {msg.role === 'assistant' && msg.tools && msg.tools.length > 0 && (
                        <div className="tool-calls-container">
                          {msg.tools.map((tool, tIdx) => (
                            <div key={tIdx} className={`tool-call-item ${tool.status}`}>
                              <span className="tool-status-icon">
                                {tool.status === 'running' ? '⏳' : tool.status === 'completed' ? '✅' : '❌'}
                              </span>
                              <span className="tool-name">
                                {tool.name} ({tool.arguments ? JSON.stringify(tool.arguments).slice(0, 60) : ''}...)
                              </span>
                            </div>
                          ))}
                        </div>
                      )}

                      <div className="message-text">
                        {msg.role === 'assistant' ? (
                          <ReactMarkdown>{msg.content}</ReactMarkdown>
                        ) : (
                          msg.content
                        )}
                      </div>
                    </div>
                  </div>
                ))}
                
                {loading && messages[messages.length - 1]?.content === '' && (
                  <div className="message-item assistant loading">
                    <div className="message-avatar">AI</div>
                    <div className="message-content-wrapper">
                      <div className="message-sender">Hosted Agent</div>
                      <div className="message-text">Analyzing SharePoint records...</div>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>

              <div className="sticky-input-area">
                <div className="input-box">
                  <textarea 
                    placeholder="Message Hosted Agent..." 
                    value={prompt}
                    onChange={e => setPrompt(e.target.value)}
                    onKeyDown={e => {
                      if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault()
                        handleSend()
                      }
                    }}
                  />
                  <button className="icon-btn send-btn" onClick={handleSend} disabled={loading || !prompt.trim()}>
                    <svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor">
                      <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"></path>
                    </svg>
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default App
