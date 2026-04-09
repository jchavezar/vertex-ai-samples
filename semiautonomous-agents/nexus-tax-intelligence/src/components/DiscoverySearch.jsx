import React, { useState, useEffect } from 'react';
import { Search, X, FileText, Loader2 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import ReactMarkdown from 'react-markdown';
import PdfChatOverlay from './PdfChatOverlay';
import './DiscoverySearch.css';

const suggestedQueries = ["Digital Services Tax EMEA", "Pillar Two Compliance", "Transfer Pricing Guidelines", "Permanent Establishment Risk"];

const DiscoverySearch = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [aiOverview, setAiOverview] = useState('');
  const [isGeneratingOverview, setIsGeneratingOverview] = useState(false);
  const [pdfSuggestion, setPdfSuggestion] = useState(null);
  const [selectedPdf, setSelectedPdf] = useState(null);
  const [isPdfChatOpen, setIsPdfChatOpen] = useState(false);

  useEffect(() => {
    const handleKeyDown = (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') { e.preventDefault(); setIsOpen(true); }
      if (e.key === 'Escape') setIsOpen(false);
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  const handleSearch = async (searchQuery) => {
    const q = searchQuery || query;
    if (!q.trim()) return;
    setIsSearching(true);
    setResults([]);
    setAiOverview('');
    setPdfSuggestion(null);

    try {
      const response = await fetch('/pwc/api/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: q })
      });
      const data = await response.json();
      const searchResults = data.results || [];
      setResults(searchResults.slice(0, 8));
      if (searchResults.length > 0) generateOverview(q, searchResults);
    } catch (error) {
      console.error("Search error:", error);
    } finally {
      setIsSearching(false);
    }
  };

  const generateOverview = async (q, searchResults) => {
    setIsGeneratingOverview(true);
    try {
      const response = await fetch('/pwc/api/search/generative-overview', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: q, search_results: searchResults })
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
                if (parsed.text) { fullText += parsed.text; setAiOverview(fullText); }
              } catch (err) { /* skip */ }
            }
          }
        }
      }

      // Parse PDF suggestion
      const pdfMatch = fullText.match(/\[PDF_SUGGESTION\](.*?)\[\/PDF_SUGGESTION\]/s);
      if (pdfMatch) {
        try {
          setPdfSuggestion(JSON.parse(pdfMatch[1]));
          setAiOverview(fullText.replace(/\[PDF_SUGGESTION\].*?\[\/PDF_SUGGESTION\]/s, ''));
        } catch (e) { /* skip */ }
      }
    } catch (error) {
      console.error("Overview error:", error);
    } finally {
      setIsGeneratingOverview(false);
    }
  };

  const openPdfChat = (doc) => {
    setSelectedPdf(doc);
    setIsPdfChatOpen(true);
  };

  return (
    <>
      <div className="search-trigger" onClick={() => setIsOpen(true)}>
        <Search size={16} />
        <span>Search</span>
        <span className="search-shortcut">Cmd K</span>
      </div>

      <AnimatePresence>
        {isOpen && (
          <motion.div className="discovery-overlay" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
            <div className="discovery-container">
              <button className="discovery-close" onClick={() => setIsOpen(false)}><X size={24} /></button>
              <div className="discovery-search-bar">
                <Search size={20} />
                <input autoFocus placeholder="Search tax intelligence corpus..." value={query} onChange={(e) => setQuery(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && handleSearch()} />
                {isSearching && <Loader2 size={20} className="spin" />}
              </div>

              {!results.length && !isSearching && (
                <div className="suggested-queries">
                  {suggestedQueries.map((sq, idx) => (
                    <button key={idx} className="suggested-query-btn" onClick={() => { setQuery(sq); handleSearch(sq); }}>{sq}</button>
                  ))}
                </div>
              )}

              {(results.length > 0 || aiOverview) && (
                <div className="discovery-results">
                  {aiOverview && (
                    <div className="ai-overview-card">
                      <div className="overview-label">AI Executive Summary</div>
                      <ReactMarkdown>{aiOverview}</ReactMarkdown>
                    </div>
                  )}

                  {pdfSuggestion && (
                    <div className="pdf-suggestion-card" onClick={() => openPdfChat(pdfSuggestion)}>
                      <FileText size={20} />
                      <div>
                        <strong>{pdfSuggestion.title}</strong>
                        <p>{pdfSuggestion.reason}</p>
                      </div>
                      <span className="chat-with-ai-btn">Chat with AI</span>
                    </div>
                  )}

                  <div className="results-list">
                    {results.map((res, idx) => {
                      const doc = res.document || {};
                      const sd = doc.derivedStructData || {};
                      const title = sd.title || 'Untitled';
                      const snippets = sd.snippets || [];
                      const snippet = snippets[0]?.snippet || '';
                      const link = sd.link || '#';
                      const format = sd.fileFormat || '';

                      return (
                        <div key={idx} className="result-item" onClick={() => openPdfChat({ title, url: link, snippet, format })}>
                          <div className="result-header">
                            <span className="result-title">{title}</span>
                            {format && <span className={`format-badge ${format.toLowerCase().includes('pdf') ? 'pdf-badge' : ''}`}>{format}</span>}
                          </div>
                          <p className="result-snippet" dangerouslySetInnerHTML={{ __html: snippet }} />
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <PdfChatOverlay isOpen={isPdfChatOpen} onClose={() => setIsPdfChatOpen(false)} document={selectedPdf} />
    </>
  );
};

export default DiscoverySearch;
