---
name: replicating-lexgraph-spanner-mcp-app
description: Orchestrates the end-to-end replication, Cloud Spanner Hybrid GraphRAG provisioning, SEP-1865 MCP App Cloud Run deployment, and Gemini Enterprise Default Assistant registration for the LexGraph Interactive Legal Grid & Citation Highlighter. Use when the user asks to replicate, deploy, customize, or test the LexGraph Spanner GraphRAG MCP App or A2UI Legal Cockpit.
---

# Replicating the LexGraph Spanner Hybrid GraphRAG & MCP App (SEP-1865)

This skill guides the agent through deploying, testing, or customizing the **LexGraph Interactive Legal Document Grid & Citation Highlighter MCP App (`semiautonomous-agents/lexgraph-spanner-mcp-app`)**.

## When to Use This Skill
- Deploying or replicating the **LexGraph Legal Grid MCP App (SEP-1865)** in Gemini Enterprise.
- Provisioning **Cloud Spanner Graph (`LexGraphLegalGraph`)** with **3,072-dim `gemini-embedding-2` vector search**, **Spanner Full-Text Search (`TOKENLIST`)**, **Reciprocal Rank Fusion (RRF)**, and **0-ms Intapp Ethical Wall pruning**.
- Building or modifying an interactive **Dual-Surface MCP App** (`ui://lexgraph/legal-grid-workspace.html`) with dynamic question-driven column extraction, 0-ms per-column filtering, row checkbox scoping, and a right-hand **Original Contract Citation Highlighter**.

## Workflow Checklist
- [ ] **Step 1: Compile Demo Legal Corpus (`demo-documents/`)**
  - Run `python3 semiautonomous-agents/lexgraph-spanner-mcp-app/demo-documents/generate_demo_pdfs.py`.
- [ ] **Step 2: Provision & Seed Cloud Spanner Hybrid GraphRAG (`spanner-graphrag/`)**
  - Run `uv run semiautonomous-agents/lexgraph-spanner-mcp-app/spanner-graphrag/provision_spanner_graph.py`.
  - Run `uv run semiautonomous-agents/lexgraph-spanner-mcp-app/spanner-graphrag/seed_spanner_graph.py`.
- [ ] **Step 3: Deploy MCP App Server to Cloud Run (`mcp-app-grid-server/`)**
  - Run `gcloud run deploy lexgraph-legal-grid-mcp-agent --source=semiautonomous-agents/lexgraph-spanner-mcp-app/mcp-app-grid-server --project=${GOOGLE_CLOUD_PROJECT:-vtxdemos} --region=us-central1 --allow-unauthenticated --no-cpu-throttling --quiet`.
- [ ] **Step 4: Register Custom MCP Connector in Gemini Enterprise**
  - Run `uv run semiautonomous-agents/lexgraph-spanner-mcp-app/mcp-app-grid-server/register_custom_mcp_connector.py`.
- [ ] **Step 5: Verify Live Streamable HTTP JSON-RPC 2.0 (`POST /mcp`)**
  - Verify `tools/call` (`open_legal_analysis_grid`) and `resources/read` (`< 100ms` latency via `LATEST_WORKSPACE_STATE` cache).

## Critical Guardrails
1. **Never Call `element.scrollIntoView()` Inside an MCP App Guest Iframe**: Lock `html, body { position: fixed; inset: 0; overflow: hidden; }` (`lockRootViewport()`) and scroll only `#doc-paper-scroll` via `scrollEl.scrollTo()`.
2. **Instant `resources/read` (< 100ms)**: Serve `LATEST_WORKSPACE_STATE` in `resources/read` so Gemini Enterprise's `<ucs-mcp-apps>` never blocks on a 24-second spinner.
