/* ===========================================================
   envato vibe-search v2 — landing_v2.js
   Bento grid + AI tools strip + custom cursor + curated
   collections. Self-contained, prefixed with `lh-`.
   Exposes window.__envatoLanding = { show, hide } for the
   rest of the app to toggle visibility.
   =========================================================== */
(() => {
  'use strict';

  // ---------- helpers ----------
  const $  = (sel, root = document) => root.querySelector(sel);
  const fmtNum = n => Number(n || 0).toLocaleString();
  const root   = $('#landingHero');
  if (!root) return;

  // ---------- thumbnail sources (hardcoded for the demo) ----------
  // Pexels CDN (public, hot-linkable). Each card gets a representative
  // thumbnail keyed to its modality.
  const THUMB = {
    photo:    'https://images.pexels.com/photos/355465/pexels-photo-355465.jpeg?auto=compress&cs=tinysrgb&w=600',
    video:    'https://images.pexels.com/photos/2034851/pexels-photo-2034851.jpeg?auto=compress&cs=tinysrgb&w=600',
    music:    'https://images.pexels.com/photos/1763075/pexels-photo-1763075.jpeg?auto=compress&cs=tinysrgb&w=600',
    sfx:      'https://images.pexels.com/photos/164938/pexels-photo-164938.jpeg?auto=compress&cs=tinysrgb&w=600',
    graphic:  'https://images.pexels.com/photos/1572386/pexels-photo-1572386.jpeg?auto=compress&cs=tinysrgb&w=600',
    fonts:    'https://images.pexels.com/photos/1809644/pexels-photo-1809644.jpeg?auto=compress&cs=tinysrgb&w=600',
    threed:   'https://images.pexels.com/photos/1083822/pexels-photo-1083822.jpeg?auto=compress&cs=tinysrgb&w=600',
    addons:   'https://images.pexels.com/photos/1149831/pexels-photo-1149831.jpeg?auto=compress&cs=tinysrgb&w=600',
    deck:     'https://images.pexels.com/photos/265087/pexels-photo-265087.jpeg?auto=compress&cs=tinysrgb&w=600',
    all:      'https://images.pexels.com/photos/3779662/pexels-photo-3779662.jpeg?auto=compress&cs=tinysrgb&w=600',
    vidtmpl:  'https://images.pexels.com/photos/3045825/pexels-photo-3045825.jpeg?auto=compress&cs=tinysrgb&w=600',
    aitease:  'https://images.pexels.com/photos/4631060/pexels-photo-4631060.jpeg?auto=compress&cs=tinysrgb&w=600',
  };

  // ---------- AI tools (Vertex AI lineup, EBC 2026) ----------
  // Each tool has a verifiable Google product backing it.
  const AI_TOOLS = [
    { key: 'imagegen',  label: 'ImageGen',   tip: 'Imagen 4 — text-to-image on Vertex AI',                              thumb: 'https://images.pexels.com/photos/1183992/pexels-photo-1183992.jpeg?auto=compress&cs=tinysrgb&w=600' },
    { key: 'imageedit', label: 'ImageEdit',  tip: 'Imagen 4 Edit — inpaint, outpaint, mask-based editing',              thumb: 'https://images.pexels.com/photos/1183434/pexels-photo-1183434.jpeg?auto=compress&cs=tinysrgb&w=600' },
    { key: 'videogen',  label: 'VideoGen',   tip: 'Veo 3 — high-fidelity text- and image-to-video',                     thumb: 'https://images.pexels.com/photos/1576937/pexels-photo-1576937.jpeg?auto=compress&cs=tinysrgb&w=600' },
    { key: 'musicgen',  label: 'MusicGen',   tip: 'Lyria 2 — instrumental music generation',                            thumb: 'https://images.pexels.com/photos/1370545/pexels-photo-1370545.jpeg?auto=compress&cs=tinysrgb&w=600' },
    { key: 'voicegen',  label: 'VoiceGen',   tip: 'Chirp 3 HD — natural-sounding text-to-speech',                       thumb: 'https://images.pexels.com/photos/164745/pexels-photo-164745.jpeg?auto=compress&cs=tinysrgb&w=600' },
    { key: 'soundgen',  label: 'SoundGen',   tip: 'Lyria SFX — sound-effect generation from prompts',                   thumb: 'https://images.pexels.com/photos/1407322/pexels-photo-1407322.jpeg?auto=compress&cs=tinysrgb&w=600' },
    { key: 'embedgen',  label: 'EmbedGen',   tip: 'Gemini Embedding — the engine powering this demo',                   thumb: 'https://images.pexels.com/photos/256381/pexels-photo-256381.jpeg?auto=compress&cs=tinysrgb&w=600' },
    { key: 'askgen',    label: 'AskGen',     tip: 'Gemini 2.5 Pro — multimodal chat & reasoning',                       thumb: 'https://images.pexels.com/photos/2885320/pexels-photo-2885320.jpeg?auto=compress&cs=tinysrgb&w=600' },
  ];

  // ---------- bento card definitions ----------
  // 6-column grid × 2 rows. AI dark card spans 2 rows on the left; the
  // remaining 10 category cards each span 1 row, filling the 5×2 region
  // to its right with perfectly uniform card heights.
  const BENTO_LAYOUT = [
    { id: 'ai',       title: 'Create with our + AI Tools', kind: 'ai',                                                        col: 1, row: 2 },
    { id: 'video',    title: 'Video Templates',     modKey: 'video',       fallback: '150,000+', thumb: THUMB.vidtmpl,       col: 1, row: 1 },
    { id: 'photo',    title: 'Stock Photos',        modKey: 'photo',       fallback: '15.6M+',   thumb: THUMB.photo,         col: 1, row: 1 },
    { id: 'music',    title: 'Royalty-Free Music',  modKey: 'audio_music', fallback: '340,000+', thumb: THUMB.music,         col: 1, row: 1 },
    { id: 'sfx',      title: 'Sound Effects',       modKey: 'audio_sfx',   fallback: '930,000+', thumb: THUMB.sfx,           col: 1, row: 1 },
    { id: 'gtmpl',    title: 'Graphic Templates',   modKey: 'graphic',     fallback: '410,000+', thumb: THUMB.graphic,       col: 1, row: 1 },
    { id: 'fonts',    title: 'Fonts',               fixed: '76,000+',                            thumb: THUMB.fonts,         col: 1, row: 1 },
    { id: 'graphics', title: 'Stock Video',         modKey: 'video',       fallback: '270,000+', thumb: THUMB.video,         col: 1, row: 1 },
    { id: 'threed',   title: '3D',                  fixed: '380,000+',                           thumb: THUMB.threed,        col: 1, row: 1 },
    { id: 'addons',   title: 'Add-ons',             fixed: '37,000+',                            thumb: THUMB.addons,        col: 1, row: 1 },
    { id: 'pres',     title: 'Presentation Templates', fixed: '210,000+',                        thumb: THUMB.deck,          col: 1, row: 1 },
  ];

  // ---------- live counts from /api/stats ----------
  let liveCounts = null;
  async function loadStats() {
    try {
      const r = await fetch('/api/stats');
      if (!r.ok) return;
      const data = await r.json();
      liveCounts = data.by_modality || {};
    } catch (e) {
      // best-effort; fallbacks render fine
    }
  }

  function countFor(card) {
    if (card.fixed) return card.fixed;
    if (card.computed === 'all' && liveCounts) {
      const tot = Object.values(liveCounts).reduce((a, b) => a + (Number(b) || 0), 0);
      return `${fmtNum(tot)} segments`;
    }
    if (card.modKey && liveCounts && liveCounts[card.modKey] != null) {
      return `${fmtNum(liveCounts[card.modKey])} segments`;
    }
    return card.fallback || '—';
  }

  // ---------- render: bento grid ----------
  function renderBento() {
    const mount = $('#lhBento');
    if (!mount) return;
    mount.innerHTML = '';

    BENTO_LAYOUT.forEach(card => {
      const span = document.createElement('article');
      span.className = 'lh-card' + (card.kind === 'ai' ? ' lh-card--ai' : '');
      span.style.setProperty('--lh-row', String(card.row));
      span.dataset.cardId = card.id;

      if (card.kind === 'ai') {
        span.innerHTML = `
          <div class="lh-card__head">
            <div class="lh-card__title">Create with our<br/><span class="lh-plus">+</span> AI Tools</div>
          </div>
          <div class="lh-aicard">
            <div class="lh-aicard__brand">
              <svg viewBox="0 0 32 32" width="18" height="18" aria-hidden="true">
                <path d="M16 2 C 9 8, 5 16, 5 22 c 0 5 4 8 11 8 7 0 11 -3 11 -8 0 -6 -4 -14 -11 -20 z" fill="#9BE43F"/>
              </svg>
              <span class="lh-aicard__brand-name">envato</span>
              <span class="lh-aicard__brand-tag">Create</span>
            </div>
            <ul class="lh-aicard__list">
              ${AI_TOOLS.slice(0, 6).map(t => `
                <li class="lh-aicard__item" data-tip="${t.tip}">
                  <span class="lh-aicard__dot"></span>
                  <span class="lh-aicard__name">${t.label}</span>
                </li>`).join('')}
            </ul>
          </div>
          <div class="lh-aicard__hover" aria-hidden="true">
            <div class="lh-aicard__video" style="background-image: url('${THUMB.aitease}');">
              <div class="lh-aicard__caption">Porcelain cars racing</div>
            </div>
            <button type="button" class="lh-aicard__btn">Generate</button>
          </div>
        `;
      } else {
        const cnt = countFor(card);
        span.innerHTML = `
          <div class="lh-card__head">
            <div class="lh-card__title">${card.title}</div>
            <div class="lh-card__count">${cnt}</div>
          </div>
          <div class="lh-card__media">
            <div class="lh-card__img" style="background-image: url('${card.thumb}');"></div>
          </div>
        `;
      }
      mount.appendChild(span);
    });
  }

  // ---------- render: AI tools horizontal strip ----------
  function renderTools() {
    const mount = $('#lhTools');
    if (!mount) return;
    mount.innerHTML = '';

    AI_TOOLS.forEach(t => {
      const tile = document.createElement('button');
      tile.type = 'button';
      tile.className = 'lh-tool-card';
      tile.dataset.tip = t.tip;
      tile.innerHTML = `
        <div class="lh-tool-card__bg" style="background-image: url('${t.thumb}');"></div>
        <div class="lh-tool-card__shade"></div>
        <div class="lh-tool-card__chip">
          <span class="lh-tool-card__icon" aria-hidden="true">
            <svg viewBox="0 0 24 24" width="11" height="11" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="12" cy="12" r="3"/><path d="M12 2 v3 M12 19 v3 M2 12 h3 M19 12 h3 M5 5 l2 2 M17 17 l2 2 M5 19 l2 -2 M17 7 l2 -2"/>
            </svg>
          </span>
          <span class="lh-tool-card__label">${t.label}</span>
        </div>
      `;
      tile.addEventListener('click', () => {
        if (window.Create && typeof window.Create.open === 'function') {
          window.Create.open(t.key, t);
          return;
        }
        const el = document.createElement('div');
        el.className = 'lh-toast';
        el.textContent = `${t.label} — coming soon`;
        document.body.appendChild(el);
        requestAnimationFrame(() => el.classList.add('is-show'));
        setTimeout(() => { el.classList.remove('is-show'); setTimeout(() => el.remove(), 220); }, 1600);
      });
      mount.appendChild(tile);
    });
  }

  // ---------- render: curated collections ----------
  const COLLECTIONS = [
    { title: 'Vector Vibes: visual paraphrasing in action',  bg: 'linear-gradient(140deg, #B22 0%, #6E56CF 100%)', headline: 'Palisade' },
    { title: 'Chunkography: bold display fonts',             bg: 'linear-gradient(140deg, #E5575C 0%, #B0413E 100%)', headline: 'Chunk' },
    { title: 'Motion is Collective',                          bg: 'linear-gradient(140deg, #F4F1EA 0%, #E5DDD0 100%)', headline: 'Motion', dark: true },
    { title: 'Embedding aesthetics: from query to vibe',      bg: 'linear-gradient(140deg, #677664 0%, #2C3530 100%)', headline: 'Fayte', accent: true },
  ];
  function renderCollections() {
    const mount = $('#lhCollections');
    if (!mount) return;
    mount.innerHTML = '';
    COLLECTIONS.forEach(c => {
      const card = document.createElement('article');
      card.className = 'lh-coll';
      card.innerHTML = `
        <div class="lh-coll__hero" style="background: ${c.bg};">
          <div class="lh-coll__big ${c.dark ? 'is-dark' : ''} ${c.accent ? 'is-accent' : ''}">${c.headline}</div>
        </div>
        <div class="lh-coll__title">${c.title}</div>
      `;
      mount.appendChild(card);
    });
  }

  // ---------- AI Tools card hover -> reveal video preview ----------
  function wireAiCardHover() {
    const card = root.querySelector('.lh-card--ai');
    if (!card) return;
    card.addEventListener('mouseenter', () => card.classList.add('is-hover'));
    card.addEventListener('mouseleave', () => card.classList.remove('is-hover'));
    card.style.cursor = 'pointer';
    card.addEventListener('click', (e) => {
      const li = e.target.closest('.lh-aicard__item');
      const wantedKey = li ? (AI_TOOLS.find(t => t.label === li.querySelector('.lh-aicard__name')?.textContent)?.key) : null;
      const key = wantedKey || 'imagegen';
      if (window.Create && typeof window.Create.open === 'function') {
        window.Create.open(key);
      }
    });
  }

  // ---------- tooltip (small label following the cursor) ----------
  const tooltip = $('#lhTooltip');
  function bindTooltips() {
    root.addEventListener('mouseover', e => {
      const t = e.target.closest('[data-tip]');
      if (!t || !tooltip) return;
      tooltip.textContent = t.dataset.tip;
      tooltip.hidden = false;
    });
    root.addEventListener('mouseout', e => {
      const t = e.target.closest('[data-tip]');
      if (!t || !tooltip) return;
      tooltip.hidden = true;
    });
  }

  // ---------- custom cursor (green circle + arrow on hover) ----------
  function wireCursor() {
    const cursor = $('#lhCursor');
    if (!cursor) return;
    let raf = null, mx = -100, my = -100;

    function move(e) {
      mx = e.clientX; my = e.clientY;
      if (raf) return;
      raf = requestAnimationFrame(() => {
        cursor.style.transform = `translate3d(${mx}px, ${my}px, 0) translate(-50%, -50%)`;
        raf = null;
      });
    }
    function enter() { root.classList.add('lh-cursor-on'); }
    function leave() { root.classList.remove('lh-cursor-on'); cursor.classList.remove('is-active'); }

    root.addEventListener('mousemove', move);
    root.addEventListener('mouseenter', enter);
    root.addEventListener('mouseleave', leave);
    root.addEventListener('mouseover', e => {
      if (e.target.closest('.lh-card, .lh-tool-card, .lh-coll, .lh-aicard__btn')) {
        cursor.classList.add('is-active');
      }
    });
    root.addEventListener('mouseout', e => {
      if (e.target.closest('.lh-card, .lh-tool-card, .lh-coll, .lh-aicard__btn')) {
        // only deactivate if leaving to outside the card
        const to = e.relatedTarget;
        if (!to || !to.closest('.lh-card, .lh-tool-card, .lh-coll, .lh-aicard__btn')) {
          cursor.classList.remove('is-active');
        }
      }
    });
  }

  // ---------- show / hide hook ----------
  let lastShown = true;
  function show() {
    if (lastShown) return;
    root.style.display = '';
    requestAnimationFrame(() => root.classList.remove('is-hidden'));
    lastShown = true;
  }
  function hide() {
    if (!lastShown) return;
    root.classList.add('is-hidden');
    setTimeout(() => { if (!lastShown) root.style.display = 'none'; }, 220);
    lastShown = false;
  }

  // Watch the existing #resultCols for child additions; hide landing
  // when there are visible results, show otherwise.
  function wireObserver() {
    const results  = document.getElementById('results');
    const cols     = document.getElementById('resultCols');
    if (!cols || !results) return;
    // Initial: if results node is not hidden and has children, hide landing
    const sync = () => {
      const visibleResults = results && !results.hidden && cols.childElementCount > 0;
      if (visibleResults) hide(); else show();
    };
    new MutationObserver(sync).observe(cols, { childList: true });
    new MutationObserver(sync).observe(results, { attributes: true, attributeFilter: ['hidden'] });
    sync();
  }

  // ---------- public API ----------
  window.__envatoLanding = { show, hide };

  // ---------- boot ----------
  async function boot() {
    await loadStats();
    renderBento();
    renderTools();
    renderCollections();
    wireAiCardHover();
    bindTooltips();
    wireCursor();
    wireObserver();
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();
