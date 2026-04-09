import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { CheckCircle, Loader2, ArrowRight, ArrowLeft } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import './PillarTwoEngine.css';

const jurisdictions = ["United States", "United Kingdom", "Germany", "France", "Ireland", "Netherlands", "Singapore", "Japan", "Australia", "Brazil", "India", "UAE", "Switzerland", "Luxembourg", "Hong Kong", "South Korea", "Canada", "Italy", "Spain", "Mexico"];
const revenueOptions = ["Under €750M", "€750M - €2B", "€2B - €10B", "Over €10B"];

const PillarTwoEngine = () => {
  const [step, setStep] = useState(1);
  const [selected, setSelected] = useState([]);
  const [revenue, setRevenue] = useState('');
  const [etr, setEtr] = useState('');
  const [assessment, setAssessment] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const toggleJurisdiction = (j) => {
    setSelected(prev => prev.includes(j) ? prev.filter(x => x !== j) : [...prev, j]);
  };

  const runAssessment = async () => {
    setStep(3);
    setIsLoading(true);
    setAssessment('');
    try {
      const response = await fetch('/pwc/api/pillar-two/assess', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ jurisdictions: selected, revenue_range: revenue, effective_tax_rate: etr ? parseFloat(etr) : null })
      });
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
              if (dataStr === '[DONE]') break;
              try { const parsed = JSON.parse(dataStr); if (parsed.text) { fullText += parsed.text; setAssessment(fullText); } } catch {}
            }
          }
        }
      }
    } catch (error) {
      setAssessment("Error generating assessment. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  const reset = () => { setStep(1); setSelected([]); setRevenue(''); setEtr(''); setAssessment(''); };

  return (
    <section className="pillar-section">
      <div className="pillar-container">
        <div className="pillar-header">
          <h2>Pillar Two Compliance Engine</h2>
          <p className="pillar-subtitle">OECD Global Minimum Tax Assessment</p>
        </div>

        <div className="step-indicator">
          {[1, 2, 3].map((s, idx) => (
            <React.Fragment key={s}>
              <div className={`step-circle ${step >= s ? (step > s ? 'completed' : 'active') : ''}`}>
                {step > s ? <CheckCircle size={18} /> : s}
              </div>
              {idx < 2 && <div className={`step-line ${step > s ? 'completed' : ''}`}></div>}
            </React.Fragment>
          ))}
        </div>

        {step === 1 && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
            <h3 className="step-title">Select Jurisdictions</h3>
            <p className="step-desc">Choose the jurisdictions where your multinational has subsidiaries or permanent establishments.</p>
            <div className="jurisdiction-grid">
              {jurisdictions.map((j) => (
                <button key={j} className={`jurisdiction-chip ${selected.includes(j) ? 'selected' : ''}`} onClick={() => toggleJurisdiction(j)}>{j}</button>
              ))}
            </div>
            <div className="step-actions">
              <button className="next-btn" onClick={() => setStep(2)} disabled={selected.length === 0}>
                Continue <ArrowRight size={16} />
              </button>
            </div>
          </motion.div>
        )}

        {step === 2 && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
            <h3 className="step-title">Entity Data</h3>
            <div className="entity-form">
              <div className="form-group">
                <label className="form-label">Consolidated Revenue Range</label>
                <select className="form-select" value={revenue} onChange={(e) => setRevenue(e.target.value)}>
                  <option value="">Select range...</option>
                  {revenueOptions.map(r => <option key={r} value={r}>{r}</option>)}
                </select>
              </div>
              <div className="form-group">
                <label className="form-label">Average Effective Tax Rate (%)</label>
                <input className="form-input" type="number" placeholder="e.g. 12.5" value={etr} onChange={(e) => setEtr(e.target.value)} min="0" max="100" step="0.1" />
              </div>
              <div className="step-actions">
                <button className="back-btn" onClick={() => setStep(1)}><ArrowLeft size={16} /> Back</button>
                <button className="next-btn" onClick={runAssessment} disabled={!revenue}>Run Assessment <ArrowRight size={16} /></button>
              </div>
            </div>
          </motion.div>
        )}

        {step === 3 && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
            <div className="assessment-result">
              {isLoading && !assessment && (
                <div className="assessment-loading"><Loader2 size={24} className="spin" /><span>Analyzing Pillar Two compliance across {selected.length} jurisdictions...</span></div>
              )}
              <div className="assessment-content">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>{assessment}</ReactMarkdown>
              </div>
              {!isLoading && assessment && (
                <div className="step-actions"><button className="reset-btn" onClick={reset}>Start New Assessment</button></div>
              )}
            </div>
          </motion.div>
        )}
      </div>
    </section>
  );
};

export default PillarTwoEngine;
