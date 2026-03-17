import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Send, BrainCircuit, ShieldAlert, Globe, MessageSquare } from 'lucide-react';
import './SwarmBoardroomModal.css';

const EVENT_ICONS = {
  strategist: <BrainCircuit className="agent-icon" />,
  auditor: <ShieldAlert className="agent-icon" />,
  economist: <Globe className="agent-icon" />
};

export default function SwarmBoardroomModal({ isOpen, onClose }) {
  const [prompt, setPrompt] = useState("");
  const [messages, setMessages] = useState([]);
  const [isSimulating, setIsSimulating] = useState(false);
  const [activeAgent, setActiveAgent] = useState(null);
  
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, activeAgent]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!prompt.trim() || isSimulating) return;

    setMessages([]);
    setIsSimulating(true);
    setActiveAgent(null);

    try {
      // Backend expects a POST request, returning an SSE stream
      const response = await fetch('http://localhost:8009/api/future/boardroom', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt })
      });

      if (!response.body) throw new Error('ReadableStream not supported');

      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      
      let rawData = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        rawData += decoder.decode(value, { stream: true });
        
        // Split by SSE double newline
        const lines = rawData.split('\n\n');
        // Keep the last part if not complete
        rawData = lines.pop() || "";
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const dataStr = line.substring(6).trim();
            if(!dataStr) continue;
            
            try {
              const data = JSON.parse(dataStr);
              
              if (data.type === 'agent_start') {
                setActiveAgent(data.agent_id);
                setMessages(prev => [
                  ...prev,
                  { agent_id: data.agent_id, agent_name: data.agent_name, text: "" }
                ]);
              } else if (data.type === 'chunk') {
                setMessages(prev => {
                  const newMsgs = [...prev];
                  const lastMsg = newMsgs[newMsgs.length - 1];
                  if (lastMsg && lastMsg.agent_id === data.agent_id) {
                    lastMsg.text += data.text;
                  }
                  return newMsgs;
                });
              } else if (data.type === 'agent_end') {
                setActiveAgent(null);
              } else if (data.type === 'done') {
                setIsSimulating(false);
                setActiveAgent(null);
              } else if (data.type === 'error') {
                setIsSimulating(false);
                setActiveAgent(null);
              }
            } catch (err) {
              console.error("Parse error", err, dataStr);
            }
          }
        }
      }
    } catch (error) {
      console.error("Boardroom Error:", error);
      setIsSimulating(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="boardroom-overlay">
      <motion.div 
        className="boardroom-modal"
        initial={{ opacity: 0, scale: 0.95, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.95, y: 20 }}
        transition={{ duration: 0.3, ease: 'easeOut' }}
      >
        <div className="boardroom-header">
          <div className="boardroom-title-group">
            <MessageSquare className="boardroom-icon" size={24} />
            <h2>Autonomous Swarm Boardroom <span>[3080 LABS]</span></h2>
          </div>
          <button className="boardroom-close" onClick={onClose}><X size={20} /></button>
        </div>

        <div className="boardroom-content">
          <div className="boardroom-arena">
            {messages.length === 0 && !isSimulating ? (
              <div className="boardroom-empty-state">
                <div className="swarm-visual">
                  <span className="pulse-ring"></span>
                  <BrainCircuit size={48} className="center-brain" />
                </div>
                <h3>Deploy the Strategy Swarm</h3>
                <p>Present a global tax or macroeconomic challenge. Watch three distinct AI personas debate, critique, and synthesize a master strategy in real-time.</p>
              </div>
            ) : (
              <div className="boardroom-stream">
                <AnimatePresence>
                  {messages.map((msg, idx) => (
                    <motion.div 
                      key={idx} 
                      className={`agent-message-card active-${msg.agent_id}`}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.4 }}
                    >
                      <div className="agent-header">
                        {EVENT_ICONS[msg.agent_id]}
                        <h4>{msg.agent_name}</h4>
                        {activeAgent === msg.agent_id && (
                          <div className="agent-typing-indicator">
                            <span className="dot"></span><span className="dot"></span><span className="dot"></span>
                          </div>
                        )}
                      </div>
                      <div className="agent-body markdown-body">
                        <ReactMarkdown>{msg.text}</ReactMarkdown>
                      </div>
                    </motion.div>
                  ))}
                </AnimatePresence>
                <div ref={messagesEndRef} />
              </div>
            )}
          </div>

          <div className="boardroom-input-area">
            <form onSubmit={handleSubmit} className="boardroom-form">
              <input 
                type="text" 
                placeholder="e.g., Should we move our EMEA IP holding company from Ireland to Switzerland this year?"
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                disabled={isSimulating}
              />
              <button type="submit" disabled={!prompt.trim() || isSimulating}>
                {isSimulating ? "Simulating..." : "Initiate Swarm"} <Send size={18} style={{marginLeft: '8px'}} />
              </button>
            </form>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
