/* ===========================================================
   envato vibe-search v2 — app.js (vanilla)
   Talks to:
     GET  /api/health
     GET  /api/search?q=&modality=&limit=&tempo=&length=&color=
     POST /api/search/sounds-like      (multipart: file)
     POST /api/image-to-anything       (multipart: file)
     GET  /api/segment/{datapoint_id}
     POST /api/upload                  (multipart: file)
     GET  /api/stats
     GET  /api/uploads/recent?limit=
   =========================================================== */

(() => {
'use strict';

// ----- helpers -----
const $  = (sel, root = document) => root.querySelector(sel);
const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));
const el = (tag, attrs = {}, ...children) => {
  const n = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === 'class') n.className = v;
    else if (k === 'style') n.style.cssText = v;
    else if (k === 'dataset') for (const [dk, dv] of Object.entries(v)) n.dataset[dk] = dv;
    else if (k.startsWith('on') && typeof v === 'function') n.addEventListener(k.slice(2), v);
    else if (v === true) n.setAttribute(k, '');
    else if (v !== false && v != null) n.setAttribute(k, v);
  }
  for (const c of children.flat()) {
    if (c == null || c === false) continue;
    n.appendChild(c.nodeType ? c : document.createTextNode(String(c)));
  }
  return n;
};
const escapeHtml = s => String(s ?? '').replace(/[&<>"']/g, c => ({
  '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'
}[c]));
const debounce = (fn, ms) => {
  let t; return (...args) => { clearTimeout(t); t = setTimeout(() => fn(...args), ms); };
};
const fmtMs = n => (n == null ? '—' : `${Math.round(n)}ms`);
const fmtNum = n => (n == null ? '—' : Number(n).toLocaleString());
const fmtTime = s => {
  if (s == null) return '';
  const m = Math.floor(s / 60), sec = Math.floor(s % 60);
  return `${m}:${String(sec).padStart(2, '0')}`;
};
const clampScore = s => Math.max(0, Math.min(1, Number(s) || 0));

// ----- state -----
const state = {
  query: '',
  modality: 'all',
  filters: { tempo: '', length: '', color: '' },
  refineActive: new Set(),
  lastResp: null,
  inflight: null,
  bigText: false,
  audioPlayer: null,        // single shared <audio> for hover/play
  audioPlayingRow: null,    // currently-playing row element
  audioRaf: null,           // RAF id for waveform progress
};

// ===========================================================
// CUSTOM CURSOR (desktop, pointer:fine only)
// ===========================================================
const cursor = $('#cursor');
const cursorLabel = $('#cursorLabel');
const supportsFine = window.matchMedia('(pointer: fine)').matches;

if (supportsFine && cursor) {
  document.body.classList.add('has-cursor');
  let cx = 0, cy = 0, tx = 0, ty = 0;
  let raf;
  const loop = () => {
    cx += (tx - cx) * 0.35;
    cy += (ty - cy) * 0.35;
    cursor.style.transform = `translate3d(${cx}px, ${cy}px, 0)`;
    raf = requestAnimationFrame(loop);
  };
  raf = requestAnimationFrame(loop);

  document.addEventListener('mousemove', e => { tx = e.clientX; ty = e.clientY; }, { passive: true });
  document.addEventListener('mousedown', () => cursor.classList.add('is-down'));
  document.addEventListener('mouseup',   () => cursor.classList.remove('is-down'));

  // hover state detection — uses [data-cursor] and a few fallbacks
  document.addEventListener('mouseover', e => {
    const t = e.target.closest?.('[data-cursor], a, button, .card, .audiorow, .qchip, .cattile, .refchip, .reel-arrow, input[type=text], .swatch, .topnav__item');
    let kind = '';
    if (t) {
      const dc = t.dataset?.cursor;
      if (dc) kind = dc;
      else if (t.matches('.card--video')) kind = 'play';
      else if (t.matches('.card')) kind = 'open';
      else if (t.matches('.audiorow')) kind = 'listen';
      else if (t.matches('.reel-arrow--prev')) kind = 'left';
      else if (t.matches('.reel-arrow--next')) kind = 'right';
      else if (t.matches('input[type=text]')) kind = 'text';
      else if (t.matches('a, button, .qchip, .cattile, .refchip, .swatch, .topnav__item')) kind = 'link';
    }
    setCursorState(kind);
  });
  document.addEventListener('mouseout', e => {
    const to = e.relatedTarget;
    if (!to || !(to instanceof Element)) setCursorState('');
  });
}
function setCursorState(kind) {
  if (!cursor) return;
  const all = ['is-link','is-open','is-play','is-listen','is-left','is-right','is-text'];
  cursor.classList.remove(...all);
  cursorLabel.textContent = '';
  if (!kind) return;
  cursor.classList.add(`is-${kind}`);
  if (kind === 'open') cursorLabel.textContent = 'view';
  else if (kind === 'listen') cursorLabel.textContent = 'listen';
}

// ===========================================================
// HEADER & SEARCH PILL
// ===========================================================
const searchInput   = $('#searchInput');
const searchClear   = $('#searchClear');
const searchGo      = $('#searchGo');
const catBtn        = $('#catBtn');
const catLabel      = $('#catLabel');
const catMenu       = $('#catMenu');
const suggest       = $('#suggest');
const suggestList   = $('#suggestList');
const suggestTiming = $('#suggestTiming');

const MODALITIES = {
  all:     'All Items',
  photo:   'Photos',
  video:   'Video',
  audio:   'Audio (Music + SFX)',
  graphic: 'Graphics',
};

function setModality(mod, fromUI = true) {
  state.modality = mod;
  catLabel.textContent = MODALITIES[mod] || 'All Items';
  $$('.cat-menu button').forEach(b => b.classList.toggle('is-active', b.dataset.mod === mod));
  $$('input[name="modality"]').forEach(i => { i.checked = i.value === mod; });
  if (fromUI && state.query) runSearch({ showLoader: true });
}

catBtn.addEventListener('click', e => {
  e.stopPropagation();
  const open = !catMenu.hasAttribute('hidden');
  if (open) catMenu.setAttribute('hidden', '');
  else catMenu.removeAttribute('hidden');
});
$$('.cat-menu button').forEach(btn => {
  btn.addEventListener('click', e => {
    e.stopPropagation();
    setModality(btn.dataset.mod);
    catMenu.setAttribute('hidden', '');
  });
});
document.addEventListener('click', () => catMenu.setAttribute('hidden', ''));

searchInput.addEventListener('input', () => {
  const v = searchInput.value.trim();
  searchClear.hidden = v.length === 0;
  state.query = v;
  if (v.length === 0) { hideSuggest(); return; }
  triggerSuggest(v);
});
searchInput.addEventListener('focus', () => {
  if (state.query) triggerSuggest(state.query);
});
searchInput.addEventListener('keydown', e => {
  if (e.key === 'Enter') { hideSuggest(); runSearch({ showLoader: true }); }
  if (e.key === 'Escape') { hideSuggest(); }
});
searchClear.addEventListener('click', () => {
  searchInput.value = '';
  state.query = '';
  searchClear.hidden = true;
  hideSuggest();
  showLanding();
});
searchGo.addEventListener('click', () => { hideSuggest(); runSearch({ showLoader: true }); });

document.addEventListener('click', e => {
  if (!suggest.contains(e.target) && e.target !== searchInput) hideSuggest();
});

function hideSuggest() { suggest.hidden = true; suggestList.innerHTML = ''; }

// Suggest: derives from live /api/search top-k grouped by modality
const triggerSuggest = debounce(async q => {
  if (!q) return;
  try {
    const t0 = performance.now();
    const resp = await fetchSearch({ q, modality: 'all', limit: 8, suggestOnly: true });
    if (!resp) return;
    renderSuggest(q, resp, performance.now() - t0);
  } catch (err) {
    console.warn('suggest failed', err);
  }
}, 250);

function renderSuggest(q, resp, wallMs) {
  const grouped = resp.grouped || {};
  const order = [
    ['photo', 'Photos'],
    ['video', 'Video'],
    ['audio_music', 'Music'],
    ['audio_sfx', 'SFX'],
    ['graphic', 'Graphics'],
  ];
  const items = [];
  for (const [key, label] of order) {
    const arr = grouped[key] || [];
    if (!arr.length) continue;
    items.push({ q, label, count: arr.length, samples: arr.slice(0, 3) });
  }
  if (items.length === 0) { hideSuggest(); return; }

  suggestList.innerHTML = '';
  for (const it of items) {
    const li = el('li', { class: 'suggest__item', dataset: { q: it.q, mod: modKeyToFilter(it.label), cursor: 'link' } },
      el('span', { class: 'suggest__item-q' }, mkSuggestText(it.q, it.label, it.count)),
      el('span', { class: 'suggest__item-thumbs' },
        ...it.samples.map(s => {
          const sp = el('span');
          if (s.thumbnail_url) sp.style.backgroundImage = `url("${s.thumbnail_url}")`;
          return sp;
        })
      ),
      el('span', { class: 'suggest__item-mod' }, it.label),
    );
    li.addEventListener('click', () => {
      const targetMod = modKeyToFilter(it.label);
      setModality(targetMod, false);
      hideSuggest();
      runSearch({ showLoader: true });
    });
    suggestList.appendChild(li);
  }
  suggestTiming.textContent = `embed ${fmtMs(resp.query_embed_ms)} · search ${fmtMs(resp.vs_search_ms)} · total ${fmtMs(resp.total_ms)} (suggest ${fmtMs(wallMs)})`;
  suggest.hidden = false;
}
function mkSuggestText(q, label, count) {
  const span = el('span');
  span.innerHTML = `<em>${escapeHtml(q)}</em> in <b>${escapeHtml(label)}</b> <span style="color:#9AA0A8">· ${count}+</span>`;
  return span;
}
function modKeyToFilter(label) {
  if (label === 'Photos') return 'photo';
  if (label === 'Video') return 'video';
  if (label === 'Music' || label === 'SFX') return 'audio';
  if (label === 'Graphics') return 'graphic';
  return 'all';
}

// ===========================================================
// LANDING / RESULTS toggle
// ===========================================================
const landing    = $('#landing');
const results    = $('#results');
const resultCols = $('#resultCols');
const resultsTitle = $('#resultsTitle');
const resultsSub   = $('#resultsSub');
const refineBar    = $('#refineBar');
const rescueBanner = $('#rescueBanner');
const loader       = $('#loader');

function showLanding() {
  landing.hidden = false;
  results.hidden = true;
  state.lastResp = null;
  stopAudio();
  const vsRoot = document.getElementById('vibeSliderRoot');
  if (vsRoot) vsRoot.style.display = 'none';
}
function showResults() {
  landing.hidden = true;
  results.hidden = false;
  const vsRoot = document.getElementById('vibeSliderRoot');
  if (vsRoot) vsRoot.style.display = 'block';
}

// ===========================================================
// CATEGORY CARROUSEL (landing) — horizontal scrolling reel
// ===========================================================
const CATEGORIES = [
  {
    label: 'Create with our AI Tools', sub: 'Vertex AI · live',
    ai: true,
    art: 'radial-gradient(circle at 30% 30%, rgba(131,229,9,.4), transparent 45%), radial-gradient(circle at 70% 80%, rgba(110,86,207,.6), transparent 45%), linear-gradient(160deg, #1F232B 0%, #0E1014 100%)',
    mod: 'all',
  },
  { label: 'Video Templates', sub: '150,000+', art: 'linear-gradient(160deg, #FFC93B 0%, #FF6B5C 100%)', mod: 'video' },
  { label: 'Stock Photos',    sub: '15.8M+',   art: 'linear-gradient(160deg, #FF7A8A 0%, #F47A6B 100%)', mod: 'photo' },
  { label: 'Royalty-Free Music', sub: '340,000+', art: 'linear-gradient(160deg, #26C7AC 0%, #1A7F8C 100%)', mod: 'audio' },
  { label: 'Sound Effects',   sub: '930,000+', art: 'linear-gradient(160deg, #FF9E5C 0%, #E5575C 100%)', mod: 'audio' },
  { label: 'Graphic Templates', sub: '410,000+', art: 'linear-gradient(160deg, #B6E54A 0%, #6FAB22 100%)', mod: 'graphic' },
  { label: 'Fonts',           sub: '76,000+',  art: 'linear-gradient(160deg, #2A2A2A 0%, #555 100%)', mod: 'graphic' },
  { label: 'Graphics',        sub: '270,000+', art: 'linear-gradient(160deg, #84A8FF 0%, #6E56CF 100%)', mod: 'graphic' },
  { label: '3D',              sub: '180,000+', art: 'linear-gradient(160deg, #FFD27A 0%, #E5A35C 100%)', mod: 'graphic' },
  { label: 'Add-ons',         sub: '37,000+',  art: 'linear-gradient(160deg, #9079E6 0%, #6E56CF 100%)', mod: 'graphic' },
  { label: 'Presentation Templates', sub: '210,000+', art: 'linear-gradient(160deg, #FF7AA8 0%, #E5575C 100%)', mod: 'graphic' },
  { label: 'All Categories',  sub: '27.8M+',   art: 'linear-gradient(160deg, #444 0%, #111 100%)', mod: 'all' },
];

function renderCatReel() {
  const reel = $('#catreel');
  if (!reel) return;
  reel.innerHTML = '';
  CATEGORIES.forEach(c => {
    const tile = el('div', {
      class: 'cattile' + (c.ai ? ' cattile--ai' : ''),
      dataset: { mod: c.mod, cursor: 'open' },
    },
      el('div', { class: 'cattile__label' }, c.label, el('small', {}, c.sub)),
      el('div', { class: 'cattile__art', style: `background: ${c.art};` }),
    );
    tile.addEventListener('click', () => {
      setModality(c.mod, false);
      searchInput.focus();
      // small visual nudge
      tile.animate(
        [{ transform: 'translateY(-4px) scale(.98)' }, { transform: 'translateY(0) scale(1)' }],
        { duration: 180, easing: 'cubic-bezier(.22,.61,.36,1)' }
      );
    });
    reel.appendChild(tile);
  });
  wireReelArrows();
}

function wireReelArrows() {
  const reel = $('#catreel');
  const prev = $('#catReelPrev');
  const next = $('#catReelNext');
  if (!reel || !prev || !next) return;

  const updateDisabled = () => {
    prev.classList.toggle('is-disabled', reel.scrollLeft <= 4);
    const maxScroll = reel.scrollWidth - reel.clientWidth;
    next.classList.toggle('is-disabled', reel.scrollLeft >= maxScroll - 4);
  };
  const scrollByCard = dir => {
    const tile = reel.querySelector('.cattile');
    const step = tile ? (tile.offsetWidth + 14) * 2 : 320;
    reel.scrollBy({ left: dir * step, behavior: 'smooth' });
  };
  prev.onclick = () => scrollByCard(-1);
  next.onclick = () => scrollByCard(1);
  reel.addEventListener('scroll', updateDisabled, { passive: true });
  updateDisabled();
}

// ===========================================================
// AI TOOLS STRIP (landing)
// ===========================================================
const AI_TOOLS = [
  { label: 'VideoGen',   tone: 'radial-gradient(circle at 30% 30%, rgba(131,229,9,.45), transparent 55%)' },
  { label: 'ImageGen',   tone: 'radial-gradient(circle at 30% 30%, rgba(110,86,207,.55), transparent 55%)' },
  { label: 'ImageEdit',  tone: 'radial-gradient(circle at 30% 30%, rgba(38,199,172,.55), transparent 55%)' },
  { label: 'VoiceGen',   tone: 'radial-gradient(circle at 30% 30%, rgba(255,166,92,.55), transparent 55%)' },
  { label: 'MusicGen',   tone: 'radial-gradient(circle at 30% 30%, rgba(229,87,92,.55), transparent 55%)' },
  { label: 'GraphicsGen',tone: 'radial-gradient(circle at 30% 30%, rgba(132,168,255,.55), transparent 55%)' },
  { label: 'MockUpGen',  tone: 'radial-gradient(circle at 30% 30%, rgba(180,180,180,.45), transparent 55%)' },
  { label: 'SoundGen',   tone: 'radial-gradient(circle at 30% 30%, rgba(255,210,122,.55), transparent 55%)' },
];
function renderAiTools() {
  const root = $('#aitools');
  if (!root) return;
  root.innerHTML = '';
  AI_TOOLS.forEach(t => {
    const tile = el('div', { class: 'aitool', style: `--tone: ${t.tone};`, dataset: { cursor: 'open' } },
      el('span', { class: 'aitool__label' }, t.label),
    );
    root.appendChild(tile);
  });
}

// ===========================================================
// FILTERS (left sidebar)
// ===========================================================
const COLORS = ['#E5575C','#F4A56B','#F2D265','#7CD86F','#26C7AC','#5BA8E5','#6E56CF','#E37AC8','#1F1F1F','#F2EDE2'];
function renderSwatches() {
  const root = $('#swatches');
  if (!root) return;
  root.innerHTML = '';
  COLORS.forEach(c => {
    const sw = el('button', { class: 'swatch', style: `background:${c};`, dataset: { hex: c, cursor: 'link' } });
    sw.addEventListener('click', () => {
      const wasActive = sw.classList.contains('is-active');
      $$('.swatch').forEach(s => s.classList.remove('is-active'));
      if (!wasActive) sw.classList.add('is-active');
      state.filters.color = wasActive ? '' : c;
      $('#colorClear').hidden = !state.filters.color;
      if (state.query) runSearch({ showLoader: true });
    });
    root.appendChild(sw);
  });
}
$('#colorClear')?.addEventListener('click', () => {
  $$('.swatch').forEach(s => s.classList.remove('is-active'));
  state.filters.color = '';
  $('#colorClear').hidden = true;
  if (state.query) runSearch({ showLoader: true });
});

document.addEventListener('change', e => {
  const t = e.target;
  if (!t || t.tagName !== 'INPUT' || t.type !== 'radio') return;
  if (t.name === 'modality') setModality(t.value);
  if (t.name === 'tempo') { state.filters.tempo = t.value; if (state.query) runSearch({ showLoader: true }); }
  if (t.name === 'length') { state.filters.length = t.value; if (state.query) runSearch({ showLoader: true }); }
});

$('#filtersToggle')?.addEventListener('click', () => {
  const f = $('#filters');
  const collapsed = f.classList.toggle('is-collapsed');
  $('#filtersToggle').textContent = collapsed ? 'Show Filters' : 'Hide Filters';
  $$('.filters__group').forEach(g => g.style.display = collapsed ? 'none' : '');
});

// ===========================================================
// LANDING QUICK-CHIPS
// ===========================================================
$$('.qchip').forEach(c => c.addEventListener('click', () => {
  searchInput.value = c.dataset.q;
  state.query = c.dataset.q;
  searchClear.hidden = false;
  hideSuggest();
  runSearch({ showLoader: true });
}));

// ===========================================================
// SEARCH CALL
// ===========================================================
async function fetchSearch({ q, modality = state.modality, limit = 20, suggestOnly = false } = {}) {
  const params = new URLSearchParams({ q, modality, limit: String(limit) });
  if (state.filters.tempo)  params.set('tempo',  state.filters.tempo);
  if (state.filters.length) params.set('length', state.filters.length);
  if (state.filters.color)  params.set('color',  state.filters.color);

  // Vibe-slider bias (warm/energy/cinematic/busy, each in [-1, 1]).
  // window.__vibe is owned by static/vibe_slider.js. Only attach axes with
  // |value| > 0 so the URL stays clean for the default neutral state.
  const vibe = (typeof window !== 'undefined' && window.__vibe) || null;
  if (vibe) {
    for (const [axis, value] of Object.entries(vibe)) {
      const v = Number(value);
      if (Number.isFinite(v) && Math.abs(v) > 0.001) {
        params.set(`vibe_${axis}`, v.toFixed(3));
      }
    }
  }

  if (state.inflight && !suggestOnly) state.inflight.abort();
  const ctrl = new AbortController();
  if (!suggestOnly) state.inflight = ctrl;

  const r = await fetch(`/api/search?${params.toString()}`, { signal: ctrl.signal }).catch(err => {
    if (err.name === 'AbortError') return null;
    throw err;
  });
  if (!r) return null;
  if (!r.ok) throw new Error(`search HTTP ${r.status}`);
  return r.json();
}

async function runSearch({ showLoader = false } = {}) {
  const q = state.query.trim();
  if (!q) { showLanding(); return; }
  showResults();
  if (showLoader) loader.hidden = false;
  try {
    const resp = await fetchSearch({ q });
    if (!resp) return;
    state.lastResp = resp;
    renderResults(resp);
  } catch (err) {
    console.error(err);
    toast({ kind: 'err', title: 'Search failed', body: String(err.message || err) });
  } finally {
    loader.hidden = true;
  }
}

// ===========================================================
// RENDER RESULTS
// ===========================================================
function renderResults(resp) {
  // Stop any audio before re-rendering
  stopAudio();

  // Header
  resultsTitle.innerHTML = `<em>${escapeHtml(resp.query)}</em> Assets &amp; Templates`;
  const counts = `${resp.result_count} results in <strong>${fmtMs(resp.total_ms)}</strong>` +
                 ` <span style="color:#9AA0A8">(embed ${fmtMs(resp.query_embed_ms)} · search ${fmtMs(resp.vs_search_ms)} · hydrate ${fmtMs(resp.hydrate_ms)})</span>`;
  resultsSub.innerHTML = counts;

  // Rescue banner
  if (resp.rescue) {
    rescueBanner.hidden = false;
    rescueBanner.innerHTML =
      `<span class="rescue__icon">🔍</span>` +
      `<div><strong>No exact matches</strong> — recovered with <code>${escapeHtml(resp.rescue)}</code> in <strong>${fmtMs(resp.total_ms)}</strong>. ` +
      `These are semantic neighbours from the same vector space.</div>`;
  } else {
    rescueBanner.hidden = true;
    rescueBanner.innerHTML = '';
  }

  // Refinement chips from caption.objects/tags
  renderRefineBar(resp);

  // Filter visibility
  $('#tempoGroup').hidden  = !((resp.grouped && (resp.grouped.audio_music?.length || resp.grouped.audio_sfx?.length)) || resp.results.some(r => r.modality === 'audio'));
  $('#lengthGroup').hidden = !((resp.grouped && resp.grouped.video?.length) || resp.results.some(r => r.modality === 'video'));

  // Modality blocks
  resultCols.innerHTML = '';
  const grouped = resp.grouped || groupResults(resp.results);

  const blockOrder = [
    { key: 'photo',       title: 'Photos',        kind: 'grid', cls: 'photo' },
    { key: 'video',       title: 'Stock Video',   kind: 'grid', cls: 'video' },
    { key: 'audio_music', title: 'Music',         kind: 'audio' },
    { key: 'audio_sfx',   title: 'Sound Effects', kind: 'audio' },
    { key: 'graphic',     title: 'Graphics',      kind: 'grid', cls: 'graphic' },
  ];

  let rendered = 0;
  for (const b of blockOrder) {
    const items = grouped[b.key] || [];
    if (state.modality !== 'all') {
      const want = (b.key.startsWith('audio') ? 'audio' : b.key);
      if (state.modality !== want) continue;
    }
    if (!items.length) continue;
    rendered++;
    const block = el('section', { class: 'modblock' });
    block.appendChild(el('div', { class: 'modblock__head' },
      el('div', {},
        el('span', { class: 'modblock__title' }, b.title),
        el('span', { class: 'modblock__count' }, `${items.length} match${items.length === 1 ? '' : 'es'}`),
      ),
      el('a', { class: 'modblock__more', href: '#', dataset: { cursor: 'link' }, onclick: e => {
        e.preventDefault();
        setModality(b.key.startsWith('audio') ? 'audio' : b.key, false);
        runSearch({ showLoader: true });
      }}, 'Show all →'),
    ));
    if (b.kind === 'audio') block.appendChild(renderAudioList(items));
    else block.appendChild(renderCardGrid(items, b.cls));
    resultCols.appendChild(block);
  }

  if (rendered === 0) {
    resultCols.appendChild(el('div', { class: 'modblock--empty' },
      'No results in the chosen modality. Try switching to "All" in the left filters.'));
  }
}

function groupResults(results = []) {
  const g = { photo: [], video: [], audio_music: [], audio_sfx: [], graphic: [] };
  for (const r of results) {
    if (r.modality === 'photo')   g.photo.push(r);
    else if (r.modality === 'video') g.video.push(r);
    else if (r.modality === 'graphic') g.graphic.push(r);
    else if (r.modality === 'audio') (r.kind === 'sfx' ? g.audio_sfx : g.audio_music).push(r);
  }
  return g;
}

// ----- refinement chips from top results -----
function renderRefineBar(resp) {
  refineBar.innerHTML = '';
  const tags = new Map();
  const top = (resp.results || []).slice(0, 16);
  for (const r of top) {
    const cap = r.caption || {};
    const arr = []
      .concat(cap.objects || [])
      .concat(cap.tags    || [])
      .concat(cap.subjects|| []);
    for (const t of arr) {
      if (!t || typeof t !== 'string') continue;
      const k = t.toLowerCase().trim();
      if (k.length < 3 || k.length > 28) continue;
      tags.set(k, (tags.get(k) || 0) + 1);
    }
  }
  const top12 = Array.from(tags.entries())
    .sort((a, b) => b[1] - a[1])
    .slice(0, 14)
    .map(([k]) => k);

  for (const t of top12) {
    const c = el('button', {
      class: 'refchip' + (state.refineActive.has(t) ? ' is-active' : ''),
      dataset: { t, cursor: 'link' },
    }, t);
    c.addEventListener('click', () => {
      if (state.refineActive.has(t)) state.refineActive.delete(t);
      else state.refineActive.add(t);
      const extra = Array.from(state.refineActive).join(' ');
      const base = state.query.replace(/\s+\[.*\]$/, '');
      searchInput.value = extra ? `${base} ${extra}` : base;
      state.query = searchInput.value;
      runSearch({ showLoader: true });
    });
    refineBar.appendChild(c);
  }
}

// ===========================================================
// CARD GRID (photo / video / graphic) — with rich hover behavior
// ===========================================================
function renderCardGrid(items, cls) {
  const grid = el('div', { class: `cardgrid cardgrid--${cls}` });
  for (const r of items) grid.appendChild(renderCard(r, cls));
  return grid;
}
function renderCard(r, cls) {
  const card = el('article', {
    class: `card card--${cls}`,
    dataset: { id: r.datapoint_id, cursor: cls === 'video' ? 'play' : 'open' },
  });
  const media = el('div', { class: 'card__media' });

  if (r.thumbnail_url) {
    media.appendChild(el('img', { class: 'card__img', src: r.thumbnail_url, alt: r.caption_text || '', loading: 'lazy' }));
  } else {
    media.style.background = 'linear-gradient(135deg, #DDD3C3, #B6AB95)';
  }

  // score badge
  media.appendChild(el('div', { class: 'card__score' }, `${(clampScore(r.score) * 100).toFixed(0)}%`));

  // hover action icons (top-right)
  media.appendChild(el('div', { class: 'card__actions' },
    el('button', {
      class: 'card__action card__action--chat',
      title: 'Talk to this asset (Live voice + chat)',
      dataset: { cursor: 'link' },
      onclick: ev => { ev.stopPropagation(); AssetChat.open(r); }
    }, '💬'),
    el('button', {
      class: 'card__action card__action--kit',
      title: 'Build a Kit (one matching asset per modality)',
      dataset: { cursor: 'link' },
      onclick: ev => { ev.stopPropagation(); window.Kit && window.Kit.open(r.datapoint_id || r.asset_id, r); }
    }, '🧰'),
    el('button', { class: 'card__action', title: 'Save', dataset: { cursor: 'link' } }, '♡'),
    el('button', {
      class: 'card__action', title: 'Find similar', dataset: { cursor: 'link' },
      onclick: ev => { ev.stopPropagation(); reuseAsQuery(r); }
    }, '⟲'),
    el('button', {
      class: 'card__action', title: 'Download', dataset: { cursor: 'link' },
      onclick: ev => { ev.stopPropagation(); window.open(r.original_url || r.clip_url, '_blank', 'noopener'); }
    }, '⤓'),
  ));

  // video extras
  if (cls === 'video') {
    if (r.start_s != null && r.end_s != null) {
      media.appendChild(el('div', { class: 'card__timecode' }, `${fmtTime(r.start_s)}–${fmtTime(r.end_s)}`));
    }
    media.appendChild(el('div', { class: 'card__play' }));
    media.appendChild(el('div', { class: 'card__progress' }, el('span')));
  }

  // hover overlay caption
  media.appendChild(el('div', { class: 'card__overlay' },
    el('div', { class: 'card__caption' }, (r.caption_text || '').slice(0, 140))
  ));

  // envato-y watermark feel
  media.appendChild(el('div', { class: 'card__watermark' }, 'envato'));

  card.appendChild(media);
  card.appendChild(el('div', { class: 'card__byline' },
    el('span', { class: 'card__byline-name' }, r.contributor || r.sub_category || 'Envato'),
    el('span', {}, r.kind || r.modality),
  ));

  // hover behavior: video preview / photo ken-burns is via CSS transform on img
  if (cls === 'video') wireVideoHover(card, r, media);

  card.addEventListener('click', () => openDetail(r));
  return card;
}

function wireVideoHover(card, r, media) {
  let video, hoverTimer;
  const start = () => {
    if (!r.clip_url) return;
    if (!video) {
      video = el('video', {
        class: 'card__video',
        src: r.clip_url,
        muted: true,
        playsinline: true,
        loop: true,
        preload: 'metadata',
      });
      media.insertBefore(video, media.firstChild.nextSibling);  // behind overlay
    }
    card.classList.add('is-previewing');
    const p = video.play(); if (p && p.catch) p.catch(() => {});
    // progress bar
    const bar = card.querySelector('.card__progress > span');
    const tick = () => {
      if (!card.classList.contains('is-previewing')) return;
      if (video && video.duration) {
        bar.style.width = `${(video.currentTime / video.duration) * 100}%`;
      }
      requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  };
  const stop = () => {
    card.classList.remove('is-previewing');
    if (video) {
      video.pause();
      try { video.currentTime = 0; } catch {}
    }
    const bar = card.querySelector('.card__progress > span');
    if (bar) bar.style.width = '0%';
  };
  card.addEventListener('mouseenter', () => {
    clearTimeout(hoverTimer);
    hoverTimer = setTimeout(start, 180);  // small delay = doesn't fire on flyover
  });
  card.addEventListener('mouseleave', () => {
    clearTimeout(hoverTimer);
    stop();
  });
}

// ===========================================================
// AUDIO ROWS (music + sfx) with hover-play + waveform progress
// ===========================================================
function renderAudioList(items) {
  const wrap = el('div', { class: 'audiolist', style: 'display:flex;flex-direction:column;gap:8px;' });
  for (const r of items) wrap.appendChild(renderAudioRow(r));
  return wrap;
}
function renderAudioRow(r) {
  const cap = r.caption || {};
  const bpm = cap.bpm || cap.tempo_bpm || cap.tempo || null;
  const dur = (r.end_s != null && r.start_s != null) ? (r.end_s - r.start_s) : (cap.duration_s || null);

  const row = el('div', {
    class: 'audiorow',
    dataset: { id: r.datapoint_id, cursor: 'listen' },
  });

  // play
  const play = el('button', { class: 'audiorow__play', title: 'Play preview', dataset: { cursor: 'listen' } });
  play.addEventListener('click', e => { e.stopPropagation(); toggleAudio(r, row); });
  row.appendChild(play);

  // title + by
  row.appendChild(el('div', {},
    el('div', { class: 'audiorow__title' }, (cap.title || r.caption_text || '').slice(0, 60) || 'Untitled'),
    el('div', { class: 'audiorow__by' }, `By ${r.contributor || 'Envato'}`),
  ));

  // waveform — faux bars + playback overlay
  const waveBox = el('div', { class: 'audiorow__wave' });
  const baseWave = renderFauxWave(r.datapoint_id || r.caption_text || 'x');
  waveBox.appendChild(baseWave);
  // active (colored) wave overlay — clipped by width
  const activeWave = renderFauxWave(r.datapoint_id || r.caption_text || 'x');
  activeWave.classList.add('wave-active-inner');
  const activeBox = el('div', { class: 'wave-active' }, activeWave);
  waveBox.appendChild(activeBox);
  row.appendChild(waveBox);

  // bpm / duration
  row.appendChild(el('div', { class: 'audiorow__bpm' },
    bpm ? `${Math.round(bpm)}` : (dur ? fmtTime(dur) : '—'),
    el('small', {}, bpm ? 'BPM' : (r.kind === 'sfx' ? 'sfx' : 'sec'))
  ));

  // score
  row.appendChild(el('div', { class: 'audiorow__score' }, `${(clampScore(r.score) * 100).toFixed(0)}%`));

  // talk-to-asset chat button
  const chatBtn = el('button', {
    class: 'audiorow__chat',
    title: 'Talk to this asset',
    dataset: { cursor: 'link' },
  }, '💬 Talk');
  chatBtn.addEventListener('click', e => { e.stopPropagation(); AssetChat.open(r); });
  row.appendChild(chatBtn);
  // build-a-kit button (kit panel logic lives in /static/kit_panel.js)
  const kitBtn = el('button', {
    class: 'audiorow__chat audiorow__kit',
    title: 'Build a Kit',
    dataset: { cursor: 'link' },
  }, '🧰 Kit');
  kitBtn.addEventListener('click', e => { e.stopPropagation(); window.Kit && window.Kit.open(r.datapoint_id || r.asset_id, r); });
  row.appendChild(kitBtn);

  // hover-to-play (with delay)
  let hoverTimer;
  row.addEventListener('mouseenter', () => {
    clearTimeout(hoverTimer);
    hoverTimer = setTimeout(() => playAudio(r, row), 220);
  });
  row.addEventListener('mouseleave', () => {
    clearTimeout(hoverTimer);
    if (state.audioPlayingRow === row) stopAudio();
  });
  // click to open detail (but ignore button clicks)
  row.addEventListener('click', e => {
    if (e.target.closest('.audiorow__play')) return;
    openDetail(r);
  });
  return row;
}

function toggleAudio(r, row) {
  if (state.audioPlayingRow === row) { stopAudio(); return; }
  playAudio(r, row);
}
function playAudio(r, row) {
  if (!r.clip_url) return;
  stopAudio();
  if (!state.audioPlayer) state.audioPlayer = new Audio();
  state.audioPlayer.src = r.clip_url;
  state.audioPlayer.volume = 0.85;
  state.audioPlayer.play().catch(() => {});
  state.audioPlayingRow = row;
  row.classList.add('is-playing');

  const activeBox = row.querySelector('.wave-active');
  const tick = () => {
    if (state.audioPlayingRow !== row) return;
    const dur = state.audioPlayer.duration || 1;
    const pct = (state.audioPlayer.currentTime / dur) * 100;
    if (activeBox) activeBox.style.width = `${Math.max(0, Math.min(100, pct))}%`;
    state.audioRaf = requestAnimationFrame(tick);
  };
  state.audioRaf = requestAnimationFrame(tick);

  state.audioPlayer.onended = () => stopAudio();
}
function stopAudio() {
  if (state.audioRaf) cancelAnimationFrame(state.audioRaf);
  state.audioRaf = null;
  if (state.audioPlayer) {
    try { state.audioPlayer.pause(); state.audioPlayer.currentTime = 0; } catch {}
  }
  if (state.audioPlayingRow) {
    state.audioPlayingRow.classList.remove('is-playing');
    const activeBox = state.audioPlayingRow.querySelector('.wave-active');
    if (activeBox) activeBox.style.width = '0%';
  }
  state.audioPlayingRow = null;
}

// deterministic faux waveform from any string (so it stays stable)
function renderFauxWave(seed) {
  let h = 0;
  for (let i = 0; i < seed.length; i++) h = ((h << 5) - h + seed.charCodeAt(i)) | 0;
  const wave = el('div', { class: 'wave' });
  const bars = 80;
  for (let i = 0; i < bars; i++) {
    h = (h * 1664525 + 1013904223) | 0;
    const v = Math.abs(h % 100) / 100;
    const ht = 4 + Math.floor(v * 30);
    wave.appendChild(el('span', { style: `height:${ht}px;` }));
  }
  return wave;
}

// ----- find-similar shortcut from card action -----
function reuseAsQuery(r) {
  const q = (r.caption_text || (r.caption && r.caption.title) || '').slice(0, 80);
  if (!q) return;
  searchInput.value = q;
  state.query = q;
  searchClear.hidden = false;
  hideSuggest();
  runSearch({ showLoader: true });
}

// ===========================================================
// DETAIL MODAL
// ===========================================================
const detailModal = $('#detailModal');
const detailBody  = $('#detailBody');

async function openDetail(r) {
  detailBody.innerHTML = '<div style="padding:40px;text-align:center;color:#9AA0A8;">Loading…</div>';
  openModal(detailModal);
  let full = r;
  try {
    const f = await fetch(`/api/segment/${encodeURIComponent(r.datapoint_id)}`);
    if (f.ok) full = Object.assign({}, r, await f.json());
  } catch (err) { /* keep partial */ }
  renderDetail(full);
}
function renderDetail(r) {
  const cap = r.caption || {};
  let preview;
  if (r.modality === 'photo' || r.modality === 'graphic') {
    preview = el('img', { src: r.original_url || r.thumbnail_url || '', alt: '' });
  } else if (r.modality === 'video') {
    preview = el('video', { src: r.clip_url || r.original_url || '', controls: true, autoplay: true, muted: true, playsinline: true });
  } else if (r.modality === 'audio') {
    preview = el('div', { style: 'width:100%;padding:18px;display:flex;flex-direction:column;gap:12px;' },
      r.thumbnail_url ? el('img', { src: r.thumbnail_url, alt: '', style: 'width:100%;max-height:120px;object-fit:contain;' }) : renderFauxWave(r.datapoint_id || ''),
      el('audio', { src: r.clip_url || r.original_url || '', controls: true, style: 'width:100%;' }),
    );
  } else {
    preview = el('div', { style: 'color:#9AA0A8;' }, 'No preview');
  }

  const meta = el('div', { class: 'detail__meta' },
    el('span', {}, el('strong', {}, 'modality:'), ' ', r.modality),
    el('span', {}, el('strong', {}, 'kind:'), ' ', r.kind || '—'),
    el('span', {}, el('strong', {}, 'segment:'), ' ', `${fmtTime(r.start_s)}–${fmtTime(r.end_s)}`),
    el('span', {}, el('strong', {}, 'score:'), ' ', `${(clampScore(r.score) * 100).toFixed(1)}%`),
  );

  detailBody.innerHTML = '';
  detailBody.appendChild(el('div', { class: 'detail__preview' }, preview));
  detailBody.appendChild(el('div', { class: 'detail__side' },
    el('div', { class: 'ai-chip ai-chip--big' }, '✦ Vertex AI segment'),
    el('h2', {}, (cap.title || r.sub_category || 'Asset')),
    meta,
    el('div', { class: 'detail__actions' },
      el('button', { class: 'cta cta--green', dataset: { cursor: 'link' }, onclick: () => {
        closeModal(detailModal);
        AssetChat.open(r);
      } }, '💬 Talk to this asset'),
      el('button', { class: 'cta cta--ghost', dataset: { cursor: 'link' }, onclick: () => {
        const q = (r.caption_text || cap.title || '').slice(0, 80);
        if (q) {
          searchInput.value = q;
          state.query = q;
          closeModal(detailModal);
          runSearch({ showLoader: true });
        }
      } }, 'Find similar'),
      el('a', { class: 'cta cta--ghost', dataset: { cursor: 'link' }, href: r.original_url || '#', target: '_blank', rel: 'noopener' }, 'Open original'),
    ),
    el('h4', { style: 'margin-top:6px;font-size:12px;color:#6B7280;text-transform:uppercase;letter-spacing:.05em;' }, 'Caption (structured)'),
    el('pre', { class: 'detail__json' }, JSON.stringify(cap, null, 2)),
  ));
}

// ===========================================================
// MODAL plumbing
// ===========================================================
function openModal(m) { m.hidden = false; document.body.style.overflow = 'hidden'; }
function closeModal(m) { m.hidden = true; document.body.style.overflow = ''; }
$$('.modal').forEach(m => {
  m.addEventListener('click', e => {
    if (e.target.matches('[data-close]') || e.target.matches('.modal__backdrop') || e.target.matches('.modal__close')) {
      closeModal(m);
    }
  });
});
document.addEventListener('keydown', e => {
  if (e.key === 'Escape') $$('.modal').forEach(m => closeModal(m));
});

// ===========================================================
// SOUNDS-LIKE
// ===========================================================
const slModal = $('#soundsLikeModal');
const slDrop  = $('#slDrop');
const slFile  = $('#slFile');
const slStatus = $('#slStatus');

$('#soundsLikeBtn')?.addEventListener('click', () => openModal(slModal));
$('#soundsLikeLink')?.addEventListener('click', e => { e.preventDefault(); openModal(slModal); });
$('#soundsLikeLinkInline')?.addEventListener('click', e => { e.preventDefault(); openModal(slModal); });

wireDrop(slDrop, slFile, async file => {
  slStatus.innerHTML = `Uploading <code>${escapeHtml(file.name)}</code>…`;
  const fd = new FormData(); fd.append('file', file);
  try {
    const r = await fetch('/api/search/sounds-like', { method: 'POST', body: fd });
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    const resp = await r.json();
    slStatus.innerHTML = `<span class="ok">Matched ${resp.result_count} segments in ${fmtMs(resp.total_ms)}</span>`;
    state.query = `🎧 ${file.name}`;
    searchInput.value = state.query;
    state.lastResp = resp;
    closeModal(slModal);
    showResults();
    renderResults(resp);
  } catch (err) {
    slStatus.innerHTML = `<span class="err">Failed: ${escapeHtml(err.message || err)}</span>`;
  }
});

// ===========================================================
// IMAGE-TO-ANYTHING
// ===========================================================
const i2aModal = $('#imageToAnyModal');
const i2aDrop  = $('#i2aDrop');
const i2aFile  = $('#i2aFile');
const i2aStatus = $('#i2aStatus');

$('#imageToAnyBtn')?.addEventListener('click', () => openModal(i2aModal));
$('#imageToAnyLink')?.addEventListener('click', e => { e.preventDefault(); openModal(i2aModal); });

wireDrop(i2aDrop, i2aFile, async file => {
  i2aStatus.innerHTML = `Embedding <code>${escapeHtml(file.name)}</code>…`;
  const fd = new FormData(); fd.append('file', file);
  try {
    const r = await fetch('/api/image-to-anything', { method: 'POST', body: fd });
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    const resp = await r.json();
    i2aStatus.innerHTML = `<span class="ok">Cross-modal results in ${fmtMs(resp.total_ms)} — photos, video, music & SFX</span>`;
    state.query = `🖼 ${file.name}`;
    searchInput.value = state.query;
    state.lastResp = resp;
    setModality('all', false);
    closeModal(i2aModal);
    showResults();
    renderResults(resp);
  } catch (err) {
    i2aStatus.innerHTML = `<span class="err">Failed: ${escapeHtml(err.message || err)}</span>`;
  }
});

// ===========================================================
// AUTO-INGEST FAB
// ===========================================================
const ingest      = $('#ingest');
const ingestHead  = $('#ingestHead');
const ingestDrop  = $('#ingestDrop');
const ingestFile  = $('#ingestFile');
const ingestFeed  = $('#ingestFeed');

ingestHead.addEventListener('click', e => {
  if (e.target.closest('input,label')) return;
  ingest.classList.toggle('is-collapsed');
});

wireDrop(ingestDrop, ingestFile, async file => {
  const li = el('li', {}, `↑ ${file.name}…`);
  ingestFeed.prepend(li);
  toast({ kind: 'info', title: 'Uploading…', body: file.name });
  const fd = new FormData(); fd.append('file', file);
  try {
    const r = await fetch('/api/upload', { method: 'POST', body: fd });
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    const j = await r.json();
    li.innerHTML = `↑ <strong>${escapeHtml(file.name)}</strong> · queued · ETA ${j.eta_seconds ?? '?'}s`;
    li.classList.add('ok');
    pollForIngest(j.object_name, file.name);
  } catch (err) {
    li.classList.add('err');
    li.textContent = `× ${file.name} — ${err.message || err}`;
    toast({ kind: 'err', title: 'Upload failed', body: String(err.message || err) });
  }
});

async function pollForIngest(objectName, filename) {
  if (!objectName) return;
  const start = performance.now();
  for (let i = 0; i < 40; i++) {
    await new Promise(r => setTimeout(r, 1500));
    try {
      const r = await fetch('/api/uploads/recent?limit=20');
      if (!r.ok) continue;
      const j = await r.json();
      const list = j.uploads || j.items || j;
      if (!Array.isArray(list)) continue;
      const hit = list.find(u =>
        (u.object_name === objectName) || (u.filename === filename) ||
        (u.original_name === filename) || (u.asset_id && objectName && objectName.includes(u.asset_id.replace('upload-','').replace(/-[a-f0-9]{8}$/,'')))
      );
      if (hit && (hit.status === 'indexed' || hit.indexed_at || hit.segments_indexed != null || hit.segments_written != null)) {
        const dt = ((performance.now() - start) / 1000).toFixed(1);
        const segs = hit.segments_indexed ?? hit.segments ?? hit.segments_written ?? '?';
        const li = el('li', { class: 'ok' }, `✓ ${filename} — indexed in ${dt}s · ${segs} segments`);
        ingestFeed.prepend(li);
        toast({ kind: 'ok', title: 'Indexed', body: `${filename} · ${segs} segments` });
        refreshManageList();
        return;
      }
    } catch (err) { /* keep polling */ }
  }
  toast({ kind: 'info', title: 'Still ingesting', body: `${filename} — check the panel` });
}

// ===========================================================
// MANAGE UPLOADS — list user-uploaded asset_ids with delete buttons
// ===========================================================
const manageList   = $('#manageList');
const manageReload = $('#manageRefresh');

async function refreshManageList() {
  if (!manageList) return;
  try {
    const r = await fetch('/api/uploads/recent?limit=50');
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    const j = await r.json();
    const items = (j.items || []).filter(it => (it.asset_id || '').startsWith('upload-'));
    manageList.innerHTML = '';
    if (!items.length) {
      manageList.appendChild(el('li', { class: 'empty' }, 'No uploads yet'));
      return;
    }
    for (const it of items) {
      const segs = it.segments_written ?? it.segments_indexed ?? '?';
      const niceName = (it.object_name || it.asset_id).replace(/^ingest\//, '');
      const li = el('li', {},
        el('span', { class: 'name', title: it.asset_id }, niceName),
        el('span', { class: 'meta' }, `${segs} seg`),
        el('button', {
          class: 'del', title: `Delete ${it.asset_id}`,
          'aria-label': `Delete ${niceName}`,
        }, '×'),
      );
      li.querySelector('.del').addEventListener('click', () => deleteAsset(it.asset_id, niceName));
      manageList.appendChild(li);
    }
  } catch (err) {
    manageList.innerHTML = '';
    manageList.appendChild(el('li', { class: 'empty' }, `Error: ${err.message || err}`));
  }
}

async function deleteAsset(assetId, niceName) {
  if (!confirm(`Permanently delete "${niceName}" from search, GCS, and Firestore?`)) return;
  try {
    const r = await fetch(`/api/asset/${encodeURIComponent(assetId)}`, { method: 'DELETE' });
    const j = await r.json();
    if (!r.ok) throw new Error(j.detail || `HTTP ${r.status}`);
    const d = j.deleted || {};
    toast({
      kind: 'ok', title: 'Deleted',
      body: `${niceName} · VS ${d.vs_datapoints} · FS ${d.firestore_segments} · GCS ${d.gcs_objects}`,
    });
    refreshManageList();
    refreshStats();
  } catch (err) {
    toast({ kind: 'err', title: 'Delete failed', body: String(err.message || err) });
  }
}

if (manageReload) manageReload.addEventListener('click', refreshManageList);
refreshManageList();

// ===========================================================
// LIVE STATS
// ===========================================================
const statsEl   = $('#stats');
const statsHead = $('#statsHead');
const statsBig  = $('#statsBigBtn');
const statSegments = $('#stat_segments');
const statUploads  = $('#stat_uploads');
const statP50      = $('#stat_p50');
const statP95      = $('#stat_p95');
const statBars     = $('#stat_bars');
const statRecent   = $('#stat_recent');

statsHead.addEventListener('click', e => {
  if (e.target === statsBig || e.target.closest('.stats__big')) return;
  statsEl.classList.toggle('is-collapsed');
});
statsBig.addEventListener('click', e => {
  e.stopPropagation();
  state.bigText = !state.bigText;
  statsEl.classList.toggle('is-big', state.bigText);
  statsBig.classList.toggle('is-active', state.bigText);
});

async function refreshStats() {
  try {
    const r = await fetch('/api/stats');
    if (!r.ok) return;
    const s = await r.json();
    statSegments.textContent = fmtNum(s.segments_indexed);
    statUploads.textContent  = fmtNum(s.last_24h_uploads);
    statP50.textContent      = fmtMs(s.query_latency_ms_p50);
    statP95.textContent      = fmtMs(s.query_latency_ms_p95);

    statBars.innerHTML = '';
    const by = s.by_modality || {};
    const max = Math.max(1, ...Object.values(by).map(Number));
    for (const [k, v] of Object.entries(by)) {
      const w = (Number(v) / max) * 100;
      statBars.appendChild(el('div', { class: 'statbar' },
        el('span', {}, k),
        el('div', { class: 'statbar__bar' }, el('span', { style: `width:${w}%` })),
        el('span', { class: 'statbar__num' }, fmtNum(v)),
      ));
    }

    statRecent.innerHTML = '';
    for (const q of (s.recent_queries || []).slice(0, 8)) {
      const text = typeof q === 'string' ? q : (q.q || q.query || '');
      const ms = typeof q === 'string' ? null : (q.total_ms ?? q.ms);
      statRecent.appendChild(el('li', {},
        el('span', {}, text.slice(0, 28)),
        el('small', {}, ms != null ? fmtMs(ms) : ''),
      ));
    }
  } catch (err) { /* ignore */ }
}

// ===========================================================
// HEALTH
// ===========================================================
async function pingHealth() {
  try {
    const r = await fetch('/api/health');
    if (!r.ok) return;
    const j = await r.json();
    if (j.stats?.segments_indexed != null) {
      statSegments.textContent = fmtNum(j.stats.segments_indexed);
    }
  } catch {}
}

// ===========================================================
// DROP/UPLOAD wiring helper
// ===========================================================
function wireDrop(zone, fileInput, handler) {
  if (!zone) return;
  zone.addEventListener('dragover', e => { e.preventDefault(); zone.classList.add('is-drag'); });
  zone.addEventListener('dragleave', () => zone.classList.remove('is-drag'));
  zone.addEventListener('drop', e => {
    e.preventDefault();
    zone.classList.remove('is-drag');
    const f = e.dataTransfer?.files?.[0];
    if (f) handler(f);
  });
  if (fileInput) {
    fileInput.addEventListener('change', () => {
      const f = fileInput.files?.[0];
      if (f) handler(f);
      fileInput.value = '';
    });
  }
}

// ===========================================================
// TOASTS
// ===========================================================
function toast({ kind = 'info', title = '', body = '' } = {}, ms = 3500) {
  const t = el('div', { class: `toast ${kind}` },
    el('div', {},
      el('div', { class: 'toast__title' }, title),
      body ? el('div', { class: 'toast__body' }, body) : null,
    )
  );
  $('#toasts').appendChild(t);
  setTimeout(() => {
    t.style.transition = 'opacity .2s ease, transform .2s ease';
    t.style.opacity = 0; t.style.transform = 'translateX(8px)';
    setTimeout(() => t.remove(), 220);
  }, ms);
}

// ===========================================================
// TALK TO THIS ASSET — Live API (voice) + Text fallback
// ===========================================================
const AssetChat = (() => {
  const panel       = $('#assetChat');
  const closeBtn    = $('#assetChatClose');
  const previewBox  = $('#assetChatPreview');
  const metaBox     = $('#assetChatMeta');
  const transcript  = $('#assetChatTranscript');
  const statusEl    = $('#assetChatStatus');
  const micBtn      = $('#assetChatMic');
  const textInput   = $('#assetChatText');
  const sendBtn     = $('#assetChatSend');
  const liveBtn     = $('#assetChatLiveBtn');
  const textOnlyBtn = $('#assetChatTextBtn');
  const modeChip    = $('#assetChatMode');

  const TARGET_SR = 16000;
  const PLAYBACK_SR = 24000;        // Gemini Live emits PCM16 mono @ 24kHz

  const s = {
    asset: null,
    ws: null,
    mode: 'live',                   // 'live' | 'text'
    isRecording: false,
    audioCtx: null,                 // capture context (browser native rate)
    playCtx: null,                  // playback context @ PLAYBACK_SR
    mediaStream: null,
    sourceNode: null,
    workletNode: null,
    scriptNode: null,
    history: [],                    // for text-mode chat
    playQueue: [],                  // queued PCM16 chunks
    playHead: 0,                    // next playback time anchor
    transientUserBuf: '',
    transientModelBuf: '',
  };

  // --- UI helpers ---
  function setStatus(text, kind) {
    statusEl.textContent = text;
    statusEl.classList.toggle('is-live', kind === 'live');
    statusEl.classList.toggle('is-err',  kind === 'err');
  }
  function pushBubble(role, text, opts = {}) {
    const cls = role === 'user' ? 'assetchat__bubble assetchat__bubble--user'
              : role === 'sys'  ? 'assetchat__bubble assetchat__bubble--sys'
              : 'assetchat__bubble assetchat__bubble--model';
    const b = el('div', { class: cls }, text);
    if (opts.id) b.dataset.id = opts.id;
    transcript.appendChild(b);
    transcript.scrollTop = transcript.scrollHeight;
    return b;
  }
  function clearTranscript() {
    transcript.innerHTML = '';
    s.transientUserBuf = '';
    s.transientModelBuf = '';
  }

  function appendTranscript(role, chunk) {
    // Stream-style append: keep a single 'in-progress' bubble per speaker
    // until we see another role flip — much nicer than one bubble per token.
    if (role === 'user') {
      s.transientModelBuf = '';
      s.transientUserBuf += chunk;
      let last = transcript.querySelector('.assetchat__bubble--user.is-stream');
      if (!last) {
        last = pushBubble('user', '');
        last.classList.add('is-stream');
      }
      last.textContent = s.transientUserBuf;
      transcript.scrollTop = transcript.scrollHeight;
    } else {
      s.transientUserBuf = '';
      s.transientModelBuf += chunk;
      let last = transcript.querySelector('.assetchat__bubble--model.is-stream');
      if (!last) {
        last = pushBubble('model', '');
        last.classList.add('is-stream');
      }
      last.textContent = s.transientModelBuf;
      transcript.scrollTop = transcript.scrollHeight;
    }
  }

  function commitTranscripts() {
    transcript.querySelectorAll('.is-stream').forEach(n => n.classList.remove('is-stream'));
    s.transientUserBuf = '';
    s.transientModelBuf = '';
  }

  function renderPreview(r) {
    previewBox.innerHTML = '';
    if (!r) return;
    if (r.modality === 'photo' || r.modality === 'graphic') {
      previewBox.appendChild(el('img', {
        src: r.thumbnail_url || r.original_url || '', alt: ''
      }));
    } else if (r.modality === 'video') {
      previewBox.appendChild(el('video', {
        src: r.clip_url || r.original_url || '',
        muted: true, playsinline: true, autoplay: true, loop: true
      }));
    } else if (r.modality === 'audio') {
      const inner = el('div', {
        style: 'width:100%;height:100%;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:10px;background:linear-gradient(160deg,#1F232B,#0E1014);'
      });
      if (r.thumbnail_url) {
        inner.appendChild(el('img', {
          src: r.thumbnail_url,
          style: 'width:80px;height:80px;border-radius:12px;object-fit:cover;'
        }));
      }
      inner.appendChild(el('audio', {
        src: r.clip_url || r.original_url || '', controls: true,
        style: 'width:90%;'
      }));
      previewBox.appendChild(inner);
    } else {
      previewBox.appendChild(el('div', { style: 'color:#9AA0A8;' }, 'No preview'));
    }
  }

  function renderMeta(r) {
    metaBox.innerHTML = '';
    const cap = r.caption || {};
    const title = cap.title || r.caption_text || r.sub_category || 'Asset';
    metaBox.appendChild(el('strong', {}, title.slice(0, 80)));
    const parts = [];
    if (r.modality) parts.push(r.modality + (r.kind ? `/${r.kind}` : ''));
    if (r.contributor) parts.push(`by ${r.contributor}`);
    if (cap.bpm || cap.tempo_bpm) parts.push(`${Math.round(cap.bpm || cap.tempo_bpm)} bpm`);
    if (parts.length) metaBox.appendChild(el('span', {}, parts.join(' · ')));
  }

  // --- Open / Close ---
  function open(r) {
    s.asset = r;
    s.history = [];
    clearTranscript();
    renderPreview(r);
    renderMeta(r);
    panel.hidden = false;
    pushBubble('sys', 'Talk to this asset — ask about mood, lighting, what to pair it with.');
    if (s.mode === 'live') startLive();
    else { setStatus('Text mode ready', 'live'); modeChip.textContent = 'text'; }
  }
  function close() {
    stopLive();
    panel.hidden = true;
    s.asset = null;
  }

  closeBtn.addEventListener('click', close);

  // --- Mode switch ---
  liveBtn.addEventListener('click', () => switchMode('live'));
  textOnlyBtn.addEventListener('click', () => switchMode('text'));
  function switchMode(mode) {
    if (s.mode === mode) return;
    s.mode = mode;
    liveBtn.classList.toggle('is-active', mode === 'live');
    textOnlyBtn.classList.toggle('is-active', mode === 'text');
    modeChip.textContent = mode;
    if (mode === 'live') {
      pushBubble('sys', 'Switched to live voice.');
      startLive();
    } else {
      stopLive();
      pushBubble('sys', 'Switched to text mode.');
      setStatus('Text mode ready', 'live');
    }
  }

  // --- Text mode send ---
  async function sendText() {
    const txt = (textInput.value || '').trim();
    if (!txt || !s.asset) return;
    textInput.value = '';
    pushBubble('user', txt);
    s.history.push({ role: 'user', text: txt });
    if (s.mode === 'live' && s.ws && s.ws.readyState === 1) {
      // In live mode, route typed messages through the same socket as a
      // text turn so the model can speak the answer.
      s.ws.send(JSON.stringify({ type: 'text', text: txt }));
      return;
    }
    setStatus('Thinking…');
    try {
      const r = await fetch(`/api/chat/${encodeURIComponent(s.asset.datapoint_id)}`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: txt, history: s.history.slice(0, -1) }),
      });
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      const j = await r.json();
      pushBubble('model', j.reply || '(no reply)');
      s.history.push({ role: 'model', text: j.reply || '' });
      setStatus(`Replied in ${Math.round(j.latency_ms || 0)}ms · ${j.model || ''}`, 'live');
    } catch (err) {
      pushBubble('sys', `Error: ${err.message || err}`);
      setStatus('Error', 'err');
    }
  }
  sendBtn.addEventListener('click', sendText);
  textInput.addEventListener('keydown', e => {
    if (e.key === 'Enter') { e.preventDefault(); sendText(); }
  });

  // --- Live mode ---
  function startLive() {
    if (!s.asset) return;
    stopLive();
    setStatus('Connecting…');
    const proto = location.protocol === 'https:' ? 'wss:' : 'ws:';
    const url = `${proto}//${location.host}/api/live/${encodeURIComponent(s.asset.datapoint_id)}`;
    let ws;
    try { ws = new WebSocket(url); }
    catch (err) { setStatus(`WS error: ${err.message}`, 'err'); return; }
    ws.binaryType = 'arraybuffer';
    s.ws = ws;
    ws.onopen = () => setStatus('Handshake…');
    ws.onmessage = onWsMessage;
    ws.onerror = () => setStatus('WebSocket error — try Text mode', 'err');
    ws.onclose = () => {
      setStatus('Disconnected');
      stopMic();
      micBtn.classList.remove('is-active');
      micBtn.querySelector('.assetchat__mic-lbl').textContent = 'Talk';
      s.ws = null;
    };
  }

  function stopLive() {
    stopMic();
    if (s.ws) {
      try { s.ws.close(); } catch {}
      s.ws = null;
    }
  }

  function onWsMessage(ev) {
    if (typeof ev.data === 'string') {
      let msg; try { msg = JSON.parse(ev.data); } catch { return; }
      if (msg.type === 'status') {
        setStatus(msg.msg || '', msg.msg === 'live' ? 'live' : '');
      } else if (msg.type === 'transcript') {
        appendTranscript(msg.role || 'model', msg.text || '');
      } else if (msg.type === 'turn_complete') {
        commitTranscripts();
      } else if (msg.type === 'error') {
        pushBubble('sys', `Error: ${msg.msg}`);
        setStatus(msg.msg, 'err');
      }
    } else if (ev.data instanceof ArrayBuffer) {
      enqueuePlayback(ev.data);
    }
  }

  // ----- Playback (Gemini emits raw PCM16 mono @ 24kHz) -----
  function ensurePlayCtx() {
    if (!s.playCtx) {
      const Ctx = window.AudioContext || window.webkitAudioContext;
      s.playCtx = new Ctx({ sampleRate: PLAYBACK_SR });
      s.playHead = s.playCtx.currentTime;
    }
    return s.playCtx;
  }
  function enqueuePlayback(arrayBuffer) {
    const ctx = ensurePlayCtx();
    const view = new DataView(arrayBuffer);
    const numSamples = arrayBuffer.byteLength / 2;
    if (numSamples <= 0) return;
    const buf = ctx.createBuffer(1, numSamples, PLAYBACK_SR);
    const ch = buf.getChannelData(0);
    for (let i = 0; i < numSamples; i++) {
      const s16 = view.getInt16(i * 2, true);
      ch[i] = s16 / 32768;
    }
    const src = ctx.createBufferSource();
    src.buffer = buf;
    src.connect(ctx.destination);
    const now = ctx.currentTime;
    if (s.playHead < now + 0.02) s.playHead = now + 0.02;
    src.start(s.playHead);
    s.playHead += buf.duration;
  }

  // ----- Microphone capture (downsample to 16kHz PCM16) -----
  micBtn.addEventListener('click', async () => {
    if (s.mode !== 'live') {
      switchMode('live');
      return;
    }
    if (!s.ws || s.ws.readyState !== 1) {
      pushBubble('sys', 'Not connected. Reconnecting…');
      startLive();
      return;
    }
    if (s.isRecording) {
      stopMic();
      try { s.ws.send(JSON.stringify({ type: 'end' })); } catch {}
      micBtn.classList.remove('is-active');
      micBtn.querySelector('.assetchat__mic-lbl').textContent = 'Talk';
      setStatus('Listening for reply…', 'live');
    } else {
      try {
        await startMic();
        micBtn.classList.add('is-active');
        micBtn.querySelector('.assetchat__mic-lbl').textContent = 'Stop';
        setStatus('Recording — click Stop when done', 'live');
      } catch (err) {
        pushBubble('sys', `Mic error: ${err.message || err}`);
        setStatus('Mic error', 'err');
      }
    }
  });

  async function startMic() {
    s.mediaStream = await navigator.mediaDevices.getUserMedia({
      audio: {
        channelCount: 1,
        echoCancellation: true,
        noiseSuppression: true,
        sampleRate: TARGET_SR,
      },
    });
    const Ctx = window.AudioContext || window.webkitAudioContext;
    s.audioCtx = new Ctx();        // browser-native rate (usually 48kHz)
    s.sourceNode = s.audioCtx.createMediaStreamSource(s.mediaStream);

    const inputRate = s.audioCtx.sampleRate;
    const ratio = inputRate / TARGET_SR;
    const bufferSize = 4096;
    s.scriptNode = (s.audioCtx.createScriptProcessor || s.audioCtx.createJavaScriptNode)
                    .call(s.audioCtx, bufferSize, 1, 1);

    s.scriptNode.onaudioprocess = ev => {
      if (!s.ws || s.ws.readyState !== 1) return;
      const input = ev.inputBuffer.getChannelData(0);
      const outLen = Math.floor(input.length / ratio);
      const out = new Int16Array(outLen);
      // Simple decimating linear interpolation
      for (let i = 0; i < outLen; i++) {
        const idx = i * ratio;
        const lo = Math.floor(idx);
        const hi = Math.min(lo + 1, input.length - 1);
        const frac = idx - lo;
        const sample = input[lo] * (1 - frac) + input[hi] * frac;
        const clamped = Math.max(-1, Math.min(1, sample));
        out[i] = clamped < 0 ? clamped * 0x8000 : clamped * 0x7FFF;
      }
      try { s.ws.send(out.buffer); } catch {}
    };

    s.sourceNode.connect(s.scriptNode);
    s.scriptNode.connect(s.audioCtx.destination);  // necessary for processing
    s.isRecording = true;
  }

  function stopMic() {
    s.isRecording = false;
    try { s.sourceNode && s.sourceNode.disconnect(); } catch {}
    try { s.scriptNode && s.scriptNode.disconnect(); } catch {}
    if (s.mediaStream) {
      s.mediaStream.getTracks().forEach(t => t.stop());
    }
    if (s.audioCtx && s.audioCtx.state !== 'closed') {
      try { s.audioCtx.close(); } catch {}
    }
    s.sourceNode = null;
    s.scriptNode = null;
    s.audioCtx = null;
    s.mediaStream = null;
  }

  // Esc to close
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape' && !panel.hidden) close();
  });

  return { open, close };
})();

// ===========================================================
// INIT
// ===========================================================
function init() {
  renderCatReel();
  renderAiTools();
  renderSwatches();
  showLanding();
  pingHealth();
  refreshStats();
  setInterval(refreshStats, 5000);
}
document.addEventListener('DOMContentLoaded', init);
})();
