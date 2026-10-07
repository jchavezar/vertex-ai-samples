Replicate and verify the complete **LexGraph Spanner Hybrid GraphRAG & Interactive Legal Grid MCP App (SEP-1865)** end-to-end:

1. Run `python3 demo-documents/generate_demo_pdfs.py` and confirm all 8 PDFs in `demo-documents/pdf/` and 9 text files in `demo-documents/text/` are generated.
2. Verify Cloud Spanner instance `lexgraph-legal-spanner` and database `lexgraph-legal-context` (run `spanner-graphrag/provision_spanner_graph.py` and `spanner-graphrag/seed_spanner_graph.py` if needed).
3. Syntax-check `mcp-app-grid-server/app.py` and `mcp-app-grid-server/ui_template.py`, ensuring `lockRootViewport()` is present, `scrollIntoView` is never called, and `LATEST_WORKSPACE_STATE` is used in `resources/read`.
4. Deploy `mcp-app-grid-server` to Cloud Run (`lexgraph-legal-grid-mcp-agent` in `us-central1` with `--allow-unauthenticated --no-cpu-throttling`).
5. Run `mcp-app-grid-server/register_custom_mcp_connector.py` to link the Custom MCP connector to Gemini Enterprise's Default Assistant.
6. Execute a live JSON-RPC 2.0 smoke test against `POST /mcp` (`tools/call` + `resources/read`) and report the exact latencies.
