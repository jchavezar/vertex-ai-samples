import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { Send, X, Paperclip } from 'lucide-react';

interface PipelineEntity {
  entity_type: string;
  page_number: number;
  content_description: string;
  structured_data?: any;
}

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  attachments?: File[];
  pipeline_data?: PipelineEntity[];
}

function App() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [session, setSession] = useState('');
  const [attachments, setAttachments] = useState<File[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Auto-scroll to bottom of chat
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isLoading]);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const newFiles = Array.from(e.target.files);
      setAttachments(prev => [...prev, ...newFiles]);
    }
    // reset input so same file can be selected again
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const removeAttachment = (indexToRemove: number) => {
    setAttachments(prev => prev.filter((_, idx) => idx !== indexToRemove));
  };

  const sendMessage = async () => {
    if ((!input.trim() && attachments.length === 0) || isLoading) return;

    const userMessage: ChatMessage = {
      id: crypto.randomUUID(),
      role: 'user',
      content: input,
      attachments: [...attachments]
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setAttachments([]);
    setIsLoading(true);

    const formData = new FormData();
    formData.append('message', userMessage.content);
    if (session) formData.append('session_id', session);
    userMessage.attachments?.forEach(file => {
      formData.append('files', file);
    });

    try {
      const response = await fetch('http://localhost:8001/chat', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Failed to send message');
      }

      const data = await response.json();
      if (data.session_id) setSession(data.session_id);

      const assistantMessage: ChatMessage = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: data.response || "No text generated.",
        pipeline_data: data.pipeline_data,
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (err) {
      console.error(err);
      const errMsg: ChatMessage = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: `**Error**: ${err}`,
      };
      setMessages(prev => [...prev, errMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <>
      <header className="app-header">
        <div className="app-title">Nexus Multi-Doc Analyst</div>
      </header>

      <main className="chat-container" ref={scrollRef}>
        {messages.length === 0 && (
          <div style={{ textAlign: 'center', margin: 'auto', color: 'var(--text-secondary)' }}>
            <h2 style={{ color: 'var(--accent-cyan)', marginBottom: '1rem', textTransform: 'uppercase', letterSpacing: '0.1em' }}>
              System Initialization Complete
            </h2>
            <p>Upload a document, charts, or images, and ask for an analysis.</p>
          </div>
        )}

        {messages.map((msg) => (
          <div key={msg.id} className={`chat-bubble ${msg.role}`}>
            {msg.attachments && msg.attachments.length > 0 && (
              <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '0.5rem', flexWrap: 'wrap' }}>
                {msg.attachments.map((file, i) => (
                  <span key={i} style={{
                    fontSize: '0.8rem', padding: '0.2rem 0.5rem',
                    background: 'rgba(255,255,255,0.1)', borderRadius: '4px'
                  }}>
                    📄 {file.name}
                  </span>
                ))}
              </div>
            )}

            {msg.pipeline_data && msg.pipeline_data.length > 0 && (
              <div style={{
                marginBottom: '1rem',
                padding: '0.75rem',
                background: 'rgba(0,0,0,0.2)',
                borderRadius: '8px',
                border: '1px solid rgba(255,255,255,0.05)'
              }}>
                <h4 style={{ margin: '0 0 0.5rem 0', color: 'var(--accent-orange)', fontSize: '0.85rem', textTransform: 'uppercase' }}>Extracted Entities Context</h4>
                <div style={{ display: 'flex', gap: '0.5rem', overflowX: 'auto', paddingBottom: '0.5rem' }}>
                  {msg.pipeline_data.map((entity, i) => (
                    <div key={i} style={{
                      minWidth: '200px',
                      background: 'var(--bg-card)',
                      padding: '0.5rem',
                      borderRadius: '4px',
                      fontSize: '0.8rem',
                      borderLeft: `2px solid ${entity.entity_type === 'chart' ? 'var(--accent-cyan)' : entity.entity_type === 'table' ? 'var(--accent-orange)' : 'var(--accent-magenta)'}`
                    }}>
                      <strong>{entity.entity_type.toUpperCase()}</strong> (Page {entity.page_number})
                      <div style={{ marginTop: '0.25rem', opacity: 0.8, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                        {entity.content_description}
                      </div>
                      <div style={{ marginTop: '0.25rem', fontSize: '0.7rem', color: 'var(--accent-cyan)', opacity: 0.6 }}>
                        + Vector Embedding (Dim 768)
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <ReactMarkdown>{msg.content}</ReactMarkdown>
          </div>
        ))}
        {isLoading && <div className="spinner"></div>}
      </main>

      <footer className="input-area">
        <div className="input-wrapper">
          {attachments.length > 0 && (
            <div className="file-list">
              {attachments.map((file, idx) => (
                <div key={idx} className="file-chip">
                  <span>{file.name}</span>
                  <X
                    size={14}
                    style={{ cursor: 'pointer' }}
                    onClick={() => removeAttachment(idx)}
                  />
                </div>
              ))}
            </div>
          )}
          <textarea
            placeholder="Type your message or attach files..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isLoading}
            rows={1}
            style={{ minHeight: attachments.length > 0 ? "40px" : "50px" }}
          />
        </div>

        <input
          type="file"
          multiple
          ref={fileInputRef}
          style={{ display: 'none' }}
          onChange={handleFileSelect}
        />
        <button
          className="btn"
          onClick={() => fileInputRef.current?.click()}
          title="Attach files"
          disabled={isLoading}
        >
          <Paperclip size={20} />
        </button>

        <button
          className="btn primary"
          onClick={sendMessage}
          disabled={isLoading || (!input.trim() && attachments.length === 0)}
        >
          <Send size={20} />
        </button>
      </footer>
    </>
  );
}

export default App;
