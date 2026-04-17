import { useState, useRef, useEffect, useCallback } from 'react';

interface Source {
  title: string;
  uri: string;
  category: string;
}

interface PrecisionInfo {
  score: number;
  level: string;
  label: string;
  description: string;
}

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  text: string;
  sources?: Source[];
  precision?: PrecisionInfo;
  isStreaming?: boolean;
}

const WELCOME: ChatMessage = {
  id: 'welcome',
  role: 'assistant',
  text: "Welcome! I'm **A2A Sensei** — your specialist guide on Google's Agent-to-Agent protocol and multi-cloud agent interoperability.\n\nAsk me anything about A2A specs, agent cards, task lifecycle, streaming, MCP vs A2A, or cross-cloud agent patterns. My answers are grounded via Google Search with a precision score.",
};

function precisionColor(score: number): string {
  if (score >= 80) return '#22c55e';
  if (score >= 60) return '#3b82f6';
  if (score >= 40) return '#f59e0b';
  return '#ef4444';
}

export default function ChatWidget() {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([WELCOME]);
  const [input, setInput] = useState('');
  const [thinking, setThinking] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const scroll = useCallback(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(scroll, [messages, thinking, scroll]);
  useEffect(() => { if (open) inputRef.current?.focus(); }, [open]);

  const send = async () => {
    const text = input.trim();
    if (!text || thinking) return;

    const userMsg: ChatMessage = { id: uid(), role: 'user', text };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setThinking(true);

    const aId = uid();
    const history = messages
      .filter(m => m.id !== 'welcome')
      .map(m => ({ role: m.role, text: m.text }));

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text, history }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);

      const reader = res.body!.getReader();
      const dec = new TextDecoder();
      let buf = '';
      let full = '';
      let added = false;

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buf += dec.decode(value, { stream: true });
        const lines = buf.split('\n');
        buf = lines.pop() || '';

        for (const line of lines) {
          if (!line.startsWith('data: ')) continue;
          let data: Record<string, unknown>;
          try { data = JSON.parse(line.slice(6)); } catch { continue; }

          if (data.type === 'thinking') {
            // keep thinking state
          } else if (data.type === 'chunk') {
            if (!added) {
              setMessages(prev => [...prev, { id: aId, role: 'assistant', text: '', isStreaming: true }]);
              added = true;
              setThinking(false);
            }
            full += data.delta as string;
            const snapshot = full;
            setMessages(prev => prev.map(m => m.id === aId ? { ...m, text: snapshot } : m));
          } else if (data.type === 'done') {
            const finalText = (data.fullText as string) || full;
            const sources = (data.sources as Source[]) || [];
            const precision = data.precision as PrecisionInfo;
            setMessages(prev => prev.map(m =>
              m.id === aId ? { ...m, text: finalText, sources, precision, isStreaming: false } : m
            ));
            setThinking(false);
          } else if (data.type === 'error') {
            if (!added) {
              setMessages(prev => [...prev, {
                id: aId, role: 'assistant',
                text: `Error: ${data.message}`, isStreaming: false,
              }]);
              added = true;
            }
            setThinking(false);
          }
        }
      }
    } catch {
      setThinking(false);
      setMessages(prev => [...prev, {
        id: aId, role: 'assistant',
        text: 'Connection error — make sure the backend is running on port 8000.',
        precision: { score: 0, level: 'error', label: 'Error', description: 'Could not reach chat service' },
      }]);
    }
  };

  return (
    <>
      {!open && (
        <button className="chat-fab" onClick={() => setOpen(true)} title="A2A Sensei — Protocol Specialist">
          <span className="chat-fab-icon">✦</span>
          <span className="chat-fab-pulse" />
        </button>
      )}

      {open && (
        <div className="chat-panel">
          <div className="chat-header">
            <div className="chat-header-left">
              <div className="chat-header-orb">✦</div>
              <div>
                <div className="chat-header-title">A2A Sensei</div>
                <div className="chat-header-sub">Search Grounded • Multi-Source</div>
              </div>
            </div>
            <button className="chat-close" onClick={() => setOpen(false)}>✕</button>
          </div>

          <div className="chat-messages">
            {messages.map(msg => (
              <div key={msg.id} className={`chat-msg chat-msg--${msg.role}`}>
                <div className={`chat-bubble chat-bubble--${msg.role}`}>
                  <div className="chat-bubble-text">
                    {renderMarkdown(msg.text)}
                    {msg.isStreaming && <span className="chat-cursor">▊</span>}
                  </div>

                  {msg.precision && msg.id !== 'welcome' && (
                    <div className="chat-precision" style={{ borderLeftColor: precisionColor(msg.precision.score) }}>
                      <span className="chat-precision-score" style={{ color: precisionColor(msg.precision.score) }}>
                        {msg.precision.score}%
                      </span>
                      <div className="chat-precision-meta">
                        <span className="chat-precision-label">{msg.precision.label}</span>
                        <span className="chat-precision-desc">{msg.precision.description}</span>
                      </div>
                    </div>
                  )}

                  {msg.sources && msg.sources.length > 0 && (
                    <div className="chat-sources">
                      {msg.sources.map((src, i) => (
                        <a key={i} href={src.uri} target="_blank" rel="noopener noreferrer" className="chat-source-chip">
                          <span className="chat-source-cat">{src.category}</span>
                          <span className="chat-source-title">{src.title || domain(src.uri)}</span>
                        </a>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}

            {thinking && (
              <div className="chat-msg chat-msg--assistant">
                <div className="chat-bubble chat-bubble--assistant">
                  <div className="chat-thinking">
                    <span className="chat-dot" />
                    <span className="chat-dot" />
                    <span className="chat-dot" />
                  </div>
                </div>
              </div>
            )}
            <div ref={bottomRef} />
          </div>

          <div className="chat-input-bar">
            <input
              ref={inputRef}
              className="chat-field"
              type="text"
              placeholder="Ask about A2A protocol..."
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && send()}
              disabled={thinking}
            />
            <button className="chat-send" onClick={send} disabled={!input.trim() || thinking}>
              ↑
            </button>
          </div>
        </div>
      )}
    </>
  );
}

/* Helpers */
function uid(): string {
  return Date.now().toString(36) + Math.random().toString(36).slice(2);
}

function domain(uri: string): string {
  try { return new URL(uri).hostname.replace('www.', ''); } catch { return 'source'; }
}

function renderMarkdown(text: string): (string | JSX.Element)[] {
  // Minimal inline markdown: **bold** and `code`
  const parts: (string | JSX.Element)[] = [];
  const regex = /(\*\*(.+?)\*\*|`(.+?)`)/g;
  let last = 0;
  let match: RegExpExecArray | null;
  let key = 0;
  while ((match = regex.exec(text)) !== null) {
    if (match.index > last) parts.push(text.slice(last, match.index));
    if (match[2]) parts.push(<strong key={key++}>{match[2]}</strong>);
    else if (match[3]) parts.push(<code key={key++} className="chat-inline-code">{match[3]}</code>);
    last = match.index + match[0].length;
  }
  if (last < text.length) parts.push(text.slice(last));
  return parts;
}
