import React, { useState, useEffect, useRef } from 'react';
import {
  X,
  Send,
  Bot,
  User,
  Shield,
  MessageSquare,
  Database,
  ChevronRight,
  Terminal,
  Play,
  Zap,
  Cpu,
  History,
  Command,
  Layers
} from 'lucide-react';
import './McpInspector.css';

interface Message {
  id: string;
  role: 'user' | 'assistant' | 'protocol' | 'agentless';
  content: string;
}

interface McpTool {
  name: string;
  description: string;
  inputSchema?: any;
}

interface McpInspectorProps {
  goHome: () => void;
}

const agentCommands = [
  {
    label: 'Audit Materiality',
    query: 'Audit the ledger for material transactions (those above $1.5M) and flag any outliers.',
    icon: 'Bot'
  },
  {
    label: 'Scan Anomalies',
    query: 'Scrutinize the ledger for transactions above $1,000,000 highlighting outliers and forensic anomalies.',
    icon: 'Bot'
  },
  {
    label: 'Jurisdiction Risk',
    query: 'Summarize transactions in high-risk jurisdictions (Cayman Islands, Panama) and assess audit risk.',
    icon: 'Bot'
  }
];

const protocolCommands = [
  {
    label: 'Fetch Cayman (Raw)',
    query: 'EXECUTE PROTOCOL: { "jurisdiction_name": "Cayman Islands" }',
    icon: 'Terminal'
  },
  {
    label: 'Get High Value (Raw)',
    query: 'EXECUTE PROTOCOL: { "min_amount": 1000000 }',
    icon: 'Terminal'
  },
  {
    label: 'Check Ledger (Raw)',
    query: 'EXECUTE PROTOCOL: { "limit": 10 }',
    icon: 'Terminal'
  }
];

const agentlessCommands = [
  {
    label: 'Cayman Dump (No-LLM)',
    query: 'AGENTLESS_DIRECT: Fetch Cayman',
    icon: 'Zap'
  },
  {
    label: 'Pending List (No-LLM)',
    query: 'AGENTLESS_DIRECT: Get Pending',
    icon: 'Zap'
  },
  {
    label: 'Vertex Direct (No-LLM)',
    query: 'AGENTLESS_DIRECT: Vertex solutions',
    icon: 'Zap'
  }
];

export const McpInspector: React.FC<McpInspectorProps> = ({ goHome }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isSending, setIsSending] = useState(false);
  const [lastInput, setLastInput] = useState('');
  const [tools, setTools] = useState<McpTool[]>([]);
  const [isLoadingTools, setIsLoadingTools] = useState(false);
  const [expandedTool, setExpandedTool] = useState<string | null>(null);
  const [protocolPayload, setProtocolPayload] = useState('{\n  "jurisdiction_name": "Cayman Islands"\n}');
  const [sessionId] = useState<string>(`session-${Date.now()}`);
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const fetchTools = async () => {
    setIsLoadingTools(true);
    try {
      const response = await fetch('/mcp/list_tools');
      if (response.ok) {
        const data = await response.json();
        if (data && data.tools) {
          setTools(data.tools);
        } else {
          throw new Error("No tools list");
        }
      } else {
        throw new Error("Failed to fetch");
      }
    } catch (error) {
      console.error('Failed to fetch tools:', error);
      setTools([
        { name: 'get_all_transactions', description: 'Fetches a batch of transactions from the ledger' },
        { name: 'query_transactions_by_jurisdiction', description: 'Queries transactions for a specific jurisdiction' },
        { name: 'query_high_value_transactions', description: 'Queries transactions exceeding a certain amount' }
      ]);
    } finally {
      setIsLoadingTools(false);
    }
  };

  useEffect(() => {
    fetchTools();
  }, []);

  const handleSendMessage = async (text?: string) => {
    const messageContent = text || input;
    if (!messageContent.trim()) return;

    if (!text) setInput('');
    setLastInput(messageContent);

    const userMsg: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: messageContent
    };

    setMessages(prev => [...prev, userMsg]);
    setIsSending(true);

    try {
      const response = await fetch('/api/mcp_chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          messages: [...messages, userMsg].map(m => ({ role: m.role, content: m.content })),
          id: sessionId
        })
      });

      if (!response.ok) throw new Error('Failed to get response');

      const data = await response.json();
      const isProtocol = messageContent.startsWith('EXECUTE PROTOCOL:');
      const isAgentless = messageContent.startsWith('AGENTLESS_DIRECT:');

      const assistantMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: isAgentless ? 'agentless' : (isProtocol ? 'protocol' : 'assistant'),
        content: data.reply || 'Request processed.'
      };

      setMessages(prev => [...prev, assistantMsg]);
    } catch (error: any) {
      const errorMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `Error: ${error.message}`
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setIsSending(false);
    }
  };

  const handleToolClick = (toolName: string) => {
    setExpandedTool(expandedTool === toolName ? null : toolName);
  };

  const getDefaultPayload = (name: string) => {
    switch (name) {
      case 'query_transactions_by_jurisdiction':
        return JSON.stringify({ jurisdiction_name: 'Cayman Islands' }, null, 2);
      case 'query_high_value_transactions':
        return JSON.stringify({ min_amount: 1000000 }, null, 2);
      case 'get_all_transactions':
        return JSON.stringify({ limit: 10 }, null, 2);
      default:
        return '{}';
    }
  };

  return (
    <div className="mcp-toolbox-kit">
      <header className="mcp-header">
        <div className="mcp-title-group">
          <Terminal size={20} className="text-[#00d1ff]" />
          <div>
            <h1>VERITY NEXUS MCP</h1>
            <p>Direct Swarm Interaction & Protocol Inspector</p>
          </div>
        </div>
        <button className="mcp-close-btn" onClick={goHome}><X size={20} /></button>
      </header>

      <main className="mcp-main">
        <section className="mcp-panel">
          <div className="mcp-messages">
            {messages.length === 0 && (
              <div className="mcp-welcome">
                <Shield size={40} className="mb-4 text-[#00d1ff] opacity-40" />
                <h2>Swarm Terminal Initialized</h2>
                <p>Execute forensic queries or raw protocol calls below.</p>
              </div>
            )}
            {messages.map((msg) => (
              <div key={msg.id} className={`mcp-message ${msg.role}`}>
                <div className="mcp-message-header">
                  {msg.role === 'user' ? (
                    <User size={12} />
                  ) : msg.role === 'protocol' ? (
                    <Database size={12} className="text-[#00ffaa]" />
                  ) : msg.role === 'agentless' ? (
                    <Zap size={12} className="text-[#ff9900]" />
                  ) : (
                    <Bot size={12} className="text-[#00d1ff]" />
                  )}
                  <span>
                    {msg.role === 'user' ? 'INVESTIGATOR' :
                      msg.role === 'protocol' ? 'MCP PROTOCOL' :
                        msg.role === 'agentless' ? 'DIRECT PIPE' : 'AGENT'}
                  </span>
                </div>
                <div className="mcp-message-content">{msg.content}</div>
              </div>
            ))}
            {isSending && (
              <div className={`mcp-message assistant animate-pulse ${lastInput.startsWith('EXECUTE PROTOCOL:') ? 'protocol-stream' : ''}`}>
                <div className="mcp-message-header">
                  {lastInput.startsWith('AGENTLESS_DIRECT:') ? (
                    <Zap size={12} className="text-[#ff9900]" />
                  ) : lastInput.startsWith('EXECUTE PROTOCOL:') ? (
                    <Database size={12} className="text-[#00ffaa]" />
                  ) : (
                    <Bot size={12} className="text-[#00d1ff]" />
                  )}
                  <span>
                    {lastInput.startsWith('AGENTLESS_DIRECT:') ? 'BINARY STREAM' :
                      lastInput.startsWith('EXECUTE PROTOCOL:') ? 'PROTOCOL' : 'AGENT'}
                  </span>
                </div>
                <div className="mcp-message-content">
                  {lastInput.startsWith('AGENTLESS_DIRECT:') ? 'Streaming raw binary data (No-LLM)...' :
                    lastInput.startsWith('EXECUTE PROTOCOL:') ? 'Establishing direct handshake...' : 'Synchronizing with forensic swarm...'}
                </div>
              </div>
            )}
            <div ref={chatEndRef} />
          </div>

          <div className="mcp-action-container">
            <div className="mcp-action-section">
              <div className="mcp-action-header">
                <div className="flex items-center gap-2">
                  <Cpu size={14} className="text-[#00d1ff]" />
                  <span className="text-[9px] font-bold tracking-widest text-[#00d1ff]">AGENT INTELLIGENCE</span>
                </div>
              </div>
              <div className="mcp-input-group">
                <input
                  type="text"
                  placeholder="Ask the swarm to audit the ledger..."
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                  disabled={isSending}
                />
                <button className="mcp-send-btn" onClick={() => handleSendMessage()} disabled={isSending || !input}><Send size={16} /></button>
              </div>
            </div>

            <div className="mcp-action-section protocol-mode">
              <div className="mcp-action-header">
                <div className="flex items-center gap-2">
                  <Terminal size={14} className="text-[#00ffaa]" />
                  <span className="text-[9px] font-bold tracking-widest text-[#00ffaa]">DIRECT PROTOCOL CALL (RAW JSON)</span>
                </div>
              </div>
              <div className="mcp-protocol-input-group">
                <textarea
                  className="mcp-protocol-textarea"
                  value={protocolPayload}
                  onChange={(e) => setProtocolPayload(e.target.value)}
                />
                <button
                  className="mcp-protocol-execute-btn"
                  onClick={() => handleSendMessage(`EXECUTE PROTOCOL: ${protocolPayload}`)}
                  disabled={isSending}
                >
                  <Zap size={14} />
                  <span>EXECUTE</span>
                </button>
              </div>
            </div>
          </div>
        </section>

        <section className="mcp-panel mcp-sidebar-panel">
          <div className="mcp-sidebar-content">
            <div className="mcp-sidebar-section">
              <div className="mcp-section-header">
                <Bot size={14} className="text-[#00d1ff]" />
                <h3>SWARM ANALYSIS</h3>
              </div>
              <div className="mcp-command-grid">
                {agentCommands.map((cmd, idx) => (
                  <button key={idx} className="mcp-command-btn agent-mode" onClick={() => handleSendMessage(cmd.query)}>
                    <div className="mcp-btn-top"><Bot size={12} /><span>{cmd.label}</span></div>
                    <p>{cmd.query.slice(0, 40)}...</p>
                  </button>
                ))}
              </div>
            </div>

            <div className="mcp-sidebar-section">
              <div className="mcp-section-header">
                <Terminal size={14} className="text-[#00ffaa]" />
                <h3>DIRECT PROTOCOL</h3>
              </div>
              <div className="mcp-command-grid">
                {protocolCommands.map((cmd, idx) => (
                  <button key={idx} className="mcp-command-btn protocol-mode" onClick={() => handleSendMessage(cmd.query)}>
                    <div className="mcp-btn-top"><Terminal size={12} /><span>{cmd.label}</span></div>
                    <p>{cmd.query.slice(17, 57)}...</p>
                  </button>
                ))}
              </div>
            </div>

            <div className="mcp-sidebar-section">
              <div className="mcp-section-header">
                <Zap size={14} className="text-[#ff9900]" />
                <h3>DIRECT BINARY PIPE (ZERO-LLM)</h3>
              </div>
              <div className="mcp-command-grid">
                {agentlessCommands.map((cmd, idx) => (
                  <button key={idx} className="mcp-command-btn agentless-mode" style={{ borderColor: 'rgba(255,153,0,0.2)' }} onClick={() => handleSendMessage(cmd.query)}>
                    <div className="mcp-btn-top"><Zap size={12} className="text-[#ff9900]" /><span>{cmd.label}</span></div>
                    <p>Bypasses LLM. Instant data stream.</p>
                  </button>
                ))}
              </div>
            </div>

            <div className="mcp-sidebar-section">
              <div className="mcp-section-header flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Database size={14} className="text-[#00d1ff]" />
                  <h3>DEPLOYED MCP TOOLS</h3>
                </div>
              </div>
              <div className="mcp-tools-list">
                {tools.map((tool, idx) => (
                  <div key={idx} className={`mcp-tool-card ${expandedTool === tool.name ? 'expanded' : ''}`}>
                    <div className="mcp-tool-info-row" onClick={() => handleToolClick(tool.name)}>
                      <div className="mcp-tool-info">
                        <div className="flex items-center gap-2 mb-1">
                          <Database size={12} className="text-[#00d1ff]" />
                          <h3>{tool.name.toUpperCase()}</h3>
                        </div>
                        <p>{tool.description}</p>
                      </div>
                      <ChevronRight size={14} className={`mcp-tool-chevron ${expandedTool === tool.name ? 'rotate-90' : ''}`} />
                    </div>
                    {expandedTool === tool.name && (
                      <div className="mcp-protocol-tester">
                        <textarea id={`side-payload-${tool.name}`} className="mcp-tester-input" defaultValue={getDefaultPayload(tool.name)} />
                        <button className="mcp-tester-btn" onClick={() => {
                          const el = document.getElementById(`side-payload-${tool.name}`) as HTMLTextAreaElement;
                          handleSendMessage(`EXECUTE PROTOCOL: ${el.value}`);
                        }}><Play size={10} />EXECUTE</button>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
};
