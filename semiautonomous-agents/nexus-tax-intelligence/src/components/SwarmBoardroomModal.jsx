import React, { useState } from 'react';
import { X, Zap, Shield, Globe, Send, Loader2 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import ReactMarkdown from 'react-markdown';
import './SwarmBoardroomModal.css';

const agents = [
  { id: 'strategist', name: 'The Aggressive Strategist', icon: Zap, color: '#FD5108' },
  { id: 'auditor', name: 'The Conservative Auditor', icon: Shield, color: '#D93954' },
  { id: 'economist', name: 'The Global Economist', icon: Globe, color: '#D04A02' },
];

const quickActions = ["AI Tariffs", "Pillar Two", "Offshoring Risk", "Digital IP Restructuring"];

const SwarmBoardroomModal = ({ isOpen, onClose }) => {
  const [prompt, setPrompt] = useState('');
  const [isDebating, setIsDebating] = useState(false);
  const [agentResponses, setAgentResponses] = useState({});
  const [activeAgent, setActiveAgent] = useState(null);
  const [debateComplete, setDebateComplete] = useState(false);

  const startDebate = async (text) => {
    const q = text || prompt;
    if (!q.trim()) return;
    setIsDebating(true);
    setAgentResponses({});
    setDebateComplete(false);
    setActiveAgent(null);

    try {
      const response = await fetch('/pwc/api/future/boardroom', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: q })
      });
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
          const lines = sseEvent.split(/\r?\n/);
          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const dataStr = line.substring(6).trim();
              try {
                const parsed = JSON.parse(dataStr);
                if (parsed.type === 'agent_start') setActiveAgent(parsed.agent_id);
                else if (parsed.type === 'chunk') {
                  setAgentResponses(prev => ({ ...prev, [parsed.agent_id]: (prev[parsed.agent_id] || '') + parsed.text }));
                }
                else if (parsed.type === 'agent_end') setActiveAgent(null);
                else if (parsed.type === 'done') { setDebateComplete(true); setIsDebating(false); }
              } catch (err) { /* skip */ }
            }
          }
        }
      }
    } catch (error) {
      console.error("Boardroom error:", error);
      setIsDebating(false);
    }
  };

  const reset = () => {
    setPrompt('');
    setAgentResponses({});
    setDebateComplete(false);
    setActiveAgent(null);
  };

  if (!isOpen) return null;

  const hasStarted = Object.keys(agentResponses).length > 0;

  return (
    <AnimatePresence>
      <motion.div className="boardroom-overlay" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
        <motion.div className="boardroom-modal" initial={{ scale: 0.95 }} animate={{ scale: 1 }}>
          <div className="boardroom-header">
            <div>
              <h2 className="boardroom-title">Innovation Lab</h2>
              <p className="boardroom-subtitle">Multi-Agent Tax Strategy Arena</p>
            </div>
            <button className="boardroom-close" onClick={() => { onClose(); reset(); }}><X size={20} /></button>
          </div>

          <div className="boardroom-body">
            {!hasStarted && (
              <div className="boardroom-empty">
                <div className="holo-core">
                  <div className="holo-ring ring-1"></div>
                  <div className="holo-ring ring-2"></div>
                  <div className="holo-ring ring-3"></div>
                  <div className="holo-center">N</div>
                </div>
                <p className="holo-desc">Three AI agents will debate your tax challenge from opposing perspectives.</p>
              </div>
            )}

            {agents.map((agent) => {
              const AgentIcon = agent.icon;
              const text = agentResponses[agent.id];
              if (!text && activeAgent !== agent.id) return null;
              return (
                <motion.div key={agent.id} className="agent-card" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
                  <div className="agent-header">
                    <div className="agent-icon" style={{ background: `${agent.color}22` }}><AgentIcon size={20} style={{ color: agent.color }} /></div>
                    <span className="agent-name">{agent.name}</span>
                    {activeAgent === agent.id && <div className="equalizer">{[...Array(8)].map((_, i) => <div key={i} className="eq-bar" style={{ animationDelay: `${i * 0.1}s` }}></div>)}</div>}
                  </div>
                  <div className="agent-text"><ReactMarkdown>{text || ''}</ReactMarkdown></div>
                </motion.div>
              );
            })}

            {debateComplete && <div className="debate-complete"><button className="reset-debate-btn" onClick={reset}>Run Another Debate</button></div>}
          </div>

          {!debateComplete && (
            <>
              <div className="quick-actions">
                {quickActions.map((qa, idx) => (
                  <button key={idx} className="quick-btn" onClick={() => { setPrompt(qa); startDebate(qa); }} disabled={isDebating}>{qa}</button>
                ))}
              </div>
              <div className="boardroom-input-area">
                <input className="boardroom-input" value={prompt} onChange={(e) => setPrompt(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && startDebate()} placeholder="Enter a tax challenge to debate..." disabled={isDebating} />
                <button className="boardroom-submit" onClick={() => startDebate()} disabled={isDebating || !prompt.trim()}>
                  {isDebating ? <Loader2 size={18} className="spin" /> : <Send size={18} />}
                </button>
              </div>
            </>
          )}
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default SwarmBoardroomModal;
