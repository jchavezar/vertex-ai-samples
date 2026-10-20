# -*- coding: utf-8 -*-
"""Live Bidirectional Bridge between the Rocket Cloud Run Suite and the Active Cloudtop Jetski Session
(`b8e05efd-fa58-497e-9665-9f5570facc35` on `jesus.c.googlers.com` in `/usr/local/google/home/jesusarguelles/rocket`).

Provides:
1. In-memory + `/tmp` persisted relay state on `rocket-hackathon-portal` + transparent proxy from the 7 domain services.
2. Self-contained HTML/CSS/JS Overlay (`render_jetski_live_overlay_html`) with:
   - 0ms optimistic message rendering
   - Claude-Code Shrinking & Shining Ink indicator with blinking/fading live step words
   - State-diffing scroll lock (never jumps while reading or inspecting logs)
   - Collapsible Thinking & Tool Execution logs (`📋 Thinking & Tool Logs (N)`) separated from the Final Answer
   - Context-aware quick instructions for the currently open demo square (`1.1` through `M.5` or `portal`)
   - Screenshot/image upload (`📷`) and Jetski Language Server model selector
"""

import base64
import json
import os
import time
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional

PINNED_CONVERSATION_ID = "b8e05efd-fa58-497e-9665-9f5570facc35"
PORTAL_UPSTREAM_URL = os.environ.get(
    "PORTAL_BRIDGE_UPSTREAM",
    "https://rocket-hackathon-portal-254356041555.us-central1.run.app",
).rstrip("/")
PERSIST_FILE = Path("/tmp/rocket_jetski_bridge_state.json")

_BRIDGE_STATE: Dict[str, Any] = {
    "conversation_id": PINNED_CONVERSATION_ID,
    "workspace": "/usr/local/google/home/jesusarguelles/rocket",
    "hostname": "jesus.c.googlers.com",
    "last_push_ts": 0.0,
    "telemetry": {
        "session_state": "IDLE",
        "total_steps": 0,
        "total_turns": 0,
        "updated_at": "",
    },
    "turns": [],
}
_COMMAND_QUEUE: List[Dict[str, Any]] = []


def _load_persisted() -> None:
    global _BRIDGE_STATE, _COMMAND_QUEUE
    if PERSIST_FILE.exists() and not _BRIDGE_STATE.get("turns"):
        try:
            raw = json.loads(PERSIST_FILE.read_text(encoding="utf-8"))
            if isinstance(raw, dict):
                if raw.get("state"):
                    _BRIDGE_STATE = raw["state"]
                if isinstance(raw.get("queue"), list):
                    _COMMAND_QUEUE = raw["queue"]
        except Exception:
            pass


def _save_persisted() -> None:
    try:
        PERSIST_FILE.write_text(
            json.dumps({"state": _BRIDGE_STATE, "queue": _COMMAND_QUEUE}),
            encoding="utf-8",
        )
    except Exception:
        pass


def _proxy_to_portal(path: str, method: str = "GET", payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    url = f"{PORTAL_UPSTREAM_URL}{path}"
    basic = base64.b64encode(b"rocket:Argon2026!").decode("ascii")
    headers = {
        "Authorization": f"Basic {basic}",
        "Content-Type": "application/json",
    }
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))


def get_bridge_state(service_mode: str = "portal") -> Dict[str, Any]:
    """Returns the latest Jetski session transcript & live status."""
    if service_mode != "portal":
        try:
            return _proxy_to_portal("/api/jetski-bridge/state", method="GET")
        except Exception as exc:
            return {
                "ok": False,
                "error": f"Portal bridge proxy error: {exc}",
                "conversation_id": PINNED_CONVERSATION_ID,
                "turns": [],
            }

    _load_persisted()
    now = time.time()
    last_push = float(_BRIDGE_STATE.get("last_push_ts") or 0.0)
    daemon_age = round(now - last_push, 1) if last_push > 0 else 9999.0
    return {
        "ok": True,
        "conversation_id": _BRIDGE_STATE.get("conversation_id", PINNED_CONVERSATION_ID),
        "workspace": _BRIDGE_STATE.get("workspace", "/usr/local/google/home/jesusarguelles/rocket"),
        "hostname": _BRIDGE_STATE.get("hostname", "jesus.c.googlers.com"),
        "daemon_online": daemon_age < 30.0,
        "daemon_heartbeat_age_s": daemon_age,
        "queued_commands_count": len(_COMMAND_QUEUE),
        "telemetry": _BRIDGE_STATE.get("telemetry", {}),
        "turns": _BRIDGE_STATE.get("turns", []),
    }


def enqueue_bridge_command(
    service_mode: str,
    prompt: str,
    active_square: str = "portal",
    page_url: str = "",
    model: str = "auto",
    attachments: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """Queues an instruction or question to be injected into Cloudtop session b8e05efd-fa58-497e-9665-9f5570facc35."""
    if service_mode != "portal":
        return _proxy_to_portal(
            "/api/jetski-bridge/send",
            method="POST",
            payload={
                "prompt": prompt,
                "active_square": active_square,
                "page_url": page_url,
                "model": model,
                "attachments": attachments or [],
            },
        )

    _load_persisted()
    now_iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    cmd_id = f"cmd_{int(time.time() * 1000)}"
    cmd_obj = {
        "cmd_id": cmd_id,
        "action": "send_prompt",
        "conversation_id": PINNED_CONVERSATION_ID,
        "prompt": prompt,
        "active_square": active_square,
        "page_url": page_url,
        "model": model or "auto",
        "attachments": attachments or [],
        "created_at": now_iso,
        "created_ts": time.time(),
    }
    _COMMAND_QUEUE.append(cmd_obj)

    # Also add an optimistic in-flight turn so any browser tab sees THINKING immediately
    turns = _BRIDGE_STATE.setdefault("turns", [])
    next_step_idx = (_BRIDGE_STATE.get("telemetry", {}).get("last_step_index") or 1050) + 1
    turns.append({
        "turn_id": f"opt_{cmd_id}",
        "user_step_index": next_step_idx,
        "user_prompt": prompt,
        "active_square": active_square,
        "source": "ROCKET_WEB_OVERLAY",
        "created_at": now_iso,
        "dispatched_ts": time.time(),
        "status": "THINKING",
        "live_step_banner": {
            "step_index": next_step_idx,
            "kind": "INIT",
            "headline": f"Step #{next_step_idx} • Queued for Cloudtop Session b8e05efd…",
            "subline": f"Delivering instruction from [{active_square}] to jesus.c.googlers.com via reverse tunnel…",
        },
        "intermediate_steps": [],
        "final_response": "",
    })
    _BRIDGE_STATE.setdefault("telemetry", {})["session_state"] = "THINKING"
    _save_persisted()
    return {
        "ok": True,
        "cmd_id": cmd_id,
        "conversation_id": PINNED_CONVERSATION_ID,
        "queued_commands_count": len(_COMMAND_QUEUE),
        "created_at": now_iso,
    }


def pull_pending_commands() -> Dict[str, Any]:
    """Called by scripts/rocket_jetski_bridge_daemon.py on jesus.c.googlers.com every 0.45s."""
    global _COMMAND_QUEUE
    _load_persisted()
    cmds = list(_COMMAND_QUEUE)
    _COMMAND_QUEUE = []
    if cmds:
        _save_persisted()
    return {
        "ok": True,
        "commands": cmds,
        "needs_push": (_BRIDGE_STATE.get("last_push_ts") or 0.0) == 0.0,
    }


def push_bridge_state(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Called by scripts/rocket_jetski_bridge_daemon.py on jesus.c.googlers.com whenever transcript changes."""
    global _BRIDGE_STATE
    _load_persisted()
    _BRIDGE_STATE = {
        "conversation_id": payload.get("conversation_id", PINNED_CONVERSATION_ID),
        "workspace": payload.get("workspace", "/usr/local/google/home/jesusarguelles/rocket"),
        "hostname": payload.get("hostname", "jesus.c.googlers.com"),
        "last_push_ts": time.time(),
        "telemetry": payload.get("telemetry", {}),
        "turns": payload.get("turns", []),
    }
    _save_persisted()
    return {"ok": True, "turns_count": len(_BRIDGE_STATE["turns"])}


SQUARE_TO_FILE_MAP = {
    "portal": ("shared/portal_ui.py", "rocket-hackathon-portal"),
    "1.1": ("shared/standalone_uis/sq_1_1.py", "rocket-demo-origination"),
    "1.2": ("shared/standalone_uis/sq_1_2.py", "rocket-demo-origination"),
    "1.3": ("shared/standalone_uis/sq_1_3.py", "rocket-demo-origination"),
    "1.4": ("shared/standalone_uis/sq_1_4.py", "rocket-demo-origination"),
    "1.5": ("shared/standalone_uis/sq_1_5.py", "rocket-demo-origination"),
    "2.1": ("shared/standalone_uis/sq_2_1.py", "rocket-demo-underwriting"),
    "2.2": ("shared/standalone_uis/sq_2_2.py", "rocket-demo-underwriting"),
    "2.3": ("shared/standalone_uis/sq_2_3.py", "rocket-demo-underwriting"),
    "2.4": ("shared/standalone_uis/sq_2_4.py", "rocket-demo-underwriting"),
    "2.5": ("shared/standalone_uis/sq_2_5.py", "rocket-demo-underwriting"),
    "3.1": ("shared/standalone_uis/sq_3_1.py", "rocket-demo-servicing"),
    "3.2": ("shared/standalone_uis/sq_3_2.py", "rocket-demo-servicing"),
    "3.3": ("shared/standalone_uis/sq_3_3.py", "rocket-demo-servicing"),
    "3.4": ("shared/standalone_uis/sq_3_4.py", "rocket-demo-servicing"),
    "3.5": ("shared/standalone_uis/sq_3_5.py", "rocket-demo-servicing"),
    "4.1": ("shared/standalone_uis/sq_4_1.py", "rocket-demo-marketing"),
    "4.2": ("shared/standalone_uis/sq_4_2.py", "rocket-demo-marketing"),
    "4.3": ("shared/standalone_uis/sq_4_3.py", "rocket-demo-marketing"),
    "4.4": ("shared/standalone_uis/sq_4_4.py", "rocket-demo-marketing"),
    "4.5": ("shared/standalone_uis/sq_4_5.py", "rocket-demo-marketing"),
    "5.1": ("shared/standalone_uis/sq_5_1.py", "rocket-demo-compliance"),
    "5.2": ("shared/standalone_uis/sq_5_2.py", "rocket-demo-compliance"),
    "5.3": ("shared/standalone_uis/sq_5_3.py", "rocket-demo-compliance"),
    "5.4": ("shared/standalone_uis/sq_5_4.py", "rocket-demo-compliance"),
    "5.5": ("shared/standalone_uis/sq_5_5.py", "rocket-demo-compliance"),
    "6.1": ("shared/standalone_uis/sq_6_1.py", "rocket-demo-sdlc"),
    "6.2": ("shared/standalone_uis/sq_6_2.py", "rocket-demo-sdlc"),
    "6.3": ("shared/standalone_uis/sq_6_3.py", "rocket-demo-sdlc"),
    "6.4": ("shared/standalone_uis/sq_6_4.py", "rocket-demo-sdlc"),
    "6.5": ("shared/standalone_uis/sq_6_5.py", "rocket-demo-sdlc"),
    "M.1": ("shared/standalone_uis/sq_m_1.py", "rocket-demo-moonshots"),
    "M.2": ("shared/standalone_uis/sq_m_2.py", "rocket-demo-moonshots"),
    "M.3": ("shared/standalone_uis/sq_m_3.py", "rocket-demo-moonshots"),
    "M.4": ("shared/standalone_uis/sq_m_4.py", "rocket-demo-moonshots"),
    "M.5": ("shared/standalone_uis/sq_m_5.py", "rocket-demo-moonshots"),
}


def render_jetski_live_overlay_html(current_code: str = "portal", auth_token: str = "") -> str:
    """Renders the floating & expandable Jetski Live Session Co-Pilot Overlay (`⌘J` / `Ctrl+J`)
    bound directly to Cloudtop conversation `b8e05efd-fa58-497e-9665-9f5570facc35`."""
    norm_code = (current_code or "portal").strip()
    target_file, target_service = SQUARE_TO_FILE_MAP.get(norm_code, ("shared/portal_ui.py", "rocket-hackathon-portal"))
    context_label = f"Main Command Portal ({target_file})" if norm_code == "portal" else f"Square [{norm_code}] ({target_file})"

    return f"""
<!-- ============================================================================
     JETSKI LIVE SESSION CO-PILOT OVERLAY (BOUND TO SESSION b8e05efd-fa58-497e-9665-9f5570facc35)
     Allows asking questions and sending live code/UI modification instructions directly
     to the active Cloudtop Jetski session from any browser window!
     ============================================================================ -->
<style>
  @keyframes jskInkPulse {{
    0%, 100% {{ transform: scale(1); opacity: 0.95; box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.55); }}
    50% {{ transform: scale(0.72); opacity: 0.65; box-shadow: 0 0 16px 4px rgba(56, 189, 248, 0.45); }}
  }}
  @keyframes jskTextSweep {{
    0% {{ background-position: -200% 0; opacity: 0.72; }}
    50% {{ opacity: 1; }}
    100% {{ background-position: 200% 0; opacity: 0.72; }}
  }}
  .jsk-shrinking-ink {{
    width: 11px;
    height: 11px;
    border-radius: 999px;
    background: radial-gradient(circle at 30% 30%, #a7f3d0, #10b981, #0369a1);
    animation: jskInkPulse 1.5s infinite cubic-bezier(0.4, 0, 0.2, 1);
    flex-shrink: 0;
  }}
  .jsk-sweep-text {{
    background: linear-gradient(90deg, #e2e8f0 0%, #38bdf8 45%, #34d399 55%, #e2e8f0 100%);
    background-size: 200% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: jskTextSweep 2.4s linear infinite;
    font-weight: 700;
  }}
  #jsk-floating-pill {{
    position: fixed;
    bottom: 24px;
    left: 24px;
    z-index: 9997;
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 16px;
    border-radius: 999px;
    background: linear-gradient(135deg, rgba(9, 13, 24, 0.96), rgba(15, 23, 42, 0.96));
    border: 1.5px solid rgba(16, 185, 129, 0.55);
    color: #f8fafc;
    box-shadow: 0 14px 34px rgba(2, 6, 23, 0.55), 0 0 22px rgba(16, 185, 129, 0.22);
    cursor: pointer;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    transition: transform 0.16s ease, border-color 0.16s ease;
    user-select: none;
  }}
  #jsk-floating-pill:hover {{
    transform: translateY(-2px);
    border-color: #34d399;
  }}
  #jsk-overlay-backdrop {{
    position: fixed;
    inset: 0;
    z-index: 10002;
    background: rgba(2, 6, 23, 0.68);
    backdrop-filter: blur(8px);
    display: none;
    align-items: center;
    justify-content: center;
    padding: 16px;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  }}
  #jsk-overlay-window {{
    width: 100%;
    max-width: 1060px;
    height: min(88vh, 860px);
    background: #0b0f19;
    border: 1.5px solid rgba(52, 211, 153, 0.4);
    border-radius: 20px;
    box-shadow: 0 28px 80px rgba(0, 0, 0, 0.78), 0 0 40px rgba(16, 185, 129, 0.15);
    display: flex;
    flex-direction: column;
    overflow: hidden;
    color: #f1f5f9;
    transition: all 0.2s ease;
  }}
  #jsk-overlay-window.jsk-docked-right {{
    position: fixed;
    top: 12px;
    right: 12px;
    bottom: 12px;
    width: min(520px, 95vw);
    max-width: 520px;
    height: auto;
  }}
  #jsk-overlay-backdrop.jsk-docked-mode {{
    background: transparent;
    backdrop-filter: none;
    pointer-events: none;
  }}
  #jsk-overlay-backdrop.jsk-docked-mode #jsk-overlay-window {{
    pointer-events: auto;
  }}
  .jsk-mono {{
    font-family: 'JetBrains Mono', 'IBM Plex Mono', monospace;
  }}
  .jsk-chip {{
    appearance: none;
    background: rgba(30, 41, 59, 0.78);
    border: 1px solid rgba(148, 163, 184, 0.25);
    color: #e2e8f0;
    font-size: 11.5px;
    font-weight: 600;
    padding: 6px 11px;
    border-radius: 999px;
    cursor: pointer;
    transition: all 0.14s ease;
    white-space: nowrap;
  }}
  .jsk-chip:hover {{
    background: rgba(16, 185, 129, 0.18);
    border-color: rgba(52, 211, 153, 0.6);
    color: #ffffff;
  }}
  .jsk-user-bubble {{
    margin-left: auto;
    max-width: 82%;
    background: linear-gradient(135deg, rgba(6, 78, 59, 0.65), rgba(15, 23, 42, 0.92));
    border: 1px solid rgba(52, 211, 153, 0.45);
    border-radius: 16px 16px 4px 16px;
    padding: 12px 16px;
    color: #ecfdf5;
    font-size: 13.5px;
    line-height: 1.55;
    box-shadow: 0 6px 18px rgba(0, 0, 0, 0.25);
  }}
  .jsk-agent-card {{
    max-width: 92%;
    background: rgba(15, 23, 42, 0.9);
    border: 1px solid rgba(71, 85, 105, 0.45);
    border-radius: 16px 16px 16px 4px;
    padding: 14px 18px;
    color: #f1f5f9;
    font-size: 13.5px;
    line-height: 1.62;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
  }}
  .jsk-tool-details {{
    margin-bottom: 10px;
    background: rgba(2, 6, 23, 0.65);
    border: 1px solid rgba(56, 189, 248, 0.28);
    border-radius: 10px;
    overflow: hidden;
  }}
  .jsk-tool-details summary {{
    cursor: pointer;
    padding: 8px 12px;
    font-size: 11.5px;
    font-weight: 700;
    color: #38bdf8;
    display: flex;
    align-items: center;
    justify-content: space-between;
    user-select: none;
    list-style: none;
  }}
  .jsk-tool-details summary::-webkit-details-marker {{ display: none; }}
</style>

<!-- Floating Bottom-Left Launcher Pill -->
<div id="jsk-floating-pill" onclick="window.toggleJetskiBridgeOverlay(true)" title="Open Live Jetski Session Bridge (⌘J / Ctrl+J)">
  <span class="jsk-shrinking-ink" id="jsk-pill-dot"></span>
  <div style="display:flex;flex-direction:column;line-height:1.15;">
    <span style="font-size:12px;font-weight:800;letter-spacing:-0.01em;display:flex;align-items:center;gap:6px;">
      🛠️ Jetski Live Co-Pilot
      <span class="jsk-mono" style="font-size:10px;padding:1px 6px;border-radius:6px;background:rgba(16,185,129,0.2);color:#6ee7b7;border:1px solid rgba(16,185,129,0.35);">b8e05efd</span>
    </span>
    <span class="jsk-mono" id="jsk-pill-substatus" style="font-size:10px;color:#94a3b8;">Modify [{norm_code}] on the fly • ⌘J</span>
  </div>
</div>

<!-- Expandable / Dockable Jetski Live Session Modal -->
<div id="jsk-overlay-backdrop" onclick="if(event.target===this) window.toggleJetskiBridgeOverlay(false)">
  <div id="jsk-overlay-window" onclick="event.stopPropagation()">
    <!-- Top Header Bar -->
    <div style="padding:14px 18px;background:rgba(2,6,23,0.92);border-bottom:1px solid rgba(51,65,85,0.65);display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap;">
      <div style="display:flex;align-items:center;gap:10px;">
        <span class="jsk-shrinking-ink" id="jsk-header-dot"></span>
        <div>
          <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
            <span style="font-size:14.5px;font-weight:800;color:#ffffff;letter-spacing:-0.01em;">
              🛠️ Jetski Live Session Bridge
            </span>
            <span class="jsk-mono" style="font-size:10.5px;padding:2px 8px;border-radius:999px;background:rgba(16,185,129,0.16);color:#34d399;border:1px solid rgba(16,185,129,0.38);">
              Session: b8e05efd-fa58-497e-9665-9f5570facc35
            </span>
            <span class="jsk-mono" id="jsk-daemon-badge" style="font-size:10.5px;padding:2px 8px;border-radius:999px;background:rgba(56,189,248,0.14);color:#38bdf8;border:1px solid rgba(56,189,248,0.3);">
              ⚡ Connecting Tunnel…
            </span>
          </div>
          <div class="jsk-mono" style="font-size:11px;color:#94a3b8;margin-top:2px;">
            Active Target: <strong style="color:#e2e8f0;">{context_label}</strong> • Service: <span style="color:#6ee7b7;">{target_service}</span>
          </div>
        </div>
      </div>

      <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
        <select id="jsk-model-select" class="jsk-mono" style="background:#0f172a;color:#e2e8f0;border:1px solid #334155;border-radius:8px;padding:5px 9px;font-size:11px;font-weight:600;outline:none;cursor:pointer;" title="Jetski Language Server Planner Model">
          <option value="auto" selected>🧠 Model: Auto (Gemini Pro Next)</option>
          <option value="gemini-launch-candidate-high">🚀 Gemini 4 Argon (High)</option>
          <option value="gemini-3.8-flash-high">⚡ Gemini 3.8 Flash (High)</option>
          <option value="opus-5.5-high">🎭 Claude Opus 5.5 (High)</option>
        </select>

        <button onclick="window.toggleJetskiDockMode()" id="jsk-dock-btn" class="jsk-mono" style="background:#1e293b;color:#cbd5e1;border:1px solid #334155;border-radius:8px;padding:5px 10px;font-size:11px;font-weight:700;cursor:pointer;" title="Dock to right side of screen so you can view the demo while chatting">
          ◫ Dock Right
        </button>

        <button onclick="window.location.reload()" class="jsk-mono" style="background:rgba(16,185,129,0.16);color:#6ee7b7;border:1px solid rgba(16,185,129,0.4);border-radius:8px;padding:5px 10px;font-size:11px;font-weight:700;cursor:pointer;" title="Reload current page to see newly deployed changes">
          🔄 Reload App
        </button>

        <button onclick="window.toggleJetskiBridgeOverlay(false)" style="background:#1e293b;color:#94a3b8;border:1px solid #334155;border-radius:8px;padding:5px 10px;font-size:12px;font-weight:800;cursor:pointer;">
          ✕ ESC
        </button>
      </div>
    </div>

    <!-- Live Step / Shrinking & Shining Ink Status Banner (Shown when THINKING or EXECUTING_TOOLS) -->
    <div id="jsk-live-banner" style="display:none;padding:10px 18px;background:linear-gradient(90deg, rgba(6,78,59,0.45), rgba(15,23,42,0.95));border-bottom:1px solid rgba(52,211,153,0.35);align-items:center;justify-content:space-between;gap:12px;">
      <div style="display:flex;align-items:center;gap:10px;min-width:0;">
        <span class="jsk-shrinking-ink"></span>
        <div style="min-width:0;">
          <div class="jsk-sweep-text jsk-mono" id="jsk-banner-headline" style="font-size:12px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">
            Jetski Planner Thinking…
          </div>
          <div class="jsk-mono" id="jsk-banner-subline" style="font-size:11px;color:#94a3b8;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">
            Streaming live from jesus.c.googlers.com…
          </div>
        </div>
      </div>
      <span class="jsk-mono" id="jsk-banner-step-badge" style="font-size:10.5px;padding:3px 8px;border-radius:6px;background:rgba(245,158,11,0.2);color:#fbbf24;border:1px solid rgba(245,158,11,0.4);white-space:nowrap;">
        ⚡ WORKING LIVE
      </span>
    </div>

    <!-- Context-Aware Quick Modification & Question Chips -->
    <div style="padding:10px 18px;background:rgba(15,23,42,0.65);border-bottom:1px solid rgba(51,65,85,0.45);display:flex;align-items:center;gap:8px;overflow-x:auto;">
      <span class="jsk-mono" style="font-size:10.5px;color:#64748b;font-weight:700;flex-shrink:0;">QUICK INSTRUCTIONS:</span>
      <button class="jsk-chip" onclick="window.prefillJetskiPrompt('Explain how the current page [{norm_code}] ({target_file}) is architected and what Vertex AI models/APIs it calls.')">
        🔍 Explain [{norm_code}] Architecture
      </button>
      <button class="jsk-chip" onclick="window.prefillJetskiPrompt('In [{norm_code}] ({target_file}), add an executive ROI summary callout banner at the top and deploy it live.')">
        ✨ Add Executive Callout to [{norm_code}]
      </button>
      <button class="jsk-chip" onclick="window.prefillJetskiPrompt('In [{norm_code}] ({target_file}), customize the color palette / typography and add a new interactive preset button, then redeploy.')">
        🎨 Modify [{norm_code}] UI & Redeploy
      </button>
      <button class="jsk-chip" onclick="window.prefillJetskiPrompt('Check the status of all 8 Cloud Run services and verify that Astra 2.0 and the 24 FPS Live Avatar are healthy.')">
        🩺 Health-Check All 8 Services
      </button>
    </div>

    <!-- Scrollable Transcript Stream -->
    <div id="jsk-chat-stream" style="flex:1;overflow-y:auto;padding:18px;display:flex;flex-direction:column;gap:16px;">
      <div style="text-align:center;padding:28px;color:#64748b;font-size:13px;" class="jsk-mono">
        Loading live conversation history from Cloudtop session <code>b8e05efd-fa58-497e-9665-9f5570facc35</code>…
      </div>
    </div>

    <!-- Attachment Preview Row -->
    <div id="jsk-attachment-row" style="display:none;padding:8px 18px;background:rgba(15,23,42,0.9);border-top:1px solid rgba(51,65,85,0.5);align-items:center;gap:10px;">
      <span class="jsk-mono" id="jsk-attachment-label" style="font-size:11px;color:#38bdf8;">📷 Attached image ready</span>
      <button onclick="window.clearJetskiAttachment()" class="jsk-mono" style="font-size:10.5px;color:#f87171;background:transparent;border:none;cursor:pointer;">✕ Remove</button>
    </div>

    <!-- Composer Input Bar -->
    <div style="padding:14px 18px;background:rgba(2,6,23,0.95);border-top:1px solid rgba(51,65,85,0.7);display:flex;align-items:flex-end;gap:10px;">
      <input type="file" id="jsk-file-input" accept="image/*" style="display:none" onchange="window.handleJetskiFileSelect(event)">
      <button onclick="document.getElementById('jsk-file-input').click()" style="background:#1e293b;color:#cbd5e1;border:1px solid #334155;border-radius:12px;padding:10px 12px;font-size:14px;cursor:pointer;flex-shrink:0;" title="Attach Screenshot or Image for Jetski to inspect">
        📷
      </button>
      <textarea id="jsk-prompt-input" rows="2"
        placeholder="Ask a question about [{norm_code}] or type an instruction to modify {target_file} on the fly (Enter to send, Shift+Enter for newline)…"
        style="flex:1;background:#0f172a;color:#f8fafc;border:1.5px solid #334155;border-radius:12px;padding:10px 14px;font-size:13.5px;line-height:1.45;resize:none;outline:none;font-family:inherit;"
        onkeydown="if(event.key==='Enter' && !event.shiftKey){{ event.preventDefault(); window.sendJetskiBridgePrompt(); }}"></textarea>
      <button id="jsk-send-btn" onclick="window.sendJetskiBridgePrompt()"
        style="background:linear-gradient(135deg, #10b981, #0284c7);color:#ffffff;border:none;border-radius:12px;padding:11px 18px;font-size:13px;font-weight:800;cursor:pointer;flex-shrink:0;box-shadow:0 4px 14px rgba(16,185,129,0.3);">
        Send to Jetski →
      </button>
    </div>
  </div>
</div>

<script>
(function() {{
  const JSK_CURRENT_CODE = {json.dumps(norm_code)};
  const JSK_TARGET_FILE = {json.dumps(target_file)};
  const JSK_TARGET_SERVICE = {json.dumps(target_service)};
  const JSK_AUTH_TOKEN = {json.dumps(auth_token or "")};

  let jskOverlayOpen = false;
  let jskDockedRight = false;
  let jskLastRenderSig = "";
  let jskPendingAttachment = null;
  let jskOptimisticTurns = [];
  let jskActionWordIdx = 0;
  const JSK_ACTION_WORDS = [
    "Synthesizing architecture & reading workspace files…",
    "Executing live tool calls on jesus.c.googlers.com…",
    "Editing Python UI module & verifying syntax…",
    "Streaming response back to Rocket Command Overlay…"
  ];

  function jskEscapeHtml(str) {{
    return String(str || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");
  }}

  function jskFormatMarkdown(md) {{
    if (!md) return "";
    let html = jskEscapeHtml(md);
    html = html.replace(/```([a-zA-Z0-9_-]*)\\n([\\s\\S]*?)```/g, function(_, lang, code) {{
      return '<pre class="jsk-mono" style="background:#020617;border:1px solid #1e293b;border-radius:10px;padding:10px 12px;margin:8px 0;overflow-x:auto;font-size:11.5px;color:#e2e8f0;"><code>' + code + '</code></pre>';
    }});
    html = html.replace(/`([^`]+)`/g, '<code class="jsk-mono" style="background:rgba(56,189,248,0.12);color:#7dd3fc;padding:1px 5px;border-radius:4px;font-size:12px;">$1</code>');
    html = html.replace(/\\*\\*([^*]+)\\*\\*/g, '<strong style="color:#ffffff;">$1</strong>');
    html = html.replace(/^### (.*)$/gm, '<div style="font-size:14px;font-weight:800;color:#6ee7b7;margin:10px 0 4px 0;">$1</div>');
    html = html.replace(/^## (.*)$/gm, '<div style="font-size:15px;font-weight:800;color:#38bdf8;margin:12px 0 6px 0;">$1</div>');
    html = html.replace(/^- (.*)$/gm, '<div style="padding-left:12px;margin:3px 0;">• $1</div>');
    html = html.replace(/\\n/g, "<br>");
    return html;
  }}

  window.toggleJetskiBridgeOverlay = function(forceState) {{
    const bd = document.getElementById("jsk-overlay-backdrop");
    if (!bd) return;
    jskOverlayOpen = typeof forceState === "boolean" ? forceState : !jskOverlayOpen;
    bd.style.display = jskOverlayOpen ? "flex" : "none";
    if (jskOverlayOpen) {{
      window.pollJetskiBridgeState(true);
      setTimeout(() => {{
        const inp = document.getElementById("jsk-prompt-input");
        if (inp) inp.focus();
      }}, 60);
    }}
  }};

  window.toggleJetskiDockMode = function() {{
    const bd = document.getElementById("jsk-overlay-backdrop");
    const win = document.getElementById("jsk-overlay-window");
    const btn = document.getElementById("jsk-dock-btn");
    if (!bd || !win) return;
    jskDockedRight = !jskDockedRight;
    if (jskDockedRight) {{
      bd.classList.add("jsk-docked-mode");
      win.classList.add("jsk-docked-right");
      if (btn) btn.textContent = "⛶ Center Modal";
    }} else {{
      bd.classList.remove("jsk-docked-mode");
      win.classList.remove("jsk-docked-right");
      if (btn) btn.textContent = "◫ Dock Right";
    }}
  }};

  window.prefillJetskiPrompt = function(text) {{
    const inp = document.getElementById("jsk-prompt-input");
    if (!inp) return;
    inp.value = text;
    inp.focus();
  }};

  window.handleJetskiFileSelect = function(ev) {{
    const file = ev.target.files && ev.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = function(e) {{
      jskPendingAttachment = {{
        mime_type: file.type || "image/png",
        data_b64: e.target.result,
        name: file.name
      }};
      const row = document.getElementById("jsk-attachment-row");
      const lbl = document.getElementById("jsk-attachment-label");
      if (row) row.style.display = "flex";
      if (lbl) lbl.textContent = "📷 Attached: " + file.name;
    }};
    reader.readAsDataURL(file);
  }};

  window.clearJetskiAttachment = function() {{
    jskPendingAttachment = null;
    const row = document.getElementById("jsk-attachment-row");
    const fi = document.getElementById("jsk-file-input");
    if (row) row.style.display = "none";
    if (fi) fi.value = "";
  }};

  window.sendJetskiBridgePrompt = async function() {{
    const inp = document.getElementById("jsk-prompt-input");
    if (!inp) return;
    const rawPrompt = (inp.value || "").trim();
    if (!rawPrompt) return;

    const modelSel = document.getElementById("jsk-model-select");
    const chosenModel = modelSel ? modelSel.value : "auto";
    const attList = jskPendingAttachment ? [jskPendingAttachment] : [];

    inp.value = "";
    window.clearJetskiAttachment();

    // 0ms Optimistic UI render
    const nowIso = new Date().toISOString();
    jskOptimisticTurns.push({{
      turn_id: "local_" + Date.now(),
      user_prompt: rawPrompt,
      active_square: JSK_CURRENT_CODE,
      created_at: nowIso,
      status: "THINKING",
      live_step_banner: {{
        headline: "Delivering instruction to Cloudtop session b8e05efd…",
        subline: JSK_ACTION_WORDS[0]
      }},
      intermediate_steps: [],
      final_response: ""
    }});
    jskLastRenderSig = ""; // force immediate DOM update
    renderJetskiStream(window._lastJskState || {{ turns: [], telemetry: {{ session_state: "THINKING" }} }}, true);

    try {{
      const q = JSK_AUTH_TOKEN ? ("?auth_token=" + encodeURIComponent(JSK_AUTH_TOKEN)) : "";
      await fetch("/api/jetski-bridge/send" + q, {{
        method: "POST",
        headers: {{ "Content-Type": "application/json" }},
        body: JSON.stringify({{
          prompt: rawPrompt,
          active_square: JSK_CURRENT_CODE,
          page_url: window.location.href,
          model: chosenModel,
          attachments: attList
        }})
      }});
      setTimeout(() => window.pollJetskiBridgeState(true), 350);
    }} catch (err) {{
      console.error("Jetski bridge send error:", err);
    }}
  }};

  function renderJetskiStream(data, scrollToBottom) {{
    window._lastJskState = data;
    const stream = document.getElementById("jsk-chat-stream");
    const daemonBadge = document.getElementById("jsk-daemon-badge");
    const liveBanner = document.getElementById("jsk-live-banner");
    const pillSub = document.getElementById("jsk-pill-substatus");

    if (daemonBadge) {{
      if (data.daemon_online) {{
        daemonBadge.style.background = "rgba(16,185,129,0.16)";
        daemonBadge.style.color = "#34d399";
        daemonBadge.style.borderColor = "rgba(16,185,129,0.4)";
        daemonBadge.textContent = "● Cloudtop Live (" + (data.daemon_heartbeat_age_s || 0) + "s)";
      }} else {{
        daemonBadge.style.background = "rgba(245,158,11,0.16)";
        daemonBadge.style.color = "#fbbf24";
        daemonBadge.style.borderColor = "rgba(245,158,11,0.4)";
        daemonBadge.textContent = "⚡ Tunnel Syncing…";
      }}
    }}

    const serverTurns = Array.isArray(data.turns) ? data.turns : [];
    // Prune optimistic turns that have now appeared in serverTurns
    jskOptimisticTurns = jskOptimisticTurns.filter(opt => {{
      return !serverTurns.some(st => (st.user_prompt || "").includes(opt.user_prompt));
    }});
    const allTurns = serverTurns.concat(jskOptimisticTurns);

    const lastTurn = allTurns.length ? allTurns[allTurns.length - 1] : null;
    const sessState = (lastTurn && lastTurn.status in {{"THINKING":1, "EXECUTING_TOOLS":1, "IN_PROGRESS":1}})
      ? lastTurn.status
      : ((data.telemetry && data.telemetry.session_state) || "IDLE");
    const isWorking = (sessState === "THINKING" || sessState === "EXECUTING_TOOLS" || sessState === "IN_PROGRESS" || jskOptimisticTurns.length > 0);

    if (liveBanner) {{
      if (isWorking) {{
        liveBanner.style.display = "flex";
        const b = (lastTurn && lastTurn.live_step_banner) || {{}};
        const hl = document.getElementById("jsk-banner-headline");
        const sl = document.getElementById("jsk-banner-subline");
        jskActionWordIdx = (jskActionWordIdx + 1) % JSK_ACTION_WORDS.length;
        if (hl) hl.textContent = b.headline || "Jetski Session b8e05efd Working Live…";
        if (sl) sl.textContent = b.subline || JSK_ACTION_WORDS[jskActionWordIdx];
        if (pillSub) pillSub.textContent = "⚡ Working live on Cloudtop…";
      }} else {{
        liveBanner.style.display = "none";
        if (pillSub) pillSub.textContent = "Modify [" + JSK_CURRENT_CODE + "] on the fly • ⌘J";
      }}
    }}

    if (!stream) return;

    // State-diffing signature so we NEVER reset scroll or collapse open <details> unless content changed
    const sig = JSON.stringify(allTurns.map(t => [
      t.turn_id,
      t.status,
      (t.intermediate_steps || []).length,
      (t.final_response || "").length,
      (t.live_step_banner || {{}}).headline || ""
    ]));
    if (sig === jskLastRenderSig && !scrollToBottom) {{
      return;
    }}
    const wasNearBottom = (stream.scrollHeight - stream.scrollTop - stream.clientHeight) < 90;
    jskLastRenderSig = sig;

    if (!allTurns.length) {{
      stream.innerHTML = '<div class="jsk-mono" style="text-align:center;padding:30px;color:#94a3b8;font-size:12.5px;">Connected to session <code>b8e05efd-fa58-497e-9665-9f5570facc35</code>. Send a question or instruction below!</div>';
      return;
    }}

    stream.innerHTML = allTurns.map(turn => {{
      const cleanPrompt = String(turn.user_prompt || "").replace(/^\\[ROCKET-WEB-BRIDGE[^\\]]*\\]\\s*/i, "");
      const steps = Array.isArray(turn.intermediate_steps) ? turn.intermediate_steps : [];
      let toolCount = 0;
      let thinkCount = 0;
      const stepRowsHtml = steps.map(st => {{
        if (st.kind === "THINKING") {{
          thinkCount++;
          return '<div style="padding:8px 10px;border-bottom:1px solid rgba(51,65,85,0.4);font-size:11.5px;color:#cbd5e1;">' +
            '<span class="jsk-mono" style="color:#a78bfa;font-weight:700;">🧠 THINKING (Step #' + (st.step_index || "") + '):</span> ' +
            jskEscapeHtml(String(st.thinking || "").slice(0, 420)) +
            (String(st.thinking || "").length > 420 ? "…" : "") +
          '</div>';
        }}
        if (st.kind === "TOOL_BATCH") {{
          const tools = Array.isArray(st.tools) ? st.tools : [];
          return tools.map(tc => {{
            toolCount++;
            const badgeColor = tc.status === "RUNNING" ? "#fbbf24" : "#34d399";
            return '<div class="jsk-mono" style="padding:7px 10px;border-bottom:1px solid rgba(51,65,85,0.4);font-size:11px;color:#e2e8f0;display:flex;align-items:center;justify-content:space-between;gap:8px;">' +
              '<div style="min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">' +
                '<strong style="color:#38bdf8;">🔧 ' + jskEscapeHtml(tc.name || "tool") + '</strong> • ' +
                '<span>' + jskEscapeHtml(tc.summary || tc.command_preview || "") + '</span>' +
              '</div>' +
              '<span style="color:' + badgeColor + ';flex-shrink:0;">' + jskEscapeHtml(tc.status || "DONE") + (tc.duration_ms ? (" (" + tc.duration_ms + "ms)") : "") + '</span>' +
            '</div>';
          }}).join("");
        }}
        return "";
      }}).join("");

      const logsDropdown = (steps.length > 0)
        ? '<details class="jsk-tool-details">' +
            '<summary class="jsk-mono">' +
              '<span>📋 Internal Thinking &amp; Tool Logs (' + thinkCount + ' thoughts, ' + toolCount + ' tool calls)</span>' +
              '<span style="font-size:10px;color:#94a3b8;">Click to expand ▾</span>' +
            '</summary>' +
            '<div style="max-height:220px;overflow-y:auto;">' + stepRowsHtml + '</div>' +
          '</details>'
        : "";

      const turnWorking = (turn.status === "THINKING" || turn.status === "EXECUTING_TOOLS" || turn.status === "IN_PROGRESS") && !turn.final_response;
      const bannerObj = turn.live_step_banner || {{}};
      const finalHtml = turn.final_response
        ? '<div style="margin-top:4px;">' + jskFormatMarkdown(turn.final_response) + '</div>'
        : (turnWorking
            ? '<div style="display:flex;align-items:center;gap:10px;padding:6px 0;">' +
                '<span class="jsk-shrinking-ink"></span>' +
                '<span class="jsk-sweep-text jsk-mono" style="font-size:12px;">' + jskEscapeHtml(bannerObj.headline || "Jetski is working on your request…") + '</span>' +
              '</div>'
            : '<div class="jsk-mono" style="font-size:11.5px;color:#94a3b8;">Completed tool execution.</div>');

      return '<div style="display:flex;flex-direction:column;gap:8px;">' +
        '<div class="jsk-user-bubble">' +
          '<div class="jsk-mono" style="font-size:10px;color:#6ee7b7;margin-bottom:4px;display:flex;justify-content:space-between;gap:8px;">' +
            '<span>👤 YOU → JETSKI SESSION b8e05efd</span>' +
            '<span>' + jskEscapeHtml((turn.created_at || "").slice(11, 19)) + '</span>' +
          '</div>' +
          '<div>' + jskEscapeHtml(cleanPrompt) + '</div>' +
        '</div>' +
        '<div class="jsk-agent-card">' +
          '<div class="jsk-mono" style="font-size:10px;color:#38bdf8;margin-bottom:6px;display:flex;justify-content:space-between;">' +
            '<span>🤖 JETSKI CLOUDTOP AGENT (jesus.c.googlers.com)</span>' +
            '<span>Step #' + jskEscapeHtml(turn.final_step_index || turn.user_step_index || "") + '</span>' +
          '</div>' +
          logsDropdown +
          finalHtml +
        '</div>' +
      '</div>';
    }}).join("");

    if (scrollToBottom || wasNearBottom) {{
      stream.scrollTop = stream.scrollHeight;
    }}
  }}

  window.pollJetskiBridgeState = async function(forceScroll) {{
    try {{
      const q = JSK_AUTH_TOKEN ? ("?auth_token=" + encodeURIComponent(JSK_AUTH_TOKEN)) : "";
      const res = await fetch("/api/jetski-bridge/state" + q, {{ cache: "no-store" }});
      if (!res.ok) return;
      const data = await res.json();
      if (data && data.ok) {{
        renderJetskiStream(data, Boolean(forceScroll));
      }}
    }} catch (e) {{
      // ignore transient network error
    }}
  }};

  // Keyboard shortcuts: Cmd+J / Ctrl+J toggles Jetski Live Session Bridge; Escape closes
  document.addEventListener("keydown", function(e) {{
    if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "j") {{
      e.preventDefault();
      window.toggleJetskiBridgeOverlay();
    }} else if (e.key === "Escape" && jskOverlayOpen) {{
      window.toggleJetskiBridgeOverlay(false);
    }}
  }});

  // Poll every 1.4s when overlay is open, or every 5s in background to keep status dot fresh
  setInterval(function() {{
    if (jskOverlayOpen) {{
      window.pollJetskiBridgeState(false);
    }}
  }}, 1400);
  setInterval(function() {{
    if (!jskOverlayOpen) {{
      window.pollJetskiBridgeState(false);
    }}
  }}, 5500);
  setTimeout(() => window.pollJetskiBridgeState(false), 600);
}})();
</script>
"""
