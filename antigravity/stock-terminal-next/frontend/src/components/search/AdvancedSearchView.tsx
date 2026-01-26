import React, { useState, useEffect, useRef } from 'react';
import { Search, Sparkles, Globe, Calendar, ExternalLink, Loader2, ArrowRight, FileText } from 'lucide-react';
import clsx from 'clsx';
import ReactMarkdown from 'react-markdown';
import { motion, AnimatePresence } from 'framer-motion';

// Types
interface SearchResult {
  document: {
    derivedStructData: {
      title?: string;
      link?: string;
      htmlSnippet?: string;
      snippets?: { htmlSnippet: string }[];
      pagemap?: {
        cse_thumbnail?: { src: string }[];
      };
      displayLink?: string;
      mime?: string;
      fileFormat?: string;
    };
  };
}

interface SummaryState {
  summaryText: string;
  loading: boolean;
  followUpQuestions?: string[];
  pdfSuggestion?: {
    title: string;
    url: string;
    reason: string;
  };
  pdfAnalysis?: {
    text: string;
    loading: boolean;
  };
}

export const AdvancedSearchView = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [totalSize, setTotalSize] = useState(0);
  const [summary, setSummary] = useState<SummaryState | null>(null);
  const [isOverviewExpanded, setIsOverviewExpanded] = useState(true);
  const debounceTimer = useRef<any>(null);

  const handleSearch = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError(null);
    setSummary(null); // Reset summary on new search
    setIsOverviewExpanded(true);

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

      // Trigger AI Summary if results found
      if (resultsList.length > 0) {
        generateSummary(query, resultsList);
      }

    } catch (err) {
      console.error(err);
      setError('Failed to fetch search results. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const generateSummary = async (searchQuery: string, resultsList: SearchResult[]) => {
    setSummary({ summaryText: '', loading: true });

    try {
      // Extract top 5 snippets with metadata
      const topResults = resultsList.slice(0, 5).map(res => {
        const doc = res.document.derivedStructData;
        const snippet = doc.htmlSnippet || (doc.snippets?.[0]?.htmlSnippet) || '';
        return {
          link: doc.link || doc.displayLink || '',
          title: doc.title || 'Untitled',
          snippet: snippet,
          mime: doc.mime || '',
          fileFormat: doc.fileFormat || ''
        };
      });

      const response = await fetch('http://localhost:8001/search/generative-overview', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: searchQuery,
          contexts: topResults.map(r => r.snippet).filter(Boolean), // Fallback
          search_results: topResults
        })
      });

      if (!response.ok) return;

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      if (!reader) return;

      // Read the stream (which now contains one or more JSON lines)
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (!line.trim()) continue;
          try {
            const data = JSON.parse(line);

            // Handle Unified Payload
            if (data.text) {
              setSummary(prev => ({
                ...prev!,
                summaryText: data.text,
                loading: false
              }));
            }

            if (data.data?.follow_up_questions) {
              setSummary(prev => ({
                ...prev!,
                followUpQuestions: data.data.follow_up_questions
              }));
            }

            if (data.data?.pdf_suggestion) {
              setSummary(prev => ({
                ...prev!,
                pdfSuggestion: data.data.pdf_suggestion
              }));
            }

            // Handle Error
            if (data.error) {
              console.error("Overview Error:", data.error);
              setSummary(null);
            }

          } catch (e) {
            console.warn("Stream parse error", e);
          }
        }
      }
    } catch (err) {
      console.error("Summary failed", err);
      setSummary(null);
    }
  };



  const handleAnalyzePdf = async (url: string) => {
    if (!summary) return;

    // Set loading state inside existing summary
    setSummary(prev => ({
      ...prev!,
      pdfAnalysis: { text: '', loading: true }
    }));

    try {
      const response = await fetch('http://localhost:8001/search/analyze-pdf', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url, query: query || "Summarize the key financial highlights." })
      });

      if (!response.ok) throw new Error("Analysis failed");

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      if (!reader) return;

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
              setSummary(prev => ({
                ...prev!,
                pdfAnalysis: {
                  text: (prev?.pdfAnalysis?.text || '') + data.text,
                  loading: false
                }
              }));
            }
          } catch (e) { }
        }
      }
    } catch (e) {
      console.error("PDF Analysis Error", e);
      setSummary(prev => ({
        ...prev!,
        pdfAnalysis: { text: 'Failed to analyze PDF. Please try again.', loading: false }
      }));
    }
  };

  // Debounce
  useEffect(() => {
    if (debounceTimer.current) clearTimeout(debounceTimer.current);

    if (query.length > 2) {
      debounceTimer.current = setTimeout(() => {
        handleSearch();
      }, 300);
    }

    return () => {
      if (debounceTimer.current) clearTimeout(debounceTimer.current);
    };
  }, [query]);

  // Derived state for layout transition
  const isResultsView = results.length > 0 || loading || (summary?.loading || !!summary?.summaryText);

  return (
    <div className="pb-20 bg-[var(--bg-app)] min-h-full">
      {/* Hero Section */}
      <div className={clsx(
        "px-5 text-center bg-[radial-gradient(circle_at_center,var(--bg-card)_0%,transparent_70%)] transition-all duration-500 ease-in-out",
        isResultsView ? "py-6 mb-2" : "py-16 mb-5"
      )}>
        <div className="max-w-3xl mx-auto">

          {/* Animated Hero Content (Hide on Results) */}
          <AnimatePresence>
            {!isResultsView && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                transition={{ duration: 0.4, ease: "easeInOut" }}
                className="overflow-hidden"
              >
                <div className="inline-flex items-center gap-1.5 bg-blue-500/10 text-blue-400 px-3 py-1 rounded-full text-[10px] font-bold tracking-wider mb-5 border border-blue-500/20">
                  <Sparkles size={12} />
                  <span>AI POWERED SEARCH</span>
                </div>

                <h1 className="text-4xl font-extrabold tracking-tight mb-3 bg-gradient-to-br from-white to-blue-500 bg-clip-text text-transparent">
                  Discover Financial Intelligence
                </h1>
                <p className="text-[var(--text-secondary)] text-base mb-10">
                  Guided, next-generation search across the FactSet knowledge base.
                </p>
              </motion.div>
            )}
          </AnimatePresence>

          <form onSubmit={handleSearch} className="relative max-w-xl mx-auto mb-6">
            <motion.div
              layout
              className={clsx(
                "flex items-center bg-[var(--bg-card)] px-5 py-2 rounded-full border border-[var(--border)] shadow-xl transition-all duration-300",
                loading && "border-blue-500/50 shadow-blue-500/10",
                "focus-within:border-blue-500 focus-within:shadow-2xl focus-within:-translate-y-0.5"
              )}>
              <Search className="text-[var(--text-muted)]" size={20} />
              <input
                type="text"
                placeholder="Search earnings, reports, filings..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                autoFocus
                className="flex-1 border-none bg-transparent p-3 text-base text-[var(--text-primary)] outline-none placeholder:text-[var(--text-muted)]"
              />
              <button
                type="submit"
                disabled={loading || !query.trim()}
                className="w-10 h-10 bg-gradient-to-r from-blue-600 to-blue-500 text-white rounded-full flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed hover:brightness-110 transition-all"
              >
                {loading ? <Loader2 className="animate-spin" size={18} /> : <ArrowRight size={18} />}
              </button>
            </motion.div>
          </form>

          {/* Suggestions (Hide on Results) */}
          <AnimatePresence>
            {!isResultsView && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                transition={{ duration: 0.3 }}
                className="flex items-center justify-center gap-3 flex-wrap overflow-hidden"
              >
                <span className="text-xs text-[var(--text-muted)]">Try:</span>
                {[
                  { label: "Ownership & Transactions", q: "How can I incorporate financial transaction data and insider transactions into my investment process?" },
                  { label: "Supply Chain Networks", q: "How does FactSet help access complex networks of customers, suppliers, and competitors?" },
                  { label: "FactSet Marketplace", q: "What solutions are available on FactSet Marketplace?" },
                  { label: "ESG Study Data (PDF)", q: "How many unique firm-day observations were included in the final sample of the study on stock price reactions to ESG news?" }
                ].map((btn) => (
                  <button
                    key={btn.label}
                    onClick={() => setQuery(btn.q)}
                    className="text-xs text-[var(--text-secondary)] px-3 py-1 border border-[var(--border)] rounded-full hover:bg-[var(--bg-card)] hover:text-blue-400 transition-colors"
                  >
                    {btn.label}
                  </button>
                ))}
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>

      {/* Results Section */}
      <div className="max-w-6xl mx-auto px-5">
        {loading && !results.length && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {[1, 2, 3, 4, 5, 6].map(i => (
              <div key={i} className="h-48 rounded-2xl bg-[var(--bg-card)] animate-pulse border border-[var(--border)]" />
            ))}
          </div>
        )}

        {error && <div className="text-center text-red-400 py-10">{error}</div>}

        {/* AI Overview */}
        {(summary?.loading || summary?.summaryText) && (
          <div className="bg-[var(--bg-card)] border border-blue-500/30 rounded-2xl mb-8 relative overflow-hidden shadow-lg shadow-blue-900/5 transition-all duration-500 ease-out animate-in fade-in slide-in-from-bottom-2">

            {/* Collapsible Header */}
            <button
              onClick={() => setIsOverviewExpanded(!isOverviewExpanded)}
              className="w-full flex items-center justify-between p-4 hover:bg-blue-500/5 transition-colors"
            >
              <div className="flex items-center gap-2 text-[11px] font-bold text-blue-400 tracking-wider">
                <Sparkles size={14} className={summary.loading ? "animate-pulse" : ""} />
                <span>AI OVERVIEW (BETA)</span>
              </div>
              <div className="flex items-center gap-2 text-xs text-[var(--text-muted)] font-medium">
                {isOverviewExpanded ? 'Hide' : 'Show'}
                <ArrowRight size={14} className={clsx("transition-transform duration-300", isOverviewExpanded ? "-rotate-90" : "rotate-90")} />
              </div>
            </button>

            {/* Collapsible Content */}
            <AnimatePresence>
              {isOverviewExpanded && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: "auto", opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  transition={{ duration: 0.3 }}
                >
                  <div className="px-6 pb-6">
                    {summary.summaryText ? (
                      <div className="animate-in fade-in">
                        {/* Main Summary Text */}
                        <div className="prose prose-invert prose-sm max-w-none text-[var(--text-primary)] leading-relaxed mb-6">
                          <ReactMarkdown>{summary.summaryText.split('```json')[0].trim()}</ReactMarkdown>
                        </div>

                        {summary.pdfSuggestion && (
                          <div className="mt-6 mb-2 p-4 bg-blue-50/50 border border-blue-100 rounded-xl flex items-start gap-4 animate-in slide-in-from-bottom-3 fade-in duration-500 text-left relative overflow-hidden group">
                            {/* Decorative Background */}
                            <div className="absolute top-0 right-0 p-10 bg-blue-500/5 rounded-full blur-2xl -translate-y-1/2 translate-x-1/2 group-hover:bg-blue-500/10 transition-colors" />

                            <div className="p-2.5 bg-white border border-blue-100 rounded-lg shrink-0 text-blue-600 shadow-sm relative z-10">
                              <Sparkles size={20} className="fill-blue-100" />
                            </div>
                            <div className="flex-1 min-w-0 relative z-10">
                              <div className="flex items-center gap-2 mb-2">
                                <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-blue-100 text-blue-700 uppercase tracking-wider">
                                  Context Match
                                </span>
                                <h4 className="text-sm font-bold text-gray-900">
                                  Relevant Document Found
                                </h4>
                              </div>

                              <div className="bg-white/60 p-3 rounded-lg border border-blue-100/50 mb-3">
                                <span className="text-[10px] text-blue-500 font-bold uppercase tracking-wide block mb-1">Match Reason</span>
                                <p className="text-xs text-slate-700 leading-relaxed font-medium">
                                  {summary.pdfSuggestion.reason}
                                </p>
                              </div>

                              <div className="flex items-center gap-3 mt-1">
                                <button
                                  onClick={() => handleAnalyzePdf(summary.pdfSuggestion!.url)}
                                  disabled={summary.pdfAnalysis?.loading}
                                  className="px-4 py-2 text-xs font-bold bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-all shadow-sm flex items-center gap-2 disabled:opacity-50 hover:shadow-md hover:scale-[1.02]"
                                >
                                  {summary.pdfAnalysis?.loading ? <Loader2 size={13} className="animate-spin" /> : <FileText size={13} />}
                                  {summary.pdfAnalysis?.loading ? 'Analyzing Content...' : 'Deep Dive & Verify'}
                                </button>
                                <span className="text-[10px] text-blue-400 font-medium">
                                  Source: <span className="text-blue-600 underline decoration-blue-300 underline-offset-2">"{summary.pdfSuggestion.title}"</span>
                                </span>
                              </div>

                              {/* Analysis Result */}
                              {summary.pdfAnalysis && (summary.pdfAnalysis.text || summary.pdfAnalysis.loading) && (
                                <div className="mt-4 pt-4 border-t border-blue-100/50 w-full overflow-hidden">
                                  <div className="flex items-center gap-2 mb-2">
                                    <Sparkles size={12} className="text-blue-500" />
                                    <h5 className="text-xs font-bold text-blue-900 uppercase tracking-wider">Extraction Result</h5>
                                  </div>
                                  <div className="prose prose-sm max-w-none text-slate-800 leading-relaxed bg-white p-4 rounded-xl border border-blue-100 shadow-sm break-words relative">
                                    <ReactMarkdown>{summary.pdfAnalysis.text}</ReactMarkdown>
                                    {summary.pdfAnalysis.loading && <span className="inline-block w-1.5 h-4 bg-blue-600 animate-pulse ml-1 align-middle" />}
                                  </div>
                                </div>
                              )}
                            </div>
                          </div>
                        )}

                        {/* Related Questions */}
                        {summary.followUpQuestions && summary.followUpQuestions.length > 0 && (
                          <div className="border-t border-[var(--border)] pt-4 mt-4 animate-in slide-in-from-bottom-2 fade-in duration-500">
                            <span className="text-[10px] font-bold text-[var(--text-muted)] uppercase tracking-wider mb-3 block">Related Questions</span>
                            <div className="flex flex-wrap gap-2 justify-center">
                              {summary.followUpQuestions.map((q, idx) => (
                                <button
                                  key={idx}
                                  onClick={() => setQuery(q)}
                                  className="text-xs text-blue-400 bg-blue-400/10 border border-blue-400/20 px-3 py-1.5 rounded-full hover:bg-blue-400/20 hover:border-blue-400/40 transition-all text-left"
                                >
                                  {q}
                                </button>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    ) : (
                      <div className="space-y-3 p-1">
                        <div className="h-4 bg-gradient-to-r from-blue-500/10 via-blue-500/20 to-blue-500/10 rounded w-3/4 animate-pulse" />
                        <div className="h-4 bg-gradient-to-r from-blue-500/5 via-blue-500/10 to-blue-500/5 rounded w-full animate-pulse delay-75" />
                        <div className="h-4 bg-gradient-to-r from-blue-500/5 via-blue-500/10 to-blue-500/5 rounded w-5/6 animate-pulse delay-150" />
                        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/5 to-transparent skew-x-12 translate-x-[-100%] animate-[shimmer_1.5s_infinite]" />
                      </div>
                    )}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        )}

        {!loading && results.length > 0 && (
          <div className="animate-in fade-in slide-in-from-bottom-4 duration-700 fill-mode-backwards" style={{ animationDelay: '100ms' }}>
            <div className="mb-6 text-xs text-[var(--text-muted)] font-bold uppercase tracking-wide">
              Found {totalSize} structured documents
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
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
                    className="group flex flex-col gap-4 bg-[var(--bg-card)] border border-[var(--border)] rounded-2xl p-5 transition-all hover:-translate-y-1 hover:border-blue-500/50 hover:shadow-xl hover:shadow-blue-500/5"
                  >
                    <div className="flex gap-4 items-start">
                      {thumbnail ? (
                        <div className="w-20 h-20 rounded-xl overflow-hidden shrink-0 bg-[var(--bg-app)]">
                          <img src={thumbnail} alt="" className="w-full h-full object-cover" />
                        </div>
                      ) : (
                        <div className="w-20 h-20 rounded-xl shrink-0 bg-[var(--bg-app)] flex items-center justify-center text-[var(--text-muted)]">
                          <Globe size={24} />
                        </div>
                      )}
                      <div className="min-w-0 flex-1">
                        <div className="text-[11px] text-[var(--text-muted)] font-bold mb-1 capitalize truncate">
                          {domain}
                        </div>
                        <h3
                          className="text-base font-bold text-[var(--text-primary)] leading-snug line-clamp-2 group-hover:text-blue-400 transition-colors"
                          dangerouslySetInnerHTML={{ __html: doc.title || 'Untitled Document' }}
                        />
                      </div>
                    </div>

                    {snippet && (
                      <div
                        className="text-sm text-[var(--text-secondary)] leading-relaxed line-clamp-3"
                        dangerouslySetInnerHTML={{ __html: snippet }}
                      />
                    )}

                    <div className="mt-auto pt-3 border-t border-[var(--border)] flex items-center justify-between text-[var(--text-muted)]">
                      <div className="flex items-center gap-1.5 text-[11px] font-medium">
                        <Calendar size={12} />
                        <span>Document</span>
                      </div>
                      <ExternalLink size={14} className="group-hover:text-blue-400 transition-colors" />
                    </div>
                  </a>
                );
              })}
            </div>
          </div>
        )}

        {!loading && !results.length && query && !error && (
          <div className="text-center py-20 text-[var(--text-muted)]">
            <Search size={48} className="mx-auto mb-4 opacity-50" />
            <h2 className="text-xl font-bold mb-2">No results found</h2>
            <p>Try broadening your search terms or checking for typos.</p>
          </div>
        )}
      </div>
    </div>
  );
};
