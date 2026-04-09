import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Loader2, Rocket, ArrowRight } from 'lucide-react';
import './TransformationRoadmap.css';

const industries = [
  "Technology", "Financial Services", "Pharmaceuticals", "Energy & Utilities",
  "Manufacturing", "Retail & Consumer", "Telecommunications", "Healthcare",
  "Real Estate", "Automotive", "Media & Entertainment", "Professional Services"
];

const TransformationRoadmap = () => {
  const [currentState, setCurrentState] = useState('');
  const [futureState, setFutureState] = useState('');
  const [industry, setIndustry] = useState('');
  const [roadmap, setRoadmap] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const generateRoadmap = async () => {
    setIsLoading(true);
    setRoadmap(null);
    try {
      const response = await fetch('/pwc/api/roadmap/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ current_state: currentState, future_state: futureState, industry })
      });
      const data = await response.json();
      setRoadmap(data);
    } catch (error) {
      setRoadmap({ error: true });
    } finally {
      setIsLoading(false);
    }
  };

  const reset = () => {
    setRoadmap(null);
    setCurrentState('');
    setFutureState('');
    setIndustry('');
  };

  return (
    <section className="roadmap-section">
      <div className="roadmap-container">
        <div className="roadmap-header">
          <h2>Tax Transformation Roadmap</h2>
          <p className="roadmap-subtitle">AI-generated phased transformation plan for your tax operating model</p>
        </div>

        {!roadmap && !isLoading && (
          <motion.div className="roadmap-form" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
            <div className="roadmap-form-grid">
              <div className="roadmap-field">
                <label>Current Tax Operating Model</label>
                <textarea
                  className="roadmap-textarea"
                  placeholder="e.g., Manual spreadsheet-based compliance, decentralized tax function across 15 entities, limited transfer pricing documentation..."
                  value={currentState}
                  onChange={(e) => setCurrentState(e.target.value)}
                />
              </div>
              <div className="roadmap-field">
                <label>Desired Future State</label>
                <textarea
                  className="roadmap-textarea"
                  placeholder="e.g., Centralized tax command center with real-time ETR monitoring, automated compliance across all jurisdictions, AI-powered transfer pricing..."
                  value={futureState}
                  onChange={(e) => setFutureState(e.target.value)}
                />
              </div>
              <div className="roadmap-field">
                <label>Industry</label>
                <select className="roadmap-select" value={industry} onChange={(e) => setIndustry(e.target.value)}>
                  <option value="">Select industry...</option>
                  {industries.map(i => <option key={i} value={i}>{i}</option>)}
                </select>
              </div>
            </div>
            <button className="generate-roadmap-btn" onClick={generateRoadmap} disabled={!currentState.trim() || !futureState.trim() || !industry}>
              <Rocket size={18} /> Generate Roadmap <ArrowRight size={16} />
            </button>
          </motion.div>
        )}

        {isLoading && (
          <div className="roadmap-loading">
            <Loader2 size={24} className="spin" />
            <span>Building your transformation roadmap...</span>
          </div>
        )}

        {roadmap && !roadmap.error && (
          <motion.div className="roadmap-result" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
            <div className="roadmap-summary">
              <h3>Executive Summary</h3>
              <p>{roadmap.executive_summary}</p>
              <div className="roadmap-meta">
                <span className="meta-chip">{roadmap.industry}</span>
                <span className="meta-chip">Est. Savings: {roadmap.total_estimated_savings}</span>
              </div>
            </div>

            <div className="roadmap-timeline">
              {(roadmap.phases || []).map((phase, idx) => (
                <motion.div
                  key={idx}
                  className="phase-card"
                  initial={{ opacity: 0, y: 30 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: idx * 0.15 }}
                >
                  <div className={`phase-number phase-${idx + 1}`}>{idx + 1}</div>
                  <div className="phase-name">{phase.phase_name}</div>
                  <div className="phase-duration">{phase.duration}</div>
                  <div className="phase-divider"></div>

                  <div className="phase-sub-title">Milestones</div>
                  <ul className="phase-list">
                    {(phase.milestones || []).map((m, i) => <li key={i}>{m}</li>)}
                  </ul>

                  <div className="phase-sub-title">Technologies</div>
                  <div className="phase-tech-tags">
                    {(phase.technologies || []).map((t, i) => <span key={i} className="tech-tag">{t}</span>)}
                  </div>

                  <div className="phase-roi">ROI: {phase.estimated_roi_percentage}</div>
                  <div className="phase-pillar">{phase.mapped_pillar}</div>
                </motion.div>
              ))}
            </div>

            <div className="roadmap-actions">
              <button className="new-roadmap-btn" onClick={reset}>Generate New Roadmap</button>
            </div>
          </motion.div>
        )}

        {roadmap && roadmap.error && (
          <div className="roadmap-loading" style={{ color: '#E0301E' }}>
            Unable to generate roadmap. Please try again.
          </div>
        )}
      </div>
    </section>
  );
};

export default TransformationRoadmap;
