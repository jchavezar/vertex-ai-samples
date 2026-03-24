import React, { useState, useEffect, useRef } from 'react';
import { createPortal } from 'react-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Send, Sparkles, User, FileText, ChevronRight, Download, Link, Layers } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import './PdfChatOverlay.css';

const PdfChatOverlay = ({ pdfInfo, onClose }) => {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);
  const chatContainerRef = useRef(null);
  const title = pdfInfo?.title || 'Tax Briefing Document';
  const url = pdfInfo?.url || pdfInfo?.link || '#';
  const snippet = pdfInfo?.snippet || 'Detailed policy and compliance guidelines extracted from internal repositories.';

  // Initial message when overlay opens
  useEffect(() => {
    // Hidden internal message strictly to brief the context to the model - we don't display it
    const systemBrief = `CONTEXT_INJECTION: The user is deeply exploring the following document: "${title}" at URL: ${url}. Analyze queries relative to this document specifically. Ensure high accuracy and professional tone.`;

    // The first visible message we show the user
    const welcomeMsg = {
      role: 'assistant',
      content: `I have established secure access to **${title}**. What specific compliance clauses, risk factors, or calculations would you like me to analyze from this document?`,
      isInitial: true
    };
    
    // We'll store the context briefly to pass to the API on first chat
    setMessages([welcomeMsg]);
  }, [pdfInfo]);

  const scrollToBottom = () => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const handleSend = async (text) => {
    if (!text.trim() || isTyping) return;
    
    // Check if this is the first user query, if so prepend context
    let payloadMessages = [...messages.filter(m => !m.isInitial)];
    
    if (messages.length === 1) { // Only the welcome message exists
        payloadMessages.unshift({
            role: 'user', 
            content: `System Context constraints: We are chatting specifically about the document "${title}" (${url}). Snippet context: ${snippet}.\n\nUser Query: ${text}`
        });
    } else {
        payloadMessages.push({ role: 'user', content: text });
    }

    setMessages(prev => [...prev, { role: 'user', content: text }]);
    setInputValue('');
    setIsTyping(true);
    setMessages(prev => [...prev, { role: 'assistant', content: '' }]);
    
    setTimeout(scrollToBottom, 50);

    try {
      const response = await fetch('api/gemini/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ messages: payloadMessages })
      });

      if (!response.body) throw new Error("Stream closed");

      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let buffer = '';
      
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const parts = buffer.split(/\r?\n\r?\n/);
        buffer = parts.pop() || ''; 
        
        for (const sseEvent of parts) {
          if (!sseEvent.trim()) continue;
          const lines = sseEvent.split(/\r?\n/);
          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const dataStr = line.substring(6).trim();
              if (dataStr === '[DONE]') {
                setIsTyping(false);
                break;
              }
              if (dataStr) {
                try {
                  const parsed = JSON.parse(dataStr);
                  if (parsed.content || parsed.text) {
                    const textContent = parsed.content || parsed.text;
                    setMessages(prev => {
                      const newMessages = [...prev];
                      const lastMsg = { ...newMessages[newMessages.length - 1] };
                      lastMsg.content += textContent;
                      newMessages[newMessages.length - 1] = lastMsg;
                      return newMessages;
                    });
                  }
                } catch (e) {
                  // ignore incomplete JSON
                }
              }
            }
          }
        }
      }
    } catch (error) {
      console.error(error);
      setMessages(prev => {
        const newMsgs = [...prev];
        newMsgs[newMsgs.length - 1].content = "Connection to Chief Tax Gemini was interrupted. Please try again.";
        return newMsgs;
      });
    } finally {
      setIsTyping(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    handleSend(inputValue);
  };

  return createPortal(
    <div className="pdf-chat-overlay-backdrop">
      <motion.div 
        className="pdf-chat-modal"
        initial={{ opacity: 0, scale: 0.95, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.95, y: -20 }}
        transition={{ duration: 0.3, ease: 'easeOut' }}
        onClick={(e) => e.stopPropagation()} // Prevent closing when clicking inside
      >
        <div className="pdf-chat-header">
          <div className="pdf-chat-header-title">
            <Layers className="pdf-chat-icon" size={20} />
            <h3>Document Intelligence Explorer</h3>
            <span>Deep Dive Active</span>
          </div>
          <button className="close-overlay-btn" onClick={onClose} aria-label="Close Overlay">
            <X size={20} />
          </button>
        </div>

        <div className="pdf-chat-body">
          {/* Left Pane - Document Preview */}
          <div className="pdf-preview-pane">
            <div className="pdf-preview-card">
              <h4>{title}</h4>
              <p dangerouslySetInnerHTML={{ __html: snippet }}></p>
              
              <a href={url} target="_blank" rel="noreferrer" className="pdf-action-link">
                <Link size={16} /> Open Origin Source
              </a>
            </div>

            <div className="pdf-metadata">
              <div className="metadata-item">
                <span className="label">Format</span>
                <span className="value">PDF/Secure Document</span>
              </div>
              <div className="metadata-item">
                <span className="label">Analysis Engine</span>
                <span className="value">Gemini 3.1 Flash Lite</span>
              </div>
              <div className="metadata-item">
                <span className="label">Status</span>
                <span className="value" style={{color: '#00d2ff'}}>Indexed & Active</span>
              </div>
            </div>
          </div>

          {/* Right Pane - Dedicated Chat Interface */}
          <div className="pdf-chat-interface">
            <div className="pdf-chat-messages" ref={chatContainerRef}>
              <AnimatePresence>
                {messages.map((msg, idx) => (
                  <motion.div 
                    key={idx}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3 }}
                    className={`pdf-message-wrapper ${msg.role === 'user' ? 'pdf-wrapper-user' : 'pdf-wrapper-assistant'}`}
                  >
                    <div className={`pdf-avatar ${msg.role === 'user' ? 'pdf-avatar-user' : 'pdf-avatar-assistant'}`}>
                      {msg.role === 'user' ? <User size={16} /> : <span className="accenture-avatar-text" style={{ fontWeight: '800', color: '#fff' }}>A</span>}
                    </div>
                    <div className={`pdf-message-bubble ${msg.role === 'user' ? 'pdf-bubble-user' : 'pdf-bubble-assistant'}`}>
                      {msg.role === 'assistant' ? (
                        <div className="markdown-body">
                          {(!msg.content || msg.content.trim() === '') && isTyping ? (
                            <div className="pdf-scanning-indicator">
                              <motion.div animate={{ rotate: 360 }} transition={{ repeat: Infinity, duration: 2, ease: "linear" }}>
                                <Sparkles size={16} />
                              </motion.div>
                              Extracting Document Semantics...
                            </div>
                          ) : (
                            <ReactMarkdown remarkPlugins={[remarkGfm]}>
                              {msg.content}
                            </ReactMarkdown>
                          )}
                        </div>
                      ) : (
                        <span>{msg.content}</span>
                      )}
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>
              <div ref={messagesEndRef} />
            </div>

            <form className="pdf-chat-input-area" onSubmit={handleSubmit}>
              <div className="pdf-input-wrapper">
                <input 
                  type="text" 
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  placeholder={`Interrogate "${title.substring(0, 30)}..."`}
                  className="pdf-chat-input"
                  autoFocus
                />
                <button 
                  type="submit" 
                  className={`pdf-send-btn ${inputValue.trim() ? 'active' : ''}`}
                  disabled={!inputValue.trim() || isTyping}
                >
                  <Send size={18} />
                </button>
              </div>
            </form>
          </div>
        </div>
      </motion.div>
    </div>,
    document.body
  );
};

export default PdfChatOverlay;
