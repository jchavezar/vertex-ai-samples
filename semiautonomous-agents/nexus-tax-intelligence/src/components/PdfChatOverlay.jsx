import React, { useState, useRef, useEffect } from 'react';
import { X, Send, Loader2, ExternalLink } from 'lucide-react';
import { AnimatePresence, motion } from 'framer-motion';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import './PdfChatOverlay.css';

const PdfChatOverlay = ({ isOpen, onClose, document: doc }) => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    if (isOpen && doc) {
      setMessages([{
        role: 'assistant',
        content: `I'm ready to analyze **${doc.title || 'this document'}**. What would you like to know about it?`
      }]);
    }
  }, [isOpen, doc]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;
    const userMsg = input.trim();
    setInput('');

    const contextPrefix = messages.length <= 1
      ? `[Context: Document "${doc?.title}", URL: ${doc?.url || 'N/A'}, Snippet: ${doc?.snippet || 'N/A'}]\n\n`
      : '';

    const newMessages = [...messages, { role: 'user', content: userMsg }];
    setMessages(newMessages);
    setIsLoading(true);

    const apiMessages = newMessages.map((m, idx) => ({
      role: m.role === 'assistant' ? 'model' : 'user',
      content: idx === 0 ? m.content : (idx === 1 ? contextPrefix + m.content : m.content)
    })).filter((_, idx) => idx !== 0);

    try {
      const response = await fetch('/pwc/api/gemini/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ messages: apiMessages })
      });
      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let buffer = '';
      let aiText = '';
      setMessages(prev => [...prev, { role: 'assistant', content: '' }]);

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
              if (dataStr === '[DONE]') break;
              try {
                const parsed = JSON.parse(dataStr);
                if (parsed.text) {
                  aiText += parsed.text;
                  setMessages(prev => { const u = [...prev]; u[u.length - 1] = { role: 'assistant', content: aiText }; return u; });
                }
              } catch (err) { /* skip */ }
            }
          }
        }
      }
    } catch (error) {
      setMessages(prev => [...prev, { role: 'assistant', content: "Unable to process request. Please try again." }]);
    } finally {
      setIsLoading(false);
    }
  };

  if (!isOpen || !doc) return null;

  return (
    <AnimatePresence>
      <motion.div className="pdf-overlay" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
        <motion.div className="pdf-modal" initial={{ scale: 0.95, opacity: 0 }} animate={{ scale: 1, opacity: 1 }}>
          <div className="pdf-preview">
            <button className="pdf-close-btn" onClick={onClose}><X size={20} /></button>
            <div className="pdf-preview-card">
              <h3 className="pdf-title">{doc.title}</h3>
              {doc.snippet && <p className="pdf-snippet">{doc.snippet}</p>}
              {doc.url && doc.url !== '#' && (
                <a href={doc.url} target="_blank" rel="noopener noreferrer" className="pdf-origin-link">
                  <ExternalLink size={14} /> Open Origin Source
                </a>
              )}
              <div className="pdf-meta">
                <span className="pdf-meta-badge">{doc.format || 'Document'}</span>
                <span className="pdf-meta-badge">Gemini Analysis</span>
                <span className="pdf-meta-badge status-ready">Ready</span>
              </div>
            </div>
          </div>

          <div className="pdf-chat">
            <div className="pdf-chat-header">
              <span className="pdf-chat-title">Document Intelligence</span>
            </div>
            <div className="pdf-chat-messages">
              {messages.map((msg, idx) => (
                <div key={idx} className={`message message-${msg.role === 'assistant' ? 'ai' : 'user'}`}>
                  {msg.role === 'assistant' && <div className="ai-avatar-sm">N</div>}
                  <div className={msg.role === 'assistant' ? 'ai-bubble' : 'user-bubble'}>
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>{msg.content}</ReactMarkdown>
                  </div>
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>
            <div className="pdf-chat-input">
              <input value={input} onChange={(e) => setInput(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && sendMessage()} placeholder="Ask about this document..." disabled={isLoading} />
              <button onClick={sendMessage} disabled={isLoading || !input.trim()}>
                {isLoading ? <Loader2 size={18} className="spin" /> : <Send size={18} />}
              </button>
            </div>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default PdfChatOverlay;
