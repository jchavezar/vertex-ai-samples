import {
  useEffect,
  useRef,
  useState,
  useCallback,
  type KeyboardEvent,
} from 'react';
import './SearchBar.css';
import AndesiaVoice from './AndesiaVoice/AndesiaVoice';

/* ---------------------------------------------------------------------------
 * SearchBar — AI-native search experience
 *
 *  ┌─────────────────────────────────────────────────────────────────────┐
 *  │  [search icon]  Buscar en cajalosandes.cl…   [mic]  [×]  [→]        │
 *  └─────────────────────────────────────────────────────────────────────┘
 *  ┌─ dropdown ──────────────────────────────────────────────────────────┐
 *  │  ✨  Preguntas sugeridas: ┌─ chip ─┐ ┌─ chip ─┐ ┌─ chip ─┐          │
 *  │                                                                     │
 *  │  ◆  AI Overview (Vertex AI Search + Gemini)                         │
 *  │     Para acceder al Crédito Social… [1] [4] (streaming…)            │
 *  │     ─ Fuentes: [1] Crédito Social  [2] Crédito Universal …          │
 *  │                                                                     │
 *  │  Resultados (8):                                                    │
 *  │     • title / snippet / link                                        │
 *  │     • title / snippet / link                                        │
 *  └─────────────────────────────────────────────────────────────────────┘
 *
 * Backend endpoints:
 *   POST /api/suggest          -> {suggestions:string[]}
 *   POST /api/search           -> {results:[]}
 *   POST /api/search/answer    -> SSE: citations, text..., done
 * -------------------------------------------------------------------------- */

const API_BASE =
  (import.meta.env.VITE_API_BASE as string | undefined) ?? 'http://localhost:8000';

interface SearchResult {
  id?: string;
  title: string;
  snippet?: string;
  link?: string;
  favicon?: string;
}

interface AnswerCitation {
  n: number;
  title: string;
  link: string;
}

const DEBOUNCE_MS = 450;
const ANSWER_IDLE_MS = 800;
const MIN_QUERY_LEN = 3;

export default function SearchBar() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[] | null>(null);
  const [loadingResults, setLoadingResults] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [open, setOpen] = useState(false);
  const [activeIndex, setActiveIndex] = useState(-1);

  const [suggestions, setSuggestions] = useState<string[]>([]);

  const [aiText, setAiText] = useState('');
  const [aiCitations, setAiCitations] = useState<AnswerCitation[]>([]);
  const [aiStreaming, setAiStreaming] = useState(false);

  const [voiceOpen, setVoiceOpen] = useState(false);

  const containerRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const debounceRef = useRef<number | null>(null);
  const answerIdleRef = useRef<number | null>(null);
  const searchAbortRef = useRef<AbortController | null>(null);
  const suggestAbortRef = useRef<AbortController | null>(null);
  const answerAbortRef = useRef<AbortController | null>(null);

  /* close on outside click */
  useEffect(() => {
    function onDocClick(e: MouseEvent) {
      if (!containerRef.current) return;
      if (!containerRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    document.addEventListener('mousedown', onDocClick);
    return () => document.removeEventListener('mousedown', onDocClick);
  }, []);

  /* ─── network helpers ─────────────────────────────────────────────── */

  const runResults = useCallback(async (q: string) => {
    searchAbortRef.current?.abort();
    const ctl = new AbortController();
    searchAbortRef.current = ctl;
    setLoadingResults(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/api/search`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: q }),
        signal: ctl.signal,
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(data.error || `HTTP ${res.status}`);
      setResults(data.results ?? []);
      setActiveIndex(-1);
    } catch (err) {
      if ((err as Error).name === 'AbortError') return;
      setError(err instanceof Error ? err.message : 'Error de búsqueda');
      setResults([]);
    } finally {
      setLoadingResults(false);
    }
  }, []);

  const runSuggest = useCallback(async (partial: string) => {
    suggestAbortRef.current?.abort();
    const ctl = new AbortController();
    suggestAbortRef.current = ctl;
    try {
      const res = await fetch(`${API_BASE}/api/suggest`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ partial, max: 3 }),
        signal: ctl.signal,
      });
      const data = await res.json().catch(() => ({}));
      const list = (data.suggestions as string[]) ?? [];
      setSuggestions(list.filter((s) => s && s.trim().length > 0));
    } catch {
      /* silent — suggestions are best-effort */
    }
  }, []);

  const runAnswer = useCallback(async (q: string) => {
    answerAbortRef.current?.abort();
    const ctl = new AbortController();
    answerAbortRef.current = ctl;
    setAiText('');
    setAiCitations([]);
    setAiStreaming(true);
    try {
      const res = await fetch(`${API_BASE}/api/search/answer`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: q }),
        signal: ctl.signal,
      });
      if (!res.ok || !res.body) throw new Error(`HTTP ${res.status}`);
      const reader = res.body.getReader();
      const dec = new TextDecoder();
      let buf = '';
      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        buf += dec.decode(value, { stream: true });
        const frames = buf.split('\n\n');
        buf = frames.pop() ?? '';
        for (const frame of frames) {
          const line = frame.split('\n').find((l) => l.startsWith('data:'));
          if (!line) continue;
          let evt: Record<string, unknown> = {};
          try { evt = JSON.parse(line.slice(5).trim()); } catch { continue; }
          if (evt.type === 'citations') {
            setAiCitations((evt.items as AnswerCitation[]) ?? []);
          } else if (evt.type === 'text') {
            setAiText((s) => s + (evt.text as string));
          } else if (evt.type === 'done') {
            setAiStreaming(false);
          } else if (evt.type === 'error') {
            setAiStreaming(false);
          }
        }
      }
      setAiStreaming(false);
    } catch (err) {
      if ((err as Error).name === 'AbortError') return;
      setAiStreaming(false);
    }
  }, []);

  /* ─── debounced live-as-you-type ─────────────────────────────────── */
  useEffect(() => {
    if (debounceRef.current) window.clearTimeout(debounceRef.current);
    if (answerIdleRef.current) window.clearTimeout(answerIdleRef.current);
    // Cancel any in-flight AI Overview from a previous keystroke. The user
    // is still typing — we only want to commit to runAnswer after they stop.
    answerAbortRef.current?.abort();
    setAiStreaming(false);

    const trimmed = query.trim();
    if (trimmed.length === 0) {
      // restore default popular suggestions
      void runSuggest('');
      setResults(null);
      setAiText('');
      setAiCitations([]);
      setError(null);
      return;
    }
    debounceRef.current = window.setTimeout(() => {
      // suggestions on every keystroke pause (cheap)
      void runSuggest(trimmed);
      // Search results render as you type (cached + cheap).
      if (trimmed.length >= MIN_QUERY_LEN) {
        setOpen(true);
        void runResults(trimmed);
      }
    }, DEBOUNCE_MS);
    // AI Overview is expensive — only fire after the user has been idle a
    // full ANSWER_IDLE_MS. Re-typing cancels and re-arms this timer above.
    if (trimmed.length >= MIN_QUERY_LEN) {
      answerIdleRef.current = window.setTimeout(() => {
        void runAnswer(trimmed);
      }, ANSWER_IDLE_MS);
    }
    return () => {
      if (debounceRef.current) window.clearTimeout(debounceRef.current);
      if (answerIdleRef.current) window.clearTimeout(answerIdleRef.current);
    };
  }, [query, runSuggest, runResults, runAnswer]);

  /* ─── keyboard ─── */
  function handleKeyDown(e: KeyboardEvent<HTMLInputElement>) {
    if (e.key === 'Enter') {
      e.preventDefault();
      if (activeIndex >= 0 && results && results[activeIndex]?.link) {
        window.open(results[activeIndex].link!, '_blank', 'noopener,noreferrer');
        return;
      }
      const q = query.trim();
      if (q.length >= MIN_QUERY_LEN) {
        setOpen(true);
        void runResults(q);
        void runAnswer(q);
      }
    } else if (e.key === 'Escape') {
      setOpen(false);
      setActiveIndex(-1);
      inputRef.current?.blur();
    } else if (e.key === 'ArrowDown') {
      if (!results || results.length === 0) return;
      e.preventDefault();
      setActiveIndex((i) => (i + 1) % results.length);
    } else if (e.key === 'ArrowUp') {
      if (!results || results.length === 0) return;
      e.preventDefault();
      setActiveIndex((i) => (i <= 0 ? results.length - 1 : i - 1));
    }
  }

  /* ─── render helpers ─── */

  /** convert "[1]" / "[2]" markers in the streamed answer into clickable
   * superscript chips that scroll/open the matching citation. */
  function renderAnswer(text: string) {
    if (!text) return null;
    const parts: (string | { n: number })[] = [];
    const re = /\[(\d+)\]/g;
    let last = 0;
    let m: RegExpExecArray | null;
    while ((m = re.exec(text)) !== null) {
      if (m.index > last) parts.push(text.slice(last, m.index));
      parts.push({ n: parseInt(m[1], 10) });
      last = m.index + m[0].length;
    }
    if (last < text.length) parts.push(text.slice(last));
    return parts.map((p, i) => {
      if (typeof p === 'string') return <span key={i}>{p}</span>;
      const cit = aiCitations.find((c) => c.n === p.n);
      return (
        <a
          key={i}
          className="cla-search__cite"
          href={cit?.link || '#'}
          target="_blank"
          rel="noopener noreferrer"
          title={cit?.title || `Fuente ${p.n}`}
        >
          {p.n}
        </a>
      );
    });
  }

  const showDropdown =
    open &&
    (loadingResults ||
      error ||
      results !== null ||
      suggestions.length > 0 ||
      aiText.length > 0 ||
      aiStreaming);

  return (
    <div className="cla-search" ref={containerRef}>
      <form
        className="cla-search__form"
        role="search"
        onSubmit={(e) => {
          e.preventDefault();
          const q = query.trim();
          if (q.length >= MIN_QUERY_LEN) {
            setOpen(true);
            void runResults(q);
            void runAnswer(q);
          }
        }}
      >
        <span className="material-symbols-outlined cla-search__icon" aria-hidden>
          search
        </span>
        <input
          ref={inputRef}
          type="search"
          className="cla-search__input"
          placeholder="Buscar en cajalosandes.cl..."
          aria-label="Buscar contenido en Caja Los Andes"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onFocus={() => setOpen(true)}
          onKeyDown={handleKeyDown}
          autoComplete="off"
        />

        <button
          type="button"
          className="cla-search__mic"
          aria-label="Hablar con Andesia"
          title="Hablar con Andesia (voz natural)"
          onClick={() => setVoiceOpen(true)}
        >
          <span className="material-symbols-outlined" aria-hidden>mic</span>
        </button>

        {query && (
          <button
            type="button"
            className="cla-search__clear"
            aria-label="Limpiar búsqueda"
            onClick={() => {
              setQuery('');
              setResults(null);
              setAiText('');
              setAiCitations([]);
              setError(null);
              setOpen(false);
              inputRef.current?.focus();
            }}
          >
            <span className="material-symbols-outlined" aria-hidden>close</span>
          </button>
        )}
        <button
          type="submit"
          className="cla-search__submit"
          aria-label="Buscar"
          disabled={loadingResults || query.trim().length === 0}
        >
          {loadingResults ? (
            <span className="cla-search__spinner" aria-hidden />
          ) : (
            <span className="material-symbols-outlined" aria-hidden>arrow_forward</span>
          )}
        </button>
      </form>

      {showDropdown && (
        <div className="cla-search__dropdown" role="listbox">
          {/* ─── Predicted Questions ─── */}
          {suggestions.length > 0 && (
            <div className="cla-search__chips">
              <span
                className="material-symbols-outlined cla-search__chips-icon"
                aria-hidden
              >
                auto_awesome
              </span>
              <div className="cla-search__chips-row">
                {suggestions.map((s) => (
                  <button
                    key={s}
                    type="button"
                    className="cla-search__chip"
                    onClick={() => {
                      setQuery(s);
                      setOpen(true);
                      void runResults(s);
                      void runAnswer(s);
                    }}
                  >
                    {s}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* ─── AI Overview ─── */}
          {(aiText || aiStreaming) && (
            <div className="cla-search__overview">
              <div className="cla-search__overview-head">
                <span className="cla-search__overview-badge">
                  <span className="material-symbols-outlined" aria-hidden>
                    psychology
                  </span>
                  AI Overview
                </span>
                <span className="cla-search__overview-meta">
                  Vertex AI Search + Gemini
                </span>
              </div>
              {aiStreaming && !aiText ? (
                <div className="cla-search__overview-thinking">
                  <span className="cla-search__claude-spinner" aria-hidden />
                  <span className="cla-search__sweep-text">
                    Sintetizando respuesta…
                  </span>
                </div>
              ) : (
                <p className="cla-search__overview-text">
                  {renderAnswer(aiText)}
                  {aiStreaming && <span className="cla-search__caret" aria-hidden />}
                </p>
              )}
              {aiCitations.length > 0 && (
                <div className="cla-search__overview-cites">
                  <span className="cla-search__overview-cites-label">Fuentes:</span>
                  {aiCitations.map((c) => (
                    <a
                      key={c.n}
                      href={c.link}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="cla-search__cite-pill"
                    >
                      <span className="cla-search__cite-num">{c.n}</span>
                      {c.title}
                    </a>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* ─── Result list ─── */}
          {loadingResults && !results && (
            <div className="cla-search__status">
              <span
                className="cla-search__spinner cla-search__spinner--lg"
                aria-hidden
              />
              <span>Buscando en cajalosandes.cl…</span>
            </div>
          )}

          {!loadingResults && error && (
            <div className="cla-search__status cla-search__status--error">
              <span className="material-symbols-outlined" aria-hidden>error</span>
              <div>
                <strong>No pudimos completar la búsqueda</strong>
                <p>{error}</p>
              </div>
            </div>
          )}

          {!loadingResults && !error && results && results.length === 0 && (
            <div className="cla-search__status">
              <span className="material-symbols-outlined" aria-hidden>search_off</span>
              <span>Sin resultados para "{query}".</span>
            </div>
          )}

          {/* Resultados: NUNCA gateados por loadingResults ni por aiStreaming.
           * Apenas /api/search vuelve, se muestran. Si hay un fetch nuevo en
           * vuelo, los anteriores siguen visibles para que el usuario pueda
           * leer/click sin esperar al AI Overview. */}
          {!error && results && results.length > 0 && (
            <ul
              className={`cla-search__results${
                loadingResults ? ' is-refreshing' : ''
              }`}
            >
              {results.map((r, i) => (
                <li
                  key={r.id ?? `${r.title}-${i}`}
                  className={`cla-search__result${
                    i === activeIndex ? ' is-active' : ''
                  }`}
                  role="option"
                  aria-selected={i === activeIndex}
                >
                  <a
                    href={r.link || '#'}
                    target="_blank"
                    rel="noopener noreferrer"
                    onMouseEnter={() => setActiveIndex(i)}
                  >
                    <div className="cla-search__result-head">
                      {r.favicon ? (
                        <img
                          className="cla-search__favicon"
                          src={r.favicon}
                          alt=""
                          aria-hidden
                        />
                      ) : (
                        <span
                          className="material-symbols-outlined cla-search__result-icon"
                          aria-hidden
                        >
                          article
                        </span>
                      )}
                      <h4 className="cla-search__result-title">{r.title}</h4>
                    </div>
                    {r.snippet && (
                      <p
                        className="cla-search__result-snippet"
                        dangerouslySetInnerHTML={{ __html: r.snippet }}
                      />
                    )}
                    <span className="cla-search__result-cta">
                      Ver en cajalosandes.cl
                      <span
                        className="material-symbols-outlined"
                        aria-hidden
                      >
                        chevron_right
                      </span>
                    </span>
                  </a>
                </li>
              ))}
            </ul>
          )}

          <div className="cla-search__footer">
            <span>
              Resultados sugeridos por <strong>Vertex AI Search</strong> ·
              respuesta sintetizada por <strong>Gemini 3 Flash</strong>
            </span>
          </div>
        </div>
      )}

      <AndesiaVoice
        open={voiceOpen}
        onClose={() => setVoiceOpen(false)}
        seedText={query}
      />
    </div>
  );
}
