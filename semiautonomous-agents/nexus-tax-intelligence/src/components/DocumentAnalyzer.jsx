import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Upload, CheckCircle, Loader2, Clock, AlertTriangle, ShieldCheck, ArrowRight, FlaskConical } from 'lucide-react';
import './DocumentAnalyzer.css';

const DocumentAnalyzer = ({ onOpenAudit }) => {
  const [state, setState] = useState('dropzone'); // dropzone | analyzing | results
  const [dragOver, setDragOver] = useState(false);
  const [progress, setProgress] = useState(0);
  const [activeStep, setActiveStep] = useState(0);

  const steps = [
    "Document geometry parsed",
    "Cross-referencing Master File",
    "Synthesizing compliance matrix"
  ];

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    startAnalysis();
  };

  const startAnalysis = () => {
    setState('analyzing');
    setProgress(0);
    setActiveStep(0);
    const interval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 100) { clearInterval(interval); setState('results'); return 100; }
        const next = prev + 2;
        if (next > 33) setActiveStep(1);
        if (next > 66) setActiveStep(2);
        return next;
      });
    }, 80);
  };

  return (
    <section className="analyzer-section">
      <div className="analyzer-container">
        <div className="analyzer-header">
          <h2>Connected Compliance Analyzer</h2>
          <p className="analyzer-subtitle">Upload corporate tax documents for AI-powered compliance analysis and risk detection.</p>
        </div>

        {state === 'dropzone' && (
          <motion.div className={`dropzone ${dragOver ? 'drag-over' : ''}`} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} onDragOver={(e) => { e.preventDefault(); setDragOver(true); }} onDragLeave={() => setDragOver(false)} onDrop={handleDrop} onClick={startAnalysis}>
            <Upload size={48} className="dropzone-icon" />
            <p className="dropzone-text">Drag & Drop Tax Documents</p>
            <p className="dropzone-formats">Supports PDF, DOCX, XLSX, PNG, JPG</p>
            <button className="upload-btn" onClick={(e) => { e.stopPropagation(); startAnalysis(); }}>Select Files</button>
          </motion.div>
        )}

        {state === 'analyzing' && (
          <motion.div className="analyzing-container" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
            <div className="analyzing-file">
              <span className="file-name">LATAM_Agreement_V4.pdf</span>
              <span className="file-size">2.4 MB</span>
            </div>
            <div className="progress-bar">
              <div className="progress-fill" style={{ width: `${progress}%` }}></div>
            </div>
            <div className="analysis-steps">
              {steps.map((step, idx) => (
                <div key={idx} className="analysis-step">
                  {idx < activeStep ? <CheckCircle size={18} className="step-check" /> : idx === activeStep ? <Loader2 size={18} className="step-spinner" /> : <Clock size={18} className="step-pending" />}
                  <span className={idx <= activeStep ? 'step-active' : 'step-inactive'}>{step}</span>
                </div>
              ))}
            </div>
          </motion.div>
        )}

        {state === 'results' && (
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
            <div className="results-grid">
              <div className="result-card risk">
                <AlertTriangle size={24} className="card-icon risk-icon" />
                <h4>Compliance Risk Detected</h4>
                <p>Brazil local markup requirement unmet. Transfer pricing documentation missing Section 4 addendum for LATAM intercompany transactions.</p>
                <span className="severity-tag risk-tag">High Risk</span>
              </div>
              <div className="result-card safe">
                <ShieldCheck size={24} className="card-icon safe-icon" />
                <h4>Arm's Length Confirmed</h4>
                <p>APAC region intercompany pricing validated against comparable uncontrolled transactions. No adjustment required.</p>
                <span className="severity-tag safe-tag">Compliant</span>
              </div>
              <div className="result-card action">
                <ArrowRight size={24} className="card-icon action-icon" />
                <h4>Suggested Action</h4>
                <p>Generate Section 4 Addendum to address Brazil markup requirements. Deploy Carbon Remediation Playbook for ESG compliance gap.</p>
                <span className="severity-tag action-tag">Action Required</span>
              </div>
            </div>
            <div className="results-actions">
              <button className="reset-btn" onClick={() => setState('dropzone')}>Simulate Another</button>
              {onOpenAudit && <button className="audit-btn" onClick={onOpenAudit}><FlaskConical size={16} /> Launch Audit Simulation</button>}
            </div>
          </motion.div>
        )}
      </div>
    </section>
  );
};

export default DocumentAnalyzer;
