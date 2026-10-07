---
name: replicating-lexgraph-spanner-mcp-app
description: Orchestrates the end-to-end replication, Cloud Spanner Hybrid GraphRAG provisioning, SEP-1865 MCP App Cloud Run deployment, and Gemini Enterprise Default Assistant registration for the LexGraph Interactive Legal Grid & Citation Highlighter. Use when the user asks to replicate, deploy, customize, or test the LexGraph Spanner GraphRAG MCP App or A2UI Legal Cockpit.
---

# Replicating the LexGraph Spanner Hybrid GraphRAG & MCP App (SEP-1865)

This skill enables any autonomous coding agent (**Jetski**, **Antigravity**, **Claude Code**, or **OpenAI Codex**) to replicate the complete **LexGraph Interactive Legal Document Grid & Original Citation Highlighter MCP App** from scratch using natural language or automated scripts.

## When to Use This Skill
- Deploying or replicating the **LexGraph Legal Grid MCP App (SEP-1865)** in a new or existing GCP project.
- Provisioning **Cloud Spanner Graph (`LexGraphLegalGraph`)** with **3,072-dim `gemini-embedding-2` vector search**, **Spanner Full-Text Search (`TOKENLIST`)**, **Reciprocal Rank Fusion (RRF)**, and **0-ms Intapp Ethical Wall pruning**.
- Building an interactive **Dual-Surface MCP App** (`ui://lexgraph/legal-grid-workspace.html`) with dynamic question-driven column extraction, 0-ms per-column filtering, row checkbox scoping, and a right-hand **Original Contract Citation Highlighter** with opposing counsel redlines.
- Linking a Cloud Run MCP Server as a **Custom MCP Data Connector** to **Gemini Enterprise's Default Assistant** (`default_assistant`).

---

## Architecture Topology

```text
┌──────────────────────────────────────────────────────────────────────────┐
│  1. GEMINI ENTERPRISE HOST (Default Assistant + <ucs-mcp-apps> Iframe)   │
│     • Left Pane: Conversational Chat Reasoning (Gemini 3.8 Flash / 4 Pro)│
│     • Right PiP / Fullscreen: Interactive Guest UI (ui://lexgraph/*.html)    │
└───────────────────────────────────┬──────────────────────────────────────┘
                                    │ Streamable HTTP JSON-RPC 2.0 (POST /mcp)
                                    ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  2. CLOUD RUN MCP APP SERVER (lexgraph-legal-grid-mcp-agent)                 │
│     • SEP-1865 Tools: open_legal_analysis_grid, inspect_selected_files,  │
│       grant_teammate_email_30d                                           │
│     • Instant (<90ms) resources/read via LATEST_WORKSPACE_STATE cache    │
│     • Fast (<1.5s) Gemini dynamic column extraction (thinking_budget=0)  │
└───────────────────────────────────┬──────────────────────────────────────┘
                                    │ Single-Pass SQL + ISO GQL + RRF
                                    ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  3. CLOUD SPANNER HYBRID GRAPHRAG (lexgraph-legal-spanner / lexgraph-legal-ctx)  │
│     • Graph Traversal: (Lawyers)-[:AUTHORIZED_FOR]->(Matters)            │
│     • Ethical Wall Pruning: NOT EXISTS (:ETHICAL_WALL_BLOCK) at 0ms      │
│     • Dense Vector: COSINE_DISTANCE(embedding, gemini-embedding-2 3072d) │
│     • Lexical BM25: SCORE(fts_tokens, query)                             │
│     • Write-Back: ACID 30-day TeammateGrants edge commit (EM-9901)       │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## Step-by-Step Execution Checklist

Copy and track this checklist during execution:

- [ ] **Step 1: Environment & Pre-Flight Checks**
  - Verify `GOOGLE_CLOUD_PROJECT` (default: `vtxdemos`), `REGION` (`us-central1`), and `SPANNER_INSTANCE` (`lexgraph-legal-spanner`).
  - Enable required APIs: `spanner.googleapis.com`, `run.googleapis.com`, `aiplatform.googleapis.com`, `discoveryengine.googleapis.com`.
- [ ] **Step 2: Generate Demo Legal Documents (PDF + TXT)**
  - Run `python3 demo-documents/generate_demo_pdfs.py` to compile all 8 M&A / Credit / NDA PDFs and 9 text contracts.
- [ ] **Step 3: Provision & Seed Cloud Spanner Hybrid GraphRAG**
  - Run `uv run spanner-graphrag/provision_spanner_graph.py` to create the Spanner instance, database, tables, `ClausesFtsIdx` search index, and `LexGraphLegalGraph` property graph.
  - Run `uv run spanner-graphrag/seed_spanner_graph.py` to compute live 3,072-dim `gemini-embedding-2` vectors and insert lawyers, matters, documents, clauses, and Intapp wall edges.
- [ ] **Step 4: Deploy MCP App Server to Cloud Run**
  - Deploy `mcp-app-grid-server/` with `--allow-unauthenticated --no-cpu-throttling`:
    ```bash
    gcloud run deploy lexgraph-legal-grid-mcp-agent \
      --source=mcp-app-grid-server \
      --project=${GOOGLE_CLOUD_PROJECT:-vtxdemos} \
      --region=us-central1 \
      --allow-unauthenticated \
      --no-cpu-throttling \
      --quiet
    ```
- [ ] **Step 5: Register Custom MCP Connector in Gemini Enterprise**
  - Run `uv run mcp-app-grid-server/register_custom_mcp_connector.py` to create/update the `CUSTOM_MCP` DataConnector (`lexgraph-legal-grid-mcp-app`), bind its DataStore to the Gemini Enterprise Engine (`default_search`), and grant `roles/run.invoker` to the Discovery Engine service agent.
- [ ] **Step 6: Verify JSON-RPC & Viewport Scroll-Lock**
  - Test `POST /mcp` (`tools/call` and `resources/read`) and verify `resources/read` returns in `< 100ms` with `lockRootViewport` enabled and zero `scrollIntoView()` calls.

---

## Critical Engineering Guardrails (Must Enforce)

1. **Never Call `element.scrollIntoView()` Inside an MCP App Guest Iframe**:
   - `scrollIntoView()` scrolls ancestor containers including the iframe's root `<html>` document, pushing the top header and grid off-screen when `<body>` has `overflow: hidden`.
   - Always lock `html, body { position: fixed; inset: 0; overflow: hidden; }` and scroll only the internal document container (`#doc-paper-scroll.scrollTo({ top, behavior: "smooth" })`).
2. **Instant `resources/read` (< 100ms)**:
   - Gemini Enterprise's `<ucs-mcp-apps>` shows a blocking loading spinner while `fetchAppResource` calls `resources/read`. Cache `LATEST_WORKSPACE_STATE` during `tools/call` so `resources/read` returns the hydrated HTML immediately without re-running an LLM call.
3. **Responsive PiP (`~680px`) & Fullscreen (`>1000px`) Dual-Surface Layout**:
   - Provide header view-switcher pills (`◫ Split`, `📊 Grid`, `📑 Citation Doc`) and a compact 1-line Scoped Q&A bar at the bottom of the Grid pane so the Document Grid never gets crushed vertically in right-side PiP mode.
