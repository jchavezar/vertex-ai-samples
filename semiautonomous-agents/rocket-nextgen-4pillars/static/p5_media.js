/* =========================================================================
   Pillar 5 media module (Worker E)
   1. Full-screen photo lightbox for listing photos (result cards, property
      modal hero / mosaic / "Show all photos" grid, rooms tab, floorplan images).
   2. Instant tour player for the modal "16:9 3D Video Tour" tab:
      Veo 3.1 AI walkthrough (if present) -> pre-rendered cinematic MP4 on
      Cloud Storage -> legacy canvas. Chapter pills synced to currentTime,
      loading skeleton with an 8 s fallback (never an infinite spinner).
   Loaded at the end of <body> after the main inline script. Idempotent and
   never throws at load.
   ========================================================================= */
(function () {
  'use strict';
  try {
    if (window.__P5M && window.__P5M.version) return;
  } catch (e) { /* ignore */ }

  var P5M = { version: 'p5m-1.0' };
  window.__P5M = P5M;

  var ICON = {
    expand: '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="15 3 21 3 21 9"/><polyline points="9 21 3 21 3 15"/><line x1="21" y1="3" x2="14" y2="10"/><line x1="3" y1="21" x2="10" y2="14"/></svg>',
    grid: '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></svg>',
    close: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" aria-hidden="true"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>',
    prev: '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="15 18 9 12 15 6"/></svg>',
    next: '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="9 18 15 12 9 6"/></svg>',
    film: '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="2" y="4" width="20" height="16" rx="2"/><line x1="7" y1="4" x2="7" y2="20"/><line x1="17" y1="4" x2="17" y2="20"/><line x1="2" y1="12" x2="22" y2="12"/></svg>',
    spark: '<svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 2l1.9 6.1L20 10l-6.1 1.9L12 18l-1.9-6.1L4 10l6.1-1.9z"/><path d="M19 15l.9 2.1L22 18l-2.1.9L19 21l-.9-2.1L16 18l2.1-.9z"/></svg>',
    play: '<svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><polygon points="6 4 20 12 6 20 6 4"/></svg>',
    canvas: '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>'
  };

  // ---------------------------------------------------------------- helpers
  function $(id) { return document.getElementById(id); }
  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }
  function baseUrl(u) { return String(u || '').split('#')[0].split('?')[0]; }
  function sameUrl(a, b) { return !!a && !!b && baseUrl(a) === baseUrl(b); }
  function pad2(n) { return (n < 10 ? '0' : '') + n; }
  function fmtTime(s) {
    s = Math.max(0, Math.floor(s || 0));
    return Math.floor(s / 60) + ':' + pad2(s % 60);
  }
  function clamp01(x) { return x < 0 ? 0 : x > 1 ? 1 : x; }
  function safe(fn) {
    return function () {
      try { return fn.apply(this, arguments); } catch (e) { try { console.warn('[p5m]', e); } catch (e2) { /* ignore */ } }
    };
  }

  // Legacy top-level bindings from the main inline script (shared global scope).
  function activeItem() {
    try { return (typeof p5ActiveModalItem !== 'undefined' && p5ActiveModalItem) ? p5ActiveModalItem : null; } catch (e) { return null; }
  }
  function catalogItem(id) {
    try { if (typeof p5CatalogById !== 'undefined' && p5CatalogById && p5CatalogById[id]) return p5CatalogById[id]; } catch (e) { /* ignore */ }
    try {
      if (typeof p5Results !== 'undefined' && Array.isArray(p5Results)) {
        for (var i = 0; i < p5Results.length; i++) if (p5Results[i] && p5Results[i].id === id) return p5Results[i];
      }
    } catch (e) { /* ignore */ }
    var a = activeItem();
    return a && a.id === id ? a : null;
  }
  function cardRoomIdx(id) {
    try { return (typeof p5CardRoomIdx !== 'undefined' && p5CardRoomIdx && p5CardRoomIdx[id]) || 0; } catch (e) { return 0; }
  }
  function slidesFor(item) {
    var rooms = (item && Array.isArray(item.rooms)) ? item.rooms : [];
    var out = [];
    rooms.forEach(function (r) {
      if (!r || !r.image_url) return;
      out.push({
        src: r.image_url,
        title: r.title || '',
        sub: [r.dimensions, r.level].filter(Boolean).join(' · '),
        note: r.caption || '',
        roomId: r.room_id || ''
      });
    });
    if (!out.length && item && item.hero_exterior_url) out.push({ src: item.hero_exterior_url, title: item.title || '', sub: '', note: '' });
    return out;
  }
  function indexOfSrc(slides, src) {
    for (var i = 0; i < slides.length; i++) if (sameUrl(slides[i].src, src)) return i;
    return -1;
  }

  var imgCache = {};
  function preload(src) {
    if (!src || imgCache[src]) return imgCache[src];
    var im = new Image();
    im.decoding = 'async';
    im.src = src;
    imgCache[src] = im;
    return im;
  }

  // ============================================================ LIGHTBOX
  var LB = {
    el: null, img: null, slides: [], idx: 0, item: null, isOpen: false, gridFromSingle: false,
    lastFocus: null, touchX: null
  };

  function lbBuild() {
    if (LB.el) return LB.el;
    var el = document.createElement('div');
    el.className = 'p5m-lb';
    el.id = 'p5m-lightbox';
    el.setAttribute('role', 'dialog');
    el.setAttribute('aria-modal', 'true');
    el.setAttribute('aria-label', 'Listing photo viewer');
    el.innerHTML =
      '<div class="p5m-lb-top">' +
        '<div class="p5m-lb-heading"><span class="p5m-lb-kicker" id="p5m-lb-kicker"></span><span class="p5m-lb-name" id="p5m-lb-name"></span></div>' +
        '<div class="p5m-lb-actions">' +
          '<span class="p5m-lb-count" id="p5m-lb-count" aria-live="polite">1 / 1</span>' +
          '<button type="button" class="p5m-lb-btn" data-act="grid" id="p5m-lb-gridbtn" title="All photos (G)">' + ICON.grid + '<span>All photos</span></button>' +
          '<button type="button" class="p5m-lb-btn" data-act="close" title="Close (Esc)" aria-label="Close photo viewer">' + ICON.close + '</button>' +
        '</div>' +
      '</div>' +
      '<div class="p5m-lb-stage" id="p5m-lb-stage">' +
        '<button type="button" class="p5m-lb-nav prev" data-act="prev" aria-label="Previous photo">' + ICON.prev + '</button>' +
        '<img class="p5m-lb-img" id="p5m-lb-img" alt="" draggable="false" />' +
        '<div class="p5m-lb-spin"></div>' +
        '<button type="button" class="p5m-lb-nav next" data-act="next" aria-label="Next photo">' + ICON.next + '</button>' +
      '</div>' +
      '<div class="p5m-lb-caption"><div class="p5m-lb-cap-title" id="p5m-lb-cap-title"></div><div class="p5m-lb-cap-sub" id="p5m-lb-cap-sub"></div><div class="p5m-lb-cap-note" id="p5m-lb-cap-note"></div></div>' +
      '<div class="p5m-lb-strip" id="p5m-lb-strip" role="listbox" aria-label="Photo thumbnails"></div>' +
      '<div class="p5m-lb-grid" id="p5m-lb-grid"></div>';
    document.body.appendChild(el);
    LB.el = el;
    LB.img = $('p5m-lb-img');

    el.addEventListener('click', safe(function (e) {
      var act = e.target.closest('[data-act]');
      if (act) {
        e.stopPropagation();
        var a = act.getAttribute('data-act');
        if (a === 'close') lbClose();
        else if (a === 'prev') lbGo(-1);
        else if (a === 'next') lbGo(1);
        else if (a === 'grid') lbToggleGrid();
        return;
      }
      var thumb = e.target.closest('.p5m-lb-thumb');
      if (thumb) { lbShowIndex(parseInt(thumb.getAttribute('data-i'), 10) || 0, 0); return; }
      var tile = e.target.closest('.p5m-lb-tile');
      if (tile) {
        el.classList.remove('grid-mode');
        lbShowIndex(parseInt(tile.getAttribute('data-i'), 10) || 0, 0, tile.querySelector('img'));
        return;
      }
      // Click outside the photo (stage background) closes.
      if (e.target.id === 'p5m-lb-stage' || e.target === el) lbClose();
    }));
    var stage = $('p5m-lb-stage');
    stage.addEventListener('pointerdown', function (e) { LB.touchX = e.pointerType === 'mouse' ? null : e.clientX; });
    stage.addEventListener('pointerup', safe(function (e) {
      if (LB.touchX == null) return;
      var dx = e.clientX - LB.touchX;
      LB.touchX = null;
      if (Math.abs(dx) > 45) lbGo(dx < 0 ? 1 : -1);
    }));
    LB.img.addEventListener('load', function () { el.classList.remove('loading'); lbFit(); });
    LB.img.addEventListener('error', function () { el.classList.remove('loading'); });
    window.addEventListener('resize', safe(function () { if (LB.isOpen) lbFit(); }));
    return el;
  }

  function lbFit() {
    var stage = $('p5m-lb-stage');
    var img = LB.img;
    if (!stage || !img) return;
    var cs = getComputedStyle(stage);
    var sw = stage.clientWidth - parseFloat(cs.paddingLeft) - parseFloat(cs.paddingRight);
    var sh = stage.clientHeight - parseFloat(cs.paddingTop) - parseFloat(cs.paddingBottom);
    var nw = img.naturalWidth || 16, nh = img.naturalHeight || 9;
    var ar = nw / nh;
    var w = Math.max(80, Math.min(sw, sh * ar));
    img.style.width = Math.round(w) + 'px';
    img.style.height = Math.round(w / ar) + 'px';
  }

  function lbOpen(slides, idx, opts) {
    opts = opts || {};
    if (!slides || !slides.length) return;
    lbBuild();
    LB.slides = slides;
    LB.item = opts.item || null;
    LB.idx = Math.max(0, Math.min(slides.length - 1, idx || 0));
    LB.lastFocus = document.activeElement;
    var it = LB.item;
    $('p5m-lb-kicker').textContent = it ? [it.id, it.city].filter(Boolean).join(' · ') : 'Listing photos';
    $('p5m-lb-name').textContent = it ? (it.title || '') : '';
    $('p5m-lb-strip').innerHTML = slides.map(function (s, i) {
      return '<button type="button" class="p5m-lb-thumb" role="option" data-i="' + i + '" title="' + esc(s.title) + '"><img src="' + esc(s.src) + '" alt="" loading="lazy" /></button>';
    }).join('');
    $('p5m-lb-grid').innerHTML = slides.map(function (s, i) {
      return '<button type="button" class="p5m-lb-tile" data-i="' + i + '" style="animation-delay:' + Math.min(i * 22, 300) + 'ms">' +
        '<img src="' + esc(s.src) + '" alt="' + esc(s.title) + '" loading="lazy" />' +
        '<span class="p5m-lb-tile-n">' + (i + 1) + ' / ' + slides.length + '</span>' +
        '<span class="p5m-lb-tile-cap"><span class="p5m-lb-tile-t">' + esc(s.title) + '</span><span class="p5m-lb-tile-s">' + esc(s.sub) + '</span></span>' +
        '</button>';
    }).join('');
    $('p5m-lb-gridbtn').querySelector('span').textContent = 'All ' + slides.length + ' photos';
    var el = LB.el;
    el.classList.add('open');
    el.classList.toggle('grid-mode', !!opts.grid);
    LB.gridFromSingle = false;
    LB.isOpen = true;
    // force reflow so the opacity transition runs
    void el.offsetWidth;
    el.classList.add('visible');
    lbShowIndex(LB.idx, 0, opts.grid ? null : opts.origin);
    var focusEl = opts.grid ? el.querySelector('.p5m-lb-tile') : el.querySelector('[data-act="next"]');
    try { if (focusEl) focusEl.focus({ preventScroll: true }); } catch (e) { /* ignore */ }
  }

  function lbShowIndex(i, dir, originEl) {
    var n = LB.slides.length;
    if (!n) return;
    LB.idx = ((i % n) + n) % n;
    var s = LB.slides[LB.idx];
    var img = LB.img;
    var cached = imgCache[s.src];
    var ready = cached && cached.complete && cached.naturalWidth > 0;
    if (!ready && !(originEl && originEl.complete)) LB.el.classList.add('loading');
    img.alt = s.title || 'Listing photo';
    if (img.getAttribute('src') !== s.src) img.src = s.src;
    else LB.el.classList.remove('loading');
    lbFit();
    $('p5m-lb-cap-title').textContent = s.title || '';
    $('p5m-lb-cap-sub').textContent = s.sub || '';
    $('p5m-lb-cap-note').textContent = s.note || '';
    $('p5m-lb-count').textContent = (LB.idx + 1) + ' / ' + n;
    var strip = $('p5m-lb-strip');
    Array.prototype.forEach.call(strip.children, function (b, k) {
      var on = k === LB.idx;
      b.classList.toggle('active', on);
      b.setAttribute('aria-selected', on ? 'true' : 'false');
    });
    var th = strip.children[LB.idx];
    if (th) {
      var left = th.offsetLeft - strip.clientWidth / 2 + th.clientWidth / 2;
      try { strip.scrollTo({ left: Math.max(0, left), behavior: 'smooth' }); } catch (e) { strip.scrollLeft = left; }
    }
    // Animations: zoom-in from the clicked photo (FLIP), or a directional slide.
    try {
      if (originEl && originEl.getBoundingClientRect && img.animate) {
        var r0 = originEl.getBoundingClientRect();
        var r1 = img.getBoundingClientRect();
        if (r0.width > 4 && r1.width > 4) {
          var dx = (r0.left + r0.width / 2) - (r1.left + r1.width / 2);
          var dy = (r0.top + r0.height / 2) - (r1.top + r1.height / 2);
          var sc = Math.max(r0.width / r1.width, r0.height / r1.height);
          img.animate([
            { transform: 'translate(' + dx + 'px,' + dy + 'px) scale(' + sc + ')', opacity: 0.35, borderRadius: '16px' },
            { transform: 'none', opacity: 1, borderRadius: '10px' }
          ], { duration: 360, easing: 'cubic-bezier(0.2, 0.8, 0.2, 1)' });
        }
      } else if (dir && img.animate) {
        img.animate([
          { transform: 'translateX(' + (dir > 0 ? 36 : -36) + 'px)', opacity: 0.2 },
          { transform: 'none', opacity: 1 }
        ], { duration: 240, easing: 'cubic-bezier(0.2, 0.8, 0.2, 1)' });
      }
    } catch (e) { /* ignore */ }
    // Preload neighbours.
    [1, -1, 2, -2].forEach(function (d) { var t = LB.slides[(LB.idx + d + n) % n]; if (t) preload(t.src); });
    var prevBtn = LB.el.querySelector('.p5m-lb-nav.prev');
    var nextBtn = LB.el.querySelector('.p5m-lb-nav.next');
    if (prevBtn) prevBtn.disabled = n < 2;
    if (nextBtn) nextBtn.disabled = n < 2;
  }

  function lbGo(d) {
    if (!LB.isOpen) return;
    if (LB.el.classList.contains('grid-mode')) return;
    lbShowIndex(LB.idx + d, d);
  }

  function lbToggleGrid() {
    if (!LB.isOpen) return;
    var on = !LB.el.classList.contains('grid-mode');
    LB.el.classList.toggle('grid-mode', on);
    LB.gridFromSingle = on;
    if (on) {
      var tile = LB.el.querySelectorAll('.p5m-lb-tile')[LB.idx];
      if (tile) { try { tile.scrollIntoView({ block: 'nearest' }); tile.focus({ preventScroll: true }); } catch (e) { /* ignore */ } }
    }
  }

  function lbClose() {
    if (!LB.el || !LB.isOpen) return;
    LB.isOpen = false;
    var el = LB.el;
    el.classList.remove('visible');
    setTimeout(function () { if (!LB.isOpen) { el.classList.remove('open'); el.classList.remove('grid-mode'); } }, 230);
    try { if (LB.lastFocus && LB.lastFocus.focus) LB.lastFocus.focus({ preventScroll: true }); } catch (e) { /* ignore */ }
  }

  // Keyboard (capture phase so the property modal never sees keys meant for us).
  window.addEventListener('keydown', function (e) {
    if (!LB.isOpen) return;
    var k = e.key;
    var handled = true;
    if (k === 'Escape') {
      if (LB.el.classList.contains('grid-mode') && LB.gridFromSingle) { LB.el.classList.remove('grid-mode'); LB.gridFromSingle = false; }
      else lbClose();
    } else if (k === 'ArrowRight') lbGo(1);
    else if (k === 'ArrowLeft') lbGo(-1);
    else if (k === 'Home') lbShowIndex(0, -1);
    else if (k === 'End') lbShowIndex(LB.slides.length - 1, 1);
    else if (k === 'g' || k === 'G') lbToggleGrid();
    else handled = false;
    if (handled) { e.preventDefault(); e.stopPropagation(); if (e.stopImmediatePropagation) e.stopImmediatePropagation(); }
  }, true);

  P5M.openLightbox = safe(lbOpen);
  P5M.closeLightbox = safe(lbClose);
  P5M.openListingPhotos = safe(function (listingOrId, startSrcOrIdx, originEl, grid) {
    var item = typeof listingOrId === 'string' ? catalogItem(listingOrId) : (listingOrId || activeItem());
    if (!item) return;
    var slides = slidesFor(item);
    var idx = typeof startSrcOrIdx === 'number' ? startSrcOrIdx : indexOfSrc(slides, startSrcOrIdx);
    lbOpen(slides, idx < 0 ? 0 : idx, { item: item, origin: originEl, grid: !!grid });
  });

  // ---------------------------------------------- modal photo affordances
  function addBadge(host) {
    if (!host || host.querySelector('.p5m-expand-badge')) return;
    var b = document.createElement('span');
    b.className = 'p5m-expand-badge';
    b.innerHTML = ICON.expand + '<span>Expand</span>';
    host.appendChild(b);
  }

  var enhanceModal = safe(function () {
    var item = activeItem();
    if (!item) return;
    var slides = slidesFor(item);
    var bento = $('re-modal-bento');
    if (bento) {
      var hero = bento.querySelector('.abnb-mosaic-main');
      if (hero) {
        hero.classList.add('p5m-zoomable');
        hero.onclick = safe(function () {
          var img = $('re-bento-hero-img');
          var i = indexOfSrc(slides, img && img.getAttribute('src'));
          lbOpen(slides, i < 0 ? 0 : i, { item: item, origin: img });
        });
        addBadge(hero);
      }
      Array.prototype.forEach.call(bento.querySelectorAll('.abnb-mosaic-cell'), function (cell) {
        var img = cell.querySelector('img');
        if (!img) return;
        cell.classList.add('p5m-zoomable');
        cell.onclick = safe(function (e) {
          if (e.target.closest('.abnb-show-all-photos-btn')) return;
          var i = indexOfSrc(slides, img.getAttribute('src'));
          lbOpen(slides, i < 0 ? 0 : i, { item: item, origin: img });
        });
      });
      var showAll = bento.querySelector('.abnb-show-all-photos-btn');
      if (showAll) {
        showAll.innerHTML = '<span style="display:inline-flex;align-items:center;gap:6px;">' + ICON.grid + ' Show all ' + slides.length + ' photos</span>';
        showAll.onclick = safe(function (e) {
          e.stopPropagation();
          lbOpen(slides, 0, { item: item, grid: true });
        });
      }
    }
    var grid = $('re-modal-rooms-grid');
    if (grid) {
      Array.prototype.forEach.call(grid.children, function (card) {
        var img = card.querySelector('img');
        if (!img) return;
        card.classList.add('p5m-zoomable');
        card.onclick = safe(function () {
          var i = indexOfSrc(slides, img.getAttribute('src'));
          lbOpen(slides, i < 0 ? 0 : i, { item: item, origin: img });
        });
        if (img.parentElement) addBadge(img.parentElement);
      });
    }
    ['re-fp-selected-img', 're-modal-3d-fp-img'].forEach(function (id) {
      var img = $(id);
      if (!img || img.getAttribute('data-p5m')) return;
      img.setAttribute('data-p5m', '1');
      img.classList.add('p5m-zoomable');
      img.addEventListener('click', safe(function () {
        var cur = activeItem() || item;
        var sl = slidesFor(cur);
        var src = img.getAttribute('src');
        var i = indexOfSrc(sl, src);
        if (i < 0 && src) { sl = [{ src: src, title: id === 're-modal-3d-fp-img' ? '3D Isometric Floorplan' : (($('re-fp-selected-title') || {}).textContent || ''), sub: '', note: '' }]; i = 0; }
        lbOpen(sl, i, { item: cur, origin: img });
      }));
    });
    // Warm the tour video when the user heads for the tour tab.
    var tab = $('re-mtab-walkthrough');
    if (tab && !tab.getAttribute('data-p5m')) {
      tab.setAttribute('data-p5m', '1');
      tab.addEventListener('pointerenter', safe(function () { warmTour(); }));
    }
    loadManifest(false);
  });

  // ------------------------------------------------- result-card expand
  function decorateCards() {
    var medias = document.querySelectorAll('.abnb-card-media:not([data-p5m])');
    Array.prototype.forEach.call(medias, function (media) {
      media.setAttribute('data-p5m', '1');
      var img = media.querySelector('img.abnb-card-img') || media.querySelector('img');
      if (!img) return;
      var id = (img.id || '').replace(/^re-card-img-/, '');
      if (!id) return;
      var b = document.createElement('button');
      b.type = 'button';
      b.className = 'p5m-card-expand';
      b.title = 'View photos full screen';
      b.setAttribute('aria-label', 'View listing photos full screen');
      b.innerHTML = ICON.expand;
      b.addEventListener('click', safe(function (e) {
        e.preventDefault();
        e.stopPropagation();
        var it = catalogItem(id);
        if (!it) return;
        var sl = slidesFor(it);
        var i = indexOfSrc(sl, img.getAttribute('src'));
        lbOpen(sl, i < 0 ? cardRoomIdx(id) : i, { item: it, origin: img });
      }));
      media.appendChild(b);
    });
  }
  var cardsQueued = false;
  function queueDecorate() {
    if (cardsQueued) return;
    cardsQueued = true;
    requestAnimationFrame(function () { cardsQueued = false; try { decorateCards(); } catch (e) { /* ignore */ } });
  }

  // ============================================================ TOUR PLAYER
  var TOUR = {
    manifest: null, fetchedAt: 0, loading: null, token: 0, timer: 0, raf: 0,
    cur: null, cands: [], idx: 0, ac: null, warmed: '', canvasMode: false
  };
  var ORIG = {};

  function fetchJSON(url) {
    return fetch(url, { credentials: 'same-origin', cache: 'no-store' }).then(function (r) {
      if (!r.ok) throw new Error('HTTP ' + r.status);
      return r.json();
    });
  }
  function loadManifest(force) {
    var now = Date.now();
    if (!force && TOUR.manifest && now - TOUR.fetchedAt < 30000) return Promise.resolve(TOUR.manifest);
    if (TOUR.loading) return TOUR.loading;
    TOUR.loading = fetchJSON('/api/pillar5/tours-manifest')
      .then(function (d) {
        if (!d || typeof d !== 'object' || (!d.cinematic && !d.veo)) throw new Error('bad manifest');
        return { cinematic: d.cinematic || {}, veo: d.veo || {} };
      })
      .catch(function () {
        return fetchJSON('/static/tours_manifest.json?ts=' + Math.floor(now / 30000))
          .then(function (c) { return { cinematic: (c && typeof c === 'object') ? c : {}, veo: {} }; });
      })
      .then(function (m) { TOUR.manifest = m; TOUR.fetchedAt = Date.now(); TOUR.loading = null; return m; })
      .catch(function () { TOUR.loading = null; return TOUR.manifest || { cinematic: {}, veo: {} }; });
    return TOUR.loading;
  }
  P5M.loadManifest = loadManifest;

  function candidatesFor(id, m, prefer) {
    var out = [];
    var v = m && m.veo && m.veo[id];
    var c = m && m.cinematic && m.cinematic[id];
    if (v && v.url) out.push(Object.assign({ kind: 'veo' }, v));
    if (c && c.url) out.push(Object.assign({ kind: 'cinematic' }, c));
    if (prefer) out.sort(function (a, b) { return (a.kind === prefer ? 0 : 1) - (b.kind === prefer ? 0 : 1); });
    return out;
  }

  function vidEl() { return $('re-modal-walkthrough-vid'); }
  function canvasEl() { return $('re-modal-walkthrough-canvas'); }
  function tourBox() { var v = vidEl(); return v ? v.parentElement : null; }
  function tourVisible() {
    var pane = $('re-mpane-walkthrough');
    var modal = $('re-property-modal');
    return !!(pane && pane.style.display !== 'none' && modal && modal.classList.contains('open'));
  }

  function ensurePlayerUi() {
    var box = tourBox();
    if (!box) return;
    if (!$('p5m-tour-skel')) {
      var sk = document.createElement('div');
      sk.className = 'p5m-tour-skel';
      sk.id = 'p5m-tour-skel';
      sk.innerHTML = '<span class="p5m-skel-pill"><span class="p5m-ink"></span><span id="p5m-skel-text">Loading tour</span></span>';
      box.appendChild(sk);
    }
    if (!$('p5m-tour-bar')) {
      var bar = document.createElement('div');
      bar.className = 'p5m-tour-bar';
      bar.id = 'p5m-tour-bar';
      bar.innerHTML =
        '<span class="p5m-tour-badge" id="p5m-tour-badge">' + ICON.film + '<span>Cinematic Tour</span></span>' +
        '<span class="p5m-tour-srcs" id="p5m-tour-srcs" style="display:none;"></span>' +
        '<span class="p5m-tour-meta" id="p5m-tour-meta"></span>' +
        '<span class="p5m-tour-time" id="p5m-tour-time">0:00 / 0:00</span>';
      box.parentNode.insertBefore(bar, box.nextSibling);
      bar.addEventListener('click', safe(function (e) {
        var b = e.target.closest('.p5m-tour-src');
        if (!b) return;
        openTour({ prefer: b.getAttribute('data-kind'), restart: true });
      }));
    }
    var v = vidEl();
    if (v && !v.getAttribute('data-p5m')) {
      v.setAttribute('data-p5m', '1');
      v.classList.add('p5m-vid');
      ['timeupdate', 'seeked', 'loadedmetadata'].forEach(function (ev) { v.addEventListener(ev, safe(syncNow)); });
      v.addEventListener('play', safe(startSync));
    }
    var strip = $('re-wt-scene-pills');
    if (strip && !strip.getAttribute('data-p5m')) {
      strip.setAttribute('data-p5m', '1');
      strip.addEventListener('click', safe(function (e) {
        var b = e.target.closest('.p5m-chip');
        if (!b || !TOUR.cur || TOUR.canvasMode) return;
        var t = parseFloat(b.getAttribute('data-t')) || 0;
        var vv = vidEl();
        try { vv.currentTime = t + 0.04; } catch (err) { /* ignore */ }
        if (vv.paused) { var p = vv.play(); if (p && p.catch) p.catch(function () { /* ignore */ }); }
        syncNow();
      }));
    }
  }

  function showSkel(text, poster) {
    var sk = $('p5m-tour-skel');
    if (!sk) return;
    var t = $('p5m-skel-text');
    if (t) t.textContent = text || 'Loading tour';
    sk.style.backgroundImage = poster ? 'url("' + String(poster).replace(/"/g, '%22') + '")' : '';
    sk.classList.add('show');
  }
  function hideSkel() { var sk = $('p5m-tour-skel'); if (sk) sk.classList.remove('show'); }

  function setBadge(kind, c) {
    var b = $('p5m-tour-badge');
    if (!b) return;
    b.className = 'p5m-tour-badge' + (kind === 'veo' ? ' veo' : kind === 'canvas' ? ' canvas' : '');
    var label = kind === 'veo' ? 'AI Walkthrough · Veo 3.1' : kind === 'canvas' ? 'Live Canvas Tour' : 'Cinematic Tour';
    b.innerHTML = (kind === 'veo' ? ICON.spark : kind === 'canvas' ? ICON.canvas : ICON.film) + '<span>' + label + '</span>';
    var meta = $('p5m-tour-meta');
    if (meta) {
      if (kind === 'canvas') meta.textContent = 'Rendered in the browser from this listing\u2019s photos';
      else {
        var n = (c && c.chapters && c.chapters.length) || 0;
        var parts = [];
        if (n) parts.push(n + ' rooms');
        if (c && c.duration_s) parts.push(fmtTime(c.duration_s));
        parts.push(kind === 'veo' ? (c && c.model ? c.model : 'veo-3.1') : '1280\u00d7720 H.264');
        parts.push(c && c.live ? 'built on demand' : 'Cloud Storage CDN');
        meta.textContent = parts.join(' \u00b7 ');
      }
    }
    var srcs = $('p5m-tour-srcs');
    if (srcs) {
      var kinds = TOUR.cands.filter(function (x) { return !x.live; }).map(function (x) { return x.kind; });
      if (kinds.length > 1) {
        srcs.style.display = '';
        srcs.innerHTML = kinds.map(function (k) {
          return '<button type="button" class="p5m-tour-src' + (k === kind ? ' active' : '') + '" data-kind="' + k + '">' +
            (k === 'veo' ? 'AI Walkthrough' : 'Cinematic') + '</button>';
        }).join('');
      } else {
        srcs.style.display = 'none';
        srcs.innerHTML = '';
      }
    }
  }

  function renderChapters(c) {
    var strip = $('re-wt-scene-pills');
    if (!strip) return;
    var chs = (c && Array.isArray(c.chapters)) ? c.chapters : [];
    strip.classList.add('p5m-chips');
    strip.innerHTML = chs.map(function (ch, k) {
      return '<button type="button" class="p5m-chip" data-k="' + k + '" data-t="' + (Number(ch.t) || 0) + '" title="Jump to ' + esc(ch.title) + '">' +
        '<span class="p5m-chip-idx">' + pad2(k + 1) + '</span><span>' + esc(ch.title || ch.room_id || ('Scene ' + (k + 1))) + '</span>' +
        '<i class="p5m-chip-fill"></i></button>';
    }).join('');
  }

  function syncNow() {
    var c = TOUR.cur;
    var v = vidEl();
    if (!c || !v || TOUR.canvasMode) return;
    var t = v.currentTime || 0;
    var dur = (isFinite(v.duration) && v.duration > 0) ? v.duration : (c.duration_s || 0);
    var tl = $('p5m-tour-time');
    if (tl) tl.textContent = fmtTime(t) + ' / ' + fmtTime(dur);
    var chs = c.chapters || [];
    if (!chs.length) return;
    var k = 0;
    for (var j = 0; j < chs.length; j++) if (t >= (Number(chs[j].t) || 0) - 0.02) k = j;
    var pills = document.querySelectorAll('#re-wt-scene-pills .p5m-chip');
    for (var i = 0; i < pills.length; i++) {
      var b = pills[i];
      var on = i === k;
      if (b.classList.contains('active') !== on) b.classList.toggle('active', on);
      b.classList.toggle('done', i < k);
      var p = i < k ? 1 : 0;
      if (on) {
        var t0 = Number(chs[k].t) || 0;
        var t1 = k + 1 < chs.length ? (Number(chs[k + 1].t) || dur) : dur;
        p = t1 > t0 ? clamp01((t - t0) / (t1 - t0)) : 0;
      }
      b.style.setProperty('--p', p.toFixed(3));
    }
  }
  function startSync() {
    cancelAnimationFrame(TOUR.raf);
    var loop = function () {
      syncNow();
      var v = vidEl();
      if (v && !v.paused && tourVisible()) TOUR.raf = requestAnimationFrame(loop);
    };
    TOUR.raf = requestAnimationFrame(loop);
  }

  function teardown() {
    TOUR.token++;
    clearTimeout(TOUR.timer);
    cancelAnimationFrame(TOUR.raf);
    if (TOUR.ac) { try { TOUR.ac.abort(); } catch (e) { /* ignore */ } TOUR.ac = null; }
    hideSkel();
    var v = vidEl();
    if (v) { try { v.pause(); } catch (e) { /* ignore */ } }
  }
  P5M.stopTour = safe(teardown);

  function fallbackCanvas() {
    TOUR.canvasMode = true;
    TOUR.cur = null;
    hideSkel();
    setBadge('canvas', null);
    var tl = $('p5m-tour-time');
    if (tl) tl.textContent = '';
    var strip = $('re-wt-scene-pills');
    if (strip) strip.classList.remove('p5m-chips');
    if (ORIG.start) { try { ORIG.start(false); } catch (e) { /* ignore */ } }
  }

  function playCandidate(i, token, opts) {
    if (token !== TOUR.token) return;
    var c = TOUR.cands[i];
    if (!c) { fallbackCanvas(); return; }
    TOUR.idx = i;
    TOUR.cur = c;
    TOUR.canvasMode = false;
    var v = vidEl();
    var cv = canvasEl();
    if (!v) { fallbackCanvas(); return; }
    // Stop the legacy canvas loop (it would otherwise keep drawing underneath).
    try { if (typeof modalTourPlaying !== 'undefined') modalTourPlaying = false; } catch (e) { /* ignore */ }
    try { if (typeof modalTourAnimId !== 'undefined' && modalTourAnimId) { cancelAnimationFrame(modalTourAnimId); modalTourAnimId = null; } } catch (e) { /* ignore */ }
    if (cv) cv.style.display = 'none';
    v.style.display = 'block';
    setBadge(c.kind, c);
    renderChapters(c);
    showSkel(c.kind === 'veo' ? 'Loading AI walkthrough' : (c.live ? 'Building tour' : 'Loading cinematic tour'), c.poster);
    if (TOUR.ac) { try { TOUR.ac.abort(); } catch (e) { /* ignore */ } }
    var ac = typeof AbortController !== 'undefined' ? new AbortController() : null;
    TOUR.ac = ac;
    var done = false;
    var finish = function (ok) {
      if (done || token !== TOUR.token) return;
      done = true;
      clearTimeout(TOUR.timer);
      if (ac) { try { ac.abort(); } catch (e) { /* ignore */ } }
      if (ok) { hideSkel(); startSync(); syncNow(); }
      else playCandidate(i + 1, token, opts);
    };
    var lopts = ac ? { signal: ac.signal } : { once: true };
    v.addEventListener('playing', function () { finish(true); }, lopts);
    v.addEventListener('error', function () { finish(false); }, lopts);
    TOUR.timer = setTimeout(function () { finish(false); }, c.live ? 45000 : 8000);
    var sameSrc = sameUrl(v.getAttribute('src'), c.url) || v.getAttribute('src') === c.url;
    if (c.poster) v.poster = c.poster; else v.removeAttribute('poster');
    if (!sameSrc) {
      v.preload = 'auto';
      v.src = c.url;
    } else if (opts && opts.restart) {
      try { v.currentTime = 0; } catch (e) { /* ignore */ }
    }
    v.loop = true;
    v.playsInline = true;
    var attempt = function () {
      var p;
      try { p = v.play(); } catch (e) { finish(false); return; }
      if (p && p.catch) {
        p.catch(function (err) {
          if (done || token !== TOUR.token) return;
          var name = err && err.name;
          if (name === 'NotAllowedError' && !v.muted) { v.muted = true; attempt(); }
          else if (name === 'AbortError') { /* superseded by a newer load; the timer still guards us */ }
          else finish(false);
        });
      }
    };
    attempt();
    if (sameSrc && !v.paused && v.readyState >= 3) finish(true);
  }

  function openTour(opts) {
    opts = opts || {};
    var item = activeItem();
    if (!item) return;
    ensurePlayerUi();
    teardown();
    var token = TOUR.token;
    var sub = $('re-wt-header-sub');
    var go = function (m) {
      if (token !== TOUR.token) return;
      var cands = candidatesFor(item.id, m, opts.prefer);
      if (!cands.length) {
        cands.push({
          kind: 'cinematic',
          live: true,
          url: '/api/pillar5/listing-video/' + encodeURIComponent(item.id) + '?aspect=16x9',
          chapters: [],
          duration_s: 0
        });
      }
      TOUR.cands = cands;
      if (sub) {
        sub.textContent = cands[0].kind === 'veo'
          ? 'Generative AI walkthrough of ' + item.id + ' \u00b7 Veo 3.1, with this home\u2019s rooms as chapters'
          : 'Guided walkthrough of ' + item.id + ': front elevation \u2192 great room \u2192 kitchen \u2192 dining \u2192 primary suite \u2192 bath \u2192 patio \u2192 aerial';
      }
      playCandidate(0, token, opts);
    };
    if (TOUR.manifest) { go(TOUR.manifest); loadManifest(false); }
    else {
      showSkel('Loading tour', null);
      TOUR.timer = setTimeout(function () { if (token === TOUR.token && !TOUR.manifest) go({ cinematic: {}, veo: {} }); }, 8000);
      loadManifest(false).then(function (m) { clearTimeout(TOUR.timer); go(m); });
    }
  }
  P5M.openTour = safe(openTour);

  function warmTour() {
    var item = activeItem();
    var v = vidEl();
    if (!item || !v || !TOUR.manifest || TOUR.warmed === item.id) return;
    if (!v.paused) return;
    var c = candidatesFor(item.id, TOUR.manifest)[0];
    if (!c) return;
    TOUR.warmed = item.id;
    if (!sameUrl(v.getAttribute('src'), c.url)) {
      v.preload = 'auto';
      if (c.poster) v.poster = c.poster;
      v.src = c.url;
      try { v.load(); } catch (e) { /* ignore */ }
    }
  }

  // ------------------------------------------------------- legacy hooks
  var installHooks = safe(function () {
    if (typeof window.openRePropertyModal === 'function' && !window.openRePropertyModal.__p5m) {
      ORIG.open = window.openRePropertyModal;
      var wrappedOpen = function () {
        var self = this, args = arguments;
        TOUR.warmed = '';
        var r;
        try { r = ORIG.open.apply(self, args); } catch (e) { enhanceModal(); throw e; }
        return Promise.resolve(r).then(function (v) { enhanceModal(); return v; }, function (err) { enhanceModal(); throw err; });
      };
      wrappedOpen.__p5m = true;
      window.openRePropertyModal = wrappedOpen;
    }
    if (typeof window.switchReModalTab === 'function' && !window.switchReModalTab.__p5m) {
      ORIG.switchTab = window.switchReModalTab;
      var wrappedTab = function (tabKey, btnEl) {
        if (tabKey !== 'walkthrough') {
          teardown();
          return ORIG.switchTab.apply(this, arguments);
        }
        ['rooms', 'floorplan', 'walkthrough', 'reel', 'judge'].forEach(function (k) {
          var pane = $('re-mpane-' + k);
          var tab = $('re-mtab-' + k);
          if (pane) pane.style.display = k === tabKey ? 'block' : 'none';
          if (tab) tab.classList.toggle('active', k === tabKey);
        });
        try { if (typeof window.stopModalWalkthroughAndReel === 'function') window.stopModalWalkthroughAndReel(); } catch (e) { /* ignore */ }
        openTour({});
      };
      wrappedTab.__p5m = true;
      window.switchReModalTab = wrappedTab;
    }
    if (typeof window.startModalWalkthroughAnimation === 'function' && !window.startModalWalkthroughAnimation.__p5m) {
      ORIG.start = window.startModalWalkthroughAnimation;
      var wrappedStart = function (withVoice) {
        if (withVoice && typeof window.speakActiveModalPropertyTour === 'function') {
          try { window.speakActiveModalPropertyTour(document.getElementById('btn-re-modal-speak')); } catch (e) { /* ignore */ }
        }
        if (TOUR.canvasMode) return ORIG.start(false);
        openTour({});
      };
      wrappedStart.__p5m = true;
      window.startModalWalkthroughAnimation = wrappedStart;
    }
    if (typeof window.streamListingSpecificMp4 === 'function' && !window.streamListingSpecificMp4.__p5m) {
      ORIG.mp4 = window.streamListingSpecificMp4;
      var wrappedMp4 = function (aspect, btnEl) {
        if (aspect === '9:16' || aspect === true) return ORIG.mp4.apply(this, arguments);
        var btn = btnEl || $('btn-render-listing-mp4');
        if (!tourVisible()) {
          var pane = $('re-mpane-walkthrough');
          if (pane) window.switchReModalTab('walkthrough');
        }
        openTour({ prefer: 'cinematic', restart: true });
        if (btn) {
          btn.classList.add('p5m-mp4-btn-flash');
          setTimeout(function () { btn.classList.remove('p5m-mp4-btn-flash'); }, 900);
        }
      };
      wrappedMp4.__p5m = true;
      window.streamListingSpecificMp4 = wrappedMp4;
    }
    if (typeof window.closeRePropertyModal === 'function' && !window.closeRePropertyModal.__p5m) {
      ORIG.close = window.closeRePropertyModal;
      var wrappedClose = function () {
        teardown();
        lbClose();
        return ORIG.close.apply(this, arguments);
      };
      wrappedClose.__p5m = true;
      window.closeRePropertyModal = wrappedClose;
    }
    var mp4Btn = $('btn-render-listing-mp4');
    if (mp4Btn && !mp4Btn.getAttribute('data-p5m')) {
      mp4Btn.setAttribute('data-p5m', '1');
      mp4Btn.innerHTML = '<span style="display:inline-flex;align-items:center;gap:6px;">' + ICON.play + ' Play MP4 Tour \u00b7 instant</span>';
      mp4Btn.title = 'Pre-rendered 1280\u00d7720 H.264 tour served from Cloud Storage';
    }
  });

  // ------------------------------------------------------------- boot
  var boot = safe(function () {
    installHooks();
    decorateCards();
    var target = $('p5-property-grid') || document.body;
    if (typeof MutationObserver !== 'undefined' && target) {
      new MutationObserver(queueDecorate).observe(target, { childList: true, subtree: true });
      if (target !== document.body) new MutationObserver(queueDecorate).observe(document.body, { childList: true });
    }
    try {
      var l = document.createElement('link');
      l.rel = 'preconnect';
      l.href = 'https://storage.googleapis.com';
      document.head.appendChild(l);
    } catch (e) { /* ignore */ }
    loadManifest(false);
    // If the modal is already open (e.g. hot reload), enhance it now.
    var modal = $('re-property-modal');
    if (modal && modal.classList.contains('open')) enhanceModal();
  });

  try {
    boot();
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', safe(function () { installHooks(); decorateCards(); }));
  } catch (e) { /* never throw at load */ }
})();
