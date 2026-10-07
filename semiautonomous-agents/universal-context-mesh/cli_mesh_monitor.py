#!/usr/bin/env python3
"""
Claude-Code Style CLI Topology & Universal Context Mesh Inspector (`cli_mesh_monitor.py`).
Renders crisp Unicode box-drawing diagrams, live A2A runtime status, and cross-session
state/memory flow directly in the terminal.
"""

import json
import sys
import urllib.request
from typing import Any, Dict

API_BASE = "http://localhost:8010"


def fetch_json(url: str) -> Dict[str, Any]:
    try:
        with urllib.request.urlopen(url, timeout=5) as r:
            return json.loads(r.read().decode("utf-8"))
    except Exception as e:
        return {"error": str(e)}


def print_claude_style_topology(user_id: str = "carlos@restaurant.io") -> None:
    health = fetch_json(f"{API_BASE}/api/health")
    ctx = fetch_json(f"{API_BASE}/api/users/{urllib.request.quote(user_id)}/context")

    state = ctx.get("state", {})
    profile = state.get("user:profile", {})
    order = state.get("user:active_order", {})
    delivery = state.get("user:delivery_logistics", {})
    memories = ctx.get("memories", [])
    sessions = ctx.get("sessions", {})

    print("\n" + "═" * 96)
    print("  ⚡ UNIVERSAL CONTEXT MESH // CLAUDE-CODE CLI TOPOLOGY & CROSS-SESSION MONITOR")
    print("═" * 96)

    raw_items = order.get("items_summary") or ", ".join(order.get("items", []))
    items_display = (raw_items[:53] + "..") if len(raw_items) > 55 else raw_items

    diagram = f"""
  ┌──────────────────────────────────────────────────────────────────────────────────────────┐
  │ 👤 CUSTOMER IDENTITY: {user_id:<26} Name: {profile.get('name', 'Carlos'):<27} │
  └───────────────┬──────────────────────────────────────────┬───────────────────────────────┘
                  │                                          │
      (1) Opens Session #1                       (3) Opens Session #2 (Minutes Later)
       "Add Wagyu Gyoza &                         "What items are in my order right now?
        Gate Code #7766"                           (Without me repeating them!)"
                  │                                          │
                  ▼                                          ▼
  ┌───────────────────────────────┐          ┌───────────────────────────────┐
  │ 💬 SESSION #1 (Isolated Chat) │          │ 💬 SESSION #2 (Isolated Chat) │
  │ ID: session-ordering-1        │          │ ID: session-delivery-2        │
  └───────────────┬───────────────┘          └───────────────┬───────────────┘
                  │                                          │
                  ▼                                          ▼
  ┌───────────────────────────────┐          ┌───────────────────────────────┐
  │ 🍕 ORDERING AGENT (:8011)     │          │ 🛵 DELIVERY AGENT (:8012)     │
  │ • Google ADK + A2A Server     │          │ • Google ADK + A2A Server     │
  │ • gemini-3-flash-preview      │          │ • gemini-3-flash-preview      │
  └───────────────┬───────────────┘          └───────────────▲───────────────┘
                  │                                          │
      (2) Writes Order + Auto-Extracts           (4) Zero-Latency Context Injection
          Turn Facts via Context Bridge              BEFORE LLM Turn Executes!
                  │                                          │
                  ▼                                          │
  ╔══════════════════════════════════════════════════════════╧═══════════════════════════════╗
  ║ 🧠 UNIVERSAL USER CONTEXT MESH (Hub :8010 · Scoped to `{user_id}`)             ║
  ╠══════════════════════════════════════════════════════════════════════════════════════════╣
  ║                                                                                          ║
  ║  ┌─[ A. STRUCTURED NAMESPACES (`user:*`) ]────────────────────────────────────────────┐  ║
  ║  │ • user:active_order       : Order {str(order.get('order_id', '#ORD-9042')):<10} | Total: ${str(order.get('total_usd', 58.50)):<7}              │  ║
  ║  │   Items                   : {items_display:<55}│  ║
  ║  │ • user:delivery_logistics : Driver: {str(delivery.get('driver_assigned', 'Marco V.')):<18} | Gate Code: {str(delivery.get('gate_code', '#7766')):<8} │  ║
  ║  └────────────────────────────────────────────────────────────────────────────────────┘  ║
  ║                                                                                          ║
  ║  ┌─[ B. UNIVERSAL MEMORY BANK ({len(memories):02d} Shared Cross-Session Facts) ]──────────────────────┐  ║"""

    print(diagram)
    for m in memories[:4]:
        fact_str = m.get("fact", "").replace("\n", " ")
        if len(fact_str) > 76:
            fact_str = fact_str[:73] + "..."
        print(f"  ║  │ ▸ {fact_str:<80} │  ║")

    footer = f"""  ║  └────────────────────────────────────────────────────────────────────────────────────┘  ║
  ║                                                                                          ║
  ║  ┌─[ C. PEER A2A PROTOCOL JSON-RPC 2.0 MESH ]─────────────────────────────────────────┐  ║
  ║  │ • Orchestrator (:8010) ◄──JSON-RPC 2.0──► Ordering (:8011) | Delivery (:8012)      │  ║
  ║  │                        ◄──JSON-RPC 2.0──► VIP Support (:8013)                      │  ║
  ║  └────────────────────────────────────────────────────────────────────────────────────┘  ║
  ╚══════════════════════════════════════════════════════════════════════════════════════════╝
"""
    print(footer)

    print("  ┌─[ ACTIVE SESSIONS & MESSAGE COUNTS ]─────────────────────────────────────────────────┐")
    for sid, sdata in sessions.items():
        msg_count = len(sdata.get("messages", []))
        target = sdata.get("target_agent", "agent")
        print(f"  │ • {sid:<32} ──► Agent: {target:<18} ({msg_count} msgs)       │")
    print("  └──────────────────────────────────────────────────────────────────────────────────────┘\n")


if __name__ == "__main__":
    uid = sys.argv[1] if len(sys.argv) > 1 else "carlos@restaurant.io"
    print_claude_style_topology(uid)
