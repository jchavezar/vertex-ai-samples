import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Loader2, Shield, Gavel, Scale, Play } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import './AuditSimulator.css';

const AuditSimulator = ({ isOpen, onClose }) => {
  const [round, setRound] = useState(0); // 0=input, 1=auditor, 2=defense, 3=verdict
  const [scenario, setScenario] = useState('');
  const [auditorText, setAuditorText] = useState('');
  const [defenseText, setDefenseText] = useState('');
  const [verdictText, setVerdictText] = useState('');
  const [resilienceScore, setResilienceScore] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const parseSSE = async (response, onText) => {
    const reader = response.body.getReader();
    const decoder = new TextDecoder('utf-8');
    let buffer = '';
    let fullText = '';
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
            if (dataStr === '[DONE]') return fullText;
            try {
              const parsed = JSON.parse(dataStr);
              if (parsed.text) { fullText += parsed.text; onText(fullText); }
            } catch {}
          }
        }
      }
    }
    return fullText;
  };

  const startSimulation = async () => {
    if (!scenario.trim()) return;
    setRound(1);
    setIsLoading(true);
    setAuditorText('');
    setDefenseText('');
    setVerdictText('');
    setResilienceScore(null);

    try {
      // Round 1: Auditor questions
      const r1 = await fetch('/pwc/api/audit-sim/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ scenario: scenario, round_num: 1 })
      });
      const auditorResult = await parseSSE(r1, (text) => setAuditorText(text));

      // Round 2: Defense responses
      setRound(2);
      const r2 = await fetch('/pwc/api/audit-sim/round', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ scenario: scenario, round_num: 2, auditor_questions: auditorResult })
      });
      const defenseResult = await parseSSE(r2, (text) => setDefenseText(text));

      // Round 3: Verdict
      setRound(3);
      const r3 = await fetch('/pwc/api/audit-sim/round', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ scenario: scenario, round_num: 3, auditor_questions: auditorResult, defense_responses: defenseResult })
      });
      const verdictResult = await parseSSE(r3, (text) => {
        setVerdictText(text);
        // Try to extract score from text
        const scoreMatch = text.match(/(\d+)\s*\/\s*10|score[:\s]*(\d+)/i);
        if (scoreMatch) {
          setResilienceScore(parseInt(scoreMatch[1] || scoreMatch[2]));
        }
      });

      // Final score extraction
      const finalMatch = verdictResult.match(/(\d+)\s*\/\s*10|score[:\s]*(\d+)/i);
      if (finalMatch) setResilienceScore(parseInt(finalMatch[1] || finalMatch[2]));

    } catch (error) {
      setAuditorText(prev => prev || "Error running simulation. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  const reset = () => {
    setRound(0);
    setScenario('');
    setAuditorText('');
    setDefenseText('');
    setVerdictText('');
    setResilienceScore(null);
  };

  const getScoreColor = (score) => {
    if (score >= 7) return 'score-high';
    if (score >= 4) return 'score-mid';
    return 'score-low';
  };

  const getBarColor = (score) => {
    if (score >= 7) return '#22c55e';
    if (score >= 4) return '#f59e0b';
    return '#ef4444';
  };

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <motion.div className="audit-overlay" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} onClick={onClose}>
        <motion.div className="audit-modal" initial={{ scale: 0.92, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.92, opacity: 0 }} onClick={(e) => e.stopPropagation()}>
          <div className="audit-header">
            <div>
              <div className="audit-title">AI Tax Audit Simulator</div>
              <div className="audit-subtitle">Adversarial stress-test your tax position against an AI auditor</div>
            </div>
            <button className="audit-close" onClick={onClose}><X size={20} /></button>
          </div>

          <div className="audit-body">
            {/* Round indicator */}
            <div className="round-indicator">
              {['Auditor', 'Defense', 'Verdict'].map((label, idx) => {
                const r = idx + 1;
                return (
                  <React.Fragment key={r}>
                    <div className={`round-circle ${round >= r ? (round > r ? 'completed' : 'active') : ''}`}>
                      {round > r ? '✓' : r}
                      <span className="round-label">{label}</span>
                    </div>
                    {idx < 2 && <div className={`round-line ${round > r ? 'completed' : ''}`}></div>}
                  </React.Fragment>
                );
              })}
            </div>

            {/* Input state */}
            {round === 0 && (
              <motion.div className="scenario-form" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
                <label className="scenario-label">Describe your tax position or scenario</label>
                <textarea
                  className="scenario-textarea"
                  placeholder="e.g., Our US parent licenses IP to an Irish subsidiary at a 2% royalty rate. The Irish entity has 12 employees and generates €200M in annual revenue from European customers..."
                  value={scenario}
                  onChange={(e) => setScenario(e.target.value)}
                />
                <p className="scenario-hint">Be specific about entity structure, transaction types, and amounts for the most realistic simulation.</p>
                <button className="start-sim-btn" onClick={startSimulation} disabled={!scenario.trim()}>
                  <Play size={18} /> Launch Simulation
                </button>
              </motion.div>
            )}

            {/* Auditor + Defense panels */}
            {round >= 1 && round <= 3 && (
              <div className="audit-panels">
                <div className="audit-panel panel-auditor">
                  <div className="panel-title">
                    <div className="panel-icon panel-icon-auditor"><Gavel size={18} /></div>
                    <div>
                      <div className="panel-name">Tax Authority Auditor</div>
                      <div className="panel-role">Adversarial Examiner</div>
                    </div>
                  </div>
                  <div className="panel-content">
                    {round === 1 && !auditorText && <div className="panel-loading"><Loader2 size={16} className="spin" /> Examining position...</div>}
                    <ReactMarkdown>{auditorText}</ReactMarkdown>
                  </div>
                </div>

                <div className="audit-panel panel-defense">
                  <div className="panel-title">
                    <div className="panel-icon panel-icon-defense"><Shield size={18} /></div>
                    <div>
                      <div className="panel-name">Defense Advisor</div>
                      <div className="panel-role">Tax Defense Counsel</div>
                    </div>
                  </div>
                  <div className="panel-content">
                    {round < 2 && <div className="panel-loading" style={{ opacity: 0.4 }}>Waiting for auditor...</div>}
                    {round === 2 && !defenseText && <div className="panel-loading"><Loader2 size={16} className="spin" /> Constructing defense...</div>}
                    <ReactMarkdown>{defenseText}</ReactMarkdown>
                  </div>
                </div>
              </div>
            )}

            {/* Verdict panel */}
            {round === 3 && (
              <motion.div className="verdict-panel" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
                <div className="verdict-header">
                  <div className="verdict-icon"><Scale size={22} /></div>
                  <div>
                    <div className="verdict-title">Tribunal Verdict</div>
                    <div className="verdict-subtitle">Independent assessment of audit resilience</div>
                  </div>
                </div>

                {resilienceScore !== null && (
                  <div className="resilience-score">
                    <div className={`score-number ${getScoreColor(resilienceScore)}`}>{resilienceScore}</div>
                    <div style={{ flex: 1 }}>
                      <div className="score-bar-bg">
                        <div className="score-bar-fill" style={{ width: `${resilienceScore * 10}%`, background: getBarColor(resilienceScore) }}></div>
                      </div>
                      <div className="score-label">Audit Resilience Score (1-10)</div>
                    </div>
                  </div>
                )}

                <div className="verdict-content">
                  {!verdictText && <div className="panel-loading"><Loader2 size={16} className="spin" /> Deliberating...</div>}
                  <ReactMarkdown>{verdictText}</ReactMarkdown>
                </div>
              </motion.div>
            )}

            {/* Reset */}
            {round === 3 && !isLoading && verdictText && (
              <div className="audit-actions">
                <button className="reset-audit-btn" onClick={reset}>Run New Simulation</button>
              </div>
            )}
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default AuditSimulator;
