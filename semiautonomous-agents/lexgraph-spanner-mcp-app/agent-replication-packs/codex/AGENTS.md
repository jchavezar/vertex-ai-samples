# AGENTS.md — OpenAI Codex CLI & Autonomous Agent Specification

## Project Overview
`lexgraph-spanner-mcp-app` is a production reference implementation for extending **Google Cloud Gemini Enterprise (Discovery Engine)** with an interactive **Model Context Protocol (MCP) App (SEP-1865)** backed by **Cloud Spanner Hybrid GraphRAG** (`LexGraphLegalGraph` + 3,072-dim `gemini-embedding-2` + Spanner FTS + Reciprocal Rank Fusion).

## Directory Map
- `demo-documents/`: 8 synthetic M&A / Private Equity / Credit / NDA PDFs (`pdf/`), plain-text contracts (`text/`), and `generate_demo_pdfs.py`.
- `spanner-graphrag/`: `schema.sql`, `provision_spanner_graph.py`, and `seed_spanner_graph.py`.
- `mcp-app-grid-server/`: FastAPI Streamable HTTP MCP App server (`app.py`), Vercel Monochrome Dual-Surface Grid + Citation Highlighter (`ui_template.py`), and Gemini Enterprise connector registrar (`register_custom_mcp_connector.py`).
- `a2ui-v09-canvas-agent/`: Native A2UI v0.9 Canvas agent (`cloudrun_a2ui/`) and Vertex AI Agent Engine ADK Spanner agent (`adk_spanner_agent/`).
- `standalone-workbench/`: Standalone full-screen legal workbench (`index.html`, `server.py`, `legal_brain.py`).

## Verification Rules
- Always verify `python3 -m py_compile mcp-app-grid-server/app.py mcp-app-grid-server/ui_template.py` before deploying.
- Never use `element.scrollIntoView()` inside `ui_template.py`; use `#doc-paper-scroll.scrollTo()` and keep `html, body` locked with `position: fixed; inset: 0; overflow: hidden;`.
- Always verify `POST /mcp` with both `tools/call` and `resources/read` after Cloud Run deployment.
