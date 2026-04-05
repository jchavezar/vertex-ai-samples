/**
 * AgentPanel - Standalone floating panel for Agent Engine interaction
 * This is a separate add-on that doesn't modify App.tsx
 */
import { useState, useRef, useEffect } from 'react';
import { Bot, X, Send, Sparkles, MinusCircle, Cpu, Database, Search, FileText, Zap, BrainCircuit } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface AgentMessage {
  id: string;
  role: 'user' | 'agent';
  content: string;
  timestamp: Date;
  isLoading?: boolean;
  toolsUsed?: string[];
}

interface AgentPanelProps {
  accessToken?: string;
}

const AGENT_TOOLS = [
  { name: 'SharePoint Search', icon: Database },
  { name: 'Document Analysis', icon: FileText },
  { name: 'Web Search', icon: Search },
  { name: 'Reasoning', icon: BrainCircuit },
];

const THINKING_PHRASES = [
  'Analyzing query...',
  'Searching documents...',
  'Reasoning through data...',
  'Connecting insights...',
  'Synthesizing response...',
];

export default function AgentPanel({ accessToken }: AgentPanelProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [messages, setMessages] = useState<AgentMessage[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [thinkingPhrase, setThinkingPhrase] = useState(THINKING_PHRASES[0]);
  const [activeTools, setActiveTools] = useState<number[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  useEffect(() => {
    if (isOpen && !isMinimized) {
      inputRef.current?.focus();
    }
  }, [isOpen, isMinimized]);

  // Animate thinking phrases while loading
  useEffect(() => {
    if (!isLoading) return;
    let idx = 0;
    const interval = setInterval(() => {
      idx = (idx + 1) % THINKING_PHRASES.length;
      setThinkingPhrase(THINKING_PHRASES[idx]);
    }, 2000);
    return () => clearInterval(interval);
  }, [isLoading]);

  // Animate tool activation while loading
  useEffect(() => {
    if (!isLoading) {
      setActiveTools([]);
      return;
    }
    let toolIdx = 0;
    const interval = setInterval(() => {
      setActiveTools(prev => {
        if (prev.length >= AGENT_TOOLS.length) return [toolIdx % AGENT_TOOLS.length];
        return [...prev, toolIdx % AGENT_TOOLS.length];
      });
      toolIdx++;
    }, 800);
    return () => clearInterval(interval);
  }, [isLoading]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMsg: AgentMessage = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: input,
      timestamp: new Date()
    };

    const loadingMsg: AgentMessage = {
      id: `agent-${Date.now()}`,
      role: 'agent',
      content: '',
      timestamp: new Date(),
      isLoading: true
    };

    setMessages(prev => [...prev, userMsg, loadingMsg]);
    setInput('');
    setIsLoading(true);

    try {
      const resp = await fetch('/api/agent', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(accessToken ? { 'X-Entra-Id-Token': accessToken } : {})
        },
        body: JSON.stringify({ query: input })
      });

      const data = await resp.json();

      setMessages(prev => prev.map(m =>
        m.isLoading
          ? { ...m, content: data.answer || data.error || 'No response', isLoading: false }
          : m
      ));
    } catch (err) {
      setMessages(prev => prev.map(m =>
        m.isLoading
          ? { ...m, content: `Error: ${err}`, isLoading: false }
          : m
      ));
    } finally {
      setIsLoading(false);
    }
  };

  if (!isOpen) {
    return (
      <button
        className="agent-fab"
        onClick={() => setIsOpen(true)}
        title="Open AI Agent"
      >
        <div className="agent-fab-inner">
          <BrainCircuit size={28} />
          <div className="agent-fab-pulse"></div>
        </div>
        <span className="agent-fab-label">AGENT</span>
      </button>
    );
  }

  if (isMinimized) {
    return (
      <div className="agent-minimized" onClick={() => setIsMinimized(false)}>
        <BrainCircuit size={18} />
        <span>Agent</span>
        <span className="agent-msg-count">{messages.filter(m => m.role === 'agent').length}</span>
      </div>
    );
  }

  return (
    <div className="agent-panel">
      <div className="agent-header">
        <div className="agent-title">
          <div className="agent-icon-wrapper">
            <BrainCircuit size={20} />
          </div>
          <div className="agent-title-text">
            <span className="agent-name">InsightComparator</span>
            <span className="agent-badge">AI AGENT</span>
          </div>
        </div>
        <div className="agent-controls">
          <button onClick={() => setIsMinimized(true)} title="Minimize">
            <MinusCircle size={16} />
          </button>
          <button onClick={() => setIsOpen(false)} title="Close">
            <X size={16} />
          </button>
        </div>
      </div>

      {/* Agent Tools Bar */}
      <div className="agent-tools-bar">
        {AGENT_TOOLS.map((tool, idx) => (
          <div
            key={tool.name}
            className={`agent-tool ${activeTools.includes(idx) ? 'active' : ''}`}
            title={tool.name}
          >
            <tool.icon size={14} />
          </div>
        ))}
        <span className="agent-tools-label">Tools</span>
      </div>

      <div className="agent-messages">
        {messages.length === 0 ? (
          <div className="agent-welcome">
            <div className="agent-welcome-icon">
              <BrainCircuit size={48} />
              <Zap size={20} className="agent-welcome-zap" />
            </div>
            <h3>I'm an AI Agent</h3>
            <p>Unlike a chatbot, I can <strong>reason</strong>, <strong>use tools</strong>, and <strong>take actions</strong> to help you analyze your SharePoint documents.</p>
            <div className="agent-capabilities">
              <div className="agent-cap"><Search size={14} /> Search</div>
              <div className="agent-cap"><FileText size={14} /> Analyze</div>
              <div className="agent-cap"><BrainCircuit size={14} /> Reason</div>
              <div className="agent-cap"><Cpu size={14} /> Compare</div>
            </div>
            <p className="agent-hint">Try: "Compare Q1 and Q2 revenue trends"</p>
          </div>
        ) : (
          messages.map(msg => (
            <div key={msg.id} className={`agent-msg ${msg.role}`}>
              {msg.isLoading ? (
                <div className="agent-thinking">
                  <div className="agent-thinking-header">
                    <BrainCircuit size={16} className="agent-thinking-icon" />
                    <span className="agent-thinking-label">Agent is working</span>
                  </div>
                  <div className="agent-thinking-status">
                    <span className="agent-thinking-phrase">{thinkingPhrase}</span>
                  </div>
                  <div className="agent-thinking-tools">
                    {AGENT_TOOLS.map((tool, idx) => (
                      <div
                        key={tool.name}
                        className={`agent-thinking-tool ${activeTools.includes(idx) ? 'active' : ''}`}
                      >
                        <tool.icon size={12} />
                        <span>{tool.name}</span>
                      </div>
                    ))}
                  </div>
                </div>
              ) : msg.role === 'agent' ? (
                <>
                  <div className="agent-msg-header">
                    <BrainCircuit size={12} />
                    <span>Agent Response</span>
                  </div>
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>{msg.content}</ReactMarkdown>
                </>
              ) : (
                <p>{msg.content}</p>
              )}
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      <form className="agent-input" onSubmit={(e) => { e.preventDefault(); handleSend(); }}>
        <input
          ref={inputRef}
          type="text"
          placeholder="Ask the agent..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={isLoading}
        />
        <button type="submit" disabled={!input.trim() || isLoading}>
          <Send size={16} />
        </button>
      </form>
    </div>
  );
}
