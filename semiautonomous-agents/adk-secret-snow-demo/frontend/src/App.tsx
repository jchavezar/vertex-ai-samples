import { useState, useRef, useEffect } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import './App.css'

interface Message {
  role: 'user' | 'assistant'
  content: string
}

function App() {
  const [prompt, setPrompt] = useState('')
  const [messages, setMessages] = useState<Message[]>([])
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  const autoResize = (el: HTMLTextAreaElement) => {
    el.style.height = 'auto'
    el.style.height = Math.min(el.scrollHeight, 200) + 'px'
  }

  const handleSend = async () => {
    if (!prompt.trim()) return
    setMessages(prev => [...prev, { role: 'user', content: prompt }])
    const msg = prompt
    setPrompt('')
    document.querySelectorAll('textarea').forEach(el => { el.style.height = 'auto' })
    setLoading(true)
    let hasStarted = false

    try {
      const res = await fetch(`http://localhost:8001/chat?message=${encodeURIComponent(msg)}`, { method: 'POST' })
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const reader = res.body?.getReader()
      const decoder = new TextDecoder()

      while (reader) {
        const { done, value } = await reader.read()
        if (done) break
        for (const line of decoder.decode(value, { stream: true }).split('\n')) {
          if (!line.startsWith('data: ')) continue
          const raw = line.slice(6)
          if (raw === '[DONE]') break
          let text: string
          try { text = JSON.parse(raw) } catch { text = raw }

          if (!hasStarted) {
            hasStarted = true
            setLoading(false)
            setMessages(prev => [...prev, { role: 'assistant', content: text }])
          } else {
            setMessages(prev => {
              const last = prev[prev.length - 1]
              return last?.role === 'assistant'
                ? [...prev.slice(0, -1), { ...last, content: last.content + text }]
                : prev
            })
          }
        }
      }
    } catch (err) {
      setMessages(prev => [...prev, { role: 'assistant', content: `Error: ${(err as Error).message}` }])
    } finally {
      setLoading(false)
    }
  }

  const pills = [
    { label: 'List Incidents', prompt: 'List all the incidents' },
    { label: 'Create Incident', prompt: 'Create a P2 incident for email server downtime' },
    { label: 'Search Tickets', prompt: 'Search incidents about network outage' },
  ]

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="sidebar-brand">
          <span className="brand-icon">S</span>
          <span className="brand-name">SecretOps</span>
        </div>
        <nav className="sidebar-nav">
          <button className="nav-item active">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
            Operations
          </button>
          <button className="nav-item">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"/><path d="M12 8v4l3 3"/></svg>
            Incidents
          </button>
        </nav>
        <div className="sidebar-footer">
          <div className="status-dot" />
          <span>Connected</span>
        </div>
        <a href="https://www.linkedin.com/in/jchavezar" target="_blank" rel="noopener noreferrer" className="signature">
          <svg viewBox="0 0 180 50" width="140" height="40" xmlns="http://www.w3.org/2000/svg">
            <defs>
              <linearGradient id="sig-grad" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="#9ca3af" />
                <stop offset="50%" stopColor="#6b7280" />
                <stop offset="100%" stopColor="#9ca3af" />
              </linearGradient>
            </defs>
            <text x="90" y="18" textAnchor="middle" fill="url(#sig-grad)" fontSize="10" fontFamily="Georgia, serif" fontStyle="italic" letterSpacing="0.5">Made with</text>
            <text x="90" y="18" textAnchor="middle" dx="38" fill="url(#sig-grad)" fontSize="10">&#x1F64F;</text>
            <text x="90" y="36" textAnchor="middle" fill="#4b5563" fontSize="16" fontFamily="Georgia, serif" fontWeight="600" fontStyle="italic" letterSpacing="1">by Jesus</text>
            <line x1="30" y1="43" x2="150" y2="43" stroke="url(#sig-grad)" strokeWidth="0.5" opacity="0.5" />
          </svg>
        </a>
      </aside>

      <main className="main">
        {messages.length === 0 && !loading ? (
          <div className="hero">
            <div className="hero-glow" />
            <h1>SecretOps</h1>
            <p className="hero-sub">Secure IT operations powered by<br/>Secret Manager + ServiceNow MCP</p>
            <div className="hero-input-wrap">
              <div className="input-bar">
                <textarea
                  rows={1}
                  placeholder="Ask about incidents, create tickets, search issues..."
                  value={prompt}
                  onChange={e => { setPrompt(e.target.value); autoResize(e.target) }}
                  onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend() } }}
                />
                <button className="send-btn" onClick={handleSend} disabled={loading || !prompt.trim()}>
                  <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/></svg>
                </button>
              </div>
              <div className="pills">
                {pills.map(p => (
                  <button key={p.label} className="pill" onClick={() => setPrompt(p.prompt)}>{p.label}</button>
                ))}
              </div>
            </div>
          </div>
        ) : (
          <div className="chat-wrap">
            <div className="messages">
              {messages.map((msg, i) => (
                <div key={i} className={`msg ${msg.role}`}>
                  {msg.role === 'assistant' && (
                    <div className="msg-avatar">
                      <span>S</span>
                    </div>
                  )}
                  <div className={`msg-bubble ${msg.role}`}>
                    {msg.role === 'assistant' ? (
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>{msg.content}</ReactMarkdown>
                    ) : msg.content}
                  </div>
                </div>
              ))}
              {loading && (
                <div className="msg assistant">
                  <div className="msg-avatar loading-avatar">
                    <span className="claude-spinner" />
                  </div>
                  <div className="msg-bubble assistant loading-bubble">
                    <span className="sweep-text">Thinking...</span>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
            <div className="chat-input-wrap">
              <div className="input-bar">
                <textarea
                  rows={1}
                  placeholder="Message SecretOps..."
                  value={prompt}
                  onChange={e => { setPrompt(e.target.value); autoResize(e.target) }}
                  onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend() } }}
                />
                <button className="send-btn" onClick={handleSend} disabled={loading || !prompt.trim()}>
                  <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/></svg>
                </button>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}

export default App
