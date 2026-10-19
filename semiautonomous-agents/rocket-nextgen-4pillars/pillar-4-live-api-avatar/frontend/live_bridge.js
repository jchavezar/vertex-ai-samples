/*
 * RocketLive bridge — wires the bottom Omni bar, floating PiP / dock avatar and the legacy
 * stop / barge-in buttons to window.RocketLive (native Gemini 3.8 Live mic streaming).
 *
 * While a RocketLive session is active the legacy webkitSpeechRecognition path is fully disabled,
 * so two recognizers never compete for the microphone.
 */
(function () {
  'use strict';

  var TAG = '[RocketLiveBridge]';

  // Idempotent re-init: tear down a previous copy, but always wrap the ORIGINAL legacy functions.
  try {
    if (window.__rocketLiveBridge && typeof window.__rocketLiveBridge.teardown === 'function') {
      window.__rocketLiveBridge.teardown();
    }
  } catch (e) {}

  var ORIG = window.__rocketLiveBridgeOriginals || {};
  window.__rocketLiveBridgeOriginals = ORIG;
  [
    'toggleUnifiedLiveVoiceMic', 'ensureLiveAvatarWebSocket', 'stopAllAudioAndAvatarNow', 'bargeInInterruptNow',
    'selectAvatarProfile', 'drawVisemeTileWithJawSync', 'startBrowserSpeechRecognizer',
    'handleAvatarTapInterruptOrVoice', 'toggleOfficialVideoAvatarMode'
  ].forEach(function (n) {
    try { if (!ORIG[n] && typeof window[n] === 'function') ORIG[n] = window[n]; } catch (e) {}
  });

  function RL() { return window.RocketLive || null; }
  function callOrig(name, self, args) {
    var fn = ORIG[name];
    if (typeof fn !== 'function') return undefined;
    try { return fn.apply(self, args); } catch (e) { try { console.warn(TAG, name, 'failed', e); } catch (e2) {} }
    return undefined;
  }
  function $(id) { return document.getElementById(id); }
  function avatarName() {
    try { if (typeof currentActiveAvatar === 'string' && currentActiveAvatar) return currentActiveAvatar; } catch (e) {}
    var r = RL();
    var o = r && r.getOptions ? r.getOptions() : null;
    return (o && o.avatar) || 'Kira';
  }
  function avatarVoice() {
    try { if (typeof currentActiveVoice === 'string' && currentActiveVoice) return currentActiveVoice; } catch (e) {}
    return 'Aoede';
  }
  function wantVideo(avatar) {
    try {
      var prof = (typeof AVATAR_PROFILES_MAP !== 'undefined' && AVATAR_PROFILES_MAP) ? AVATAR_PROFILES_MAP[avatar || avatarName()] : null;
      var enabled = (typeof officialVideoAvatarEnabled !== 'undefined') ? Boolean(officialVideoAvatarEnabled) : true;
      return Boolean(enabled && prof && prof.hasOfficialVideo);
    } catch (e) { return false; }
  }

  // ---------------------------------------------------------------- legacy recognizer + flags
  function disableLegacyRecognizer() {
    try {
      if (typeof speechRec !== 'undefined' && speechRec) {
        try { speechRec.onresult = null; speechRec.onend = null; speechRec.onerror = null; } catch (e) {}
        try { speechRec.abort(); } catch (e) {}
      }
    } catch (e) {}
    try { speechRec = null; } catch (e) {}
    try { if (typeof speechFinalizeTimer !== 'undefined' && speechFinalizeTimer) { clearTimeout(speechFinalizeTimer); speechFinalizeTimer = null; } } catch (e) {}
    try { if (typeof micResumeTimer !== 'undefined' && micResumeTimer) { clearTimeout(micResumeTimer); micResumeTimer = null; } } catch (e) {}
    try { if (typeof spokenUtteranceBuffer !== 'undefined') spokenUtteranceBuffer = ''; } catch (e) {}
    // Close any legacy /ws/live-avatar socket so two live sessions never talk at once.
    try {
      if (typeof p4Ws !== 'undefined' && p4Ws) {
        if (typeof LiveAudioEngine !== 'undefined' && LiveAudioEngine) LiveAudioEngine.closeSocketQuietly(p4Ws);
        p4Ws = null;
      }
    } catch (e) {}
  }
  function resetLegacyFlags(micOn) {
    try { p4TurnInProgress = false; } catch (e) {}
    try { isKiraBusyOrSpeaking = false; } catch (e) {}
    try { voiceMicActive = Boolean(micOn); } catch (e) {}
  }

  // ---------------------------------------------------------------- UI sync
  var MIC_SVG = '<svg class="ico ico-sm" viewBox="0 0 24 24"><path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/></svg>';
  var lastOmniCaption = '';

  function setOmniButton(stateName) {
    var btn = $('btn-omni-voice');
    var lbl = $('lbl-omni-voice');
    var labels = {
      connecting: 'Connecting Live...',
      listening: 'Listening',
      user_speaking: 'Listening',
      thinking: 'Thinking',
      speaking: 'Speaking'
    };
    var active = stateName && stateName !== 'idle';
    if (btn) btn.classList.toggle('mic-live', Boolean(active));
    if (lbl) {
      var r = RL();
      var micOn = r && r.isMicOn && r.isMicOn();
      var txt = active ? (labels[stateName] || 'Listening') : 'Start Live Voice & Mic';
      if (active && !micOn && stateName === 'listening') txt = 'Live (Mic Off)';
      lbl.textContent = txt;
    }
  }

  function setPipStatus(stateName) {
    var el = $('kira-pip-status');
    var card = $('kira-pip-card');
    var name = String(avatarName() || 'KIRA').toUpperCase();
    var words = {
      connecting: 'CONNECTING',
      listening: 'LISTENING',
      user_speaking: 'HEARING YOU',
      thinking: 'THINKING',
      speaking: 'SPEAKING'
    };
    if (card) card.classList.toggle('speaking', stateName === 'speaking');
    if (!el) return;
    if (!stateName || stateName === 'idle') {
      el.textContent = name + ' (' + String(avatarVoice()).toUpperCase() + ') · READY';
      return;
    }
    el.textContent = name + ' · ' + (words[stateName] || 'LISTENING');
  }

  function setOmniCaption(text) {
    var el = $('omni-live-transcript');
    if (!el || !text) return;
    lastOmniCaption = text;
    el.textContent = text;
  }

  function isOmni() {
    var r = RL();
    return Boolean(r && r.isActive() && r.getSource() === 'omni');
  }

  var subs = [];
  function bindEvents() {
    var r = RL();
    if (!r || typeof r.on !== 'function') return false;
    subs.push(r.on('state', function (d) {
      var st = d && d.state;
      setPipStatus(st);
      if (st === 'idle') {
        setOmniButton('idle');
        resetLegacyFlags(false);
        return;
      }
      disableLegacyRecognizer();
      try { isKiraBusyOrSpeaking = (st === 'speaking'); } catch (e) {}
      if (isOmni()) {
        setOmniButton(st);
        if (st === 'listening' && !lastOmniCaption) setOmniCaption('Listening — speak anytime; talk over ' + avatarName() + ' to interrupt.');
      } else {
        setOmniButton('idle');
      }
    }));
    subs.push(r.on('ready', function (d) {
      if (!isOmni()) return;
      var micOn = r.isMicOn && r.isMicOn();
      resetLegacyFlags(micOn);
      setOmniCaption(avatarName() + ' is live on Gemini 3.8 Live' + (d && d.videoActive ? ' (video avatar)' : '') +
        (micOn ? ' — speak anytime, talk over to interrupt.' : ' — type a request below.'));
    }));
    subs.push(r.on('user_transcript', function (d) {
      if (!isOmni() || !d || !d.text) return;
      setOmniCaption('You: "' + d.text + (d.final ? '"' : '…"'));
    }));
    subs.push(r.on('avatar_transcript', function (d) {
      if (!isOmni() || !d || !d.text) return;
      setOmniCaption(avatarName() + ': ' + d.text);
    }));
    subs.push(r.on('interrupted', function (d) {
      var cursor = $('agent-cursor');
      if (cursor) cursor.classList.remove('visible', 'clicking');
      if (isOmni() && d && d.source === 'server') setOmniCaption('Interrupted — listening to you…');
    }));
    subs.push(r.on('error', function (d) {
      var msg = (d && d.message) || 'Live session error';
      try { console.warn(TAG, msg); } catch (e) {}
      if (!d || d.source === 'omni') setOmniCaption('Live voice: ' + msg);
    }));
    subs.push(r.on('mic', function () {
      if (isOmni()) { resetLegacyFlags(true); setOmniButton(r.getState()); }
    }));
    return true;
  }

  // ---------------------------------------------------------------- overrides
  var inSelectAvatar = false;
  var pendingGreeting = null;

  window.toggleUnifiedLiveVoiceMic = function () {
    var r = RL();
    if (!r) return callOrig('toggleUnifiedLiveVoiceMic', this, arguments);
    try {
      if (r.isActive() && r.getSource() === 'omni') {
        if (!r.isMicOn()) {
          disableLegacyRecognizer();
          r.enableMic();
          setOmniCaption('Mic on — speak anytime; talk over ' + avatarName() + ' to interrupt.');
          return;
        }
        r.stop();
        resetLegacyFlags(false);
        setOmniButton('idle');
        setOmniCaption('Live voice stopped. Click "Start Live Voice & Mic" or type a command.');
        return;
      }
      disableLegacyRecognizer();
      try { if (typeof LiveAudioEngine !== 'undefined' && LiveAudioEngine && LiveAudioEngine.isSpeakingOrQueued()) LiveAudioEngine.stopAll(); } catch (e) {}
      lastOmniCaption = '';
      var av = avatarName();
      setOmniCaption('Connecting ' + av + ' to Gemini 3.8 Live…');
      r.start({ avatar: av, voice: avatarVoice(), video: wantVideo(av), tools: true, mic: true, source: 'omni' });
    } catch (e) {
      try { console.warn(TAG, 'toggle failed', e); } catch (e2) {}
    }
  };

  window.ensureLiveAvatarWebSocket = function (initialTextToSend, expectedEpoch) {
    var r = RL();
    if (!r) return callOrig('ensureLiveAvatarWebSocket', this, arguments);
    if (!initialTextToSend) return; // legacy pre-warm calls: the live session connects on demand
    if (inSelectAvatar) { pendingGreeting = String(initialTextToSend); return; }
    try {
      disableLegacyRecognizer();
      var av = avatarName();
      r.sendText(String(initialTextToSend), { avatar: av, voice: avatarVoice(), video: wantVideo(av), tools: true, mic: false, source: 'omni' });
    } catch (e) {
      try { console.warn(TAG, 'sendText failed', e); } catch (e2) {}
    }
  };

  window.stopAllAudioAndAvatarNow = function () {
    var r = RL();
    try { if (r && r.isActive()) r.stop(); } catch (e) {}
    var out = callOrig('stopAllAudioAndAvatarNow', this, arguments);
    resetLegacyFlags(false);
    setOmniButton('idle');
    return out;
  };

  window.bargeInInterruptNow = function () {
    var r = RL();
    var active = Boolean(r && r.isActive());
    var out = callOrig('bargeInInterruptNow', this, arguments);
    if (active) {
      try { r.interrupt(); } catch (e) {}
      disableLegacyRecognizer();
      resetLegacyFlags(r.isMicOn && r.isMicOn());
      setPipStatus(r.getState());
      if (isOmni()) setOmniButton(r.getState());
    }
    return out;
  };

  window.selectAvatarProfile = function (avatarKey, voiceName, btnEl, triggerGreeting) {
    var r = RL();
    var wasActive = Boolean(r && r.isActive());
    var prevOpts = wasActive && r.getOptions ? r.getOptions() : null;
    inSelectAvatar = true;
    pendingGreeting = null;
    var out;
    try {
      out = callOrig('selectAvatarProfile', this, arguments);
    } finally {
      inSelectAvatar = false;
    }
    var greeting = pendingGreeting;
    pendingGreeting = null;
    if (!r) return out;
    try {
      var av = avatarName();
      var voice = avatarVoice();
      if (wasActive && prevOpts) {
        r.start({
          avatar: av, voice: voice, video: wantVideo(av), tools: prevOpts.tools, mic: prevOpts.mic,
          videoEl: prevOpts.videoEl || undefined, source: prevOpts.source
        });
        if (greeting) r.sendText(greeting);
      } else if (greeting) {
        r.sendText(greeting, { avatar: av, voice: voice, video: wantVideo(av), tools: true, mic: false, source: 'omni' });
      }
    } catch (e) {
      try { console.warn(TAG, 'avatar switch failed', e); } catch (e2) {}
    }
    return out;
  };

  window.toggleOfficialVideoAvatarMode = function (enabled) {
    var r = RL();
    var wasActive = Boolean(r && r.isActive());
    var prevOpts = wasActive && r.getOptions ? r.getOptions() : null;
    var out = callOrig('toggleOfficialVideoAvatarMode', this, arguments);
    if (wasActive && prevOpts) {
      try {
        var av = avatarName();
        r.start({ avatar: av, voice: avatarVoice(), video: wantVideo(av), tools: prevOpts.tools, mic: prevOpts.mic,
          videoEl: prevOpts.videoEl || undefined, source: prevOpts.source });
      } catch (e) {}
    }
    return out;
  };

  window.startBrowserSpeechRecognizer = function () {
    var r = RL();
    if (r && r.isActive()) { disableLegacyRecognizer(); return; }
    return callOrig('startBrowserSpeechRecognizer', this, arguments);
  };

  window.handleAvatarTapInterruptOrVoice = function () {
    var r = RL();
    if (r && r.isActive()) {
      var st = r.getState();
      if (st === 'speaking' || st === 'thinking') {
        r.interrupt();
        if (isOmni()) setOmniCaption('Interrupted ' + avatarName() + ' — go ahead.');
        return;
      }
      if (r.getSource() !== 'omni' || !r.isMicOn()) { window.toggleUnifiedLiveVoiceMic(); return; }
      return; // listening already: a tap should never kill the live mic
    }
    return callOrig('handleAvatarTapInterruptOrVoice', this, arguments);
  };

  // Paint the live 3.8 video avatar into the floating PiP and Omni dock canvases.
  window.drawVisemeTileWithJawSync = function (ctx, W, H, tileIdx, jawOpenNorm) {
    try {
      var r = RL();
      if (r && r.isActive() && r.isVideoMode() && ctx && ctx.canvas) {
        var id = ctx.canvas.id;
        if (id === 'kira-pip-canvas' || id === 'kira-dock-canvas') {
          var v = r.getVideoEl();
          if (v && v.videoWidth > 0 && v.readyState >= 2) {
            var vw = v.videoWidth, vh = v.videoHeight;
            var side = Math.min(vw, vh);
            var sx = Math.round((vw - side) * 0.5);
            var sy = Math.round((vh - side) * 0.34);
            ctx.globalAlpha = 1.0;
            ctx.drawImage(v, sx, sy, side, side, 0, 0, W, H);
            return;
          }
        }
      }
    } catch (e) {}
    return callOrig('drawVisemeTileWithJawSync', this, arguments);
  };

  // ---------------------------------------------------------------- init
  var bound = bindEvents();
  var bindTimer = null;
  if (!bound) {
    // live_session.js normally loads first; retry briefly in case of out-of-order loading.
    var tries = 0;
    bindTimer = setInterval(function () {
      tries++;
      if (bindEvents() || tries > 40) { clearInterval(bindTimer); bindTimer = null; }
    }, 250);
  }

  window.__rocketLiveBridge = {
    version: '2026.10.16-a',
    teardown: function () {
      subs.forEach(function (u) { try { u(); } catch (e) {} });
      subs = [];
      if (bindTimer) { clearInterval(bindTimer); bindTimer = null; }
      Object.keys(ORIG).forEach(function (n) { try { window[n] = ORIG[n]; } catch (e) {} });
    }
  };
})();
