# CLAUDE.md — LexGraph Spanner Hybrid GraphRAG & MCP App (SEP-1865) Blueprint

You are operating inside `semiautonomous-agents/lexgraph-spanner-mcp-app`. This project implements the **LexGraph Enterprise Legal LLP Interactive Legal Document Grid & Citation Highlighter** powered by **Cloud Spanner Hybrid GraphRAG** and the **Model Context Protocol (MCP) Apps Standard (SEP-1865)** inside **Gemini Enterprise**.

## Core Architecture & Invariants

1. **Cloud Spanner Hybrid GraphRAG (`spanner-graphrag/`)**:
   - Instance: `lexgraph-legal-spanner` | Database: `lexgraph-legal-context` | Graph: `LexGraphLegalGraph`.
   - Single-pass SQL + ISO GQL query combines:
     1. **0-ms Intapp Ethical Wall Pruning** (`NOT EXISTS (EthicalWallBlocks)` blocks `DOC-M999-WALL` before retrieval).
     2. **3,072-dim Dense Vector Search** (`COSINE_DISTANCE` via Vertex AI `gemini-embedding-2`).
     3. **Lexical BM25 Full-Text Search** (`SCORE(fts_tokens, query)` via `ClausesFtsIdx`).
     4. **Reciprocal Rank Fusion (RRF)**: `1/(60 + vec_rank) + 1/(60 + fts_rank)`.
   - **ACID Write-Back**: `execute_spanner_teammate_grant()` commits a 30-day temporal `TeammateGrants` graph edge unlocking unfiled partner email `EM-9901`.

2. **MCP App Server (`mcp-app-grid-server/`)**:
   - Implements Streamable HTTP JSON-RPC 2.0 at `POST /mcp` (`initialize`, `tools/list`, `tools/call`, `resources/list`, `resources/read`).
   - Tool `_meta.ui` binds `resourceUri: "ui://lexgraph/legal-grid-workspace.html"` (`mimeType: "text/html;profile=mcp-app"`, `defaultDisplayMode: "pip"`).
   - **Latency Guardrail**: `resources/read` MUST return in `< 100ms` by reading `LATEST_WORKSPACE_STATE` cached during `tools/call`. Never run a blocking LLM call inside `resources/read`.
   - **Gemini Extraction**: Uses `gemini-3.8-flash` with `thinking_budget=0` and a 4.5s timeout falling back to `_build_question_aware_fallback()`.

3. **Guest UI (`mcp-app-grid-server/ui_template.py`)**:
   - **Vercel Monochrome Architecture**: Light Mode default (`:root`), dynamic `🌙 Dark / ☀️ Light` toggle (`[data-theme="dark"]`), and Claude-Code Shrinking & Shining Ink loader (`.shrinking-shining-ink`).
   - **Iframe Viewport Scroll-Lock**: `html, body` MUST have `position: fixed; inset: 0; overflow: hidden;` and `lockRootViewport()`. NEVER call `element.scrollIntoView()` (which scrolls the outer iframe `<html>` and clips the header/grid). Scroll only `#doc-paper-scroll` via `scrollEl.scrollTo({ top, behavior: "smooth" })`.
   - **Dual-Surface Layout**: Includes `[◫ Split | 📊 Grid | 📑 Citation Doc]` view-mode switcher buttons so both Right-Side PiP (`~680px`) and Fullscreen (`>1000px`) render with zero vertical crushing.

## Standard Commands

```bash
# 1. Generate 8 Demo PDFs & 9 Text Contracts
python3 demo-documents/generate_demo_pdfs.py

# 2. Provision & Seed Cloud Spanner GraphRAG
uv run spanner-graphrag/provision_spanner_graph.py
uv run spanner-graphrag/seed_spanner_graph.py

# 3. Deploy MCP App Server to Cloud Run
gcloud run deploy lexgraph-legal-grid-mcp-agent \
  --source=mcp-app-grid-server \
  --project=${GOOGLE_CLOUD_PROJECT:-vtxdemos} \
  --region=us-central1 \
  --allow-unauthenticated \
  --no-cpu-throttling \
  --quiet

# 4. Link Custom MCP Connector to Gemini Enterprise Default Assistant
uv run mcp-app-grid-server/register_custom_mcp_connector.py
```
