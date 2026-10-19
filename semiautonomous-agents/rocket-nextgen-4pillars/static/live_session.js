/*
 * RocketLive — Gemini 3.8 Live session engine for the Rocket studio.
 *
 * Streams the microphone natively to /ws/live-avatar (16 kHz PCM16, server VAD + native barge-in)
 * and plays the official Gemini 3.8 Live video avatar (fragmented MP4 over MSE) or 24 kHz PCM audio.
 *
 * API (window.RocketLive):
 *   start({avatar, voice, video, tools, mic, videoEl, source}) -> Promise<{ok, videoActive, toolsEnabled, error?}>
 *   stop(), interrupt(), sendText(text[, startOpts]) -> Promise, enableMic() -> Promise
 *   isActive(), getState(), getSource(), getOutputLevel(), getVideoEl(), isVideoMode(), isMicOn()
 *   on(evt, fn) -> unsubscribe, off(evt, fn)
 * Events (also dispatched as window CustomEvents 'rocketlive:<evt>'):
 *   state {state, prev, source}, user_transcript {text, delta, final}, avatar_transcript {text, delta, final},
 *   turn_complete, interrupted {source}, tool_call {id, name, args}, error {message}, ready {videoActive, toolsEnabled}
 * The start() promise never rejects (failures resolve with ok:false and also emit 'error').
 */
(function () {
  'use strict';

  var VERSION = '2026.10.16-a';
  var TAG = '[RocketLive]';

  // Idempotent: replace any previously loaded copy cleanly (e.g. a newer copy injected for testing).
  try {
    if (window.RocketLive && typeof window.RocketLive.__teardown === 'function') {
      window.RocketLive.__teardown();
    }
  } catch (e) {}

  var cfg = {
    frameMs: 40,               // mic frame size sent to the server
    bargeInMinRms: 0.03,       // absolute floor for barge-in while the avatar is audible
    bargeInRatio: 3.0,         // ...and mic RMS must exceed echoFloor * ratio
    bargeInFrames: 3,          // consecutive loud frames needed to open the gate
    bargeInHangoverMs: 700,    // keep forwarding this long after the last loud frame
    echoTailMs: 300,           // treat the avatar as audible for this long after playback stops
    prerollFrames: 6,          // frames replayed to the server when the gate opens (~240 ms)
    duckVolume: 0.35,          // video volume while the user is barging in (until the server confirms)
    readyTimeoutMs: 30000,
    preReadyFrames: 25,        // mic frames buffered while connecting (~1 s)
    userSilenceMs: 900,        // input transcript silence that ends the 'user_speaking' state
    thinkingTimeoutMs: 12000,
    videoVoiceRms: 0.006,      // decoded avatar audio above this = the avatar is talking (video mode)
    videoVoiceHoldMs: 350,
    maxIdleLatency: 0.6,       // seconds of idle-video backlog before skipping ahead
    maxSpeakingLatency: 1.2    // seconds of speaking backlog before playing at 1.08x
  };

  // ------------------------------------------------------------------ events
  var listeners = {};
  function on(evt, fn) {
    if (typeof fn !== 'function') return function () {};
    (listeners[evt] = listeners[evt] || []).push(fn);
    return function () { off(evt, fn); };
  }
  function off(evt, fn) {
    var arr = listeners[evt];
    if (!arr) return;
    var i = arr.indexOf(fn);
    if (i >= 0) arr.splice(i, 1);
  }
  function emit(evt, detail) {
    var arr = listeners[evt] ? listeners[evt].slice() : [];
    for (var i = 0; i < arr.length; i++) {
      try { arr[i](detail); } catch (e) { try { console.warn(TAG, 'listener error for', evt, e); } catch (e2) {} }
    }
    try { window.dispatchEvent(new CustomEvent('rocketlive:' + evt, { detail: detail })); } catch (e) {}
  }

  // ------------------------------------------------------------------ legacy globals (bare names from the main inline script)
  function LAE() {
    try { return (typeof LiveAudioEngine !== 'undefined' && LiveAudioEngine) ? LiveAudioEngine : null; } catch (e) { return null; }
  }
  function legacyEpoch() {
    try { return (typeof commandEpoch === 'number') ? commandEpoch : 0; } catch (e) { return 0; }
  }
  function legacyDefaults() {
    var d = { avatar: 'Kira', voice: 'Aoede', video: true };
    try { if (typeof currentActiveAvatar === 'string' && currentActiveAvatar) d.avatar = currentActiveAvatar; } catch (e) {}
    try { if (typeof currentActiveVoice === 'string' && currentActiveVoice) d.voice = currentActiveVoice; } catch (e) {}
    try {
      var prof = (typeof AVATAR_PROFILES_MAP !== 'undefined' && AVATAR_PROFILES_MAP) ? AVATAR_PROFILES_MAP[d.avatar] : null;
      var enabled = (typeof officialVideoAvatarEnabled !== 'undefined') ? Boolean(officialVideoAvatarEnabled) : true;
      d.video = Boolean(enabled && prof && prof.hasOfficialVideo);
    } catch (e) {}
    return d;
  }

  // ------------------------------------------------------------------ helpers
  function nowMs() { return (window.performance && performance.now) ? performance.now() : Date.now(); }
  function abToB64(buf) {
    var bytes = new Uint8Array(buf);
    var bin = '';
    for (var i = 0; i < bytes.length; i += 0x8000) {
      bin += String.fromCharCode.apply(null, bytes.subarray(i, Math.min(bytes.length, i + 0x8000)));
    }
    return btoa(bin);
  }
  function b64ToBytes(b64) {
    var bin = atob(b64);
    var out = new Uint8Array(bin.length);
    for (var i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i);
    return out;
  }
  function bufferedEnd(el) {
    try {
      var b = el.buffered;
      return (b && b.length) ? b.end(b.length - 1) : 0;
    } catch (e) { return 0; }
  }
  function sbBufferedEnd(sb) {
    try {
      var b = sb.buffered;
      return (b && b.length) ? b.end(b.length - 1) : 0;
    } catch (e) { return 0; }
  }
  function wsUrl(opts) {
    var proto = location.protocol === 'https:' ? 'wss:' : 'ws:';
    var q = 'voice=' + encodeURIComponent(opts.voice || 'Aoede') +
      '&avatar=' + encodeURIComponent(opts.avatar || 'Kira') +
      '&video_avatar=' + (opts.video ? '1' : '0') +
      '&tools=' + (opts.tools ? '1' : '0');
    try {
      var tok = new URLSearchParams(location.search).get('auth_token');
      if (tok) q += '&auth_token=' + encodeURIComponent(tok);
    } catch (e) {}
    return proto + '//' + location.host + '/ws/live-avatar?' + q;
  }

  // ------------------------------------------------------------------ mic worklet (inline module)
  var WORKLET_SRC = [
    'class RocketMicProcessor extends AudioWorkletProcessor {',
    '  constructor(options) {',
    '    super();',
    '    var o = (options && options.processorOptions) || {};',
    '    this.ratio = sampleRate / (o.outRate || 16000);',
    '    this.frameSamples = o.frameSamples || 640;',
    '    this.buf = new Int16Array(this.frameSamples);',
    '    this.len = 0; this.pos = 0; this.acc = 0; this.accN = 0; this.sumSq = 0;',
    '  }',
    '  process(inputs) {',
    '    var input = inputs[0];',
    '    if (!input || !input[0]) return true;',
    '    var ch = input[0];',
    '    for (var i = 0; i < ch.length; i++) {',
    '      this.acc += ch[i]; this.accN++; this.pos += 1;',
    '      if (this.pos >= this.ratio) {',
    '        this.pos -= this.ratio;',
    '        var s = this.acc / this.accN; this.acc = 0; this.accN = 0;',
    '        if (s > 1) s = 1; else if (s < -1) s = -1;',
    '        this.buf[this.len++] = s < 0 ? s * 0x8000 : s * 0x7FFF;',
    '        this.sumSq += s * s;',
    '        if (this.len >= this.frameSamples) {',
    '          var rms = Math.sqrt(this.sumSq / this.len);',
    '          this.port.postMessage({ pcm: this.buf.buffer, rms: rms }, [this.buf.buffer]);',
    '          this.buf = new Int16Array(this.frameSamples); this.len = 0; this.sumSq = 0;',
    '        }',
    '      }',
    '    }',
    '    return true;',
    '  }',
    '}',
    "registerProcessor('rocket-mic-processor', RocketMicProcessor);"
  ].join('\n');
  var workletUrl = null;
  function getWorkletUrl() {
    if (!workletUrl) workletUrl = URL.createObjectURL(new Blob([WORKLET_SRC], { type: 'application/javascript' }));
    return workletUrl;
  }

  // ------------------------------------------------------------------ MSE video sink (single SourceBuffer, never blanks)
  var MIME_CANDIDATES = [
    'video/mp4; codecs="avc1.42E01E, mp4a.40.2"',
    'video/mp4; codecs="avc1.42c01f, mp4a.40.2"',
    'video/mp4; codecs="avc1.4D401E, mp4a.40.2"',
    'video/mp4; codecs="avc1.64001F, mp4a.40.2"',
    'video/mp4; codecs="avc1.42E01E"',
    'video/mp4'
  ];

  var internalVideo = null;
  function getInternalVideo() {
    if (internalVideo && document.body && document.body.contains(internalVideo)) return internalVideo;
    var v = document.createElement('video');
    v.id = 'rocketlive-video';
    v.setAttribute('playsinline', '');
    v.playsInline = true;
    v.autoplay = true;
    v.style.cssText = 'position:fixed;right:0;bottom:0;width:4px;height:4px;opacity:0.01;pointer-events:none;z-index:-1;';
    (document.body || document.documentElement).appendChild(v);
    internalVideo = v;
    return v;
  }

  function VideoSink(el, external, session) {
    this.v = el;
    this.external = external;
    this.session = session;
    this.ms = null;
    this.sb = null;
    this.url = null;
    this.ops = [];
    this.ready = false;
    this.closed = false;
    this.hasFrames = false;
    this.appended = 0;
    this.segments = 0;
    this.duck = false;
    this.handlers = [];
  }
  VideoSink.prototype.open = function () {
    var self = this;
    var v = this.v;
    if (typeof MediaSource === 'undefined') throw new Error('MediaSource is not supported in this browser');
    try { v.pause(); } catch (e) {}
    this.ms = new MediaSource();
    this.url = URL.createObjectURL(this.ms);
    v.playsInline = true;
    v.autoplay = true;
    v.muted = false;
    v.volume = 1;
    if (this.external) {
      v.style.transition = 'opacity 220ms ease';
      v.style.opacity = '0';
    }
    var onOpen = function () {
      try { self.ms.removeEventListener('sourceopen', onOpen); } catch (e) {}
      if (self.closed) return;
      var mime = null;
      for (var i = 0; i < MIME_CANDIDATES.length; i++) {
        try { if (MediaSource.isTypeSupported(MIME_CANDIDATES[i])) { mime = MIME_CANDIDATES[i]; break; } } catch (e) {}
      }
      if (!mime) { self.session && failSession(self.session, 'No supported MSE MP4 codec'); return; }
      try {
        self.sb = self.ms.addSourceBuffer(mime);
        self.sb.mode = 'sequence';
        self.sb.addEventListener('updateend', function () { self.pump(); });
        self.sb.addEventListener('error', function () { try { console.warn(TAG, 'SourceBuffer error'); } catch (e) {} });
        self.ready = true;
        self.pump();
      } catch (e) {
        try { console.warn(TAG, 'addSourceBuffer failed', e); } catch (e2) {}
      }
    };
    this.ms.addEventListener('sourceopen', onOpen);
    var onFrame = function () {
      if (self.closed) return;
      if (!self.hasFrames && v.videoWidth > 0) {
        self.hasFrames = true;
        if (self.external) v.style.opacity = '1';
        try { v.classList.add('rocketlive-has-frames'); } catch (e) {}
      }
    };
    this.listen('playing', onFrame);
    this.listen('loadeddata', onFrame);
    this.listen('timeupdate', onFrame);
    v.src = this.url;
  };
  VideoSink.prototype.listen = function (evt, fn) {
    try { this.v.addEventListener(evt, fn); this.handlers.push([evt, fn]); } catch (e) {}
  };
  VideoSink.prototype.beginSegment = function () {
    if (this.closed) return;
    this.segments++;
    this.ops.push({ kind: 'segment' });
    this.pump();
  };
  VideoSink.prototype.append = function (data) {
    if (this.closed) return;
    this.ops.push({ kind: 'append', data: data });
    this.pump();
  };
  VideoSink.prototype.pump = function () {
    if (!this.ready || !this.sb || this.closed) return;
    var sb = this.sb;
    var v = this.v;
    while (this.ops.length && !sb.updating) {
      var op = this.ops[0];
      if (op.kind === 'segment') {
        this.ops.shift();
        try { if (this.ms.readyState === 'open') sb.abort(); } catch (e) {}
        var end = sbBufferedEnd(sb);
        var t = Math.max(end, v.currentTime || 0);
        try { sb.timestampOffset = t; } catch (e) {}
        // Trim old media (> 30 s behind the playhead) to keep the SourceBuffer small.
        var cur = v.currentTime || 0;
        if (cur > 45) {
          try { sb.remove(0, cur - 30); return; } catch (e) {}
        }
        continue;
      }
      if (op.kind === 'flush') {
        this.ops.shift();
        try { if (this.ms.readyState === 'open') sb.abort(); } catch (e) {}
        var start = v.currentTime || 0;
        var bEnd = sbBufferedEnd(sb);
        if (bEnd > start + 0.05) {
          try { sb.remove(start, Infinity); op = null; } catch (e) {}
          if (op === null) {
            // After the removal completes, re-seek in place so the decoder pipeline drops stale frames.
            this.ops.unshift({ kind: 'reseek' });
            return;
          }
        }
        continue;
      }
      if (op.kind === 'reseek') {
        this.ops.shift();
        try {
          var be = sbBufferedEnd(sb);
          var target = Math.max(0, Math.min(v.currentTime || 0, be - 0.04));
          if (be > 0 && Math.abs((v.currentTime || 0) - target) > 0.001) v.currentTime = target;
        } catch (e) {}
        continue;
      }
      if (op.kind === 'trim') {
        this.ops.shift();
        if (op.end > 1) {
          try { sb.remove(0, op.end); return; } catch (e) {}
        }
        continue;
      }
      if (op.kind === 'append') {
        this.ops.shift();
        try {
          sb.appendBuffer(op.data);
          this.appended += op.data.byteLength || 0;
          if (v.paused && !this.session.dropping && !this.session.awaitingSegment) {
            var pp = v.play();
            if (pp && pp.catch) pp.catch(function () {});
          }
          return;
        } catch (e) {
          if (e && e.name === 'QuotaExceededError') {
            this.ops.unshift(op);
            var c2 = v.currentTime || 0;
            try { sb.remove(0, Math.max(0.1, c2 - 2)); } catch (e2) { this.ops.shift(); }
            return;
          }
          try { console.warn(TAG, 'appendBuffer failed', e && e.name); } catch (e3) {}
          continue;
        }
      }
      this.ops.shift();
    }
  };
  // Instant flush: silence now, keep the last frame visible, drop everything buffered ahead.
  VideoSink.prototype.flush = function () {
    if (this.closed) return;
    try { this.v.pause(); } catch (e) {}
    this.ops = this.ops.filter(function (o) { return o.kind !== 'append'; });
    this.ops.push({ kind: 'flush' });
    this.setDuck(false);
    this.pump();
  };
  VideoSink.prototype.isPlaying = function () {
    var v = this.v;
    if (this.closed || !v || v.paused || v.muted || v.volume === 0) return false;
    return (bufferedEnd(v) - (v.currentTime || 0)) > 0.02 && v.readyState >= 2;
  };
  VideoSink.prototype.isAudible = VideoSink.prototype.isPlaying;
  VideoSink.prototype.trim = function () {
    if (this.closed) return;
    var cur = this.v.currentTime || 0;
    if (cur > 50 && !this.ops.some(function (o) { return o.kind === 'trim'; })) {
      this.ops.push({ kind: 'trim', end: cur - 25 });
      this.pump();
    }
  };
  // Keep the live avatar close to real time: skip idle backlog, gently speed up a speaking backlog.
  VideoSink.prototype.controlLatency = function (speaking) {
    var v = this.v;
    if (this.closed || !v || v.paused || v.seeking) return;
    var ahead = bufferedEnd(v) - (v.currentTime || 0);
    try {
      if (!speaking && ahead > cfg.maxIdleLatency) {
        v.currentTime = bufferedEnd(v) - 0.12;
        if (v.playbackRate !== 1) v.playbackRate = 1;
      } else if (speaking && ahead > cfg.maxSpeakingLatency) {
        if (v.playbackRate !== 1.08) v.playbackRate = 1.08;
      } else if (v.playbackRate !== 1 && ahead < 0.35) {
        v.playbackRate = 1;
      }
    } catch (e) {}
  };
  VideoSink.prototype.setDuck = function (on) {
    if (this.duck === on) return;
    this.duck = on;
    try { this.v.volume = on ? cfg.duckVolume : 1; } catch (e) {}
  };
  VideoSink.prototype.close = function (fadeOut) {
    if (this.closed) return;
    this.closed = true;
    var v = this.v;
    this.ops = [];
    for (var i = 0; i < this.handlers.length; i++) {
      try { v.removeEventListener(this.handlers[i][0], this.handlers[i][1]); } catch (e) {}
    }
    this.handlers = [];
    try { v.pause(); } catch (e) {}
    try { v.volume = 1; } catch (e) {}
    try { v.classList.remove('rocketlive-has-frames'); } catch (e) {}
    if (this.external && fadeOut !== false) {
      try { v.style.opacity = '0'; } catch (e) {}
    }
    var url = this.url;
    var detach = function () {
      // Only detach if the element still plays OUR MediaSource (a new session may already own it).
      try { if (url && v.src === url) { v.removeAttribute('src'); v.load(); } } catch (e) {}
      try { if (url) URL.revokeObjectURL(url); } catch (e) {}
    };
    if (this.external && fadeOut !== false) setTimeout(detach, 240); else detach();
  };

  // ------------------------------------------------------------------ fallback 24 kHz PCM player (when LiveAudioEngine is absent)
  function PcmPlayer() {
    this.ctx = null; this.gain = null; this.analyser = null; this.nodes = []; this.nextTime = 0; this.data = null;
  }
  PcmPlayer.prototype.ensure = function () {
    if (!this.ctx || this.ctx.state === 'closed') {
      var AC = window.AudioContext || window.webkitAudioContext;
      this.ctx = new AC({ sampleRate: 24000 });
      this.gain = this.ctx.createGain();
      this.analyser = this.ctx.createAnalyser();
      this.analyser.fftSize = 512;
      this.data = new Uint8Array(this.analyser.fftSize);
      this.gain.connect(this.analyser);
      this.analyser.connect(this.ctx.destination);
      this.nextTime = 0;
    }
    if (this.ctx.state === 'suspended') { try { this.ctx.resume(); } catch (e) {} }
    return this.ctx;
  };
  PcmPlayer.prototype.play = function (b64) {
    var ctx = this.ensure();
    var bytes = b64ToBytes(b64);
    var n = Math.floor(bytes.length / 2);
    if (n <= 0) return;
    var dv = new DataView(bytes.buffer);
    var f32 = new Float32Array(n);
    for (var i = 0; i < n; i++) f32[i] = dv.getInt16(i * 2, true) / 32768;
    var buf = ctx.createBuffer(1, n, 24000);
    buf.getChannelData(0).set(f32);
    var src = ctx.createBufferSource();
    src.buffer = buf;
    src.connect(this.gain);
    var t = ctx.currentTime;
    if (this.nextTime < t) this.nextTime = t + 0.04;
    src.start(this.nextTime);
    this.nextTime += buf.duration;
    var self = this;
    this.nodes.push(src);
    src.onended = function () { self.nodes = self.nodes.filter(function (x) { return x !== src; }); };
  };
  PcmPlayer.prototype.stop = function () {
    for (var i = 0; i < this.nodes.length; i++) {
      try { this.nodes[i].onended = null; this.nodes[i].stop(0); } catch (e) {}
      try { this.nodes[i].disconnect(); } catch (e) {}
    }
    this.nodes = [];
    this.nextTime = 0;
  };
  PcmPlayer.prototype.isPlaying = function () {
    return !!(this.ctx && this.nodes.length && this.nextTime > this.ctx.currentTime);
  };
  PcmPlayer.prototype.level = function () {
    if (!this.analyser || !this.isPlaying()) return 0;
    this.analyser.getByteTimeDomainData(this.data);
    var s = 0;
    for (var i = 0; i < this.data.length; i++) { var x = (this.data[i] - 128) / 128; s += x * x; }
    return Math.sqrt(s / this.data.length);
  };
  var fallbackPlayer = null;

  // ------------------------------------------------------------------ session state
  var S = null;               // active session
  var sessionSeq = 0;
  var state = 'idle';
  var lastSource = null;
  var lastVideoEl = null;
  var outLevel = 0;
  var ticker = null;

  function setState(next) {
    if (next === state) return;
    var prev = state;
    state = next;
    emit('state', { state: next, prev: prev, source: S ? S.opts.source : lastSource });
  }

  function normalizeOpts(o) {
    o = o || {};
    var d = legacyDefaults();
    var avatar = o.avatar || d.avatar;
    var video = (typeof o.video === 'boolean') ? o.video : (o.avatar ? false : d.video);
    if (typeof o.video !== 'boolean' && o.avatar) {
      try {
        var prof = (typeof AVATAR_PROFILES_MAP !== 'undefined' && AVATAR_PROFILES_MAP) ? AVATAR_PROFILES_MAP[avatar] : null;
        var enabled = (typeof officialVideoAvatarEnabled !== 'undefined') ? Boolean(officialVideoAvatarEnabled) : true;
        video = Boolean(enabled && prof && prof.hasOfficialVideo);
      } catch (e) { video = true; }
    }
    return {
      avatar: avatar,
      voice: o.voice || (o.avatar ? (function () {
        try { var p = AVATAR_PROFILES_MAP[avatar]; return (p && p.voice) || d.voice; } catch (e) { return d.voice; }
      })() : d.voice),
      video: Boolean(video),
      tools: o.tools !== false,
      mic: o.mic !== false,
      videoEl: (o.videoEl && typeof o.videoEl === 'object' && o.videoEl.tagName === 'VIDEO') ? o.videoEl : null,
      source: o.source || 'omni'
    };
  }

  function sendJson(s, obj) {
    if (!s || !s.ws || s.ws.readyState !== 1) return false;
    try { s.ws.send(JSON.stringify(obj)); return true; } catch (e) { return false; }
  }

  function start(opts) {
    var o = normalizeOpts(opts);
    if (S) stopInternal(true);
    var s = {
      id: ++sessionSeq,
      opts: o,
      ws: null,
      ready: false,
      readyResolve: null,
      videoActive: false,
      toolsEnabled: o.tools,
      serverTurnActive: false,
      dropping: false,
      awaitingSegment: true,
      userText: '',
      userClosed: true,
      avatarText: '',
      lastUserTxMs: 0,
      serverUserSpeaking: false,
      localUserSpeakingUntil: 0,
      awaitingResponse: false,
      awaitingSince: 0,
      pendingTurnComplete: false,
      lastAudibleMs: 0,
      echoFloor: 0.01,
      ambient: 0.005,
      loudFrames: 0,
      gateOpenUntil: 0,
      preroll: [],
      preReady: [],
      pendingTexts: [],
      micOn: false,
      mic: null,
      video: null,
      analyser: null,
      stopped: false,
      stats: { framesSent: 0, framesGated: 0, gateOpens: 0, binaryIn: 0, audioIn: 0, toolCalls: 0, interrupts: 0 }
    };
    S = s;
    lastSource = o.source;
    setState('connecting');
    ensureTicker();

    // Output sinks are prepared synchronously (inside the user gesture) so autoplay with sound is allowed.
    if (o.video) {
      try {
        try { var LAC = window.AudioContext || window.webkitAudioContext; s.levelCtx = new LAC(); } catch (e0) { s.levelCtx = null; }
        var el = o.videoEl || getInternalVideo();
        s.video = new VideoSink(el, Boolean(o.videoEl), s);
        s.video.open();
        lastVideoEl = el;
        var pp = el.play();
        if (pp && pp.catch) pp.catch(function () {});
      } catch (e) {
        try { console.warn(TAG, 'video sink unavailable, using audio', e); } catch (e2) {}
        s.video = null;
        o.video = false;
      }
    }
    var lae = LAE();
    if (lae) {
      try { lae.allowNewTurnAudio(); } catch (e) {}
    }
    if (o.mic) startMic(s);

    var p = new Promise(function (resolve) { s.readyResolve = resolve; });
    openSocket(s);
    s.readyTimer = setTimeout(function () {
      if (S === s && !s.ready) failSession(s, 'Timed out connecting to Gemini 3.8 Live');
    }, cfg.readyTimeoutMs);
    return p;
  }

  function resolveReady(s, result) {
    if (s.readyResolve) {
      var r = s.readyResolve;
      s.readyResolve = null;
      try { r(result); } catch (e) {}
    }
  }

  function failSession(s, message) {
    if (!s) return;
    var msg = String(message || 'Live session error');
    try { console.warn(TAG, msg); } catch (e) {}
    emit('error', { message: msg, source: s.opts.source });
    resolveReady(s, { ok: false, error: msg, videoActive: false, toolsEnabled: s.toolsEnabled });
    if (S === s) stopInternal(false);
  }

  function openSocket(s) {
    var ws;
    try {
      ws = new WebSocket(wsUrl(s.opts));
    } catch (e) {
      failSession(s, 'Could not open the live socket: ' + (e && e.message));
      return;
    }
    ws.binaryType = 'arraybuffer';
    s.ws = ws;
    ws.onmessage = function (evt) {
      if (S !== s) return;
      try { handleMessage(s, evt.data); } catch (e) { try { console.warn(TAG, 'message handling error', e); } catch (e2) {} }
    };
    ws.onerror = function () {};
    ws.onclose = function (evt) {
      if (S !== s || s.stopped) return;
      var why = (evt && evt.code === 1008) ? 'Not authorized for the live socket' : ('Live session closed (' + (evt && evt.code) + ')');
      failSession(s, s.lastServerError || why);
    };
  }

  function handleMessage(s, data) {
    if (typeof data !== 'string') {
      // The official avatar streams video continuously (idle + speaking), so media alone
      // never implies a model turn; transcripts and tool calls do.
      s.stats.binaryIn++;
      if (!s.video || s.dropping || s.awaitingSegment) return;
      s.video.append(data);
      return;
    }
    var msg;
    try { msg = JSON.parse(data); } catch (e) { return; }
    var type = msg.type || '';

    if (type === 'ready') {
      s.ready = true;
      s.videoActive = Boolean(msg.video_avatar_active) && Boolean(s.video);
      s.toolsEnabled = msg.tools_enabled !== false && s.opts.tools;
      if (s.readyTimer) { clearTimeout(s.readyTimer); s.readyTimer = null; }
      if (!s.videoActive && s.video) {
        // Server fell back to audio: release the video sink.
        s.video.close(true);
        s.video = null;
      }
      // Flush mic audio captured while connecting, then any queued texts.
      var pre = s.preReady.splice(0);
      for (var i = 0; i < pre.length; i++) sendAudioFrame(s, pre[i]);
      var texts = s.pendingTexts.splice(0);
      for (var j = 0; j < texts.length; j++) sendJson(s, { type: 'text', text: texts[j] });
      if (texts.length) { s.awaitingResponse = true; s.awaitingSince = nowMs(); }
      updateState();
      var info = { videoActive: s.videoActive, toolsEnabled: s.toolsEnabled, avatar: msg.avatar || s.opts.avatar, serverVad: Boolean(msg.server_vad) };
      emit('ready', info);
      resolveReady(s, { ok: true, videoActive: s.videoActive, toolsEnabled: s.toolsEnabled });
      return;
    }
    if (type === 'error' || (msg.error && !type)) {
      s.lastServerError = String(msg.error || 'Live session error');
      emit('error', { message: s.lastServerError, source: s.opts.source });
      return;
    }
    if (type === 'new_video_segment') {
      s.awaitingSegment = false;
      s.dropping = false;
      if (s.video) s.video.beginSegment();
      return;
    }
    if (type === 'interrupted' || (msg.interrupted && !type)) {
      if (msg.local) {
        // Server acknowledged our click-interrupt. Keep dropping the stale turn until a turn boundary
        // (turn_complete), the next user turn (transcript / voice activity / sendText) or a fresh segment.
        return;
      }
      s.stats.interrupts++;
      s.dropping = false;
      s.awaitingSegment = true;
      s.serverTurnActive = false;
      s.turnEndMs = nowMs();
      flushPlayback(s);
      finishAvatarText(s, true);
      emit('interrupted', { source: 'server' });
      updateState();
      return;
    }
    if (type === 'input_transcript' || (msg.input_transcript && !type)) {
      var piece = String(msg.input_transcript || '');
      if (!piece) return;
      s.dropping = false;
      if (s.userClosed) { s.userText = ''; s.userClosed = false; }
      s.userText += piece;
      s.lastUserTxMs = nowMs();
      var fin = Boolean(msg.finished);
      emit('user_transcript', { text: s.userText.trim(), delta: piece, final: fin });
      if (fin) {
        s.userClosed = true;
        s.awaitingResponse = true;
        s.awaitingSince = nowMs();
      }
      updateState();
      return;
    }
    if (type === 'output_transcript' || (msg.output_transcript && !type)) {
      if (s.dropping) return;
      var opiece = String(msg.output_transcript || '');
      if (!opiece) return;
      s.serverTurnActive = true;
      markResponseStarted(s);
      s.avatarText += opiece;
      emit('avatar_transcript', { text: s.avatarText.trim(), delta: opiece, final: false });
      return;
    }
    if (type === 'audio' || (msg.audio_b64 && !type)) {
      s.stats.audioIn++;
      if (s.dropping || !msg.audio_b64) return;
      s.serverTurnActive = true;
      markResponseStarted(s);
      playAudioChunk(s, msg.audio_b64);
      return;
    }
    if (type === 'voice_activity') {
      s.serverUserSpeaking = msg.activity === 'start';
      if (s.serverUserSpeaking) s.dropping = false;
      if (!s.serverUserSpeaking && s.userText && !s.userClosed) {
        s.awaitingResponse = true;
        s.awaitingSince = nowMs();
      }
      updateState();
      return;
    }
    if (type === 'tool_call_batch' && Array.isArray(msg.calls)) {
      s.serverTurnActive = true;
      markResponseStarted(s);
      runToolCalls(s, msg.calls);
      return;
    }
    if (type === 'turn_complete' || (msg.turn_complete && !type)) {
      s.dropping = false;
      s.serverTurnActive = false;
      s.turnEndMs = nowMs();
      s.userClosed = true;
      s.awaitingResponse = false;
      finishAvatarText(s, false);
      s.pendingTurnComplete = true;
      updateState();
      return;
    }
    if (type === 'go_away') {
      emit('error', { message: 'Live session is about to expire; restart the mic to continue.', source: s.opts.source });
    }
  }

  function markResponseStarted(s) {
    s.awaitingResponse = false;
    if (!s.userClosed && s.userText) {
      s.userClosed = true;
      emit('user_transcript', { text: s.userText.trim(), delta: '', final: true });
    }
  }

  function finishAvatarText(s, interrupted) {
    if (s.avatarText.trim()) {
      emit('avatar_transcript', { text: s.avatarText.trim(), delta: '', final: true, interrupted: Boolean(interrupted) });
    }
    s.avatarText = '';
  }

  function useLegacyAudio(s) {
    var lae = LAE();
    return Boolean(lae && typeof lae.playPcmChunk === 'function' && !s.videoActive);
  }

  function playAudioChunk(s, b64) {
    var lae = LAE();
    if (useLegacyAudio(s)) {
      try {
        if (lae.ignoreIncomingAudio) lae.allowNewTurnAudio();
        lae.playPcmChunk(b64);
        return;
      } catch (e) {}
    }
    if (!fallbackPlayer) fallbackPlayer = new PcmPlayer();
    try { fallbackPlayer.play(b64); } catch (e) {}
  }

  function flushPlayback(s) {
    if (s.video) s.video.flush();
    var lae = LAE();
    if (lae && !s.videoActive) {
      try { lae.stopAll(); } catch (e) {}
      try { lae.allowNewTurnAudio(); } catch (e) {}
    }
    if (fallbackPlayer) fallbackPlayer.stop();
    s.pendingTurnComplete = false;
    s.gateOpenUntil = 0;
    s.loudFrames = 0;
    s.lastVoiceMs = 0;
  }

  // Is the avatar's VOICE audible right now? (The official avatar streams idle video continuously,
  // so in video mode we look at the decoded audio level, falling back to the server turn window.)
  function avatarAudible(s) {
    if (!s) return false;
    var t = nowMs();
    if (s.video && s.videoActive) {
      if (!s.video.isPlaying()) return false;
      var lvl = analyserLevel(s);
      if (lvl >= 0) {
        if (lvl > cfg.videoVoiceRms) s.lastVoiceMs = t;
        return (t - (s.lastVoiceMs || 0)) < cfg.videoVoiceHoldMs;
      }
      return Boolean(s.serverTurnActive) || (t - (s.turnEndMs || 0)) < 600;
    }
    var lae = LAE();
    if (useLegacyAudio(s)) {
      try { if (lae.isSpeakingOrQueued()) return true; } catch (e) {}
    }
    if (fallbackPlayer && fallbackPlayer.isPlaying()) return true;
    return false;
  }

  async function runToolCalls(s, calls) {
    var responses = [];
    for (var i = 0; i < calls.length; i++) {
      var call = calls[i] || {};
      s.stats.toolCalls++;
      emit('tool_call', { id: call.id, name: call.name, args: call.args || {} });
      var result = null;
      if (S === s && s.toolsEnabled && typeof window.executeAgentScreenTool === 'function') {
        try {
          result = await window.executeAgentScreenTool(call.name, call.args || {}, legacyEpoch());
        } catch (e) {
          result = { status: 'error', message: String((e && e.message) || e) };
        }
      }
      if (!result || typeof result !== 'object') result = { status: 'updated_on_screen' };
      responses.push({ id: call.id, name: call.name, result: result });
    }
    if (S === s) sendJson(s, { type: 'tool_result', responses: responses });
  }

  // ------------------------------------------------------------------ microphone
  function startMic(s) {
    if (s.mic || s.stopped) return Promise.resolve(Boolean(s.mic));
    var AC = window.AudioContext || window.webkitAudioContext;
    if (!AC || !navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      emit('error', { message: 'Microphone capture is not supported in this browser', source: s.opts.source });
      return Promise.resolve(false);
    }
    var mic = { ctx: null, stream: null, src: null, node: null, sink: null };
    s.mic = mic;
    try { mic.ctx = new AC(); } catch (e) {
      s.mic = null;
      emit('error', { message: 'Could not create an audio context for the microphone', source: s.opts.source });
      return Promise.resolve(false);
    }
    var frameSamples = Math.round(16000 * cfg.frameMs / 1000);
    return navigator.mediaDevices.getUserMedia({
      audio: { echoCancellation: true, noiseSuppression: true, autoGainControl: true, channelCount: 1 }
    }).then(function (stream) {
      if (S !== s || s.stopped || s.mic !== mic) {
        stream.getTracks().forEach(function (t) { try { t.stop(); } catch (e) {} });
        return false;
      }
      mic.stream = stream;
      var ctx = mic.ctx;
      var resumeP = (ctx.state === 'suspended') ? ctx.resume().catch(function () {}) : Promise.resolve();
      return resumeP.then(function () {
        mic.src = ctx.createMediaStreamSource(stream);
        mic.sink = ctx.createGain();
        mic.sink.gain.value = 0;
        mic.sink.connect(ctx.destination);
        var useWorklet = Boolean(ctx.audioWorklet && window.AudioWorkletNode);
        var p = useWorklet ? ctx.audioWorklet.addModule(getWorkletUrl()).then(function () {
          var node = new AudioWorkletNode(ctx, 'rocket-mic-processor', {
            numberOfInputs: 1, numberOfOutputs: 1, outputChannelCount: [1],
            processorOptions: { outRate: 16000, frameSamples: frameSamples }
          });
          node.port.onmessage = function (e) { onMicFrame(s, e.data.pcm, e.data.rms); };
          return node;
        }).catch(function () { return null; }) : Promise.resolve(null);
        return p.then(function (node) {
          if (S !== s || s.stopped || s.mic !== mic) return false;
          if (!node) node = makeScriptProcessor(ctx, s, frameSamples);
          mic.node = node;
          mic.src.connect(node);
          node.connect(mic.sink);
          s.micOn = true;
          emit('mic', { active: true, source: s.opts.source });
          updateState();
          return true;
        });
      });
    }).catch(function (err) {
      if (s.mic === mic) s.mic = null;
      try { mic.ctx && mic.ctx.close(); } catch (e) {}
      if (S === s) emit('error', { message: 'Microphone unavailable: ' + ((err && (err.message || err.name)) || err), source: s.opts.source });
      return false;
    });
  }

  function makeScriptProcessor(ctx, s, frameSamples) {
    var node = ctx.createScriptProcessor(4096, 1, 1);
    var ratio = ctx.sampleRate / 16000;
    var buf = new Int16Array(frameSamples), len = 0, pos = 0, acc = 0, accN = 0, sumSq = 0;
    node.onaudioprocess = function (e) {
      var ch = e.inputBuffer.getChannelData(0);
      for (var i = 0; i < ch.length; i++) {
        acc += ch[i]; accN++; pos += 1;
        if (pos >= ratio) {
          pos -= ratio;
          var v = acc / accN; acc = 0; accN = 0;
          if (v > 1) v = 1; else if (v < -1) v = -1;
          buf[len++] = v < 0 ? v * 0x8000 : v * 0x7FFF;
          sumSq += v * v;
          if (len >= frameSamples) {
            var rms = Math.sqrt(sumSq / len);
            onMicFrame(s, buf.buffer, rms);
            buf = new Int16Array(frameSamples); len = 0; sumSq = 0;
          }
        }
      }
    };
    return node;
  }

  function stopMic(s) {
    var mic = s && s.mic;
    if (!mic) return;
    s.mic = null;
    s.micOn = false;
    try { if (mic.node && mic.node.port) mic.node.port.onmessage = null; } catch (e) {}
    try { if (mic.node) mic.node.onaudioprocess = null; } catch (e) {}
    try { mic.src && mic.src.disconnect(); } catch (e) {}
    try { mic.node && mic.node.disconnect(); } catch (e) {}
    try { mic.sink && mic.sink.disconnect(); } catch (e) {}
    try { if (mic.stream) mic.stream.getTracks().forEach(function (t) { try { t.stop(); } catch (e2) {} }); } catch (e) {}
    try { if (mic.ctx && mic.ctx.state !== 'closed') mic.ctx.close(); } catch (e) {}
  }

  function sendAudioFrame(s, pcm) {
    if (sendJson(s, { type: 'audio', pcm16_b64: abToB64(pcm) })) s.stats.framesSent++;
  }

  // Echo-safe forwarding: while the avatar is audible only clearly-louder-than-echo speech opens the gate.
  function onMicFrame(s, pcm, rms) {
    if (S !== s || s.stopped || !pcm) return;
    var t = nowMs();
    rms = Number(rms) || 0;
    s.lastMicRms = rms;
    if (!s.ready) {
      s.preReady.push(pcm);
      if (s.preReady.length > cfg.preReadyFrames) s.preReady.shift();
      return;
    }
    var audible = avatarAudible(s);
    if (audible) s.lastAudibleMs = t;
    var echoWindow = audible || (t - s.lastAudibleMs) < cfg.echoTailMs;
    if (!echoWindow) {
      s.ambient += (rms - s.ambient) * 0.05;
      s.echoFloor += (Math.max(0.006, s.ambient) - s.echoFloor) * 0.01;
      s.loudFrames = 0;
      s.preroll.length = 0;
      if (s.video) s.video.setDuck(false);
      if (rms > Math.max(0.02, s.ambient * 3)) s.localUserSpeakingUntil = t + 400;
      sendAudioFrame(s, pcm);
      return;
    }
    var thr = Math.max(cfg.bargeInMinRms, s.echoFloor * cfg.bargeInRatio);
    if (rms > thr) {
      s.loudFrames++;
    } else {
      s.loudFrames = 0;
      s.echoFloor += (rms - s.echoFloor) * (rms > s.echoFloor ? 0.12 : 0.03);
      if (s.echoFloor < 0.004) s.echoFloor = 0.004;
    }
    var wasOpen = t < s.gateOpenUntil;
    if (s.loudFrames >= cfg.bargeInFrames || (wasOpen && rms > thr)) {
      s.gateOpenUntil = t + cfg.bargeInHangoverMs;
    }
    if (t < s.gateOpenUntil) {
      if (!wasOpen) {
        s.stats.gateOpens++;
        var pre = s.preroll.splice(0);
        for (var i = 0; i < pre.length; i++) sendAudioFrame(s, pre[i]);
        if (s.video) s.video.setDuck(true);
      }
      s.localUserSpeakingUntil = t + 400;
      sendAudioFrame(s, pcm);
    } else {
      if (wasOpen && s.video) s.video.setDuck(false);
      s.stats.framesGated++;
      s.preroll.push(pcm);
      if (s.preroll.length > cfg.prerollFrames) s.preroll.shift();
    }
  }

  // ------------------------------------------------------------------ state ticker
  function ensureTicker() {
    if (ticker) return;
    ticker = setInterval(tick, 50);
  }
  function computeLevel(s) {
    var raw = 0;
    if (!s) return 0;
    if (s.videoActive && s.video) {
      if (s.video.isPlaying()) {
        raw = analyserLevel(s);
        if (raw < 0) raw = avatarAudible(s) ? 0.22 + 0.12 * Math.abs(Math.sin(nowMs() * 0.012)) : 0;
        else raw = Math.min(1, raw * 4.2);
      }
    } else if (useLegacyAudio(s)) {
      var lae = LAE();
      try { if (lae.isSpeakingOrQueued()) raw = Math.min(1, (Number(lae.currentAmp) || 0) * 1.6); } catch (e) {}
    } else if (fallbackPlayer) {
      raw = Math.min(1, fallbackPlayer.level() * 4.2);
    }
    return raw;
  }
  function analyserLevel(s) {
    try {
      if (!s.analyser) {
        if (s.analyserFailed || !s.video || !s.video.hasFrames) return -1;
        var v = s.video.v;
        var cap = v.captureStream ? v.captureStream() : (v.mozCaptureStream ? v.mozCaptureStream() : null);
        if (!cap || !cap.getAudioTracks().length) { return -1; }
        var AC = window.AudioContext || window.webkitAudioContext;
        var ctx = s.levelCtx || new AC();
        s.levelCtx = null;
        var src = ctx.createMediaStreamSource(cap);
        var an = ctx.createAnalyser();
        an.fftSize = 512;
        an.smoothingTimeConstant = 0.2;
        var mute = ctx.createGain();
        mute.gain.value = 0;
        src.connect(an);
        an.connect(mute);
        mute.connect(ctx.destination);
        s.analyser = { ctx: ctx, an: an, data: new Uint8Array(an.fftSize), src: src, stream: cap };
      }
      var a = s.analyser;
      if (a.ctx.state === 'suspended') { try { a.ctx.resume(); } catch (e) {} }
      a.an.getByteTimeDomainData(a.data);
      var sum = 0;
      for (var i = 0; i < a.data.length; i++) { var x = (a.data[i] - 128) / 128; sum += x * x; }
      return Math.sqrt(sum / a.data.length);
    } catch (e) {
      s.analyserFailed = true;
      return -1;
    }
  }
  function updateState() {
    var s = S;
    if (!s) { setState('idle'); return; }
    if (!s.ready) { setState('connecting'); return; }
    var t = nowMs();
    var audible = avatarAudible(s);
    if (audible) s.lastAudibleMs = t;
    var userSpeaking = s.serverUserSpeaking || (t - s.lastUserTxMs) < cfg.userSilenceMs ||
      (t < s.localUserSpeakingUntil && t < s.gateOpenUntil);
    if (s.awaitingResponse && (t - s.awaitingSince) > cfg.thinkingTimeoutMs) s.awaitingResponse = false;
    var next;
    if (audible && !(t < s.gateOpenUntil && userSpeaking)) next = 'speaking';
    else if (userSpeaking) next = 'user_speaking';
    else if (s.awaitingResponse || (s.serverTurnActive && !audible)) next = 'thinking';
    else next = 'listening';
    setState(next);
  }
  function tick() {
    var s = S;
    try {
      var raw = computeLevel(s);
      outLevel += (raw - outLevel) * (raw > outLevel ? 0.5 : 0.18);
      if (outLevel < 0.003) outLevel = 0;
      if (!s) { setState('idle'); return; }
      updateState();
      if (s.video && s.videoActive) {
        s.video.controlLatency(state === 'speaking');
        if (!s.lastTrimMs || nowMs() - s.lastTrimMs > 10000) { s.lastTrimMs = nowMs(); s.video.trim(); }
      }
      if (s.pendingTurnComplete && !s.serverTurnActive && !avatarAudible(s)) {
        s.pendingTurnComplete = false;
        if (s.video) s.video.setDuck(false);
        emit('turn_complete', { source: s.opts.source });
      }
    } catch (e) {}
  }

  // ------------------------------------------------------------------ public API
  function stopInternal(quiet) {
    var s = S;
    if (!s) return;
    S = null;
    s.stopped = true;
    if (s.readyTimer) { clearTimeout(s.readyTimer); s.readyTimer = null; }
    try { if (s.micOn) sendJson(s, { type: 'audio_stream_end' }); } catch (e) {}
    stopMic(s);
    var ws = s.ws;
    s.ws = null;
    if (ws) {
      try {
        ws.onmessage = null; ws.onerror = null; ws.onclose = null;
        if (ws.readyState === 0) ws.onopen = function () { try { ws.close(); } catch (e) {} };
        else if (ws.readyState === 1) ws.close(1000, 'client stop');
      } catch (e) {}
    }
    if (s.video) { s.video.close(true); s.video = null; }
    if (s.analyser) {
      try { s.analyser.src.disconnect(); } catch (e) {}
      try { s.analyser.ctx.close(); } catch (e) {}
      s.analyser = null;
    }
    if (s.levelCtx) { try { s.levelCtx.close(); } catch (e) {} s.levelCtx = null; }
    var lae = LAE();
    if (lae && !s.videoActive) {
      try { if (lae.isSpeakingOrQueued()) lae.stopAll(); } catch (e) {}
      try { lae.allowNewTurnAudio(); } catch (e) {}
    }
    if (fallbackPlayer) fallbackPlayer.stop();
    resolveReady(s, { ok: false, error: 'stopped', videoActive: false, toolsEnabled: s.toolsEnabled });
    outLevel = 0;
    if (!quiet) {
      setState('idle');
      emit('stopped', { source: s.opts.source });
    } else {
      // Restart in progress: report idle only through the next session's 'connecting' state.
      state = 'idle';
    }
  }

  function stop() { stopInternal(false); }

  function interrupt(withText) {
    var s = S;
    if (!s) return;
    s.stats.interrupts++;
    flushPlayback(s);
    s.dropping = true;
    if (s.videoActive) s.awaitingSegment = true;
    finishAvatarText(s, true);
    var msg = { type: 'interrupt' };
    if (withText) msg.text = String(withText);
    if (!sendJson(s, msg)) s.dropping = false;
    s.serverTurnActive = false;
    s.turnEndMs = nowMs();
    s.lastVoiceMs = 0;
    emit('interrupted', { source: 'local' });
    updateState();
  }

  function sendText(text, startOpts) {
    var t = String(text || '').trim();
    if (!t) return Promise.resolve({ ok: false, error: 'empty text' });
    var s = S;
    var p;
    if (!s) {
      var o = Object.assign({ tools: true, mic: false, source: 'omni' }, startOpts || {});
      p = start(o);
      s = S;
    } else {
      p = Promise.resolve({ ok: true, videoActive: s.videoActive, toolsEnabled: s.toolsEnabled });
    }
    if (!s) return p;
    s.userText = t;
    s.userClosed = true;
    emit('user_transcript', { text: t, delta: t, final: true, typed: true });
    if (s.ready) {
      if (avatarAudible(s) || s.serverTurnActive) {
        interrupt(t); // one message: flush + drop the stale turn + send the new request (it interrupts server-side)
      } else {
        s.dropping = false;
        sendJson(s, { type: 'text', text: t });
      }
      s.awaitingResponse = true;
      s.awaitingSince = nowMs();
    } else {
      s.pendingTexts.push(t);
    }
    updateState();
    return p;
  }

  function enableMic() {
    var s = S;
    if (!s) return Promise.resolve(false);
    s.opts.mic = true;
    return startMic(s);
  }

  function teardown() {
    try { stopInternal(false); } catch (e) {}
    if (ticker) { clearInterval(ticker); ticker = null; }
    listeners = {};
  }

  window.RocketLive = {
    version: VERSION,
    config: cfg,
    start: start,
    stop: stop,
    interrupt: interrupt,
    sendText: sendText,
    enableMic: enableMic,
    isActive: function () { return Boolean(S); },
    isReady: function () { return Boolean(S && S.ready); },
    getState: function () { return S ? state : 'idle'; },
    getSource: function () { return S ? S.opts.source : null; },
    getOptions: function () { return S ? Object.assign({}, S.opts) : null; },
    getOutputLevel: function () { return S ? Math.max(0, Math.min(1, outLevel)) : 0; },
    getVideoEl: function () { return (S && S.video) ? S.video.v : (S ? null : null); },
    isVideoMode: function () { return Boolean(S && S.video && S.videoActive); },
    hasVideoFrames: function () { return Boolean(S && S.video && S.video.hasFrames && S.video.v.videoWidth > 0); },
    isMicOn: function () { return Boolean(S && S.micOn); },
    on: on,
    off: off,
    debug: function () {
      var s = S;
      if (!s) return { state: 'idle', lastVideoEl: Boolean(lastVideoEl) };
      var v = s.video ? s.video.v : null;
      return {
        state: state, source: s.opts.source, opts: Object.assign({}, s.opts, { videoEl: Boolean(s.opts.videoEl) }),
        ready: s.ready, videoActive: s.videoActive, toolsEnabled: s.toolsEnabled, micOn: s.micOn,
        dropping: s.dropping, awaitingSegment: s.awaitingSegment, serverTurnActive: s.serverTurnActive,
        echoFloor: s.echoFloor, ambient: s.ambient, lastMicRms: s.lastMicRms || 0,
        stats: Object.assign({}, s.stats),
        video: v ? {
          videoWidth: v.videoWidth, videoHeight: v.videoHeight, paused: v.paused, muted: v.muted, volume: v.volume,
          currentTime: v.currentTime, bufferedEnd: bufferedEnd(v), readyState: v.readyState,
          appendedBytes: s.video.appended, segments: s.video.segments, hasFrames: s.video.hasFrames
        } : null,
        outputLevel: outLevel
      };
    },
    __teardown: teardown
  };
})();
