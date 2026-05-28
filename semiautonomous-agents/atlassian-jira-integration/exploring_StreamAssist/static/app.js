// streamAssist Inspector — vanilla JS module
const $ = (sel) => document.querySelector(sel);

const state = {
  sessionId: `s-${Math.random().toString(36).slice(2, 10)}`,
  events: [],            // {id, type, t_ms, ts, payload, summary}
  transcript: [],        // {role, text, citations?}
  currentAssist: null,   // {textEl, citationsEl, buffer, citations[]}
  reasoning: [],         // strings
  filters: { request: true, chat: true, raw: true, error: true, done: true, trace: true, auth_mode: true },
  newestFirst: false,
  search: "",
  engine: null,
  startedAt: 0,
  activeTab: "events",
  auth: {
    configured: false,    // server has OAUTH_CLIENT_ID set
    clientId: null,
    scopes: [],
    user: null,           // {email, name, picture, user_pseudo_id, sub}
    accessToken: null,
    accessTokenExpiresAt: 0,
    tokenClient: null,    // google.accounts.oauth2 client
    jiraConsented: null,  // null=unknown, true=ok, false=needs consent
  },
  // logs tab
  logs: {
    es: null,           // EventSource
    traceId: null,
    project: "vtxdemos",
    entries: [],        // raw summaries from server
    byInsert: new Set(),
    counts: { total: 0, otel: 0, audit: 0, other: 0 },
    filters: { audit: true, "user.message": true, choice: true, function_call: false },
    search: "",
    unread: 0,
    status: "idle",     // idle | waiting | live | done | error
    startedAt: 0,
  },
  // unread counter on the inactive REST tab
  eventsUnread: 0,
};

$("#session-badge").textContent = `session: ${state.sessionId}`;

// ---------- engine info ----------
fetch("/api/engine").then(r => r.json()).then(meta => {
  state.engine = meta;
  const ds = (meta.dataStoreIds || []).length;
  $("#engine-line").textContent =
    `${meta.displayName || meta.name} — ${ds} datastores attached`;
  $("#engine-line").title = (meta.dataStoreIds || []).join("\n");
}).catch(() => {
  $("#engine-line").textContent = "engine metadata unavailable";
});

// ---------- auth: bootstrap, sign-in, sign-out, banner, toast ----------
const signinBtn = $("#signin-btn");
const signinFallback = $("#signin-fallback");
const userChip = $("#user-chip");
const userAvatarEl = $("#user-avatar");
const userEmailEl = $("#user-email");
const signoutBtn = $("#signout-btn");
const connectJiraBtn = $("#connect-jira-btn");
const authBanner = $("#auth-banner");
const toastHost = $("#toast-host");
const composerEl = $("#composer");

function toast(msg, kind = "ok", ms = 4500) {
  const el = document.createElement("div");
  el.className = `toast ${kind}`;
  el.textContent = msg;
  toastHost.appendChild(el);
  setTimeout(() => { el.style.opacity = "0"; el.style.transition = "opacity .25s"; }, ms - 250);
  setTimeout(() => el.remove(), ms);
}

function setBanner(kind, html) {
  if (!html) {
    authBanner.classList.add("hidden");
    authBanner.innerHTML = "";
    return;
  }
  authBanner.className = `auth-banner ${kind || ""}`;
  authBanner.innerHTML = `<span class="dot"></span><span>${html}</span>`;
  authBanner.classList.remove("hidden");
}

function setComposerLocked(locked) {
  composerEl.classList.toggle("locked", !!locked);
  $("#input").disabled = !!locked;
  $("#send").disabled = !!locked;
}

function refreshUIForAuthState() {
  const cfg = state.auth;
  const signedIn = !!cfg.user;

  // Sign-in / chip visibility
  if (!cfg.configured) {
    signinBtn.classList.add("hidden");
    signinFallback.classList.remove("hidden");
    userChip.classList.add("hidden");
  } else if (signedIn) {
    signinBtn.classList.add("hidden");
    signinFallback.classList.add("hidden");
    userChip.classList.remove("hidden");
    userAvatarEl.src = cfg.user.picture || "";
    userEmailEl.textContent = cfg.user.email || cfg.user.name || "signed in";
  } else {
    signinBtn.classList.remove("hidden");
    signinFallback.classList.add("hidden");
    userChip.classList.add("hidden");
  }

  // Connect Jira button: enabled iff signed in
  connectJiraBtn.disabled = !signedIn;
  connectJiraBtn.title = signedIn
    ? "Open Gemini Enterprise to grant 3LO access to your Jira"
    : "Sign in with Google first";
  connectJiraBtn.classList.toggle("needs-consent", signedIn && cfg.jiraConsented === false);

  // Composer + banner
  if (!cfg.configured) {
    setComposerLocked(false); // SA still works for non-Jira
    setBanner("warn",
      "End-user OAuth is not configured on this server — running in service-account mode. " +
      "Federated Jira will not work for individual users until <code>OAUTH_CLIENT_ID</code> is set.");
  } else if (!signedIn) {
    setComposerLocked(true);
    setBanner("warn",
      "Sign in with Google to use the federated Jira connector. " +
      "Service-account mode is also available for non-Jira queries only.");
  } else if (cfg.jiraConsented === false) {
    setComposerLocked(false);
    setBanner("warn",
      `Signed in as <strong>${escapeHtml(cfg.user.email || "")}</strong>. ` +
      `Jira connector reports no active grant — click <strong>Connect Jira</strong> to consent.`);
  } else {
    setComposerLocked(false);
    setBanner("ok",
      `Signed in as <strong>${escapeHtml(cfg.user.email || "")}</strong>. ` +
      `Using user OAuth for streamAssist (user_pseudo_id=<code>${escapeHtml(cfg.user.user_pseudo_id || "?")}</code>).`);
  }
}

async function bootAuth() {
  // 1. Fetch server config
  let cfg;
  try {
    cfg = await fetch("/api/auth/config").then(r => r.json());
  } catch (e) {
    cfg = { configured: false, client_id: null, scopes: [] };
  }
  state.auth.configured = !!cfg.configured;
  state.auth.clientId = cfg.client_id || null;
  state.auth.scopes = cfg.scopes || [];

  // 2. Restore existing server-side session, if any
  try {
    const me = await fetch("/api/auth/me").then(r => r.json());
    if (me.signed_in) {
      state.auth.user = {
        email: me.email,
        name: me.name,
        picture: me.picture,
        user_pseudo_id: me.user_pseudo_id,
      };
    }
  } catch {}

  // 3. Initialise GIS token client if we have a client_id
  if (state.auth.configured && window.google?.accounts?.oauth2) {
    initTokenClient();
  } else if (state.auth.configured) {
    // GIS script may load slightly after us; poll briefly.
    const t0 = Date.now();
    const iv = setInterval(() => {
      if (window.google?.accounts?.oauth2 && window.google?.accounts?.id) {
        clearInterval(iv);
        initTokenClient();
        initIdClient();
      } else if (Date.now() - t0 > 8000) {
        clearInterval(iv);
        console.warn("Google Identity Services failed to load");
      }
    }, 150);
  }

  refreshUIForAuthState();
}

function initIdClient() {
  if (!state.auth.configured) return;
  if (!window.google?.accounts?.id) return;
  google.accounts.id.initialize({
    client_id: state.auth.clientId,
    callback: onCredentialResponse,
    auto_select: false,
  });
}

function initTokenClient() {
  if (!state.auth.configured) return;
  if (!window.google?.accounts?.oauth2) return;
  state.auth.tokenClient = google.accounts.oauth2.initTokenClient({
    client_id: state.auth.clientId,
    scope: "https://www.googleapis.com/auth/cloud-platform",
    callback: (resp) => {
      if (resp.error) {
        console.warn("token error", resp);
        toast(`Token error: ${resp.error}`, "error");
        return;
      }
      state.auth.accessToken = resp.access_token;
      state.auth.accessTokenExpiresAt = Date.now() + (resp.expires_in || 3000) * 1000;
      try { sessionStorage.setItem("ess_access_token", resp.access_token); } catch {}
    },
  });
}

async function onCredentialResponse(resp) {
  if (!resp?.credential) return;
  try {
    const verified = await fetch("/api/auth/verify", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ credential: resp.credential }),
    }).then(r => {
      if (!r.ok) throw new Error(`verify failed: ${r.status}`);
      return r.json();
    });
    state.auth.user = {
      email: verified.email,
      name: verified.name,
      picture: verified.picture,
      user_pseudo_id: verified.user_pseudo_id,
      sub: verified.sub,
    };
    refreshUIForAuthState();
    toast(`Signed in as ${verified.email}`, "ok");
    // Immediately request an access token in the same user gesture window.
    if (state.auth.tokenClient) {
      state.auth.tokenClient.requestAccessToken({ prompt: "" });
    }
  } catch (e) {
    toast(`Sign-in failed: ${e.message || e}`, "error");
  }
}

signinBtn.addEventListener("click", () => {
  if (!state.auth.configured) {
    toast("OAuth client is not configured on the server. See README.", "warn", 6000);
    return;
  }
  if (!window.google?.accounts?.id) {
    toast("Google Identity Services not loaded yet — try again in a moment.", "warn");
    return;
  }
  // Use the GIS One-Tap flow as a popup-equivalent: request via prompt().
  // initIdClient may not have run yet if GIS loaded after bootAuth() finished
  // its first pass — ensure it is initialised here.
  if (!window.__ess_id_inited) {
    initIdClient();
    window.__ess_id_inited = true;
  }
  google.accounts.id.prompt((notification) => {
    if (notification.isNotDisplayed?.() || notification.isSkippedMoment?.()) {
      // Fallback: render a button overlay? Just inform the user.
      const reason = notification.getNotDisplayedReason?.() || notification.getSkippedReason?.();
      toast(`Google prompt blocked (${reason || "unknown"}). Allow third-party cookies for accounts.google.com.`, "warn", 7000);
    }
  });
});

signoutBtn.addEventListener("click", async () => {
  try { await fetch("/api/auth/logout", { method: "POST" }); } catch {}
  state.auth.user = null;
  state.auth.accessToken = null;
  state.auth.accessTokenExpiresAt = 0;
  state.auth.jiraConsented = null;
  try { sessionStorage.removeItem("ess_access_token"); } catch {}
  if (window.google?.accounts?.id) {
    try { google.accounts.id.disableAutoSelect(); } catch {}
  }
  refreshUIForAuthState();
  toast("Signed out", "ok");
});

// Tracks the currently open consent popup so the popup-closed fallback
// poller can detect when the user finishes (or closes it manually).
let _jiraConsentPopup = null;
let _jiraConsentPoll = null;
let _jiraExchangeInFlight = false;

async function exchangeJiraCode(fullRedirectUrl) {
  if (_jiraExchangeInFlight) return;
  const tok = getAccessTokenSync();
  if (!tok) {
    toast("Sign in expired — sign in again then retry Connect Jira.", "error");
    return false;
  }
  _jiraExchangeInFlight = true;
  toast("Storing Jira grant…", "info", 3000);
  try {
    const r = await fetch("/api/jira/exchange", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${tok}`,
      },
      body: JSON.stringify({ fullRedirectUrl }),
    });
    const data = await r.json();
    if (r.ok && data.success) {
      state.auth.jiraConsented = true;
      refreshUIForAuthState();
      toast("Jira connected — ask away.", "ok", 6000);
      hideJiraRecovery();
      return true;
    }
    toast(`Jira exchange failed: ${data.error || r.status}`, "error", 8000);
    return false;
  } catch (e) {
    toast(`Jira exchange network error: ${e.message}`, "error", 8000);
    return false;
  } finally {
    _jiraExchangeInFlight = false;
  }
}

async function checkJiraConnection() {
  const tok = getAccessTokenSync();
  if (!tok) return false;
  try {
    const r = await fetch("/api/jira/check-connection", {
      headers: { "Authorization": `Bearer ${tok}` },
    });
    const data = await r.json();
    return !!data.connected;
  } catch {
    return false;
  }
}

function showJiraRecovery(authUrl) {
  let box = document.getElementById("jira-recovery");
  if (!box) {
    box = document.createElement("div");
    box.id = "jira-recovery";
    box.className = "jira-recovery";
    box.innerHTML = `
      <div class="jira-recovery-title">If the popup didn't connect automatically</div>
      <div class="jira-recovery-help">
        Copy the full URL from the popup's address bar after you finish signing in
        (it starts with <code>https://vertexaisearch.cloud.google.com/oauth-redirect?code=…</code>),
        then paste it here.
      </div>
      <div class="jira-recovery-row">
        <input id="jira-recovery-input" type="text" placeholder="https://vertexaisearch.cloud.google.com/oauth-redirect?code=…" />
        <button id="jira-recovery-submit" class="btn-primary">Finish connecting</button>
      </div>
      <div class="jira-recovery-row">
        <button id="jira-recovery-reopen" class="btn-ghost">Re-open Atlassian sign-in</button>
        <button id="jira-recovery-check" class="btn-ghost">I already connected — verify</button>
        <button id="jira-recovery-dismiss" class="btn-ghost">Dismiss</button>
      </div>`;
    const banner = document.getElementById("auth-banner");
    banner.parentNode.insertBefore(box, banner.nextSibling);
    document.getElementById("jira-recovery-submit").addEventListener("click", async () => {
      const v = document.getElementById("jira-recovery-input").value.trim();
      if (!v || !v.includes("code=")) {
        toast("Paste the full URL ending with ?code=…", "warn");
        return;
      }
      await exchangeJiraCode(v);
    });
    document.getElementById("jira-recovery-reopen").addEventListener("click", () => {
      const u = box.dataset.authUrl;
      if (u) window.open(u, "ge-jira-consent", "width=600,height=720,left=200,top=100");
    });
    document.getElementById("jira-recovery-check").addEventListener("click", async () => {
      toast("Checking grant on Gemini Enterprise…", "info");
      const ok = await checkJiraConnection();
      if (ok) {
        state.auth.jiraConsented = true;
        refreshUIForAuthState();
        toast("Jira connected — ask away.", "ok", 6000);
        hideJiraRecovery();
      } else {
        toast("No grant found yet. Paste the callback URL above to finish.", "warn", 8000);
      }
    });
    document.getElementById("jira-recovery-dismiss").addEventListener("click", hideJiraRecovery);
  }
  box.dataset.authUrl = authUrl || "";
  box.classList.remove("hidden");
}

function hideJiraRecovery() {
  const box = document.getElementById("jira-recovery");
  if (box) box.classList.add("hidden");
}

connectJiraBtn.addEventListener("click", async () => {
  if (!state.auth.user) return;
  let authUrl;
  try {
    const r = await fetch("/api/jira/auth-url").then(r => r.json());
    authUrl = r.auth_url;
  } catch {
    toast("Could not retrieve Jira auth URL", "error");
    return;
  }
  if (!authUrl) {
    toast("Backend returned no auth URL", "error");
    return;
  }
  _jiraConsentPopup = window.open(
    authUrl,
    "ge-jira-consent",
    "width=600,height=720,left=200,top=100"
  );
  if (!_jiraConsentPopup) {
    toast("Pop-up blocked. Allow pop-ups for this site and retry.", "warn");
    return;
  }
  toast("Complete the Atlassian sign-in in the popup…", "info", 8000);
  state.auth.jiraConsented = null;
  refreshUIForAuthState();
  showJiraRecovery(authUrl);

  // Background grant-watcher. COOP severs both window.opener AND popup.closed
  // for cross-origin popups, so we can't detect when the user finishes —
  // instead poll the backend every 2s for up to 90s and declare success
  // the first time acquireAccessToken returns a token. The grant lands
  // server-side via Google's /oauth-redirect page using the user's Google
  // session cookies, keyed by the same Google identity our bearer presents.
  if (_jiraConsentPoll) clearInterval(_jiraConsentPoll);
  const pollStart = Date.now();
  const pollMaxMs = 90_000;
  _jiraConsentPoll = setInterval(async () => {
    const elapsed = Date.now() - pollStart;
    if (elapsed > pollMaxMs) {
      clearInterval(_jiraConsentPoll);
      _jiraConsentPoll = null;
      toast("Still no grant after 90s. Re-open or paste the callback URL.", "warn", 8000);
      return;
    }
    if (await checkJiraConnection()) {
      clearInterval(_jiraConsentPoll);
      _jiraConsentPoll = null;
      state.auth.jiraConsented = true;
      refreshUIForAuthState();
      toast("Jira connected — ask away.", "ok", 6000);
      hideJiraRecovery();
      try { _jiraConsentPopup && _jiraConsentPopup.close(); } catch {}
      _jiraConsentPopup = null;
    }
  }, 2000);
});

// Listen for the postMessage from Google's vertexaisearch.cloud.google.com/
// oauth-redirect page. The payload shape is {fullRedirectUrl, code, state}.
// Frequently blocked by COOP; the popup-closed poller + manual paste cover the gap.
window.addEventListener("message", (ev) => {
  const d = ev.data || {};
  const url = typeof d.fullRedirectUrl === "string" ? d.fullRedirectUrl
            : typeof d.fullRedirectUri === "string" ? d.fullRedirectUri
            : null;
  if (url && url.includes("code=")) {
    exchangeJiraCode(url);
    try { _jiraConsentPopup && _jiraConsentPopup.close(); } catch {}
  }
});

// ---------- live access-token getter (with refresh-on-expiry) ----------
function getAccessTokenSync() {
  const a = state.auth;
  if (!a.user || !a.accessToken) return null;
  if (Date.now() > a.accessTokenExpiresAt - 30_000) {
    // Token near expiry — kick off a silent refresh, but caller still uses
    // the existing token for now (or null if it's already expired).
    if (a.tokenClient) {
      try { a.tokenClient.requestAccessToken({ prompt: "" }); } catch {}
    }
    if (Date.now() > a.accessTokenExpiresAt) return null;
  }
  return a.accessToken;
}

// Kick off bootstrap immediately
bootAuth();

// ---------- composer ----------
const input = $("#input");
const composer = $("#composer");

function autoSize() {
  input.style.height = "auto";
  input.style.height = Math.min(input.scrollHeight, 280) + "px";
}
input.addEventListener("input", autoSize);
input.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    composer.requestSubmit();
  }
});
composer.addEventListener("submit", (e) => {
  e.preventDefault();
  const q = input.value.trim();
  if (!q) return;
  input.value = "";
  autoSize();
  ask(q);
});

// ---------- chat rendering ----------
const messages = $("#messages");
const toBottomBtn = $("#to-bottom");

messages.addEventListener("scroll", () => {
  const near = messages.scrollHeight - messages.scrollTop - messages.clientHeight < 60;
  toBottomBtn.classList.toggle("hidden", near);
});
toBottomBtn.addEventListener("click", () => {
  messages.scrollTo({ top: messages.scrollHeight, behavior: "smooth" });
});

function scrollToBottom() {
  const near = messages.scrollHeight - messages.scrollTop - messages.clientHeight < 200;
  if (near) messages.scrollTop = messages.scrollHeight;
}

function addUserMessage(text) {
  const el = document.createElement("div");
  el.className = "msg user";
  el.textContent = text;
  messages.appendChild(el);
  state.transcript.push({ role: "user", text });
  scrollToBottom();
}

function startAssistMessage() {
  const el = document.createElement("div");
  el.className = "msg assist";
  const textEl = document.createElement("div");
  textEl.className = "md";
  const typing = document.createElement("div");
  typing.className = "typing";
  typing.innerHTML = "<span></span><span></span><span></span>";
  el.appendChild(typing);
  el.appendChild(textEl);
  const citationsEl = document.createElement("div");
  citationsEl.className = "citations";
  el.appendChild(citationsEl);
  messages.appendChild(el);
  state.currentAssist = { rootEl: el, textEl, typingEl: typing, citationsEl, buffer: "", citations: [] };
  scrollToBottom();
}

function appendAssistDelta(delta) {
  if (!state.currentAssist) startAssistMessage();
  state.currentAssist.buffer += delta;
  state.currentAssist.textEl.innerHTML = marked.parse(state.currentAssist.buffer);
  state.currentAssist.textEl.querySelectorAll("pre code").forEach((b) => {
    if (!b.dataset.hl) { hljs.highlightElement(b); b.dataset.hl = "1"; }
  });
  scrollToBottom();
}

function finalizeAssistMessage() {
  if (!state.currentAssist) return;
  state.currentAssist.typingEl?.remove();
  // citations
  const cits = state.currentAssist.citations;
  if (cits.length) {
    state.currentAssist.citationsEl.innerHTML = "";
    cits.forEach((c, i) => {
      const chip = document.createElement("span");
      chip.className = "citation";
      chip.title = `${c.title || ""}\n${c.uri || ""}`.trim();
      if (c.uri) {
        const a = document.createElement("a");
        a.href = c.uri; a.target = "_blank"; a.rel = "noreferrer";
        a.textContent = `[${i + 1}] ${shortHost(c.uri)}`;
        chip.appendChild(a);
      } else {
        chip.textContent = `[${i + 1}] ${c.title || "source"}`;
      }
      state.currentAssist.citationsEl.appendChild(chip);
    });
  }
  state.transcript.push({
    role: "assistant",
    text: state.currentAssist.buffer,
    citations: cits,
  });
  state.currentAssist = null;
}

function shortHost(u) {
  try { return new URL(u).hostname.replace(/^www\./, ""); } catch { return u; }
}

// ---------- inspector / REST events tab ----------
const eventsEl = $("#events");
const reasoningListEl = $("#reasoning-list");

document.querySelectorAll(".filters input[data-type]").forEach((cb) => {
  cb.addEventListener("change", () => {
    state.filters[cb.dataset.type] = cb.checked;
    rerenderEvents();
  });
});
$("#search").addEventListener("input", (e) => { state.search = e.target.value.toLowerCase(); rerenderEvents(); });
$("#newest-first").addEventListener("change", (e) => { state.newestFirst = e.target.checked; rerenderEvents(); });

function visibleEvents() {
  let list = state.events.filter((e) => state.filters[e.type] !== false);
  if (state.search) {
    list = list.filter((e) => JSON.stringify(e.payload).toLowerCase().includes(state.search));
  }
  return state.newestFirst ? [...list].reverse() : list;
}

function rerenderEvents() {
  eventsEl.innerHTML = "";
  visibleEvents().forEach(renderEvent);
}

function summarize(type, p) {
  if (type === "request") return `POST ${truncate(p.url, 60)}`;
  if (type === "chat") return JSON.stringify(p.delta).slice(0, 80);
  if (type === "raw") {
    const ans = p.chunk?.answer || {};
    const replies = ans.replies?.length || 0;
    const di = ans.diagnosticInfo;
    const ps = di?.plannerSteps?.length || 0;
    const state_ = ans.state || "—";
    return `state=${state_} replies=${replies}${ps ? ` plannerSteps=${ps}` : ""}`;
  }
  if (type === "done") return `events=${p.events} elapsed=${p.elapsed_ms}ms`;
  if (type === "trace") return p.trace_id ? `trace=${p.trace_id.slice(0,16)}… (${p.source})` : `no trace (${p.source})`;
  if (type === "auth_mode") return `mode=${p.mode}${p.email ? ` user=${p.email}` : ""}`;
  if (type === "error") return p.exception || `status=${p.status}`;
  return "";
}

function truncate(s, n) { return s && s.length > n ? s.slice(0, n - 1) + "…" : s; }

function renderEvent(ev) {
  const det = document.createElement("details");
  det.className = "event";
  det.dataset.type = ev.type;
  if (ev.type !== "raw") det.open = true;

  const sum = document.createElement("summary");
  sum.innerHTML = `
    <span class="tag">${ev.type}</span>
    <span class="meta">#${ev.seq ?? "—"} +${ev.t_ms ?? 0}ms</span>
    <span class="summary"></span>
    <span class="actions"></span>
  `;
  sum.querySelector(".summary").textContent = summarize(ev.type, ev.payload);

  // copy-as-curl on request
  if (ev.type === "request") {
    const btn = document.createElement("button");
    btn.className = "btn";
    btn.type = "button";
    btn.textContent = "Copy as cURL";
    btn.addEventListener("click", (e) => {
      e.preventDefault();
      const c = buildCurl(ev.payload);
      navigator.clipboard.writeText(c);
      btn.textContent = "Copied ✓";
      setTimeout(() => (btn.textContent = "Copy as cURL"), 1500);
    });
    sum.querySelector(".actions").appendChild(btn);
  }

  const pre = document.createElement("pre");
  const code = document.createElement("code");
  code.className = "language-json";
  code.textContent = JSON.stringify(ev.payload, null, 2);
  pre.appendChild(code);

  det.appendChild(sum);
  det.appendChild(pre);

  det.addEventListener("toggle", () => {
    if (det.open && !code.dataset.hl) {
      hljs.highlightElement(code);
      code.dataset.hl = "1";
    }
  });
  if (det.open) { hljs.highlightElement(code); code.dataset.hl = "1"; }

  eventsEl.appendChild(det);
  if (!state.newestFirst) eventsEl.scrollTop = eventsEl.scrollHeight;
}

function buildCurl(p) {
  const headers = Object.entries(p.headers || {})
    .map(([k, v]) => `  -H '${k}: ${k.toLowerCase() === "authorization" ? "Bearer $TOKEN" : v}' \\`)
    .join("\n");
  return `curl -N -X ${p.method} '${p.url}' \\\n${headers}\n  -d '${JSON.stringify(p.body)}'`;
}

// ---------- reasoning extraction ----------
function extractReasoning(chunk) {
  const ans = chunk?.answer;
  if (!ans) return;
  // function calls in planner steps
  const ps = ans.diagnosticInfo?.plannerSteps || [];
  for (const step of ps) {
    const parts = step.planStep?.parts || [];
    for (const part of parts) {
      const fc = part.functionCall;
      if (fc && !state._seenFCs?.has(fc.functionId)) {
        state._seenFCs ||= new Set();
        state._seenFCs.add(fc.functionId);
        const args = JSON.stringify(fc.args || {});
        addReasoning(
          `→ <span class="fn">${escapeHtml(fc.functionName)}</span>(<code>${escapeHtml(args).slice(0, 160)}</code>)`
        );
      }
    }
  }
  // citations / references in grounded content
  for (const reply of ans.replies || []) {
    const tgm = reply.groundedContent?.textGroundingMetadata;
    if (!tgm) continue;
    const refs = tgm.references || [];
    refs.forEach((r, idx) => {
      const m = r.documentMetadata || {};
      const key = m.uri || m.document;
      if (!key) return;
      state._seenRefs ||= new Set();
      if (state._seenRefs.has(key)) return;
      state._seenRefs.add(key);
      const title = m.title || m.uri || "(untitled)";
      addReasoning(
        `<span class="ref">grounded on</span> [${state._seenRefs.size}] <a href="${escapeAttr(m.uri || "#")}" target="_blank" rel="noreferrer">${escapeHtml(title)}</a>`
      );
      if (state.currentAssist) {
        state.currentAssist.citations.push({ title, uri: m.uri });
      }
    });
  }
}

function addReasoning(html) {
  const li = document.createElement("li");
  li.innerHTML = html;
  reasoningListEl.appendChild(li);
}

function escapeHtml(s) { return String(s).replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c])); }
function escapeAttr(s) { return escapeHtml(s).replace(/"/g, "&quot;"); }

// ---------- tabs ----------
const tabBtns = document.querySelectorAll(".tabs .tab");
const tabPanels = document.querySelectorAll(".tab-panel");

function switchTab(name) {
  state.activeTab = name;
  tabBtns.forEach((b) => b.classList.toggle("active", b.dataset.tab === name));
  tabPanels.forEach((p) => p.classList.toggle("active", p.dataset.panel === name));
  if (name === "logs") {
    state.logs.unread = 0;
    updateLogsBadge();
  } else if (name === "events") {
    state.eventsUnread = 0;
    updateEventsBadge();
  }
}
tabBtns.forEach((b) => b.addEventListener("click", () => switchTab(b.dataset.tab)));

function updateLogsBadge() {
  const el = $("#tab-badge-logs");
  if (state.activeTab !== "logs" && state.logs.unread > 0) {
    el.textContent = String(state.logs.unread);
    el.classList.remove("hidden");
  } else {
    el.classList.add("hidden");
  }
}
function updateEventsBadge() {
  const el = $("#tab-badge-events");
  if (state.activeTab !== "events" && state.eventsUnread > 0) {
    el.textContent = String(state.eventsUnread);
    el.classList.remove("hidden");
  } else {
    el.classList.add("hidden");
  }
}

// ---------- Cloud Logging tail tab ----------
const logEntriesEl = $("#log-entries");
const logFooterEl = $("#log-footer");
const logSkeleton = $("#logs-skeleton");
const logsStatus = $("#logs-status");
const logsTraceLine = $("#logs-trace-line");
const copyTraceBtn = $("#copy-trace");
const openExplorerLink = $("#open-explorer");

document.querySelectorAll(".filters input[data-logfilter]").forEach((cb) => {
  cb.addEventListener("change", () => {
    state.logs.filters[cb.dataset.logfilter] = cb.checked;
    rerenderLogs();
  });
});
$("#logs-search").addEventListener("input", (e) => {
  state.logs.search = e.target.value.toLowerCase();
  rerenderLogs();
});

copyTraceBtn.addEventListener("click", () => {
  if (!state.logs.traceId) return;
  navigator.clipboard.writeText(state.logs.traceId);
  copyTraceBtn.textContent = "Copied ✓";
  setTimeout(() => (copyTraceBtn.textContent = "Copy trace ID"), 1500);
});

function setLogsStatus(s, label) {
  state.logs.status = s;
  logsStatus.className = `counter-status ${s}`;
  logsStatus.textContent = label || s;
}

function updateLogsCounters() {
  const c = state.logs.counts;
  document.querySelector(".counter-pill.total").textContent = `${c.total} entries`;
  document.querySelector(".counter-pill.otel").textContent = `${c.otel} OTel`;
  document.querySelector(".counter-pill.audit").textContent = `${c.audit} audit`;
  document.querySelector(".counter-pill.other").textContent = `${c.other} other`;
}

function classifyEntry(e) {
  const ln = (e.logName || "").split("/").pop();
  if (ln.includes("gen_ai.user.message")) return { kind: "usermsg", group: "otel" };
  if (ln.includes("gen_ai.choice")) return { kind: "choice", group: "otel" };
  if (ln.includes("gen_ai")) return { kind: "usermsg", group: "otel" };
  if (ln.includes("gemini_enterprise_user_activity")) return { kind: "activity", group: "audit" };
  return { kind: "other", group: "other" };
}

function entryMatchesFilters(e, cls) {
  const f = state.logs.filters;
  if (cls.group === "audit" && !f.audit) return false;
  if (cls.kind === "usermsg" && !f["user.message"]) return false;
  if (cls.kind === "choice" && !f.choice) return false;
  if (f.function_call) {
    const has = JSON.stringify(e.payload || {}).includes("\"function_call\"")
              || JSON.stringify(e.payload || {}).includes("\"functionCall\"");
    if (!has) return false;
  }
  if (state.logs.search) {
    if (!JSON.stringify(e).toLowerCase().includes(state.logs.search)) return false;
  }
  return true;
}

function fmtTs(iso) {
  if (!iso) return "—";
  try {
    const d = new Date(iso);
    return d.toISOString().slice(11, 23); // HH:MM:SS.mmm
  } catch { return iso; }
}

function findFunctionCallSnippet(payload) {
  // Walk content.parts for function_call / functionCall
  const c = payload?.content;
  const parts = c?.parts || [];
  for (const p of parts) {
    const fc = p.function_call || p.functionCall;
    if (fc) {
      const name = fc.name || fc.functionName || "fn";
      let args = fc.args || fc.arguments || {};
      if (typeof args !== "string") args = JSON.stringify(args);
      return `→ tool: ${name}(${args.slice(0, 120)}${args.length > 120 ? "…" : ""})`;
    }
  }
  return null;
}

function firstTextSnippet(payload) {
  const c = payload?.content;
  const parts = c?.parts || [];
  for (const p of parts) {
    if (typeof p.text === "string" && p.text.trim()) {
      return p.text.trim().slice(0, 80);
    }
  }
  return null;
}

function renderLogEntry(e) {
  const cls = classifyEntry(e);
  const det = document.createElement("details");
  det.className = `log-entry kind-${cls.kind}`;
  det.dataset.insert = e.insertId || "";
  // detect function_call to highlight border
  const fcSnippet = findFunctionCallSnippet(e.payload);
  if (fcSnippet) det.classList.add("has-fc");

  const sum = document.createElement("summary");

  const tEl = document.createElement("span");
  tEl.className = "log-time";
  tEl.textContent = fmtTs(e.timestamp);

  const nEl = document.createElement("span");
  nEl.className = "log-event-name";
  nEl.textContent = e.eventName || "entry";

  const metaEl = document.createElement("span");
  metaEl.className = "log-meta-bits";
  const bits = [];
  if (e.role) bits.push(`<span class="pill">role=${escapeHtml(e.role)}</span>`);
  if (e.methodName) bits.push(`<span class="pill">${escapeHtml(e.methodName)}</span>`);
  metaEl.innerHTML = bits.join("");

  const snipEl = document.createElement("span");
  snipEl.className = "log-snippet";
  if (fcSnippet) {
    snipEl.classList.add("fc");
    snipEl.textContent = fcSnippet;
  } else {
    const t = firstTextSnippet(e.payload);
    if (t) snipEl.textContent = t;
  }

  sum.appendChild(tEl);
  sum.appendChild(nEl);
  sum.appendChild(snipEl);
  sum.appendChild(metaEl);

  const pre = document.createElement("pre");
  const code = document.createElement("code");
  code.className = "language-json";
  code.textContent = JSON.stringify(e.payload, null, 2);
  pre.appendChild(code);

  det.appendChild(sum);
  det.appendChild(pre);

  det.addEventListener("toggle", () => {
    if (det.open && !code.dataset.hl) {
      hljs.highlightElement(code);
      code.dataset.hl = "1";
    }
  });
  return det;
}

function appendLogEntry(e) {
  if (!entryMatchesFilters(e, classifyEntry(e))) return;
  // Maintain timestamp asc order. Since server feeds ascending, simple append.
  const det = renderLogEntry(e);
  logEntriesEl.appendChild(det);
  // auto-scroll only if user is near the bottom of the panel
  const panel = logEntriesEl;
  const near = panel.scrollHeight - panel.scrollTop - panel.clientHeight < 200;
  if (near) panel.scrollTop = panel.scrollHeight;
}

function rerenderLogs() {
  logEntriesEl.innerHTML = "";
  const list = [...state.logs.entries].sort(
    (a, b) => (a.timestamp || "").localeCompare(b.timestamp || "")
  );
  for (const e of list) {
    if (entryMatchesFilters(e, classifyEntry(e))) {
      logEntriesEl.appendChild(renderLogEntry(e));
    }
  }
}

function handleLogEntry(e) {
  if (!e.insertId || state.logs.byInsert.has(e.insertId)) return;
  state.logs.byInsert.add(e.insertId);
  state.logs.entries.push(e);
  const cls = classifyEntry(e);
  state.logs.counts.total++;
  state.logs.counts[cls.group]++;
  updateLogsCounters();
  appendLogEntry(e);
  if (state.activeTab !== "logs") {
    state.logs.unread++;
    updateLogsBadge();
  }
  // hide skeleton on first entry
  logSkeleton.classList.add("hidden");
  setLogsStatus("live", "live · polling");
}

function openLogsStream(traceId, project) {
  closeLogsStream();
  state.logs.traceId = traceId;
  state.logs.project = project;
  state.logs.entries = [];
  state.logs.byInsert = new Set();
  state.logs.counts = { total: 0, otel: 0, audit: 0, other: 0 };
  state.logs.startedAt = performance.now();
  state.logs.unread = 0;
  logEntriesEl.innerHTML = "";
  logFooterEl.classList.add("hidden");
  logFooterEl.textContent = "";
  updateLogsCounters();

  logsTraceLine.textContent = `trace=${traceId} · project=${project}`;
  copyTraceBtn.disabled = false;
  // Logs Explorer deep link
  const flt = `trace="${traceId}"\n(logName="projects/${project}/logs/discoveryengine.googleapis.com%2Fgemini_enterprise_user_activity" OR logName=~"discoveryengine.googleapis.com%2Fgen_ai")`;
  const url = `https://console.cloud.google.com/logs/query;query=${encodeURIComponent(flt)}?project=${project}`;
  openExplorerLink.href = url;
  openExplorerLink.classList.remove("disabled");

  setLogsStatus("waiting", "waiting for first entry…");
  logSkeleton.classList.remove("hidden");

  const es = new EventSource(`/api/logs/${encodeURIComponent(traceId)}`);
  state.logs.es = es;
  es.addEventListener("log_meta", () => {});
  es.addEventListener("log_entry", (ev) => {
    try { handleLogEntry(JSON.parse(ev.data)); } catch {}
  });
  es.addEventListener("log_tick", () => {});
  es.addEventListener("log_done", (ev) => {
    let data = {};
    try { data = JSON.parse(ev.data); } catch {}
    setLogsStatus("done", `closed · ${data.reason || "done"}`);
    logFooterEl.classList.remove("hidden");
    logFooterEl.textContent = `Tail closed — ${data.entries ?? state.logs.counts.total} entries total over ${data.elapsed_s ?? "?"}s (${data.reason || "done"})`;
    logSkeleton.classList.add("hidden");
    closeLogsStream();
  });
  es.addEventListener("log_error", (ev) => {
    let data = {};
    try { data = JSON.parse(ev.data); } catch {}
    setLogsStatus("error", "error");
    logSkeleton.classList.add("hidden");
    const card = document.createElement("div");
    card.className = "log-entry kind-other";
    card.innerHTML = `<summary><span class="log-time">${fmtTs(new Date().toISOString())}</span><span class="log-event-name" style="color:var(--red)">log_error</span><span class="log-snippet">${escapeHtml(data.message || "unknown")}</span><span></span></summary>`;
    logEntriesEl.appendChild(card);
  });
  es.onerror = () => {
    // server closed normally after log_done; only flag if we haven't already.
    if (state.logs.status !== "done") {
      setLogsStatus("done", "connection closed");
    }
    closeLogsStream();
  };
}

function closeLogsStream() {
  if (state.logs.es) {
    try { state.logs.es.close(); } catch {}
    state.logs.es = null;
  }
}

// ---------- SSE / fetch streaming for /api/assist ----------
async function ask(question) {
  state.startedAt = performance.now();
  addUserMessage(question);
  startAssistMessage();

  // Auto-open the logs tab + show skeleton.
  switchTab("logs");
  closeLogsStream();
  state.logs.entries = [];
  state.logs.byInsert = new Set();
  state.logs.counts = { total: 0, otel: 0, audit: 0, other: 0 };
  state.logs.traceId = null;
  logEntriesEl.innerHTML = "";
  logFooterEl.classList.add("hidden");
  updateLogsCounters();
  copyTraceBtn.disabled = true;
  openExplorerLink.classList.add("disabled");
  logsTraceLine.textContent = "waiting for trace ID from streamAssist…";
  setLogsStatus("waiting", "awaiting trace…");
  logSkeleton.classList.remove("hidden");

  let resp;
  try {
    const headers = { "content-type": "application/json" };
    const at = getAccessTokenSync();
    if (at) headers["Authorization"] = `Bearer ${at}`;
    resp = await fetch("/api/assist", {
      method: "POST",
      headers,
      body: JSON.stringify({
        question,
        session: state.sessionId,
        include_thoughts: $("#thoughts").checked,
      }),
    });
  } catch (e) {
    pushEvent({ type: "error", payload: { exception: String(e) }, t_ms: 0 });
    return;
  }
  if (!resp.ok || !resp.body) {
    pushEvent({ type: "error", payload: { status: resp.status }, t_ms: 0 });
    return;
  }

  const reader = resp.body.getReader();
  const decoder = new TextDecoder();
  let buf = "";
  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buf += decoder.decode(value, { stream: true });
    let nl;
    while ((nl = buf.indexOf("\n\n")) !== -1) {
      const raw = buf.slice(0, nl);
      buf = buf.slice(nl + 2);
      handleSSEFrame(raw);
    }
  }
  finalizeAssistMessage();
}

function handleSSEFrame(raw) {
  let event = "message";
  const dataLines = [];
  for (const line of raw.split("\n")) {
    if (line.startsWith("event:")) event = line.slice(6).trim();
    else if (line.startsWith("data:")) dataLines.push(line.slice(5).replace(/^ /, ""));
  }
  if (!dataLines.length) return;
  let payload;
  try { payload = JSON.parse(dataLines.join("\n")); } catch { payload = { raw: dataLines.join("\n") }; }

  pushEvent({ type: event, payload, t_ms: payload.t_ms ?? Math.round(performance.now() - state.startedAt), seq: payload.seq });

  if (event === "chat" && payload.delta) {
    appendAssistDelta(payload.delta);
  }
  if (event === "raw") {
    extractReasoning(payload.chunk);
  }
  if (event === "trace") {
    if (payload.trace_id) {
      openLogsStream(payload.trace_id, payload.project || "vtxdemos");
    } else {
      setLogsStatus("error", payload.source || "no trace");
      logSkeleton.classList.add("hidden");
      logsTraceLine.textContent = payload.note || "no trace available for this call";
    }
  }
  if (event === "auth_mode") {
    if (payload.mode === "service_account" && state.auth.user) {
      toast("Sent as SA — your OAuth token wasn't attached. Try signing in again.", "warn", 6000);
    }
  }
  if (event === "error") {
    appendAssistDelta(`\n\n_⚠ error: ${payload.exception || payload.status || "unknown"}_`);
    // Heuristic: if the streamAssist body mentions Jira not being active /
    // not consented / no grant / etc., flag the Connect Jira button.
    const body = String(payload.body || payload.exception || "").toLowerCase();
    if (state.auth.user && (
      body.includes("not active") ||
      body.includes("not consented") ||
      body.includes("no grant") ||
      body.includes("not authorized") ||
      body.includes("oauth") ||
      body.includes("3lo") ||
      body.includes("jira")
    )) {
      state.auth.jiraConsented = false;
      refreshUIForAuthState();
    }
  }
}

function pushEvent(ev) {
  ev.id = state.events.length;
  ev.ts = Date.now();
  state.events.push(ev);
  if (state.activeTab !== "events") {
    state.eventsUnread++;
    updateEventsBadge();
  }
  // render only if it passes filters
  if (state.filters[ev.type] === false) return;
  if (state.search && !JSON.stringify(ev.payload).toLowerCase().includes(state.search)) return;
  renderEvent(ev);
}

// ---------- clear / export ----------
$("#clear-btn").addEventListener("click", () => {
  state.events = []; state.transcript = []; state.reasoning = [];
  state._seenFCs = new Set(); state._seenRefs = new Set();
  messages.innerHTML = ""; eventsEl.innerHTML = ""; reasoningListEl.innerHTML = "";
  // also clear logs tab
  closeLogsStream();
  state.logs.entries = []; state.logs.byInsert = new Set();
  state.logs.counts = { total: 0, otel: 0, audit: 0, other: 0 };
  state.logs.traceId = null;
  logEntriesEl.innerHTML = ""; logFooterEl.classList.add("hidden");
  copyTraceBtn.disabled = true; openExplorerLink.classList.add("disabled");
  logsTraceLine.textContent = "waiting for a streamAssist call…";
  setLogsStatus("idle", "idle");
  logSkeleton.classList.add("hidden");
  updateLogsCounters();
});
$("#export-btn").addEventListener("click", () => {
  const blob = new Blob([JSON.stringify({
    sessionId: state.sessionId,
    engine: state.engine,
    transcript: state.transcript,
    events: state.events,
    logEntries: state.logs.entries,
    traceId: state.logs.traceId,
    exportedAt: new Date().toISOString(),
  }, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `streamassist-${state.sessionId}.json`;
  a.click();
  URL.revokeObjectURL(url);
});

// ---------- splitter ----------
const splitter = $("#splitter");
const chatPane = document.querySelector(".chat-pane");
let dragging = false;
splitter.addEventListener("mousedown", (e) => { dragging = true; e.preventDefault(); document.body.style.cursor = "col-resize"; });
window.addEventListener("mousemove", (e) => {
  if (!dragging) return;
  const split = document.getElementById("split");
  const rect = split.getBoundingClientRect();
  const pct = ((e.clientX - rect.left) / rect.width) * 100;
  chatPane.style.flex = `0 0 ${Math.min(85, Math.max(25, pct))}%`;
});
window.addEventListener("mouseup", () => { dragging = false; document.body.style.cursor = ""; });

autoSize();
updateLogsCounters();
