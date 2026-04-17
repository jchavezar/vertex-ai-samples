import React, { useState, useRef, useEffect } from 'react';
import { Send, Loader2, Zap, Brain, Sparkles, FlaskConical } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import './App.css';

const AGENTS = {
  assistant: { label: 'Orchestrator', color: '#3b82f6', icon: Zap, model: 'Gemini 2.5 Flash' },
  market_analyst: { label: 'Market Analyst', color: '#a855f7', icon: Brain, model: 'Claude Sonnet' },
  creative_strategist: { label: 'Creative Strategist', color: '#22c55e', icon: Sparkles, model: 'Flash-Lite' },
  product_research: { label: 'Research Team', color: '#f59e0b', icon: FlaskConical, model: 'Sequential' },
};

const SUGGESTED = [
  "What is transfer learning in machine learning?",
  "Product research for an AI-powered code review tool",
  "Explain microservices vs monolithic architecture",
];

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [activeAgent, setActiveAgent] = useState(null);
  const chatRef = useRef(null);

  useEffect(() => {
    if (chatRef.current) {
      chatRef.current.scrollTop = chatRef.current.scrollHeight;
    }
  }, [messages]);

  const sendMessage = async (text) => {
    const msg = text || input.trim();
    if (!msg || isLoading) return;
    setInput('');
    setActiveAgent(null);

    const userMsg = { role: 'user', content: msg };
    setMessages(prev => [...prev, userMsg]);
    setIsLoading(true);

    const assistantMsg = { role: 'assistant', content: '', agents: [] };
    setMessages(prev => [...prev, assistantMsg]);

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: msg, session_id: sessionId, user_id: 'ui-user' }),
      });

      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let buffer = '';
      let fullText = '';
      let agentsSeen = [];

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const parts = buffer.split(/\r?\n\r?\n/);
        buffer = parts.pop() || '';

        for (const sseEvent of parts) {
          const lines = sseEvent.split(/\r?\n/);
          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const dataStr = line.substring(6).trim();
              try {
                const parsed = JSON.parse(dataStr);

                if (parsed.type === 'session') {
                  setSessionId(parsed.session_id);
                } else if (parsed.type === 'agent_switch') {
                  setActiveAgent(parsed.agent);
                  if (!agentsSeen.includes(parsed.agent)) {
                    agentsSeen = [...agentsSeen, parsed.agent];
                  }
                } else if (parsed.type === 'chunk') {
                  fullText += parsed.text;
                  if (parsed.agent && !agentsSeen.includes(parsed.agent)) {
                    agentsSeen = [...agentsSeen, parsed.agent];
                  }
                  setMessages(prev => {
                    const updated = [...prev];
                    updated[updated.length - 1] = { role: 'assistant', content: fullText, agents: [...agentsSeen] };
                    return updated;
                  });
                } else if (parsed.type === 'done') {
                  setActiveAgent(null);
                } else if (parsed.type === 'error') {
                  fullText += `\n\n**Error:** ${parsed.message}`;
                  setMessages(prev => {
                    const updated = [...prev];
                    updated[updated.length - 1] = { role: 'assistant', content: fullText, agents: [...agentsSeen] };
                    return updated;
                  });
                }
              } catch {}
            }
          }
        }
      }
    } catch (error) {
      setMessages(prev => {
        const updated = [...prev];
        updated[updated.length - 1] = { role: 'assistant', content: 'Connection error. Please try again.', agents: [] };
        return updated;
      });
    } finally {
      setIsLoading(false);
      setActiveAgent(null);
    }
  };

  const isEmpty = messages.length === 0;

  return (
    <div className="app">
      <header className="header">
        <div className="header-left">
          <div className="logo-icon">
            <div className="logo-pulse"></div>
            <span>O</span>
          </div>
          <div>
            <h1 className="header-title">Observability Orchestra</h1>
            <p className="header-subtitle">Multi-Agent Intelligence Engine</p>
          </div>
        </div>
        <div className="header-agents">
          {Object.entries(AGENTS).filter(([k]) => k !== 'product_research').map(([key, agent]) => (
            <div key={key} className={`agent-status ${activeAgent === key ? 'active' : ''}`}>
              <div className="agent-dot" style={{ background: agent.color }}></div>
              <span className="agent-status-label">{agent.label}</span>
              <span className="agent-model">{agent.model}</span>
            </div>
          ))}
        </div>
      </header>

      <div className="chat-area" ref={chatRef}>
        {isEmpty ? (
          <div className="empty-state">
            <div className="empty-orb">
              <div className="orb-ring r1"></div>
              <div className="orb-ring r2"></div>
              <div className="orb-ring r3"></div>
              <div className="orb-center">O</div>
            </div>
            <h2>Multi-Agent Intelligence</h2>
            <p>Ask anything or trigger a multi-agent product research pipeline.</p>
            <div className="suggested-prompts">
              {SUGGESTED.map((s, i) => (
                <button key={i} className="suggested-btn" onClick={() => sendMessage(s)}>{s}</button>
              ))}
            </div>
          </div>
        ) : (
          <div className="messages">
            {messages.map((msg, idx) => (
              <div key={idx} className={`message message-${msg.role}`}>
                {msg.role === 'assistant' && (
                  <div className="msg-meta">
                    {(msg.agents || []).map(a => {
                      const agentInfo = AGENTS[a];
                      if (!agentInfo) return null;
                      const Icon = agentInfo.icon;
                      return (
                        <span key={a} className="agent-badge" style={{ background: `${agentInfo.color}18`, color: agentInfo.color, borderColor: `${agentInfo.color}40` }}>
                          <Icon size={12} /> {agentInfo.label}
                        </span>
                      );
                    })}
                  </div>
                )}
                <div className={`msg-bubble ${msg.role}`}>
                  {msg.role === 'assistant' ? (
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>{msg.content || ''}</ReactMarkdown>
                  ) : (
                    <p>{msg.content}</p>
                  )}
                  {msg.role === 'assistant' && isLoading && idx === messages.length - 1 && !msg.content && (
                    <div className="typing-indicator">
                      <span></span><span></span><span></span>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {activeAgent && AGENTS[activeAgent] && (
        <div className="active-bar" style={{ borderColor: AGENTS[activeAgent].color }}>
          <Loader2 size={14} className="spin" style={{ color: AGENTS[activeAgent].color }} />
          <span style={{ color: AGENTS[activeAgent].color }}>{AGENTS[activeAgent].label}</span>
          <span className="active-model">is responding via {AGENTS[activeAgent].model}</span>
        </div>
      )}

      <div className="input-area">
        <div className="input-container">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
            placeholder="Ask anything, or say 'product research for ...' to trigger multi-agent pipeline"
            disabled={isLoading}
          />
          <button onClick={() => sendMessage()} disabled={isLoading || !input.trim()}>
            {isLoading ? <Loader2 size={18} className="spin" /> : <Send size={18} />}
          </button>
        </div>
        <p className="input-hint">Orchestrator routes to specialized agents when needed</p>
      </div>
    </div>
  );
}

export default App;
