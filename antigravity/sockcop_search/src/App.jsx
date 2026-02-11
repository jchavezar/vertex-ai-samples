import React, { useState, useEffect } from 'react';
import DOMPurify from 'dompurify';
import {
  exchangeForGoogleToken,
  getWifLoginUrl
} from './api/auth';
import { CONFIG } from './api/config';
import { executeSearch } from './api/search';
import { Search, LogIn, ShieldCheck, Database, FileText, ExternalLink, Loader2, ChevronRight, AlertCircle } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

function App() {
  const [googleToken, setGoogleToken] = useState(localStorage.getItem('google_token'));
  const [loading, setLoading] = useState(false);
  const [query, setQuery] = useState('');
  const [searchResult, setSearchResult] = useState(null);
  const [error, setError] = useState(null);
  const [activeCitation, setActiveCitation] = useState(null);

  // Handle OAuth Callbacks
  useEffect(() => {
    const hash = window.location.hash;

    console.log('[AUTH DEBUG] Component Render/Update');
    console.log('[AUTH DEBUG] Hash:', hash);
    console.log('[AUTH DEBUG] Current Local Token:', googleToken ? 'PRESENT' : 'MISSING');

    // Check for ID Token (WIF flow)
    if (hash && hash.includes('id_token=')) {
      console.log('[AUTH DEBUG] Path: WIF Hash detected');
      const hashParams = new URLSearchParams(hash.substring(1));
      const idToken = hashParams.get('id_token');

      if (idToken) {
        console.log('[AUTH DEBUG] ID Token found. Length:', idToken.length);
        setLoading(true);
        setError(null);
        console.log('[AUTH DEBUG] Triggering exchangeForGoogleToken...');
        exchangeForGoogleToken(idToken)
          .then(data => {
            console.log('[AUTH DEBUG] SUCCESS: Google Token Received');
            setGoogleToken(data.access_token);
            localStorage.setItem('google_token', data.access_token);
            // Clear URL
            window.history.replaceState({}, document.title, window.location.pathname);
          })
          .catch(err => {
            console.error('[AUTH DEBUG] ERROR: STS Exchange Failed', err);
            setError("WIF Exchange Failed: " + (err.response?.data?.error_description || err.message));
          })
          .finally(() => setLoading(false));
      } else {
        console.warn('[AUTH DEBUG] Hash contains id_token key but NO VALUE');
      }
    }
  }, [googleToken]);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const data = await executeSearch(googleToken, query);
      setSearchResult(data);
    } catch (err) {
      setError("Search failed: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem('google_token');
    setGoogleToken(null);
    setIsSpAuthorized(false);
    setSearchResult(null);
  };

  if (!googleToken) {
    return (
      <div className="min-h-screen bg-cave-900 flex flex-col items-center justify-center p-4 text-white">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass p-8 rounded-3xl max-w-md w-full text-center space-y-6"
        >
          <div className="flex justify-center">
            <div className="p-4 bg-sockcop-gold/10 rounded-2xl">
              <ShieldCheck className="w-12 h-12 text-sockcop-gold" />
            </div>
          </div>
          <h1 className="text-3xl font-bold font-inter tracking-tight text-white">Sockcop Search</h1>
          <p className="text-gray-400">Secure GenAI Search grounded in your SharePoint data.</p>
          <button
            onClick={() => window.location.href = getWifLoginUrl()}
            className="w-full bg-[#d4af37] hover:bg-[#b8962e] text-white font-bold py-4 rounded-xl flex items-center justify-center gap-2 transition-all active:scale-95 shadow-lg shadow-[#d4af37]/30"
          >
            <LogIn className="w-5 h-5 text-white" />
            Sign in with Entra ID
          </button>
          <div className="text-xs text-gray-500 uppercase tracking-widest pt-4">Workforce Identity Federated</div>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-cave-900 text-white flex flex-col">
      {/* Header */}
      <nav className="glass sticky top-0 z-50 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-sockcop-gold rounded-lg flex items-center justify-center">
            <ShieldCheck className="w-5 h-5 text-black" />
          </div>
          <span className="text-xl font-bold tracking-tight">Sockcop</span>
        </div>

        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-full text-sm font-medium bg-green-500/10 text-green-400">
            <Database className="w-4 h-4" />
            SharePoint Connected
          </div>
          <button onClick={logout} className="text-sm text-gray-400 hover:text-white underline underline-offset-4">Sign Out</button>
        </div>
      </nav>

      {/* Main Content */}
      <main className="flex-1 max-w-6xl w-full mx-auto p-6 flex flex-col gap-8">
        {/* Search Box */}
        <div className="space-y-4">
          <form onSubmit={handleSearch} className="relative group">
                <input
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Ask Sockcop about your documents..."
                  className="w-full bg-cave-800 border border-white/10 p-6 pr-16 rounded-3xl text-xl focus:ring-2 focus:ring-sockcop-gold outline-none transition-all placeholder:text-gray-400 group-hover:bg-cave-700"
                />
                <button
                  type="submit"
                  disabled={loading}
                  className="absolute right-4 top-1/2 -translate-y-1/2 p-3 bg-sockcop-gold rounded-2xl text-black hover:scale-105 active:scale-95 transition-all disabled:grayscale"
                >
                  {loading ? <Loader2 className="w-6 h-6 animate-spin" /> : <Search className="w-6 h-6" />}
                </button>
              </form>

              <div className="flex gap-2 justify-center">
                {['Recent policies', 'IT Support', 'Holiday Calendar'].map(tag => (
                  <button
                    key={tag}
                    onClick={() => { setQuery(tag); }}
                    className="px-4 py-1.5 bg-white/5 border border-white/10 rounded-full text-sm text-gray-300 hover:bg-white/10 transition-colors"
                  >
                    {tag}
                  </button>
                ))}
              </div>
            </div>

            {/* Results Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 pb-12">
              {/* Answer Column */}
              <div className="lg:col-span-2 space-y-6">
                <AnimatePresence mode="wait">
                  {searchResult && activeCitation !== null ? (
                    <motion.div
                      key="citation-detail"
                      initial={{ opacity: 0, scale: 0.95 }}
                      animate={{ opacity: 1, scale: 1 }}
                      exit={{ opacity: 0, scale: 0.95 }}
                      className="carved p-8 space-y-4"
                    >
                      <button
                        onClick={() => setActiveCitation(null)}
                        className="text-xs font-bold text-gray-500 uppercase tracking-widest hover:text-sockcop-gold transition-colors flex items-center gap-2 mb-4"
                      >
                        <ChevronRight className="w-4 h-4 rotate-180" />
                        Back to AI Summary
                      </button>

                      <div className="flex items-center gap-3 border-b border-white/10 pb-4">
                        <div className="w-10 h-10 bg-sockcop-gold/10 rounded-lg flex items-center justify-center shrink-0">
                          <FileText className="w-5 h-5 text-sockcop-gold" />
                        </div>
                        <div>
                          <h2 className="text-xl font-bold font-inter text-white line-clamp-2">
                            {searchResult.results[activeCitation].document.derivedStructData?.title ||
                              searchResult.results[activeCitation].document.structData?.title ||
                              searchResult.results[activeCitation].document.structData?.name ||
                              searchResult.results[activeCitation].document.name.split('/').pop()}
                          </h2>
                          {(searchResult.results[activeCitation].document.structData?.url || searchResult.results[activeCitation].document.derivedStructData?.link) && (
                            <a
                              href={searchResult.results[activeCitation].document.structData?.url || searchResult.results[activeCitation].document.derivedStructData?.link}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-xs text-sockcop-gold hover:underline mt-1 inline-flex items-center gap-1"
                            >
                              <ExternalLink className="w-3 h-3" />
                              View Original Document
                            </a>
                          )}
                        </div>
                      </div>

                      <div className="prose prose-invert max-w-none prose-p:text-gray-300 prose-a:text-sockcop-gold hover:prose-a:text-[#d4af37]">
                        {(() => {
                          const doc = searchResult.results[activeCitation].document;
                          // snippets normally come in derivedStructData.snippets
                          const snippets = doc.derivedStructData?.snippets || [];
                          const extractiveAnswers = doc.derivedStructData?.extractiveAnswers || [];
                          const fallbackHtml = doc.structData?.snippet || doc.structData?.content || "No detailed snippet available for this section.";

                          if (snippets.length > 0) {
                            return snippets.map((snip, idx) => (
                              <div key={idx} className="bg-white/5 p-4 rounded-xl border border-white/5 mb-4 last:mb-0">
                                <div dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(snip.snippet) }} />
                              </div>
                            ));
                          } else if (extractiveAnswers.length > 0) {
                            return extractiveAnswers.map((answer, idx) => (
                              <div key={`ans-${idx}`} className="bg-white/5 p-4 rounded-xl border border-white/5 mb-4 last:mb-0">
                                <div dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(answer.content) }} />
                              </div>
                            ));
                          } else {
                            return (
                              <div className="bg-white/5 p-4 rounded-xl border border-white/5">
                                <div dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(fallbackHtml) }} />
                              </div>
                            );
                          }
                        })()}
                      </div>
                    </motion.div>
                  ) : searchResult && (
                    <motion.div
                      key="result"
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="carved p-8 space-y-4 leading-relaxed"
                    >
                      <div className="text-xs font-mono text-sockcop-gold flex items-center gap-2">
                        <Loader2 className="w-3 h-3 animate-pulse" />
                        AI GENERATED ANSWER
                      </div>
                      <div className="text-lg text-gray-100 whitespace-pre-wrap">
                        {searchResult.answer || searchResult.summary?.summaryText || "I couldn't find a specific answer, but here is what I found in the documents."}
                      </div>
                    </motion.div>
                  )}
                  {error && (
                    <motion.div className="bg-red-500/20 border border-red-500/50 p-4 rounded-xl text-red-200 flex gap-3">
                      <AlertCircle className="shrink-0" />
                      {error}
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>

              {/* Citations Sidebar */}
              <div className="space-y-4">
                <h3 className="text-xs font-bold text-gray-500 uppercase tracking-widest flex items-center gap-2">
                  <FileText className="w-4 h-4" />
                  Grounded Sources
                </h3>
                <div className="space-y-3">
                  {searchResult?.results?.map((res, i) => (
                    <motion.div
                      key={i}
                      initial={{ opacity: 0, x: 20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: i * 0.1 }}
                      className={`glass p-4 rounded-2xl cursor-pointer transition-all hover:bg-white/5 group border-2 ${activeCitation === i ? 'border-sockcop-gold' : 'border-transparent'}`}
                      onClick={() => setActiveCitation(i)}
                    >
                      <div className="flex justify-between items-start mb-2">
                        <span className="text-xs bg-sockcop-gold/10 text-sockcop-gold px-2 py-0.5 rounded uppercase font-bold">
                          DOC {i + 1}
                        </span>
                        <ChevronRight className="w-4 h-4 text-gray-600 group-hover:text-white" />
                      </div>
                      <h4 className="font-semibold text-sm line-clamp-1 group-hover:text-sockcop-gold transition-colors">
                        {res.document.derivedStructData?.title ||
                          res.document.structData?.title ||
                          res.document.structData?.name ||
                          res.document.name.split('/').pop()}
                      </h4>
                      <p className="text-xs text-gray-500 mt-2 line-clamp-3">
                        {res.document.derivedStructData?.snippets?.[0]?.snippet
                          ? DOMPurify.sanitize(res.document.derivedStructData.snippets[0].snippet).replace(/<[^>]+>/g, '')
                          : res.document.structData?.snippet
                            ? DOMPurify.sanitize(res.document.structData.snippet).replace(/<[^>]+>/g, '')
                            : "Click to see details..."}
                      </p>
                    </motion.div>
                  ))}

                  {!searchResult && !loading && (
                    <div className="border border-white/5 border-dashed rounded-2xl p-10 text-center text-gray-600">
                      Citations will appear here after search
                    </div>
                  )}

                  {loading && (
                    <div className="space-y-3">
                      {[1, 2, 3].map(i => (
                        <div key={i} className="glass p-4 rounded-2xl animate-pulse">
                          <div className="h-4 bg-white/5 w-1/2 mb-3 rounded" />
                          <div className="h-3 bg-white/5 w-full mb-1 rounded" />
                          <div className="h-3 bg-white/5 w-3/4 rounded" />
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
        </div>
      </main>
      <footer className="glass border-t border-white/5 py-3 px-6 text-xs text-gray-500 flex justify-between items-center">
        <div className="flex gap-4">
          <span>Project: {CONFIG.PROJECT_NUMBER}</span>
          <span>Location: {CONFIG.LOCATION}</span>
        </div>
        {error && (
          <div className="text-red-400 font-bold animate-pulse flex items-center gap-1">
            <AlertCircle className="w-3 h-3" />
            AUTH ERROR DETECTED
          </div>
        )}
        <div className="text-sockcop-gold font-mono">SOCKCOP CORE v1.0 [GROUNDED]</div>
      </footer>
    </div>
  );
}

export default App;
