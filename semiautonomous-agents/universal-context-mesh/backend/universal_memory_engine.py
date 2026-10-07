"""
Universal User Context & Memory Bank Engine.
Provides cross-session, cross-agent state synchronization (`user:*` namespace),
long-term semantic Memory Bank, versioned Artifact Vault, automatic post-turn
context extraction (`after_turn_auto_extractor`), and real-time WebSocket telemetry.
"""

import asyncio
import json
import os
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

DATA_FILE = Path(__file__).parent.parent / "runtime_data" / "universal_context_store.json"


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


DEFAULT_USERS: Dict[str, Dict[str, Any]] = {
    "carlos@restaurant.io": {
        "user_id": "carlos@restaurant.io",
        "display_name": "Carlos (Restaurant Ordering ↔ Delivery Customer)",
        "domain_mode": "restaurant",
        "avatar": "CR",
        "universal_state": {
            "user:profile": {
                "full_name": "Carlos",
                "phone": "+1 (555) 019-2834",
                "loyalty_tier": "Gold Member",
                "dietary_preferences": "Loves spicy food, no peanuts",
            },
            "user:active_order": {
                "order_id": "ORD-9042",
                "status": "In Kitchen - Preparing",
                "restaurant_branch": "Sakura & Wagyu Downtown Kitchen",
                "items": [
                    {"name": "Spicy Tuna Crispy Rice", "qty": 2, "price_usd": 28.0},
                    {"name": "A5 Wagyu Smash Burger", "qty": 1, "price_usd": 32.0},
                    {"name": "Organic Iced Matcha Latte", "qty": 1, "price_usd": 7.5},
                ],
                "subtotal_usd": 67.50,
                "ordered_at": "2026-09-17T08:45:00Z",
                "created_in_session": "session-ordering-seed",
            },
            "user:delivery_logistics": {
                "delivery_address": "742 Evergreen Terrace, Apt 4B",
                "driver_assigned": "Marco V. (Electric Scooter #14)",
                "estimated_arrival_mins": 18,
                "gate_code": "Pending customer confirmation",
                "dropoff_instructions": "Leave at front desk if gate is locked",
            },
            "user:recent_cross_session_turns": [
                {
                    "session_id": "session-ordering-seed",
                    "agent": "ordering_agent (wealth_agent slot)",
                    "summary": "Carlos ordered 2x Spicy Tuna Crispy Rice, 1x A5 Wagyu Smash Burger, and 1x Iced Matcha Latte ($67.50) to 742 Evergreen Terrace.",
                    "timestamp": "2026-09-17T08:45:00Z",
                }
            ],
        },
        "memories": [
            {
                "memory_id": "mem-rest-101",
                "user_id": "carlos@restaurant.io",
                "fact": "Customer name is Carlos (Gold Member, no peanuts allergy preference).",
                "category": "customer_profile",
                "source_agent": "ordering_agent",
                "session_id": "session-ordering-seed",
                "confidence": 0.99,
                "timestamp": "2026-09-17T08:44:00Z",
            },
            {
                "memory_id": "mem-rest-102",
                "user_id": "carlos@restaurant.io",
                "fact": "Active Order #ORD-9042 placed in Ordering Session: 2x Spicy Tuna Crispy Rice, 1x A5 Wagyu Smash Burger, 1x Iced Matcha Latte ($67.50 total).",
                "category": "active_order",
                "source_agent": "ordering_agent",
                "session_id": "session-ordering-seed",
                "confidence": 0.99,
                "timestamp": "2026-09-17T08:45:00Z",
            },
            {
                "memory_id": "mem-rest-103",
                "user_id": "carlos@restaurant.io",
                "fact": "Delivery destination for Order #ORD-9042 is 742 Evergreen Terrace, Apt 4B (Driver Marco V., ETA 18 mins).",
                "category": "delivery_logistics",
                "source_agent": "delivery_agent",
                "session_id": "session-delivery-seed",
                "confidence": 0.98,
                "timestamp": "2026-09-17T08:46:00Z",
            },
        ],
        "artifacts": [
            {
                "artifact_id": "art-rest-v1",
                "filename": "order_receipt_ORD9042.md",
                "title": "Live Order & Kitchen Ticket #ORD-9042",
                "mime_type": "text/markdown",
                "version": 1,
                "scope": "user:universal",
                "created_by_agent": "ordering_agent",
                "session_id": "session-ordering-seed",
                "timestamp": "2026-09-17T08:45:10Z",
                "content": (
                    "# Live Order & Kitchen Ticket #ORD-9042\n"
                    "**Customer**: Carlos (`carlos@restaurant.io`)\n"
                    "**Created By**: Ordering Agent (`Session #1`)\n"
                    "**Shared With**: Delivery Agent (`Session #2`) & Support Agent (`Session #3`)\n\n"
                    "## Ordered Items\n"
                    "- **2x Spicy Tuna Crispy Rice** — $28.00\n"
                    "- **1x A5 Wagyu Smash Burger** — $32.00\n"
                    "- **1x Organic Iced Matcha Latte** — $7.50\n"
                    "- **Total Paid**: **$67.50 USD**\n\n"
                    "## Live Delivery Handoff Context\n"
                    "- **Address**: 742 Evergreen Terrace, Apt 4B\n"
                    "- **Assigned Courier**: Marco V. (ETA: 18 mins)\n"
                    "- **Gate Code / Notes**: Pending customer confirmation\n"
                ),
            }
        ],
        "sessions": {},
        "mutation_history": [],
    },
    "alex.rivera@enterprise.io": {
        "user_id": "alex.rivera@enterprise.io",
        "display_name": "Alex Rivera (Tech Founder & Investor)",
        "domain_mode": "wealth",
        "avatar": "AR",
        "universal_state": {
            "user:profile": {
                "full_name": "Alex Rivera",
                "citizenship": "United States",
                "current_residence": "San Francisco, CA",
                "family_status": "Married, 2 children",
                "primary_goal": "Post-liquidity wealth preservation, European expansion & tax optimization",
            },
            "user:financial_profile": {
                "liquid_net_worth_usd": 14500000,
                "recent_liquidity_event": "Sold $6.2M in AI startup secondary shares (Q3 2026)",
                "core_holdings": "45% US Tech Equities (NVDA, GOOGL), 35% Treasury Bills, 20% Venture PE",
                "risk_tolerance": "Moderate-Growth with currency hedging",
                "annual_budget_usd": 420000,
            },
            "user:legal_tax_status": {
                "current_tax_jurisdiction": "US Federal + California Franchise Tax Board",
                "foreign_entities": "Evaluating Swiss GmbH holding company vs Delaware LLC",
                "compliance_flags": [
                    "FATCA / FBAR reporting required on foreign accounts > $10,000",
                    "California exit tax audit risk if CA ties remain active",
                ],
                "tax_treaty_status": "US-Switzerland Double Taxation Treaty (Article 4 tie-breaker pending)",
            },
            "user:mobility_plan": {
                "target_destinations": ["Zurich, Switzerland", "Lisbon, Portugal"],
                "preferred_timeline": "Q1 2027 Relocation",
                "schengen_days_used_rolling_180": 42,
                "schengen_days_remaining": 48,
                "visa_pathway": "Swiss Lump-Sum / Residence Permit B via Investment",
            },
            "user:recent_cross_session_turns": [],
        },
        "memories": [
            {
                "memory_id": "mem-init-101",
                "user_id": "alex.rivera@enterprise.io",
                "fact": "Alex completed a $6.2M secondary equity sale in Q3 2026 and holds $14.5M total liquid net worth.",
                "category": "financial",
                "source_agent": "wealth_agent",
                "session_id": "session-wealth-seed",
                "confidence": 0.99,
                "timestamp": "2026-09-16T14:10:00Z",
            },
            {
                "memory_id": "mem-init-102",
                "user_id": "alex.rivera@enterprise.io",
                "fact": "Alex is subject to US worldwide taxation (FATCA) and high California state tax exposure until formal domicile severance.",
                "category": "legal_tax",
                "source_agent": "legal_tax_agent",
                "session_id": "session-legal-seed",
                "confidence": 0.98,
                "timestamp": "2026-09-16T14:15:00Z",
            },
            {
                "memory_id": "mem-init-103",
                "user_id": "alex.rivera@enterprise.io",
                "fact": "Alex has used 42 of 90 Schengen visa-free days in the last 180 days and plans a family move to Zurich in Q1 2027.",
                "category": "mobility",
                "source_agent": "mobility_agent",
                "session_id": "session-mobility-seed",
                "confidence": 0.97,
                "timestamp": "2026-09-16T14:20:00Z",
            },
        ],
        "artifacts": [
            {
                "artifact_id": "art-wealth-v1",
                "filename": "portfolio_analysis.md",
                "title": "Executive Wealth & Currency Allocation Plan",
                "mime_type": "text/markdown",
                "version": 1,
                "scope": "user:universal",
                "created_by_agent": "wealth_agent",
                "session_id": "session-wealth-seed",
                "timestamp": "2026-09-16T14:12:00Z",
                "content": (
                    "# Executive Wealth & Currency Allocation Plan\n"
                    "**Client**: Alex Rivera (`alex.rivera@enterprise.io`)\n"
                    "**Generated By**: Wealth & Portfolio ADK Agent (`wealth_agent`)\n\n"
                    "## 1. Liquidity Summary\n"
                    "- **Total Liquid Net Worth**: $14,500,000 USD\n"
                    "- **Recent Liquidity Event**: $6,200,000 USD net proceeds from secondary equity sale\n\n"
                    "## 2. Recommended Cross-Border Asset Allocation\n"
                    "| Asset Class | Current % | Target % | Currency | Notes |\n"
                    "|---|---|---|---|---|\n"
                    "| US Tech Equities | 45% | 30% | USD | Trim concentration risk |\n"
                    "| Swiss Sovereign / CHF Liquidity | 0% | 25% | CHF | Hedge upcoming Zurich relocation |\n"
                    "| US Short-Term Treasuries | 35% | 25% | USD | Yield 4.6% liquid reserve |\n"
                    "| Global Private Credit / PE | 20% | 20% | Multi | Long-term growth |\n"
                ),
            },
        ],
        "sessions": {},
        "mutation_history": [],
    },
}


class UniversalContextEngine:
    """Thread-safe / async-safe singleton store for Universal User Context, Memory Bank, Artifacts, and Telemetry."""

    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self.users: Dict[str, Dict[str, Any]] = {}
        self.telemetry_log: List[Dict[str, Any]] = []
        self._ws_subscribers: List[asyncio.Queue] = []
        self._load_or_init()

    def _load_or_init(self) -> None:
        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        if DATA_FILE.exists():
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    loaded_users = data.get("users", {})
                    # Ensure carlos@restaurant.io is always present
                    for k, v in DEFAULT_USERS.items():
                        if k not in loaded_users:
                            loaded_users[k] = v
                    self.users = loaded_users
                    self.telemetry_log = data.get("telemetry_log", [])[-200:]
                    return
            except Exception as e:
                print(f"Warning: failed to load persisted store ({e}), initializing default.")
        self.users = json.loads(json.dumps(DEFAULT_USERS))
        self._save()

    def _save(self) -> None:
        try:
            DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "users": self.users,
                        "telemetry_log": self.telemetry_log[-200:],
                    },
                    f,
                    indent=2,
                )
        except Exception as e:
            print(f"Warning: failed to save store: {e}")

    def ensure_user(self, user_id: str) -> Dict[str, Any]:
        if user_id not in self.users:
            self.users[user_id] = {
                "user_id": user_id,
                "display_name": user_id.split("@")[0].replace(".", " ").title(),
                "domain_mode": "restaurant" if "restaurant" in user_id or "carlos" in user_id.lower() else "wealth",
                "avatar": user_id[:2].upper(),
                "universal_state": {
                    "user:profile": {"full_name": user_id, "primary_goal": "Universal Multi-Agent Context"},
                    "user:active_order": {},
                    "user:delivery_logistics": {},
                    "user:recent_cross_session_turns": [],
                },
                "memories": [],
                "artifacts": [],
                "sessions": {},
                "mutation_history": [],
            }
            self._save()
        return self.users[user_id]

    async def broadcast_telemetry(self, event_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        event = {
            "event_id": f"evt-{uuid.uuid4().hex[:8]}",
            "timestamp": _now_iso(),
            "event_type": event_type,
            **payload,
        }
        self.telemetry_log.append(event)
        if len(self.telemetry_log) > 250:
            self.telemetry_log = self.telemetry_log[-250:]
        self._save()

        dead_queues = []
        for q in self._ws_subscribers:
            try:
                q.put_nowait(event)
            except Exception:
                dead_queues.append(q)
        for dq in dead_queues:
            if dq in self._ws_subscribers:
                self._ws_subscribers.remove(dq)
        return event

    def subscribe_ws(self) -> asyncio.Queue:
        q: asyncio.Queue = asyncio.Queue(maxsize=200)
        self._ws_subscribers.append(q)
        return q

    def unsubscribe_ws(self, q: asyncio.Queue) -> None:
        if q in self._ws_subscribers:
            self._ws_subscribers.remove(q)

    # -------------------------------------------------------------------------
    # UNIVERSAL STATE (`user:*`) READ & WRITE
    # -------------------------------------------------------------------------
    async def update_universal_state(
        self,
        user_id: str,
        namespace_key: str,
        updates: Dict[str, Any],
        source_agent: str,
        session_id: str = "global",
    ) -> Dict[str, Any]:
        """Updates a `user:*` namespace key in the Universal Context and records diff + telemetry."""
        async with self._lock:
            u = self.ensure_user(user_id)
            if not namespace_key.startswith("user:"):
                namespace_key = f"user:{namespace_key}"

            prev_val = json.loads(json.dumps(u["universal_state"].get(namespace_key, {})))
            if isinstance(prev_val, dict) and isinstance(updates, dict):
                # If a brand-new order_id is placed, completely supersede previous order & prune old order memories!
                new_oid = str(updates.get("order_id", "")).strip()
                old_oid = str(prev_val.get("order_id", "")).strip()
                if namespace_key == "user:active_order" and new_oid and old_oid and new_oid != old_oid:
                    merged = updates
                    clean_old = old_oid.replace("#", "")
                    if clean_old:
                        u["memories"] = [m for m in u["memories"] if clean_old not in m.get("fact", "")]
                elif namespace_key == "user:active_order" and updates.get("items_summary"):
                    # If items_summary is updated, remove stale "items" list from previous order preset
                    merged = {**prev_val, **updates}
                    if "items" in merged and "items" not in updates:
                        merged["items"] = [updates["items_summary"]]
                else:
                    merged = {**prev_val, **updates}
            else:
                merged = updates

            u["universal_state"][namespace_key] = merged

            mutation = {
                "mutation_id": f"mut-{uuid.uuid4().hex[:8]}",
                "timestamp": _now_iso(),
                "user_id": user_id,
                "namespace_key": namespace_key,
                "source_agent": source_agent,
                "session_id": session_id,
                "previous_value": prev_val,
                "new_value": merged,
                "updated_fields": list(updates.keys()) if isinstance(updates, dict) else [namespace_key],
            }
            u["mutation_history"].insert(0, mutation)
            u["mutation_history"] = u["mutation_history"][:50]
            self._save()

        await self.broadcast_telemetry(
            "CONTEXT_WRITE",
            {
                "user_id": user_id,
                "source_agent": source_agent,
                "session_id": session_id,
                "namespace_key": namespace_key,
                "updated_fields": mutation["updated_fields"],
                "summary": f"{source_agent} updated universal state `{namespace_key}` ({', '.join(mutation['updated_fields'])})",
            },
        )
        return merged

    async def clear_user_context(self, user_id: str) -> Dict[str, Any]:
        """Completely wipes all preloaded orders, memories, sessions, and artifacts for a clean slate."""
        async with self._lock:
            u = self.ensure_user(user_id)
            u["memories"] = []
            u["artifacts"] = []
            u["sessions"] = {}
            u["mutation_history"] = []
            u["universal_state"]["user:active_order"] = {
                "status": "Empty — Ready for new order",
                "order_id": "NONE",
                "items_summary": "No items ordered yet",
                "total_usd": 0.0,
            }
            u["universal_state"]["user:delivery_logistics"] = {
                "delivery_status": "Awaiting new order",
                "driver_assigned": "Unassigned",
                "eta_minutes": 0,
            }
            u["universal_state"]["user:recent_cross_session_turns"] = []
            self._save()

        await self.broadcast_telemetry(
            "CONTEXT_CLEARED",
            {
                "user_id": user_id,
                "summary": f"🗑️ Wiped all preloaded orders, Memory Bank facts, and sessions for `{user_id}` (Empty Slate).",
            },
        )
        return u

    def get_universal_state(self, user_id: str) -> Dict[str, Any]:
        u = self.ensure_user(user_id)
        return u["universal_state"]

    # -------------------------------------------------------------------------
    # UNIVERSAL MEMORY BANK (`MemoryBank`)
    # -------------------------------------------------------------------------
    async def add_memory(
        self,
        user_id: str,
        fact: str,
        category: str,
        source_agent: str,
        session_id: str = "global",
        confidence: float = 0.96,
    ) -> Dict[str, Any]:
        """Stores a semantic fact in the user's Universal Memory Bank accessible to all agents."""
        async with self._lock:
            u = self.ensure_user(user_id)
            for m in u["memories"]:
                if m["fact"].strip().lower() == fact.strip().lower():
                    m["timestamp"] = _now_iso()
                    m["source_agent"] = source_agent
                    self._save()
                    return m

            mem = {
                "memory_id": f"mem-{uuid.uuid4().hex[:8]}",
                "user_id": user_id,
                "fact": fact.strip(),
                "category": category,
                "source_agent": source_agent,
                "session_id": session_id,
                "confidence": confidence,
                "timestamp": _now_iso(),
            }
            u["memories"].insert(0, mem)
            self._save()

        await self.broadcast_telemetry(
            "MEMORY_ADDED",
            {
                "user_id": user_id,
                "source_agent": source_agent,
                "session_id": session_id,
                "memory": mem,
                "summary": f"{source_agent} committed new memory to Universal Memory Bank: '{fact[:85]}'",
            },
        )
        return mem

    def get_memories(self, user_id: str, category: Optional[str] = None) -> List[Dict[str, Any]]:
        u = self.ensure_user(user_id)
        mems = u["memories"]
        if category:
            mems = [m for m in mems if m.get("category") == category]
        return mems

    # -------------------------------------------------------------------------
    # AUTOMATIC POST-TURN MEMORY & CONTEXT EXTRACTOR (`after_agent_callback`)
    # -------------------------------------------------------------------------
    async def auto_extract_and_sync_turn(
        self,
        user_id: str,
        session_id: str,
        agent_name: str,
        user_message: str,
        agent_response: str,
    ) -> List[Dict[str, Any]]:
        """
        Runs automatically after EVERY conversation turn in ANY session.
        Guarantees that even if the user just chats casually (e.g. 'hey Im carlos', 'add gate code #4321',
        or 'add 2 spicy tuna rolls'), the Memory Bank, `user:*` state, and Cross-Session Transcript Log
        are immediately updated so the next agent in another session has 100% real-time awareness!
        """
        extracted_memories = []
        u = self.ensure_user(user_id)

        # 1. Always record in the shared Cross-Session Live Turn Buffer (`user:recent_cross_session_turns`)
        recent_turns = u["universal_state"].get("user:recent_cross_session_turns", [])
        if not isinstance(recent_turns, list):
            recent_turns = []

        turn_entry = {
            "session_id": session_id,
            "agent": agent_name,
            "user_said": user_message[:220],
            "agent_replied": agent_response[:220],
            "timestamp": _now_iso(),
        }
        recent_turns.insert(0, turn_entry)
        u["universal_state"]["user:recent_cross_session_turns"] = recent_turns[:10]

        # 2. Use Gemini 3 Flash Preview to extract any semantic facts or state changes from this turn
        try:
            from google import genai
            client = genai.Client(
                vertexai=True,
                project=os.environ.get("GOOGLE_CLOUD_PROJECT", "vtxdemos"),
                location=os.environ.get("GOOGLE_CLOUD_LOCATION", "global"),
            )
            extractor_prompt = (
                "You are an Automatic Cross-Session Memory & State Extractor for a Universal Context Mesh.\n"
                f"Active User ID: {user_id}\n"
                f"Session ID: {session_id} | Active Agent: {agent_name}\n"
                f"USER MESSAGE: {user_message}\n"
                f"AGENT RESPONSE: {agent_response}\n\n"
                "Extract 1 to 2 concise semantic facts from what the USER stated or ordered or updated in this turn "
                "(e.g., user's name/identity, items ordered, delivery address/gate code, preferences, or financial/legal updates).\n"
                "Return ONLY valid JSON with this schema:\n"
                '{"facts": [{"fact": "string", "category": "order_or_profile_or_delivery_or_wealth"}], '
                '"profile_updates": {"full_name": "optional string if user stated their name"}, '
                '"order_updates": {"items_summary": "optional string", "delivery_notes_or_gate_code": "optional string"}}'
            )
            resp = client.models.generate_content(
                model=os.environ.get("GEMINI_MODEL", "gemini-3-flash-preview"),
                contents=extractor_prompt,
            )
            raw_text = (resp.text or "").strip()
            if raw_text.startswith("```"):
                raw_text = raw_text.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
            parsed = json.loads(raw_text)

            # Commit extracted facts to Memory Bank
            for fitem in parsed.get("facts", []):
                fact_str = fitem.get("fact", "").strip()
                if fact_str:
                    mem = await self.add_memory(
                        user_id=user_id,
                        fact=f"[{session_id}] {fact_str}",
                        category=fitem.get("category", "session_share"),
                        source_agent=f"{agent_name} (Auto-Extractor)",
                        session_id=session_id,
                    )
                    extracted_memories.append(mem)

            # Apply profile updates if detected (e.g. "hey Im carlos")
            prof_upd = parsed.get("profile_updates", {})
            if prof_upd and prof_upd.get("full_name"):
                await self.update_universal_state(
                    user_id=user_id,
                    namespace_key="user:profile",
                    updates={"full_name": prof_upd["full_name"]},
                    source_agent=f"{agent_name} (Auto-Extractor)",
                    session_id=session_id,
                )

            # Apply order/delivery updates if detected (e.g. restaurant ordering -> delivery agent share)
            ord_upd = parsed.get("order_updates", {})
            if ord_upd:
                if ord_upd.get("items_summary"):
                    await self.update_universal_state(
                        user_id=user_id,
                        namespace_key="user:active_order",
                        updates={
                            "latest_items_update": ord_upd["items_summary"],
                            "last_updated_session": session_id,
                            "last_updated_by": agent_name,
                        },
                        source_agent=f"{agent_name} (Auto-Extractor)",
                        session_id=session_id,
                    )
                if ord_upd.get("delivery_notes_or_gate_code"):
                    await self.update_universal_state(
                        user_id=user_id,
                        namespace_key="user:delivery_logistics",
                        updates={
                            "gate_code_or_notes": ord_upd["delivery_notes_or_gate_code"],
                            "last_updated_session": session_id,
                        },
                        source_agent=f"{agent_name} (Auto-Extractor)",
                        session_id=session_id,
                    )
        except Exception as e:
            # Fallback deterministic extraction if JSON parse fails
            fallback_fact = f"In session '{session_id}' with {agent_name}, user said: '{user_message[:120]}'"
            mem = await self.add_memory(
                user_id=user_id,
                fact=fallback_fact,
                category="live_session_turn",
                source_agent=f"{agent_name} (Auto-Sync)",
                session_id=session_id,
            )
            extracted_memories.append(mem)

        self._save()
        return extracted_memories

    # -------------------------------------------------------------------------
    # SHARED ARTIFACT VAULT (`UniversalArtifactVault`)
    # -------------------------------------------------------------------------
    async def save_artifact(
        self,
        user_id: str,
        filename: str,
        title: str,
        content: str,
        created_by_agent: str,
        session_id: str = "global",
        mime_type: str = "text/markdown",
        scope: str = "user:universal",
    ) -> Dict[str, Any]:
        """Saves a versioned artifact in the Universal Artifact Vault."""
        async with self._lock:
            u = self.ensure_user(user_id)
            existing_versions = [a["version"] for a in u["artifacts"] if a["filename"] == filename]
            next_version = max(existing_versions, default=0) + 1

            artifact = {
                "artifact_id": f"art-{uuid.uuid4().hex[:8]}-v{next_version}",
                "filename": filename,
                "title": title,
                "mime_type": mime_type,
                "version": next_version,
                "scope": scope,
                "created_by_agent": created_by_agent,
                "session_id": session_id,
                "timestamp": _now_iso(),
                "content": content,
            }
            u["artifacts"].insert(0, artifact)
            self._save()

        await self.broadcast_telemetry(
            "ARTIFACT_SAVED",
            {
                "user_id": user_id,
                "source_agent": created_by_agent,
                "session_id": session_id,
                "artifact_id": artifact["artifact_id"],
                "filename": filename,
                "version": next_version,
                "summary": f"{created_by_agent} published shared artifact `{filename}` (v{next_version})",
            },
        )
        return artifact

    def get_artifacts(self, user_id: str) -> List[Dict[str, Any]]:
        u = self.ensure_user(user_id)
        return u["artifacts"]

    # -------------------------------------------------------------------------
    # PROMPT INJECTION BUILDER (Universal Context Share for ADK Agents)
    # -------------------------------------------------------------------------
    async def build_universal_context_injection(
        self,
        user_id: str,
        requesting_agent: str,
        session_id: str,
    ) -> Dict[str, Any]:
        """
        Builds the Universal Context injection string containing:
        1. All `user:*` state namespaces from all agents (including `user:active_order`, `user:delivery_logistics`, `user:recent_cross_session_turns`)
        2. Cross-agent Memory Bank facts (highlighting facts created in OTHER sessions or by OTHER agents)
        3. Available Shared Artifacts
        """
        u = self.ensure_user(user_id)
        state = u["universal_state"]
        memories = u["memories"]
        artifacts = u["artifacts"]
        domain_mode = u.get("domain_mode", "wealth")

        cross_agent_memories = [m for m in memories if m.get("session_id") != session_id]
        all_injected_ids = [m["memory_id"] for m in memories[:15]]

        role_mapping_note = ""
        if domain_mode == "restaurant" or "carlos" in user_id.lower() or "restaurant" in user_id.lower():
            role_mapping_note = (
                "NOTE ON ACTIVE CUSTOMER DOMAIN (RESTAURANT ORDERING ↔ DELIVERY MESH):\n"
                "- If you are `wealth_agent` (:8011), act as the **Ordering & Menu Agent (`ordering_agent`)** handling food/drink orders, customizations, and `user:active_order`.\n"
                "- If you are `legal_tax_agent` (:8012), act as the **Delivery & Driver Logistics Agent (`delivery_agent`)** tracking courier ETA, gate codes, drop-off instructions, and reading what was ordered from `user:active_order`!\n"
                "- If you are `mobility_agent` (:8013), act as the **Kitchen & VIP Customer Support Agent (`support_agent`)** handling dietary allergies, modifications, and refunds.\n"
            )

        lines = [
            "================================================================================",
            f"UNIVERSAL USER CONTEXT MESH (SHARED REAL-TIME CONTEXT FOR USER: {user_id})",
            f"Current Active Runtime: {requesting_agent} | Active Session: {session_id}",
            "================================================================================",
            role_mapping_note,
            "1. LIVE CROSS-SESSION STATE (`user:*` namespace synchronized across ALL sessions):",
            json.dumps(state, indent=2),
            "",
            "2. UNIVERSAL MEMORY BANK & RECENT CROSS-SESSION FACTS (Discovered across peer sessions):",
        ]
        for m in memories[:15]:
            origin_tag = (
                f"[SHARED FROM SESSION '{m['session_id']}' by {m['source_agent']}]"
                if m.get("session_id") != session_id
                else f"[Current Session Memory]"
            )
            lines.append(f"  - ({m['category'].upper()}) {m['fact']} {origin_tag}")

        lines.append("")
        lines.append("3. SHARED UNIVERSAL ARTIFACT VAULT (Receipts, Tickets & Plans):")
        seen_files = set()
        for a in artifacts:
            if a["filename"] not in seen_files:
                seen_files.add(a["filename"])
                lines.append(
                    f"  - `{a['filename']}` (v{a['version']}) by {a['created_by_agent']}: {a['title']}"
                )
        lines.append("================================================================================")

        prompt_block = "\n".join(lines)

        await self.broadcast_telemetry(
            "MEMORY_INJECTED",
            {
                "user_id": user_id,
                "target_agent": requesting_agent,
                "session_id": session_id,
                "total_memories_injected": len(memories[:15]),
                "cross_agent_memories_count": len(cross_agent_memories),
                "cross_agent_sources": list({m["source_agent"] for m in cross_agent_memories}),
                "injected_memory_ids": all_injected_ids,
                "summary": (
                    f"Injected Universal Context into `{requesting_agent}` in session `{session_id}` "
                    f"({len(cross_agent_memories)} cross-session memories shared)"
                ),
            },
        )

        return {
            "prompt_block": prompt_block,
            "injected_memories": memories[:15],
            "cross_agent_memories": cross_agent_memories,
            "universal_state_snapshot": state,
        }

    # -------------------------------------------------------------------------
    # SESSION & MESSAGE TRACKING
    # -------------------------------------------------------------------------
    def ensure_session(self, user_id: str, session_id: str, target_agent: str, title: Optional[str] = None) -> Dict[str, Any]:
        u = self.ensure_user(user_id)
        if session_id not in u["sessions"]:
            u["sessions"][session_id] = {
                "session_id": session_id,
                "user_id": user_id,
                "target_agent": target_agent,
                "title": title or f"Session with {target_agent}",
                "created_at": _now_iso(),
                "updated_at": _now_iso(),
                "messages": [],
                "session_local_state": {
                    "session:created_by": target_agent,
                    "session:turn_count": 0,
                },
            }
            self._save()
        return u["sessions"][session_id]

    def append_message(
        self,
        user_id: str,
        session_id: str,
        target_agent: str,
        role: str,
        content: str,
        agent_name: str,
        tool_calls: Optional[List[Dict[str, Any]]] = None,
        a2a_trace: Optional[List[Dict[str, Any]]] = None,
        injected_memories: Optional[List[Dict[str, Any]]] = None,
        mutated_keys: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        sess = self.ensure_session(user_id, session_id, target_agent)
        sess["updated_at"] = _now_iso()
        sess["session_local_state"]["session:turn_count"] = sess["session_local_state"].get("session:turn_count", 0) + 1
        msg = {
            "message_id": f"msg-{uuid.uuid4().hex[:8]}",
            "timestamp": _now_iso(),
            "role": role,
            "agent_name": agent_name,
            "content": content,
            "tool_calls": tool_calls or [],
            "a2a_trace": a2a_trace or [],
            "injected_memories": injected_memories or [],
            "mutated_keys": mutated_keys or [],
        }
        sess["messages"].append(msg)
        self._save()
        return msg


# Global Singleton Engine
context_engine = UniversalContextEngine()
