import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { ShieldCheck, Cpu } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import './HeroRadar.css';

const HeroRadar = () => {
  const [insight, setInsight] = useState('');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchInsight = async () => {
      try {
        const response = await fetch('/pwc/api/radar/insight');
        const reader = response.body.getReader();
        const decoder = new TextDecoder('utf-8');
        let buffer = '';
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
                  if (parsed.text) setInsight(prev => prev + parsed.text);
                } catch (err) { /* skip */ }
              }
            }
          }
        }
      } catch (error) {
        console.error("Failed to fetch radar insight:", error);
        setInsight("**Global minimum tax** reforms continue to reshape multinational compliance landscapes across OECD jurisdictions.");
      } finally {
        setIsLoading(false);
      }
    };
    fetchInsight();
  }, []);

  const scrollToGemini = () => {
    const el = document.querySelector('.gemini-section');
    if (el) el.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <section className="hero-section">
      <div className="hero-container">
        <motion.div className="hero-text" initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.8 }}>
          <h1 className="hero-headline">
            Global Tax Intelligence.{' '}
            <span className="hero-accent">Powered by Gemini AI.</span>
          </h1>
          <p className="hero-subtitle">
            Next-generation tax intelligence combining real-time regulatory monitoring, multi-agent analysis, and enterprise-grade AI to transform how organizations navigate global tax complexity.
          </p>
          <button className="hero-cta" onClick={scrollToGemini}>Analyze Global Compliance</button>
          <div className="trust-badges">
            <span className="trust-badge"><ShieldCheck size={14} /> SOC2 Compliant</span>
            <span className="trust-badge"><Cpu size={14} /> Vertex AI Secured</span>
          </div>
        </motion.div>

        <motion.div className="hero-radar" initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} transition={{ duration: 1, delay: 0.3 }}>
          <div className="globe-container">
            <svg viewBox="0 0 400 400" className="globe-canvas">
              <defs>
                <radialGradient id="globeGlow" cx="50%" cy="50%" r="50%">
                  <stop offset="0%" stopColor="#D04A02" stopOpacity="0.06" />
                  <stop offset="70%" stopColor="#D04A02" stopOpacity="0.02" />
                  <stop offset="100%" stopColor="#D04A02" stopOpacity="0" />
                </radialGradient>
              </defs>

              {/* Ambient glow */}
              <circle cx="200" cy="200" r="185" className="globe-glow" />

              {/* Globe outline */}
              <circle cx="200" cy="200" r="150" className="globe-outline" />

              {/* Wireframe meridians (rotating) */}
              <g className="globe-spin">
                <ellipse cx="200" cy="200" rx="150" ry="150" className="globe-meridian" />
                <ellipse cx="200" cy="200" rx="100" ry="150" className="globe-meridian" />
                <ellipse cx="200" cy="200" rx="40" ry="150" className="globe-meridian" />
                <ellipse cx="200" cy="200" rx="130" ry="150" className="globe-meridian" style={{transform: 'rotate(60deg)', transformOrigin: '200px 200px'}} />
                <ellipse cx="200" cy="200" rx="80" ry="150" className="globe-meridian" style={{transform: 'rotate(60deg)', transformOrigin: '200px 200px'}} />
              </g>

              {/* Parallels */}
              <ellipse cx="200" cy="130" rx="120" ry="22" className="globe-parallel" />
              <ellipse cx="200" cy="200" rx="150" ry="28" className="globe-equator" />
              <ellipse cx="200" cy="270" rx="120" ry="22" className="globe-parallel" />
              <ellipse cx="200" cy="100" rx="80" ry="14" className="globe-parallel" />
              <ellipse cx="200" cy="300" rx="80" ry="14" className="globe-parallel" />

              {/* Orbit rings for satellites */}
              <circle cx="200" cy="200" r="170" className="orbit-ring" />
              <circle cx="200" cy="200" r="185" className="orbit-ring" style={{opacity: 0.3}} />

              {/* Orbiting satellites */}
              <g className="orbit-path-1"><circle cx="200" cy="30" r="4" className="orbit-sat" /></g>
              <g className="orbit-path-2"><circle cx="370" cy="200" r="3" className="orbit-sat" style={{fill: '#FD5108'}} /></g>
              <g className="orbit-path-3"><circle cx="200" cy="385" r="3.5" className="orbit-sat" style={{fill: '#D93954'}} /></g>

              {/* Data nodes on globe surface (counter-rotating so they stay visible) */}
              <g className="globe-spin-reverse">
                <circle cx="145" cy="120" r="4" fill="#D04A02" className="globe-node" />
                <circle cx="145" cy="120" r="4" className="node-pulse" />
                <circle cx="260" cy="140" r="4" fill="#FD5108" className="globe-node" />
                <circle cx="260" cy="140" r="4" className="node-pulse" />
                <circle cx="170" cy="240" r="4" fill="#D04A02" className="globe-node" />
                <circle cx="170" cy="240" r="4" className="node-pulse" />
                <circle cx="280" cy="220" r="4" fill="#D93954" className="globe-node" />
                <circle cx="280" cy="220" r="4" className="node-pulse" />
                <circle cx="220" cy="100" r="3" fill="#FD5108" className="globe-node" />
                <circle cx="220" cy="100" r="3" className="node-pulse" />
                <circle cx="130" cy="190" r="3" fill="#D04A02" className="globe-node" />
                <circle cx="130" cy="190" r="3" className="node-pulse" />

                {/* Connection arcs between nodes */}
                <path d="M145,120 Q200,80 260,140" className="globe-arc" />
                <path d="M260,140 Q310,200 280,220" className="globe-arc" />
                <path d="M170,240 Q140,180 145,120" className="globe-arc" />
              </g>

              {/* Floating jurisdiction labels */}
              <text x="108" y="112" className="globe-label">EMEA</text>
              <text x="270" y="135" className="globe-label">APAC</text>
              <text x="152" y="258" className="globe-label">LATAM</text>
              <text x="288" y="232" className="globe-label">NAM</text>

              {/* Center logo */}
              <circle cx="200" cy="200" r="22" className="globe-center-bg" />
              <text x="200" y="207" textAnchor="middle" className="globe-logo">N</text>
            </svg>
          </div>

          <motion.div className="insight-card" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 1.2 }}>
            <div className="insight-label">Live Strategic Insight</div>
            <div className="insight-content">
              {isLoading && !insight ? (
                <div className="insight-loading">Scanning global tax landscape...</div>
              ) : (
                <ReactMarkdown>{insight}</ReactMarkdown>
              )}
            </div>
          </motion.div>
        </motion.div>
      </div>
    </section>
  );
};

export default HeroRadar;
