import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowRight, X, Loader2 } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import './ResearchInsights.css';

const reports = [
  { type: "RESEARCH REPORT", title: "OECD Pillar Two Implementation Guide", description: "Comprehensive analysis of GloBE rules and their impact on multinational tax structures." },
  { type: "PERSPECTIVE", title: "Digital Services Tax: Global Impact Assessment", description: "Evaluating the cascade effect of unilateral DSTs across 40+ jurisdictions." },
  { type: "RESEARCH REPORT", title: "Transfer Pricing in the AI Era", description: "How artificial intelligence is reshaping intercompany transaction documentation and analysis." },
  { type: "INSIGHT", title: "ESG Tax Incentives: A Global Overview", description: "Mapping green tax incentives and carbon pricing mechanisms across key economies." },
  { type: "RESEARCH REPORT", title: "Cross-Border M&A Tax Structuring", description: "Optimizing acquisition structures for tax efficiency in a post-BEPS landscape." },
  { type: "PERSPECTIVE", title: "Crypto Asset Taxation Framework", description: "Emerging regulatory approaches to digital asset classification and reporting." },
  { type: "RESEARCH REPORT", title: "Supply Chain Tax Optimization", description: "Strategic considerations for tariff mitigation and customs duty planning." },
  { type: "INSIGHT", title: "Global Minimum Tax: Country-by-Country", description: "Tracking Pillar Two adoption status and safe harbor provisions per jurisdiction." },
];

const ResearchInsights = () => {
  const [activeReport, setActiveReport] = useState(null);
  const [detail, setDetail] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const loadInsight = async (report) => {
    setActiveReport(report);
    setDetail('');
    setIsLoading(true);
    try {
      const response = await fetch('/pwc/api/insights/detail', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: report.title, type: report.type, description: report.description })
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
              try {
                const parsed = JSON.parse(dataStr);
                if (parsed.text) { fullText += parsed.text; setDetail(fullText); }
              } catch {}
            }
          }
        }
      }
    } catch (error) {
      setDetail("Unable to load insight. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  const closeDetail = () => {
    setActiveReport(null);
    setDetail('');
  };

  return (
    <section className="research-section">
      <div className="research-container">
        <div className="research-header">
          <h2>Latest Tax Insights</h2>
          <p className="research-subtitle">Expert analysis and perspectives on the issues shaping global tax policy. Click any insight for an AI-powered deep dive.</p>
        </div>
        <div className="research-grid">
          {reports.map((report, idx) => (
            <motion.div key={idx} className="research-card" initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ delay: idx * 0.08 }} whileHover={{ y: -8 }} onClick={() => loadInsight(report)}>
              <span className="card-type">{report.type}</span>
              <h3 className="card-title">{report.title}</h3>
              <p className="card-description">{report.description}</p>
              <span className="card-link">Read Insight <ArrowRight size={14} /></span>
            </motion.div>
          ))}
        </div>

        <AnimatePresence>
          {activeReport && (
            <motion.div className="insight-overlay" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} onClick={closeDetail}>
              <motion.div className="insight-modal" initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: 30 }} onClick={(e) => e.stopPropagation()}>
                <div className="insight-modal-header">
                  <div>
                    <span className="card-type">{activeReport.type}</span>
                    <h3>{activeReport.title}</h3>
                  </div>
                  <button className="insight-close" onClick={closeDetail}><X size={20} /></button>
                </div>
                <div className="insight-modal-body">
                  {isLoading && !detail && (
                    <div className="insight-loading"><Loader2 size={20} className="spin" /> Generating AI-powered analysis with Google Search...</div>
                  )}
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>{detail}</ReactMarkdown>
                </div>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </section>
  );
};

export default ResearchInsights;
