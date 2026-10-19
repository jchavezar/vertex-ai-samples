/* ==========================================================================
   Pillar 4 · Live Avatar conversation stage
   --------------------------------------------------------------------------
   Rebuilds #pillar-4 at runtime into a clean, cinematic conversation stage:
     · large 4:5 portrait stage (idle poster w/ breathing motion, live 24 fps
       engine video with crossfade + last-frame hold so turns never flash
       black, state glow ring, live audio-level visualizer)
     · avatar picker (Kira, Sam, Ben, Vera, Leo official 3.8 video avatars +
       Jesus 2D portrait in audio mode via the legacy #kira-stage-canvas)
     · chat-style live transcript with streaming captions + smart auto-scroll
     · one primary Start/End button, an Interrupt button and a hint line.
   Engine: window.RocketLive (static/live_session.js). Missing engine shows a
   graceful "engine loading" state instead of throwing.
   Legacy shim: every legacy #pillar-4 node is kept alive inside a hidden
   container so the legacy inline script never dereferences null.
   The module is an idempotent, defensive IIFE: it never throws at load.
   ========================================================================== */
(function () {
  'use strict';

  var VERSION = 10;

  try {
    if (window.__P4S && window.__P4S.version >= VERSION) return;
    if (window.__P4S && typeof window.__P4S.destroy === 'function') {
      try { window.__P4S.destroy(); } catch (e) { /* ignore */ }
    }
  } catch (e) { /* ignore */ }

  // ------------------------------------------------------------------------
  // Avatar catalog (legacy keys kept for selectAvatarProfile + backend map)
  // ------------------------------------------------------------------------
  var AVATARS = [
    { id: 'kira', key: 'Kira', name: 'Kira', voice: 'Aoede', video: true,
      thumb: '/static/official_kira_38.jpg', full: '/static/official_kira_38_full.jpg' },
    { id: 'sam', key: 'Sam', name: 'Sam', voice: 'Puck', video: true,
      thumb: '/static/official_sam_38.jpg', full: '/static/official_sam_38_full.jpg' },
    { id: 'ben', key: 'Marcus', name: 'Ben', voice: 'Fenrir', video: true,
      thumb: '/static/official_ben_38.jpg', full: '/static/official_ben_38_full.jpg' },
    { id: 'vera', key: 'Elena', name: 'Vera', voice: 'Kore', video: true,
      thumb: '/static/official_vera_38.jpg', full: '/static/official_vera_38_full.jpg' },
    { id: 'leo', key: 'Devon', name: 'Leo', voice: 'Charon', video: true,
      thumb: '/static/official_leo_38.jpg', full: '/static/official_leo_38_full.jpg' },
    { id: 'jesus', key: 'Jesus', name: 'Jesus', voice: 'Puck', video: false,
      thumb: '/static/jesus_idle_closed.jpg', full: null }
  ];
  var LEGACY_TO_ID = { Kira: 'kira', Sam: 'sam', Marcus: 'ben', Ben: 'ben', Elena: 'vera', Vera: 'vera',
    Devon: 'leo', Leo: 'leo', Jesus: 'jesus' };

  // Legacy IDs the inline script dereferences without null checks. They are
  // all kept alive (moved into the hidden shim) and recreated if missing.
  var LEGACY_IDS = [
    'p4-live-transcript', 'p4-avatar-name', 'p4-conn-badge', 'p4-active-voice-badge',
    'kira-portrait-ring', 'kira-stage-canvas', 'kira-stage-mse-video', 'avatar-ring-canvas',
    'btn-p4-start', 'lbl-p4-start', 'btn-p4-stop', 'lbl-p4-stop', 'btn-p4-test-speech',
    'p4-avatar-selector-row', 'chk-official-video-avatar', 'custom-avatar-upload',
    'p4-val-subs', 'p4-sub-subs', 'p4-val-piti', 'p4-val-refi', 'p4-years-saved',
    'p4-card-rm', 'p4-card-rf', 'p4-card-mc', 'agent-action-log'
  ];
  var LEGACY_TAGS = { 'kira-stage-canvas': 'canvas', 'avatar-ring-canvas': 'canvas',
    'kira-stage-mse-video': 'video', 'btn-p4-start': 'button', 'btn-p4-stop': 'button',
    'btn-p4-test-speech': 'button', 'chk-official-video-avatar': 'input', 'custom-avatar-upload': 'input' };

  var STATE_LABEL = {
    off: 'Engine loading…', idle: 'Ready', connecting: 'Connecting…', listening: 'Listening…',
    user_speaking: 'Listening…', thinking: 'Thinking…', speaking: 'Speaking'
  };
  var STATE_GROUP = {
    off: 'idle', idle: 'idle', connecting: 'thinking', listening: 'listening',
    user_speaking: 'listening', thinking: 'thinking', speaking: 'speaking'
  };

  var ICONS = {
    mic: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3a3 3 0 0 0-3 3v6a3 3 0 0 0 6 0V6a3 3 0 0 0-3-3z"/><path d="M19 11a7 7 0 0 1-14 0"/><line x1="12" y1="18" x2="12" y2="21"/></svg>',
    stop: '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="7" y="7" width="10" height="10" rx="2"/></svg>',
    hand: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 13V5.5a1.5 1.5 0 0 1 3 0V12"/><path d="M11 11.5V4a1.5 1.5 0 0 1 3 0v7.5"/><path d="M14 11.5V5.5a1.5 1.5 0 0 1 3 0v8"/><path d="M17 9.5a1.5 1.5 0 0 1 3 0V15a7 7 0 0 1-7 7h-1a7 7 0 0 1-5.6-2.8L3.6 15.5a1.6 1.6 0 0 1 2.5-2l1.9 2"/></svg>',
    wave: '<svg viewBox="0 0 24 24" aria-hidden="true"><line x1="4" y1="10" x2="4" y2="14"/><line x1="8" y1="7" x2="8" y2="17"/><line x1="12" y1="4" x2="12" y2="20"/><line x1="16" y1="7" x2="16" y2="17"/><line x1="20" y1="10" x2="20" y2="14"/></svg>',
    chat: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M21 12a8 8 0 0 1-11.6 7.1L4 20l1-4.6A8 8 0 1 1 21 12z"/></svg>',
    down: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 5v14"/><path d="M6 13l6 6 6-6"/></svg>',
    alert: '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9"/><line x1="12" y1="8" x2="12" y2="12.5"/><line x1="12" y1="16" x2="12" y2="16"/></svg>',
    video: '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="6" width="13" height="12" rx="2.5"/><path d="M16 10.5l5-3v9l-5-3"/></svg>'
  };

  var NUM_BARS = 22;

  // ------------------------------------------------------------------------
  // Instance state
  // ------------------------------------------------------------------------
  var S = {
    avatar: AVATARS[0],
    state: 'off',
    engineReady: false,
    sessionMine: false,
    restarting: false,
    pinned: true,
    cur: { user: null, avatar: null },
    level: 0,
    rafId: 0,
    lastFrameAt: 0,
    holdHasFrame: false,
    holdFadeTimer: 0,
    vfcHandle: 0,
    active: false,
    listeners: [],
    timers: [],
    observer: null,
    destroyed: false,
    engineSubscribed: false,
    lastErrorAt: 0
  };
  var E = {}; // element refs

  // ------------------------------------------------------------------------
  // Helpers
  // ------------------------------------------------------------------------
  function $(id) { return document.getElementById(id); }
  function safe(fn) {
    return function () {
      try { return fn.apply(this, arguments); } catch (e) {
        try { console.warn('[p4_stage]', e && e.message ? e.message : e); } catch (e2) { /* ignore */ }
      }
      return undefined;
    };
  }
  function on(target, evt, fn, opts) {
    if (!target || !target.addEventListener) return;
    var wrapped = safe(fn);
    target.addEventListener(evt, wrapped, opts || false);
    S.listeners.push([target, evt, wrapped, opts || false]);
  }
  function later(fn, ms) {
    var t = setTimeout(safe(fn), ms);
    S.timers.push(t);
    return t;
  }
  function el(tag, cls, html) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (html != null) n.innerHTML = html;
    return n;
  }
  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }
  function avatarById(id) {
    for (var i = 0; i < AVATARS.length; i++) if (AVATARS[i].id === id) return AVATARS[i];
    return null;
  }
  function RL() {
    var r = window.RocketLive;
    return (r && typeof r.start === 'function') ? r : null;
  }
  function engineSource() {
    var r = RL();
    try { return r && typeof r.getSource === 'function' ? r.getSource() : null; } catch (e) { return null; }
  }
  function engineState() {
    var r = RL();
    try { return r && typeof r.getState === 'function' ? (r.getState() || 'idle') : 'idle'; } catch (e) { return 'idle'; }
  }
  function isMineActive() {
    var st = engineState();
    return st !== 'idle' && engineSource() === 'p4';
  }
  function legacyAvatarKey() {
    try {
      /* global currentActiveAvatar */
      if (typeof currentActiveAvatar !== 'undefined' && currentActiveAvatar) return String(currentActiveAvatar);
    } catch (e) { /* ignore */ }
    return null;
  }
  function legacyAmp() {
    try {
      /* global LiveAudioEngine */
      if (typeof LiveAudioEngine !== 'undefined' && LiveAudioEngine && typeof LiveAudioEngine.currentAmp === 'number') {
        return LiveAudioEngine.currentAmp;
      }
    } catch (e) { /* ignore */ }
    return 0;
  }
  function isP4Visible() {
    var pane = $('pillar-4');
    return !!(pane && pane.classList.contains('active'));
  }

  // ------------------------------------------------------------------------
  // Legacy shim: keep every legacy node alive (hidden)
  // ------------------------------------------------------------------------
  function ensureShim(pane) {
    var shim = $('p4-legacy-shim');
    if (!shim) {
      shim = el('div', 'p4s-legacy-shim');
      shim.id = 'p4-legacy-shim';
      shim.setAttribute('aria-hidden', 'true');
      shim.hidden = true;
      shim.style.display = 'none';
    }
    // Park every original child of #pillar-4 (moat strip, grid, cards, logs...)
    var kids = Array.prototype.slice.call(pane.childNodes);
    kids.forEach(function (n) {
      if (n === shim) return;
      if (n.id === 'p4s-root') return;
      shim.appendChild(n);
    });
    pane.appendChild(shim);
    // Recreate any legacy IDs that are missing anywhere in the document.
    LEGACY_IDS.forEach(function (id) {
      if ($(id)) return;
      var tag = LEGACY_TAGS[id] || (id.indexOf('lbl-') === 0 ? 'span' : 'div');
      var n = document.createElement(tag);
      n.id = id;
      if (tag === 'canvas') { n.width = 320; n.height = 320; }
      if (tag === 'input') n.type = id === 'chk-official-video-avatar' ? 'checkbox' : 'file';
      shim.appendChild(n);
    });
    // Keep at least one .rowan-sub-chk so recalcRowanAutopilot() has inputs.
    if (!document.querySelector('.rowan-sub-chk')) {
      var c = document.createElement('input');
      c.type = 'checkbox'; c.className = 'rowan-sub-chk'; c.setAttribute('data-amt', '0');
      shim.appendChild(c);
    }
    return shim;
  }

  // ------------------------------------------------------------------------
  // Build UI
  // ------------------------------------------------------------------------
  function chipHtml(av) {
    return '' +
      '<span class="p4s-chip-face"><img src="' + esc(av.thumb) + '?v=38" alt="" loading="eager" decoding="async"></span>' +
      '<span class="p4s-chip-txt">' +
        '<span class="p4s-chip-name">' + esc(av.name) + '</span>' +
        '<span class="p4s-chip-voice">' + esc(av.voice) + '</span>' +
      '</span>';
  }

  function build(pane) {
    var root = el('div', 'p4s');
    root.id = 'p4s-root';

    var bars = '';
    for (var i = 0; i < NUM_BARS; i++) bars += '<i style="--i:' + i + '"></i>';

    root.innerHTML = '' +
      '<header class="p4s-head">' +
        '<div class="p4s-head-txt">' +
          '<h2 class="p4s-title">Live Avatar <span class="p4s-title-sep">·</span> <span class="p4s-title-model">Gemini 3.8 Live</span></h2>' +
          '<p class="p4s-sub">A real-time, face-to-face voice conversation — native 24 fps video avatar, 24 kHz voice, interrupt anytime.</p>' +
        '</div>' +
        '<div class="p4s-cast" id="p4s-cast" role="radiogroup" aria-label="Choose avatar"></div>' +
      '</header>' +
      '<div class="p4s-body">' +
        '<div class="p4s-stage-col">' +
          '<div class="p4s-stage" id="p4s-stage" data-state="idle" data-group="idle" data-mode="video">' +
            '<div class="p4s-media">' +
              '<div class="p4s-backdrop" id="p4s-backdrop"></div>' +
              '<img class="p4s-poster" id="p4s-poster" alt="" decoding="async">' +
              '<canvas class="p4s-hold" id="p4s-hold" width="704" height="1280" aria-hidden="true"></canvas>' +
              '<video class="p4s-video" id="p4s-video" playsinline autoplay preload="auto"></video>' +
              '<div class="p4s-portrait" id="p4s-portrait"></div>' +
            '</div>' +
            '<div class="p4s-shade" aria-hidden="true"></div>' +
            '<div class="p4s-ring" aria-hidden="true"></div>' +
            '<div class="p4s-badges">' +
              '<span class="p4s-live" id="p4s-live"><i></i>LIVE</span>' +
              '<span class="p4s-mode" id="p4s-mode">' + ICONS.video + '<span id="p4s-mode-txt">24 fps video</span></span>' +
            '</div>' +
            '<div class="p4s-plate">' +
              '<div class="p4s-plate-name" id="p4s-plate-name">Kira</div>' +
              '<div class="p4s-plate-meta" id="p4s-plate-meta">Aoede voice · Gemini 3.8 Live video avatar</div>' +
            '</div>' +
            '<div class="p4s-viz" id="p4s-viz" aria-hidden="true">' + bars + '</div>' +
          '</div>' +
        '</div>' +
        '<section class="p4s-convo" aria-label="Conversation">' +
          '<div class="p4s-convo-head">' +
            '<div class="p4s-convo-title">' + ICONS.chat + '<span>Conversation</span></div>' +
            '<div class="p4s-state" id="p4s-state" data-group="idle"><span class="p4s-ink" aria-hidden="true"></span><span class="p4s-state-txt" id="p4s-state-txt">Ready</span></div>' +
          '</div>' +
          '<div class="p4s-tx-wrap">' +
            '<div class="p4s-tx" id="p4s-tx" role="log" aria-live="polite" aria-relevant="additions text">' +
              '<div class="p4s-empty" id="p4s-empty">' +
                '<div class="p4s-empty-ico">' + ICONS.wave + '</div>' +
                '<div class="p4s-empty-title">Start a conversation and just talk.</div>' +
                '<div class="p4s-empty-sub" id="p4s-empty-sub">Kira listens, thinks and answers face-to-face in real time. Interrupt anytime — she stops instantly.</div>' +
              '</div>' +
            '</div>' +
            '<button type="button" class="p4s-jump" id="p4s-jump" hidden>' + ICONS.down + '<span>Latest</span></button>' +
          '</div>' +
          '<div class="p4s-error" id="p4s-error" hidden>' + ICONS.alert + '<span id="p4s-error-txt"></span></div>' +
          '<div class="p4s-controls">' +
            '<button type="button" class="p4s-primary" id="p4s-primary" data-mode="start">' +
              '<span class="p4s-btn-ico" id="p4s-primary-ico">' + ICONS.mic + '</span>' +
              '<span id="p4s-primary-txt">Start conversation</span>' +
            '</button>' +
            '<button type="button" class="p4s-secondary" id="p4s-interrupt" disabled>' +
              '<span class="p4s-btn-ico">' + ICONS.hand + '</span><span>Interrupt</span>' +
            '</button>' +
          '</div>' +
          '<div class="p4s-hint">' + ICONS.mic + '<span>Just talk — interrupt anytime</span></div>' +
        '</section>' +
      '</div>';

    pane.insertBefore(root, pane.firstChild);

    E.root = root;
    E.stage = $('p4s-stage');
    E.poster = $('p4s-poster');
    E.hold = $('p4s-hold');
    E.video = $('p4s-video');
    E.portrait = $('p4s-portrait');
    E.backdrop = $('p4s-backdrop');
    E.viz = $('p4s-viz');
    E.bars = Array.prototype.slice.call(E.viz.querySelectorAll('i'));
    E.cast = $('p4s-cast');
    E.plateName = $('p4s-plate-name');
    E.plateMeta = $('p4s-plate-meta');
    E.modeTxt = $('p4s-mode-txt');
    E.live = $('p4s-live');
    E.body = E.root.querySelector('.p4s-body');
    E.stateBox = $('p4s-state');
    E.stateTxt = $('p4s-state-txt');
    E.tx = $('p4s-tx');
    E.empty = $('p4s-empty');
    E.emptySub = $('p4s-empty-sub');
    E.jump = $('p4s-jump');
    E.err = $('p4s-error');
    E.errTxt = $('p4s-error-txt');
    E.primary = $('p4s-primary');
    E.primaryTxt = $('p4s-primary-txt');
    E.primaryIco = $('p4s-primary-ico');
    E.interrupt = $('p4s-interrupt');

    // The stage video must stay unmuted (engine audio rides on it).
    E.video.muted = false;

    AVATARS.forEach(function (av) {
      var b = el('button', 'p4s-chip', chipHtml(av));
      b.type = 'button';
      b.setAttribute('role', 'radio');
      b.setAttribute('data-id', av.id);
      b.setAttribute('aria-checked', 'false');
      b.title = av.name + ' — ' + av.voice + ' voice' + (av.video ? ' · official 3.8 video avatar' : ' · 2D portrait, audio mode');
      on(b, 'click', function () { chooseAvatar(av.id, true); });
      E.cast.appendChild(b);
    });

    on(E.primary, 'click', onPrimary);
    on(E.interrupt, 'click', onInterrupt);
    on(E.jump, 'click', function () { scrollToBottom(true); });
    on(E.tx, 'scroll', function () {
      S.pinned = nearBottom();
      if (S.pinned) E.jump.hidden = true;
    }, { passive: true });

    // Video lifecycle → crossfade + hold-frame bookkeeping (see bindVideo)
    startFrameCopy();
  }

  // ------------------------------------------------------------------------
  // Avatar selection
  // ------------------------------------------------------------------------
  function setPoster(av) {
    var img = E.poster;
    img.classList.remove('is-ready');
    img.onerror = null;
    if (!av.video) {
      img.removeAttribute('src');
      return;
    }
    var wantFull = !!av.full;
    img.onload = function () { img.classList.add('is-ready'); };
    img.onerror = function () {
      if (wantFull) { wantFull = false; img.classList.add('is-thumb'); img.src = av.thumb + '?v=38'; }
    };
    img.classList.toggle('is-thumb', !wantFull);
    img.src = wantFull ? (av.full + '?v=38') : (av.thumb + '?v=38');
  }

  function mountPortraitCanvas(show) {
    var c = $('kira-stage-canvas');
    if (!c) return;
    if (show) {
      if (c.parentNode !== E.portrait) E.portrait.appendChild(c);
      c.classList.add('p4s-portrait-canvas');
    } else {
      var shim = $('p4-legacy-shim');
      var ring = $('kira-portrait-ring');
      var home = ring && shim && shim.contains(ring) ? ring : shim;
      if (home && c.parentNode !== home) home.appendChild(c);
      c.classList.remove('p4s-portrait-canvas');
    }
  }

  function renderAvatar() {
    var av = S.avatar;
    E.stage.setAttribute('data-mode', av.video ? 'video' : 'portrait');
    E.stage.setAttribute('data-avatar', av.id);
    E.plateName.textContent = av.name;
    E.plateMeta.textContent = av.voice + ' voice · ' + (av.video ? 'Gemini 3.8 Live video avatar' : '2D portrait · 24 kHz audio');
    E.modeTxt.textContent = av.video ? '24 fps video' : '24 kHz audio';
    E.backdrop.style.backgroundImage = 'url("' + av.thumb + '?v=38")';
    E.emptySub.textContent = av.name + ' listens, thinks and answers face-to-face in real time. Interrupt anytime — ' +
      (av.id === 'kira' || av.id === 'vera' ? 'she' : 'he') + ' stops instantly.';
    setPoster(av);
    mountPortraitCanvas(!av.video);
    // Clear any held frame from the previous avatar.
    S.holdHasFrame = false;
    E.stage.classList.remove('is-hold', 'is-video');
    Array.prototype.forEach.call(E.cast.querySelectorAll('.p4s-chip'), function (b) {
      var sel = b.getAttribute('data-id') === av.id;
      b.classList.toggle('is-active', sel);
      b.setAttribute('aria-checked', sel ? 'true' : 'false');
    });
  }

  function chooseAvatar(id, fromUser) {
    var av = avatarById(id);
    if (!av) return;
    var changed = av !== S.avatar;
    S.avatar = av;
    renderAvatar();
    if (fromUser) {
      // Keep the legacy app (omni bar, PiP, cursor) in sync without greeting.
      try {
        if (typeof window.selectAvatarProfile === 'function') {
          S.syncingLegacy = true;
          window.selectAvatarProfile(av.key, av.voice, null, false);
        }
      } catch (e) { /* ignore */ } finally { S.syncingLegacy = false; }
    }
    if (changed && isMineActive()) restartSession();
  }

  // ------------------------------------------------------------------------
  // Session control
  // ------------------------------------------------------------------------
  function startSession() {
    var r = RL();
    if (!r) { showError('The live engine is still loading — try again in a moment.'); return; }
    hideError();
    var av = S.avatar;
    if (!av.video) mountPortraitCanvas(true);
    if (av.video) {
      if (S.videoUsed) freshVideoElement();
      S.videoUsed = true;
    }
    S.sessionMine = true;
    S.cur.user = null; S.cur.avatar = null;
    var opts = {
      avatar: av.key,
      avatarName: av.name,
      voice: av.voice,
      video: !!av.video,
      tools: false,
      mic: true,
      videoEl: E.video,
      source: 'p4'
    };
    setUiState('connecting');
    ensureStageInView();
    try {
      var p = r.start(opts);
      if (p && typeof p.then === 'function') {
        p.then(function (res) {
          if (res && res.ok === false) {
            showError(humanError(res.error || res.message || 'could not start'));
            syncFromEngine();
          } else if (res && av.video && res.videoActive === false) {
            E.modeTxt.textContent = 'audio only';
          }
        }, function (err) {
          showError(humanError(err));
          syncFromEngine();
        });
      }
    } catch (e) {
      showError(humanError(e));
      setUiState('idle');
    }
  }

  function stopSession() {
    var r = RL();
    S.sessionMine = false;
    try { if (r && typeof r.stop === 'function') r.stop(); } catch (e) { /* ignore */ }
    finalizeBubbles(false);
    setUiState('idle');
  }

  function restartSession() {
    if (S.restarting) return;
    S.restarting = true;
    try {
      // RocketLive.start() quietly replaces the running session (no idle flash).
      finalizeBubbles(false);
      addSystemNote('Switched to ' + S.avatar.name + ' · ' + S.avatar.voice);
      later(function () { S.restarting = false; if (!S.destroyed) startSession(); }, 60);
    } catch (e) {
      S.restarting = false;
    }
  }

  function onPrimary() {
    if (!RL()) { showError('The live engine is still loading — try again in a moment.'); return; }
    var st = engineState();
    if (st !== 'idle' && engineSource() === 'p4') { stopSession(); return; }
    if (st !== 'idle' && engineSource() && engineSource() !== 'p4') {
      // Another surface owns the engine — take over cleanly.
      try { RL().stop(); } catch (e) { /* ignore */ }
      later(startSession, 200);
      return;
    }
    startSession();
  }

  function onInterrupt() {
    var r = RL();
    if (!r || typeof r.interrupt !== 'function') return;
    try { r.interrupt(); } catch (e) { /* ignore */ }
    markInterrupted();
  }

  function humanError(err) {
    var m = err && (err.message || err.reason || err.error) ? (err.message || err.reason || err.error) : String(err || '');
    if (/permission|notallowed|denied/i.test(m)) return 'Microphone access was blocked. Allow the mic in the browser bar and try again.';
    if (/notfound|no.*device/i.test(m)) return 'No microphone was found on this device.';
    return m ? ('Live session error — ' + m) : 'Live session error — please try again.';
  }
  function showError(msg) {
    if (!E.err) return;
    E.errTxt.textContent = msg;
    E.err.hidden = false;
    S.lastErrorAt = Date.now();
  }
  function hideError() { if (E.err) E.err.hidden = true; }

  function ensureStageInView() {
    try {
      var body = E.root.querySelector('.p4s-body');
      if (!body) return;
      var r = body.getBoundingClientRect();
      var omni = document.querySelector('.omni-copilot-bar');
      var bottomLimit = window.innerHeight - 12;
      if (omni) {
        var or = omni.getBoundingClientRect();
        var cs = window.getComputedStyle(omni);
        if (cs.position === 'fixed' && cs.display !== 'none' && or.height > 0) bottomLimit = or.top - 10;
      }
      var nav = document.querySelector('.top-nav');
      var topLimit = nav ? nav.getBoundingClientRect().bottom + 10 : 10;
      var delta = 0;
      if (r.bottom > bottomLimit) delta = r.bottom - bottomLimit;
      var head = E.root.getBoundingClientRect();
      if (head.top - delta < topLimit) delta = head.top - topLimit;
      if (Math.abs(delta) > 4) window.scrollBy({ top: delta, behavior: 'smooth' });
    } catch (e) { /* ignore */ }
  }

  // ------------------------------------------------------------------------
  // UI state
  // ------------------------------------------------------------------------
  function setUiState(st) {
    if (!STATE_LABEL[st]) st = 'idle';
    S.state = st;
    var group = STATE_GROUP[st];
    E.stage.setAttribute('data-state', st);
    E.stage.setAttribute('data-group', group);
    E.stateBox.setAttribute('data-group', group);
    E.stateBox.setAttribute('data-state', st);
    var label = STATE_LABEL[st];
    if (st === 'idle' && !S.engineReady) label = STATE_LABEL.off;
    E.stateTxt.textContent = label;

    var running = st !== 'idle' && st !== 'off';
    E.primary.setAttribute('data-mode', running ? 'end' : 'start');
    E.primaryTxt.textContent = running ? 'End' : (S.engineReady ? 'Start conversation' : 'Engine loading…');
    E.primaryIco.innerHTML = running ? ICONS.stop : ICONS.mic;
    E.primary.disabled = !S.engineReady && !running;
    E.primary.setAttribute('aria-pressed', running ? 'true' : 'false');
    E.interrupt.disabled = !(st === 'speaking' || st === 'thinking');
    E.live.classList.toggle('is-on', running && st !== 'connecting');
    if (document.body) document.body.classList.toggle('p4s-session-live', running);
  }

  function syncFromEngine() {
    var r = RL();
    S.engineReady = !!r;
    if (!r) { setUiState('off'); return; }
    var src = engineSource();
    var st = engineState();
    if (src && src !== 'p4' && st !== 'idle') { setUiState('idle'); return; }
    setUiState(st || 'idle');
  }

  // ------------------------------------------------------------------------
  // Transcript
  // ------------------------------------------------------------------------
  function nearBottom() {
    var t = E.tx;
    return (t.scrollHeight - t.scrollTop - t.clientHeight) < 56;
  }
  function scrollToBottom(force) {
    if (!E.tx) return;
    if (!force && !S.pinned) { E.jump.hidden = false; return; }
    E.tx.scrollTop = E.tx.scrollHeight;
    S.pinned = true;
    E.jump.hidden = true;
  }
  function mergeText(prev, incoming, detail) {
    incoming = String(incoming == null ? '' : incoming);
    if (detail && (detail.delta === true || detail.isDelta === true)) return prev + incoming;
    if (detail && detail.cumulative === true) return incoming;
    if (!prev) return incoming;
    if (incoming.indexOf(prev) === 0) return incoming;          // cumulative update
    if (prev.slice(-incoming.length) === incoming) return prev; // duplicate delta
    var needsSpace = !/\s$/.test(prev) && !/^[\s.,!?;:'’)]/.test(incoming);
    return prev + (needsSpace ? ' ' : '') + incoming;            // delta
  }
  function hideEmpty() { if (E.empty && E.empty.parentNode) E.empty.parentNode.removeChild(E.empty); }

  function makeBubble(who) {
    hideEmpty();
    var row = el('div', 'p4s-msg p4s-msg-' + who + ' is-partial');
    if (who === 'avatar') {
      var av = S.avatar;
      row.innerHTML = '<span class="p4s-msg-face"><img src="' + esc(av.thumb) + '?v=38" alt=""></span>' +
        '<div class="p4s-msg-col"><div class="p4s-msg-who">' + esc(av.name) + '</div><div class="p4s-bubble"></div></div>';
    } else {
      row.innerHTML = '<div class="p4s-msg-col"><div class="p4s-msg-who">You</div><div class="p4s-bubble"></div></div>';
    }
    row._text = '';
    row._bubble = row.querySelector('.p4s-bubble');
    E.tx.appendChild(row);
    // Cap history so very long demos stay light.
    var msgs = E.tx.querySelectorAll('.p4s-msg, .p4s-note');
    if (msgs.length > 120) { for (var i = 0; i < msgs.length - 120; i++) msgs[i].parentNode.removeChild(msgs[i]); }
    return row;
  }
  function finalizeRow(row, interrupted) {
    if (!row) return;
    row.classList.remove('is-partial');
    if (interrupted && !row.classList.contains('is-interrupted')) {
      row.classList.add('is-interrupted');
      var tag = el('span', 'p4s-msg-tag', 'interrupted');
      var col = row.querySelector('.p4s-msg-col');
      if (col) col.appendChild(tag);
    }
    if (!row._text) row.parentNode && row.parentNode.removeChild(row);
  }
  function finalizeBubbles(interrupted) {
    finalizeRow(S.cur.user, false);
    finalizeRow(S.cur.avatar, interrupted);
    S.cur.user = null; S.cur.avatar = null;
  }
  function markInterrupted() {
    if (S.cur.avatar) { finalizeRow(S.cur.avatar, true); S.cur.avatar = null; }
  }
  function addSystemNote(text) {
    if (!E.tx) return;
    hideEmpty();
    var n = el('div', 'p4s-note', '<span>' + esc(text) + '</span>');
    E.tx.appendChild(n);
    scrollToBottom(false);
  }
  function onTranscript(who, detail) {
    if (!detail) return;
    // RocketLive sends {text (cumulative for the turn), delta (new piece), final}.
    var hasText = typeof detail.text === 'string';
    var text = hasText ? detail.text : (typeof detail.delta === 'string' ? detail.delta : '');
    var d = hasText ? { cumulative: true } : { delta: true };
    if (!text && !detail.final) return;
    var wasPinned = S.pinned || nearBottom();
    if (who === 'user') {
      if (S.cur.avatar) { finalizeRow(S.cur.avatar, S.state === 'speaking'); S.cur.avatar = null; }
      if (!S.cur.user) {
        if (!text) return;
        S.cur.user = makeBubble('user');
      }
      var u = S.cur.user;
      if (text) { u._text = mergeText(u._text, text, d); u._bubble.textContent = u._text; }
      if (detail.final) { finalizeRow(u, false); S.cur.user = null; }
    } else {
      if (S.cur.user) { finalizeRow(S.cur.user, false); S.cur.user = null; }
      if (!S.cur.avatar) {
        if (!text) return;
        S.cur.avatar = makeBubble('avatar');
      }
      var a = S.cur.avatar;
      if (text) { a._text = mergeText(a._text, text, d); a._bubble.textContent = a._text; }
      if (detail.final) { finalizeRow(a, !!detail.interrupted); S.cur.avatar = null; }
    }
    S.pinned = wasPinned;
    scrollToBottom(false);
  }

  // ------------------------------------------------------------------------
  // Engine events (window CustomEvents: rocketlive:<evt>)
  // ------------------------------------------------------------------------
  function eventIsMine(detail) {
    var src = detail && typeof detail === 'object' ? detail.source : null;
    // 'server' / 'local' describe who interrupted, not which surface owns it.
    if (!src || src === 'server' || src === 'local') src = engineSource();
    return src === 'p4' || (!src && S.sessionMine);
  }
  function subscribeEngine() {
    if (S.engineSubscribed) return;
    S.engineSubscribed = true;
    on(window, 'rocketlive:state', function (ev) {
      var d = ev.detail || {};
      var st = typeof d === 'string' ? d : (d.state || d.to || engineState());
      if (!eventIsMine(d)) { if (S.state !== 'idle') setUiState('idle'); return; }
      setUiState(st);
      if (st === 'idle') { finalizeBubbles(false); S.sessionMine = false; }
    });
    on(window, 'rocketlive:user_transcript', function (ev) { if (eventIsMine(ev.detail)) onTranscript('user', ev.detail); });
    on(window, 'rocketlive:avatar_transcript', function (ev) { if (eventIsMine(ev.detail)) onTranscript('avatar', ev.detail); });
    on(window, 'rocketlive:turn_complete', function (ev) { if (eventIsMine(ev.detail)) finalizeBubbles(false); });
    on(window, 'rocketlive:interrupted', function (ev) { if (eventIsMine(ev.detail)) markInterrupted(); });
    on(window, 'rocketlive:error', function (ev) {
      if (!eventIsMine(ev.detail)) return;
      showError(humanError(ev.detail || {}));
    });
    on(window, 'rocketlive:ready', function (ev) {
      if (!eventIsMine(ev.detail)) return;
      hideError();
      var d = ev.detail || {};
      if (S.avatar.video && d.videoActive === false) {
        E.modeTxt.textContent = 'audio only';
      }
    });
  }

  function waitForEngine() {
    var tries = 0;
    var tick = function () {
      if (S.destroyed) return;
      if (RL()) { S.engineReady = true; syncFromEngine(); return; }
      tries += 1;
      if (tries === 40) showError('The live engine did not load. Reload the page to try again.');
      later(tick, tries < 40 ? 300 : 2000);
    };
    tick();
  }

  // ------------------------------------------------------------------------
  // Video: copy frames to the hold canvas so turns never flash black
  // ------------------------------------------------------------------------
  function sourceVideo() {
    var r = RL();
    var v = null;
    try { v = r && typeof r.getVideoEl === 'function' ? r.getVideoEl() : null; } catch (e) { v = null; }
    return (v && v.tagName === 'VIDEO') ? v : E.video;
  }
  function copyFrame(v) {
    if (!v || v.readyState < 2 || !v.videoWidth) return false;
    var c = E.hold;
    if (c.width !== v.videoWidth || c.height !== v.videoHeight) { c.width = v.videoWidth; c.height = v.videoHeight; }
    try {
      c.getContext('2d').drawImage(v, 0, 0, c.width, c.height);
      S.holdHasFrame = true;
      return true;
    } catch (e) { return false; }
  }
  function startFrameCopy() { bindVideo(E.video); }

  function bindVideo(v) {
    if (!v) return;
    v.muted = false;
    v.playsInline = true;
    v.autoplay = true;
    v.setAttribute('playsinline', '');
    v.setAttribute('webkit-playsinline', '');
    on(v, 'playing', function () { if (v === E.video) S.lastFrameAt = performance.now(); });
    on(v, 'emptied', function () { if (v === E.video) E.stage.classList.remove('is-video'); });
    on(v, 'error', function () { if (v === E.video) E.stage.classList.remove('is-video'); });
    if (typeof v.requestVideoFrameCallback === 'function') {
      var cb = function () {
        if (S.destroyed || v !== E.video) return; // retired element: stop the chain
        if (sourceVideo() === v && S.avatar.video) {
          S.lastFrameAt = performance.now();
          copyFrame(v);
        }
        try { v.requestVideoFrameCallback(cb); } catch (e) { /* ignore */ }
      };
      try { v.requestVideoFrameCallback(cb); } catch (e) { /* ignore */ }
      S.useVfc = true;
    }
  }

  // Each RocketLive session gets a brand-new <video>. RocketLive's VideoSink
  // detaches the previous session's element 240 ms after stop(); reusing the
  // same element for an immediate restart (avatar switch) would let that
  // deferred detach kill the new MediaSource (silent, frozen avatar).
  function freshVideoElement() {
    var old = E.video;
    if (!old || !old.parentNode) return;
    var v = document.createElement('video');
    v.className = old.className;
    v.preload = 'auto';
    old.removeAttribute('id');
    v.id = 'p4s-video';
    old.parentNode.insertBefore(v, old.nextSibling);
    E.video = v;
    bindVideo(v);
    later(function () {
      try { old.pause(); } catch (e) { /* ignore */ }
      if (old.parentNode) old.parentNode.removeChild(old);
    }, 900);
  }
  function adoptForeignVideo() {
    // If the engine renders into its own <video>, host it inside the stage.
    var v = sourceVideo();
    if (v && v !== E.video && v.parentNode && !E.stage.contains(v)) {
      v.classList.add('p4s-video', 'p4s-video-foreign');
      E.video.parentNode.insertBefore(v, E.video.nextSibling);
    }
    return v;
  }

  // ------------------------------------------------------------------------
  // Render loop (only while P4 is visible)
  // ------------------------------------------------------------------------
  var barPhase = [];
  for (var bi = 0; bi < NUM_BARS; bi++) barPhase.push(Math.random() * Math.PI * 2);

  function frame(ts) {
    if (S.destroyed || !S.active) { S.rafId = 0; return; }
    S.rafId = requestAnimationFrame(frame);
    try { tick(ts || performance.now()); } catch (e) { /* never break the loop */ }
  }
  function tick(now) {
    var st = S.state;
    var group = STATE_GROUP[st] || 'idle';
    var av = S.avatar;

    // Re-fit periodically (content above the stage can change height).
    if (!S.lastLayoutAt || now - S.lastLayoutAt > 700) { S.lastLayoutAt = now; layout(); }

    // --- video presence / crossfade ---
    if (av.video) {
      var v = adoptForeignVideo();
      var fresh = false;
      if (v && v.readyState >= 2 && v.videoWidth > 0 && !v.paused && !v.ended) {
        if (!S.useVfc || v !== E.video) {
          // Fallback path: sample frames ourselves.
          if (copyFrame(v)) S.lastFrameAt = now;
        }
        fresh = (now - S.lastFrameAt) < 260;
      }
      var running = st !== 'idle' && st !== 'off';
      E.stage.classList.toggle('is-video', fresh);
      // Hold the last frame briefly after video stops (and while a turn ends),
      // then let the idle poster (breathing) take over.
      var holdMs = (st === 'speaking' || st === 'thinking') ? 2200 : 900;
      var holdOn = S.holdHasFrame && running && (fresh || (now - S.lastFrameAt) < holdMs);
      E.stage.classList.toggle('is-hold', holdOn);
    } else {
      E.stage.classList.remove('is-video', 'is-hold');
    }

    // --- output level ---
    var target = 0;
    if (group === 'speaking') {
      var r = RL();
      var lv = 0;
      try { lv = r && typeof r.getOutputLevel === 'function' ? Number(r.getOutputLevel()) || 0 : 0; } catch (e) { lv = 0; }
      if (!lv) lv = Math.min(1, legacyAmp() * 1.6);
      target = Math.max(0.06, Math.min(1, lv * 1.35));
    } else if (st === 'user_speaking') {
      target = 0.32;
    }
    S.level += (target - S.level) * (target > S.level ? 0.35 : 0.12);
    var L = S.level;
    E.stage.style.setProperty('--p4s-level', L.toFixed(3));

    // --- visualizer bars ---
    var t = now / 1000;
    var bars = E.bars;
    for (var i = 0; i < bars.length; i++) {
      var x = i / (bars.length - 1);
      var env = 0.35 + 0.65 * Math.sin(Math.PI * x); // taller in the middle
      var h;
      if (group === 'speaking') {
        var wob = 0.55 + 0.45 * Math.sin(t * (7.5 + (i % 5)) + barPhase[i]);
        h = 0.12 + env * L * wob * 1.15;
      } else if (group === 'listening') {
        var amp = st === 'user_speaking' ? 0.42 : 0.16;
        h = 0.1 + env * amp * (0.5 + 0.5 * Math.sin(t * 3.2 + i * 0.55));
      } else if (group === 'thinking') {
        var travel = Math.sin(t * 5 - i * 0.45);
        h = 0.1 + 0.22 * env * Math.max(0, travel);
      } else {
        h = 0.08;
      }
      bars[i].style.transform = 'scaleY(' + Math.max(0.06, Math.min(1, h)).toFixed(3) + ')';
    }
  }
  function setActive(active) {
    active = !!active;
    if (S.active === active) return;
    S.active = active;
    document.body && document.body.classList.toggle('p4s-on', active);
    if (active && !S.rafId) S.rafId = requestAnimationFrame(frame);
    if (active) { syncFromEngine(); later(layout, 30); }
  }

  // ------------------------------------------------------------------------
  // Fit the stage to the laptop viewport: the whole stage + controls stay
  // visible above the fixed omni bar at scroll 0 (1280×800 → 1440×900+).
  // ------------------------------------------------------------------------
  function layout() {
    if (!E.root || !E.body || !S.active) return;
    var h;
    if (window.innerWidth <= 1100) {
      h = 560;
    } else {
      var top = E.body.getBoundingClientRect().top + (window.scrollY || window.pageYOffset || 0);
      var limit = window.innerHeight - 14;
      var omni = document.querySelector('.omni-copilot-bar');
      if (omni) {
        var cs = window.getComputedStyle(omni);
        var r = omni.getBoundingClientRect();
        if (cs.position === 'fixed' && cs.display !== 'none' && cs.visibility !== 'hidden' && r.height > 0 && r.top > window.innerHeight * 0.5) {
          limit = r.top - 14;
        }
      }
      h = Math.round(limit - top);
      h = Math.max(460, Math.min(660, h));
    }
    if (Math.abs(h - (S.stageH || 0)) > 2) {
      S.stageH = h;
      E.root.style.setProperty('--p4s-stage-h', h + 'px');
    }
  }

  // ------------------------------------------------------------------------
  // Pillar switching: stop a p4 session when leaving the tab
  // ------------------------------------------------------------------------
  function onPillarChange(num) {
    var p4 = Number(num) === 4;
    setActive(p4 && isP4Visible());
    if (!p4 && engineSource() === 'p4' && engineState() !== 'idle') {
      stopSession();
    }
  }
  function installSwitchWrapper() {
    var orig = window.switchPillar;
    if (typeof orig !== 'function' || orig.__p4sWrapped) return;
    var wrapped = function (num) {
      var res = orig.apply(this, arguments);
      try { if (window.__P4S && typeof window.__P4S.onPillar === 'function') window.__P4S.onPillar(num); } catch (e) { /* ignore */ }
      return res;
    };
    wrapped.__p4sWrapped = true;
    wrapped.__p4sOrig = orig;
    window.switchPillar = wrapped;
  }
  function installAvatarWrapper() {
    var orig = window.selectAvatarProfile;
    if (typeof orig !== 'function' || orig.__p4sWrapped) return;
    var wrapped = function (key) {
      var res = orig.apply(this, arguments);
      try { if (window.__P4S && typeof window.__P4S.onLegacyAvatar === 'function') window.__P4S.onLegacyAvatar(key); } catch (e) { /* ignore */ }
      return res;
    };
    wrapped.__p4sWrapped = true;
    wrapped.__p4sOrig = orig;
    window.selectAvatarProfile = wrapped;
  }
  function onLegacyAvatar(key) {
    if (S.syncingLegacy) return;
    var id = LEGACY_TO_ID[String(key || '')];
    if (id && (!S.avatar || S.avatar.id !== id)) chooseAvatar(id, false);
  }
  function observePane(pane) {
    if (typeof MutationObserver === 'undefined') return;
    S.observer = new MutationObserver(safe(function () {
      var vis = isP4Visible();
      setActive(vis);
      if (!vis && engineSource() === 'p4' && engineState() !== 'idle') stopSession();
    }));
    S.observer.observe(pane, { attributes: true, attributeFilter: ['class'] });
  }

  // ------------------------------------------------------------------------
  // Init / destroy
  // ------------------------------------------------------------------------
  function preload() {
    AVATARS.forEach(function (av) {
      var srcs = [av.thumb];
      if (av.full) srcs.push(av.full);
      srcs.forEach(function (s) { var i = new Image(); i.decoding = 'async'; i.src = s + '?v=38'; });
    });
  }

  function init() {
    var pane = $('pillar-4');
    if (!pane) return false;
    var old = $('p4s-root');
    if (old && old.parentNode) old.parentNode.removeChild(old);
    ensureShim(pane);
    pane.classList.add('p4s-pane');
    build(pane);

    var id = LEGACY_TO_ID[legacyAvatarKey() || ''] || 'kira';
    S.avatar = avatarById(id) || AVATARS[0];
    renderAvatar();

    subscribeEngine();
    S.engineReady = !!RL();
    syncFromEngine();
    if (!S.engineReady) waitForEngine();

    installSwitchWrapper();
    installAvatarWrapper();
    observePane(pane);
    on(window, 'resize', function () { S.lastLayoutAt = 0; layout(); });
    setActive(isP4Visible());
    preload();
    return true;
  }

  function destroy() {
    S.destroyed = true;
    S.active = false;
    if (S.rafId) { try { cancelAnimationFrame(S.rafId); } catch (e) { /* ignore */ } S.rafId = 0; }
    S.listeners.forEach(function (l) { try { l[0].removeEventListener(l[1], l[2], l[3]); } catch (e) { /* ignore */ } });
    S.listeners = [];
    S.timers.forEach(function (t) { clearTimeout(t); });
    S.timers = [];
    if (S.observer) { try { S.observer.disconnect(); } catch (e) { /* ignore */ } }
    try { mountPortraitCanvas(false); } catch (e) { /* ignore */ }
    var root = $('p4s-root');
    if (root && root.parentNode) root.parentNode.removeChild(root);
    if (document.body) document.body.classList.remove('p4s-on', 'p4s-session-live');
  }

  window.__P4S = {
    version: VERSION,
    destroy: destroy,
    onPillar: safe(onPillarChange),
    onLegacyAvatar: safe(onLegacyAvatar),
    select: safe(function (id) { chooseAvatar(LEGACY_TO_ID[id] || id, true); }),
    start: safe(startSession),
    stop: safe(stopSession),
    state: function () { return S.state; },
    avatars: AVATARS.map(function (a) { return { id: a.id, key: a.key, name: a.name, voice: a.voice, video: a.video }; })
  };

  var boot = safe(function () {
    if (!init()) {
      // #pillar-4 not parsed yet (unexpected) — retry once the DOM is ready.
      if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', safe(init), { once: true });
    }
  });
  boot();
})();
