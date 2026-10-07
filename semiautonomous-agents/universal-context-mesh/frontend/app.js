/* ============================================================================
   UNIVERSAL CONTEXT MESH — FRONTEND CONTROLLER (`app.js`)
   ============================================================================ */

const API_BASE = window.location.port === "5173" ? "http://localhost:8010" : "";
const WS_BASE =
  window.location.port === "5173"
    ? "ws://localhost:8010/ws/telemetry"
    : `${window.location.protocol === "https:" ? "wss:" : "ws:"}//${window.location.host}/ws/telemetry`;

let activeUserId = "carlos@restaurant.io";
let activeTargetAgent = "orchestrator_agent";
let activeSessionId = "session-orchestrator_agent-main";
let universalContextData = null;
let runtimeHealthData = null;
let telemetryEvents = [];
let wsConnection = null;

function isRestaurantUser(userId) {
  return (userId || "").toLowerCase().includes("carlos") || (userId || "").toLowerCase().includes("restaurant");
}

function getAgentFriendlyName(agentName, userId) {
  if (isRestaurantUser(userId)) {
    if (agentName === "wealth_agent" || agentName === "ordering_agent") return "🍕 Ordering & Menu Agent (Session #1)";
    if (agentName === "legal_tax_agent" || agentName === "delivery_agent") return "🛵 Delivery & Driver Agent (Session #2)";
    if (agentName === "mobility_agent" || agentName === "support_agent") return "🛎️ Kitchen & VIP Support (Session #3)";
    if (agentName === "orchestrator_agent") return "🌐 Universal Orchestrator Hub";
  } else {
    if (agentName === "wealth_agent") return "💼 Wealth & Portfolio Agent (Session #1)";
    if (agentName === "legal_tax_agent") return "⚖️ Legal & Tax Compliance Agent (Session #2)";
    if (agentName === "mobility_agent") return "✈️ Global Mobility Concierge (Session #3)";
    if (agentName === "orchestrator_agent") return "🌐 Universal Orchestrator Hub";
  }
  return agentName;
}

function updateDomainUI(userId) {
  const isRest = isRestaurantUser(userId);
  const p1 = document.getElementById("pillLabel1");
  const p2 = document.getElementById("pillLabel2");
  const p3 = document.getElementById("pillLabel3");
  if (p1) p1.textContent = isRest ? "ORDERING A2A :8011" : "WEALTH A2A :8011";
  if (p2) p2.textContent = isRest ? "DELIVERY A2A :8012" : "LEGAL A2A :8012";
  if (p3) p3.textContent = isRest ? "SUPPORT A2A :8013" : "MOBILITY A2A :8013";

  const cn1 = document.getElementById("cardName1");
  const cs1 = document.getElementById("cardSub1");
  const cn2 = document.getElementById("cardName2");
  const cs2 = document.getElementById("cardSub2");
  const cn3 = document.getElementById("cardName3");
  const cs3 = document.getElementById("cardSub3");
  const cs0 = document.getElementById("cardSub0");
  const rDesc = document.getElementById("roundtableDesc");
  const chips = document.getElementById("scenarioChipsContainer");

  if (isRest) {
    if (cs0) cs0.textContent = "Coordinates Ordering, Delivery & Support agents via A2A JSON-RPC 2.0";
    if (cn1) cn1.textContent = "🍕 Ordering & Menu Agent";
    if (cs1) cs1.textContent = "Session #1: Takes food orders & allergies -> Updates `user:active_order`";
    if (cn2) cn2.textContent = "🛵 Delivery & Driver Agent";
    if (cs2) cs2.textContent = "Session #2 (Separate!): Automatically knows items ordered in Session #1!";
    if (cn3) cn3.textContent = "🛎️ Kitchen & VIP Support";
    if (cs3) cs3.textContent = "Session #3 (Separate!): Verifies allergy prep (Sess #1) & gate code (Sess #2)";
    if (rDesc)
      rDesc.textContent =
        "Watch Ordering Agent (Session #1), Delivery Agent (Session #2), and VIP Support (Session #3) collaborate in real time—automatically sharing order items & gate codes across separate sessions!";
    if (chips) {
      chips.innerHTML = `
        <button class="scenario-chip" onclick="runQuickScenario('wealth_agent', 'Hi! I am Carlos. Please place a brand new order #ORD-5500: 3x Birria Tacos ($18) and 1x Horchata ($5) for delivery to 1600 Amphitheatre Pkwy, Mountain View. Note: severe peanut allergy!')">
          <span class="scenario-chip-badge">STEP 1 → ORDERING AGENT (SESSION #1)</span>
          "Place brand-new Order #ORD-5500: 3x Birria Tacos & Horchata to 1600 Amphitheatre Pkwy..."
        </button>
        <button class="scenario-chip" onclick="runQuickScenario('legal_tax_agent', 'Hey Delivery Agent! In this separate session, without me repeating my order, what items do you see in my active order right now, and can you check Google Maps for the live delivery route, traffic conditions, and exact ETA to my address?')">
          <span class="scenario-chip-badge">STEP 2 → DELIVERY AGENT + GOOGLE MAPS ETA (SESSION #2)</span>
          "Check Google Maps for live route, traffic & exact ETA for my order!"
        </button>
        <button class="scenario-chip" onclick="runQuickScenario('mobility_agent', 'Hi Support! Can you confirm that the kitchen saw my peanut allergy from Ordering Session #1 and check the latest Google Maps ETA from Delivery Session #2?')">
          <span class="scenario-chip-badge">STEP 3 → VIP SUPPORT (SESSION #3 - DIFFERENT SESSION!)</span>
          "Confirm kitchen saw my peanut allergy (Sess #1) & check Google Maps ETA (Sess #2)."
        </button>
      `;
    }
  } else {
    if (cs0) cs0.textContent = "Coordinates Wealth, Legal & Mobility agents via A2A JSON-RPC 2.0";
    if (cn1) cn1.textContent = "Wealth & Portfolio Agent";
    if (cs1) cs1.textContent = "Direct session: Updates `user:financial_profile` & `portfolio_analysis.md`";
    if (cn2) cn2.textContent = "Legal & Tax Compliance Agent";
    if (cs2) cs2.textContent = "Direct session: Reads wealth/mobility context & updates `user:legal_tax_status`";
    if (cn3) cn3.textContent = "Global Mobility Concierge";
    if (cs3) cs3.textContent = "Direct session: Aligns Permit B / visas with legal rules & wealth budget";
    if (rDesc)
      rDesc.textContent =
        "Watch 3 specialized A2A agents & the Orchestrator interact in real time across separate sessions—automatically inheriting each other's newly discovered memories & `user:*` state!";
    if (chips) {
      chips.innerHTML = `
        <button class="scenario-chip" onclick="runQuickScenario('wealth_agent', 'I just sold an additional $3.8M in AI secondary shares (total liquid net worth now $18.3M) and want to allocate $4.5M into Swiss Francs (CHF).')">
          <span class="scenario-chip-badge">STEP A → WEALTH AGENT (SESSION 1)</span>
          "I just sold $3.8M in shares (net worth $18.3M) & want $4.5M in CHF..."
        </button>
        <button class="scenario-chip" onclick="runQuickScenario('legal_tax_agent', 'Without me repeating my financial numbers, what are my California exit tax & Swiss Lump-Sum treaty obligations given my latest liquidity update?')">
          <span class="scenario-chip-badge">STEP B → LEGAL AGENT (SESSION 2 - INHERITS STEP A!)</span>
          "Without repeating my numbers, what are my tax rules for my latest liquidity?"
        </button>
        <button class="scenario-chip" onclick="runQuickScenario('mobility_agent', 'Based on the updated CHF budget from Wealth and tax treaty structure from Legal, create my Q1 2027 Zurich Permit B family relocation roadmap.')">
          <span class="scenario-chip-badge">STEP C → MOBILITY AGENT (SESSION 3 - INHERITS A & B!)</span>
          "Using my Wealth CHF budget & Legal structure, build my Zurich visa roadmap."
        </button>
      `;
    }
  }
}

// ----------------------------------------------------------------------------
// 1. THEME TOGGLE (LIGHT DEFAULT + DYNAMIC DARK MODE)
// ----------------------------------------------------------------------------
function toggleTheme() {
  const html = document.documentElement;
  const current = html.getAttribute("data-theme") || "light";
  const next = current === "light" ? "dark" : "light";
  html.setAttribute("data-theme", next);
  const btn = document.getElementById("themeToggleBtn");
  if (btn) {
    btn.textContent = next === "light" ? "🌙 Dark" : "☀️ Light";
  }
}

// ----------------------------------------------------------------------------
// 2. INITIALIZATION & WEBSOCKET CONNECTION
// ----------------------------------------------------------------------------
window.addEventListener("DOMContentLoaded", async () => {
  updateDomainUI(activeUserId);
  await checkRuntimeHealth();
  await loadUserUniversalContext(activeUserId);
  connectWebSocketTelemetry();
});

async function checkRuntimeHealth() {
  try {
    const resp = await fetch(`${API_BASE}/api/health`);
    if (resp.ok) {
      runtimeHealthData = await resp.json();
    }
  } catch (err) {
    console.warn("Health check warning:", err);
  }
}

let liveThinkingState = {
  active: false,
  agent: "",
  sessionId: "",
  startTime: 0,
  steps: [],
  timerInterval: null,
};

function startLiveThinking(agentName, sessionId) {
  if (liveThinkingState.timerInterval) clearInterval(liveThinkingState.timerInterval);
  liveThinkingState.active = true;
  liveThinkingState.agent = agentName;
  liveThinkingState.sessionId = sessionId;
  liveThinkingState.startTime = Date.now();
  liveThinkingState.steps = [
    {
      elapsed_sec: 0.0,
      title: "Universal Context Mesh Lookup",
      detail: `Fetching shared 'user:*' state & Cross-Agent Memory Bank for ${activeUserId}...`,
    },
  ];
  liveThinkingState.timerInterval = setInterval(() => {
    const timerEl = document.getElementById("liveThinkingTimer");
    if (timerEl && liveThinkingState.active) {
      const elapsed = ((Date.now() - liveThinkingState.startTime) / 1000).toFixed(1);
      timerEl.textContent = `${elapsed}s`;
    }
  }, 100);
}

function appendLiveReasoningStep(title, detail, elapsedSec = null) {
  if (!liveThinkingState.active) return;
  const elapsed =
    elapsedSec !== null
      ? Number(elapsedSec).toFixed(1)
      : ((Date.now() - liveThinkingState.startTime) / 1000).toFixed(1);
  liveThinkingState.steps.push({
    elapsed_sec: elapsed,
    title: title,
    detail: detail,
  });
  setLoaderState(true, `✳ ${title}...`, detail);
  renderActiveSessionMessages();
}

function stopLiveThinking() {
  if (liveThinkingState.timerInterval) clearInterval(liveThinkingState.timerInterval);
  liveThinkingState.active = false;
  liveThinkingState.timerInterval = null;
}

function toggleReasoningBox(boxId) {
  const el = document.getElementById(boxId);
  if (el) {
    el.classList.toggle("expanded");
  }
}

function connectWebSocketTelemetry() {
  const badge = document.getElementById("wsStatusBadge");
  try {
    wsConnection = new WebSocket(WS_BASE);
    wsConnection.onopen = () => {
      if (badge) badge.textContent = "WS: LIVE";
    };
    wsConnection.onmessage = async (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === "INITIAL_LOG" && Array.isArray(data.events)) {
          telemetryEvents = data.events.reverse();
          renderTelemetryStream();
        } else if (data.type === "LIVE_EVENT" && data.event) {
          telemetryEvents.unshift(data.event);
          if (telemetryEvents.length > 150) telemetryEvents.pop();
          renderTelemetryStream();
          pulseTopologyNode(data.event);

          const ev = data.event;
          // Stream live reasoning steps into the Claude-Code thinking box!
          if (ev.event_type === "REASONING_STEP") {
            appendLiveReasoningStep(ev.title || "Reasoning", ev.summary || "", ev.elapsed_sec);
          } else if (ev.event_type === "ROUNDTABLE_STEP") {
            appendLiveReasoningStep(ev.title, ev.summary);
          } else if (ev.event_type === "CONTEXT_WRITE" && liveThinkingState.active) {
            appendLiveReasoningStep(
              `Synchronized ${ev.namespace || "user:*"}`,
              ev.summary || `Updated ${ev.namespace} across Universal Mesh`
            );
          } else if (ev.event_type === "MEMORY_ADDED" && liveThinkingState.active) {
            appendLiveReasoningStep(
              "Memory Bank Commit",
              ev.summary || `Saved new semantic fact to shared Memory Bank`
            );
          }

          // Refresh right panel context automatically on write/memory/artifact events
          if (
            ["CONTEXT_WRITE", "MEMORY_ADDED", "ARTIFACT_SAVED", "ROUNDTABLE_COMPLETE"].includes(
              ev.event_type
            )
          ) {
            await loadUserUniversalContext(activeUserId, false);
          }
        }
      } catch (e) {
        console.error("WS parse error:", e);
      }
    };
    wsConnection.onclose = () => {
      if (badge) badge.textContent = "WS: RECONNECTING";
      setTimeout(connectWebSocketTelemetry, 3000);
    };
  } catch (err) {
    console.warn("WebSocket error:", err);
  }
}

function pulseTopologyNode(evt) {
  const agent = evt.source_agent || evt.target_agent || evt.agent || evt.source;
  if (agent) {
    const node = document.getElementById(`meshNode-${agent}`);
    if (node) {
      node.classList.add("pulsing");
      setTimeout(() => node.classList.remove("pulsing"), 1200);
    }
  }
  const hub = document.getElementById("hubNodeBox");
  if (hub) {
    hub.style.transform = "scale(1.015)";
    setTimeout(() => (hub.style.transform = "scale(1)"), 400);
  }
}

// ----------------------------------------------------------------------------
// 3. LOAD & RENDER UNIVERSAL CONTEXT
// ----------------------------------------------------------------------------
async function loadUserUniversalContext(userId, renderChat = true) {
  try {
    const resp = await fetch(`${API_BASE}/api/users/${encodeURIComponent(userId)}/context`);
    if (!resp.ok) return;
    universalContextData = await resp.json();
    renderRightInspector();
    if (renderChat) {
      renderActiveSessionMessages();
    }
  } catch (err) {
    console.error("Failed to load context:", err);
  }
}

function renderRightInspector() {
  if (!universalContextData) return;

  // 1. Memories
  const memories = universalContextData.memories || [];
  document.getElementById("memCountBadge").textContent = memories.length;
  const memContainer = document.getElementById("memoriesListContainer");
  memContainer.innerHTML = memories
    .map(
      (m) => `
      <div class="context-card">
        <div class="context-card-header">
          <span class="context-card-title">${escapeHtml(m.source_agent || "agent")}</span>
          <span class="context-card-badge">${escapeHtml(m.category || "fact")} · ${escapeHtml(
            (m.session_id || "").slice(0, 16)
          )}</span>
        </div>
        <div style="font-size: 12px; line-height: 1.45; margin-bottom: 6px;">
          ${escapeHtml(m.fact)}
        </div>
        <div style="display: flex; justify-content: space-between; align-items: center; font-family: var(--font-mono); font-size: 10px; color: var(--text-secondary);">
          <span>${formatTime(m.timestamp)}</span>
          <button class="btn btn-secondary btn-mono" style="padding: 2px 6px; font-size: 9px;" onclick="deleteMemory('${
            m.memory_id
          }')">DELETE</button>
        </div>
      </div>
    `
    )
    .join("");

  // 2. Universal State (`user:*`)
  const state = universalContextData.universal_state || {};
  const stateContainer = document.getElementById("universalStateContainer");
  stateContainer.innerHTML = Object.entries(state)
    .map(
      ([nsKey, val]) => `
      <div class="context-card">
        <div class="context-card-header">
          <span class="context-card-title">${escapeHtml(nsKey)}</span>
          <span class="context-card-badge">UNIVERSAL NAMESPACE</span>
        </div>
        <pre class="json-pre">${escapeHtml(JSON.stringify(val, null, 2))}</pre>
      </div>
    `
    )
    .join("");

  // Mutation History
  const mutations = universalContextData.mutation_history || [];
  const mutContainer = document.getElementById("mutationHistoryContainer");
  if (mutations.length === 0) {
    mutContainer.innerHTML = `<div style="font-size:11px; color:var(--text-secondary);">No mutations recorded yet in this session.</div>`;
  } else {
    mutContainer.innerHTML = mutations
      .slice(0, 10)
      .map(
        (mut) => `
        <div class="context-card">
          <div class="context-card-header">
            <span class="context-card-title">${escapeHtml(mut.source_agent)} → ${escapeHtml(
              mut.namespace_key
            )}</span>
            <span class="context-card-badge">${formatTime(mut.timestamp)}</span>
          </div>
          <div style="font-family: var(--font-mono); font-size: 10px; color: var(--text-secondary); margin-bottom: 4px;">
            Fields mutated: ${escapeHtml((mut.updated_fields || []).join(", "))}
          </div>
        </div>
      `
      )
      .join("");
  }

  // 3. Shared Artifacts
  const artifacts = universalContextData.artifacts || [];
  document.getElementById("artCountBadge").textContent = artifacts.length;
  const artContainer = document.getElementById("artifactsListContainer");
  artContainer.innerHTML = artifacts
    .map(
      (a, idx) => `
      <div class="context-card" style="cursor: pointer;" onclick="inspectArtifact(${idx})">
        <div class="context-card-header">
          <span class="context-card-title">📄 ${escapeHtml(a.filename)}</span>
          <span class="context-card-badge">v${a.version} · ${escapeHtml(a.created_by_agent)}</span>
        </div>
        <div style="font-size: 12px; font-weight: 600; margin-bottom: 4px;">
          ${escapeHtml(a.title)}
        </div>
        <div style="font-family: var(--font-mono); font-size: 10px; color: var(--text-secondary);">
          Scope: ${escapeHtml(a.scope)} · Click to view & download Markdown
        </div>
      </div>
    `
    )
    .join("");
}

// ----------------------------------------------------------------------------
// 4. CHAT & SESSION MANAGEMENT
// ----------------------------------------------------------------------------
function selectTargetAgent(agentName) {
  activeTargetAgent = agentName;
  activeSessionId = `session-${agentName}-interactive`;

  document.querySelectorAll(".agent-card-btn").forEach((btn) => {
    btn.classList.toggle("active", btn.getAttribute("data-agent") === agentName);
  });

  renderActiveSessionMessages();
}

function renderActiveSessionMessages() {
  const listEl = document.getElementById("chatMessagesList");
  if (!universalContextData || !universalContextData.sessions) {
    listEl.innerHTML = "";
    return;
  }

  // Gather messages for activeSessionId OR show welcome banner explaining cross-session context sharing
  const sess = universalContextData.sessions[activeSessionId];
  const messages = sess ? sess.messages || [] : [];

  if (messages.length === 0) {
    const friendlyName = getAgentFriendlyName(activeTargetAgent, activeUserId);
    listEl.innerHTML = `
      <div class="msg-card agent" style="max-width: 100%;">
        <div class="msg-header">
          <span class="msg-author">🌐 ACTIVE SESSION: ${escapeHtml(activeSessionId)} — ${escapeHtml(
            friendlyName
          )}</span>
          <span class="msg-time">UNIVERSAL CONTEXT ATTACHED</span>
        </div>
        <div class="msg-content">Welcome to the dedicated session for <strong>${escapeHtml(
          friendlyName
        )}</strong>.
Even though this is a separate session, <strong>${escapeHtml(
          friendlyName
        )}</strong> has instant, zero-latency access to:
• All <code>user:*</code> namespaces updated in other sessions (e.g., <code>user:active_order</code> from Ordering Session #1, <code>user:delivery_logistics</code> from Delivery Session #2)
• All semantic facts in the <strong>Universal Memory Bank</strong> (${
          (universalContextData.memories || []).length
        } active memories across all sessions)
• All versioned documents in the <strong>Shared Artifact Vault</strong> (${
          (universalContextData.artifacts || []).length
        } artifacts)

Type any message below (every turn is automatically extracted into the shared Memory Bank!) or click a <strong>1-Click Cross-Session Share Test</strong> on the left!</div>
      </div>
    `;
    return;
  }

  listEl.innerHTML = messages
    .map((msg, idx) => {
      const isUser = msg.role === "user";
      const injectedCount = (msg.injected_memories || []).length;
      const crossCount = (msg.injected_memories || []).filter(
        (m) => m.source_agent !== msg.agent_name
      ).length;
      const toolCalls = msg.tool_calls || [];
      const a2aTraces = msg.a2a_trace || [];

      let telemetryHtml = "";
      if (!isUser) {
        const badges = [];
        if (injectedCount > 0) {
          badges.push(`
            <span class="telemetry-badge" onclick="inspectInjectedMemories('${activeSessionId}', ${idx})">
              🔗 Injected ${injectedCount} Universal Memories (${crossCount} cross-agent)
            </span>
          `);
        }
        toolCalls.forEach((tc) => {
          badges.push(`
            <span class="telemetry-badge">
              🛠️ ADK Tool: ${escapeHtml(tc.tool || tc.name || "tool")}
            </span>
          `);
        });
        if (a2aTraces.length > 0) {
          badges.push(`
            <span class="telemetry-badge" onclick="inspectA2ATrace('${activeSessionId}', ${idx})">
              🔍 View A2A JSON-RPC 2.0 Trace (${a2aTraces.length} call${a2aTraces.length > 1 ? "s" : ""})
            </span>
          `);
        }
        if (badges.length > 0) {
          telemetryHtml = `<div class="msg-telemetry-bar">${badges.join("")}</div>`;
        }
      }

      // Render collapsible Claude-Code Reasoning & Cross-Session Trace accordion for agent messages
      let reasoningHtml = "";
      if (!isUser) {
        const rSteps = msg.reasoning_steps || [
          {
            elapsed_sec: 0.1,
            title: "Universal Context Mesh Lookup",
            detail: `Read shared user:* namespaces & ${injectedCount} cross-session memories.`,
          },
          ...(toolCalls.length > 0
            ? [
                {
                  elapsed_sec: 0.9,
                  title: "ADK Tool Execution",
                  detail: `Executed ${toolCalls.map((t) => t.tool || t.name || "tool").join(", ")}`,
                },
              ]
            : []),
          {
            elapsed_sec: msg.elapsed_sec || 1.4,
            title: "Post-Turn Memory & Context Sync",
            detail: "Extracted turn facts into shared Universal Memory Bank across all sessions.",
          },
        ];
        const totalSec = msg.elapsed_sec || rSteps[rSteps.length - 1]?.elapsed_sec || "1.4";
        const boxId = `reasoningBox-${idx}`;
        const stepsRows = rSteps
          .map(
            (st) => `
          <div class="claude-reasoning-step">
            <span class="claude-reasoning-step-time">[${escapeHtml(st.elapsed_sec)}s]</span>
            <span><strong>${escapeHtml(st.title)}:</strong> ${escapeHtml(st.detail)}</span>
          </div>
        `
          )
          .join("");

        reasoningHtml = `
          <div class="claude-reasoning-box" id="${boxId}">
            <div class="claude-reasoning-header" onclick="toggleReasoningBox('${boxId}')">
              <div class="claude-reasoning-title">
                <span>🧠 Claude-Code Reasoning & Cross-Session Trace</span>
              </div>
              <div class="claude-reasoning-meta">
                <span>${rSteps.length} steps · ${escapeHtml(totalSec)}s</span>
                <span>▾</span>
              </div>
            </div>
            <div class="claude-reasoning-steps">
              ${stepsRows}
            </div>
          </div>
        `;
      }

      return `
        <div class="msg-card ${isUser ? "user" : "agent"}">
          <div class="msg-header">
            <span class="msg-author">${
              isUser
                ? `👤 ${isRestaurantUser(activeUserId) ? "CARLOS (CUSTOMER)" : "USER"}`
                : `🤖 ${escapeHtml(getAgentFriendlyName(msg.agent_name, activeUserId))}`
            }</span>
            <span class="msg-time">${formatTime(msg.timestamp)} · ${escapeHtml(activeSessionId)}</span>
          </div>
          ${reasoningHtml}
          <div class="msg-content">${escapeHtml(msg.content)}</div>
          ${telemetryHtml}
        </div>
      `;
    })
    .join("");

  // If liveThinkingState is active, append the live blinking/shrinking ink + streaming reasoning card!
  if (liveThinkingState.active) {
    const elapsedNow = ((Date.now() - liveThinkingState.startTime) / 1000).toFixed(1);
    const liveStepsHtml = liveThinkingState.steps
      .map(
        (st, sIdx) => `
        <div class="claude-reasoning-step ${sIdx === liveThinkingState.steps.length - 1 ? "active-step" : ""}">
          <span class="claude-reasoning-step-time">[${escapeHtml(st.elapsed_sec)}s]</span>
          <span>▸ <strong>${escapeHtml(st.title)}:</strong> ${escapeHtml(st.detail)}</span>
        </div>
      `
      )
      .join("");

    listEl.innerHTML += `
      <div class="claude-reasoning-box live-thinking expanded" id="liveThinkingCard">
        <div class="claude-reasoning-header">
          <div class="claude-reasoning-title">
            <span class="shrinking-shining-ink"></span>
            <span class="yazdani-spinner"></span>
            <span class="sweep-text" style="font-weight: 700;">
              ${escapeHtml(getAgentFriendlyName(liveThinkingState.agent, activeUserId))} is thinking & reasoning...
            </span>
          </div>
          <div class="claude-reasoning-meta">
            <span id="liveThinkingTimer" style="font-weight: 700; color: var(--text-primary);">${elapsedNow}s</span>
            <span>LIVE A2A + ADK STREAM</span>
          </div>
        </div>
        <div class="claude-reasoning-steps" style="display: flex;">
          ${liveStepsHtml}
        </div>
      </div>
    `;
  }

  listEl.scrollTop = listEl.scrollHeight;
}

async function handleChatSubmit(e) {
  e.preventDefault();
  const input = document.getElementById("chatInputBox");
  const text = input.value.trim();
  if (!text) return;
  input.value = "";
  await sendTurnToAgent(activeTargetAgent, activeSessionId, text);
}

async function runQuickScenario(targetAgent, promptText) {
  selectTargetAgent(targetAgent);
  await sendTurnToAgent(targetAgent, activeSessionId, promptText);
}

async function sendTurnToAgent(targetAgent, sessionId, messageText) {
  startLiveThinking(targetAgent, sessionId);
  setLoaderState(
    true,
    `✳ ${getAgentFriendlyName(targetAgent, activeUserId)} is reasoning...`,
    `Injecting Universal Context ('user:*' state + Cross-Agent Memory Bank) into ${sessionId}`
  );

  // Optimistically append user message
  if (universalContextData) {
    if (!universalContextData.sessions[sessionId]) {
      universalContextData.sessions[sessionId] = {
        session_id: sessionId,
        target_agent: targetAgent,
        messages: [],
      };
    }
    universalContextData.sessions[sessionId].messages.push({
      role: "user",
      agent_name: "user",
      content: messageText,
      timestamp: new Date().toISOString(),
    });
    renderActiveSessionMessages();
  }

  try {
    const resp = await fetch(`${API_BASE}/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        user_id: activeUserId,
        session_id: sessionId,
        target_agent: targetAgent,
        message: messageText,
      }),
    });
    if (resp.ok) {
      const data = await resp.json();
      universalContextData = data.universal_context;
    }
  } catch (err) {
    console.error("Chat turn error:", err);
  } finally {
    stopLiveThinking();
    setLoaderState(false);
    renderRightInspector();
    renderActiveSessionMessages();
  }
}

// ----------------------------------------------------------------------------
// 5. LIVE AUTONOMOUS MULTI-AGENT ROUNDTABLE (E2E SESSION SHARE)
// ----------------------------------------------------------------------------
async function runLiveRoundtable() {
  const btn = document.getElementById("roundtableBtn");
  if (btn) btn.disabled = true;

  startLiveThinking("orchestrator_agent", activeSessionId);
  setLoaderState(
    true,
    "⚡ Running Autonomous Multi-Agent Session-Share Roundtable...",
    "Step 1/4: Executing cross-session collaboration & updating Universal Context..."
  );
  renderActiveSessionMessages();

  try {
    const resp = await fetch(`${API_BASE}/api/roundtable/run`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id: activeUserId }),
    });
    if (resp.ok) {
      const data = await resp.json();
      universalContextData = data.universal_context;
      activeTargetAgent = "orchestrator_agent";
      if (data.sessions && data.sessions.length > 0) {
        activeSessionId = data.sessions[data.sessions.length - 1];
      }
    }
  } catch (err) {
    console.error("Roundtable error:", err);
  } finally {
    stopLiveThinking();
    setLoaderState(false);
    if (btn) btn.disabled = false;
    renderRightInspector();
    renderActiveSessionMessages();
  }
}

function setLoaderState(active, statusText = "", subText = "") {
  const banner = document.getElementById("inkLoaderBanner");
  if (!banner) return;
  banner.classList.toggle("active", active);
  if (statusText) document.getElementById("loaderStatusText").textContent = statusText;
  if (subText) document.getElementById("loaderSubText").textContent = subText;
}

// ----------------------------------------------------------------------------
// 6. TELEMETRY STREAM & TAB SWITCHING
// ----------------------------------------------------------------------------
function renderTelemetryStream() {
  const badge = document.getElementById("telemetryCountBadge");
  if (badge) badge.textContent = telemetryEvents.length;

  const list = document.getElementById("telemetryStreamList");
  if (!list) return;

  list.innerHTML = telemetryEvents
    .slice(0, 60)
    .map(
      (ev) => `
      <div class="telemetry-event-row">
        <div class="telemetry-event-top">
          <span class="event-type-pill">${escapeHtml(ev.event_type)}</span>
          <span style="color: var(--text-secondary); font-size: 10px;">${formatTime(ev.timestamp)}</span>
        </div>
        <div style="font-weight: 600; margin-top: 2px;">
          ${escapeHtml(ev.summary || JSON.stringify(ev))}
        </div>
      </div>
    `
    )
    .join("");
}

function clearTelemetryView() {
  telemetryEvents = [];
  renderTelemetryStream();
}

function switchCenterTab(tab) {
  document.getElementById("tabBtnChat").classList.toggle("active", tab === "chat");
  document.getElementById("tabBtnTopology").classList.toggle("active", tab === "topology");
  document.getElementById("centerChatPane").style.display = tab === "chat" ? "flex" : "none";
  document.getElementById("centerTopologyPane").style.display = tab === "topology" ? "flex" : "none";
}

function switchRightTab(tab) {
  document.getElementById("rightTabMemories").classList.toggle("active", tab === "memories");
  document.getElementById("rightTabState").classList.toggle("active", tab === "state");
  document.getElementById("rightTabArtifacts").classList.toggle("active", tab === "artifacts");

  document.getElementById("rightPaneMemories").style.display = tab === "memories" ? "block" : "none";
  document.getElementById("rightPaneState").style.display = tab === "state" ? "block" : "none";
  document.getElementById("rightPaneArtifacts").style.display = tab === "artifacts" ? "block" : "none";
}

// ----------------------------------------------------------------------------
// 7. MODALS: INSPECT A2A AGENT CARDS, JSON-RPC TRACES, MEMORIES, & ARTIFACTS
// ----------------------------------------------------------------------------
async function inspectRuntimeCard(agentName) {
  await checkRuntimeHealth();
  const modalTitle = document.getElementById("modalTitle");
  const modalBody = document.getElementById("modalBody");

  modalTitle.textContent = `A2A AGENT CARD // ${agentName.toUpperCase()}`;
  let cardData = {};
  if (runtimeHealthData && runtimeHealthData.a2a_agents && runtimeHealthData.a2a_agents[agentName]) {
    cardData = runtimeHealthData.a2a_agents[agentName];
  } else if (agentName === "orchestrator_agent" && runtimeHealthData) {
    cardData = runtimeHealthData.orchestrator;
  }

  modalBody.innerHTML = `
    <div style="margin-bottom: 12px; font-size: 12px; color: var(--text-secondary);">
      Live A2A Protocol JSON-RPC 2.0 Discovery Metadata fetched from <code>/.well-known/agent-card.json</code>:
    </div>
    <pre class="json-pre" style="background: var(--bg-canvas); padding: 14px; border: 1px solid var(--border-subtle); border-radius: 6px;">${escapeHtml(
      JSON.stringify(cardData, null, 2)
    )}</pre>
  `;
  document.getElementById("inspectorModal").classList.add("open");
}

function inspectInjectedMemories(sessionId, msgIndex) {
  const sess = universalContextData?.sessions?.[sessionId];
  const msg = sess?.messages?.[msgIndex];
  if (!msg) return;

  const modalTitle = document.getElementById("modalTitle");
  const modalBody = document.getElementById("modalBody");
  modalTitle.textContent = `CROSS-AGENT UNIVERSAL MEMORY INJECTION // TURN #${msgIndex + 1}`;

  const mems = msg.injected_memories || [];
  modalBody.innerHTML = `
    <div style="margin-bottom: 14px; font-size: 12px; line-height: 1.45;">
      Before <strong>${escapeHtml(msg.agent_name)}</strong> executed this turn in session <code>${escapeHtml(
        sessionId
      )}</code>, the Universal Context Engine automatically injected the following <strong>${
        mems.length
      } semantic memories</strong> discovered across peer sessions and agents:
    </div>
    ${mems
      .map(
        (m) => `
      <div class="context-card">
        <div class="context-card-header">
          <span class="context-card-title">Origin Agent: ${escapeHtml(m.source_agent)}</span>
          <span class="context-card-badge">Origin Session: ${escapeHtml(m.session_id)}</span>
        </div>
        <div style="font-size: 12px; margin-top: 4px;">${escapeHtml(m.fact)}</div>
      </div>
    `
      )
      .join("")}
  `;
  document.getElementById("inspectorModal").classList.add("open");
}

function inspectA2ATrace(sessionId, msgIndex) {
  const sess = universalContextData?.sessions?.[sessionId];
  const msg = sess?.messages?.[msgIndex];
  if (!msg) return;

  const modalTitle = document.getElementById("modalTitle");
  const modalBody = document.getElementById("modalBody");
  modalTitle.textContent = `A2A PROTOCOL JSON-RPC 2.0 WIRE TRACE`;

  modalBody.innerHTML = `
    <div style="margin-bottom: 12px; font-size: 12px; color: var(--text-secondary);">
      Complete A2A JSON-RPC 2.0 Request & Response envelopes exchanged over HTTP:
    </div>
    <pre class="json-pre" style="background: var(--bg-canvas); padding: 14px; border: 1px solid var(--border-subtle); border-radius: 6px;">${escapeHtml(
      JSON.stringify(msg.a2a_trace, null, 2)
    )}</pre>
  `;
  document.getElementById("inspectorModal").classList.add("open");
}

function inspectArtifact(idx) {
  const art = universalContextData?.artifacts?.[idx];
  if (!art) return;

  const modalTitle = document.getElementById("modalTitle");
  const modalBody = document.getElementById("modalBody");
  modalTitle.textContent = `SHARED ARTIFACT // ${art.filename} (v${art.version})`;

  modalBody.innerHTML = `
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px;">
      <div style="font-family: var(--font-mono); font-size: 11px; color: var(--text-secondary);">
        Created by <strong>${escapeHtml(art.created_by_agent)}</strong> in session <code>${escapeHtml(
          art.session_id
        )}</code>
      </div>
      <button class="btn btn-primary btn-mono" onclick="downloadArtifact(${idx})">⬇ Download ${escapeHtml(
        art.filename
      )}</button>
    </div>
    <pre class="json-pre" style="background: var(--bg-canvas); padding: 16px; border: 1px solid var(--border-subtle); border-radius: 6px; font-size: 12px; line-height: 1.6;">${escapeHtml(
      art.content
    )}</pre>
  `;
  document.getElementById("inspectorModal").classList.add("open");
}

function downloadArtifact(idx) {
  const art = universalContextData?.artifacts?.[idx];
  if (!art) return;
  const blob = new Blob([art.content], { type: art.mime_type || "text/markdown" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = art.filename;
  a.click();
  URL.revokeObjectURL(url);
}

function closeInspectorModal() {
  document.getElementById("inspectorModal").classList.remove("open");
}

// ----------------------------------------------------------------------------
// 8. USER MANAGEMENT & MEMORY CRUD
// ----------------------------------------------------------------------------
async function onUserChanged(newUserId) {
  activeUserId = newUserId;
  updateDomainUI(newUserId);
  await loadUserUniversalContext(activeUserId, true);
}

async function promptNewUser() {
  const email = prompt("Enter new user ID / email (e.g., marcus.vane@venture.io):");
  if (!email || !email.trim()) return;
  const name = prompt("Enter user full name (e.g., Marcus Vane):") || email;

  await fetch(`${API_BASE}/api/users`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_id: email.trim(), display_name: name.trim() }),
  });

  const sel = document.getElementById("userSelector");
  const opt = document.createElement("option");
  opt.value = email.trim();
  opt.textContent = `${name.trim()} (${email.trim()})`;
  sel.appendChild(opt);
  sel.value = email.trim();
  await onUserChanged(email.trim());
}

async function addManualMemory() {
  const inp = document.getElementById("newMemoryInput");
  const fact = inp.value.trim();
  if (!fact) return;
  inp.value = "";

  await fetch(`${API_BASE}/api/context/${encodeURIComponent(activeUserId)}/memory`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      fact: fact,
      category: "user_defined",
      source_agent: "user_manual",
      session_id: activeSessionId,
    }),
  });
  await loadUserUniversalContext(activeUserId, false);
}

async function deleteMemory(memId) {
  await fetch(
    `${API_BASE}/api/context/${encodeURIComponent(activeUserId)}/memory/${encodeURIComponent(memId)}`,
    { method: "DELETE" }
  );
  await loadUserUniversalContext(activeUserId, false);
}

async function clearUserSlate() {
  await fetch(`${API_BASE}/api/users/${encodeURIComponent(activeUserId)}/clear`, { method: "POST" });
  await loadUserUniversalContext(activeUserId, true);
}

async function resetDemoData() {
  await fetch(`${API_BASE}/api/reset`, { method: "POST" });
  await loadUserUniversalContext(activeUserId, true);
}

// Helpers
function escapeHtml(str) {
  if (str === null || str === undefined) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function formatTime(iso) {
  if (!iso) return "";
  try {
    const d = new Date(iso);
    return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" });
  } catch {
    return iso;
  }
}
