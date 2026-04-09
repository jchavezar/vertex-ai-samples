import React, { useState, useRef, useEffect } from 'react';
import { Send, Loader2, Bot } from 'lucide-react';
import { motion } from 'framer-motion';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import './ChiefTaxGemini.css';

const suggestedPrompts = [
  "What are the tax implications if we manufacture in Vietnam but hold IP in Singapore?",
  "Summarize the latest OECD Pillar Two updates affecting our EU entities.",
  "Generate an optimal entity structure for our upcoming expansion into LATAM."
];

const ChiefTaxGemini = () => {
  const [messages, setMessages] = useState([
    { role: 'assistant', content: "I am your **Nexus Chief Tax Intelligence Advisor**. I can help you navigate complex global tax landscapes, analyze transfer pricing structures, and assess regulatory risks across 150+ jurisdictions.\n\nHow can I assist your tax strategy today?" }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const chatContainerRef = useRef(null);
  const isInitialRender = useRef(true);

  useEffect(() => {
    if (isInitialRender.current) {
      isInitialRender.current = false;
      return;
    }
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [messages]);

  const sendMessage = async (text) => {
    const userMessage = text || input.trim();
    if (!userMessage || isLoading) return;
    setInput('');

    const newMessages = [...messages, { role: 'user', content: userMessage }];
    setMessages(newMessages);
    setIsLoading(true);

    const apiMessages = newMessages.filter(m => m.role !== 'assistant' || newMessages.indexOf(m) !== 0).map(m => ({
      role: m.role === 'assistant' ? 'model' : 'user',
      content: m.content
    }));

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
                  setMessages(prev => {
                    const updated = [...prev];
                    updated[updated.length - 1] = { role: 'assistant', content: aiText };
                    return updated;
                  });
                }
              } catch (err) { /* skip */ }
            }
          }
        }
      }
    } catch (error) {
      console.error("Chat error:", error);
      setMessages(prev => [...prev, { role: 'assistant', content: "I apologize, but I'm experiencing a connectivity issue. Please try again." }]);
    } finally {
      setIsLoading(false);
    }
  };

  const showSuggested = messages.length <= 1;

  return (
    <section className="gemini-section">
      <div className="gemini-container">
        <motion.div className="gemini-info" initial={{ opacity: 0, x: -30 }} whileInView={{ opacity: 1, x: 0 }} viewport={{ once: true }}>
          <div className="gemini-avatar">N</div>
          <h2>Your Nexus Tax Advisor</h2>
          <p>AI-powered tax intelligence with real-time Google Search grounding, multi-jurisdictional expertise, and strategic advisory capabilities.</p>
          <div className="gemini-badge">Powered by Gemini</div>
        </motion.div>

        <motion.div className="gemini-chat" initial={{ opacity: 0, x: 30 }} whileInView={{ opacity: 1, x: 0 }} viewport={{ once: true }}>
          <div className="chat-header">
            <span className="chat-title">Nexus Intelligence Engine</span>
            <span className="online-indicator"><span className="online-dot"></span> Online</span>
          </div>

          <div className="chat-messages" ref={chatContainerRef}>
            {messages.map((msg, idx) => (
              <div key={idx} className={`message message-${msg.role === 'assistant' ? 'ai' : 'user'}`}>
                {msg.role === 'assistant' && <div className="ai-avatar">N</div>}
                <div className={msg.role === 'assistant' ? 'ai-bubble' : 'user-bubble'}>
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>{msg.content}</ReactMarkdown>
                </div>
              </div>
            ))}
            {isLoading && messages[messages.length - 1]?.role !== 'assistant' && (
              <div className="message message-ai">
                <div className="ai-avatar">N</div>
                <div className="ai-bubble loading-bubble"><span className="loading-dots"><span></span><span></span><span></span></span></div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {showSuggested && (
            <div className="suggested-prompts">
              {suggestedPrompts.map((prompt, idx) => (
                <button key={idx} className="prompt-btn" onClick={() => sendMessage(prompt)}>{prompt}</button>
              ))}
            </div>
          )}

          <div className="chat-input-area">
            <input className="chat-input" value={input} onChange={(e) => setInput(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && sendMessage()} placeholder="Ask about global tax strategy..." disabled={isLoading} />
            <button className="send-btn" onClick={() => sendMessage()} disabled={isLoading || !input.trim()}>
              {isLoading ? <Loader2 size={18} className="spin" /> : <Send size={18} />}
            </button>
          </div>
        </motion.div>
      </div>
    </section>
  );
};

export default ChiefTaxGemini;
