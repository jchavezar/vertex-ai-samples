import React, { useState, useEffect, useRef } from 'react';
import { Search, Loader2, X, FileText, ChevronRight, Bot } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import ReactMarkdown from 'react-markdown';
import PdfChatOverlay from './PdfChatOverlay';
import './DiscoverySearch.css';

const DiscoverySearch = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [query, setQuery] = useState('');
  const [results, setResults] = useState(null);
  const [isSearching, setIsSearching] = useState(false);
  const [aiOverview, setAiOverview] = useState('');
  const [pdfSuggestion, setPdfSuggestion] = useState(null);
  const [selectedPdf, setSelectedPdf] = useState(null);
  const [isOverviewLoading, setIsOverviewLoading] = useState(false);
  const searchRef = useRef(null);
  const inputRef = useRef(null);
  const overviewAbortControllerRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (document.querySelector('.pdf-chat-overlay-backdrop')?.contains(event.target)) {
        return;
      }
      if (searchRef.current && !searchRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };
    
    const handleKeyDown = (event) => {
      if (event.key === 'Escape') {
        setIsOpen(false);
      }
      if ((event.metaKey || event.ctrlKey) && event.key === 'k') {
        event.preventDefault();
        setIsOpen(true);
        setTimeout(() => {
          inputRef.current?.focus();
        }, 100);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    document.addEventListener("keydown", handleKeyDown);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, []);

  useEffect(() => {
    const timeoutId = setTimeout(() => {
      if (query.trim().length > 2) {
        performSearch(query);
      } else {
        setResults(null);
      }
    }, 250); // 250ms debounce for faster feel
    return () => clearTimeout(timeoutId);
  }, [query]);

  const performSearch = async (searchQuery) => {
    setIsSearching(true);
    setAiOverview('');
    setPdfSuggestion(null);
    setIsOverviewLoading(true);
    if (overviewAbortControllerRef.current) {
      overviewAbortControllerRef.current.abort();
    }
    try {
      const response = await fetch('/api/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: searchQuery })
      });
      if (response.ok) {
        const data = await response.json();
        setResults(data);
        if (data && data.results && data.results.length > 0) {
           fetchGenerativeOverview(searchQuery, data.results);
        } else {
           setIsOverviewLoading(false);
        }
      } else {
        console.error("Discovery Engine search returned HTTP error");
        setIsOverviewLoading(false);
      }
    } catch (error) {
      console.error("Discovery Engine search failed:", error);
      setIsOverviewLoading(false);
    } finally {
      setIsSearching(false);
    }
  };

  const fetchGenerativeOverview = async (searchQuery, searchResults) => {
    const controller = new AbortController();
    overviewAbortControllerRef.current = controller;
    
    try {
      const response = await fetch('/api/search/generative-overview', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: searchQuery, search_results: searchResults }),
        signal: controller.signal
      });
      
      if (!response.body) {
        setIsOverviewLoading(false);
        return;
      }
      
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let overviewText = "";
      
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split('\n');
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const dataStr = line.slice(6);
            if (dataStr === '[DONE]') break;
            
            try {
              const parsed = JSON.parse(dataStr);
              if (parsed.text) {
                setIsOverviewLoading(false); // Found first token
                overviewText += parsed.text;
                
                // Check if the stream has reached the [PDF_SUGGESTION] tag
                const pdfMatch = overviewText.match(/\[PDF_SUGGESTION\](.*)\[\/PDF_SUGGESTION\]/s);
                if (pdfMatch) {
                    try {
                        const pdfObj = JSON.parse(pdfMatch[1]);
                        setPdfSuggestion(pdfObj);
                        overviewText = overviewText.replace(/\[PDF_SUGGESTION\].*\[\/PDF_SUGGESTION\]/s, "");
                    } catch (e) {
                        console.error("Could not parse PDF Suggestion", e);
                    }
                }
                
                setAiOverview(overviewText);
              }
            } catch (e) {
              // Ignore parse errors on incomplete chunks
            }
          }
        }
      }
    } catch (error) {
      if (error.name !== 'AbortError') {
        console.error("Generative overview failed:", error);
      }
    } finally {
      setIsOverviewLoading(false);
    }
  };

  const handleOpen = () => {
    setIsOpen(true);
    setTimeout(() => {
      inputRef.current?.focus();
    }, 100);
  };

  const handleClear = () => {
    setQuery('');
    setResults(null);
    setAiOverview('');
    setPdfSuggestion(null);
    setSelectedPdf(null);
    setIsOverviewLoading(false);
    if (overviewAbortControllerRef.current) {
      overviewAbortControllerRef.current.abort();
    }
    inputRef.current?.focus();
  };

  const handlePdfDeepDive = (e, pdfInfo) => {
    e.preventDefault();
    setSelectedPdf(pdfInfo);
  };

  return (
    <div className="discovery-search-container" ref={searchRef}>
      {/* Trigger Button */}
      <div 
        className={`search-trigger ${isOpen ? 'active' : ''}`}
        onClick={handleOpen}
      >
        <Search size={18} />
        <span>Search Global Intelligence...</span>
        <div className="search-shortcut">⌘K</div>
      </div>

      {/* Crystal Glass Overlay */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            key="discovery-overlay-backdrop"
            className="discovery-overlay-backdrop"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setIsOpen(false)}
          />
        )}
      </AnimatePresence>

      <AnimatePresence>
        {isOpen && (
          <div key="discovery-overlay-wrapper" className="discovery-overlay-wrapper">
              <motion.div 
                className="discovery-overlay-panel glass-panel"
                initial={{ opacity: 0, y: -20, scale: 0.95 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: -20, scale: 0.95 }}
                transition={{ duration: 0.2, ease: "easeOut" }}
              >
                <div className="search-input-header">
                  <Search size={24} className="search-input-icon text-accent" />
                  <input 
                    ref={inputRef}
                    type="text" 
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="Search Global Intelligence, tax compliance, or policies..."
                    autoComplete="off"
                    spellCheck="false"
                  />
                  {query && (
                    <button className="clear-search-btn" onClick={handleClear}>
                      <X size={20} />
                    </button>
                  )}
                </div>

                <div className="search-results-viewport">
                  {isSearching && (
                    <div className="search-loading-state">
                      <motion.div 
                        animate={{ rotate: 360 }} 
                        transition={{ repeat: Infinity, duration: 1.5, ease: "linear" }}
                      >
                        <Loader2 size={32} className="text-accent" />
                      </motion.div>
                      <p>Quantum Synthesizing Vertex Search...</p>
                    </div>
                  )}

                  {!isSearching && isOverviewLoading && !aiOverview && (
                    <div className="generative-overview-section">
                      <div className="overview-header">
                        <motion.div animate={{ rotate: 360 }} transition={{ repeat: Infinity, duration: 1.5, ease: "linear" }}>
                          <Loader2 size={20} className="text-accent" />
                        </motion.div>
                        <span>Analyzing insights...</span>
                      </div>
                    </div>
                  )}

                  {aiOverview && (
                    <div className="generative-overview-section">
                      <div className="overview-header">
                        <Bot size={20} className="text-accent" />
                        <span>AI Executive Summary</span>
                      </div>
                      <div className="overview-content ai-markdown-content">
                        <ReactMarkdown>{aiOverview}</ReactMarkdown>
                      </div>
                      {pdfSuggestion && (
                        <div 
                          onClick={(e) => handlePdfDeepDive(e, pdfSuggestion)}
                          className="pdf-suggestion-card"
                          role="button"
                          tabIndex={0}
                        >
                          <FileText size={24} className="text-accent" />
                          <div className="pdf-details">
                            <span className="pdf-title">{pdfSuggestion.title}</span>
                            <span className="pdf-hint">Deep Dive: Click to analyze with Chief Tax Gemini</span>
                          </div>
                        </div>
                      )}
                    </div>
                  )}

                  {!isSearching && results && results.results && results.results.length > 0 && (
                    <div className="search-results-list">
                      <div className="results-badge">
                        <span>{results.totalSize || results.results.length} results from Knowledge Graph</span>
                      </div>
                      {results.results.slice(0, 8).map((item, idx) => {
                        const structData = item.document?.derivedStructData || {};
                        const pagemap = structData.pagemap || {};
                        const thumbnail = pagemap.cse_thumbnail?.[0]?.src;
                        const meta = pagemap.metatags?.[0] || {};
                        const date = meta.publishdate || meta.displaydate || meta.sortdate?.split('T')[0];
                        const snippet = structData.snippets?.[0]?.htmlSnippet || structData.snippets?.[0]?.snippet;
                        
                        const isPdf = structData.fileFormat === "PDF/Adobe Acrobat" || (structData.link && structData.link.toLowerCase().endsWith('.pdf'));
                        return (
                          <motion.div 
                            key={idx} 
                            className="search-result-item"
                            initial={{ opacity: 0, x: -10 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: idx * 0.05 }}
                          >
                            <div className="result-icon">
                              {thumbnail ? (
                                <img src={thumbnail} alt="thumb" className="result-thumbnail" />
                              ) : (
                                <FileText size={20} />
                              )}
                            </div>
                            <div className="result-content">
                              <h4>
                                <a href={structData.link || '#'} target={structData.link ? "_blank" : "_self"} rel="noreferrer" className="result-title-link">
                                  {structData.title || structData.htmlTitle?.replace(/<[^>]*>?/gm, '') || item.document?.name || 'Tax Briefing Document'}
                                </a>
                              </h4>
                              {snippet && (
                                <p dangerouslySetInnerHTML={{ __html: snippet }}></p>
                              )}
                              <div className="result-meta">
                                {date && <span className="meta-badge date-badge">{date}</span>}
                                {isPdf && <span className="meta-badge pdf-badge">PDF</span>}
                                {structData.displayLink && <a href={structData.link} target="_blank" rel="noreferrer" className="meta-link">{structData.displayLink}</a>}
                              </div>
                            </div>
                            <div className="result-action">
                              {isPdf && (
                                <button className="result-action-btn pdf-chat-action" onClick={(e) => handlePdfDeepDive(e, {
                                    title: structData.title || item.document?.name || 'Tax Document',
                                    url: structData.link,
                                    snippet: snippet || ''
                                })}>
                                  <Bot size={14} /> Chat
                                </button>
                              )}
                              <a href={structData.link || '#'} target="_blank" rel="noreferrer" className="result-action-btn primary">
                                <ChevronRight size={18} />
                              </a>
                            </div>
                          </motion.div>
                        );
                      })}
                    </div>
                  )}

                  {!isSearching && results && (!results.results || results.results.length === 0) && (
                    <div className="search-empty-state">
                      <p>No actionable intelligence found for "{query}".</p>
                    </div>
                  )}

                  {!isSearching && !results && query.length <= 2 && (
                    <div className="search-suggestions">
                      <h5>Suggested Intelligence Queries</h5>
                      <div className="suggestion-chips">
                        <span onClick={() => setQuery("Digital Services Tax EMEA")}>Digital Services Tax EMEA</span>
                        <span onClick={() => setQuery("Pillar Two Compliance")}>Pillar Two Compliance</span>
                        <span onClick={() => setQuery("Transfer Pricing Guidelines")}>Transfer Pricing Guidelines</span>
                        <span onClick={() => setQuery("Permanent Establishment")}>Permanent Establishment Risk</span>
                      </div>
                    </div>
                  )}
                </div>
                
                <div className="search-footer">
                  <span className="powered-by">
                     Powered by <strong>Vertex AI Discovery Engine</strong>
                  </span>
                  <span className="esc-hint">Press ESC to close</span>
                </div>
              </motion.div>
          </div>
        )}
      </AnimatePresence>

      <AnimatePresence>
        {isOpen && selectedPdf && (
          <PdfChatOverlay 
            key="pdf-chat-overlay"
            pdfInfo={selectedPdf} 
            onClose={() => setSelectedPdf(null)} 
          />
        )}
      </AnimatePresence>
    </div>
  );
};

export default DiscoverySearch;
