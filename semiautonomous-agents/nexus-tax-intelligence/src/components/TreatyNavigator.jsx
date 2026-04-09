import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Loader2, ArrowRight, Building, Globe, Shield, FileText } from 'lucide-react';
import './TreatyNavigator.css';

const countries = [
  "United States", "United Kingdom", "Germany", "France", "Ireland", "Netherlands",
  "Singapore", "Japan", "Australia", "Brazil", "India", "UAE", "Switzerland",
  "Luxembourg", "Hong Kong", "South Korea", "Canada", "Italy", "Spain",
  "Mexico", "South Africa", "China", "Saudi Arabia", "Sweden", "Norway",
  "Denmark", "Belgium", "Austria", "Poland", "Czech Republic", "Israel",
  "New Zealand", "Chile", "Colombia", "Thailand", "Vietnam", "Indonesia",
  "Malaysia", "Philippines", "Turkey"
];

const TreatyNavigator = () => {
  const [countryA, setCountryA] = useState('');
  const [countryB, setCountryB] = useState('');
  const [result, setResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const analyzeTreaty = async () => {
    setIsLoading(true);
    setResult(null);
    try {
      const response = await fetch('/pwc/api/treaty/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ country_a: countryA, country_b: countryB })
      });
      const data = await response.json();
      setResult(data);
    } catch (error) {
      setResult({ error: true });
    } finally {
      setIsLoading(false);
    }
  };

  const reset = () => {
    setResult(null);
    setCountryA('');
    setCountryB('');
  };

  const getStrengthClass = (score) => {
    if (score >= 7) return 'score-strong';
    if (score >= 4) return 'score-moderate';
    return 'score-weak';
  };

  const getBarColor = (score) => {
    if (score >= 7) return '#16a34a';
    if (score >= 4) return '#ea580c';
    return '#dc2626';
  };

  const getStrengthLabel = (score) => {
    if (score >= 8) return 'Comprehensive Protection';
    if (score >= 6) return 'Strong Protection';
    if (score >= 4) return 'Moderate Protection';
    if (score >= 2) return 'Limited Protection';
    return 'Minimal Protection';
  };

  return (
    <section className="treaty-section">
      <div className="treaty-container">
        <div className="treaty-header">
          <h2>Tax Treaty Navigator</h2>
          <p className="treaty-subtitle">AI-powered bilateral tax treaty analysis with Google Search grounding</p>
        </div>

        {!result && !isLoading && (
          <motion.div className="treaty-selector" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
            <div className="treaty-row">
              <select className="treaty-select" value={countryA} onChange={(e) => setCountryA(e.target.value)}>
                <option value="">Select country...</option>
                {countries.filter(c => c !== countryB).map(c => <option key={c} value={c}>{c}</option>)}
              </select>
              <span className="treaty-vs">⇄</span>
              <select className="treaty-select" value={countryB} onChange={(e) => setCountryB(e.target.value)}>
                <option value="">Select country...</option>
                {countries.filter(c => c !== countryA).map(c => <option key={c} value={c}>{c}</option>)}
              </select>
            </div>
            <button className="analyze-treaty-btn" onClick={analyzeTreaty} disabled={!countryA || !countryB}>
              Analyze Treaty <ArrowRight size={16} />
            </button>
          </motion.div>
        )}

        {isLoading && (
          <div className="treaty-loading">
            <Loader2 size={24} className="spin" />
            <span>Analyzing treaty between {countryA} and {countryB}...</span>
          </div>
        )}

        {result && !result.error && result.treaty_exists && (
          <motion.div className="treaty-result" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
            {/* Strength meter */}
            <div className="treaty-strength">
              <div className="strength-label">Treaty Protection Score</div>
              <div className="strength-meter">
                <div className={`strength-score ${getStrengthClass(result.overall_protection_score)}`}>
                  {result.overall_protection_score}
                </div>
                <div>
                  <div className="meter-bar-bg">
                    <div className="meter-bar-fill" style={{ width: `${result.overall_protection_score * 10}%`, background: getBarColor(result.overall_protection_score) }}></div>
                  </div>
                  <div className="strength-desc">{getStrengthLabel(result.overall_protection_score)}</div>
                </div>
              </div>
            </div>

            {/* Withholding rates table */}
            {result.withholding_rates && (
              <div className="treaty-table-card">
                <h3>Withholding Tax Rates</h3>
                <table className="treaty-table">
                  <thead>
                    <tr>
                      <th>Income Type</th>
                      <th>Treaty Rate</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr><td>Dividends (Portfolio)</td><td className="rate-cell">{result.withholding_rates.dividends_portfolio}</td></tr>
                    <tr><td>Dividends (Substantial Holding)</td><td className="rate-cell">{result.withholding_rates.dividends_substantial}</td></tr>
                    <tr><td>Interest</td><td className="rate-cell">{result.withholding_rates.interest}</td></tr>
                    <tr><td>Royalties</td><td className="rate-cell">{result.withholding_rates.royalties}</td></tr>
                  </tbody>
                </table>
              </div>
            )}

            {/* Info cards */}
            <div className="treaty-info-grid">
              <div className="treaty-info-card">
                <div className="info-card-icon"><Building size={18} /></div>
                <div className="info-card-title">PE Definition</div>
                <div className="info-card-text">{result.pe_definition}</div>
              </div>
              <div className="treaty-info-card">
                <div className="info-card-icon"><Shield size={18} /></div>
                <div className="info-card-title">Limitation on Benefits</div>
                <div className="info-card-text">{result.lob_provisions}</div>
              </div>
              <div className="treaty-info-card">
                <div className="info-card-icon"><Globe size={18} /></div>
                <div className="info-card-title">MLI Impact</div>
                <div className="info-card-text">{result.mli_impact}</div>
              </div>
              <div className="treaty-info-card">
                <div className="info-card-icon"><FileText size={18} /></div>
                <div className="info-card-title">Recent Amendments</div>
                <div className="info-card-text">{result.recent_amendments}</div>
              </div>
            </div>

            {/* Recommendations */}
            {result.strategic_recommendations && result.strategic_recommendations.length > 0 && (
              <div className="treaty-recs">
                <h3>Strategic Recommendations</h3>
                <ul className="rec-list">
                  {result.strategic_recommendations.map((rec, idx) => (
                    <li key={idx}><span className="rec-bullet">→</span> {rec}</li>
                  ))}
                </ul>
              </div>
            )}

            <div className="treaty-actions">
              <button className="new-treaty-btn" onClick={reset}>Analyze Another Treaty</button>
            </div>
          </motion.div>
        )}

        {result && !result.error && result.treaty_exists === false && (
          <div className="no-treaty">
            <h3>No Treaty Found</h3>
            <p>There is no bilateral tax treaty in force between {result.country_a} and {result.country_b}.</p>
            <div className="treaty-actions">
              <button className="new-treaty-btn" onClick={reset}>Try Different Countries</button>
            </div>
          </div>
        )}

        {result && result.error && (
          <div className="treaty-loading" style={{ color: '#E0301E' }}>
            Unable to analyze treaty. Please try again.
            <div className="treaty-actions" style={{ marginTop: 16 }}>
              <button className="new-treaty-btn" onClick={reset}>Try Again</button>
            </div>
          </div>
        )}
      </div>
    </section>
  );
};

export default TreatyNavigator;
