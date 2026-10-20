/**
 * Compiled from `portal_liquid_glass.ts`
 * Apple iOS 26 / visionOS Liquid Glass + Black Mirror Spatial UI Controller
 */
(function () {
  'use strict';

  var AVATAR_ROSTER = {
    Kira: {
      key: 'Kira',
      name: 'Kira',
      role: 'Principal AI Portal Concierge',
      voice: 'Aoede',
      posterUrl: '/static/official_kira_38_full.jpg',
      hasOfficialVideo: true
    },
    Sam: {
      key: 'Sam',
      name: 'Sam',
      role: 'Cloud & GECX Solutions Architect',
      voice: 'Puck',
      posterUrl: '/static/official_sam_38_full.jpg',
      hasOfficialVideo: true
    },
    Ben: {
      key: 'Ben',
      name: 'Ben',
      role: 'BigQuery TimesFM & Vector Lead',
      voice: 'Fenrir',
      posterUrl: '/static/official_ben_38_full.jpg',
      hasOfficialVideo: true
    },
    Vera: {
      key: 'Vera',
      name: 'Vera',
      role: 'Redfin & Veo 3.1 Creative Director',
      voice: 'Kore',
      posterUrl: '/static/official_vera_38_full.jpg',
      hasOfficialVideo: true
    },
    Leo: {
      key: 'Leo',
      name: 'Leo',
      role: 'Mr. Cooper Servicing & Security Lead',
      voice: 'Charon',
      posterUrl: '/static/official_leo_38_full.jpg',
      hasOfficialVideo: true
    }
  };

  var VERSION_ORDER = ['v1', 'v2', 'v3', 'v4'];
  var VERSION_META = {
    v1: {
      id: 'v1',
      index: 1,
      shortLabel: 'UI: V1 · Prism',
      badge: 'V1 · CUPERTINO DAYLIGHT PRISM',
      title: 'Apple iOS 26 / visionOS Daylight Liquid Glass',
      subtitle: 'Explore the 5 Flagship Production Studios, Ricky Merrefield’s GECX Launchpad, the <3 Minute GitHub Replication Kit, and the synchronized Customer AI Glossary.'
    },
    v2: {
      id: 'v2',
      index: 2,
      shortLabel: 'UI: V2 · Black Mirror',
      badge: 'V2 · BLACK MIRROR OBSIDIAN NEURAL',
      title: 'Black Mirror Holographic Obsidian Glass',
      subtitle: 'Deep-space smoked quartz slabs, volumetric crimson/cyan caustics, and futuristic spatial telemetry.'
    },
    v3: {
      id: 'v3',
      index: 3,
      shortLabel: 'UI: V3 · Titanium 3D',
      badge: 'V3 · VISION PRO SPATIAL TITANIUM 3D',
      title: 'Apple Vision Pro Grade-5 Titanium Spatial Studio',
      subtitle: 'Interactive 3D perspective depth slabs, warm champagne rim lighting, and tactile squircle 3D glass icons.'
    },
    v4: {
      id: 'v4',
      index: 4,
      shortLabel: 'UI: V4 · Stillness',
      badge: 'V4 · RYAN HOLIDAY STILLNESS MONOLITH',
      title: 'Architectural Frosted Silica & Editorial Stillness',
      subtitle: 'Zero-noise warm stone & frosted glass monolith engineered for effortless executive comprehension.'
    }
  };

  var currentVersion = 'v1';
  var currentTab = 'studios';
  var currentAvatarKey = 'Kira';
  var activeVendorFilter = 'all';
  var activeArchiveDept = 'all';
  var ttsAudioCtx = null;
  var ttsActiveSource = null;
  var ttsActiveWs = null;
  var ttsActiveBtn = null;
  var ttsEpoch = 0;

  var INLINE_SVG = {
    swap: '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12a9 9 0 0 0-9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/><path d="M3 12a9 9 0 0 0 9 9 9.75 9.75 0 0 0 6.74-2.74L21 16"/><path d="M16 16h5v5"/></svg>',
    wave: '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 10v3"/><path d="M6 6v11"/><path d="M10 3v18"/><path d="M14 8v7"/><path d="M18 5v13"/><path d="M22 10v3"/></svg>',
    stop: '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="14" height="14" x="5" y="5" rx="2" fill="currentColor" fill-opacity="0.25"/></svg>',
    check: '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>'
  };

  function setLiquidVersion(ver) {
    if (!VERSION_META[ver]) ver = 'v1';
    currentVersion = ver;
    document.documentElement.setAttribute('data-liquid-version', ver);

    document.querySelectorAll('[data-ver-btn]').forEach(function (btn) {
      var isMatch = btn.getAttribute('data-ver-btn') === ver;
      btn.classList.toggle('active', isMatch);
      btn.setAttribute('aria-pressed', isMatch ? 'true' : 'false');
    });

    var meta = VERSION_META[ver];
    var badgeEl = document.getElementById('liquid-edition-badge');
    var subEl = document.getElementById('liquid-edition-subtitle');
    var activeLblEl = document.getElementById('ui-version-active-label');
    var cycleBtnEl = document.getElementById('ui-version-cycle-btn');
    if (badgeEl && meta) badgeEl.textContent = meta.badge;
    if (subEl && meta) subEl.textContent = meta.subtitle;
    if (activeLblEl && meta) activeLblEl.textContent = meta.shortLabel;
    if (cycleBtnEl && meta) {
      cycleBtnEl.innerHTML = INLINE_SVG.swap + '<span>Swap UI (' + meta.index + '/4)</span>';
    }
  }

  function cycleLiquidVersion() {
    var idx = VERSION_ORDER.indexOf(currentVersion);
    var nextVer = VERSION_ORDER[(idx + 1) % VERSION_ORDER.length] || 'v1';
    setLiquidVersion(nextVer);
    closeVersionPopover();
  }

  function toggleVersionPopover(ev) {
    if (ev && ev.stopPropagation) ev.stopPropagation();
    var pop = document.getElementById('ui-version-popover');
    if (pop) pop.classList.toggle('open');
  }

  function closeVersionPopover() {
    var pop = document.getElementById('ui-version-popover');
    if (pop) pop.classList.remove('open');
  }

  function switchPortalTab(tabId, highlightId) {
    var validTabs = ['studios', 'build', 'glossary', 'archive'];
    if (validTabs.indexOf(tabId) === -1) tabId = 'studios';
    currentTab = tabId;

    document.querySelectorAll('.portal-tab-pane').forEach(function (pane) {
      pane.classList.toggle('active', pane.id === 'tab-pane-' + tabId);
    });

    document.querySelectorAll('[data-tab-btn]').forEach(function (btn) {
      var isAct = btn.getAttribute('data-tab-btn') === tabId;
      btn.classList.toggle('active', isAct);
      btn.setAttribute('aria-selected', isAct ? 'true' : 'false');
    });

    if (highlightId) {
      setTimeout(function () {
        var target = document.getElementById(highlightId);
        if (target) {
          target.scrollIntoView({ behavior: 'smooth', block: 'center' });
          target.classList.add('liquid-pulse-highlight');
          setTimeout(function () {
            target.classList.remove('liquid-pulse-highlight');
          }, 2600);
        }
      }, 90);
    } else {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  }

  function selectPortalAvatar(key) {
    var prof = AVATAR_ROSTER[key] || AVATAR_ROSTER.Kira;
    currentAvatarKey = prof.key;

    document.querySelectorAll('[data-avatar-chip]').forEach(function (chip) {
      chip.classList.toggle('active', chip.getAttribute('data-avatar-chip') === prof.key);
    });

    var poster = document.getElementById('portal-avatar-poster');
    var orbImg = document.getElementById('portal-orb-avatar-img');
    var nameEl = document.getElementById('portal-avatar-name');
    var roleEl = document.getElementById('portal-avatar-role');
    var voiceBadge = document.getElementById('portal-avatar-voice-badge');

    if (poster) poster.src = prof.posterUrl;
    if (orbImg) orbImg.src = prof.posterUrl;
    if (nameEl) nameEl.textContent = prof.name;
    if (roleEl) roleEl.textContent = prof.role;
    if (voiceBadge) {
      voiceBadge.textContent = prof.hasOfficialVideo
        ? 'gemini-3.8-live · 24fps Video · ' + prof.voice
        : 'gemini-3.8-live · 24kHz Audio · ' + prof.voice;
    }

    if (window.RocketLive && window.RocketLive.isActive()) {
      startLiveSessionWithProfile(prof);
    }
  }

  function createFreshStageVideoEl() {
    var stage = document.getElementById('portal-avatar-stage-box');
    if (!stage) return null;
    var oldVid = document.getElementById('portal-avatar-live-video');
    if (oldVid && oldVid.parentNode) {
      oldVid.parentNode.removeChild(oldVid);
    }
    var vid = document.createElement('video');
    vid.id = 'portal-avatar-live-video';
    vid.className = 'portal-avatar-video';
    vid.playsInline = true;
    vid.autoplay = true;
    vid.controls = false;
    stage.appendChild(vid);
    return vid;
  }

  function startLiveSessionWithProfile(prof) {
    if (!window.RocketLive) {
      appendCopilotMessage('assistant', 'Live Avatar engine is initializing. Ask any question in the text box below!');
      return;
    }
    var vidEl = createFreshStageVideoEl();
    updateAvatarStatusUI('connecting', 'Connecting to Gemini 3.8 Live (' + prof.name + ')…');
    window.RocketLive.start({
      avatar: prof.key,
      voice: prof.voice,
      video: prof.hasOfficialVideo,
      tools: true,
      mic: true,
      videoEl: vidEl,
      source: 'p4'
    });
  }

  function togglePortalLiveAvatar() {
    var prof = AVATAR_ROSTER[currentAvatarKey] || AVATAR_ROSTER.Kira;
    if (window.RocketLive && window.RocketLive.isActive()) {
      stopAllPortalAudio();
      return;
    }
    stopTtsPlayback();
    if (typeof window.stopGlossaryAudio === 'function') {
      try { window.stopGlossaryAudio(); } catch (_) {}
    }
    startLiveSessionWithProfile(prof);
  }

  function stopAllPortalAudio() {
    if (fullTourTimer) {
      clearTimeout(fullTourTimer);
      fullTourTimer = null;
    }
    if (window.RocketLive) {
      try { window.RocketLive.interrupt(); } catch (_) {}
      try { window.RocketLive.stop(); } catch (_) {}
    }
    var vidEl = document.getElementById('portal-avatar-live-video');
    if (vidEl) {
      try {
        vidEl.pause();
        vidEl.muted = true;
        vidEl.removeAttribute('src');
        vidEl.srcObject = null;
        vidEl.classList.remove('is-streaming');
      } catch (_) {}
    }
    stopTtsPlayback();
    if (typeof window.stopGlossaryAudio === 'function') {
      try { window.stopGlossaryAudio(); } catch (_) {}
    }
    if (window.speechSynthesis && typeof window.speechSynthesis.cancel === 'function') {
      try { window.speechSynthesis.cancel(); } catch (_) {}
    }
    updateAvatarStatusUI('idle', 'Audio Stopped · Click "Start Live Video Avatar" or ask anything below');
  }

  function interruptPortalAvatar() {
    stopAllPortalAudio();
  }

  function updateAvatarStatusUI(state, labelText) {
    var stage = document.getElementById('portal-avatar-stage-box');
    var statusDot = document.getElementById('portal-avatar-status-dot');
    var statusTxt = document.getElementById('portal-avatar-status-text');
    var startBtnLbl = document.getElementById('portal-btn-live-label');
    var startBtn = document.getElementById('portal-btn-live-toggle');
    var vidEl = document.getElementById('portal-avatar-live-video');

    if (stage) {
      stage.setAttribute('data-live-state', state || 'idle');
    }
    if (statusDot) {
      statusDot.className = 'status-dot state-' + (state || 'idle');
    }
    if (statusTxt && labelText) {
      statusTxt.textContent = labelText;
    }
    var active = state && state !== 'idle';
    if (startBtnLbl) {
      startBtnLbl.textContent = active ? 'End Live Video Call' : 'Start Live Video Avatar';
    }
    if (startBtn) {
      startBtn.classList.toggle('is-live', !!active);
    }
    if (vidEl) {
      var hasFrames = vidEl.readyState >= 2 && vidEl.videoWidth > 0 && active;
      vidEl.classList.toggle('is-streaming', !!hasFrames);
    }
  }

  var activeWorkbenchDemoId = 'pillar-1';
  var fullTourTimer = null;
  var cursorHideTimer = null;

  function movePortalAgentCursorTo(selectorOrEl, labelText) {
    var cursor = document.getElementById('portal-agent-cursor');
    var lbl = document.getElementById('portal-agent-cursor-label');
    if (!cursor) return Promise.resolve();
    if (cursorHideTimer) {
      clearTimeout(cursorHideTimer);
      cursorHideTimer = null;
    }
    var target = typeof selectorOrEl === 'string'
      ? document.querySelector(selectorOrEl)
      : selectorOrEl;
    if (lbl && labelText) lbl.textContent = labelText;
    cursor.classList.add('visible');

    if (target && target.getBoundingClientRect) {
      var r = target.getBoundingClientRect();
      if (r.width > 0 && r.height > 0) {
        var cx = Math.max(24, Math.min(window.innerWidth - 400, r.left + Math.min(60, r.width * 0.25)));
        var cy = Math.max(96, Math.min(window.innerHeight - 60, r.top + r.height * 0.5));
        cursor.style.left = cx + 'px';
        cursor.style.top = cy + 'px';
      }
    }
    return new Promise(function (resolve) {
      setTimeout(resolve, 420);
    });
  }

  function hidePortalAgentCursorSoon(delayMs) {
    if (cursorHideTimer) clearTimeout(cursorHideTimer);
    cursorHideTimer = setTimeout(function () {
      var cursor = document.getElementById('portal-agent-cursor');
      if (cursor) cursor.classList.remove('visible');
    }, delayMs || 1600);
  }

  function switchWorkbenchMode(mode) {
    var execBody = document.getElementById('wb-exec-body');
    var iframeBody = document.getElementById('wb-iframe-body');
    var btnExec = document.getElementById('wb-mode-exec-btn');
    var btnIframe = document.getElementById('wb-mode-iframe-btn');
    var iframeEl = document.getElementById('wb-studio-iframe');
    var stepsEl = document.getElementById('wb-steps-container');

    if (mode === 'iframe') {
      if (execBody) execBody.style.display = 'none';
      if (stepsEl) stepsEl.style.display = 'none';
      if (iframeBody) iframeBody.style.display = 'block';
      if (btnExec) { btnExec.className = 'lg-btn lg-btn-glass sm'; }
      if (btnIframe) { btnIframe.className = 'lg-btn lg-btn-primary sm'; }
      if (iframeEl) {
        var pNum = (activeWorkbenchDemoId || 'pillar-1').replace('pillar-', '') || '1';
        var targetUrl = 'https://rocket-polymorphic-search-254356041555.us-central1.run.app/?auth_token=rocket:e3a48aa96ebeb0731e4c751d&pillar=' + encodeURIComponent(pNum);
        if (activeWorkbenchDemoId === 'gecx') {
          targetUrl = 'https://rocket-cxas-launchpad-721536271629.us-central1.run.app/';
        } else if (activeWorkbenchDemoId === 'superwow') {
          targetUrl = 'https://rocket-monday-superwow-254356041555.us-central1.run.app/?auth_token=rocket:e3a48aa96ebeb0731e4c751d';
        }
        if (iframeEl.src !== targetUrl) iframeEl.src = targetUrl;
      }
    } else {
      if (execBody) execBody.style.display = 'block';
      if (stepsEl) stepsEl.style.display = 'grid';
      if (iframeBody) iframeBody.style.display = 'none';
      if (btnExec) { btnExec.className = 'lg-btn lg-btn-primary sm'; }
      if (btnIframe) { btnIframe.className = 'lg-btn lg-btn-glass sm'; }
    }
  }

  function closeAutonomousWorkbench() {
    if (fullTourTimer) {
      clearTimeout(fullTourTimer);
      fullTourTimer = null;
    }
    var wb = document.getElementById('portal-autonomous-workbench');
    if (wb) wb.classList.remove('open');
    hidePortalAgentCursorSoon(100);
  }

  function buildTimesFmSvgChart(hist, fcast, upper, lower) {
    var allVals = (hist || []).concat(upper || []).concat(lower || []);
    var minV = Math.min.apply(null, allVals.length ? allVals : [0]) * 0.94;
    var maxV = Math.max.apply(null, allVals.length ? allVals : [100]) * 1.04;
    var W = 680, H = 210, padL = 48, padR = 18, padT = 18, padB = 28;
    var plotW = W - padL - padR;
    var plotH = H - padT - padB;
    var totalPts = (hist.length || 8) + (fcast.length || 12);

    function xAt(idx) {
      return (padL + (idx / Math.max(1, totalPts - 1)) * plotW).toFixed(1);
    }
    function yAt(v) {
      var ratio = (v - minV) / Math.max(1, maxV - minV);
      return (padT + plotH - ratio * plotH).toFixed(1);
    }

    var histPts = hist.map(function (v, i) { return xAt(i) + ',' + yAt(v); }).join(' ');
    var startIdx = Math.max(0, hist.length - 1);
    var lastHist = hist[startIdx] || fcast[0] || 0;

    var fcastPts = [xAt(startIdx) + ',' + yAt(lastHist)];
    var upperPts = [xAt(startIdx) + ',' + yAt(lastHist)];
    var lowerPts = [xAt(startIdx) + ',' + yAt(lastHist)];

    fcast.forEach(function (v, j) {
      var xi = startIdx + 1 + j;
      fcastPts.push(xAt(xi) + ',' + yAt(v));
      upperPts.push(xAt(xi) + ',' + yAt(upper[j] || v));
      lowerPts.unshift(xAt(xi) + ',' + yAt(lower[j] || v));
    });

    var polyBand = upperPts.concat(lowerPts).join(' ');
    var dividerX = xAt(startIdx);

    return (
      '<svg viewBox="0 0 ' + W + ' ' + H + '" style="width:100%;height:auto;background:var(--glass-surface-strong);border:1px solid var(--glass-outer-stroke);border-radius:14px;padding:8px;">' +
      '<line x1="' + dividerX + '" y1="' + padT + '" x2="' + dividerX + '" y2="' + (H - padB) + '" stroke="#94A3B8" stroke-dasharray="4 4" stroke-width="1.5"/>' +
      '<polygon points="' + polyBand + '" fill="rgba(216, 30, 40, 0.15)" />' +
      '<polyline fill="none" stroke="#0066CC" stroke-width="3" points="' + histPts + '" />' +
      '<polyline fill="none" stroke="#D81E28" stroke-width="3" points="' + fcastPts.join(' ') + '" />' +
      '<text x="' + (padL + 6) + '" y="' + (padT + 14) + '" fill="#0066CC" font-size="11" font-weight="700" font-family="JetBrains Mono, monospace">Historical (8 Wks)</text>' +
      '<text x="' + (parseFloat(dividerX) + 10) + '" y="' + (padT + 14) + '" fill="#D81E28" font-size="11" font-weight="700" font-family="JetBrains Mono, monospace">TimesFM 2.0 Forecast (12 Wks · 90% CI Band)</text>' +
      '</svg>'
    );
  }

  function renderWorkbenchExecution(data) {
    if (!data) return;
    var badgeEl = document.getElementById('wb-active-badge');
    var titleEl = document.getElementById('wb-active-title');
    var stepsEl = document.getElementById('wb-steps-container');
    var bodyEl = document.getElementById('wb-exec-body');
    var openLink = document.getElementById('wb-open-tab-link');

    var did = data.demo_id || 'pillar-1';
    activeWorkbenchDemoId = did === 'full-tour' ? 'pillar-1' : did;

    if (badgeEl) badgeEl.textContent = data.badge || 'LIVE AUTONOMOUS STUDIO EXECUTION';
    if (titleEl) titleEl.textContent = data.title || 'Live Autonomous Studio';
    if (openLink) {
      var pNum = activeWorkbenchDemoId.replace('pillar-', '') || '1';
      openLink.href = 'https://rocket-polymorphic-search-254356041555.us-central1.run.app/?auth_token=rocket:e3a48aa96ebeb0731e4c751d&pillar=' + encodeURIComponent(pNum);
    }

    if (stepsEl && Array.isArray(data.steps)) {
      stepsEl.innerHTML = data.steps.map(function (st, idx) {
        return (
          '<div id="wb-step-box-' + idx + '" class="wb-step-card">' +
          '<div class="mono" style="font-size:10px;font-weight:800;color:var(--accent-primary);">STEP ' + (idx + 1) + ' OF ' + data.steps.length + '</div>' +
          '<div>' + escapeHtml(st) + '</div>' +
          '</div>'
        );
      }).join('');
    }

    if (!bodyEl) return;

    if (did === 'pillar-1') {
      var kpis = data.kpis || {};
      var chartSvg = buildTimesFmSvgChart(data.historical || [], data.forecast || [], data.upper_ci || [], data.lower_ci || []);
      bodyEl.innerHTML = (
        '<div style="display:flex;flex-direction:column;gap:14px;">' +
        '<div class="wb-controls-bar">' +
          '<span class="mono" style="font-size:11px;font-weight:700;">COHORT:</span>' +
          '<button type="button" id="wb-p1-c1" class="quick-ask-chip ' + (data.cohort_id === 'mr_cooper_refi' ? 'active' : '') + '" onclick="runAutonomousStudioDemo(\'pillar-1\', \'mr_cooper_refi\', ' + (data.rate_shock_bps || -100) + ', false)">Mr. Cooper $2.1T Refi Locks</button>' +
          '<button type="button" id="wb-p1-c2" class="quick-ask-chip ' + (data.cohort_id === 'redfin_velocity' ? 'active' : '') + '" onclick="runAutonomousStudioDemo(\'pillar-1\', \'redfin_velocity\', ' + (data.rate_shock_bps || -100) + ', false)">Redfin Buyer Tour Velocity</button>' +
          '<button type="button" id="wb-p1-c3" class="quick-ask-chip ' + (data.cohort_id === 'escrow_outflow' ? 'active' : '') + '" onclick="runAutonomousStudioDemo(\'pillar-1\', \'escrow_outflow\', ' + (data.rate_shock_bps || -100) + ', false)">Mr. Cooper Escrow Outflow</button>' +
          '<span class="mono" style="font-size:11px;font-weight:700;margin-left:auto;">FED RATE SHOCK: <strong id="wb-p1-shock-lbl" style="color:var(--accent-primary);">' + (data.rate_shock_bps || -100) + ' bps</strong></span>' +
          '<input id="wb-p1-shock-slider" type="range" min="-150" max="100" step="25" value="' + (data.rate_shock_bps || -100) + '" style="width:140px;accent-color:var(--accent-primary);" onchange="runAutonomousStudioDemo(\'pillar-1\', \'' + (data.cohort_id || 'mr_cooper_refi') + '\', parseInt(this.value,10), false)">' +
        '</div>' +
        '<div class="wb-kpi-grid">' +
          '<div class="wb-kpi-box"><div class="wb-kpi-lbl">Current Weekly Baseline</div><div class="wb-kpi-val mono">' + escapeHtml(kpis.baseline || '22,545') + '</div></div>' +
          '<div class="wb-kpi-box"><div class="wb-kpi-lbl">TimesFM 2.0 Peak Forecast</div><div class="wb-kpi-val mono" style="color:var(--accent-primary);">' + escapeHtml(kpis.peak || '34,178') + ' <span style="font-size:13px;">(' + escapeHtml(kpis.delta_pct || '+51.6%') + ')</span></div></div>' +
          '<div class="wb-kpi-box"><div class="wb-kpi-lbl">12-Week Cumulative Volume</div><div class="wb-kpi-val mono">' + escapeHtml(kpis.cumulative || '368,420') + '</div></div>' +
          '<div class="wb-kpi-box"><div class="wb-kpi-lbl">Projected Rocket Impact</div><div class="wb-kpi-val mono" style="color:var(--accent-tertiary);">' + escapeHtml(kpis.revenue_impact || '$980.1M') + '</div></div>' +
        '</div>' +
        '<div style="display:grid;grid-template-columns:1.45fr 1fr;gap:14px;align-items:stretch;">' +
          '<div id="wb-p1-chart-box">' + chartSvg + '</div>' +
          '<div class="code-terminal" style="margin:0;display:flex;flex-direction:column;justify-content:space-between;">' +
            '<div class="mono" style="font-size:10.5px;color:#38BDF8;font-weight:700;margin-bottom:6px;">LIVE BIGQUERY ML STANDARD SQL (TimesFM 2.0)</div>' +
            '<pre style="white-space:pre-wrap;font-size:11.5px;margin:0;">' + escapeHtml(data.sql || '') + '</pre>' +
          '</div>' +
        '</div>' +
        '</div>'
      );
    } else if (did === 'pillar-2') {
      var scenesHtml = (data.scenes || []).map(function (sc) {
        return '<div class="wb-step-card done" style="font-size:12px;">' + escapeHtml(sc) + '</div>';
      }).join('');
      bodyEl.innerHTML = (
        '<div style="display:flex;flex-direction:column;gap:14px;">' +
        '<div class="wb-controls-bar">' +
          '<span class="mono" style="font-size:11px;font-weight:700;">SELECT LISTING REEL:</span>' +
          '<button type="button" class="quick-ask-chip" onclick="runAutonomousStudioDemo(\'pillar-2\', \'royal_oak\', -100, false)">418 Elmhurst · Royal Oak ($460K)</button>' +
          '<button type="button" class="quick-ask-chip" onclick="runAutonomousStudioDemo(\'pillar-2\', \'corktown_loft\', -100, false)">1420 Michigan Ave · Corktown ($385K)</button>' +
          '<button type="button" class="quick-ask-chip" onclick="runAutonomousStudioDemo(\'pillar-2\', \'ann_arbor\', -100, false)">2105 Devonshire · Ann Arbor ($695K)</button>' +
          '<button type="button" class="quick-ask-chip" onclick="runAutonomousStudioDemo(\'pillar-2\', \'scottsdale\', -100, false)">Camelback Adobe · Scottsdale ($1.22M)</button>' +
        '</div>' +
        '<div style="display:grid;grid-template-columns:280px 1fr;gap:18px;align-items:start;">' +
          '<div style="position:relative;border-radius:18px;overflow:hidden;background:#0B0F19;border:2px solid var(--glass-outer-stroke);aspect-ratio:9/16;max-height:420px;margin:0 auto;width:100%;">' +
            '<video id="wb-p2-video" src="' + escapeHtml(data.video_url || '') + '" autoplay muted loop playsinline controls style="width:100%;height:100%;object-fit:cover;"></video>' +
            '<div style="position:absolute;bottom:42px;left:10px;right:10px;background:rgba(11,15,25,0.84);backdrop-filter:blur(10px);padding:8px 10px;border-radius:10px;color:#FFF;font-size:11px;pointer-events:none;">' +
              '<div style="font-weight:800;color:#34D399;">' + escapeHtml(data.piti || '$2,685/mo') + ' All-In PITI</div>' +
              '<div style="font-size:10px;color:#E2E8F0;">' + escapeHtml(data.credit || '') + '</div>' +
            '</div>' +
          '</div>' +
          '<div style="display:flex;flex-direction:column;gap:12px;">' +
            '<div class="wb-kpi-grid" style="grid-template-columns:repeat(3,1fr);">' +
              '<div class="wb-kpi-box"><div class="wb-kpi-lbl">Listing Price</div><div class="wb-kpi-val mono">$' + Number(data.price || 460000).toLocaleString() + '</div></div>' +
              '<div class="wb-kpi-box"><div class="wb-kpi-lbl">Verified Monthly PITI</div><div class="wb-kpi-val mono" style="color:var(--accent-primary);">' + escapeHtml(data.piti || '$2,685/mo') + '</div></div>' +
              '<div class="wb-kpi-box"><div class="wb-kpi-lbl">Closing Credit / Grant</div><div class="wb-kpi-val mono" style="font-size:14px;color:var(--accent-tertiary);">' + escapeHtml(data.credit || '') + '</div></div>' +
            '</div>' +
            '<div class="mono" style="font-size:11px;font-weight:800;color:var(--text-muted);">4-SCENE GEMINI 3.8 FLASH + VEO 3.1 CINEMATOGRAPHY BEAT SHEET:</div>' +
            '<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;">' + scenesHtml + '</div>' +
          '</div>' +
        '</div>' +
        '</div>'
      );
    } else if (did === 'pillar-3') {
      var placesHtml = (data.places || []).map(function (pl) {
        return (
          '<div class="wb-kpi-box" style="padding:10px 12px;">' +
            '<div class="mono" style="font-size:10px;color:var(--accent-secondary);font-weight:700;">' + escapeHtml(pl.type || 'Place') + ' · ' + escapeHtml(pl.rating || '') + '</div>' +
            '<div style="font-size:13px;font-weight:800;margin-top:2px;">' + escapeHtml(pl.name || '') + '</div>' +
            '<div class="mono" style="font-size:11px;color:var(--text-muted);margin-top:2px;">' + escapeHtml(pl.dist || '') + '</div>' +
          '</div>'
        );
      }).join('');
      bodyEl.innerHTML = (
        '<div style="display:flex;flex-direction:column;gap:14px;">' +
        '<div class="wb-controls-bar">' +
          '<span class="mono" style="font-size:11px;font-weight:700;">GROUNDING HUB:</span>' +
          '<button type="button" class="quick-ask-chip" onclick="runAutonomousStudioDemo(\'pillar-3\', \'royal_oak\', -100, false)">418 Elmhurst · Royal Oak ($460K)</button>' +
          '<button type="button" class="quick-ask-chip" onclick="runAutonomousStudioDemo(\'pillar-3\', \'corktown_detroit\', -100, false)">1420 Michigan Ave · Corktown ($385K)</button>' +
          '<button type="button" class="quick-ask-chip" onclick="runAutonomousStudioDemo(\'pillar-3\', \'ann_arbor\', -100, false)">2105 Devonshire · Ann Arbor ($695K)</button>' +
        '</div>' +
        '<div class="wb-kpi-box" style="border-left:4px solid var(--accent-secondary);">' +
          '<div class="mono" style="font-size:11px;font-weight:800;color:var(--accent-secondary);">TRI-MODAL GROUNDED SYNTHESIS (' + escapeHtml(data.address || '') + ')</div>' +
          '<p style="font-size:13.5px;line-height:1.55;margin-top:6px;color:var(--text-primary);">' + escapeHtml(data.answer || '') + '</p>' +
          '<div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:10px;">' +
            '<span class="lg-badge lg-badge-emerald">' + escapeHtml(data.grant_badge || '') + '</span>' +
            '<span class="lg-badge lg-badge-cobalt">YouTube Video Inspection: ' + escapeHtml(data.youtube_inspection || '') + '</span>' +
          '</div>' +
        '</div>' +
        '<div class="wb-kpi-grid">' + placesHtml + '</div>' +
        '</div>'
      );
    } else if (did === 'pillar-4') {
      var avCards = (data.avatars || []).map(function (av) {
        return (
          '<div class="wb-kpi-box" style="display:flex;flex-direction:column;align-items:center;text-align:center;gap:6px;cursor:pointer;" onclick="selectPortalAvatar(\'' + escapeHtml(av.key) + '\')">' +
            '<img src="' + escapeHtml(av.img) + '" alt="' + escapeHtml(av.key) + '" style="width:68px;height:68px;border-radius:50%;object-fit:cover;border:2px solid var(--accent-primary);">' +
            '<div style="font-size:13.5px;font-weight:800;">' + escapeHtml(av.key) + '</div>' +
            '<div class="mono" style="font-size:10.5px;color:var(--accent-secondary);">Voice: ' + escapeHtml(av.voice) + ' · 24fps H.264</div>' +
            '<div style="font-size:11px;color:var(--text-secondary);">' + escapeHtml(av.role) + '</div>' +
          '</div>'
        );
      }).join('');
      bodyEl.innerHTML = (
        '<div style="display:flex;flex-direction:column;gap:14px;">' +
          '<div class="wb-kpi-grid" style="grid-template-columns:repeat(5,1fr);">' + avCards + '</div>' +
        '</div>'
      );
    } else {
      var matchCards = (data.matches || []).map(function (m) {
        return (
          '<div class="wb-kpi-box" style="display:flex;flex-direction:column;gap:8px;">' +
            '<img src="' + escapeHtml(m.img) + '" alt="' + escapeHtml(m.title) + '" style="width:100%;height:130px;object-fit:cover;border-radius:10px;">' +
            '<div style="display:flex;justify-content:space-between;gap:4px;flex-wrap:wrap;">' +
              '<span class="lg-badge lg-badge-crimson">' + escapeHtml(m.cosine) + '</span>' +
              '<span class="lg-badge lg-badge-emerald">' + escapeHtml(m.judge_score) + '</span>' +
            '</div>' +
            '<div style="font-size:14px;font-weight:800;">' + escapeHtml(m.title) + '</div>' +
            '<div class="mono" style="font-size:12px;color:var(--accent-primary);font-weight:700;">' + escapeHtml(m.price) + ' · ' + escapeHtml(m.piti) + '</div>' +
            '<div style="font-size:11.5px;color:var(--text-secondary);">' + escapeHtml(m.city) + ' · ' + escapeHtml(m.specs) + '</div>' +
          '</div>'
        );
      }).join('');
      bodyEl.innerHTML = (
        '<div style="display:flex;flex-direction:column;gap:14px;">' +
          '<div style="display:grid;grid-template-columns:1.25fr 1fr;gap:16px;align-items:start;">' +
            '<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:10px;">' + matchCards + '</div>' +
            '<div class="wb-kpi-box" style="display:flex;flex-direction:column;gap:8px;">' +
              '<div class="mono" style="font-size:11px;font-weight:800;color:var(--accent-primary);">16:9 VEO 3.1 AI WALKTHROUGH VIDEO TOUR (RKT-098)</div>' +
              '<video src="' + escapeHtml(data.featured_tour_url || '') + '" autoplay muted loop playsinline controls style="width:100%;border-radius:10px;background:#000;"></video>' +
              '<div style="font-size:11.5px;color:var(--text-secondary);">' + escapeHtml(data.judge_summary || '') + '</div>' +
            '</div>' +
          '</div>' +
        '</div>'
      );
    }
  }

  async function runAutonomousStudioDemo(demoId, scenarioQuery, rateShockBps, withVoiceReadout) {
    if (fullTourTimer) {
      clearTimeout(fullTourTimer);
      fullTourTimer = null;
    }
    var targetCardId = demoId === 'full-tour' ? 'pillar-1' : (demoId || 'pillar-1');
    switchPortalTab('studios', 'card-' + targetCardId);
    await movePortalAgentCursorTo('#card-' + targetCardId, 'Kira Agent · Highlighting ' + targetCardId.toUpperCase() + ' Studio…');
    hidePortalAgentCursorSoon(1200);
    return { status: 'completed', demo_id: targetCardId };
  }

  function executePortalScreenAction(action) {
    if (!action || !action.name) return { status: 'no_action' };
    var args = action.args || {};
    if (action.name === 'run_live_studio_demo') {
      var did = args.demo_id || 'pillar-1';
      switchPortalTab('studios', 'card-' + did);
      return { status: 'highlighted_studio_card', demo_id: did };
    }
    if (action.name === 'navigate_portal_tab') {
      switchPortalTab(args.tab_id || 'studios', args.highlight_id || '');
      return { status: 'navigated', tab_id: args.tab_id, highlight_id: args.highlight_id || '' };
    }
    if (action.name === 'search_glossary_or_translator') {
      switchPortalTab('glossary');
      var glInput = document.getElementById('gl-search-input');
      if (glInput) {
        glInput.value = args.query || '';
      }
      if (typeof window.searchGlossaryConcepts === 'function') {
        window.searchGlossaryConcepts();
      } else {
        filterGlossaryView(args.query || '', 'all');
      }
      return { status: 'filtered_glossary', query: args.query || '' };
    }
    if (action.name === 'filter_reference_library') {
      switchPortalTab('archive');
      filterArchiveBlueprints(args.department_or_query || 'all');
      return { status: 'filtered_archive', filter: args.department_or_query || 'all' };
    }
    return { status: 'completed' };
  }

  // Expose legacy tool hook called by `live_session.js` when Gemini 3.8 Live invokes a tool
  window.executeAgentScreenTool = async function (name, args) {
    if (name === 'run_live_studio_demo') {
      var did = (args && args.demo_id) || 'pillar-1';
      var sq = (args && args.scenario_query) || '';
      var shock = (args && typeof args.rate_shock_bps === 'number') ? args.rate_shock_bps : -100;
      var execRes = await runAutonomousStudioDemo(did, sq, shock, false);
      return execRes || { status: 'executed', demo_id: did };
    }
    return executePortalScreenAction({ name: name, args: args || {} });
  };

  function appendCopilotMessage(role, text, metaBadge) {
    var feed = document.getElementById('portal-copilot-feed');
    if (!feed) return;
    var msg = document.createElement('div');
    msg.className = 'copilot-msg copilot-msg-' + role;

    var header = document.createElement('div');
    header.className = 'copilot-msg-hdr';
    var who = role === 'user' ? 'You' : (AVATAR_ROSTER[currentAvatarKey]?.name || 'Kira') + ' · Portal AI Concierge';
    header.innerHTML = '<span>' + escapeHtml(who) + '</span>' +
      (metaBadge ? '<span class="copilot-meta-pill">' + escapeHtml(metaBadge) + '</span>' : '');

    var body = document.createElement('div');
    body.className = 'copilot-msg-body';
    body.textContent = text;

    msg.appendChild(header);
    msg.appendChild(body);

    if (role === 'assistant') {
      var actions = document.createElement('div');
      actions.className = 'copilot-msg-actions';
      var listenBtn = document.createElement('button');
      listenBtn.type = 'button';
      listenBtn.className = 'copilot-action-btn';
      listenBtn.innerHTML = INLINE_SVG.wave + ' <span>Hear 24kHz Voice</span>';
      listenBtn.onclick = function () {
        speakPortalText(text, listenBtn);
      };
      actions.appendChild(listenBtn);
      msg.appendChild(actions);
    }

    feed.appendChild(msg);
    feed.scrollTop = feed.scrollHeight;
  }

  async function askPortalCopilot(presetQuestion) {
    var input = document.getElementById('portal-copilot-input');
    var q = (typeof presetQuestion === 'string' && presetQuestion.trim())
      ? presetQuestion.trim()
      : (input ? input.value.trim() : '');
    if (!q) return;
    if (input && !presetQuestion) input.value = '';

    appendCopilotMessage('user', q);

    // If Live Video Avatar session is active, also send into the live stream so the video avatar speaks it!
    if (window.RocketLive && window.RocketLive.isActive()) {
      window.RocketLive.sendText(q);
    }

    var loader = document.getElementById('portal-copilot-loader');
    if (loader) loader.style.display = 'inline-flex';

    try {
      var token = window.PORTAL_AUTH_TOKEN || '';
      var resp = await fetch('/api/portal-copilot?auth_token=' + encodeURIComponent(token), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: q, avatar: currentAvatarKey })
      });
      var data = await resp.json();
      if (loader) loader.style.display = 'none';
      if (data && data.answer) {
        var badge = (data.model || 'gemini-3.8-flash') + ' · ' + Math.round(data.latency_ms || 0) + 'ms';
        if (data.screen_action && data.screen_action.name) {
          executePortalScreenAction(data.screen_action);
          badge += ' · Screen Synced';
        }
        appendCopilotMessage('assistant', data.answer, badge);
      }
    } catch (err) {
      if (loader) loader.style.display = 'none';
      appendCopilotMessage('assistant', 'Navigated portal view. Use the 4 top tabs to inspect any studio, GitHub guide, or glossary item.');
    }
  }

  function stopTtsPlayback() {
    ttsEpoch += 1;
    if (ttsActiveWs) {
      try {
        ttsActiveWs.onopen = null;
        ttsActiveWs.onmessage = null;
        ttsActiveWs.onerror = null;
        ttsActiveWs.onclose = null;
        ttsActiveWs.close();
      } catch (_) {}
      ttsActiveWs = null;
    }
    if (ttsActiveSource) {
      try {
        ttsActiveSource.onended = null;
        ttsActiveSource.stop(0);
        ttsActiveSource.disconnect();
      } catch (_) {}
      ttsActiveSource = null;
    }
    if (ttsAudioCtx) {
      try { ttsAudioCtx.close(); } catch (_) {}
      ttsAudioCtx = null;
    }
    if (ttsActiveBtn) {
      if (ttsActiveBtn.dataset && ttsActiveBtn.dataset.origHtml) {
        ttsActiveBtn.innerHTML = ttsActiveBtn.dataset.origHtml;
      }
      ttsActiveBtn.classList.remove('is-speaking');
      ttsActiveBtn = null;
    }
  }

  function speakPortalText(text, btnEl) {
    if (!text) return;
    // Toggle off if clicking the same button while playing
    if (btnEl && ttsActiveBtn === btnEl && (ttsActiveWs || ttsActiveSource)) {
      stopTtsPlayback();
      return;
    }
    stopTtsPlayback();
    if (typeof window.stopGlossaryAudio === 'function') {
      try { window.stopGlossaryAudio(); } catch (_) {}
    }

    var myEpoch = ++ttsEpoch;
    var prof = AVATAR_ROSTER[currentAvatarKey] || AVATAR_ROSTER.Kira;
    var proto = location.protocol === 'https:' ? 'wss:' : 'ws:';
    var token = window.PORTAL_AUTH_TOKEN || '';
    var wsUrl = proto + '//' + location.host + '/ws/live-tts?auth_token=' + encodeURIComponent(token);

    if (btnEl) {
      if (!btnEl.dataset.origHtml) {
        btnEl.dataset.origHtml = btnEl.innerHTML;
      }
      ttsActiveBtn = btnEl;
      btnEl.classList.add('is-speaking');
      btnEl.innerHTML = INLINE_SVG.stop + ' <span>Stop 24kHz Audio</span>';
    }

    try {
      var AC = window.AudioContext || window.webkitAudioContext;
      ttsAudioCtx = new AC({ sampleRate: 24000 });
      if (ttsAudioCtx.state === 'suspended') ttsAudioCtx.resume();
    } catch (_) {}

    var chunks = [];
    var ws = new WebSocket(wsUrl);
    ttsActiveWs = ws;
    ws.onopen = function () {
      if (myEpoch !== ttsEpoch) {
        try { ws.close(); } catch (_) {}
        return;
      }
      ws.send(JSON.stringify({ text: text, voice: prof.voice }));
    };
    ws.onmessage = function (ev) {
      if (myEpoch !== ttsEpoch) return;
      try {
        var msg = JSON.parse(ev.data);
        if (msg.pcm_b64) {
          var bin = atob(msg.pcm_b64);
          var bytes = new Uint8Array(bin.length);
          for (var i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
          chunks.push(bytes);
        }
        if (msg.done) {
          ttsActiveWs = null;
          if (chunks.length > 0 && ttsAudioCtx && myEpoch === ttsEpoch) {
            var totalLen = chunks.reduce(function (acc, c) { return acc + c.length; }, 0);
            var merged = new Uint8Array(totalLen);
            var off = 0;
            chunks.forEach(function (c) { merged.set(c, off); off += c.length; });
            var samples = Math.floor(merged.byteLength / 2);
            var f32 = new Float32Array(samples);
            var dv = new DataView(merged.buffer);
            for (var j = 0; j < samples; j++) {
              f32[j] = dv.getInt16(j * 2, true) / 32768.0;
            }
            var buf = ttsAudioCtx.createBuffer(1, samples, 24000);
            buf.getChannelData(0).set(f32);
            var src = ttsAudioCtx.createBufferSource();
            src.buffer = buf;
            src.connect(ttsAudioCtx.destination);
            ttsActiveSource = src;
            src.onended = function () {
              if (myEpoch === ttsEpoch) {
                stopTtsPlayback();
              }
            };
            src.start(0);
          } else if (myEpoch === ttsEpoch) {
            stopTtsPlayback();
          }
        }
      } catch (_) {}
    };
    ws.onerror = function () {
      if (myEpoch === ttsEpoch) {
        stopTtsPlayback();
      }
    };
  }

  function filterGlossaryView(query, vendorTag) {
    var searchInput = document.getElementById('glossary-search-input');
    if (typeof query === 'string' && searchInput && searchInput.value !== query) {
      searchInput.value = query;
    }
    var q = (searchInput ? searchInput.value : (query || '')).trim().toLowerCase();
    if (vendorTag) activeVendorFilter = vendorTag;

    document.querySelectorAll('[data-vendor-pill]').forEach(function (pill) {
      pill.classList.toggle('active', pill.getAttribute('data-vendor-pill') === activeVendorFilter);
    });

    document.querySelectorAll('.glossary-filter-item').forEach(function (item) {
      var text = (item.textContent || '').toLowerCase();
      var tags = (item.getAttribute('data-tags') || 'all').toLowerCase();
      var matchesText = !q || text.indexOf(q) !== -1;
      var matchesVendor = activeVendorFilter === 'all' || tags.indexOf(activeVendorFilter) !== -1;
      item.style.display = (matchesText && matchesVendor) ? '' : 'none';
    });
  }

  function filterArchiveBlueprints(deptOrQuery) {
    var searchInput = document.getElementById('archive-search-input');
    var validDepts = ['all', 'sales', 'ops', 'servicing', 'marketing', 'risk', 'sdlc', 'moonshots'];

    if (deptOrQuery && validDepts.indexOf(deptOrQuery) !== -1) {
      activeArchiveDept = deptOrQuery;
    } else if (typeof deptOrQuery === 'string' && searchInput) {
      activeArchiveDept = 'all';
      searchInput.value = deptOrQuery;
    }

    document.querySelectorAll('[data-archive-dept]').forEach(function (btn) {
      btn.classList.toggle('active', btn.getAttribute('data-archive-dept') === activeArchiveDept);
    });

    var q = (searchInput ? searchInput.value : '').trim().toLowerCase();
    var visibleCount = 0;
    document.querySelectorAll('.archive-blueprint-card').forEach(function (card) {
      var dept = card.getAttribute('data-dept') || '';
      var text = (card.textContent || '').toLowerCase();
      var matchDept = activeArchiveDept === 'all' || dept === activeArchiveDept;
      var matchText = !q || text.indexOf(q) !== -1;
      var show = matchDept && matchText;
      card.style.display = show ? '' : 'none';
      if (show) visibleCount++;
    });

    var countBadge = document.getElementById('archive-visible-count');
    if (countBadge) countBadge.textContent = visibleCount + ' Blueprints Shown';
  }

  var activeLightboxState = {
    archSrc: '',
    walkSrc: '',
    baseTitle: '',
    githubUrl: ''
  };

  function openDiagramLightbox(archSrc, title, walkSrc, githubUrl, initialMode) {
    var modal = document.getElementById('portal-diagram-lightbox');
    var img = document.getElementById('portal-lightbox-img');
    var ttl = document.getElementById('portal-lightbox-title');
    var pillsWrap = document.getElementById('portal-lightbox-mode-pills');
    var ghLink = document.getElementById('lightbox-github-link');
    if (!modal || !img) return;

    activeLightboxState.archSrc = archSrc || '';
    activeLightboxState.walkSrc = walkSrc || '';
    activeLightboxState.baseTitle = title || 'Architecture Blueprint';
    activeLightboxState.githubUrl = githubUrl || '';

    if (pillsWrap) {
      pillsWrap.style.display = walkSrc ? 'inline-flex' : 'none';
    }
    if (ghLink) {
      if (githubUrl) {
        ghLink.href = githubUrl;
        ghLink.style.display = 'inline-flex';
      } else {
        ghLink.style.display = 'none';
      }
    }

    var mode = initialMode === 'walk' && walkSrc ? 'walk' : 'arch';
    switchLightboxView(mode);
    modal.classList.add('open');
  }

  function switchLightboxView(mode) {
    var img = document.getElementById('portal-lightbox-img');
    var ttl = document.getElementById('portal-lightbox-title');
    var btnArch = document.getElementById('lightbox-btn-arch');
    var btnWalk = document.getElementById('lightbox-btn-walk');
    if (!img) return;

    if (mode === 'walk' && activeLightboxState.walkSrc) {
      img.src = activeLightboxState.walkSrc;
      if (ttl) ttl.textContent = activeLightboxState.baseTitle + ' — 5-Block Component Flow';
      if (btnArch) btnArch.classList.remove('active');
      if (btnWalk) btnWalk.classList.add('active');
    } else {
      img.src = activeLightboxState.archSrc;
      if (ttl) ttl.textContent = activeLightboxState.baseTitle + (activeLightboxState.walkSrc ? ' — 3x GCP Reference Architecture' : '');
      if (btnArch) btnArch.classList.add('active');
      if (btnWalk) btnWalk.classList.remove('active');
    }
  }

  function closeDiagramLightbox() {
    var modal = document.getElementById('portal-diagram-lightbox');
    if (modal) modal.classList.remove('open');
  }

  function copyTextSnippet(text, btnEl) {
    if (!navigator.clipboard) return;
    navigator.clipboard.writeText(text).then(function () {
      if (btnEl) {
        var orig = btnEl.innerHTML;
        btnEl.innerHTML = INLINE_SVG.check + ' <span>Copied!</span>';
        setTimeout(function () { btnEl.innerHTML = orig; }, 1600);
      }
    });
  }

  function escapeHtml(str) {
    return String(str || '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');
  }

  function init3DSpatialGlassPhysics() {
    document.addEventListener('mousemove', function (e) {
      var cards = document.querySelectorAll('.liquid-3d-tilt');
      cards.forEach(function (card) {
        var rect = card.getBoundingClientRect();
        if (
          e.clientX < rect.left - 40 ||
          e.clientX > rect.right + 40 ||
          e.clientY < rect.top - 40 ||
          e.clientY > rect.bottom + 40
        ) {
          card.style.setProperty('--rx', '0deg');
          card.style.setProperty('--ry', '0deg');
          return;
        }
        var x = (e.clientX - rect.left) / Math.max(1, rect.width);
        var y = (e.clientY - rect.top) / Math.max(1, rect.height);
        var ry = ((x - 0.5) * 5.5).toFixed(2) + 'deg';
        var rx = ((0.5 - y) * 4.5).toFixed(2) + 'deg';
        card.style.setProperty('--rx', rx);
        card.style.setProperty('--ry', ry);
        card.style.setProperty('--glare-x', (x * 100).toFixed(1) + '%');
        card.style.setProperty('--glare-y', (y * 100).toFixed(1) + '%');
      });
    }, { passive: true });
  }

  function bindRocketLiveEvents() {
    window.addEventListener('rocketlive:state', function (ev) {
      var st = (ev.detail && ev.detail.state) || 'idle';
      var labels = {
        idle: 'Ready · Click "Start Live Video Avatar" or ask anything below',
        connecting: 'Connecting to Gemini 3.8 Live 24fps Video Stream…',
        listening: 'Listening Live (16kHz PCM + Server VAD Barge-In Active)…',
        user_speaking: 'Hearing you speak…',
        thinking: 'Gemini 3.8 Live reasoning & syncing portal view…',
        speaking: (AVATAR_ROSTER[currentAvatarKey]?.name || 'Kira') + ' is speaking live (24fps H.264 + 24kHz)…'
      };
      updateAvatarStatusUI(st, labels[st] || st);
    });

    window.addEventListener('rocketlive:user_transcript', function (ev) {
      var d = ev.detail || {};
      if (d.text && d.final) {
        appendCopilotMessage('user', d.text, 'Live Voice Mic');
      }
    });

    window.addEventListener('rocketlive:avatar_transcript', function (ev) {
      var d = ev.detail || {};
      var liveCap = document.getElementById('portal-avatar-live-caption');
      if (liveCap && d.text) {
        liveCap.textContent = d.text;
      }
      if (d.text && d.final) {
        appendCopilotMessage('assistant', d.text, 'gemini-3.8-live · 24fps Video Avatar');
      }
    });

    setInterval(function () {
      var vidEl = document.getElementById('portal-avatar-live-video');
      if (vidEl && window.RocketLive && window.RocketLive.isActive()) {
        var ready = vidEl.readyState >= 2 && vidEl.videoWidth > 0;
        vidEl.classList.toggle('is-streaming', ready);
      }
    }, 250);
  }

  // Export globals
  window.setLiquidVersion = setLiquidVersion;
  window.cycleLiquidVersion = cycleLiquidVersion;
  window.toggleVersionPopover = toggleVersionPopover;
  window.closeVersionPopover = closeVersionPopover;
  window.switchPortalTab = switchPortalTab;
  window.selectPortalAvatar = selectPortalAvatar;
  window.togglePortalLiveAvatar = togglePortalLiveAvatar;
  window.interruptPortalAvatar = interruptPortalAvatar;
  window.stopAllPortalAudio = stopAllPortalAudio;
  window.stopPortalAudio = stopAllPortalAudio;
  window.stopTtsPlayback = stopTtsPlayback;
  window.askPortalCopilot = askPortalCopilot;
  window.speakPortalText = speakPortalText;
  window.filterGlossaryView = filterGlossaryView;
  window.filterArchiveBlueprints = filterArchiveBlueprints;
  window.openDiagramLightbox = openDiagramLightbox;
  window.switchLightboxView = switchLightboxView;
  window.closeDiagramLightbox = closeDiagramLightbox;
  window.copyTextSnippet = copyTextSnippet;
  window.runAutonomousStudioDemo = runAutonomousStudioDemo;
  window.switchWorkbenchMode = switchWorkbenchMode;
  window.closeAutonomousWorkbench = closeAutonomousWorkbench;

  document.addEventListener('click', function (e) {
    var wrap = document.getElementById('ui-version-switcher-wrap');
    if (wrap && !wrap.contains(e.target)) {
      closeVersionPopover();
    }
  });

  document.addEventListener('DOMContentLoaded', function () {
    var params = new URLSearchParams(window.location.search);
    var urlVer = (params.get('version') || params.get('v') || '').toLowerCase();
    // Always default to Version 1 (Cupertino Daylight Prism) unless explicitly requested via URL param
    if (urlVer === '2' || urlVer === 'v2') setLiquidVersion('v2');
    else if (urlVer === '3' || urlVer === 'v3') setLiquidVersion('v3');
    else if (urlVer === '4' || urlVer === 'v4') setLiquidVersion('v4');
    else setLiquidVersion('v1');

    var urlTab = (params.get('tab') || '').toLowerCase();
    if (['studios', 'build', 'glossary', 'archive'].indexOf(urlTab) !== -1) {
      switchPortalTab(urlTab);
    }

    init3DSpatialGlassPhysics();
    bindRocketLiveEvents();
  });
})();
