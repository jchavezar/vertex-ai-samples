import React, { useState, useEffect } from 'react';
import { X, Activity, Loader2 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import './GenerativeDashboardModal.css';

const GenerativeDashboardModal = ({ isOpen, onClose, industry, navQuery }) => {
  const [data, setData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (isOpen && industry) {
      setIsLoading(true);
      setData(null);
      fetch('/pwc/api/generate-dashboard', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ industry })
      })
        .then(res => res.json())
        .then(d => { setData(d); setIsLoading(false); })
        .catch(() => setIsLoading(false));
    }
  }, [isOpen, industry]);

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <motion.div className="dashboard-overlay" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} onClick={onClose}>
        <motion.div className="dashboard-modal" initial={{ scale: 0.95, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} onClick={(e) => e.stopPropagation()}>
          <div className="dashboard-header">
            <div>
              <h2 className="dashboard-title">{industry} Risk Dashboard</h2>
              {navQuery && <p className="dashboard-context">Context: {navQuery}</p>}
            </div>
            <button className="dashboard-close" onClick={onClose}><X size={20} /></button>
          </div>

          <div className="dashboard-body">
            {isLoading && (
              <div className="dashboard-loading">
                <Loader2 size={32} className="spin" />
                <p>Synthesizing Global Risk Matrix...</p>
              </div>
            )}

            {data && !isLoading && (
              <>
                <motion.div className="summary-card" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
                  <h3 className="summary-title">Executive Summary</h3>
                  <p>{data.executive_summary}</p>
                  {data.market_trend && <p className="summary-trend">{data.market_trend}</p>}
                </motion.div>

                {data.risk_factors && (
                  <>
                    <h3 className="section-label">Critical Risk Factors</h3>
                    <div className="risks-grid">
                      {data.risk_factors.map((risk, idx) => (
                        <motion.div key={idx} className="risk-card" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: idx * 0.1 }}>
                          <div className="risk-card-header">
                            <span className="risk-area">{risk.area}</span>
                            <span className={`severity-badge severity-${risk.severity?.toLowerCase()}`}>{risk.severity}</span>
                          </div>
                          <p>{risk.impact}</p>
                        </motion.div>
                      ))}
                    </div>
                  </>
                )}

                {data.action_plan && (
                  <>
                    <h3 className="section-label">Strategic Action Plan</h3>
                    <div className="action-steps">
                      {data.action_plan.map((action, idx) => (
                        <motion.div key={idx} className="action-step" initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: idx * 0.1 }}>
                          <div className="step-number">{action.step}</div>
                          <div><h4>{action.title}</h4><p>{action.description}</p></div>
                        </motion.div>
                      ))}
                    </div>
                  </>
                )}
              </>
            )}
          </div>

          <div className="dashboard-footer">
            <button className="dismiss-btn" onClick={onClose}>Dismiss</button>
            <button className="export-btn">Export Dossier</button>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default GenerativeDashboardModal;
