# ADK // StreamAssist Enterprise Session & MemoryBank Workbench

This project implements and verifies the **3-Tier Session & Long-Term Memory Architecture** combining a **Custom UI**, **Google ADK**, **Vertex AI Memory Bank (`VertexAiMemoryBankService`)**, and **Gemini Enterprise `StreamAssist`** with federated Microsoft 365 (SharePoint/Outlook) connectors.

## 1. Past Conversation History (Resumable IDs)

- **Primary Architecture & Live Workbench Build (Sep 21, 2026 — 136 steps):**
  - Conversation ID: `4cc59580-8981-4643-a320-07da4ba342f2`
  - Resume inside CLI: `/resume 4cc59580-8981-4643-a320-07da4ba342f2`
  - Resume from shell: `jetski --conversation 4cc59580-8981-4643-a320-07da4ba342f2`
  - Full Transcript: [transcript_full.jsonl](file:///usr/local/google/home/jesusarguelles/.gemini/jetski/brain/4cc59580-8981-4643-a320-07da4ba342f2/.system_generated/logs/transcript_full.jsonl)
- **Internal Google3 `StreamAssist` + ADK MemoryBank Deep Research Subagent (Sep 21, 2026):**
  - Conversation ID: `ad866e2f-e04d-47b1-8430-e27adda3a001`
  - Full Transcript: [transcript_full.jsonl](file:///usr/local/google/home/jesusarguelles/.gemini/jetski/brain/ad866e2f-e04d-47b1-8430-e27adda3a001/.system_generated/logs/transcript_full.jsonl)
- **History Discovery & Summary Session (Sep 30, 2026):**
  - Conversation ID: `ceb9a15b-041b-41a7-9594-bb39e9ddbe82`
  - Full Transcript: [transcript_full.jsonl](file:///usr/local/google/home/jesusarguelles/.gemini/jetski/brain/ceb9a15b-041b-41a7-9594-bb39e9ddbe82/.system_generated/logs/transcript_full.jsonl)

## 2. Project Files & Entrypoints

- **Backend Orchestrator (Port `8787`):** [backend/main.py](file:///usr/local/google/home/jesusarguelles/vertex-ai-samples/semiautonomous-agents/adk-streamassist-memory-workbench/backend/main.py)
  - `EnterpriseSessionOrchestrator`: Manages Tier 1 (`temp:*` RAM scratchpad), Tier 2 (`adk_events` + Discovery Engine `v1alpha` `Session` + Gemini 2.5 Flash rolling compaction), and Tier 3 (`memory_bank` with strict ACL provenance filtering: `PERSISTED_USER_PREF` vs. `BLOCKED_ACL_DOCUMENT_FACT`).
- **Frontend UI (2-Tab Vercel Monochrome Studio):** [frontend/index.html](file:///usr/local/google/home/jesusarguelles/vertex-ai-samples/semiautonomous-agents/adk-streamassist-memory-workbench/frontend/index.html)
  - **Tab 1 (`01 // Architecture & Topology`):** Interactive 4-Plane SVG schematic + 4-State Lifecycle Finite State Machine (`ACTIVE` -> `IDLE_COMPACTED` -> `DORMANT_LOGGED_OUT` -> `RE-HYDRATED`).
  - **Tab 2 (`02 // Live Session & Memory Workbench`):** Live chat with `StreamAssist`, lifecycle state triggers, and 4-subtab Live 3-Tier Memory Inspector (`Tier 1: RAM`, `Tier 2: GE`, `Tier 3: Bank`, `cURL`).
- **Environment Config:** [.env](file:///usr/local/google/home/jesusarguelles/vertex-ai-samples/semiautonomous-agents/adk-streamassist-memory-workbench/.env)
- **SQLite State Store:** [data/workbench_state.db](file:///usr/local/google/home/jesusarguelles/vertex-ai-samples/semiautonomous-agents/adk-streamassist-memory-workbench/data/workbench_state.db)

## 3. Core Architectural invariants

1. **Tier 1 — Working State (`session.state` + `temp:*` RAM):**
   - Ephemeral document buffers (`temp:w1_document_cache`, capped at 64 MB / 10 MB per doc) and per-user OAuth/WIF tokens are purged immediately on turn completion or idle compaction.
2. **Tier 2 — Episodic Session Store (`VertexAiSessionService` / SQLite + GE `Session`):**
   - Stores verbatim turn events, citation metadata (`Reference.content` + `DocumentMetadata`), and rolling `EventsCompactionConfig` summaries (`retrieved_context` is stripped before Spanner commit per `assist_answer.proto`).
3. **Tier 3 — Long-Term Memory Bank (`VertexAiMemoryBankService`):**
   - Persists **only** user-scoped preferences and entity aliases (`PERSISTED_USER_PREF`).
   - **Never** persists raw SharePoint/Outlook document facts (`BLOCKED_ACL_DOCUMENT_FACT`) so live Microsoft Graph ACL validation in `StreamAssist` remains authoritative on every turn.
