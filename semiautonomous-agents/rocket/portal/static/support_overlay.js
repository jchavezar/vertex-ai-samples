/**
 * Rocket × Google Cloud Portal — Bottom-Right AI + Live Human Google Chat Support Widget
 * (`static/support_overlay.js`)
 *
 * Provides:
 * 1. Instant AI Portal Concierge (`gemini-3.8-flash` via `POST /api/support/ask-ai`)
 * 2. Live 2-Way Human Escalation to Google Workspace Chat Space:
 *    `Detroit Dream Team: Halloween Hackathon` (`spaces/AAQA9IvwTUs`)
 *    via `POST /api/support/send-human` and `GET /api/support/ticket/{ticket_id}`
 */
(function () {
  'use strict';

  var activeTab = 'ai'; // 'ai' | 'human'
  var isOpen = false;
  var aiHistory = [];
  var lastUserAiQuestion = '';
  var activeTicketId = '';
  var seenMsgCount = 0;
  var unreadHumanCount = 0;
  var pollTimer = null;

  var SVG = {
    support: '<svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/><path d="M8 10h.01"/><path d="M12 10h.01"/><path d="M16 10h.01"/></svg>',
    sparkle: '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3l1.9 5.8a2 2 0 0 0 1.3 1.3L21 12l-5.8 1.9a2 2 0 0 0-1.3 1.3L12 21l-1.9-5.8a2 2 0 0 0-1.3-1.3L3 12l5.8-1.9a2 2 0 0 0 1.3-1.3L12 3z"/></svg>',
    users: '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>',
    send: '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>',
    close: '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>'
  };

  function escapeHtml(str) {
    return String(str || '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');
  }

  function formatInlineMd(str) {
    var s = escapeHtml(str).replace(/\n/g, '<br>');
    s = s.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    s = s.replace(/`([^`]+)`/g, '<code style="background:rgba(56,189,248,0.14);color:#38BDF8;padding:1px 5px;border-radius:4px;font-family:\'JetBrains Mono\',monospace;font-size:11px;">$1</code>');
    return s;
  }

  function getAuthToken() {
    if (window.PORTAL_AUTH_TOKEN) return window.PORTAL_AUTH_TOKEN;
    var root = document.getElementById('gl-launchpad-root');
    if (root && root.getAttribute('data-auth-token')) return root.getAttribute('data-auth-token');
    var params = new URLSearchParams(window.location.search);
    return params.get('auth_token') || 'rocket:e3a48aa96ebeb0731e4c751d';
  }

  function mountSupportOverlay() {
    if (document.getElementById('rkt-support-root')) return;

    try {
      activeTicketId = localStorage.getItem('rkt_support_ticket_id') || '';
    } catch (_) {}

    var root = document.createElement('div');
    root.id = 'rkt-support-root';
    root.innerHTML = (
      '<button type="button" id="rkt-support-fab" class="rkt-support-fab" onclick="window.toggleRocketSupportOverlay()" title="Ask the Portal AI Assistant or message the Google Cloud × Rocket Team live in Google Chat">' +
        '<span class="rkt-support-fab-dot"></span>' +
        SVG.support +
        '<span>Ask AI / Live Google Team</span>' +
        '<span id="rkt-support-unread-badge" class="rkt-support-unread">0</span>' +
      '</button>' +

      '<div id="rkt-support-window" class="rkt-support-window" role="dialog" aria-label="Rocket Portal AI and Google Chat Support">' +
        '<div class="rkt-sup-header">' +
          '<div class="rkt-sup-title-row">' +
            '<div class="rkt-sup-brand">' +
              '<span class="rkt-sup-brand-badge">' + SVG.support + '</span>' +
              '<div>' +
                '<div style="font-size:14px;font-weight:800;letter-spacing:-0.01em;">Rocket × Google Cloud Support</div>' +
                '<div style="font-size:10.5px;color:#94A3B8;font-family:\'JetBrains Mono\',monospace;">AI CONCIERGE + LIVE GOOGLE WORKSPACE CHAT</div>' +
              '</div>' +
            '</div>' +
            '<button type="button" class="rkt-sup-close-btn" onclick="window.toggleRocketSupportOverlay(false)" title="Minimize Support Window">' +
              SVG.close +
            '</button>' +
          '</div>' +

          '<div class="rkt-sup-tabs" role="tablist">' +
            '<button type="button" class="rkt-sup-tab-btn active" data-sup-tab="ai" onclick="window.switchRocketSupportTab(\'ai\')">' +
              SVG.sparkle + ' <span>1. Ask Portal AI</span>' +
            '</button>' +
            '<button type="button" class="rkt-sup-tab-btn" data-sup-tab="human" onclick="window.switchRocketSupportTab(\'human\')">' +
              SVG.users + ' <span>2. Talk to a Human</span>' +
            '</button>' +
          '</div>' +
        '</div>' +

        '<!-- PANE 1: AI PORTAL CONCIERGE -->' +
        '<div id="rkt-sup-pane-ai" class="rkt-sup-pane active">' +
          '<div id="rkt-sup-ai-feed" class="rkt-sup-feed">' +
            '<div class="rkt-sup-msg rkt-sup-msg-ai">' +
              '<div class="rkt-sup-msg-meta"><span>Gemini 3.8 Flash · Portal AI Concierge</span><span>Instant</span></div>' +
              '<div>Hi! Ask me anything about the <strong>5 Flagship Studios</strong>, the <strong>Agent Platform Glossary &amp; Mini-IDE</strong>, the <strong>33 Hackathon Microservices</strong>, or GCP setup.<br><br>Want to collaborate directly with our Google Cloud engineers? Click <strong>Talk to a Human</strong> anytime to message our live Google Chat room!</div>' +
              '<button type="button" class="rkt-sup-escalate-btn" onclick="window.switchRocketSupportTab(\'human\')">' +
                SVG.users + ' <span>Talk to a Human in Google Chat →</span>' +
              '</button>' +
            '</div>' +
          '</div>' +
          '<div class="rkt-sup-chips">' +
            '<button type="button" class="rkt-sup-chip" onclick="window.askRocketSupportAi(\'How do I request GCP PAM access for dev-233554-hllwn26-hack-f1f8?\')">GCP PAM Access?</button>' +
            '<button type="button" class="rkt-sup-chip" onclick="window.askRocketSupportAi(\'Which studio or blueprint should I use for Mortgage Underwriting & Form 1084?\')">Underwriting Blueprint?</button>' +
            '<button type="button" class="rkt-sup-chip" onclick="window.switchRocketSupportTab(\'human\')">Talk to Human Team →</button>' +
          '</div>' +
          '<div class="rkt-sup-input-bar">' +
            '<input type="text" id="rkt-sup-ai-input" class="rkt-sup-input" placeholder="Ask AI about any studio, repo, or ADK tool…" onkeydown="if(event.key===\'Enter\')window.askRocketSupportAi()">' +
            '<button type="button" class="rkt-sup-send-btn" onclick="window.askRocketSupportAi()">' +
              SVG.send + ' <span>Ask</span>' +
            '</button>' +
          '</div>' +
        '</div>' +

        '<!-- PANE 2: LIVE HUMAN TEAM IN GOOGLE WORKSPACE CHAT -->' +
        '<div id="rkt-sup-pane-human" class="rkt-sup-pane">' +
          '<div class="rkt-sup-team-strip">' +
            '<span><strong>Live Space:</strong> Detroit Dream Team: Halloween Hackathon</span>' +
            '<span id="rkt-sup-ticket-badge" style="font-family:\'JetBrains Mono\',monospace;font-size:10px;color:#34D399;">2-Way Google Chat Bridge</span>' +
          '</div>' +
          '<div class="rkt-sup-identity-box">' +
            '<input type="text" id="rkt-sup-user-name" class="rkt-sup-id-input" placeholder="Your Name (e.g. Alex · Rocket)">' +
            '<input type="email" id="rkt-sup-user-email" class="rkt-sup-id-input" placeholder="Your Email (@rocket.com)">' +
            '<input type="text" id="rkt-sup-user-track" class="rkt-sup-id-input" style="grid-column:1 / -1;" placeholder="Team / Hackathon Track or Collaboration Topic">' +
          '</div>' +
          '<div id="rkt-sup-human-feed" class="rkt-sup-feed">' +
            '<div class="rkt-sup-msg rkt-sup-msg-human_agent">' +
              '<div class="rkt-sup-msg-meta"><span>Detroit Dream Team · @google.com</span><span>Live</span></div>' +
              '<div>Send a message below and it posts <strong>directly into our internal Google Workspace Chat space</strong> (<em>Detroit Dream Team: Halloween Hackathon</em> — Jesus Chavez, Sundar Chellappa, Angela Kavanaugh, Joris Wynendaele, Luis Lopez, Ricky Merrefield).<br><br>When any Googler replies to your thread in Google Chat, their answer appears right here in real time!</div>' +
            '</div>' +
          '</div>' +
          '<div class="rkt-sup-input-bar">' +
            '<input type="text" id="rkt-sup-human-input" class="rkt-sup-input" placeholder="Message the Google Cloud team in Google Chat…" onkeydown="if(event.key===\'Enter\')window.sendRocketHumanSupportMessage()">' +
            '<button type="button" id="rkt-sup-human-send-btn" class="rkt-sup-send-btn human-btn" onclick="window.sendRocketHumanSupportMessage()">' +
              SVG.send + ' <span>Send</span>' +
            '</button>' +
          '</div>' +
        '</div>' +
      '</div>'
    );

    document.body.appendChild(root);

    // Restore saved participant identity if present
    try {
      var savedName = localStorage.getItem('rkt_support_name') || '';
      var savedEmail = localStorage.getItem('rkt_support_email') || '';
      var savedTrack = localStorage.getItem('rkt_support_track') || '';
      if (savedName) document.getElementById('rkt-sup-user-name').value = savedName;
      if (savedEmail) document.getElementById('rkt-sup-user-email').value = savedEmail;
      if (savedTrack) document.getElementById('rkt-sup-user-track').value = savedTrack;
    } catch (_) {}

    if (activeTicketId) {
      var badge = document.getElementById('rkt-sup-ticket-badge');
      if (badge) badge.textContent = 'Ticket #' + activeTicketId + ' · Live';
      startTicketPolling();
    }
  }

  function toggleRocketSupportOverlay(forceState) {
    var win = document.getElementById('rkt-support-window');
    if (!win) return;
    isOpen = typeof forceState === 'boolean' ? forceState : !isOpen;
    win.classList.toggle('open', isOpen);
    if (isOpen && activeTab === 'human') {
      unreadHumanCount = 0;
      updateUnreadBadge();
    }
  }

  function switchRocketSupportTab(tab, prefillQuestion) {
    activeTab = tab === 'human' ? 'human' : 'ai';
    document.querySelectorAll('[data-sup-tab]').forEach(function (btn) {
      btn.classList.toggle('active', btn.getAttribute('data-sup-tab') === activeTab);
    });
    var pAi = document.getElementById('rkt-sup-pane-ai');
    var pHu = document.getElementById('rkt-sup-pane-human');
    if (pAi) pAi.classList.toggle('active', activeTab === 'ai');
    if (pHu) pHu.classList.toggle('active', activeTab === 'human');

    if (activeTab === 'human') {
      unreadHumanCount = 0;
      updateUnreadBadge();
      var hInput = document.getElementById('rkt-sup-human-input');
      if (hInput && (prefillQuestion || lastUserAiQuestion) && !hInput.value) {
        hInput.value = prefillQuestion || lastUserAiQuestion;
      }
      if (hInput) hInput.focus();
    } else {
      var aInput = document.getElementById('rkt-sup-ai-input');
      if (aInput) aInput.focus();
    }
  }

  function appendAiMessage(role, text, metaLabel) {
    var feed = document.getElementById('rkt-sup-ai-feed');
    if (!feed) return;
    var div = document.createElement('div');
    div.className = 'rkt-sup-msg rkt-sup-msg-' + (role === 'user' ? 'user' : 'ai');
    var who = role === 'user' ? 'You' : 'Gemini 3.8 Flash · Portal AI';
    var inner = (
      '<div class="rkt-sup-msg-meta"><span>' + escapeHtml(who) + '</span><span>' + escapeHtml(metaLabel || '') + '</span></div>' +
      '<div>' + formatInlineMd(text) + '</div>'
    );
    if (role !== 'user') {
      inner += (
        '<button type="button" class="rkt-sup-escalate-btn" onclick="window.switchRocketSupportTab(\'human\')">' +
          SVG.users + ' <span>Ask Human Team in Google Chat →</span>' +
        '</button>'
      );
    }
    div.innerHTML = inner;
    feed.appendChild(div);
    feed.scrollTop = feed.scrollHeight;
  }

  async function askRocketSupportAi(presetQ) {
    var input = document.getElementById('rkt-sup-ai-input');
    var q = (typeof presetQ === 'string' && presetQ.trim())
      ? presetQ.trim()
      : (input ? input.value.trim() : '');
    if (!q) return;
    if (input && !presetQ) input.value = '';

    lastUserAiQuestion = q;
    appendAiMessage('user', q, 'Just now');
    aiHistory.push({ role: 'user', text: q });

    try {
      var token = getAuthToken();
      var res = await fetch('/api/support/ask-ai?auth_token=' + encodeURIComponent(token), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: q, history: aiHistory.slice(-6) })
      });
      var data = await res.json();
      if (data && data.ok) {
        aiHistory.push({ role: 'assistant', text: data.answer });
        appendAiMessage('ai', data.answer, (data.latency_ms || 0) + ' ms');
      } else {
        appendAiMessage('ai', 'Could not reach AI assistant. Click **Ask Human Team in Google Chat** below to message us directly!', 'Fallback');
      }
    } catch (e) {
      appendAiMessage('ai', 'Network error. Click **Ask Human Team in Google Chat** to message our Google Cloud team directly!', 'Offline');
    }
  }

  function renderHumanMessages(messages) {
    var feed = document.getElementById('rkt-sup-human-feed');
    if (!feed || !Array.isArray(messages)) return;

    // Keep the welcome card at index 0 and render all ticket messages below
    var welcomeHtml = (
      '<div class="rkt-sup-msg rkt-sup-msg-human_agent">' +
        '<div class="rkt-sup-msg-meta"><span>Detroit Dream Team · @google.com</span><span>Live</span></div>' +
        '<div>Connected to <strong>Detroit Dream Team: Halloween Hackathon</strong> in Google Chat. Replies from our Google Cloud team stream directly into this window.</div>' +
      '</div>'
    );

    var msgsHtml = messages.map(function (m) {
      var isUser = m.role === 'user';
      var cls = isUser ? 'rkt-sup-msg-user' : 'rkt-sup-msg-human_agent';
      var statusTag = isUser
        ? (m.delivered_to_gchat ? 'Delivered to Google Chat' : 'Syncing to Google Chat…')
        : 'Live Google Chat Reply';
      return (
        '<div class="rkt-sup-msg ' + cls + '">' +
          '<div class="rkt-sup-msg-meta">' +
            '<span>' + escapeHtml(m.sender_name || (isUser ? 'You' : 'Google Cloud Team')) + '</span>' +
            '<span>' + escapeHtml(statusTag) + '</span>' +
          '</div>' +
          '<div>' + formatInlineMd(m.text || '') + '</div>' +
        '</div>'
      );
    }).join('');

    feed.innerHTML = welcomeHtml + msgsHtml;
    feed.scrollTop = feed.scrollHeight;
  }

  function updateUnreadBadge() {
    var badge = document.getElementById('rkt-support-unread-badge');
    if (!badge) return;
    if (unreadHumanCount > 0) {
      badge.textContent = String(unreadHumanCount);
      badge.classList.add('visible');
    } else {
      badge.classList.remove('visible');
    }
  }

  async function sendRocketHumanSupportMessage() {
    var nameEl = document.getElementById('rkt-sup-user-name');
    var emailEl = document.getElementById('rkt-sup-user-email');
    var trackEl = document.getElementById('rkt-sup-user-track');
    var inputEl = document.getElementById('rkt-sup-human-input');
    var sendBtn = document.getElementById('rkt-sup-human-send-btn');

    var msgText = inputEl ? inputEl.value.trim() : '';
    if (!msgText) return;

    var userName = (nameEl && nameEl.value.trim()) || 'Rocket Participant';
    var userEmail = (emailEl && emailEl.value.trim()) || 'participant@rocket.com';
    var userTrack = (trackEl && trackEl.value.trim()) || 'Rocket Hackathon Portal';

    try {
      localStorage.setItem('rkt_support_name', userName);
      localStorage.setItem('rkt_support_email', userEmail);
      localStorage.setItem('rkt_support_track', userTrack);
    } catch (_) {}

    if (inputEl) inputEl.value = '';
    if (sendBtn) sendBtn.disabled = true;

    try {
      var token = getAuthToken();
      var res = await fetch('/api/support/send-human?auth_token=' + encodeURIComponent(token), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ticket_id: activeTicketId,
          user_name: userName,
          user_email: userEmail,
          track: userTrack,
          message: msgText,
          ai_context: lastUserAiQuestion
        })
      });
      var data = await res.json();
      if (sendBtn) sendBtn.disabled = false;

      if (data && data.ok) {
        activeTicketId = data.ticket_id;
        try { localStorage.setItem('rkt_support_ticket_id', activeTicketId); } catch (_) {}
        var badge = document.getElementById('rkt-sup-ticket-badge');
        if (badge) {
          badge.textContent = 'Ticket #' + activeTicketId + (data.delivered_immediately ? ' · Sent to Google Chat' : ' · Queued');
        }
        seenMsgCount = (data.messages || []).length;
        renderHumanMessages(data.messages || []);
        startTicketPolling();
      }
    } catch (e) {
      if (sendBtn) sendBtn.disabled = false;
    }
  }

  async function pollActiveTicket() {
    if (!activeTicketId) return;
    try {
      var token = getAuthToken();
      var res = await fetch('/api/support/ticket/' + encodeURIComponent(activeTicketId) + '?auth_token=' + encodeURIComponent(token));
      var data = await res.json();
      if (data && data.ok && Array.isArray(data.messages)) {
        if (data.messages.length !== seenMsgCount || data.new_replies_count > 0) {
          var added = Math.max(0, data.messages.length - seenMsgCount);
          seenMsgCount = data.messages.length;
          renderHumanMessages(data.messages);
          if ((!isOpen || activeTab !== 'human') && added > 0) {
            unreadHumanCount += added;
            updateUnreadBadge();
          }
        }
      }
    } catch (_) {}
  }

  function startTicketPolling() {
    if (pollTimer) clearInterval(pollTimer);
    pollActiveTicket();
    pollTimer = setInterval(pollActiveTicket, 3000);
  }

  window.toggleRocketSupportOverlay = toggleRocketSupportOverlay;
  window.switchRocketSupportTab = switchRocketSupportTab;
  window.askRocketSupportAi = askRocketSupportAi;
  window.sendRocketHumanSupportMessage = sendRocketHumanSupportMessage;

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', mountSupportOverlay);
  } else {
    mountSupportOverlay();
  }
})();
