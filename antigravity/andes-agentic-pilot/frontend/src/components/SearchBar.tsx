import { useEffect, useRef, useState, useCallback, type KeyboardEvent } from 'react';
import './SearchBar.css';

/* ---------------------------------------------------------------------------
 * SearchBar
 *   Vertex AI Search-backed "navegador" for cajalosandes.cl content.
 *   Pings the FastAPI backend (/api/search) which proxies Discovery Engine.
 *   Shows a dropdown with title / snippet / source link, keyboard-friendly:
 *     - Enter           : submit / open active result
 *     - ArrowDown / Up  : move within results
 *     - Esc             : close dropdown
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

interface ApiResponse {
  results?: SearchResult[];
  totalSize?: number;
  error?: string;
}

export default function SearchBar() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[] | null>(null);
  const [loading, setLoading] = useState(false);
  const [open, setOpen] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeIndex, setActiveIndex] = useState(-1);

  const containerRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  /* Click-outside closes the dropdown. */
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

  const runSearch = useCallback(
    async (q: string) => {
      const trimmed = q.trim();
      if (!trimmed) return;
      setLoading(true);
      setError(null);
      setOpen(true);
      try {
        const res = await fetch(`${API_BASE}/api/search`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ query: trimmed }),
        });
        const data: ApiResponse = await res.json().catch(() => ({}));
        if (!res.ok) {
          throw new Error(data.error || `HTTP ${res.status}`);
        }
        setResults(data.results ?? []);
        setActiveIndex(-1);
      } catch (err) {
        const msg = err instanceof Error ? err.message : 'Error de búsqueda';
        setError(msg);
        setResults([]);
      } finally {
        setLoading(false);
      }
    },
    [],
  );

  function handleKeyDown(e: KeyboardEvent<HTMLInputElement>) {
    if (e.key === 'Enter') {
      e.preventDefault();
      if (activeIndex >= 0 && results && results[activeIndex]?.link) {
        window.open(results[activeIndex].link, '_blank', 'noopener,noreferrer');
        return;
      }
      void runSearch(query);
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

  const showDropdown = open && (loading || error || results !== null);

  return (
    <div className="cla-search" ref={containerRef}>
      <form
        className="cla-search__form"
        role="search"
        onSubmit={(e) => {
          e.preventDefault();
          void runSearch(query);
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
          onFocus={() => results !== null && setOpen(true)}
          onKeyDown={handleKeyDown}
          autoComplete="off"
        />
        {query && (
          <button
            type="button"
            className="cla-search__clear"
            aria-label="Limpiar búsqueda"
            onClick={() => {
              setQuery('');
              setResults(null);
              setOpen(false);
              setError(null);
              inputRef.current?.focus();
            }}
          >
            <span className="material-symbols-outlined" aria-hidden>
              close
            </span>
          </button>
        )}
        <button
          type="submit"
          className="cla-search__submit"
          aria-label="Buscar"
          disabled={loading || query.trim().length === 0}
        >
          {loading ? (
            <span className="cla-search__spinner" aria-hidden />
          ) : (
            <span className="material-symbols-outlined" aria-hidden>
              arrow_forward
            </span>
          )}
        </button>
      </form>

      {showDropdown && (
        <div className="cla-search__dropdown" role="listbox">
          {loading && (
            <div className="cla-search__status">
              <span className="cla-search__spinner cla-search__spinner--lg" aria-hidden />
              <span>Buscando en cajalosandes.cl…</span>
            </div>
          )}

          {!loading && error && (
            <div className="cla-search__status cla-search__status--error">
              <span className="material-symbols-outlined" aria-hidden>error</span>
              <div>
                <strong>No pudimos completar la búsqueda</strong>
                <p>{error}</p>
              </div>
            </div>
          )}

          {!loading && !error && results && results.length === 0 && (
            <div className="cla-search__status">
              <span className="material-symbols-outlined" aria-hidden>search_off</span>
              <span>Sin resultados para "{query}".</span>
            </div>
          )}

          {!loading && !error && results && results.length > 0 && (
            <ul className="cla-search__results">
              {results.map((r, i) => (
                <li
                  key={r.id ?? `${r.title}-${i}`}
                  className={`cla-search__result${i === activeIndex ? ' is-active' : ''}`}
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
                      <span className="material-symbols-outlined" aria-hidden>
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
              Resultados sugeridos por <strong>Vertex AI Search</strong>
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
