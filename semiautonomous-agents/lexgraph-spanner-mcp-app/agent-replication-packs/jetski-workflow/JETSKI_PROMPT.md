# 🚀 Jetski Natural-Language Replication Prompt & Dynamic Workflow

Copy and paste the natural-language prompt below into **Jetski** to replicate or redeploy the entire **LexGraph Spanner Hybrid GraphRAG + MCP App (SEP-1865)** architecture automatically using parallel and pipeline subagents.

---

## Option A: One-Line Dynamic Workflow Execution
> Run the dynamic workflow at `semiautonomous-agents/lexgraph-spanner-mcp-app/agent-replication-packs/jetski-workflow/replicate_lexgraph_mcp_app_workflow.py` using `run_workflow`.

---

## Option B: Full Natural-Language Blueprint Prompt (Zero-to-Production)

```text
Act as a Principal Google Cloud AI Architect. Replicate the complete "LexGraph Interactive Legal Document Grid & Citation Highlighter MCP App (SEP-1865)" coupled with Cloud Spanner Hybrid GraphRAG inside `semiautonomous-agents/lexgraph-spanner-mcp-app`:

1. LEGAL CORPUS GENERATION (`demo-documents/`):
   - Execute `python3 demo-documents/generate_demo_pdfs.py` to compile all 8 synthetic M&A, Private Equity, Credit, and NDA contracts (`DOC-M331-01` through `DOC-M109-01`) into print-ready PDFs (`demo-documents/pdf/`) and plain-text files (`demo-documents/text/`), plus the unfiled tax email `EM-9901`.

2. CLOUD SPANNER HYBRID GRAPHRAG (`spanner-graphrag/`):
   - Provision Cloud Spanner instance `lexgraph-legal-spanner` and database `lexgraph-legal-context` using `provision_spanner_graph.py` with node tables (`Lawyers`, `Matters`, `Documents`, `Clauses`, `UnfiledEmails`), edge tables (`LawyerAuthorizedMatter`, `EthicalWallBlocks`, `TeammateGrants`), FTS search index `ClausesFtsIdx`, and ISO GQL property graph `LexGraphLegalGraph`.
   - Seed all nodes, edges, and live 3,072-dimension `gemini-embedding-2` vectors using `seed_spanner_graph.py`. Verify that `DOC-M999-WALL` is automatically blocked at 0ms by `EthicalWallBlocks` for `s-jenkins@lexgraph.com`.

3. MCP APP SEP-1865 SERVER & DUAL-SURFACE UI (`mcp-app-grid-server/`):
   - Ensure `app.py` exposes Streamable HTTP JSON-RPC 2.0 at `POST /mcp` (`initialize`, `tools/list`, `tools/call`, `resources/read`) with `_meta.ui.resourceUri = "ui://lexgraph/legal-grid-workspace.html"` and `defaultDisplayMode = "pip"`.
   - Enforce instant (<100ms) `resources/read` via `LATEST_WORKSPACE_STATE` caching and fast (<1.5s) Gemini dynamic column extraction (`thinking_budget=0`).
   - Enforce Vercel Monochrome UI (Light Mode default + Dark Mode toggle + Claude-Code shrinking & shining ink loader), root viewport scroll-lock (`position: fixed; inset: 0; overflow: hidden;` with zero `scrollIntoView()` calls), and responsive `[◫ Split | 📊 Grid | 📑 Citation Doc]` view-mode switching for both PiP (~680px) and Fullscreen (>1000px).
   - Deploy `lexgraph-legal-grid-mcp-agent` to Cloud Run (`us-central1`, `--allow-unauthenticated`, `--no-cpu-throttling`).

4. GEMINI ENTERPRISE DEFAULT ASSISTANT LINKING:
   - Run `register_custom_mcp_connector.py` to register the `CUSTOM_MCP` DataConnector (`lexgraph-legal-grid-mcp-app`) in Discovery Engine, bind its DataStore to the Gemini Enterprise Engine (`default_search`), and verify HTTP 200 across all `/mcp` JSON-RPC methods.
```
