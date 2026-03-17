import React, { useState, useEffect } from 'react';
import { ShieldAlert, Globe, Activity, CheckCircle2 } from 'lucide-react';
import { motion } from 'framer-motion';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import './HeroRadar.css';

const HeroRadar = () => {
  const [insight, setInsight] = useState('');
  const [isStreaming, setIsStreaming] = useState(true);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const handleAnalyzeClick = () => {
    setIsAnalyzing(true);
    setTimeout(() => {
      setIsAnalyzing(false);
      document.getElementById('copilot-section')?.scrollIntoView({ behavior: 'smooth' });
      window.dispatchEvent(new CustomEvent('triggerCopilot', { detail: 'Analyze Global Compliance' }));
    }, 2000);
  };

  useEffect(() => {
    let unmounted = false;

    const fetchInsight = async () => {
      try {
        const response = await fetch('/api/radar/insight', {
          method: 'GET',
        });

        if (!response.body) throw new Error("ReadableStream not yet supported in this browser.");

        const reader = response.body.getReader();
        const decoder = new TextDecoder('utf-8');

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          if (unmounted) return;

          const chunk = decoder.decode(value, { stream: true });
          const lines = chunk.split('\n');

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const dataStr = line.replace('data: ', '').trim();
              if (dataStr === '[DONE]') {
                setIsStreaming(false);
                break;
              }
              if (dataStr) {
                try {
                  const parsed = JSON.parse(dataStr);
                  const newText = parsed.text || parsed.content;
                  if (newText) {
                    setInsight(prev => prev + newText);
                  }
                } catch (e) {
                  console.error("Error parsing SSE JSON:", e);
                }
              }
            }
          }
        }
      } catch (error) {
        console.error("Insight stream error:", error);
        if (!unmounted) {
          setInsight("No current alerts detected at this moment. Radar is monitoring.");
        }
      } finally {
        if (!unmounted) setIsStreaming(false);
      }
    };

    fetchInsight();

    return () => {
      unmounted = true;
    };
  }, []);

  return (
    <section className="hero-radar-container">
      <div className="hero-radar-content">
        <motion.div 
          className="hero-text"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
        >
          <div className="badge-enterprise">
            <ShieldAlert size={14} className="text-accent" />
            <span>Zero-Leak Security Active</span>
          </div>
          <h1>
            Thinking Beyond <span className="text-gradient">Borders.</span><br />
            Powered by <span className="text-gradient-ai">Gemini AI.</span>
          </h1>
          <p className="hero-subtitle">
            Anticipate short- and long-term consequences of global tax planning with real-time, 
            AI-driven policy analysis and dynamic risk assessment.
          </p>
          
          <div className="hero-actions">
            <button 
              className={`primary-btn ${isAnalyzing ? 'btn-analyzing' : ''}`}
              onClick={handleAnalyzeClick}
              disabled={isAnalyzing}
            >
              {isAnalyzing ? 'Initializing Core Scan...' : 'Analyze Global Compliance'} <Activity size={16} />
            </button>
            <div className="trust-indicators">
              <span><CheckCircle2 size={14} className="text-green-400" /> SOC2 Compliant</span>
              <span><CheckCircle2 size={14} className="text-green-400" /> Vertex AI Secured</span>
            </div>
          </div>
        </motion.div>

        <motion.div 
          className="hero-visual"
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 1, delay: 0.2 }}
        >
          {/* Abstract Radar/Globe Visualization */}
          <div className={`radar-abstract ${isAnalyzing ? 'radar-active-scan' : ''}`}>
            {isAnalyzing && <div className="radar-sweep-beam"></div>}
            
            <div className="radar-circle circle-1"></div>
            <div className="radar-circle circle-2"></div>
            <div className="radar-circle circle-3"></div>
            
            {/* Dynamic Orbiting Satellites */}
            <div className="orbit-path orbit-1">
              <div className="orbiting-node satellite-1"></div>
            </div>
            <div className="orbit-path orbit-2">
              <div className="orbiting-node satellite-2"></div>
            </div>
            <div className="orbit-path orbit-3">
              <div className="orbiting-node satellite-3"></div>
            </div>

            {/* Glowing nodes simulating stationary data points */}
            <div className="datapoint node-eu tooltip-trigger">
               <span className="ping animate-pulse-glow"></span>
               <span className="dot"></span>
               <div className="tooltip">Pillar Two Update Detected</div>
            </div>
            
            <div className="datapoint node-asia tooltip-trigger">
               <span className="ping animate-pulse-glow" style={{ animationDelay: '1s' }}></span>
               <span className="dot" style={{ background: '#0091DA' }}></span>
               <div className="tooltip">Transfer Pricing Shift</div>
            </div>
            
            <div className="datapoint node-na tooltip-trigger">
               <span className="ping animate-pulse-glow" style={{ animationDelay: '0.5s' }}></span>
               <span className="dot"></span>
            </div>
            
            <Globe className="center-globe animate-pulse-slow" size={120} strokeWidth={1} color="#00338D" />
          </div>
          
          <div className="glass-panel quick-insight absolute-insight">
            <div className="insight-header" style={{ marginBottom: '8px', borderBottom: '1px solid var(--border-light)', paddingBottom: '6px' }}>
              <Activity size={14} className="text-accent" />
              <span style={{ fontWeight: 600, color: 'var(--text-primary)' }}>Live Strategic Insight</span>
              {isStreaming && <span className="ping animate-pulse-glow" style={{ marginLeft: 'auto', display: 'inline-block', width: '8px', height: '8px', background: 'var(--accent-secondary)', borderRadius: '50%' }}></span>}
            </div>
            <div className="insight-body" style={{ maxHeight: '200px', overflowY: 'auto', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {insight || 'Scanning global tax policies...'}
              </ReactMarkdown>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
};

export default HeroRadar;
