import { useEffect, useRef, useState } from 'react';
import { ChevronLeft, ChevronRight, ExternalLink, FileText, Minus, Plus, X } from 'lucide-react';
import * as pdfjsLib from 'pdfjs-dist';
// Bundle the worker as a module URL — Vite resolves this at build time so we
// don't have to copy pdf.worker.mjs into /public.
import pdfWorkerUrl from 'pdfjs-dist/build/pdf.worker.min.mjs?url';

// Configure worker once per module load. PDF.js v5+ uses module workers.
pdfjsLib.GlobalWorkerOptions.workerSrc = pdfWorkerUrl as string;

export interface DrawerSource {
  title: string;
  url: string;
  snippet: string;
  page?: number;
}

// ─────────────────────────────────────────────────────────────────────────────
// PDF snippet highlight helpers
// ─────────────────────────────────────────────────────────────────────────────

interface PdfTextItem {
  str: string;
  transform: number[]; // [a, b, c, d, e, f]
  width: number;
  height: number;
}

interface HighlightRect {
  /** Canvas-space (CSS px) bounding box. */
  left: number;
  top: number;
  width: number;
  height: number;
}

/** Strip Discovery Engine ellipsis tokens, collapse whitespace, lowercase. */
function normalizeForMatch(text: string): string {
  return text
    .replace(/<ddd\s*\/?>/gi, ' ')
    .replace(/[‘’]/g, "'")
    .replace(/[“”]/g, '"')
    .replace(/\s+/g, ' ')
    .toLowerCase()
    .trim();
}

/** Split into word tokens (letters/digits only — strip punctuation). */
function tokenize(text: string): string[] {
  const norm = normalizeForMatch(text);
  if (!norm) return [];
  // Match word-ish runs; keeps numbers and apostrophes inside words.
  const matches = norm.match(/[a-z0-9]+(?:'[a-z0-9]+)?/g);
  return matches ?? [];
}

/**
 * Find the cited snippet inside a page's text items.
 *
 * Strategy: build a flat token list across all page text items (remembering
 * which item each token came from). Build the snippet token list. Slide a
 * 4-gram window across the snippet; for each window, look for matches in the
 * page tokens. From each match, greedily expand forward & backward as long
 * as tokens keep matching. Return the longest contiguous run.
 *
 * Returns the set of page-text-item indices that participate in the match,
 * or null if no n-gram of size >= MIN matches.
 */
function findSnippetItemIndices(
  items: PdfTextItem[],
  snippet: string,
): Set<number> | null {
  const NGRAM = 4;
  const snippetTokens = tokenize(snippet);
  if (snippetTokens.length < NGRAM) return null;

  // Build flat page tokens with backref to item index.
  const pageTokens: string[] = [];
  const pageTokenItem: number[] = [];
  for (let i = 0; i < items.length; i++) {
    const toks = tokenize(items[i].str);
    for (const t of toks) {
      pageTokens.push(t);
      pageTokenItem.push(i);
    }
  }
  if (pageTokens.length < NGRAM) return null;

  // Index page n-grams -> list of starting positions.
  const pageNgramIdx = new Map<string, number[]>();
  for (let i = 0; i + NGRAM <= pageTokens.length; i++) {
    const key = pageTokens.slice(i, i + NGRAM).join(' ');
    const arr = pageNgramIdx.get(key);
    if (arr) arr.push(i);
    else pageNgramIdx.set(key, [i]);
  }

  let bestStart = -1;
  let bestEnd = -1; // exclusive
  let bestLen = 0;

  for (let s = 0; s + NGRAM <= snippetTokens.length; s++) {
    const key = snippetTokens.slice(s, s + NGRAM).join(' ');
    const hits = pageNgramIdx.get(key);
    if (!hits) continue;
    for (const p of hits) {
      // Greedy expand forward
      let sf = s + NGRAM;
      let pf = p + NGRAM;
      while (sf < snippetTokens.length && pf < pageTokens.length && snippetTokens[sf] === pageTokens[pf]) {
        sf++;
        pf++;
      }
      // Greedy expand backward
      let sb = s - 1;
      let pb = p - 1;
      while (sb >= 0 && pb >= 0 && snippetTokens[sb] === pageTokens[pb]) {
        sb--;
        pb--;
      }
      const startP = pb + 1;
      const endP = pf; // exclusive
      const runLen = endP - startP;
      if (runLen > bestLen) {
        bestLen = runLen;
        bestStart = startP;
        bestEnd = endP;
      }
    }
  }

  if (bestLen < NGRAM || bestStart < 0) return null;

  const itemIndices = new Set<number>();
  for (let i = bestStart; i < bestEnd; i++) {
    itemIndices.add(pageTokenItem[i]);
  }
  return itemIndices;
}

/**
 * Convert a PDF.js text item to a CSS-pixel rect on the canvas.
 *
 * The text item carries a transform [a, b, c, d, e, f] giving its baseline
 * origin in PDF user space (with the font size baked in to a/d). We pass
 * (e, f) through `viewport.convertToViewportPoint` to get the device-pixel
 * baseline-left point, then convert back to CSS pixels by dividing by dpr.
 *
 * Width/height come from the item itself (PDF user space) — we scale them
 * by the viewport scale to get device px, then divide by dpr.
 *
 * Note: `convertToViewportPoint` already accounts for page rotation +
 * the viewport's flipped y-axis, so the returned y is the top-left of
 * the glyph row (approximately) in viewport space.
 */
function itemToCanvasRect(
  item: PdfTextItem,
  viewport: {
    convertToViewportPoint: (x: number, y: number) => [number, number];
    scale: number;
  },
  dpr: number,
): HighlightRect | null {
  const tr = item.transform;
  if (!tr || tr.length < 6) return null;
  const [a, , , d, e, f] = tr;
  // Glyph height in PDF user space ≈ |d| (font size baked into transform).
  const heightUser = Math.abs(d) || Math.abs(a) || item.height || 0;
  const widthUser = item.width || 0;
  // PDF.js puts (e, f) at baseline-left of the text item.
  // We want top-left, so shift up by the glyph height in user space.
  const topLeftUserY = f + heightUser;
  const [vx, vy] = viewport.convertToViewportPoint(e, topLeftUserY);
  const widthDevice = widthUser * viewport.scale;
  const heightDevice = heightUser * viewport.scale;
  // Convert from device px (canvas internal) to CSS px (canvas styled size).
  return {
    left: vx / dpr,
    top: vy / dpr,
    width: widthDevice / dpr,
    height: heightDevice / dpr,
  };
}

/** Merge a set of rects into one enclosing bbox. Returns null if empty. */
function mergeRects(rects: HighlightRect[]): HighlightRect | null {
  if (rects.length === 0) return null;
  let minX = Infinity;
  let minY = Infinity;
  let maxX = -Infinity;
  let maxY = -Infinity;
  for (const r of rects) {
    if (r.left < minX) minX = r.left;
    if (r.top < minY) minY = r.top;
    if (r.left + r.width > maxX) maxX = r.left + r.width;
    if (r.top + r.height > maxY) maxY = r.top + r.height;
  }
  return { left: minX, top: minY, width: maxX - minX, height: maxY - minY };
}

interface Props {
  source: DrawerSource | null;
  onClose: () => void;
  /** MS Entra access token (the same one we send to /api/chat). */
  entraToken?: string | null;
}

/**
 * Right-side slide-in drawer that previews a single source.
 *
 * For SharePoint .pdf URLs we render the actual page via PDF.js, fetched
 * server-side through /api/pdf-proxy (which mints a SharePoint access token
 * via Discovery Engine's connector and pipes the bytes back).
 *
 * If the PDF can't be fetched or decoded, we gracefully fall back to the
 * snippet view so the drawer never looks broken on a single bad source.
 */
export default function SourceDrawer({ source, onClose, entraToken }: Props) {
  const open = !!source;

  const isSharePoint = source?.url?.includes('sharepoint.com') || source?.url?.includes('.sharepoint.');
  const isPdf = !!source?.url && /\.pdf(\?|#|$)/i.test(source.url);
  const host = (() => {
    try {
      return source ? new URL(source.url).host : '';
    } catch {
      return '';
    }
  })();

  // PDF state
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const stageRef = useRef<HTMLDivElement | null>(null);
  const bodyRef = useRef<HTMLDivElement | null>(null);
  // pdfjsLib has no exported type for PDFDocumentProxy at the top level we care about,
  // so just use unknown + narrow at the call sites.
  const pdfDocRef = useRef<{ numPages: number; getPage: (n: number) => Promise<unknown>; destroy: () => void } | null>(null);
  const renderTaskRef = useRef<{ cancel: () => void; promise: Promise<void> } | null>(null);
  const [numPages, setNumPages] = useState<number>(0);
  const [pageNum, setPageNum] = useState<number>(1);
  const [scale, setScale] = useState<number>(1.2);
  const [pdfLoading, setPdfLoading] = useState<boolean>(false);
  const [pdfError, setPdfError] = useState<string | null>(null);
  const [highlightRects, setHighlightRects] = useState<HighlightRect[]>([]);
  // Bumped each time we set a new highlight so the CSS animation re-fires.
  const [highlightKey, setHighlightKey] = useState<number>(0);

  // (1) Load the PDF whenever the source changes (only if it's a PDF + we have a token).
  useEffect(() => {
    let cancelled = false;
    // Reset state on every source switch
    setNumPages(0);
    setPdfError(null);
    setHighlightRects([]);
    if (renderTaskRef.current) {
      try { renderTaskRef.current.cancel(); } catch { /* ignore */ }
      renderTaskRef.current = null;
    }
    if (pdfDocRef.current) {
      try { pdfDocRef.current.destroy(); } catch { /* ignore */ }
      pdfDocRef.current = null;
    }

    if (!source || !isPdf) return;

    setPdfLoading(true);
    const initialPage = Math.max(1, source.page ?? 1);
    setPageNum(initialPage);

    const proxyUrl = `/api/pdf-proxy?url=${encodeURIComponent(source.url)}`;
    const controller = new AbortController();

    (async () => {
      try {
        const resp = await fetch(proxyUrl, {
          headers: entraToken ? { 'X-Entra-Id-Token': entraToken } : {},
          signal: controller.signal,
        });
        if (!resp.ok) {
          throw new Error(`Proxy ${resp.status}`);
        }
        const buf = await resp.arrayBuffer();
        if (cancelled) return;
        const loadingTask = pdfjsLib.getDocument({ data: buf });
        const doc = await loadingTask.promise;
        if (cancelled) {
          try { doc.destroy(); } catch { /* ignore */ }
          return;
        }
        pdfDocRef.current = doc as unknown as typeof pdfDocRef.current;
        setNumPages(doc.numPages);
        // Clamp the requested page in case the cited page > numPages
        setPageNum(prev => Math.min(Math.max(1, prev), doc.numPages));
      } catch (e: unknown) {
        if (cancelled) return;
        const msg = e instanceof Error ? e.message : 'PDF load failed';
        if (!/abort/i.test(msg)) {
          console.error('[SourceDrawer] PDF load error:', e);
          setPdfError(msg);
        }
      } finally {
        if (!cancelled) setPdfLoading(false);
      }
    })();

    return () => {
      cancelled = true;
      controller.abort();
    };
  // We deliberately don't depend on entraToken — token rotation shouldn't
  // re-trigger a PDF refetch. URL change is the trigger.
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [source?.url, isPdf]);

  // (2) Render the current page whenever pageNum / scale changes.
  useEffect(() => {
    const doc = pdfDocRef.current;
    const canvas = canvasRef.current;
    if (!doc || !canvas || !numPages) return;

    let cancelled = false;
    // Clear any previous highlight before we re-render — avoids a stale rect
    // flashing at the wrong scale during the render gap.
    setHighlightRects([]);

    (async () => {
      try {
        const page = await doc.getPage(pageNum) as {
          getViewport: (opts: { scale: number }) => {
            width: number;
            height: number;
            scale: number;
            convertToViewportPoint: (x: number, y: number) => [number, number];
          };
          getTextContent: () => Promise<{ items: PdfTextItem[] }>;
          render: (ctx: { canvasContext: CanvasRenderingContext2D; viewport: unknown; canvas: HTMLCanvasElement }) =>
            { cancel: () => void; promise: Promise<void> };
        };
        if (cancelled) return;
        // Hi-DPI: render at devicePixelRatio for crispness
        const dpr = window.devicePixelRatio || 1;
        const viewport = page.getViewport({ scale: scale * dpr });
        canvas.width = viewport.width;
        canvas.height = viewport.height;
        canvas.style.width = `${viewport.width / dpr}px`;
        canvas.style.height = `${viewport.height / dpr}px`;
        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        // Cancel any in-flight render before starting a new one
        if (renderTaskRef.current) {
          try { renderTaskRef.current.cancel(); } catch { /* ignore */ }
        }
        const task = page.render({ canvasContext: ctx, viewport, canvas });
        renderTaskRef.current = task;
        await task.promise;
        if (cancelled) return;

        // ── Snippet highlight ────────────────────────────────────────────
        // After the page is painted, fetch its text layer and try to locate
        // the cited snippet. Failures are silent — the PDF still shows.
        const snippet = source?.snippet;
        if (!snippet) return;
        let textContent: { items: PdfTextItem[] } | null = null;
        try {
          textContent = await page.getTextContent();
        } catch (err) {
          // Some PDFs (image-only, scanned) have no text layer.
          console.debug('[SourceDrawer] getTextContent failed:', err);
          return;
        }
        if (cancelled || !textContent) return;

        // ── Per-fragment matching ────────────────────────────────────────
        // DE returns snippets stitched from multiple non-contiguous source
        // spans, separated by `<ddd/>` gap markers. Treat each fragment
        // independently so the matcher doesn't lock onto whichever fragment
        // happens to have the longest contiguous run on the page.
        const MIN_FRAGMENT_TOKENS = 4;
        const fragments = snippet
          .split(/<ddd\s*\/?>/gi)
          .map(f => f.trim())
          .filter(f => tokenize(f).length >= MIN_FRAGMENT_TOKENS);
        if (fragments.length === 0) return;

        const paddedRects: HighlightRect[] = [];
        for (const frag of fragments) {
          const matchedIdx = findSnippetItemIndices(textContent.items, frag);
          if (!matchedIdx || matchedIdx.size === 0) continue;
          const fragRects: HighlightRect[] = [];
          for (const idx of matchedIdx) {
            const r = itemToCanvasRect(textContent.items[idx], viewport, dpr);
            if (r) fragRects.push(r);
          }
          const merged = mergeRects(fragRects);
          if (!merged) continue;
          // Add a tiny bit of padding so the highlight doesn't kiss the glyphs.
          paddedRects.push({
            left: merged.left - 4,
            top: merged.top - 3,
            width: merged.width + 8,
            height: merged.height + 6,
          });
        }
        if (paddedRects.length === 0 || cancelled) return;
        setHighlightRects(paddedRects);
        setHighlightKey(k => k + 1);

        // ── Auto-scroll the body so the topmost highlight is centered ────
        // Topmost = smallest `top` value (highest on the page = first cited
        // fragment in document order).
        const topmost = paddedRects.reduce((a, b) => (a.top <= b.top ? a : b));
        requestAnimationFrame(() => {
          const body = bodyRef.current;
          if (!body || !canvas) return;
          const bodyRect = body.getBoundingClientRect();
          const canvasRect = canvas.getBoundingClientRect();
          // canvasRect.top is in viewport coords; convert to body-content
          // coords by adding current scrollTop and subtracting body's top.
          const canvasTopInBody = canvasRect.top - bodyRect.top + body.scrollTop;
          const targetCenter = canvasTopInBody + topmost.top + topmost.height / 2;
          const desiredScroll = targetCenter - body.clientHeight / 2;
          body.scrollTo({
            top: Math.max(0, desiredScroll),
            behavior: 'smooth',
          });
        });
      } catch (e: unknown) {
        const msg = e instanceof Error ? e.message : '';
        if (!/cancel/i.test(msg)) {
          console.error('[SourceDrawer] page render error:', e);
        }
      }
    })();

    return () => { cancelled = true; };
  }, [pageNum, scale, numPages, source?.snippet]);

  // (3) Cleanup on unmount.
  useEffect(() => {
    return () => {
      if (renderTaskRef.current) {
        try { renderTaskRef.current.cancel(); } catch { /* ignore */ }
      }
      if (pdfDocRef.current) {
        try { pdfDocRef.current.destroy(); } catch { /* ignore */ }
      }
    };
  }, []);

  const goPrev = () => setPageNum(p => Math.max(1, p - 1));
  const goNext = () => setPageNum(p => Math.min(numPages || 1, p + 1));
  const zoomIn = () => setScale(s => Math.min(3, +(s + 0.2).toFixed(2)));
  const zoomOut = () => setScale(s => Math.max(0.4, +(s - 0.2).toFixed(2)));

  // The canvas-based PDF view is shown when we successfully loaded a PDF doc.
  // If load failed OR the source isn't a PDF, we show the snippet fallback.
  const showPdf = isPdf && !pdfError && (pdfLoading || numPages > 0);

  return (
    <>
      {open && <div className="source-drawer-backdrop" onClick={onClose} />}
      <aside
        className={`source-drawer ${open ? 'open' : ''} ${showPdf ? 'with-pdf' : ''}`}
        aria-hidden={!open}
      >
        {source && (
          <>
            <div className="source-drawer-header">
              <div className="source-drawer-icon">
                <FileText size={18} />
              </div>
              <div className="source-drawer-title-block">
                <div className="source-drawer-eyebrow">
                  {isSharePoint ? 'SharePoint document' : host || 'Source'}
                  {showPdf && numPages > 0 && (
                    <span className="source-drawer-eyebrow-page">
                      &nbsp;· Page {pageNum} of {numPages}
                    </span>
                  )}
                </div>
                <h3 className="source-drawer-title" title={source.title}>{source.title}</h3>
              </div>
              <button className="source-drawer-close" onClick={onClose} aria-label="Close">
                <X size={18} />
              </button>
            </div>

            {showPdf && (
              <div className="source-drawer-pdf-toolbar">
                <button
                  type="button"
                  className="pdf-tool-btn"
                  onClick={goPrev}
                  disabled={pageNum <= 1 || pdfLoading}
                  aria-label="Previous page"
                  title="Previous page"
                >
                  <ChevronLeft size={14} />
                  <span>Prev</span>
                </button>
                <span className="pdf-page-indicator">
                  {pdfLoading ? '…' : `${pageNum} / ${numPages || '?'}`}
                </span>
                <button
                  type="button"
                  className="pdf-tool-btn"
                  onClick={goNext}
                  disabled={pageNum >= numPages || pdfLoading}
                  aria-label="Next page"
                  title="Next page"
                >
                  <span>Next</span>
                  <ChevronRight size={14} />
                </button>
                <span className="pdf-tool-spacer" />
                <button
                  type="button"
                  className="pdf-tool-btn pdf-tool-icon"
                  onClick={zoomOut}
                  disabled={scale <= 0.4 || pdfLoading}
                  aria-label="Zoom out"
                  title="Zoom out"
                >
                  <Minus size={14} />
                </button>
                <span className="pdf-zoom-indicator">{Math.round(scale * 100)}%</span>
                <button
                  type="button"
                  className="pdf-tool-btn pdf-tool-icon"
                  onClick={zoomIn}
                  disabled={scale >= 3 || pdfLoading}
                  aria-label="Zoom in"
                  title="Zoom in"
                >
                  <Plus size={14} />
                </button>
              </div>
            )}

            <div className="source-drawer-body" ref={bodyRef}>
              {showPdf ? (
                <div className="source-drawer-pdf-stage" ref={stageRef}>
                  {pdfLoading && (
                    <div className="source-drawer-pdf-loading">
                      <div className="claude-spinner" aria-hidden="true" />
                      <span>Loading PDF…</span>
                    </div>
                  )}
                  <div className="source-drawer-pdf-canvas-wrap" style={{ position: 'relative' }}>
                    <canvas
                      ref={canvasRef}
                      className="source-drawer-pdf-canvas"
                      style={{ display: pdfLoading || numPages === 0 ? 'none' : 'block' }}
                    />
                    {highlightRects.length > 0 && !pdfLoading && numPages > 0 && (
                      highlightRects.map((rect, i) => (
                        <div
                          key={`${highlightKey}-${i}`}
                          className="pdf-highlight"
                          style={{
                            left: `${rect.left}px`,
                            top: `${rect.top}px`,
                            width: `${rect.width}px`,
                            height: `${rect.height}px`,
                          }}
                          aria-hidden="true"
                        />
                      ))
                    )}
                  </div>
                </div>
              ) : (
                <>
                  {pdfError && (
                    <div className="source-drawer-pdf-error">
                      Couldn’t load the PDF preview ({pdfError}). Showing the excerpt instead.
                    </div>
                  )}
                  {source.snippet ? (
                    <div className="source-drawer-snippet">
                      <div className="source-drawer-snippet-label">Excerpt</div>
                      <div className="source-drawer-snippet-text">{source.snippet}</div>
                    </div>
                  ) : (
                    <div className="source-drawer-snippet source-drawer-snippet-empty">
                      No preview snippet returned by the index. Open the document to view its full content.
                    </div>
                  )}

                  <div className="source-drawer-meta">
                    <div className="source-drawer-meta-row">
                      <span className="source-drawer-meta-key">Host</span>
                      <span className="source-drawer-meta-val">{host || '—'}</span>
                    </div>
                    <div className="source-drawer-meta-row">
                      <span className="source-drawer-meta-key">URL</span>
                      <a
                        className="source-drawer-meta-val source-drawer-url"
                        href={source.url}
                        target="_blank"
                        rel="noreferrer"
                        title={source.url}
                      >
                        {source.url}
                      </a>
                    </div>
                  </div>
                </>
              )}
            </div>

            <div className="source-drawer-footer">
              <a
                className="source-drawer-open-btn"
                href={source.url}
                target="_blank"
                rel="noreferrer"
              >
                <ExternalLink size={14} />
                {isSharePoint ? 'Open in SharePoint' : 'Open source'}
              </a>
            </div>
          </>
        )}
      </aside>
    </>
  );
}
