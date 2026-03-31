import React, { useState } from 'react';
import { UploadCloud, FileText, CheckCircle2, AlertTriangle, Layers, ArrowRight } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import './StrategicValueSimulator.css';

const StrategicValueSimulator = () => {
  const [isHovering, setIsHovering] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [resultsReady, setResultsReady] = useState(false);
  const [fileName, setFileName] = useState("Corporate_Annual_Report_2025.pdf");

  const handleDrop = (e) => {
    e.preventDefault();
    setIsHovering(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      setFileName(e.dataTransfer.files[0].name);
    }
    startAnalysis();
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      setFileName(e.target.files[0].name);
      startAnalysis();
    }
  };

  const startAnalysis = () => {
    setAnalyzing(true);
    // Simulate complex multi-agent analysis taking time
    setTimeout(() => {
      setAnalyzing(false);
      setResultsReady(true);
    }, 3000);
  };

  return (
    <section className="strategic-value-section">
      <div className="section-header">
        <h2>360° Value Strategy <span className="text-gradient">Simulator</span></h2>
        <p>Incorporate Annual Reports, Mergers & Acquisitions PDFs, or Sustainability Goals. Simulate enterprise-wide impacts across carbon, talent, and financial metrics.</p>
        <a href="#" className="download-sample-btn glass-panel">
          <FileText size={16} /> Download Sample Vision Brief
        </a>
      </div>

      <div className="analyzer-container">
        <AnimatePresence mode="wait">
          {!analyzing && !resultsReady && (
            <motion.div 
              key="dropzone"
              className={`dropzone glass-panel ${isHovering ? 'dropzone-hover' : ''}`}
              onDragOver={(e) => { e.preventDefault(); setIsHovering(true); }}
              onDragLeave={() => setIsHovering(false)}
              onDrop={handleDrop}
              onClick={() => document.getElementById('file-upload').click()}
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
            >
              <input 
                type="file" 
                id="file-upload" 
                style={{ display: 'none' }} 
                onChange={handleFileChange} 
                accept=".pdf,.docx,.xlsx,.png,.jpg,.jpeg" 
              />
              <div className="dropzone-content">
                <div className="upload-icon-wrapper animate-pulse-glow">
                  <UploadCloud size={40} className="text-accent" />
                </div>
                <h3>Drag & Drop Strategic Reports</h3>
                <p>Ingest corporate filings, briefs, or sustainability declarations.</p>
                <div className="supported-formats">
                  <span>PDF</span>
                  <span>DOCX</span>
                  <span>XLSX</span>
                  <span>VISION</span>
                </div>
              </div>
            </motion.div>
          )}

          {analyzing && (
            <motion.div 
              key="analyzing"
              className="analyzing-state glass-panel"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
            >
              <div className="scanner-line"></div>
              <Layers size={48} className="text-accent spinner-icon" />
              <h3>Multi-Agent Transformation Simulation Running...</h3>
              <p>Orchestrating ESG Metrics, Talent Benchmarks, and Value Realization checks.</p>
              
              <div className="progress-container">
                <div className="progress-bar">
                  <motion.div 
                    className="progress-fill" 
                    initial={{ width: "0%" }}
                    animate={{ width: "100%" }}
                    transition={{ duration: 3, ease: "linear" }}
                  />
                </div>
              </div>
              <ul className="loading-steps">
                 <li><CheckCircle2 size={12}/> Document geometry parsed</li>
                 <li className="active-step"><ActivityIcon size={12}/> Cross-referencing 360° Value Master File</li>
                 <li className="waiting-step">Synthesizing Executive Scorecard</li>
              </ul>
            </motion.div>
          )}

          {resultsReady && (
            <motion.div 
              key="results"
              className="results-dashboard glass-panel"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
            >
              <div className="dashboard-header">
                <div style={{ wordBreak: 'break-all', paddingRight: '20px' }}>
                  <h3>Simulation Complete: <span className="text-gradient">{fileName}</span></h3>
                  <p>Synthesized enterprise-wide impacts across the 360° Value metrics.</p>
                </div>
                <button className="reset-btn glass-panel" onClick={() => { setResultsReady(false); setFileName("Corporate_Annual_Report_2025.pdf"); }}>
                  Simulate Another
                </button>
              </div>

              <div className="dashboard-grid">
                <div className="stat-card risk-card">
                  <div className="stat-icon"><AlertTriangle size={24} color="#f59e0b" /></div>
                  <div className="stat-content">
                    <h4>ESG Value Gap Identified</h4>
                    <p>Scope 3 Carbon Tracking off trajectory by 12% in EMEA.</p>
                  </div>
                </div>
                
                <div className="stat-card safe-card">
                  <div className="stat-icon"><CheckCircle2 size={24} color="#4ade80" /></div>
                  <div className="stat-content">
                    <h4>Workforce Readiness Clear</h4>
                    <p>AI upskilling initiative trajectory tracking at 85% adoption.</p>
                  </div>
                </div>
                
                <div className="stat-card action-card">
                   <div className="stat-content">
                     <h4>Suggested Strategy</h4>
                     <p>Deploy Carbon Remediation Playbook</p>
                   </div>
                   <button className="generate-btn"><ArrowRight size={16} /></button>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </section>
  );
};

const ActivityIcon = ({size}) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="lucide lucide-activity text-accent"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>
);

export default StrategicValueSimulator;
