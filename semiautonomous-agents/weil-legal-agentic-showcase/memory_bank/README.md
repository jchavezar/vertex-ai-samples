# Weil, Gotshal & Manges LLP — Centralized Firestore RAG MemoryBank

> **GCP Project**: `vtxdemos`  
> **Firestore Collections**: `weil_memory_bank` (226+ embedded RAG documents) & `weil_sessions_registry` (10 indexed Jetski sessions)  
> **Embedding Model**: Vertex AI `text-embedding-005` (768-dimensional vectors)  
> **Synthesis Model**: Vertex AI `gemini-3.8-flash` (Zero-Obsolete-Model Policy)

---

## 🎯 Purpose: One Single Source of Truth ("Details Over the Details")

This module implements a centralized **Retrieval-Augmented Generation (RAG) MemoryBank** backed by **Google Cloud Firestore** in project `vtxdemos`. It consolidates **every single conversation, stakeholder profile, architectural decision, 5-step ADK walkthrough script, 5-act website modernization recipe, slide deck, and runbook** built for **Weil, Gotshal & Manges LLP** across all 10 historical Jetski sessions into one queryable memory bank.

Any single Jetski session or Google ADK agent can query this MemoryBank to retrieve 100% granular recall without switching sessions or losing context.

---

## 🗄️ Firestore Database Schema (`vtxdemos`)

### 1. Collection: `weil_memory_bank`
Stores granular, embedded RAG documents across 5 structured categories:
- `executive_context_and_stakeholders`: Complete profiles & technical priorities for Weil leadership (**Andrew Simon** CIO, **Ian Miller** Head of Tech Architecture, **Steve Kedem**, **Daulton Cockerell**, **Ravi**) and the Google Cloud team (**Jesus Chavez**, **Roberto Santana**, **Sofi Mehta**, **Brian Squibb**, **Farzan & Luke**, **Eran Lewis**, **Jagan Athreya**).
- `workshop_agenda_and_strategy`: Complete minute-by-minute schedule, session ownership, and talking points for the September 9, 2026 Google Cloud Campus EBC workshop.
- `architectural_decisions_and_use_cases`: Deep-dive specifications on **Privacy Pro ("Legal Legos")**, **SCS Benchmark Platform**, **Deterministic Ethical Walls (`EW-7809-BIO`, `EW-9912-OMG`)**, **Antigravity Computational Law MicroVM Sandbox**, **Gemma 2/4 frozen tissue-paper apps vs. Gemini 3.7/3.8 Flash**, and strict Zero-Copilot / Zero-Obsolete-Model policies.
- `walkthrough_curriculum_01_to_05`: Full code & architecture breakdowns of all 5 scripts (`01_basic_adk_agent.py`, `02_adk_with_mcp_bigquery.py`, `03_deploy_to_agent_runtime.py`, `04_agent_evaluation.py` 3-stage Quality Flywheel, and `05_a2a_orchestration.py` distributed Starlette/Uvicorn A2A servers on ports 8094/8095).
- `modernization_portal_5_acts`: Complete documentation & port map (`5173`, `8000`, `8089`, `8094`, `8095`) for the 5-Act `weil.com` modernization demo.
- `cross_session_conversation_history`: Every single Q&A turn harvested across all **10 Jetski conversation transcripts** (`3a7bfad2...`, `0e811986...`, `006dd831...`, `2f29bcd8...`, `95f2e256...`, `da963b94...`, `c5b3b672...`, `4bb3c7a1...`, `5a619144...`, `0e98ba3b...`).
- `repository_documentation`: Full chunked text of all markdown docs, executive slide decks, and scripts.

### 2. Collection: `weil_sessions_registry`
Stores session-level metadata for all 10 Jetski conversations (`conversation_id`, `first_timestamp`, `last_timestamp`, `total_steps`, `total_user_turns`, and `user_prompts_preview`).

---

## 🚀 Usage & Commands

### 1. Re-Ingest / Sync All Knowledge & Conversations to Firestore
```bash
python3 memory_bank/ingest_to_firestore.py
```

### 2. Inspect Live Firestore MemoryBank Statistics & Session Registry
```bash
python3 memory_bank/query_memory_bank.py --stats
```

### 3. Run Hybrid RAG Search + Grounded `gemini-3.8-flash` Synthesis
```bash
python3 memory_bank/query_memory_bank.py \
  --query "Explain all details of Step 4 evaluation and Step 5 A2A microservices for Weil" \
  --top-k 5 \
  --synthesize
```

### 4. Use as a Native Google ADK Function Tool
```python
from google.adk.agents import LlmAgent
from memory_bank.query_memory_bank import search_weil_memory_bank

weil_memory_agent = LlmAgent(
    name="weil_institutional_memory_agent",
    model="gemini-3.8-flash",
    tools=[search_weil_memory_bank],
    instruction="Use search_weil_memory_bank to recall any Weil stakeholder, conversation, or code detail.",
)
```
