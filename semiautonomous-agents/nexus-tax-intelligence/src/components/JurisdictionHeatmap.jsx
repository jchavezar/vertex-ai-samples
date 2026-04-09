import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Loader2 } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import './JurisdictionHeatmap.css';

const categories = ["Transfer Pricing", "Digital Tax", "PE Risk", "Withholding Tax"];

const riskData = {
  "Transfer Pricing": { US: 3, UK: 2, DE: 3, FR: 3, IE: 2, NL: 2, SG: 1, JP: 3, AU: 3, BR: 5, IN: 4, AE: 1, CH: 2, LU: 2, HK: 1, KR: 3, CA: 2, IT: 3, ES: 3, MX: 4, ZA: 3, CN: 4, SA: 2 },
  "Digital Tax": { US: 2, UK: 4, DE: 3, FR: 5, IE: 2, NL: 3, SG: 2, JP: 3, AU: 4, BR: 3, IN: 5, AE: 1, CH: 2, LU: 2, HK: 1, KR: 4, CA: 4, IT: 4, ES: 4, MX: 3, ZA: 2, CN: 4, SA: 3 },
  "PE Risk": { US: 2, UK: 3, DE: 4, FR: 3, IE: 2, NL: 2, SG: 1, JP: 3, AU: 3, BR: 4, IN: 5, AE: 1, CH: 2, LU: 1, HK: 1, KR: 3, CA: 3, IT: 4, ES: 3, MX: 3, ZA: 3, CN: 5, SA: 2 },
  "Withholding Tax": { US: 2, UK: 2, DE: 3, FR: 3, IE: 1, NL: 2, SG: 1, JP: 4, AU: 2, BR: 5, IN: 4, AE: 0, CH: 3, LU: 2, HK: 0, KR: 3, CA: 3, IT: 4, ES: 3, MX: 4, ZA: 3, CN: 3, SA: 2 },
};

const countryNames = { US: "United States", UK: "United Kingdom", DE: "Germany", FR: "France", IE: "Ireland", NL: "Netherlands", SG: "Singapore", JP: "Japan", AU: "Australia", BR: "Brazil", IN: "India", AE: "UAE", CH: "Switzerland", LU: "Luxembourg", HK: "Hong Kong", KR: "South Korea", CA: "Canada", IT: "Italy", ES: "Spain", MX: "Mexico", ZA: "South Africa", CN: "China", SA: "Saudi Arabia" };

const riskColors = ['#F5F7F8', '#FFE8D6', '#FFCC99', '#FD5108', '#C52B09', '#E0301E'];
const riskLabels = ['No Data', 'Low', 'Moderate', 'Elevated', 'High', 'Critical'];

// Simplified map regions (x, y, width, height)
const regions = [
  { code: 'CA', x: 80, y: 60, w: 70, h: 45 }, { code: 'US', x: 90, y: 110, w: 65, h: 40 }, { code: 'MX', x: 95, y: 155, w: 40, h: 30 },
  { code: 'BR', x: 195, y: 190, w: 55, h: 55 }, { code: 'UK', x: 350, y: 65, w: 25, h: 25 }, { code: 'IE', x: 330, y: 70, w: 18, h: 20 },
  { code: 'FR', x: 360, y: 100, w: 30, h: 30 }, { code: 'ES', x: 345, y: 130, w: 30, h: 25 }, { code: 'NL', x: 378, y: 72, w: 18, h: 18 },
  { code: 'DE', x: 390, y: 78, w: 30, h: 30 }, { code: 'IT', x: 395, y: 115, w: 22, h: 35 }, { code: 'CH', x: 385, y: 105, w: 18, h: 15 },
  { code: 'LU', x: 377, y: 90, w: 12, h: 12 }, { code: 'ZA', x: 440, y: 280, w: 40, h: 35 },
  { code: 'SA', x: 510, y: 150, w: 40, h: 40 }, { code: 'AE', x: 540, y: 170, w: 25, h: 20 },
  { code: 'IN', x: 610, y: 140, w: 45, h: 50 }, { code: 'CN', x: 670, y: 90, w: 65, h: 55 }, { code: 'JP', x: 750, y: 100, w: 25, h: 35 },
  { code: 'KR', x: 730, y: 110, w: 18, h: 22 }, { code: 'HK', x: 720, y: 150, w: 15, h: 15 }, { code: 'SG', x: 680, y: 210, w: 15, h: 15 },
  { code: 'AU', x: 730, y: 260, w: 65, h: 50 },
];

const JurisdictionHeatmap = () => {
  const [activeCategory, setActiveCategory] = useState("Transfer Pricing");
  const [selectedCountry, setSelectedCountry] = useState(null);
  const [briefing, setBriefing] = useState('');
  const [isBriefingLoading, setIsBriefingLoading] = useState(false);

  const getRiskLevel = (code) => riskData[activeCategory]?.[code] || 0;

  const handleCountryClick = async (code) => {
    setSelectedCountry(code);
    setBriefing('');
    setIsBriefingLoading(true);
    try {
      const response = await fetch('/pwc/api/heatmap/risk-brief', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ country: countryNames[code], risk_category: activeCategory })
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
              try { const parsed = JSON.parse(dataStr); if (parsed.text) { fullText += parsed.text; setBriefing(fullText); } } catch {}
            }
          }
        }
      }
    } catch (error) {
      setBriefing("Unable to generate risk briefing. Please try again.");
    } finally {
      setIsBriefingLoading(false);
    }
  };

  return (
    <section className="heatmap-section">
      <div className="heatmap-container">
        <div className="heatmap-header">
          <h2>Cross-Jurisdictional Tax Risk Heatmap</h2>
          <p className="heatmap-subtitle">Click any jurisdiction for an AI-powered risk briefing.</p>
        </div>

        <div className="filter-controls">
          {categories.map(cat => (
            <button key={cat} className={`filter-btn ${activeCategory === cat ? 'active' : ''}`} onClick={() => setActiveCategory(cat)}>{cat}</button>
          ))}
        </div>

        <div className="map-wrapper">
          <svg viewBox="0 0 850 360" className="world-map">
            {regions.map(({ code, x, y, w, h }) => {
              const level = getRiskLevel(code);
              return (
                <g key={code} onClick={() => handleCountryClick(code)} className="country-group">
                  <rect x={x} y={y} width={w} height={h} rx={3} fill={riskColors[level]} stroke="#fff" strokeWidth={1} className={`country-path ${level >= 4 ? 'country-pulse' : ''} ${selectedCountry === code ? 'country-selected' : ''}`} />
                  <text x={x + w / 2} y={y + h / 2 + 4} textAnchor="middle" className="country-label" fontSize={w < 20 ? 7 : 9}>{code}</text>
                </g>
              );
            })}
          </svg>

          <div className="color-legend">
            {riskLabels.map((label, idx) => (
              <div key={idx} className="legend-item">
                <div className="legend-swatch" style={{ background: riskColors[idx] }}></div>
                <span>{label}</span>
              </div>
            ))}
          </div>
        </div>

        <AnimatePresence>
          {selectedCountry && (
            <motion.div className="risk-panel" initial={{ opacity: 0, x: 30 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: 30 }}>
              <div className="risk-panel-header">
                <div>
                  <h3>{countryNames[selectedCountry]}</h3>
                  <span className={`risk-level-badge risk-level-${getRiskLevel(selectedCountry) >= 4 ? 'high' : getRiskLevel(selectedCountry) >= 3 ? 'medium' : 'low'}`}>
                    {riskLabels[getRiskLevel(selectedCountry)]} Risk
                  </span>
                </div>
                <button className="panel-close" onClick={() => setSelectedCountry(null)}><X size={18} /></button>
              </div>
              <div className="risk-category-tag">{activeCategory}</div>
              <div className="risk-briefing">
                {isBriefingLoading && !briefing && <div className="briefing-loading"><Loader2 size={18} className="spin" /> Generating risk briefing...</div>}
                <ReactMarkdown>{briefing}</ReactMarkdown>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </section>
  );
};

export default JurisdictionHeatmap;
