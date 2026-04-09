import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Loader2, Radar, X } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import './RegulatoryHorizon.css';

const RegulatoryHorizon = () => {
  const [items, setItems] = useState([]);
  const [isScanning, setIsScanning] = useState(false);
  const [selectedItem, setSelectedItem] = useState(null);
  const [detail, setDetail] = useState('');
  const [isDetailLoading, setIsDetailLoading] = useState(false);
  const [hasScanned, setHasScanned] = useState(false);

  const runScan = async () => {
    setIsScanning(true);
    setItems([]);
    setSelectedItem(null);
    setDetail('');
    try {
      const response = await fetch('/pwc/api/horizon/scan');
      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let buffer = '';
      const collected = [];
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
                if (parsed.item) {
                  collected.push(parsed.item);
                  setItems([...collected]);
                }
              } catch {}
            }
          }
        }
      }
      setHasScanned(true);
    } catch (error) {
      setItems([]);
      setHasScanned(true);
    } finally {
      setIsScanning(false);
    }
  };

  const loadDetail = async (item) => {
    setSelectedItem(item);
    setDetail('');
    setIsDetailLoading(true);
    try {
      const response = await fetch('/pwc/api/horizon/detail', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: item.title, jurisdiction: item.jurisdiction })
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
      setDetail("Unable to load regulatory detail. Please try again.");
    } finally {
      setIsDetailLoading(false);
    }
  };

  const getImpactClass = (level) => {
    const l = (level || '').toLowerCase();
    if (l === 'high') return 'high';
    if (l === 'medium') return 'medium';
    return 'low';
  };

  return (
    <section className="horizon-section">
      <div className="horizon-container">
        <div className="horizon-header">
          <h2>Regulatory Horizon Scanner</h2>
          <p className="horizon-subtitle">AI-powered scan of upcoming global tax legislation using Google Search grounding</p>
        </div>

        <button className="scan-btn" onClick={runScan} disabled={isScanning}>
          {isScanning ? <><Loader2 size={18} className="spin" /> Scanning...</> : <><Radar size={18} /> Scan Regulatory Horizon</>}
        </button>

        {isScanning && (
          <div className="horizon-loading">
            <Loader2 size={24} className="spin" />
            <span>Scanning global regulatory landscape...</span>
          </div>
        )}

        {items.length > 0 && (
          <div className="horizon-timeline">
            <div className="timeline-line"></div>
            <div className="timeline-cards">
              {items.map((item, idx) => (
                <motion.div
                  key={idx}
                  className="horizon-card"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: idx * 0.08 }}
                  onClick={() => loadDetail(item)}
                >
                  <div className={`card-impact-bar impact-${getImpactClass(item.impact_level)}`}></div>
                  <div className="horizon-card-body">
                    <div className="card-jurisdiction">{item.jurisdiction}</div>
                    <div className="card-title">{item.title}</div>
                    <div className="card-date">{item.expected_effective_date}</div>
                    <div className="card-summary">{item.summary}</div>
                    <span className={`impact-badge badge-${getImpactClass(item.impact_level)}`}>
                      {item.impact_level} Impact
                    </span>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        )}

        {hasScanned && !isScanning && items.length === 0 && (
          <div className="horizon-empty">
            <Radar size={40} />
            <p>No regulatory items found. Try scanning again.</p>
          </div>
        )}

        <AnimatePresence>
          {selectedItem && (
            <motion.div className="horizon-detail" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: 20 }}>
              <div className="detail-header">
                <div>
                  <h3>{selectedItem.title}</h3>
                  <div className="detail-jurisdiction">{selectedItem.jurisdiction} — {selectedItem.expected_effective_date}</div>
                </div>
                <button className="detail-close" onClick={() => setSelectedItem(null)}><X size={18} /></button>
              </div>
              <div className="detail-content">
                {isDetailLoading && !detail && <div className="detail-loading"><Loader2 size={16} className="spin" /> Analyzing regulation...</div>}
                <ReactMarkdown>{detail}</ReactMarkdown>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </section>
  );
};

export default RegulatoryHorizon;
