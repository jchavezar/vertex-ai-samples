/* ==========================================================================
   Rocket × Google Cloud — Zero-Latency Async Client Telemetry & Dwell Engine
   - Non-blocking (< 0.02ms) passive click, dwell-time, service affinity & UX tracker
   - Flushes out-of-band via navigator.sendBeacon('/api/telemetry/ingest')
   - Captures Work Email (@rocket.com / @google.com) on first visit
   ========================================================================== */

(function () {
  'use strict';

  var EVENT_BUFFER = [];
  var FLUSH_INTERVAL_MS = 3000;
  var DWELL_TICK_MS = 5000;
  var lastInteractionTs = Date.now();
  var currentDemoContext = {
    demo_id: 'portal-live-studios',
    demo_name: 'Flagship 5-Pillar AI Studio Hub',
    gcp_service: 'Vertex AI Gemini 3.8 Flash & Live Avatar'
  };
  var clickTimestamps = [];

  function getCookie(name) {
    try {
      var match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
      return match ? decodeURIComponent(match[2]) : '';
    } catch (e) {
      return '';
    }
  }

  function setCookie(name, value, days) {
    try {
      document.cookie =
        name +
        '=' +
        encodeURIComponent(value) +
        ';path=/;max-age=' +
        (days || 14) * 86400 +
        ';SameSite=Lax';
    } catch (e) {}
  }

  function getActiveUserEmail() {
    var cookieEmail = getCookie('rocket_user_email');
    var lsEmail = '';
    try {
      lsEmail = localStorage.getItem('rkt_user_email') || '';
    } catch (e) {}
    var email = (cookieEmail || lsEmail || '').trim().toLowerCase();
    if (email && email.indexOf('@') > 0) {
      if (!cookieEmail) setCookie('rocket_user_email', email, 14);
      try {
        if (!lsEmail) localStorage.setItem('rkt_user_email', email);
      } catch (e) {}
      return email;
    }
    return '';
  }

  function deriveNameFromEmail(email) {
    if (!email || email.indexOf('@') === -1) return '';
    var local = email.split('@')[0];
    var parts = local.replace(/[._-]+/g, ' ').split(' ');
    return parts
      .filter(Boolean)
      .map(function (w) {
        return w.charAt(0).toUpperCase() + w.slice(1);
      })
      .join(' ');
  }

  function syncEmailToSupportAndNav(email) {
    if (!email) return;
    var supEmail = document.getElementById('rkt-sup-user-email');
    if (supEmail && !supEmail.value) {
      supEmail.value = email;
      try {
        localStorage.setItem('rkt_sup_user_email', email);
      } catch (e) {}
    }
    var supName = document.getElementById('rkt-sup-user-name');
    if (supName && !supName.value) {
      var derived = deriveNameFromEmail(email);
      if (derived) {
        supName.value = derived;
        try {
          localStorage.setItem('rkt_sup_user_name', derived);
        } catch (e) {}
      }
    }
  }

  function inferGcpService(textOrId) {
    var s = (textOrId || '').toLowerCase();
    if (s.indexOf('timesfm') !== -1 || s.indexOf('pillar-1') !== -1 || s.indexOf('forecast') !== -1) {
      return 'BigQuery ML AI.FORECAST (TimesFM 2.0)';
    }
    if (s.indexOf('veo') !== -1 || s.indexOf('pillar-2') !== -1 || s.indexOf('reel') !== -1) {
      return 'Vertex AI Veo 3.1 & Nano Banana 2';
    }
    if (s.indexOf('maps') !== -1 || s.indexOf('youtube') !== -1 || s.indexOf('pillar-3') !== -1 || s.indexOf('grounding') !== -1) {
      return 'Google Maps + YouTube + Search Grounding';
    }
    if (s.indexOf('avatar') !== -1 || s.indexOf('pillar-4') !== -1 || s.indexOf('live') !== -1 || s.indexOf('kira') !== -1) {
      return 'Gemini 3.8 Live API (24kHz Voice & Video Avatar)';
    }
    if (s.indexOf('vector') !== -1 || s.indexOf('redfin') !== -1 || s.indexOf('pillar-5') !== -1 || s.indexOf('cosine') !== -1) {
      return 'BigQuery Vector Search (COSINE + RRF) & Gemini Judge';
    }
    if (s.indexOf('gecx') !== -1 || s.indexOf('cxas') !== -1 || s.indexOf('scrappy') !== -1) {
      return 'GECX / CX Agent Studio (cxas-scrappy)';
    }
    if (s.indexOf('mcp') !== -1 || s.indexOf('a2a') !== -1 || s.indexOf('adk') !== -1 || s.indexOf('harness') !== -1 || s.indexOf('subagent') !== -1) {
      return 'Google ADK + Vertex AI Agent Engine + MCP';
    }
    if (s.indexOf('armor') !== -1 || s.indexOf('sandbox') !== -1 || s.indexOf('gvisor') !== -1 || s.indexOf('security') !== -1) {
      return 'Model Armor & Cloud Run gVisor Sandbox';
    }
    if (s.indexOf('argon') !== -1 || s.indexOf('square') !== -1 || s.indexOf('blueprint') !== -1) {
      return 'Vertex AI Gemini 4 Argon (Deep Reasoning)';
    }
    return currentDemoContext.gcp_service || 'Vertex AI Gemini 3.8 Flash';
  }

  function enqueueClientEvent(evt) {
    if (!evt || typeof evt !== 'object') return;
    evt.user_email = evt.user_email || getActiveUserEmail() || 'anonymous@rocket.com';
    evt.page = evt.page || window.location.pathname;
    evt.gcp_service = evt.gcp_service || inferGcpService((evt.target_id || '') + ' ' + (evt.target_label || ''));
    evt.demo_name = evt.demo_name || currentDemoContext.demo_name;
    evt.ts_client = Date.now();
    EVENT_BUFFER.push(evt);
    if (EVENT_BUFFER.length >= 10) {
      flushTelemetryNow();
    }
  }

  function flushTelemetryNow() {
    if (!EVENT_BUFFER.length) return;
    var batch = EVENT_BUFFER.splice(0, 30);
    var authToken = window.PORTAL_AUTH_TOKEN || '';
    var url = '/api/telemetry/ingest' + (authToken ? '?auth_token=' + encodeURIComponent(authToken) : '');
    var payload = JSON.stringify({
      user_email: getActiveUserEmail() || 'anonymous@rocket.com',
      events: batch
    });

    try {
      if (navigator.sendBeacon) {
        var blob = new Blob([payload], { type: 'application/json' });
        if (navigator.sendBeacon(url, blob)) return;
      }
    } catch (e) {}

    try {
      fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: payload,
        keepalive: true
      }).catch(function () {});
    } catch (e) {}
  }

  function classifyClickedTarget(el) {
    if (!el) return null;
    var node = el.closest
      ? el.closest(
          'button, a, [data-tab-btn], [data-gl-role], [data-gl-goal], [data-rosetta-key], .gl-concept-card, .pillar-card, .archive-blueprint-card, .lg-chip'
        )
      : null;
    if (!node) return null;

    var id = node.id || '';
    var text = (node.innerText || node.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 72);
    var href = node.getAttribute('href') || '';
    var onclick = node.getAttribute('onclick') || '';
    var tabBtn = node.getAttribute('data-tab-btn') || '';

    // 1. Top Navigation Tabs
    if (tabBtn || id.indexOf('nav-tab-') === 0) {
      var tabMap = {
        studios: { demo_name: 'Tab 1 · Live AI Studios', gcp_service: 'Vertex AI Multi-Agent Studios' },
        build: { demo_name: 'Tab 2 · Build & GitHub (<3m Setup)', gcp_service: 'Google ADK + Cloud Run + Antigravity' },
        glossary: { demo_name: 'Tab 3 · Agent Platform Glossary & Mini-IDE', gcp_service: 'Vertex AI Agent Engine + ADK Sandbox' },
        archive: { demo_name: 'Tab 4 · 33 Departmental Blueprints', gcp_service: 'Vertex AI Gemini 4 Argon + gVisor Sandbox' }
      };
      var mapped = tabMap[tabBtn] || { demo_name: 'Tab: ' + (text || tabBtn), gcp_service: inferGcpService(text) };
      currentDemoContext.demo_id = 'tab-' + (tabBtn || id);
      currentDemoContext.demo_name = mapped.demo_name;
      currentDemoContext.gcp_service = mapped.gcp_service;
      return {
        event_type: 'tab_switch',
        category: 'Top Navigation',
        target_id: 'tab-' + (tabBtn || id),
        target_label: mapped.demo_name,
        demo_name: mapped.demo_name,
        gcp_service: mapped.gcp_service
      };
    }

    // 2. Glossary Mini-IDE Sandbox Launch or Run
    if (onclick.indexOf('openGlossarySandboxIde') !== -1 || id.indexOf('gl-ide-') === 0) {
      var cardEl = node.closest ? node.closest('.gl-concept-card') : null;
      var cardId = cardEl ? cardEl.id : id;
      var svc = inferGcpService(cardId + ' ' + text);
      currentDemoContext.demo_id = cardId || 'gl-sandbox-ide';
      currentDemoContext.demo_name = 'Glossary Mini-IDE Sandbox (' + (cardId || 'Live Code') + ')';
      currentDemoContext.gcp_service = svc;
      return {
        event_type: id === 'gl-ide-reset-btn' ? 'ux_friction' : 'sandbox_ide_click',
        category: 'Glossary Mini-IDE',
        target_id: cardId || id || 'gl-sandbox-ide',
        target_label: 'Mini-IDE: ' + (text || cardId || 'Sandbox Action'),
        demo_name: currentDemoContext.demo_name,
        gcp_service: svc
      };
    }

    // 3. Glossary Concept Cards / Role / Goal / Rosetta
    if (node.hasAttribute('data-gl-role') || node.hasAttribute('data-gl-goal') || node.hasAttribute('data-rosetta-key')) {
      var roleKey =
        node.getAttribute('data-gl-role') ||
        node.getAttribute('data-gl-goal') ||
        node.getAttribute('data-rosetta-key');
      currentDemoContext.demo_id = 'gl-selector-' + roleKey;
      currentDemoContext.demo_name = 'Tab 3 · Agent Platform Glossary & Mini-IDE';
      currentDemoContext.gcp_service = inferGcpService(roleKey + ' ' + text);
      return {
        event_type: 'glossary_filter',
        category: 'Agent Platform Glossary',
        target_id: 'gl-' + roleKey,
        target_label: 'Glossary Selector: ' + (text || roleKey),
        demo_name: currentDemoContext.demo_name,
        gcp_service: currentDemoContext.gcp_service
      };
    }
    if (node.classList && node.classList.contains('gl-concept-card')) {
      var cSvc = inferGcpService(node.id + ' ' + text);
      currentDemoContext.demo_id = node.id || 'gl-card';
      currentDemoContext.demo_name = 'Glossary Concept: ' + (node.id || text.slice(0, 36));
      currentDemoContext.gcp_service = cSvc;
      return {
        event_type: 'glossary_card_click',
        category: 'Agent Platform Glossary',
        target_id: node.id || 'gl-card',
        target_label: 'Glossary Card: ' + (node.id || text.slice(0, 48)),
        demo_name: currentDemoContext.demo_name,
        gcp_service: cSvc
      };
    }

    // 4. Live Studios & Autonomous Demo Runs
    if (
      onclick.indexOf('runAutonomousStudioDemo') !== -1 ||
      href.indexOf('rocket-polymorphic-search') !== -1 ||
      href.indexOf('rocket-cxas-launchpad') !== -1 ||
      href.indexOf('rocket-monday-superwow') !== -1
    ) {
      var dName = 'Flagship 5-Pillar AI Studio';
      if (onclick.indexOf('pillar-1') !== -1 || text.indexOf('TimesFM') !== -1) dName = 'Pillar 1 · BigQuery TimesFM 2.0 Forecasting';
      else if (onclick.indexOf('pillar-2') !== -1 || text.indexOf('Veo') !== -1) dName = 'Pillar 2 · Veo 3.1 9:16 Marketing Reels';
      else if (onclick.indexOf('pillar-3') !== -1 || text.indexOf('Maps') !== -1) dName = 'Pillar 3 · Maps + YouTube Grounded Chat';
      else if (onclick.indexOf('pillar-4') !== -1 || text.indexOf('Avatar') !== -1) dName = 'Pillar 4 · Gemini 3.8 Live Video Avatar';
      else if (onclick.indexOf('pillar-5') !== -1 || text.indexOf('Vector') !== -1 || text.indexOf('Redfin') !== -1) dName = 'Pillar 5 · Redfin × Rocket Hybrid Vector Search';
      else if (href.indexOf('cxas') !== -1 || onclick.indexOf('gecx') !== -1) dName = 'GECX · CX Agent Studio & cxas-scrappy';
      else if (href.indexOf('superwow') !== -1) dName = 'Monday Super-Wow 5-Option Lab';

      var stSvc = inferGcpService(dName + ' ' + onclick + ' ' + text);
      currentDemoContext.demo_id = id || dName;
      currentDemoContext.demo_name = dName;
      currentDemoContext.gcp_service = stSvc;
      return {
        event_type: 'studio_launch',
        category: 'Live AI Studios',
        target_id: dName,
        target_label: dName + ' (' + (text || 'Run') + ')',
        demo_name: dName,
        gcp_service: stSvc
      };
    }

    // 5. 33 Blueprints & Standalone Sandboxes
    if (href.indexOf('/square/') !== -1 || href.indexOf('/docs/') !== -1) {
      var bpPath = href.split('?')[0];
      var bpName = 'Blueprint ' + bpPath.replace('/square/', '').replace('/docs/', '');
      currentDemoContext.demo_id = bpPath;
      currentDemoContext.demo_name = bpName;
      currentDemoContext.gcp_service = 'Vertex AI Gemini 4 Argon + gVisor Sandbox';
      return {
        event_type: 'blueprint_open',
        category: '33 Use-Case Blueprints',
        target_id: bpPath,
        target_label: bpName + ' (' + (text || 'Open') + ')',
        demo_name: bpName,
        gcp_service: currentDemoContext.gcp_service
      };
    }

    // 6. Support Overlay & Google Chat Bridge
    if (id.indexOf('rkt-sup') === 0 || id === 'rkt-support-fab') {
      return {
        event_type: 'support_click',
        category: 'Support & Google Chat',
        target_id: id,
        target_label: 'Support Widget: ' + (text || id),
        demo_name: currentDemoContext.demo_name,
        gcp_service: 'Portal Support Concierge & Google Chat Bridge'
      };
    }

    if (text || id) {
      return {
        event_type: 'ui_click',
        category: 'Portal UI',
        target_id: id || text.toLowerCase().replace(/[^a-z0-9]+/g, '-').slice(0, 48),
        target_label: text || id,
        demo_name: currentDemoContext.demo_name,
        gcp_service: inferGcpService(id + ' ' + text)
      };
    }
    return null;
  }

  function renderEmailGateIfNeeded() {
    var existingEmail = getActiveUserEmail();
    if (existingEmail) {
      syncEmailToSupportAndNav(existingEmail);
      return;
    }
    if (document.getElementById('rkt-email-gate-backdrop')) return;

    var backdrop = document.createElement('div');
    backdrop.id = 'rkt-email-gate-backdrop';
    backdrop.style.cssText = [
      'position:fixed;inset:0;z-index:20000;',
      'background:rgba(6,9,19,0.72);backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);',
      'display:flex;align-items:center;justify-content:center;padding:20px;'
    ].join('');

    backdrop.innerHTML = [
      '<div style="width:100%;max-width:440px;background:#0F172A;border:1px solid rgba(255,255,255,0.16);border-radius:20px;padding:28px 26px;color:#F8FAFC;box-shadow:0 28px 70px rgba(0,0,0,0.65);font-family:\'Plus Jakarta Sans\',sans-serif;position:relative;overflow:hidden;">',
      '  <div style="position:absolute;top:0;left:0;right:0;height:4px;background:linear-gradient(90deg,#E11D48,#2563EB,#10B981);"></div>',
      '  <div style="display:inline-flex;align-items:center;gap:6px;padding:4px 10px;border-radius:999px;background:rgba(225,29,72,0.16);border:1px solid rgba(225,29,72,0.4);color:#FDA4AF;font-size:10px;font-weight:700;font-family:\'JetBrains Mono\',monospace;margin-bottom:12px;">',
      '    ROCKET × GOOGLE CLOUD HACKATHON',
      '  </div>',
      '  <h2 style="font-size:19px;font-weight:800;letter-spacing:-0.02em;margin:0 0 6px;">Enter Your Work Email to Continue</h2>',
      '  <p style="font-size:12.5px;color:#94A3B8;line-height:1.55;margin:0 0 18px;">Used to personalize your live Mini-IDE Sandbox sessions and route 1:1 replies from the <strong>Detroit Dream Team: Halloween Hackathon</strong> Google Chat space.</p>',
      '  <form id="rkt-email-gate-form" style="display:flex;flex-direction:column;gap:12px;">',
      '    <div>',
      '      <label style="display:block;font-size:10.5px;font-weight:700;text-transform:uppercase;letter-spacing:0.06em;color:#CBD5E1;font-family:\'JetBrains Mono\',monospace;margin-bottom:6px;">Work Email (@rocket.com or @google.com)</label>',
      '      <input id="rkt-email-gate-input" type="email" required placeholder="alex.smith@rocket.com" autocomplete="email" style="width:100%;padding:11px 14px;border-radius:10px;border:1px solid rgba(255,255,255,0.22);background:rgba(15,23,42,0.9);color:#F8FAFC;font-size:13.5px;font-family:\'JetBrains Mono\',monospace;outline:none;" />',
      '    </div>',
      '    <button type="submit" style="width:100%;padding:12px 16px;border-radius:10px;border:none;background:linear-gradient(135deg,#E11D48,#BE123C);color:#FFFFFF;font-size:13.5px;font-weight:800;cursor:pointer;">Continue to Command Hub →</button>',
      '  </form>',
      '</div>'
    ].join('');

    document.body.appendChild(backdrop);

    var inputEl = document.getElementById('rkt-email-gate-input');
    if (inputEl) {
      setTimeout(function () {
        inputEl.focus();
      }, 60);
    }

    var formEl = document.getElementById('rkt-email-gate-form');
    if (formEl) {
      formEl.addEventListener('submit', function (ev) {
        ev.preventDefault();
        var raw = (inputEl && inputEl.value ? inputEl.value : '').trim().toLowerCase();
        if (!raw || raw.indexOf('@') < 1) return;
        setCookie('rocket_user_email', raw, 14);
        try {
          localStorage.setItem('rkt_user_email', raw);
        } catch (e) {}
        syncEmailToSupportAndNav(raw);
        enqueueClientEvent({
          event_type: 'login',
          category: 'Authentication',
          target_id: 'email-gate-modal',
          target_label: 'Work Email Registered: ' + raw,
          user_email: raw
        });
        flushTelemetryNow();
        backdrop.remove();
      });
    }
  }

  function initPortalTelemetry() {
    if (window.location.pathname === '/glossary') {
      currentDemoContext.demo_id = 'standalone-glossary';
      currentDemoContext.demo_name = 'Tab 3 · Agent Platform Glossary & Mini-IDE';
      currentDemoContext.gcp_service = 'Vertex AI Agent Engine + ADK Sandbox';
    } else if (window.location.pathname.indexOf('/square/') === 0) {
      currentDemoContext.demo_id = window.location.pathname;
      currentDemoContext.demo_name = 'Blueprint ' + window.location.pathname.replace('/square/', '');
      currentDemoContext.gcp_service = 'Vertex AI Gemini 4 Argon + gVisor Sandbox';
    }

    renderEmailGateIfNeeded();

    setTimeout(function () {
      enqueueClientEvent({
        event_type: 'page_view',
        category: 'Navigation',
        target_id: window.location.pathname || '/',
        target_label: 'Page View: ' + (window.location.pathname || '/'),
        demo_name: currentDemoContext.demo_name,
        gcp_service: currentDemoContext.gcp_service
      });
    }, 150);

    // Passive activity markers for accurate dwell-time tracking
    ['mousemove', 'keydown', 'scroll', 'touchstart'].forEach(function (evtName) {
      window.addEventListener(
        evtName,
        function () {
          lastInteractionTs = Date.now();
        },
        { passive: true }
      );
    });

    // Passive click + rage-click friction detector
    document.addEventListener(
      'click',
      function (ev) {
        try {
          var now = Date.now();
          lastInteractionTs = now;
          clickTimestamps.push(now);
          while (clickTimestamps.length && now - clickTimestamps[0] > 1800) {
            clickTimestamps.shift();
          }
          var info = classifyClickedTarget(ev.target);
          if (clickTimestamps.length >= 5 && info) {
            enqueueClientEvent({
              event_type: 'ux_friction',
              category: 'Rapid Repeat Click',
              target_id: info.target_id,
              target_label: 'Rapid Click (5x in <2s) on ' + info.target_label,
              demo_name: currentDemoContext.demo_name,
              gcp_service: currentDemoContext.gcp_service
            });
            clickTimestamps = [];
          }
          if (info) {
            enqueueClientEvent(info);
          }
        } catch (e) {}
      },
      { capture: true, passive: true }
    );

    // Active Dwell-Time Heartbeat (every 5 seconds while tab is visible and user was active in last 60s)
    setInterval(function () {
      if (document.visibilityState !== 'visible') return;
      if (Date.now() - lastInteractionTs > 60000) return;
      enqueueClientEvent({
        event_type: 'dwell_ping',
        category: 'Dwell Time',
        target_id: currentDemoContext.demo_id,
        target_label: currentDemoContext.demo_name,
        demo_name: currentDemoContext.demo_name,
        gcp_service: currentDemoContext.gcp_service,
        dwell_sec: 5
      });
    }, DWELL_TICK_MS);

    setInterval(flushTelemetryNow, FLUSH_INTERVAL_MS);

    window.addEventListener('visibilitychange', function () {
      if (document.visibilityState === 'hidden') {
        flushTelemetryNow();
      }
    });
  }

  window.RocketTelemetry = {
    track: enqueueClientEvent,
    flush: flushTelemetryNow,
    getUserEmail: getActiveUserEmail
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initPortalTelemetry);
  } else {
    initPortalTelemetry();
  }
})();
