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
  const [projectId, setProjectId] = useState('vtxdemos')
  const [region, setRegion] = useState('global')
  // Token state is kept for UI but not used for request
  const [token, setToken] = useState('') 

  const handleSend = async () => {
    if (!prompt.trim()) return

    const userMessage: Message = { role: 'user', content: prompt }
    setMessages(prev => [...prev, userMessage])
    setPrompt('')
    setLoading(true)

    const assistantMessage: Message = { role: 'assistant', content: '' }
    setMessages(prev => [...prev, assistantMessage])

    try {
      // Call local backend instead of direct Vertex API
      const url = `http://localhost:8000/api/chat`
      const res = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          messages: [{ role: 'user', content: prompt }]
        })
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
            try {
              const data = JSON.parse(dataStr)
              if (data.error) {
                throw new Error(data.error)
              }
              const content = data.choices[0]?.delta?.content || ''
              setMessages(prev => {
                const last = prev[prev.length - 1]
                if (last && last.role === 'assistant') {
                  return [...prev.slice(0, -1), { ...last, content: last.content + content }]
                }
                return prev
              })
            } catch (e) {
              console.error('Failed to parse JSON', e)
            }
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
    <div className="claude-replica">
      <div className="sidebar">
        <div className="sidebar-top">
          <div className="logo">Gemma 4</div>
          <button className="new-chat-btn">+ New chat</button>
        </div>
        <div className="sidebar-nav">
          <button className="nav-item">Chats</button>
          <button className="nav-item">Settings</button>
        </div>
        <div className="sidebar-settings">
          <div className="input-group">
            <label>Project ID</label>
            <input value={projectId} onChange={e => setProjectId(e.target.value)} />
          </div>
          <div className="input-group">
            <label>Region</label>
            <input value={region} onChange={e => setRegion(e.target.value)} />
          </div>
          <div className="input-group">
            <label>Access Token</label>
            <input type="password" value={token} onChange={e => setToken(e.target.value)} placeholder="Using ADC via Backend" disabled={true} />
          </div>
        </div>
      </div>
      <div className="main-content">
        <div className="chat-area">
          {messages.length === 0 ? (
            <div className="welcome-screen">
              <h1>Good morning</h1>
              <div className="input-box-container">
                <div className="input-box">
                  <button className="icon-btn attach-btn">+</button>
                  <textarea 
                    placeholder="How can I help you today?" 
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
                  <button className="pill">Write</button>
                  <button className="pill">Learn</button>
                  <button className="pill">Code</button>
                  <button className="pill">Life stuff</button>
                </div>
              </div>
            </div>
          ) : (
            <div className="chat-history">
              <div className="messages-list">
                {messages.map((msg, idx) => (
                  <div key={idx} className={`message-item ${msg.role}`}>
                    <div className="message-avatar">
                      {msg.role === 'user' ? 'U' : 'G'}
                    </div>
                    <div className="message-content-wrapper">
                      <div className="message-sender">{msg.role === 'user' ? 'You' : 'Gemma'}</div>
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
                    <div className="message-avatar">G</div>
                    <div className="message-content-wrapper">
                      <div className="message-sender">Gemma</div>
                      <div className="message-text">Thinking...</div>
                    </div>
                  </div>
                )}
              </div>
              <div className="sticky-input-area">
                <div className="input-box">
                  <button className="icon-btn attach-btn">+</button>
                  <textarea 
                    placeholder="Message Gemma 4..." 
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
