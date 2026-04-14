import { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import './App.css'

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

function App() {
  const [prompt, setPrompt] = useState('')
  const [messages, setMessages] = useState<Message[]>([])
  const [loading, setLoading] = useState(false)

  const handleSend = async () => {
    if (!prompt.trim()) return

    const userMessage: Message = { role: 'user', content: prompt }
    setMessages(prev => [...prev, userMessage])
    setPrompt('')
    setLoading(true)

    const assistantMessage: Message = { role: 'assistant', content: '' }
    setMessages(prev => [...prev, assistantMessage])

    try {
      // Call local backend on port 8001
      const url = `http://localhost:8001/chat?message=${encodeURIComponent(prompt)}`
      const res = await fetch(url, {
        method: 'POST',
      })

      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`)
      }

      const reader = res.body?.getReader()
      const decoder = new TextDecoder()

      while (reader) {
        const { done, value } = await reader.read()
        if (done) break
        const chunk = decoder.decode(value, { stream: true })
        const lines = chunk.split('\n')
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const dataStr = line.slice(6)
            if (dataStr === '[DONE]') break
            
            setMessages(prev => {
              const last = prev[prev.length - 1]
              if (last && last.role === 'assistant') {
                return [...prev.slice(0, -1), { ...last, content: last.content + dataStr }]
              }
              return prev
            })
          }
        }
      }
    } catch (error) {
      console.error('Error:', error)
      setMessages(prev => {
        const last = prev[prev.length - 1]
        if (last && last.role === 'assistant') {
          return [...prev.slice(0, -1), { ...last, content: `Error: ${error.message}` }]
        }
        return prev
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="claude-replica dark-theme">
      <div className="sidebar">
        <div className="sidebar-top">
          <div className="logo">Secret Agent</div>
          <button className="new-chat-btn">+ New chat</button>
        </div>
        <div className="sidebar-nav">
          <button className="nav-item active">Secure Chat</button>
          <button className="nav-item">Audit Logs</button>
          <button className="nav-item">Settings</button>
        </div>
        <div className="sidebar-footer">
          <div className="status-indicator connected">Backend Connected</div>
        </div>
      </div>
      <div className="main-content">
        <div className="chat-area">
          {messages.length === 0 ? (
            <div className="welcome-screen">
              <h1>Secure Data Vault</h1>
              <p>Ask me to fetch sensitive data using Secret Manager tools.</p>
              <div className="input-box-container">
                <div className="input-box">
                  <button className="icon-btn attach-btn">+</button>
                  <textarea 
                    placeholder="What sensitive data do you need?" 
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
                  <button className="pill">Fetch Analytics</button>
                  <button className="pill">Check Status</button>
                  <button className="pill">Secure Query</button>
                </div>
              </div>
            </div>
          ) : (
            <div className="chat-history">
              <div className="messages-list">
                {messages.map((msg, idx) => (
                  <div key={idx} className={`message-item ${msg.role}`}>
                    <div className="message-avatar">
                      {msg.role === 'user' ? 'U' : 'S'}
                    </div>
                    <div className="message-content-wrapper">
                      <div className="message-sender">{msg.role === 'user' ? 'You' : 'Secret Agent'}</div>
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
                {loading && (
                  <div className="message-item assistant loading">
                    <div className="message-avatar">S</div>
                    <div className="message-content-wrapper">
                      <div className="message-sender">Secret Agent</div>
                      <div className="message-text">Thinking...</div>
                    </div>
                  </div>
                )}
              </div>
              <div className="sticky-input-area">
                <div className="input-box">
                  <button className="icon-btn attach-btn">+</button>
                  <textarea 
                    placeholder="Message Secret Agent..." 
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
