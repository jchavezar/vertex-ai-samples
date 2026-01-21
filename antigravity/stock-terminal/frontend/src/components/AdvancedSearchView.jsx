import React, { useState, useEffect, useRef } from 'react';
import { Search, Sparkles, Globe, Calendar, ExternalLink, Image as ImageIcon, Loader2, ArrowRight } from 'lucide-react';

const AdvancedSearchView = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [totalSize, setTotalSize] = useState(0);
  const [nextToken, setNextToken] = useState(null);
  const [summary, setSummary] = useState(null);
  const debounceTimer = useRef(null);

  const handleSearch = async (e) => {
    if (e) e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:8001/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: query, pageSize: 12 })
      });

      if (!response.ok) throw new Error('Search failed');
      const data = await response.json();
      const resultsList = data.results || [];

      setResults(resultsList);
      setTotalSize(data.totalSize || 0);
      setNextToken(data.nextPageToken || null);

      // PARALLEL: Trigger AI Summary if we have results
      if (resultsList.length > 0) {
        generateSummary(query, resultsList);
      } else {
        setSummary(null);
      }

    } catch (err) {
      console.error(err);
      setError('Failed to fetch search results. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const generateSummary = async (searchQuery, resultsList) => {
    setSummary({ summaryText: '', loading: true });

    try {
      // Extract top 5 snippets for context
      const topContexts = resultsList.slice(0, 5).map(res => {
        const doc = res.document.derivedStructData;
        return doc.htmlSnippet || doc.snippet || doc.title;
      }).filter(Boolean);

      const response = await fetch('http://localhost:8001/search/generative-overview', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: searchQuery, contexts: topContexts })
      });

      if (!response.ok) return;

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let accumulatedText = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (!line.trim()) continue;
          try {
            const data = JSON.parse(line);
            if (data.text) {
              accumulatedText += data.text;
              // Minimal HTML sanitization/formatting could go here
              // For now just raw text or basic markdown conversion
              setSummary(prev => ({ ...prev, summaryText: accumulatedText, loading: false }));
            }
          } catch (e) {
            console.warn("Stream parse error", e);
          }
        }
      }
    } catch (err) {
      console.error("Summary generation failed", err);
      // Silently fail for summary interaction
      setSummary(null);
    }
  };

  // Debounced Live Search
  useEffect(() => {
    if (debounceTimer.current) clearTimeout(debounceTimer.current);

    if (query.length > 2) {
      debounceTimer.current = setTimeout(() => {
        handleSearch();
      }, 600); // 600ms debounce
    } else if (query.length === 0) {
      setResults([]);
      setSummary(null);
    }

    return () => {
      if (debounceTimer.current) clearTimeout(debounceTimer.current);
    };
  }, [query]);

  return (
    <div className="advanced-search-container fade-in">
      <div className="search-hero">
        <div className="hero-content">
          <div className="brand-badge">
            <Sparkles size={14} />
            <span>AI POWERED SEARCH</span>
          </div>
          <h1>Discover Financial Intelligence</h1>
          <p>Guided, next-generation search across the FactSet knowledge base.</p>

          <form onSubmit={handleSearch} className="hero-search-wrapper">
            <div className={`search-input-box ${loading ? 'loading' : ''}`}>
              <Search className="search-icon" size={20} />
              <input
                type="text"
                placeholder="Search earnings, reports, filings..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                autoFocus
              />
              <button type="submit" disabled={loading || !query.trim()}>
                {loading ? <Loader2 className="animate-spin" size={20} /> : <ArrowRight size={20} />}
              </button>
            </div>
          </form>

          <div className="search-suggestions">
            <span>Try:</span>
            <button onClick={() => { setQuery('latest earnings Apple'); handleSearch(); }}>Apple Earnings</button>
            <button onClick={() => { setQuery('TSLA valuation analysis'); handleSearch(); }}>Tesla Valuation</button>
            <button onClick={() => { setQuery('NVIDIA AI outlook 2025'); handleSearch(); }}>NVIDIA Outlook</button>
          </div>
        </div>
      </div>

      <div className="search-results-viewport">
        {loading && !results.length && (
          <div className="results-loading">
            {[1, 2, 3, 4, 5, 6].map(i => (
              <div key={i} className="skeleton-card shimmer-bg" />
            ))}
          </div>
        )}

        {error && <div className="search-error">{error}</div>}

        {(summary?.loading || summary?.summaryText) && (
          <div className="summary-overview ai-glow fade-in">
            <div className="summary-header">
              <Sparkles size={16} className={summary.loading ? "animate-pulse" : ""} />
              <span>AI OVERVIEW (BETA)</span>
              {summary.loading && <span style={{ marginLeft: 'auto', fontSize: '10px', color: 'var(--text-muted)' }}>Generating insights...</span>}
            </div>
            {summary.summaryText ? (
              <div className="summary-content" style={{ whiteSpace: 'pre-wrap' }}>{summary.summaryText}</div>
            ) : (
              <div className="shimmer-bg" style={{ height: '60px', borderRadius: '8px', opacity: 0.5 }} />
            )}
          </div>
        )}

        {!loading && results.length > 0 && (
          <>
            <div className="results-meta">
              <span>Found {totalSize} structured documents</span>
            </div>

            <div className="results-grid">
              {results.map((res, idx) => {
                const doc = res.document.derivedStructData;
                const thumbnail = doc.pagemap?.cse_thumbnail?.[0]?.src;
                const snippet = doc.htmlSnippet || (doc.snippets?.[0]?.htmlSnippet);
                const domain = doc.displayLink || (doc.link ? new URL(doc.link).hostname : 'factset.com');

                return (
                  <a
                    key={idx}
                    href={doc.link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="search-result-card"
                  >
                    <div className="card-top">
                      {thumbnail ? (
                        <div className="card-thumb">
                          <img src={thumbnail} alt="" />
                        </div>
                      ) : (
                        <div className="card-thumb-placeholder">
                          <Globe size={24} />
                        </div>
                      )}
                      <div className="card-header-info">
                        <div className="card-domain">{domain}</div>
                        <h3 dangerouslySetInnerHTML={{ __html: doc.title }} />
                      </div>
                    </div>

                    {snippet && (
                      <div
                        className="card-snippet"
                        dangerouslySetInnerHTML={{ __html: snippet }}
                      />
                    )}

                    <div className="card-footer">
                      <div className="footer-tag">
                        <Calendar size={12} />
                        <span>Document</span>
                      </div>
                      <ExternalLink size={14} className="ext-icon" />
                    </div>
                  </a>
                );
              })}
            </div>
          </>
        )}

        {!loading && !results.length && query && !error && (
          <div className="no-results">
            <Search size={48} />
            <h2>No results found</h2>
            <p>Try broadening your search terms or checking for typos.</p>
          </div>
        )}

        {nextToken && (
          <div className="load-more-container">
            <button className="load-more-btn" onClick={() => {/* Future implementation */ }}>
              View More Results
            </button>
          </div>
        )}
      </div>

      <style jsx="true">{`
        .advanced-search-container {
          padding-bottom: 80px;
        }
        .search-hero {
          padding: 60px 20px;
          text-align: center;
          background: radial-gradient(circle at center, var(--brand-light) 0%, transparent 70%);
          margin-bottom: 20px;
        }
        .hero-content {
          max-width: 800px;
          margin: 0 auto;
        }
        .brand-badge {
          display: inline-flex;
          align-items: center;
          gap: 6px;
          background: var(--brand-light);
          color: var(--brand);
          padding: 4px 12px;
          border-radius: 999px;
          font-size: 10px;
          font-weight: 800;
          letter-spacing: 1px;
          margin-bottom: 20px;
          border: 1px solid var(--brand-light);
        }
        h1 {
          font-size: 42px;
          font-weight: 800;
          letter-spacing: -1px;
          margin-bottom: 12px;
          background: linear-gradient(135deg, var(--text-primary) 0%, var(--brand) 100%);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
        }
        .hero-content p {
          color: var(--text-secondary);
          font-size: 16px;
          margin-bottom: 40px;
        }
        .hero-search-wrapper {
          position: relative;
          max-width: 600px;
          margin: 0 auto 24px;
        }
        .search-input-box {
          display: flex;
          align-items: center;
          background: var(--bg-card);
          padding: 6px 6px 6px 20px;
          border-radius: 999px;
          border: 1px solid var(--border);
          box-shadow: 0 10px 25px rgba(0,0,0,0.05);
          transition: all 0.3s ease;
        }
        .search-input-box:focus-within {
          border-color: var(--brand);
          box-shadow: 0 15px 35px rgba(0,75,135,0.1);
          transform: translateY(-2px);
        }
        .search-input-box input {
          flex: 1;
          border: none;
          background: transparent;
          padding: 12px;
          font-size: 16px;
          color: var(--text-primary);
          outline: none;
        }
        .search-input-box button {
          width: 48px;
          height: 48px;
          background: var(--brand-gradient);
          color: white;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
        }
        .search-input-box button:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }
        .search-suggestions {
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 12px;
          flex-wrap: wrap;
        }
        .search-suggestions span {
          font-size: 12px;
          color: var(--text-muted);
        }
        .search-suggestions button {
          font-size: 12px;
          color: var(--text-secondary);
          padding: 4px 12px;
          border: 1px solid var(--border);
          border-radius: 999px;
        }
        .search-suggestions button:hover {
          background: var(--border-light);
          color: var(--brand);
        }
        
        .search-results-viewport {
          max-width: 1200px;
          margin: 0 auto;
          padding: 0 20px;
        }
        .results-meta {
          margin-bottom: 24px;
          font-size: 12px;
          color: var(--text-muted);
          font-weight: 600;
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }
        .results-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
          gap: 20px;
        }
        .search-result-card {
          background: var(--bg-card);
          border: 1px solid var(--border);
          border-radius: 16px;
          padding: 20px;
          text-decoration: none;
          display: flex;
          flex-direction: column;
          gap: 16px;
          transition: all 0.25s ease;
          position: relative;
        }
        .search-result-card:hover {
          transform: translateY(-4px);
          border-color: var(--brand);
          box-shadow: 0 12px 30px rgba(0,0,0,0.1);
        }
        .card-top {
          display: flex;
          gap: 16px;
          align-items: flex-start;
        }
        .card-thumb, .card-thumb-placeholder {
          width: 80px;
          height: 80px;
          border-radius: 12px;
          overflow: hidden;
          flex-shrink: 0;
          background: var(--border-light);
          display: flex;
          align-items: center;
          justify-content: center;
          color: var(--text-muted);
        }
        .card-thumb img {
          width: 100%;
          height: 100%;
          object-fit: cover;
        }
        .card-header-info {
          flex: 1;
          min-width: 0;
        }
        .card-domain {
          font-size: 11px;
          color: var(--text-muted);
          margin-bottom: 4px;
          font-weight: 700;
          text-transform: capitalize;
        }
        h3 {
          font-size: 16px;
          font-weight: 700;
          line-height: 1.4;
          color: var(--text-primary);
          display: -webkit-box;
          -webkit-line-clamp: 2;
          -webkit-box-orient: vertical;
          overflow: hidden;
        }
        .card-snippet {
          font-size: 13px;
          color: var(--text-secondary);
          line-height: 1.5;
          display: -webkit-box;
          -webkit-line-clamp: 3;
          -webkit-box-orient: vertical;
          overflow: hidden;
        }
        .card-snippet b {
          color: var(--brand);
          font-weight: 600;
        }
        .card-footer {
          margin-top: auto;
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding-top: 12px;
          border-top: 1px solid var(--border-light);
        }
        .footer-tag {
          display: flex;
          align-items: center;
          gap: 4px;
          font-size: 11px;
          color: var(--text-muted);
          font-weight: 600;
        }
        .ext-icon {
          color: var(--text-muted);
        }
        .search-result-card:hover .ext-icon {
          color: var(--brand);
        }

        .results-loading {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
          gap: 20px;
        }
        .skeleton-card {
          height: 200px;
          border-radius: 16px;
        }
        .no-results {
          text-align: center;
          padding: 80px 20px;
          color: var(--text-muted);
        }
        .no-results h2 {
          margin: 16px 0 8px;
        }

        .summary-overview {
          background: var(--bg-card);
          border: 1px solid var(--brand);
          border-radius: 16px;
          padding: 24px;
          margin-bottom: 32px;
          position: relative;
          overflow: hidden;
        }
        .summary-header {
          display: flex;
          align-items: center;
          gap: 8px;
          font-size: 11px;
          font-weight: 800;
          color: var(--brand);
          margin-bottom: 12px;
          letter-spacing: 1px;
        }
        .summary-content {
          font-size: 15px;
          line-height: 1.6;
          color: var(--text-primary);
        }

        .load-more-container {
          display: flex;
          justify-content: center;
          margin-top: 40px;
        }
        .load-more-btn {
          padding: 12px 32px;
          border: 1px solid var(--border);
          color: var(--text-secondary);
          font-weight: 600;
          border-radius: 999px;
          transition: all 0.2s;
        }
        .load-more-btn:hover {
          background: var(--bg-card);
          border-color: var(--brand);
          color: var(--brand);
          box-shadow: 0 4px 12px rgba(62, 166, 255, 0.1);
        }
      `}</style>
    </div>
  );
};

export default AdvancedSearchView;
