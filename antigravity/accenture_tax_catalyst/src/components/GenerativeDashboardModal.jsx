import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, TrendingUp, AlertTriangle, CheckCircle, Activity, Download } from 'lucide-react';
import './GenerativeDashboardModal.css';

const GenerativeDashboardModal = ({ isOpen, onClose, industry, navQuery }) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (isOpen && industry) {
      setLoading(true);
      setError(null);
      
      const fullIndustryQuery = navQuery ? `${industry} (${navQuery})` : industry;
      
      fetch('api/generate-dashboard', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ industry: fullIndustryQuery })
      })
      .then(res => res.json())
      .then(jsonData => {
        setData(jsonData);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setError("Failed to synthesize strategic intelligence.");
        setLoading(false);
      });
    } else {
      setData(null);
    }
  }, [isOpen, industry, navQuery]);

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <div className="gen-dashboard-overlay" onClick={onClose}>
        <motion.div 
          className="gen-dashboard-modal"
          onClick={(e) => e.stopPropagation()}
          initial={{ opacity: 0, scale: 0.95, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 20 }}
          transition={{ duration: 0.4, ease: "easeOut" }}
        >
          <div className="gen-dashboard-header">
            <div className="header-titles">
              <span className="ai-badge-large">Generative AI Synthesis</span>
              <h2>{industry} Sector Intelligence</h2>
            </div>
            <button className="close-btn" onClick={onClose} aria-label="Close modal"><X size={24} /></button>
          </div>
          
          <div className="gen-dashboard-content">
            {loading ? (
              <div className="loading-state">
                <motion.div 
                  animate={{ rotate: 360 }} 
                  transition={{ repeat: Infinity, duration: 2, ease: "linear" }}
                >
                  <Activity size={48} className="text-accent" />
                </motion.div>
                <h3>Synthesizing Global Risk Matrix...</h3>
                <p>Analyzing cross-border data for {industry}</p>
              </div>
            ) : error ? (
              <div className="error-state">
                <AlertTriangle size={48} className="text-warning" />
                <h3>{error}</h3>
                <button onClick={onClose} className="btn-primary">Return</button>
              </div>
            ) : data ? (
              <div className="dashboard-grid">
                
                {/* Executive Summary & Trends */}
                <div className="dashboard-section abstract-glass">
                  <div className="section-header">
                    <TrendingUp size={20} className="text-accent"/>
                    <h3>Executive Summary & Market Trend</h3>
                  </div>
                  <div className="section-body">
                    <p className="summary-text">{data.executive_summary}</p>
                    <div className="trend-box">
                      <strong>Dominant Trend: </strong> {data.market_trend}
                    </div>
                  </div>
                </div>

                {/* Risk Factors */}
                <div className="dashboard-section abstract-glass">
                  <div className="section-header">
                    <AlertTriangle size={20} className="text-warning"/>
                    <h3>Critical Risk Factors</h3>
                  </div>
                  <div className="section-body risk-factors-grid">
                    {data.risk_factors && data.risk_factors.map((risk, idx) => (
                      <motion.div 
                        key={idx} 
                        className={`risk-card severity-${risk.severity?.toLowerCase()}`}
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.1 * idx }}
                      >
                        <div className="risk-card-header">
                          <h4>{risk.area}</h4>
                          <span className="severity-badge">{risk.severity}</span>
                        </div>
                        <p>{risk.impact}</p>
                      </motion.div>
                    ))}
                  </div>
                </div>

                {/* Action Plan */}
                <div className="dashboard-section abstract-glass full-width">
                  <div className="section-header">
                    <CheckCircle size={20} className="text-success"/>
                    <h3>Strategic Action Plan</h3>
                  </div>
                  <div className="section-body action-plan-list">
                    {data.action_plan && data.action_plan.map((action, idx) => (
                      <motion.div 
                        key={idx} 
                        className="action-step"
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.2 + (0.1 * idx) }}
                      >
                        <div className="step-number">{action.step}</div>
                        <div className="step-content">
                          <h4>{action.title}</h4>
                          <p>{action.description}</p>
                        </div>
                      </motion.div>
                    ))}
                  </div>
                </div>
              </div>
            ) : null}
          </div>
          
          <div className="gen-dashboard-footer">
            <button className="btn-secondary" onClick={onClose}>Dismiss</button>
            <button className="btn-primary" disabled={loading}><Download size={16} /> Export Dossier</button>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
};

export default GenerativeDashboardModal;
