/* =============================================================
   vibe_slider.js — perceptual axis biasing for the search bar.

   Renders 4 horizontal sliders below the search input. Each slider
   maps to a "delta vector" on the backend that nudges the current
   query embedding along a perceptual axis (warm/cool, calm/energetic,
   everyday/cinematic, minimal/busy). Values are written to
   window.__vibe and consumed by fetchSearch() in app_v2.js.

   Design rules:
     - Snap to 0 when within ±5 of centre (dead-zone).
     - Debounce 250 ms, then trigger a re-search.
     - When the search input is empty, sliders render but are
       disabled (still visible — feature must be discoverable).
     - All-reset button below the sliders.
   ============================================================= */
(function () {
  'use strict';

  const ROOT_ID = 'vibeSliderRoot';
  const DEBOUNCE_MS = 250;
  const SNAP_PX = 5;          // |raw| <= 5 → snap to 0

  // axis key  →  { label, leftPole, rightPole }
  // Backend param will be vibe_<key>; key MUST match Python VIBE_AXES.
  const AXES = [
    { key: 'warm',      label: 'Warmth',     left: 'cooler',    right: 'warmer'    },
    { key: 'energy',    label: 'Energy',     left: 'calm',      right: 'energetic' },
    { key: 'cinematic', label: 'Look',       left: 'everyday',  right: 'cinematic' },
    { key: 'busy',      label: 'Density',    left: 'minimal',   right: 'busy'      },
  ];

  // Public state shared with app_v2.js's fetchSearch().
  // Values are floats in [-1, 1].
  window.__vibe = window.__vibe || { warm: 0, energy: 0, cinematic: 0, busy: 0 };

  let debounceTimer = null;

  function triggerSearch() {
    // app_v2.js exposes runSearch on window in the typical case; if it's
    // module-private, dispatch a synthetic input on the search field.
    if (typeof window.runSearch === 'function') {
      try { window.runSearch({ showLoader: false }); return; } catch (_) { /* fall through */ }
    }
    // Fallback: simulate Enter on the search input (only if non-empty).
    const inp = document.getElementById('searchInput');
    if (!inp || !inp.value.trim()) return;
    const ev = new KeyboardEvent('keydown', { key: 'Enter', bubbles: true });
    inp.dispatchEvent(ev);
  }

  function scheduleSearch() {
    if (debounceTimer) clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => {
      debounceTimer = null;
      triggerSearch();
    }, DEBOUNCE_MS);
  }

  function snap(raw) {
    return Math.abs(raw) <= SNAP_PX ? 0 : raw;
  }

  function searchHasQuery() {
    const inp = document.getElementById('searchInput');
    return !!(inp && inp.value && inp.value.trim());
  }

  function updateRowVisual(row, raw) {
    // Active-region track: left half if negative, right half if positive.
    const fill = row.querySelector('.vs-fill');
    const valLbl = row.querySelector('.vs-val');
    if (!fill || !valLbl) return;
    const pct = Math.abs(raw); // 0..100
    if (raw === 0) {
      fill.style.left = '50%';
      fill.style.width = '0%';
    } else if (raw > 0) {
      fill.style.left = '50%';
      fill.style.width = pct / 2 + '%';
    } else {
      fill.style.left = (50 - pct / 2) + '%';
      fill.style.width = pct / 2 + '%';
    }
    valLbl.textContent = raw === 0 ? '0' : (raw > 0 ? '+' : '') + raw;
    row.classList.toggle('is-active', raw !== 0);
  }

  function setSliderValue(row, raw, { silent = false } = {}) {
    const slider = row.querySelector('input[type=range]');
    const axis = row.dataset.axis;
    if (!slider || !axis) return;
    slider.value = String(raw);
    window.__vibe[axis] = raw / 100;
    updateRowVisual(row, raw);
    updateActiveBadge();
    if (!silent) scheduleSearch();
  }

  function updateActiveBadge() {
    const root = document.getElementById(ROOT_ID);
    if (!root) return;
    const badge = root.querySelector('.vs-badge');
    if (!badge) return;
    const active = AXES.filter(a => Math.abs(window.__vibe[a.key]) > 0.01);
    if (active.length === 0) {
      badge.textContent = 'neutral';
      badge.classList.remove('is-on');
    } else {
      const parts = active.map(a => {
        const v = window.__vibe[a.key];
        const pole = v > 0 ? a.right : a.left;
        const mag = Math.round(Math.abs(v) * 100);
        return `${pole} ${mag}%`;
      });
      badge.textContent = parts.join(' · ');
      badge.classList.add('is-on');
    }
  }

  function buildRow(axis) {
    const row = document.createElement('div');
    row.className = 'vs-row';
    row.dataset.axis = axis.key;
    row.innerHTML = `
      <div class="vs-row-head">
        <span class="vs-axis-label">${axis.label}</span>
        <span class="vs-val">0</span>
      </div>
      <div class="vs-track-wrap">
        <span class="vs-pole vs-pole--left">${axis.left}</span>
        <div class="vs-track">
          <div class="vs-track-line"></div>
          <div class="vs-tick" style="left:50%"></div>
          <div class="vs-fill"></div>
          <input type="range" min="-100" max="100" value="0" step="1"
                 aria-label="${axis.label}: ${axis.left} to ${axis.right}"
                 data-cursor="text"/>
        </div>
        <span class="vs-pole vs-pole--right">${axis.right}</span>
        <button type="button" class="vs-reset" title="Reset ${axis.label} to neutral"
                aria-label="Reset ${axis.label}">0</button>
      </div>
    `;
    const slider = row.querySelector('input[type=range]');
    const reset  = row.querySelector('.vs-reset');

    slider.addEventListener('input', () => {
      const raw = snap(parseInt(slider.value, 10) || 0);
      if (raw !== parseInt(slider.value, 10)) slider.value = String(raw);
      window.__vibe[axis.key] = raw / 100;
      updateRowVisual(row, raw);
      updateActiveBadge();
      if (searchHasQuery()) scheduleSearch();
    });

    reset.addEventListener('click', e => {
      e.preventDefault();
      setSliderValue(row, 0, { silent: !searchHasQuery() });
    });

    return row;
  }

  function applyDisabledState() {
    const root = document.getElementById(ROOT_ID);
    if (!root) return;
    const disabled = !searchHasQuery();
    root.classList.toggle('is-disabled', disabled);
    root.querySelectorAll('input[type=range]').forEach(s => { s.disabled = disabled; });
  }

  function buildUI() {
    const root = document.getElementById(ROOT_ID);
    if (!root || root.dataset.built === '1') return;
    root.dataset.built = '1';
    root.classList.add('vs-root');

    const head = document.createElement('div');
    head.className = 'vs-head';
    head.innerHTML = `
      <span class="vs-title">
        <span class="vs-spark">✦</span>
        Vibe
        <span class="vs-tag">embedding bias · live re-rank</span>
      </span>
      <span class="vs-badge" title="Active vibe bias">neutral</span>
    `;
    root.appendChild(head);

    const grid = document.createElement('div');
    grid.className = 'vs-grid';
    AXES.forEach(a => grid.appendChild(buildRow(a)));
    root.appendChild(grid);

    const foot = document.createElement('div');
    foot.className = 'vs-foot';
    foot.innerHTML = `
      <button type="button" class="vs-resetall" data-cursor="link">Reset all</button>
      <span class="vs-hint">Drag a slider to nudge the query along that axis. Re-ranks every 250 ms.</span>
    `;
    foot.querySelector('.vs-resetall').addEventListener('click', e => {
      e.preventDefault();
      const had = AXES.some(a => Math.abs(window.__vibe[a.key]) > 0.01);
      root.querySelectorAll('.vs-row').forEach(r => setSliderValue(r, 0, { silent: true }));
      if (had && searchHasQuery()) scheduleSearch();
    });
    root.appendChild(foot);

    // Disabled-until-query handling.
    applyDisabledState();
    const inp = document.getElementById('searchInput');
    if (inp) {
      inp.addEventListener('input', applyDisabledState);
      inp.addEventListener('change', applyDisabledState);
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', buildUI);
  } else {
    buildUI();
  }
})();
