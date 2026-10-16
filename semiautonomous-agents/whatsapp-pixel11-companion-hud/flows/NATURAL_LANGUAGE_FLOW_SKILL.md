# Natural-Language Flow Skill: Building the WhatsApp E2EE Companion & Pixel 11 Pro HUD

> **Target Audience:** Enterprise Solutions Architects, Customer Engineering Teams, and Autonomous Coding Agents  
> **Privacy Guarantee:** 100% Sanitized Reference Blueprint — Uses synthetic persona data (*"NYC AI Founders & Marathon Crew"*) with zero personal identifiers.

---

## 1. The Core Problem Statement (In Plain English)

Modern executive teams, founder circles, and high-trust social groups coordinate inside **End-to-End Encrypted (E2EE) WhatsApp Groups** where administrators enable **Advanced Chat Privacy**. When this setting is active:
1. In-chat cloud bots (such as `@Meta AI`) are completely blocked from reading or participating in the thread.
2. The mobile *"Export Chat"* button is disabled for all participants.
3. Standard WhatsApp Business API webhooks cannot attach to a user's personal or founder group chats.

At the same time, running an naive "auto-reply bot" inside a high-context human group immediately fails: if an agent replies in 2 seconds with generic AI phrasing, misreads a multi-line burst of messages, or cites an old message out of sequence, group members immediately spot the automation (`"bot detected"`).

**Our Goal:** Build a **Sovereign, Read-Only Co-Pilot & Psychometric Telemetry System** that:
- Ingests live decrypted messages from a linked companion browser into a local **SQLite WAL Ground Truth Ledger** (`whatsapp_truth.db`).
- Indexes 10,000+ historical and live messages into a **58.1-microsecond Hybrid FTS5 + RAM RAG** engine.
- Uses **Gemini 3.8 Flash** (`location="global"`) for sub-second live Q&A and multimodal vision/voice transcription, paired with **Gemini 4 Argon** (`location="global"`) for deep psychometric profiling and strategic coaching.
- Streams the entire experience to a **Pixel 11 Pro (`412×915` 120Hz OLED)** mobile app over 5G with **zero hallucinated quotes** and **100% human sovereignty**.

---

## 2. Step-by-Step Natural Language Flow

```text
┌──────────────────────────────────────────────────────────────────────────┐
│ STEP 1: LINKED CHROME 155 MULTI-DEVICE CDP INGESTION (PORT 9222)         │
│  • Links as an official WhatsApp Web companion device via QR / 8-char.   │
│  • Locks /tmp/wa_cdp_session.lock mutex so readers never race.           │
│  • Tags every row: 'peer' | 'human_manual' | 'historical_archive'.       │
└────────────────────────────────────┬─────────────────────────────────────┘
                                     ▼
┌──────────────────────────────────────────────────────────────────────────┐
│ STEP 2: BURST DEBOUNCE & SOVEREIGN PASSIVE LOCK (wait_for_next_msg.py)   │
│  • Waits 2–10s after a message arrives so friends finish multi-line      │
│    bursts before waking the AI co-pilot.                                 │
│  • Auto-send is permanently OFF; stages 3 contextual reply options.      │
└────────────────────────────────────┬─────────────────────────────────────┘
                                     ▼
┌──────────────────────────────────────────────────────────────────────────┐
│ STEP 3: 58.1µs HYBRID RAG + 2-TIER COGNITIVE BATCH ENGINE                │
│  • Queries SQLite FTS5 + RAM inverted index in 0.0581ms.                 │
│  • Tier-1 ($0.00 local regex) scores laughs, reactions & RLHF points.    │
│  • Tier-2 (50-msg idle batch on Gemini 3.8 Flash) updates 360° Brains.   │
└────────────────────────────────────┬─────────────────────────────────────┘
                                     ▼
┌──────────────────────────────────────────────────────────────────────────┐
│ STEP 4: PARALLEL MULTI-MODEL SUB-AGENTS (FIRST-READY STREAMING)          │
│  • Route A (Gemini 3.8 Flash): <1s synchronous Q&A & voice/video vision. │
│  • Route B (Gemini 4 Argon): Deep psychometric & negotiation synthesis.  │
└────────────────────────────────────┬─────────────────────────────────────┘
                                     ▼
┌──────────────────────────────────────────────────────────────────────────┐
│ STEP 5: DETERMINISTIC SQLITE STOP-HOOK CITATION VERIFIER                 │
│  • Checks every [wa_id:XXXX | HH:MM | WhatsApp | Sender]: "quote" tag    │
│    against whatsapp_truth.db before the turn is allowed to finish.       │
└────────────────────────────────────┬─────────────────────────────────────┘
                                     ▼
┌──────────────────────────────────────────────────────────────────────────┐
│ STEP 6: CLOUD RUN 5G REVERSE TUNNEL & PIXEL 11 PRO 120Hz HUD             │
│  • Pushes 55.7KB compressed deltas every 0.8s (0 LLM calls when idle).   │
│  • Renders minimizable Q#N->A#N threads & 5-Pillar Telemetry Glass.      │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Natural-Language Prompt Playbook (How to Instruct an Agent to Build Each Module)

### Prompt 1 — Building the Chrome CDP Ingestion & SQLite WAL Ledger
> *"Create a Python Chrome DevTools Protocol (CDP) bridge (`wa_cdp_engine.py`) that connects to a genuine non-headless Desktop Chrome instance on `127.0.0.1:9222` guarded by a file-level mutex `/tmp/wa_cdp_session.lock`. Enforce local timezone alignment via `Emulation.setTimezoneOverride`. Extract WhatsApp message rows (`[data-id]`, `[data-pre-plain-text]`, `.selectable-text`), quoted reply headers, and emoji reaction counts into a SQLite WAL database (`whatsapp_truth.db`). Stamp every message with an `origin` column: `'peer'` for incoming group messages, `'human_manual'` when `is_from_me=1` and sent from the user's physical phone, and `'historical_archive'` when harvested during nightly upward scrolling so historical backfills never trigger live message alerts."*

### Prompt 2 — Building the Read-Only Burst Listener & 3-Option Co-Pilot
> *"Create a reactive listener script (`wait_for_next_msg.py`) that monitors `whatsapp_truth.db` for new rows where `is_from_me = 0` and `origin != 'historical_archive'` with `id > baseline_id`. When a new message appears, wait in a debounce loop (`2.0s` to `5.0s`) until the sender finishes typing their multi-line burst. Do not auto-send any message to WhatsApp. Instead, invoke `gemini-3.8-flash` (`location='global'`) grounded in the last 30 group messages and the user's calendar to stage 3 natural reply options (`Executive/Analytical`, `Warm Crew`, and `Playful Banter`) in `ai_subtext_note`."*

### Prompt 3 — Building the 58.1µs Hybrid RAG & 2-Tier Batch Psychometric Profiler
> *"Build `wa_pack_hybrid_rag.py` and `wa_pack_cognitive_batch.py`. First, index all messages in a hybrid SQLite FTS5 virtual table (`wa_pack_rag_fts`) paired with an in-memory Python token inverted index for `<0.06ms` sub-millisecond retrieval. Second, implement a 2-Tier FinOps Batch Profiler: Tier 1 runs at `$0.00` locally using regex/lexical rules to score laugh triggers, verbosity, and Social RLHF points (`+3.0` per reaction, `+2.5` per laugh, `+3.5` per ally validation). Tier 2 waits for idle windows and sends 50 untagged messages in a single `gemini-3.8-flash` structured JSON call (saving 85% of input tokens) to update each member's 360° Brain Profile (`cognitive_archetype`, `sentiment_pos_pct`, `sentiment_neu_pct`, `sentiment_acid_pct`, `emotional_volatility`, `dopamine_hooks`, and `persuasion_playbook`)."*

### Prompt 4 — Configuring Parallel Sub-Agents (`Gemini 3.8 Flash` + `Gemini 4 Argon`) & Stop-Hook Guard
> *"Define two specialized sub-agents: (1) a Flash-Next Live RAG Auditor running on `gemini-3.8-flash` for `<1s` synchronous Q&A over `whatsapp_truth.db`, and (2) an Argon 4 Psychometrist running on `gemini-4-argon` (`gemini-launch-candidate-high`) for deep behavioral and strategic synthesis. Attach a deterministic `Stop` lifecycle hook (`verify_stop_hook.py`) that inspects every `[wa_id:XXXX | HH:MM | WhatsApp | Sender]: \"quote\"` citation in the response and blocks the turn if any quote does not match the exact single row in `whatsapp_truth.db`."*

### Prompt 5 — Building the Pixel 11 Pro 412×915 HUD & 5G Cloud Run Reverse Tunnel
> *"Build the mobile bridge (`server.py`, `renderer.py`, `cloud_tunnel_sync.py`, and `cyber_hud.html`) optimized for a `412x915` Pixel 11 Pro screen. Pre-compile Markdown, tables, and telemetry cards on the backend in `<2.5ms`. Render multi-message user questions as right-aligned collapsible threads (`Q#1 → A#1`, `Q#2 → A#2`) where `⚙️ Logs ▾` are minimized by default. Include a 4-way WhatsApp Studio switcher (`💬 Live`, `⚡ Split`, `📊 Crew 5-Pillar Telemetry Glass`, and `❖ Hub`) and sync state every `0.8s` outbound to Cloud Run with `0` idle LLM calls."*
