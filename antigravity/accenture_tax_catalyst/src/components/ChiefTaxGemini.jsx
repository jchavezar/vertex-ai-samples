import React, { useState, useRef, useEffect } from 'react';
import { Send, Sparkles, Bot, User, FileText, ChevronRight, Globe, Loader2, Building, X } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import './ChiefTaxGemini.css';

const ChiefTaxGemini = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: 'Hello. I am your **Accenture Chief Tax Catalyst**, accelerated by Gemini 3.1 Flash Lite. How can I assist with your global tax strategy today?',
      isInitial: true
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);
  const chatContainerRef = useRef(null);

  const scrollToBottom = (force = false) => {
    if (chatContainerRef.current) {
      const { scrollTop, scrollHeight, clientHeight } = chatContainerRef.current;
      const isNearBottom = scrollHeight - scrollTop - clientHeight < 150;
      if (isNearBottom || force) {
        chatContainerRef.current.scrollTop = scrollHeight;
      }
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const handleSendRef = useRef();

  useEffect(() => {
    const handleTrigger = (e) => {
      setIsOpen(true); // Auto-open the chat window
      if (handleSendRef.current) {
        handleSendRef.current(e.detail);
      }
    };
    window.addEventListener('triggerGemini', handleTrigger);
    return () => window.removeEventListener('triggerGemini', handleTrigger);
  }, []);

  const suggestedPrompts = [
    "Tax implications: Vietnam Mfg / Singapore IP",
    "OECD Pillar Two EU updates",
    "Optimal LATAM entity expansion structure"
  ];

  const handleSend = async (text) => {
    if (!text.trim() || isTyping) return;
    
    // Add user message
    setMessages(prev => [...prev, { role: 'user', content: text }]);
    setInputValue('');
    setIsTyping(true);

    // Initialize an empty assistant message
    setMessages(prev => [...prev, { role: 'assistant', content: '' }]);
    
    setTimeout(() => scrollToBottom(true), 50);

    try {
      const newMessages = [...messages, { role: 'user', content: text }];
      
      const response = await fetch('api/gemini/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ messages: newMessages })
      });

      if (!response.body) throw new Error("ReadableStream not yet supported.");

      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let buffer = '';
      
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        
        // Process complete SSE events separated by \n\n or \r\n\r\n
        const parts = buffer.split(/\r?\n\r?\n/);
        buffer = parts.pop() || ''; // keep the last incomplete part in the buffer
        
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
                  console.error("Error parsing SSE JSON:", e, "Data string:", dataStr);
                }
              }
            }
          }
        }
      }
    } catch (error) {
      console.error("Error communicating with backend:", error);
      setMessages(prev => {
        const newMessages = [...prev];
        const lastMsg = { ...newMessages[newMessages.length - 1] };
        lastMsg.content = `Sorry, an error occurred while connecting to the core strategic systems. (${error.message})`;
        newMessages[newMessages.length - 1] = lastMsg;
        return newMessages;
      });
    } finally {
      setIsTyping(false);
    }
  };

  // Update ref to latest handleSend instance
  useEffect(() => {
    handleSendRef.current = handleSend;
  }, [handleSend]);

  const overrideSubmit = (e) => {
    e.preventDefault();
    if (!isTyping) handleSend(inputValue);
  };

  return (
    <section className="gemini-section" id="gemini-section">
      <div className="gemini-container">
        
        <div className="gemini-info">
          <div className="accenture-logo-placeholder">
            <span className="accenture-text" style={{ position: 'relative', display: 'inline-flex', alignItems: 'center' }}>
              <span style={{ fontSize: '24px', fontWeight: '700', color: '#A100FF', letterSpacing: '-0.5px' }}>accenture</span>
              <span style={{ position: 'absolute', top: '-4px', right: '28px', color: '#ffffff', fontSize: '16px', fontWeight: '900' }}>&gt;</span>
            </span>
          </div>
          <h2>Your Chief <br/>Tax Gemini</h2>
          <p>
            Navigate complexities instantly. Our conversational AI agent synthesizes global 
            legislation, your corporate structure, and real-time market data to provide 
            actionable tax intelligence.
          </p>
          
          <div className="features-list">
            <div className="feature-item">
              <div className="feature-icon"><FileText size={18} /></div>
              <div>
                <h4>Contract Analysis</h4>
                <span>Instantly reviews intercompany agreements.</span>
              </div>
            </div>
            <div className="feature-item">
              <div className="feature-icon"><Globe size={18} /></div>
              <div>
                <h4>Multi-jurisdictional Logic</h4>
                <span>Cross-references treaties across 150+ countries.</span>
              </div>
            </div>
          </div>
        </div>

      {/* Floating Toggle Button */}
      {!isOpen && (
        <button className="chat-toggle-btn" onClick={() => setIsOpen(true)}>
          <Bot size={24} />
        </button>
      )}

      {/* Chat Window Overlay */}
      <AnimatePresence>
        {isOpen && (
          <motion.div 
            className="gemini-interface glass-panel"
            drag={window.innerWidth > 768}
            dragMomentum={false}
            style={{ cursor: window.innerWidth > 768 ? 'move' : 'default' }}
          >
          <div className="chat-window">
            <div className="chat-header">
               <div className="chat-header-left">
                 <Building size={18} className="text-accent-primary" />
                 <span className="chat-header-title">Accenture Catalyst Engine</span>
                 <div className="chat-header-status">
                   <span className="pulse-dot"></span> Online
                 </div>
               </div>
               <button className="chat-window-close-btn" onClick={() => setIsOpen(false)}>
                 <X size={18} />
               </button>
            </div>
            
            <div className="chat-messages" ref={chatContainerRef}>
              <AnimatePresence>
                {messages.map((msg, idx) => (
                  <motion.div 
                    key={idx}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3 }}
                    className={`message-wrapper ${msg.role === 'user' ? 'wrapper-user' : 'wrapper-assistant'}`}
                  >
                    <div className={`avatar ${msg.role === 'user' ? 'avatar-user' : 'avatar-assistant'}`}>
                      {msg.role === 'user' ? <User size={16} /> : <span className="accenture-avatar-text" style={{ fontWeight: '800', color: '#fff' }}>A</span>}
                    </div>
                    <div className={`message-bubble ${msg.role === 'user' ? 'bubble-user' : 'bubble-assistant'}`}>
                      {msg.role === 'assistant' ? (
                        <div className="markdown-body">
                          {(!msg.content || msg.content.trim() === '') && isTyping ? (
                            <div className="ai-dynamic-typing">
                              <div className="ai-dynamic-header">
                                <motion.div 
                                  animate={{ rotate: 360 }}
                                  transition={{ duration: 4, repeat: Infinity, ease: "linear" }}
                                  className="ai-dynamic-icon-wrapper"
                                >
                                  <Sparkles size={16} className="ai-dynamic-icon" />
                                </motion.div>
                                <span className="ai-dynamic-title">Synthesizing Global Insights</span>
                                <motion.span 
                                  className="ai-dynamic-dots"
                                  animate={{ opacity: [0.2, 1, 0.2] }}
                                  transition={{ duration: 1.5, repeat: Infinity }}
                                >
                                  ...
                                </motion.span>
                              </div>
                              <div className="ai-dynamic-scanner">
                                <motion.div 
                                  className="ai-dynamic-laser"
                                  animate={{ left: ['-10%', '110%'] }}
                                  transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
                                />
                                <div className="ai-dynamic-grid"></div>
                              </div>
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

            {messages.length === 1 && (
              <div className="suggested-prompts">
                <p className="suggested-title">Suggested analysis:</p>
                {suggestedPrompts.map((prompt, idx) => (
                  <button 
                    key={idx} 
                    className="prompt-btn"
                    onClick={() => handleSend(prompt)}
                  >
                    {prompt} <ChevronRight size={14} />
                  </button>
                ))}
              </div>
            )}
            
            <form className="chat-input-area" onSubmit={overrideSubmit}>
              <div className="input-wrapper">
                <input 
                  type="text" 
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  placeholder="Ask a global tax question to the Accenture Catalyst..."
                  className="chat-input"
                />
                <button 
                  type="submit" 
                  className={`send-btn ${inputValue.trim() ? 'active' : ''}`}
                  disabled={!inputValue.trim() || isTyping}
                >
                  <Send size={18} />
                </button>
              </div>
            </form>
          </div>
          </motion.div>
        )}
      </AnimatePresence>
      </div>
    </section>
  );
};

export default ChiefTaxGemini;
