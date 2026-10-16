---
name: whatsapp-pixel11-companion-flow
description: >-
  Natural-language end-to-end architecture and replication flow skill for
  building a Zero-Trust Multi-Device WhatsApp Companion & 5-Pillar Psychometric
  Telemetry HUD for the Pixel 11 Pro (412x915 LTPO OLED), powered by Chrome 155
  CDP, SQLite WAL Ground Truth, 58.1µs Hybrid FTS5 + RAM RAG, Gemini 3.8 Flash,
  Gemini 4 Argon parallel sub-agents, deterministic Stop-Hook citation
  verification, and a Cloud Run 5G outbound reverse-tunnel.
---

# SKILL: WhatsApp Multi-Device CDP & Pixel 11 Pro Neural Companion Flow

This skill provides a **step-by-step natural-language architectural flow** so any engineer, customer, or AI coding agent can understand and replicate the **WhatsApp Multi-Device Companion & Pixel 11 Pro Neural HUD** from scratch without exposing any personal data or requiring official WhatsApp Business API migration.

---

## 🧭 Natural-Language Flow Overview (6-Stage Pipeline)

When asked to build, extend, or explain this system, follow these **6 natural-language flow stages** in order:

### Stage 1 — Bypassing "Advanced Chat Privacy" via Linked Multi-Device Chrome CDP
1. **Why Traditional Bots Fail:** When a WhatsApp group administrator enables *"Advanced Chat Privacy"*, in-group `@Meta AI` bots are blocked and *"Export Chat"* is disabled on mobile devices.
2. **How the Companion Solves It:** Instead of injecting a third-party bot number into the group, link a genuine desktop **Chrome 155** instance as an official **Multi-Device Companion** via QR code or 8-character pairing code on local port `9222`.
3. **Concurrency & Timezone Integrity:** Guard every Chrome DevTools Protocol (CDP) inspection behind a file-level mutex (`/tmp/wa_cdp_session.lock`) so background sync daemons and interactive tools never collide. Enforce `Emulation.setTimezoneOverride` so every message timestamp aligns deterministically with the user's local timezone.
4. **DOM Extraction & Origin Classification:** Parse modern WhatsApp Web `[data-id]`, `[data-pre-plain-text]`, `.selectable-text` bubbles, quoted reply headers, and emoji reaction badges (`reactions_json`) into a local **SQLite WAL Ground Truth Ledger (`whatsapp_truth.db`)**. Every row is stamped with an explicit `origin` tag:
   - `origin = 'peer'` — Incoming message from a group participant.
   - `origin = 'human_manual'` — Outgoing message typed by the user directly on their physical phone.
   - `origin = 'historical_archive'` — Older messages harvested during the progressive nightly upward-scroll crawl (`300 batches/night`) so historical backfill never triggers live push notifications.

### Stage 2 — Sovereign Safety Lock & Human-Presence Shadow Co-Pilot
1. **100% Read-Only Passive Monitoring by Default:** Fast-moving human group chats punish robotic latency or out-of-context replies. The companion daemon (`wa_qr_watcher.py` and `wait_for_next_msg.py`) runs in **strictly passive read-only mode** with autonomous auto-dispatch loops permanently stripped.
2. **Burst Debounce & Context Window:** When a new peer message arrives (`is_from_me = 0`), the listener waits for the natural typing burst to settle (`2–10s` quiet window) before waking the orchestrator.
3. **3-Option Co-Pilot Draft Staging:** For every incoming mention or topic shift, `gemini-3.8-flash` generates three contextual response drafts grounded in the user's calendar and group history:
   - `🧐 Executive / Analytical` (Crisp, high-signal factual or scheduling anchor)
   - `💬 Crew Warm / Collaborative` (High-warmth camaraderie)
   - `😏 Playful Banter` (Calibrated wit reserved strictly for playful peer threads)

### Stage 3 — 58.1-Microsecond Hybrid RAG & 2-Tier Batch Psychometric Engine
1. **Sub-Millisecond Hybrid Retrieval (`0.0581ms`):** Combine an in-memory Python inverted token index with **SQLite FTS5 BM25** (`wa_pack_rag_fts`) so any historical reference, inside joke, or multi-month thread is retrieved in **58.1 microseconds** without network round-trips.
2. **FinOps-Optimized 2-Tier Cognitive Profiling (`85%` GCP Token Savings):**
   - **Tier 1 (`$0.00` Local Scoring):** Instant regex and lexical heuristics compute message velocity, words-per-message verbosity, laugh triggers, emoji reaction yields, and **Social RLHF Reward Scores** (`+3.0` emoji reactions, `+2.5` group laughs, `+3.5` ally validations, `+4.0` concise high-status anchor bonus, `-6.0` repetitive pattern penalty).
   - **Tier 2 (Idle 50-Message Batching on `gemini-3.8-flash`):** During idle windows, unassigned messages are grouped into batches of 50 and analyzed in a single structured JSON call on Vertex AI `gemini-3.8-flash` (`location="global"`), populating `wa_pack_message_metadata` and `wa_pack_brain_profiles` (Cognitive Archetype, Sentiment Polarity `+pos% / neu% / -acid%`, Emotional Volatility, Dopamine Hooks, and Persuasion Playbook).

### Stage 4 — Parallel Multi-Model Sub-Agent Routing (`Gemini 3.8 Flash` + `Gemini 4 Argon`)
1. **Task Complexity Split:**
   - **Fast Synchronous Q&A (`gemini-3.8-flash`):** Live "What are they talking about right now?" or "Verify when Marcus proposed dinner" queries route to a Flash-Next sub-agent that queries `whatsapp_truth.db` and returns in `< 1 second`.
   - **Deep Psychometric & Multi-Thread Strategy (`gemini-4-argon`):** Complex group dynamics, negotiation leverage, and multi-participant behavioral audits route concurrently to a **Gemini 4 Argon** (`gemini-launch-candidate-high`) sub-agent.
2. **First-Ready Out-of-Order Delivery:** Sub-agents execute concurrently and stream their answers into the Pixel 11 Pro HUD in **first-ready sequence** (`Q#1 → A#1`, `Q#2 → A#2`) so a fast lookup is never blocked behind a deep reasoning turn.

### Stage 5 — Deterministic Zero-Hallucination Lifecycle Hooks
1. **`PreInvocation` Compaction Guard:** Whenever a long agent session compacts its context window, the `PreInvocation` hook injects the latest verified row IDs from `whatsapp_truth.db` so the model never loses its chronological anchor.
2. **`Stop` Verbatim Citation Verifier:** Before any agent response is released to the user, `verify_stop_hook.py` parses every `[wa_id:XXXX | HH:MM | WhatsApp | Sender]: "quote"` tag and verifies that the exact substring exists in that single row of `whatsapp_truth.db`. Merging multiple rows with ellipses (`...`) or fabricating a quote immediately blocks the turn and forces a self-correction.

### Stage 6 — Outbound 5G Cloud Run Reverse-Tunnel & Pixel 11 Pro 120Hz HUD
1. **Zero-Inbound-Port Reverse Tunnel (`cloud_tunnel_sync.py`):** A persistent `systemd` user service checks local file modification times every `800ms` (`0` LLM calls when idle), reads unflushed protobuf steps directly from SQLite in `< 0.4ms`, compresses incremental SSE deltas by `98.8%` (`55.7 KB`), and pushes state outbound to a single-instance **Cloud Run** relay protected by 2FA TOTP and 5-minute burn-after-reading QR pairing tickets.
2. **Pixel 11 Pro 412×915 Touch Ergonomics (`cyber_hud.html` + `renderer.py`):**
   - Pre-compiles Markdown, tables, and declarative blocks into native mobile HUD cards in `< 2.5ms`.
   - Pairs each user question directly with its answer (`Q#N → A#N`) while keeping `⚙️ Logs (N) ▾` minimized by default.
   - Prevents wake-from-sleep scroll jumps via deterministic state signature diffing and releases the Screen WakeLock the instant an LLM turn finishes.

---

## 📂 Complete Flow Documentation & Reference Files
- **[`flows/NATURAL_LANGUAGE_FLOW_SKILL.md`](flows/NATURAL_LANGUAGE_FLOW_SKILL.md)** — Conversational natural-language walkthrough of every data flow and decision gate.
- **[`docs/LOW_LEVEL_DESIGN.md`](docs/LOW_LEVEL_DESIGN.md)** — Low-level database schemas, mutex locking, SQLite protobuf decoding, and FinOps math.
- **[`README.md`](README.md)** — Visual showcase with Pixel 11 Pro hardware-framed screenshots and high-DPI architecture diagrams.
