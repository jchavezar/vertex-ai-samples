/* =============================================================================
   Pillar 3 · "Ask Redfin 2.0" — grounded chat (Google Maps + YouTube + Google Search)
   - Renders into #pillar-3 (replaces the 3 static cards), streams NDJSON from POST /api/pillar3/chat
   - Reuses legacy #grounding-map (Leaflet, p3Map) and #p3-yt-iframe; keeps every legacy ID alive
   - Overrides window.runPillar3Grounding / speakPillar3GroundedBrief, wraps setGoogleMapLayer
   IIFE · defensive (never throws at load) · idempotent
   ============================================================================= */
(function () {
  'use strict';
  if (window.__p3ChatBooted) return;
  window.__p3ChatBooted = true;

  var API = '/api/pillar3/chat';
  var HUBS = {
    royal_oak: { id: 'royal_oak', address: '418 Elmhurst Ave, Royal Oak, MI 48067', short: '418 Elmhurst Ave', area: 'Royal Oak', price: '$460k', priceFull: '$460,000', lat: 42.4962, lng: -83.1477, yt: 'AwhBTrzzqeg', ytTitle: 'Mid-Century Craftsman & Garden Tour' },
    corktown_detroit: { id: 'corktown_detroit', address: '1420 Michigan Ave #4B, Corktown, Detroit, MI 48216', short: '1420 Michigan Ave #4B', area: 'Corktown', price: '$385k', priceFull: '$385,000', lat: 42.3314, lng: -83.0645, yt: 'PqpCeiYycVM', ytTitle: 'Sunlit Modern Interior & Custom Kitchen Tour' },
    ann_arbor: { id: 'ann_arbor', address: '2105 Devonshire Rd, Ann Arbor, MI 48104', short: '2105 Devonshire Rd', area: 'Ann Arbor', price: '$695k', priceFull: '$695,000', lat: 42.2682, lng: -83.7191, yt: 'EobMnSpjfTU', ytTitle: 'Mid-Century Modern Sanctuary & Courtyard Tour' }
  };
  var TOOL_LABEL = { maps: 'Google Maps', youtube: 'YouTube', search: 'Google Search' };

  function svg(body, extra) { return '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"' + (extra || '') + '>' + body + '</svg>'; }
  var I = {
    pin: svg('<path d="M12 21s-7-6.5-7-12a7 7 0 1 1 14 0c0 5.5-7 12-7 12z"/><circle cx="12" cy="9" r="2.5"/>'),
    map: svg('<polygon points="1 6 1 22 8 18 16 22 23 18 23 2 16 6 8 2 1 6"/><line x1="8" y1="2" x2="8" y2="18"/><line x1="16" y1="6" x2="16" y2="22"/>'),
    yt: svg('<rect x="2" y="4" width="20" height="16" rx="4"/><polygon points="10 9 15 12 10 15 10 9"/>'),
    search: svg('<circle cx="11" cy="11" r="7.5"/><line x1="21" y1="21" x2="16.4" y2="16.4"/>'),
    globe: svg('<circle cx="12" cy="12" r="9.5"/><line x1="2.5" y1="12" x2="21.5" y2="12"/><path d="M12 2.5a14.5 14.5 0 0 1 4 9.5 14.5 14.5 0 0 1-4 9.5 14.5 14.5 0 0 1-4-9.5 14.5 14.5 0 0 1 4-9.5z"/>'),
    link: svg('<path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/>'),
    send: svg('<line x1="12" y1="19" x2="12" y2="5"/><polyline points="5 12 12 5 19 12"/>', ' stroke-width="2.3"'),
    stop: '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="7" y="7" width="10" height="10" rx="2" fill="currentColor"/></svg>',
    copy: svg('<rect x="9" y="9" width="12" height="12" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>'),
    check: svg('<polyline points="20 6 9 17 4 12"/>', ' stroke-width="2.4"'),
    vol: svg('<polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><path d="M15.54 8.46a5 5 0 0 1 0 7.07"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14"/>'),
    x: svg('<line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>', ' stroke-width="2.2"'),
    down: svg('<line x1="12" y1="5" x2="12" y2="19"/><polyline points="19 12 12 19 5 12"/>'),
    home: svg('<path d="M3 10.5 12 3l9 7.5"/><path d="M5 9.5V21h14V9.5"/><path d="M10 21v-6h4v6"/>', ' stroke-width="2.2"'),
    play: svg('<polygon points="7 4 20 12 7 20 7 4"/>'),
    spark: '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 1.8c.75 5.2 4.1 8.6 9.4 9.4v1.6c-5.3.8-8.65 4.2-9.4 9.4h-.02c-.75-5.2-4.1-8.6-9.38-9.4v-1.6C7.9 10.4 11.25 7 12 1.8z"/></svg>',
    layers: svg('<polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/>')
  };
  var TOOL_ICON = { maps: I.map, youtube: I.yt, search: I.search };
  var STARTERS = [
    { q: "What's walkable near this home?", sub: 'Google Maps grounding', icon: I.pin },
    { q: 'Summarize the YouTube walkthrough', sub: 'YouTube video understanding', icon: I.yt },
    { q: '2026 property tax & down-payment grants here', sub: 'Google Search grounding', icon: I.search },
    { q: 'Give me the full grounded brief on this home', sub: 'Maps + YouTube + Search together', icon: I.spark }
  ];
  var CHIPS = [
    { q: "What's walkable near this home?", icon: I.pin },
    { q: 'Summarize the YouTube walkthrough', icon: I.yt },
    { q: '2026 property tax & down-payment grants here', icon: I.search },
    { q: 'Best schools and parks within a mile?', icon: I.pin },
    { q: 'Give me the full grounded brief on this home', icon: I.spark }
  ];

  var S = {
    hub: 'royal_oak', messages: [], streaming: false, ctrl: null, customYt: null,
    layer: null, homeMarker: null, placeMarkers: [], bounds: null, needsFit: true, ownMap: null, ownTile: null,
    lastAnswer: '', lastResult: null, moments: [], root: null, els: {}, stick: true, seq: 0
  };

  // ---------- small helpers ----------
  function $(sel, root) { return (root || document).querySelector(sel); }
  function esc(s) { return String(s == null ? '' : s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#39;'); }
  function nowLabel() { try { return new Date().toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' }); } catch (e) { return ''; } }
  function safe(fn) { return function () { try { return fn.apply(this, arguments); } catch (e) { try { console.warn('[p3_chat]', e); } catch (_) {} } }; }
  function getMap() { if (S.ownMap) return S.ownMap; try { return (typeof p3Map !== 'undefined' && p3Map) ? p3Map : null; } catch (e) { return null; } }
  function setLegacyHub(id) { try { currentP3Hub = id; } catch (e) {} }
  function setMapInitialized() { try { mapInitialized = true; } catch (e) {} }
  function authSuffix() { try { var t = new URLSearchParams(location.search).get('auth_token'); return t ? ('?auth_token=' + encodeURIComponent(t)) : ''; } catch (e) { return ''; } }
  function parseYt(text) {
    var m = String(text || '').match(/(?:https?:\/\/)?(?:www\.|m\.|music\.)?(?:youtube\.com\/(?:watch\?(?:[^\s#]*&)?v=|shorts\/|embed\/|live\/)|youtu\.be\/)([A-Za-z0-9_-]{11})/);
    return m ? { id: m[1], url: 'https://www.youtube.com/watch?v=' + m[1] } : null;
  }
  function tsToSec(ts) { var p = String(ts).split(':').map(Number); return p.length === 3 ? p[0] * 3600 + p[1] * 60 + p[2] : (p[0] * 60 + (p[1] || 0)); }
  function plain(md) {
    return String(md || '')
      .replace(/\[([^\]]+)\]\((https?:[^)]+)\)/g, '$1')
      .replace(/\*\*|__|`/g, '')
      .replace(/^\s*[-*•]\s+/gm, '• ')
      .replace(/\[((?:\d{1,2}:)?\d{1,2}:\d{2}[^\]]*)\]/g, '($1)')
      .replace(/\n{3,}/g, '\n\n').trim();
  }
  function speakable(md) { return plain(md).replace(/•\s*/g, '').replace(/\(((?:\d{1,2}:)?\d{1,2}:\d{2})[^)]*\)/g, '').replace(/\s{2,}/g, ' ').trim(); }

  // ---------- markdown (safe, tiny) ----------
  function inl(s) {
    var keep = [];
    var t = esc(s);
    t = t.replace(/`([^`]+)`/g, function (m, c) { keep.push('<code>' + c + '</code>'); return '\u0001' + (keep.length - 1) + '\u0001'; });
    t = t.replace(/\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g, function (m, label, url) { keep.push('<a href="' + url + '" target="_blank" rel="noopener noreferrer">' + label + '</a>'); return '\u0001' + (keep.length - 1) + '\u0001'; });
    t = t.replace(/\[((?:\d{1,2}:)?\d{1,2}:\d{2}(?:\s*(?:,|–|-|to)\s*(?:\d{1,2}:)?\d{1,2}:\d{2})*)\]/g, function (m, grp) {
      var html = grp.split(/\s*(?:,|–|-|to)\s*/).map(function (ts) { return '<button type="button" class="p3c-ts" data-ts="' + ts + '" title="Play the walkthrough at ' + ts + '">' + ts + '</button>'; }).join(' ');
      keep.push(html); return '\u0001' + (keep.length - 1) + '\u0001';
    });
    t = t.replace(/\*\*([^*]+?)\*\*/g, '<strong>$1</strong>').replace(/__([^_]+?)__/g, '<strong>$1</strong>');
    t = t.replace(/(^|[\s(])\*([^*\s][^*]*?)\*(?=[\s).,;:!?]|$)/g, '$1<em>$2</em>');
    t = t.replace(/(^|[\s(])_([^_\s][^_]*?)_(?=[\s).,;:!?]|$)/g, '$1<em>$2</em>');
    return t.replace(/\u0001(\d+)\u0001/g, function (m, i) { return keep[+i]; });
  }
  function md(src) {
    var lines = String(src || '').replace(/\r/g, '').split('\n');
    var html = '', list = null, para = [];
    function flush() { if (para.length) { html += '<p>' + para.map(inl).join('<br>') + '</p>'; para = []; } }
    function close() { if (list) { html += '</' + list + '>'; list = null; } }
    lines.forEach(function (raw) {
      var line = raw.replace(/\s+$/, ''), m;
      if (!line.trim()) { flush(); close(); return; }
      if ((m = line.match(/^(\s*)[-*•]\s+(.*)$/))) { flush(); if (list !== 'ul') { close(); html += '<ul>'; list = 'ul'; } html += '<li' + (m[1].length >= 2 ? ' class="p3c-sub"' : '') + '>' + inl(m[2]) + '</li>'; return; }
      if ((m = line.match(/^\s*(\d+)[.)]\s+(.*)$/))) { flush(); if (list !== 'ol') { close(); html += '<ol>'; list = 'ol'; } html += '<li>' + inl(m[2]) + '</li>'; return; }
      if ((m = line.match(/^#{1,6}\s+(.*)$/))) { flush(); close(); html += '<p class="p3c-h">' + inl(m[1]) + '</p>'; return; }
      close(); para.push(line.trim());
    });
    flush(); close();
    return html;
  }

  // ---------- DOM build ----------
  function build() {
    var pane = document.getElementById('pillar-3');
    if (!pane) return false;
    if (pane.querySelector('.p3c-root')) return true;

    var mapEl = document.getElementById('grounding-map');
    if (!mapEl) { mapEl = document.createElement('div'); mapEl.id = 'grounding-map'; }
    var ytEl = document.getElementById('p3-yt-iframe');
    if (!ytEl) {
      ytEl = document.createElement('iframe'); ytEl.id = 'p3-yt-iframe';
      ytEl.src = 'https://www.youtube.com/embed/' + HUBS.royal_oak.yt + '?enablejsapi=1&rel=0';
    }
    ytEl.setAttribute('title', 'YouTube property walkthrough');
    ytEl.setAttribute('allow', 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share; compute-pressure');
    ytEl.setAttribute('allowfullscreen', '');
    ytEl.removeAttribute('width'); ytEl.removeAttribute('height');

    var moat = pane.querySelector('.moat-strip');
    // Legacy nodes that legacy code reads without null checks -> keep alive in a hidden shim.
    var shim = document.createElement('div');
    shim.id = 'p3c-legacy-shim'; shim.className = 'p3c-legacy-hidden'; shim.setAttribute('aria-hidden', 'true');
    ['p3-lat-badge', 'p3-maps-summary', 'p3-maps-pills', 'p3-yt-summary', 'p3-search-summary', 'p3-search-pills', 'btn-p3-ground', 'btn-p3-tts'].forEach(function (id) {
      var el = document.getElementById(id);
      if (!el) { el = document.createElement(id.indexOf('btn') === 0 ? 'button' : 'div'); el.id = id; }
      if (el.tagName === 'BUTTON') { el.removeAttribute('onclick'); el.type = 'button'; }
      if (el.parentNode) el.parentNode.removeChild(el);
      shim.appendChild(el);
    });
    // IDs we re-create as live, visible controls (agent ghost-cursor targets).
    ['p3-hub-royal_oak', 'p3-hub-corktown_detroit', 'p3-hub-ann_arbor', 'p3-custom-yt', 'btn-map-road', 'btn-map-sat'].forEach(function (id) {
      var el = document.getElementById(id); if (el) el.removeAttribute('id');
    });
    if (mapEl.parentNode) mapEl.parentNode.removeChild(mapEl);
    if (ytEl.parentNode) ytEl.parentNode.removeChild(ytEl);
    if (moat && moat.parentNode) moat.parentNode.removeChild(moat);

    pane.innerHTML = '';
    var root = document.createElement('div');
    root.className = 'p3c-root'; root.id = 'p3c-root';

    if (!moat) { moat = document.createElement('div'); moat.className = 'moat-strip'; }
    moat.classList.add('p3c-moat');
    moat.innerHTML =
      '<div style="min-width:0;">' +
        '<div class="moat-title">Pillar 3 · "Ask Redfin 2.0" — Grounded Home Chat</div>' +
        '<div class="moat-subtitle">Gemini 3.8 Flash, grounded live in Google Maps, YouTube and Google Search — with clickable sources.</div>' +
      '</div>' +
      '<div class="p3c-tools" aria-label="Grounding tools">' +
        '<span class="p3c-tools-label">Grounding</span>' +
        ['maps', 'youtube', 'search'].map(function (t) { return '<span class="p3c-tool" data-tool="' + t + '"><span class="p3c-dot"></span>' + TOOL_ICON[t] + TOOL_LABEL[t] + '</span>'; }).join('') +
      '</div>';
    root.appendChild(moat);

    var grid = document.createElement('div');
    grid.className = 'p3c-grid';
    grid.innerHTML =
      '<section class="p3c-chat" aria-label="Ask Redfin grounded chat">' +
        '<div class="p3c-ctx" role="tablist" aria-label="Property context">' +
          '<span class="p3c-ctx-label">Home</span>' +
          Object.keys(HUBS).map(function (k) {
            var h = HUBS[k];
            return '<button type="button" class="p3c-hub" role="tab" id="p3-hub-' + k + '" data-hub="' + k + '">' + I.pin +
              '<span><b>' + esc(h.short) + '</b><small>' + esc(h.area) + ' · ' + esc(h.price) + '</small></span></button>';
          }).join('') +
        '</div>' +
        '<div class="p3c-thread" id="p3c-thread" role="log" aria-live="polite"></div>' +
        '<button type="button" class="p3c-jump" id="p3c-jump">' + I.down + 'Jump to latest</button>' +
        '<div class="p3c-suggest" id="p3c-suggest">' +
          CHIPS.map(function (c) { return '<button type="button" class="p3c-chip" data-q="' + esc(c.q) + '">' + c.icon + esc(c.q) + '</button>'; }).join('') +
        '</div>' +
        '<form class="p3c-composer" id="p3c-composer" autocomplete="off">' +
          '<div class="p3c-box">' +
            '<div class="p3c-attach-row" id="p3c-attach-row" hidden>' +
              '<input type="url" id="p3-custom-yt" placeholder="Paste a YouTube link (youtube.com/watch?v=… or youtu.be/…)" />' +
              '<button type="button" id="p3c-attach-go">Use video</button>' +
            '</div>' +
            '<div class="p3c-attached" id="p3c-attached" hidden></div>' +
            '<div class="p3c-input-row">' +
              '<button type="button" class="p3c-icon-btn" id="p3c-attach-btn" title="Attach a YouTube walkthrough link" aria-label="Attach a YouTube link">' + I.link + '</button>' +
              '<textarea class="p3c-input" id="p3c-input" rows="1" placeholder="Ask about this home — nearby places, the video tour, taxes, grants…"></textarea>' +
              '<button type="submit" class="p3c-send" id="p3c-send" aria-label="Send" title="Send (Enter)" disabled>' + I.send + '</button>' +
            '</div>' +
          '</div>' +
          '<div class="p3c-hint"><span><b>Enter</b> to send · <b>Shift+Enter</b> new line</span><span id="p3c-hint-model">gemini-3.8-flash · global</span></div>' +
        '</form>' +
      '</section>' +
      '<aside class="p3c-panel" aria-label="Grounding panel">' +
        '<div class="p3c-card p3c-map-card">' +
          '<div class="p3c-card-h"><span class="p3c-card-t">' + I.map + '<span id="p3c-map-title">Grounded places</span></span>' +
            '<div class="p3c-seg" role="group" aria-label="Map layer"><button type="button" id="btn-map-road" class="is-on">Road</button><button type="button" id="btn-map-sat">Satellite</button></div>' +
          '</div>' +
          '<div class="p3c-map-slot" id="p3c-map-slot"></div>' +
          '<div class="p3c-places" id="p3c-places"></div>' +
        '</div>' +
        '<div class="p3c-card p3c-video-card" id="p3c-video-card">' +
          '<div class="p3c-card-h"><span class="p3c-card-t">' + I.yt + 'YouTube walkthrough</span><span class="p3c-vstate" id="p3c-vstate">Ready to analyze</span></div>' +
          '<div class="p3c-vrow">' +
            '<div class="p3c-video" id="p3c-video"></div>' +
            '<div class="p3c-vmeta">' +
              '<div class="p3c-vtitle" id="p3c-vtitle"></div>' +
              '<div class="p3c-vsub" id="p3c-vsub">Gemini watches the first 60 s of the tour (0.5 fps) when you ask about it.</div>' +
              '<div class="p3c-moments" id="p3c-moments"></div>' +
            '</div>' +
          '</div>' +
        '</div>' +
      '</aside>';
    root.appendChild(grid);
    root.appendChild(shim);
    pane.appendChild(root);

    $('#p3c-map-slot', root).appendChild(mapEl);
    $('#p3c-video', root).appendChild(ytEl);

    S.root = root;
    S.els = {
      thread: $('#p3c-thread', root), input: $('#p3c-input', root), send: $('#p3c-send', root), form: $('#p3c-composer', root),
      jump: $('#p3c-jump', root), attachBtn: $('#p3c-attach-btn', root), attachRow: $('#p3c-attach-row', root),
      ytInput: $('#p3-custom-yt', root), attached: $('#p3c-attached', root), places: $('#p3c-places', root),
      video: $('#p3c-video', root), vstate: $('#p3c-vstate', root), vtitle: $('#p3c-vtitle', root), moments: $('#p3c-moments', root),
      iframe: ytEl, mapEl: mapEl, suggest: $('#p3c-suggest', root)
    };
    return true;
  }

  // ---------- thread rendering ----------
  function nearBottom() { var t = S.els.thread; return !t || (t.scrollHeight - t.scrollTop - t.clientHeight) < 90; }
  function toBottom(smooth) {
    var t = S.els.thread; if (!t) return;
    if (smooth && t.scrollTo) t.scrollTo({ top: t.scrollHeight, behavior: 'smooth' }); else t.scrollTop = t.scrollHeight;
    S.els.jump.classList.remove('is-on');
  }
  function afterUpdate(stick) { if (stick) toBottom(false); else S.els.jump.classList.add('is-on'); }

  function welcome() {
    var h = HUBS[S.hub];
    var row = document.createElement('div');
    row.className = 'p3c-msg p3c-ai p3c-welcome';
    row.innerHTML =
      '<div class="p3c-avatar">' + I.spark + '</div>' +
      '<div class="p3c-ai-body"><div class="p3c-ai-card">' +
        '<div class="p3c-who">Ask Redfin <span>Gemini 3.8 Flash · grounded</span></div>' +
        '<div class="p3c-welcome-title">Ask me anything about <span class="p3c-w-addr">' + esc(h.short + ', ' + h.area) + '</span></div>' +
        '<div class="p3c-welcome-sub">Every answer is grounded live — nearby places from <b>Google Maps</b>, what the <b>YouTube walkthrough</b> actually shows, and current tax and grant facts from <b>Google Search</b> — with sources you can open.</div>' +
        '<div class="p3c-starters">' + STARTERS.map(function (s) {
          return '<button type="button" class="p3c-starter" data-q="' + esc(s.q) + '">' + s.icon + '<span>' + esc(s.q) + '<small>' + esc(s.sub) + '</small></span></button>';
        }).join('') + '</div>' +
      '</div></div>';
    S.els.thread.appendChild(row);
  }

  function addDivider(text, icon) {
    var stick = nearBottom();
    var d = document.createElement('div');
    d.className = 'p3c-divider';
    d.innerHTML = (icon || I.pin) + '<span>' + esc(text) + '</span>';
    S.els.thread.appendChild(d);
    afterUpdate(stick);
  }

  function addUser(text) {
    var h = HUBS[S.hub];
    var row = document.createElement('div');
    row.className = 'p3c-msg p3c-user';
    row.innerHTML = '<div class="p3c-user-wrap"><div class="p3c-bubble"></div><div class="p3c-meta"><span class="p3c-ctx-tag">' + esc(h.short) + '</span><span>' + esc(nowLabel()) + '</span></div></div>';
    row.querySelector('.p3c-bubble').textContent = text;
    S.els.thread.appendChild(row);
    toBottom(true);
  }

  function addAi() {
    var row = document.createElement('div');
    row.className = 'p3c-msg p3c-ai';
    row.innerHTML =
      '<div class="p3c-avatar">' + I.spark + '</div>' +
      '<div class="p3c-ai-body"><div class="p3c-ai-card">' +
        '<div class="p3c-who">Ask Redfin <span class="p3c-who-meta">grounding…</span></div>' +
        '<div class="p3c-thinking"><div class="p3c-think-row"><span class="p3c-ink"></span><span class="p3c-sweep">Reading your question…</span></div><div class="p3c-steps"></div></div>' +
        '<div class="p3c-grounded-row" hidden></div>' +
        '<div class="p3c-md"></div>' +
        '<div class="p3c-sources" hidden></div>' +
      '</div><div class="p3c-actions" hidden></div></div>';
    S.els.thread.appendChild(row);
    toBottom(true);
    return {
      row: row, text: '', tools: [], started: false, done: false, stopped: false, rafId: 0, statusQ: [], statusTimer: 0,
      think: row.querySelector('.p3c-thinking'), sweep: row.querySelector('.p3c-sweep'), steps: row.querySelector('.p3c-steps'),
      grounded: row.querySelector('.p3c-grounded-row'), md: row.querySelector('.p3c-md'), sources: row.querySelector('.p3c-sources'),
      actions: row.querySelector('.p3c-actions'), who: row.querySelector('.p3c-who-meta'), sourcesData: null, doneData: null, t0: performance.now()
    };
  }

  function renderAi(ai) {
    ai.rafId = 0;
    var stick = nearBottom();
    var txt = ai.text;
    if (!ai.done && ((txt.match(/\*\*/g) || []).length % 2 === 1)) txt += '**';
    ai.md.innerHTML = md(txt);
    if (!ai.done) {
      var target = ai.md.lastElementChild;
      if (target && (target.tagName === 'UL' || target.tagName === 'OL')) target = target.lastElementChild || target;
      var caret = document.createElement('span'); caret.className = 'p3c-caret';
      (target || ai.md).appendChild(caret);
    }
    afterUpdate(stick);
  }
  function schedule(ai) { if (!ai.rafId) ai.rafId = requestAnimationFrame(function () { safe(renderAi)(ai); }); }

  function setToolState(tools, state) {
    if (!S.root) return;
    S.root.querySelectorAll('.p3c-tool').forEach(function (el) {
      var t = el.getAttribute('data-tool');
      el.classList.remove('is-active');
      if (state === 'active' && tools.indexOf(t) >= 0) { el.classList.add('is-active'); el.classList.remove('is-used'); }
      if (state === 'used') el.classList.toggle('is-used', tools.indexOf(t) >= 0);
    });
  }

  function onStatus(ai, evt) {
    if (ai.started) { if (ai.who) ai.who.textContent = evt.text || ''; return; }
    var tool = evt.tool || '';
    ai.statusQ.push(evt);
    if (ai.statusTimer) return;
    (function pump() {
      var e = ai.statusQ.shift();
      if (!e || ai.started) { ai.statusTimer = 0; return; }
      var existing = null;
      ai.steps.querySelectorAll('.p3c-step').forEach(function (el) { if (el.getAttribute('data-tool') === (e.tool || '')) existing = el; });
      if (existing) {
        // Heartbeat from the backend watchdog: refresh the step in place and surface it in the shimmer headline.
        existing.querySelector('span').textContent = e.text || '';
        ai.sweep.textContent = e.text || ai.sweep.textContent;
        ai.statusTimer = setTimeout(pump, 120);
        return;
      }
      var step = document.createElement('div');
      step.className = 'p3c-step is-live';
      step.setAttribute('data-tool', e.tool || '');
      step.innerHTML = (TOOL_ICON[e.tool] || I.spark) + '<span>' + esc(e.text || '') + '</span>';
      ai.steps.appendChild(step);
      var stick = nearBottom(); afterUpdate(stick);
      ai.statusTimer = setTimeout(pump, 420);
    })();
    if (tool && ai.tools.indexOf(tool) < 0) ai.tools.push(tool);
  }

  function onFirstDelta(ai) {
    ai.started = true;
    if (ai.statusTimer) { clearTimeout(ai.statusTimer); ai.statusTimer = 0; }
    ai.think.hidden = true; ai.think.style.display = 'none';
    var tools = ai.tools.length ? ai.tools : [];
    if (tools.length) {
      ai.grounded.innerHTML = tools.map(function (t) { return '<span class="p3c-gchip">' + I.check + 'Grounded · ' + esc(TOOL_LABEL[t] || t) + '</span>'; }).join('');
      ai.grounded.hidden = false;
    }
    if (ai.who) ai.who.textContent = 'streaming · gemini-3.8-flash';
  }

  function renderSources(ai, src) {
    ai.sourcesData = src;
    var html = '', n = 0;
    (src.maps || []).forEach(function (p, i) {
      n++;
      var meta = p.rating ? ('<small>' + Number(p.rating).toFixed(1) + '★</small>') : '';
      html += '<a class="p3c-src p3c-src-maps" data-place="' + i + '" href="' + esc(p.uri || ('https://www.google.com/maps/search/?api=1&query=' + encodeURIComponent(p.title))) + '" target="_blank" rel="noopener noreferrer" title="Open in Google Maps' + (p.address ? ' · ' + esc(p.address) : '') + '" style="animation-delay:' + (n * 0.05) + 's">' +
        '<span class="p3c-src-n">' + (i + 1) + '</span>' + I.pin + '<span>' + esc(p.title) + '</span>' + meta + '</a>';
    });
    (src.web || []).forEach(function (w) {
      n++;
      html += '<a class="p3c-src p3c-src-web" href="' + esc(w.uri) + '" target="_blank" rel="noopener noreferrer" title="' + esc(w.title || w.domain) + '" style="animation-delay:' + (n * 0.05) + 's">' +
        '<span class="p3c-src-n">' + n + '</span>' + I.globe + '<span>' + esc(w.domain || w.title) + '</span></a>';
    });
    if (src.youtube && src.youtube.id) {
      n++;
      html += '<button type="button" class="p3c-src p3c-src-yt" data-yt="' + esc(src.youtube.id) + '" title="Show the analyzed walkthrough" style="animation-delay:' + (n * 0.05) + 's">' + I.yt + '<span>YouTube walkthrough · ' + esc(src.youtube.id) + '</span></button>';
    }
    if (!html) return;
    ai.sources.innerHTML = '<div class="p3c-sources-label">Sources · ' + n + '</div>' + html;
    ai.sources.hidden = false;
    var stick = nearBottom(); afterUpdate(stick);
  }

  function renderActions(ai) {
    var d = ai.doneData || {};
    var lat = '';
    if (d.latency_ms) lat = (d.latency_ms / 1000).toFixed(1) + ' s' + (d.ttft_ms ? ' · first token ' + (d.ttft_ms / 1000).toFixed(1) + ' s' : '') + ' · ' + esc(d.model || 'gemini-3.8-flash');
    ai.actions.innerHTML =
      '<span class="p3c-lat">' + esc(nowLabel()) + '</span>' +
      '<button type="button" class="p3c-act" data-act="copy" title="Copy answer">' + I.copy + '<span>Copy</span></button>' +
      '<button type="button" class="p3c-act" data-act="listen" title="Listen (24 kHz voice)">' + I.vol + '<span>Listen</span></button>' +
      (ai.stopped ? '<span class="p3c-lat">stopped</span>' : '') +
      (lat ? '<span class="p3c-lat">' + lat + '</span>' : '');
    ai.actions.hidden = false;
    ai.actions.__ai = ai;
  }

  // ---------- map + video panel ----------
  function ensureMap() {
    if (typeof L === 'undefined') {
      var slot = $('#p3c-map-slot', S.root);
      if (slot && !slot.querySelector('.p3c-map-empty')) { var e = document.createElement('div'); e.className = 'p3c-map-empty'; e.textContent = 'Map unavailable offline'; slot.appendChild(e); }
      return null;
    }
    var m = getMap();
    if (!m) {
      try { if (typeof initPillar3Map === 'function') initPillar3Map(); } catch (e) {}
      m = getMap();
    }
    if (!m) {
      try {
        m = L.map(S.els.mapEl, { zoomControl: true }).setView([HUBS[S.hub].lat, HUBS[S.hub].lng], 14);
        S.ownTile = L.tileLayer('https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}', { maxZoom: 20, attribution: '&copy; Google Maps' }).addTo(m);
        S.ownMap = m;
      } catch (e) { return null; }
    }
    setMapInitialized();
    if (!S.layer) { try { S.layer = L.layerGroup().addTo(m); } catch (e) {} }
    return m;
  }

  function drawHome() {
    var m = ensureMap(); if (!m || !S.layer) return;
    var h = HUBS[S.hub];
    try { if (typeof p3MarkerGroup !== 'undefined' && p3MarkerGroup) p3MarkerGroup.clearLayers(); } catch (e) {}
    if (S.homeMarker) { try { S.layer.removeLayer(S.homeMarker); } catch (e) {} }
    S.homeMarker = L.marker([h.lat, h.lng], {
      icon: L.divIcon({ className: 'p3c-home', html: '<span>' + I.home + '</span>', iconSize: [30, 30], iconAnchor: [15, 15] }),
      zIndexOffset: 1000, keyboard: false
    }).bindPopup('<div class="p3c-popup"><b>' + esc(h.address) + '</b><small>Redfin listing · ' + esc(h.priceFull) + '</small></div>').addTo(S.layer);
  }

  function clearPlaces() {
    S.placeMarkers.forEach(function (mk) { try { S.layer.removeLayer(mk); } catch (e) {} });
    S.placeMarkers = [];
    if (S.els.places) S.els.places.innerHTML = '';
    var t = $('#p3c-map-title', S.root); if (t) t.textContent = 'Grounded places';
  }

  function showPlaces(places) {
    var m = ensureMap();
    clearPlaces();
    var h = HUBS[S.hub];
    var pts = [[h.lat, h.lng]];
    var listHtml = '';
    (places || []).forEach(function (p, i) {
      var sub = [p.rating ? Number(p.rating).toFixed(1) + '★' : '', p.type || '', p.address ? String(p.address).split(',')[0] : ''].filter(Boolean).join(' · ');
      listHtml += '<button type="button" class="p3c-place" data-place="' + i + '" style="animation-delay:' + (i * 0.06) + 's"><span class="p3c-src-n">' + (i + 1) + '</span><span>' + esc(p.title) + (sub ? '<small>' + esc(sub) + '</small>' : '') + '</span></button>';
      if (m && S.layer && typeof p.lat === 'number' && typeof p.lng === 'number') {
        var mk = L.marker([p.lat, p.lng], {
          icon: L.divIcon({ className: 'p3c-pin', html: '<span style="--d:' + (i * 0.08).toFixed(2) + 's"><i>' + (i + 1) + '</i></span>', iconSize: [24, 24], iconAnchor: [12, 26], popupAnchor: [0, -24] }),
          riseOnHover: true
        }).bindPopup('<div class="p3c-popup"><b>' + esc(p.title) + '</b>' +
          (p.rating ? '<small>' + Number(p.rating).toFixed(1) + '★' + (p.reviews ? ' · ' + Number(p.reviews).toLocaleString() + ' reviews' : '') + '</small>' : '') +
          (p.address ? '<small>' + esc(p.address) + '</small>' : '') +
          '<a href="' + esc(p.uri) + '" target="_blank" rel="noopener noreferrer">Open in Google Maps</a></div>').addTo(S.layer);
        mk.__idx = i;
        S.placeMarkers[i] = mk;
        pts.push([p.lat, p.lng]);
      }
    });
    S.els.places.innerHTML = listHtml;
    var t = $('#p3c-map-title', S.root); if (t && places && places.length) t.textContent = places.length + ' grounded places';
    S.bounds = pts.length > 1 ? pts : null;
    S.needsFit = true;
    refreshMap();
  }

  function refreshMap() {
    var m = getMap(); if (!m) return;
    try {
      m.invalidateSize(false);
      var size = m.getSize();
      if (!size || size.x < 20 || size.y < 20) return;
      if (S.needsFit) {
        if (S.bounds) m.fitBounds(S.bounds, { padding: [30, 30], maxZoom: 16 });
        else m.setView([HUBS[S.hub].lat, HUBS[S.hub].lng], 14);
        S.needsFit = false;
      }
    } catch (e) {}
  }

  function focusPlace(i, open) {
    var mk = S.placeMarkers[i];
    var m = getMap();
    S.root.querySelectorAll('.p3c-place').forEach(function (el) { el.classList.toggle('is-hot', +el.getAttribute('data-place') === i); });
    if (mk && m) {
      try { m.flyTo(mk.getLatLng(), Math.max(m.getZoom(), 15), { duration: 0.6 }); if (open) setTimeout(function () { try { mk.openPopup(); } catch (e) {} }, 380); } catch (e) {}
      return true;
    }
    return false;
  }
  function hotMarker(i, on) {
    var mk = S.placeMarkers[i];
    if (mk && mk._icon) mk._icon.classList.toggle('is-hot', !!on);
  }

  function currentVideoId() { return S.customYt ? S.customYt.id : HUBS[S.hub].yt; }
  function setVideo(id, opts) {
    opts = opts || {};
    var ifr = S.els.iframe; if (!ifr || !id) return;
    var want = 'https://www.youtube.com/embed/' + id + '?enablejsapi=1&rel=0' + (opts.start != null ? '&start=' + opts.start + '&autoplay=1' : '');
    var cur = ifr.getAttribute('src') || '';
    if (opts.start != null || cur.indexOf('/embed/' + id) < 0) ifr.setAttribute('src', want);
    var title = S.customYt && S.customYt.id === id ? 'Attached YouTube video · ' + id : 'Architectural Digest · ' + HUBS[S.hub].ytTitle;
    S.els.vtitle.textContent = title;
  }
  function markVideoReferenced(on) {
    S.els.video.classList.toggle('is-ref', !!on);
    S.els.vstate.classList.toggle('is-ref', !!on);
    S.els.vstate.textContent = on ? 'Analyzed in this answer' : 'Ready to analyze';
  }
  function addMoments(text) {
    var found = [];
    String(text || '').replace(/\[((?:\d{1,2}:)?\d{1,2}:\d{2}(?:\s*(?:,|–|-|to)\s*(?:\d{1,2}:)?\d{1,2}:\d{2})*)\]/g, function (m, grp) {
      grp.split(/\s*(?:,|–|-|to)\s*/).forEach(function (ts) { if (found.indexOf(ts) < 0) found.push(ts); });
      return m;
    });
    if (!found.length) return;
    S.moments = found.sort(function (a, b) { return tsToSec(a) - tsToSec(b); }).slice(0, 8);
    S.els.moments.innerHTML = S.moments.map(function (ts) { return '<button type="button" class="p3c-ts" data-ts="' + ts + '">' + ts + '</button>'; }).join('');
  }
  function seek(ts) {
    var sec = tsToSec(ts);
    setVideo(currentVideoId(), { start: sec });
    S.els.video.classList.add('is-ref');
    try { S.els.video.scrollIntoView({ block: 'nearest', behavior: 'smooth' }); } catch (e) {}
  }

  // ---------- hub + attachments ----------
  function setHub(id, opts) {
    opts = opts || {};
    if (!HUBS[id]) return;
    var changed = id !== S.hub;
    S.hub = id;
    setLegacyHub(id);
    S.root.querySelectorAll('.p3c-hub').forEach(function (b) {
      var on = b.getAttribute('data-hub') === id;
      b.classList.toggle('is-active', on); b.setAttribute('aria-selected', on ? 'true' : 'false');
      b.style.borderColor = '';
    });
    var h = HUBS[id];
    S.root.querySelectorAll('.p3c-w-addr').forEach(function (el) { el.textContent = h.short + ', ' + h.area; });
    if (!S.customYt) { setVideo(h.yt); markVideoReferenced(false); S.moments = []; S.els.moments.innerHTML = ''; }
    if (changed) { clearPlaces(); S.bounds = null; S.needsFit = true; }
    drawHome(); refreshMap();
    if (changed && opts.announce !== false && S.els.thread.querySelector('.p3c-user')) addDivider('Now discussing ' + h.short + ', ' + h.area + ' · ' + h.price);
  }

  function attachYt(v, opts) {
    opts = opts || {};
    if (!v) return false;
    S.customYt = v;
    S.els.attached.innerHTML = '<span class="p3c-attached-chip">' + I.yt + '<span>YouTube · ' + esc(v.id) + '</span><button type="button" id="p3c-detach" aria-label="Remove video">' + I.x + '</button></span>';
    S.els.attached.hidden = false;
    S.els.attachRow.hidden = true;
    S.els.attachBtn.classList.add('is-on');
    S.els.input.placeholder = 'Ask about the attached video — or anything about this home…';
    setVideo(v.id); markVideoReferenced(false); S.moments = []; S.els.moments.innerHTML = '';
    if (!opts.silent) addDivider('Attached YouTube video ' + v.id + ' — ask me about it', I.yt);
    return true;
  }
  function detachYt() {
    S.customYt = null;
    S.els.attached.hidden = true; S.els.attached.innerHTML = '';
    S.els.attachBtn.classList.remove('is-on');
    if (S.els.ytInput) S.els.ytInput.value = '';
    S.els.input.placeholder = 'Ask about this home — nearby places, the video tour, taxes, grants…';
    setVideo(HUBS[S.hub].yt); markVideoReferenced(false);
  }

  // ---------- streaming ----------
  function setStreaming(on) {
    S.streaming = on;
    var b = S.els.send;
    b.classList.toggle('is-stop', on);
    b.innerHTML = on ? I.stop : I.send;
    b.setAttribute('aria-label', on ? 'Stop' : 'Send');
    b.title = on ? 'Stop generating' : 'Send (Enter)';
    syncSend();
  }
  function syncSend() { S.els.send.disabled = !S.streaming && !S.els.input.value.trim(); }

  function stop() { if (S.ctrl) { try { S.ctrl.abort(); } catch (e) {} } }

  function send(text, opts) {
    opts = opts || {};
    text = String(text || '').trim();
    if (!text) return Promise.resolve(null);
    if (S.streaming) stop();
    var yt = parseYt(text);
    if (yt && (!S.customYt || S.customYt.id !== yt.id)) attachYt(yt, { silent: true });

    addUser(text);
    S.messages.push({ role: 'user', text: text });
    var ai = addAi();
    var mySeq = ++S.seq;
    var ctrl = new AbortController();
    S.ctrl = ctrl;
    setStreaming(true);

    var hubAtSend = S.hub;
    var payload = { messages: S.messages.slice(-14), hub_id: hubAtSend, youtube_url: S.customYt ? S.customYt.url : '' };

    function handle(evt) {
      if (!evt || typeof evt !== 'object') return;
      if (evt.type === 'route') {
        ai.tools = (evt.tools || []).slice();
        setToolState(ai.tools, 'active');
        if (!ai.started && ai.tools.length) {
          ai.sweep.textContent = ai.tools.length === 1 ? ('Grounding with ' + TOOL_LABEL[ai.tools[0]] + '…') : ('Grounding across ' + ai.tools.map(function (t) { return TOOL_LABEL[t]; }).join(', ') + '…');
        }
      } else if (evt.type === 'status') {
        onStatus(ai, evt);
      } else if (evt.type === 'delta') {
        if (!ai.started) onFirstDelta(ai);
        ai.text += evt.text || '';
        schedule(ai);
      } else if (evt.type === 'sources') {
        renderSources(ai, evt);
        if (S.hub === hubAtSend) {
          if (evt.maps && evt.maps.length) showPlaces(evt.maps);
          if (evt.youtube && evt.youtube.id) { setVideo(evt.youtube.id); markVideoReferenced(true); }
        }
      } else if (evt.type === 'done') {
        ai.doneData = evt;
      }
    }

    var p = fetch(API + authSuffix(), {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, credentials: 'same-origin',
      body: JSON.stringify(payload), signal: ctrl.signal
    }).then(function (res) {
      if (!res.ok || !res.body) throw new Error(res.status === 401 ? 'Session expired — reload the studio to sign in again.' : ('HTTP ' + res.status));
      var reader = res.body.getReader();
      var dec = new TextDecoder();
      var buf = '';
      function pump() {
        return reader.read().then(function (r) {
          if (r.done) {
            if (buf.trim()) { try { handle(JSON.parse(buf)); } catch (e) {} }
            return;
          }
          buf += dec.decode(r.value, { stream: true });
          var nl;
          while ((nl = buf.indexOf('\n')) >= 0) {
            var line = buf.slice(0, nl).trim(); buf = buf.slice(nl + 1);
            if (!line) continue;
            var evt = null; try { evt = JSON.parse(line); } catch (e) { evt = null; }
            if (evt) safe(handle)(evt);
          }
          return pump();
        });
      }
      return pump();
    }).catch(function (err) {
      if (ctrl.signal.aborted) { ai.stopped = true; return; }
      if (!ai.started) onFirstDelta(ai);
      ai.text += (ai.text ? '\n\n' : '') + '_Grounding hit a snag (' + (err && err.message ? err.message : 'network') + '). Please try again._';
      ai.failed = true;
    }).then(function () {
      if (!ai.started) onFirstDelta(ai);
      if (ai.stopped && !ai.text) ai.text = '_Stopped._';
      ai.done = true;
      if (ai.rafId) { cancelAnimationFrame(ai.rafId); ai.rafId = 0; }
      safe(renderAi)(ai);
      if (ai.who) ai.who.textContent = ai.stopped ? 'stopped' : ('grounded · ' + (ai.tools.map(function (t) { return TOOL_LABEL[t]; }).join(' + ') || 'gemini-3.8-flash'));
      safe(renderActions)(ai);
      if (ai.text && !ai.failed && ai.text !== '_Stopped._') {
        S.messages.push({ role: 'model', text: ai.text });
        S.lastAnswer = ai.text;
        if (ai.sourcesData && ai.sourcesData.youtube) addMoments(ai.text);
      }
      setToolState((ai.doneData && ai.doneData.tools) || ai.tools, 'used');
      if (mySeq === S.seq) { S.ctrl = null; setStreaming(false); }
      var result = { text: ai.text, sources: ai.sourcesData || { maps: [], web: [] }, done: ai.doneData || {}, hub: HUBS[hubAtSend], stopped: ai.stopped };
      S.lastResult = result;
      safe(updateLegacyShim)(result);
      var stick = nearBottom(); afterUpdate(stick);
      return result;
    });
    return p;
  }

  function updateLegacyShim(r) {
    var txt = plain(r.text || '');
    ['p3-maps-summary', 'p3-yt-summary', 'p3-search-summary'].forEach(function (id) { var el = document.getElementById(id); if (el) el.textContent = txt; });
    var badge = document.getElementById('p3-lat-badge');
    if (badge && r.done && r.done.latency_ms) badge.textContent = 'Grounded in ' + r.done.latency_ms + 'ms';
  }

  function toLegacy(r) {
    var h = HUBS[(r && r.hub && r.hub.id) || S.hub];
    var src = (r && r.sources) || { maps: [], web: [] };
    var txt = (r && r.text) || '';
    return {
      ok: !!(r && txt), pillar: 'Pillar 3 · Ask Redfin 2.0 grounded chat',
      latency_ms: (r && r.done && r.done.latency_ms) || 0,
      hub: { id: h.id, address: h.address, price: h.priceFull, lat: h.lat, lng: h.lng, youtube_id: h.yt, youtube_url: 'https://www.youtube.com/watch?v=' + h.yt },
      maps: { model: 'gemini-3.8-flash', summary: txt, places: src.maps || [] },
      search: { model: 'gemini-3.8-flash', summary: txt, sources: src.web || [] },
      youtube: { model: 'gemini-3.8-flash', youtube_url: src.youtube ? src.youtube.url : ('https://www.youtube.com/watch?v=' + h.yt), summary: txt },
      answer: txt
    };
  }

  // ---------- events ----------
  function wire() {
    var E = S.els;
    E.form.addEventListener('submit', safe(function (e) {
      e.preventDefault();
      if (S.streaming) { stop(); return; }
      var v = E.input.value;
      if (!v.trim()) return;
      E.input.value = ''; autosize(); syncSend();
      send(v);
    }));
    E.input.addEventListener('keydown', safe(function (e) {
      if (e.key === 'Enter' && !e.shiftKey && !e.isComposing && e.keyCode !== 229) {
        e.preventDefault();
        if (S.streaming && !E.input.value.trim()) return;
        if (E.input.value.trim()) { var v = E.input.value; E.input.value = ''; autosize(); syncSend(); send(v); }
      }
    }));
    E.input.addEventListener('input', safe(function () { autosize(); syncSend(); }));
    E.thread.addEventListener('scroll', function () { if (nearBottom()) E.jump.classList.remove('is-on'); }, { passive: true });
    E.jump.addEventListener('click', function () { toBottom(true); });

    S.root.addEventListener('click', safe(function (e) {
      var t = e.target.closest ? e.target.closest('button, a') : null;
      if (!t || !S.root.contains(t)) return;
      if (t.classList.contains('p3c-starter') || t.classList.contains('p3c-chip')) { send(t.getAttribute('data-q')); return; }
      if (t.classList.contains('p3c-hub')) { setHub(t.getAttribute('data-hub'), { announce: true }); return; }
      if (t.classList.contains('p3c-ts')) { seek(t.getAttribute('data-ts')); return; }
      if (t.classList.contains('p3c-place')) { var i = +t.getAttribute('data-place'); if (!focusPlace(i, true)) { var src = S.lastResult && S.lastResult.sources && S.lastResult.sources.maps && S.lastResult.sources.maps[i]; if (src && src.uri) window.open(src.uri, '_blank', 'noopener'); } return; }
      if (t.classList.contains('p3c-src-yt')) { var vid = t.getAttribute('data-yt'); setVideo(vid); markVideoReferenced(true); try { S.els.video.scrollIntoView({ block: 'nearest', behavior: 'smooth' }); } catch (_) {} return; }
      if (t.id === 'btn-map-road') { window.setGoogleMapLayer('roadmap'); return; }
      if (t.id === 'btn-map-sat') { window.setGoogleMapLayer('satellite'); return; }
      if (t.id === 'p3c-attach-btn') {
        if (S.customYt) { detachYt(); return; }
        E.attachRow.hidden = !E.attachRow.hidden;
        if (!E.attachRow.hidden) setTimeout(function () { try { E.ytInput.focus(); } catch (_) {} }, 30);
        return;
      }
      if (t.id === 'p3c-attach-go') { var v = parseYt(E.ytInput.value); if (v) attachYt(v); else { E.ytInput.style.borderColor = 'var(--p3c-red)'; setTimeout(function () { E.ytInput.style.borderColor = ''; }, 1200); } return; }
      if (t.id === 'p3c-detach') { detachYt(); return; }
      var act = t.getAttribute('data-act');
      if (act) {
        var actions = t.closest('.p3c-actions'); var ai = actions && actions.__ai; if (!ai) return;
        if (act === 'copy') copyText(plain(ai.text), t);
        if (act === 'listen') speak(speakable(ai.text), t);
      }
    }));
    S.root.addEventListener('mouseover', function (e) {
      var t = e.target.closest ? e.target.closest('[data-place]') : null;
      if (t && S.root.contains(t)) hotMarker(+t.getAttribute('data-place'), true);
    });
    S.root.addEventListener('mouseout', function (e) {
      var t = e.target.closest ? e.target.closest('[data-place]') : null;
      if (t && S.root.contains(t)) hotMarker(+t.getAttribute('data-place'), false);
    });
    E.ytInput.addEventListener('keydown', function (e) {
      if (e.key === 'Enter') { e.preventDefault(); var v = parseYt(E.ytInput.value); if (v) attachYt(v); }
      if (e.key === 'Escape') { E.attachRow.hidden = true; }
    });
    window.addEventListener('resize', debounce(function () { fitHeight(); refreshMap(); }, 120));
    var pane = document.getElementById('pillar-3');
    if (pane && window.MutationObserver) {
      new MutationObserver(function () {
        if (pane.classList.contains('active')) { fitHeight(); setTimeout(refreshMap, 60); setTimeout(refreshMap, 260); }
      }).observe(pane, { attributes: true, attributeFilter: ['class'] });
    }
    // Content above P3 (e.g. the live "Built on Google Cloud" strip) can grow/shrink at runtime -> keep the chat
    // pinned above the floating co-pilot bar with zero overlap.
    var refit = debounce(fitHeight, 60);
    if (window.ResizeObserver) { try { new ResizeObserver(function () { refit(); }).observe(document.body); } catch (e) {} }
    setInterval(function () { if (pane && pane.classList.contains('active')) safe(fitHeight)(); }, 1500);
  }

  function autosize() { var ta = S.els.input; ta.style.height = 'auto'; ta.style.height = Math.min(ta.scrollHeight, 132) + 'px'; }
  function debounce(fn, ms) { var t = 0; return function () { clearTimeout(t); t = setTimeout(function () { safe(fn)(); }, ms); }; }

  function fitHeight() {
    var pane = document.getElementById('pillar-3');
    if (!S.root || !pane || !pane.classList.contains('active')) return;
    var grid = S.root.querySelector('.p3c-grid'); if (!grid) return;
    var top = grid.getBoundingClientRect().top + (window.scrollY || 0);
    var reserve = 18;
    var bar = document.querySelector('.omni-copilot-bar');
    if (bar) {
      var cs = getComputedStyle(bar);
      if (cs.position === 'fixed' && cs.display !== 'none' && cs.visibility !== 'hidden') {
        var r = bar.getBoundingClientRect();
        if (r.top > window.innerHeight * 0.5) reserve = Math.max(reserve, window.innerHeight - r.top + 14);
      }
    }
    var h = Math.round(window.innerHeight - top - reserve);
    h = Math.max(420, Math.min(h, 900));
    if (S.root.style.getPropertyValue('--p3c-h') !== h + 'px') {
      S.root.style.setProperty('--p3c-h', h + 'px');
      setTimeout(function () { safe(refreshMap)(); }, 40);
    }
    S.root.classList.toggle('is-compact', h < 520);
  }

  function copyText(text, btn) {
    var ok = function () {
      var old = btn.innerHTML; btn.classList.add('is-ok'); btn.innerHTML = I.check + '<span>Copied</span>';
      setTimeout(function () { btn.classList.remove('is-ok'); btn.innerHTML = old; }, 1400);
    };
    try {
      if (navigator.clipboard && navigator.clipboard.writeText) { navigator.clipboard.writeText(text).then(ok, function () { fallbackCopy(text); ok(); }); return; }
    } catch (e) {}
    fallbackCopy(text); ok();
  }
  function fallbackCopy(text) {
    try { var ta = document.createElement('textarea'); ta.value = text; ta.style.position = 'fixed'; ta.style.opacity = '0'; document.body.appendChild(ta); ta.select(); document.execCommand('copy'); document.body.removeChild(ta); } catch (e) {}
  }
  function speak(text, btn) {
    try {
      var voice = 'Aoede';
      try { if (typeof currentActiveVoice !== 'undefined' && currentActiveVoice) voice = currentActiveVoice; } catch (e) {}
      if (typeof LiveAudioEngine !== 'undefined' && LiveAudioEngine && typeof LiveAudioEngine.speakClip === 'function') { LiveAudioEngine.speakClip(text, voice, btn); return; }
    } catch (e) {}
    try { if (window.speechSynthesis) { window.speechSynthesis.cancel(); window.speechSynthesis.speak(new SpeechSynthesisUtterance(text)); } } catch (e) {}
  }

  // ---------- legacy compatibility ----------
  function installOverrides() {
    window.runPillar3Grounding = function (hubId, opts) {
      try {
        var id = HUBS[hubId] ? hubId : S.hub;
        if (id !== S.hub) setHub(id, { announce: true });
        var h = HUBS[id];
        var q = (opts && typeof opts === 'object' && opts.question) ||
          ('Give me the full grounded brief for ' + h.short + ', ' + h.area + ": what's walkable nearby, what the YouTube walkthrough shows, and 2026 property taxes and down-payment grants.");
        return send(q, { via: 'copilot' }).then(toLegacy, function () { return toLegacy(null); });
      } catch (e) { return Promise.resolve(toLegacy(null)); }
    };
    window.askPillar3 = function (question, hubId) { if (hubId && HUBS[hubId]) setHub(hubId, { announce: true }); return send(question); };
    window.speakPillar3GroundedBrief = function (btnEl) {
      var h = HUBS[S.hub];
      var t = S.lastAnswer ? speakable(S.lastAnswer) : ('Ask Redfin is ready for ' + h.short + ' in ' + h.area + '. Ask about nearby places, the video walkthrough, or 2026 taxes and grants.');
      speak(t, btnEl || null);
    };
    var origLayer = (typeof window.setGoogleMapLayer === 'function') ? window.setGoogleMapLayer : null;
    window.setGoogleMapLayer = function (mode) {
      var r;
      try {
        if (S.ownMap) {
          if (S.ownTile) S.ownMap.removeLayer(S.ownTile);
          S.ownTile = L.tileLayer('https://mt1.google.com/vt/lyrs=' + (mode === 'satellite' ? 'y' : 'm') + '&x={x}&y={y}&z={z}', { maxZoom: 20, attribution: '&copy; Google Maps' }).addTo(S.ownMap);
        } else if (origLayer) { r = origLayer(mode); }
      } catch (e) {}
      try {
        var road = document.getElementById('btn-map-road'), sat = document.getElementById('btn-map-sat');
        if (road) road.classList.toggle('is-on', mode !== 'satellite');
        if (sat) sat.classList.toggle('is-on', mode === 'satellite');
      } catch (e) {}
      return r;
    };
  }

  // ---------- boot ----------
  function boot() {
    if (!build()) return;
    installOverrides();
    wire();
    welcome();
    setHub(S.hub, { announce: false });
    setVideo(HUBS[S.hub].yt);
    ensureMap();
    drawHome();
    fitHeight();
    refreshMap();
    autosize();
    syncSend();
    window.__p3Chat = { send: send, setHub: setHub, stop: stop, state: S, version: '2026-10-16.1' };
  }
  try {
    boot();
  } catch (e) {
    try { console.warn('[p3_chat] boot failed', e); } catch (_) {}
  }
})();
