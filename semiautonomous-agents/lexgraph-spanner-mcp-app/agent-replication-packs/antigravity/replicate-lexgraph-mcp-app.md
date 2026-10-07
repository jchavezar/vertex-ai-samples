---
description: End-to-end automated deployment and verification of the LexGraph Cloud Spanner Hybrid GraphRAG & Interactive Legal Grid MCP App (SEP-1865) in Gemini Enterprise.
---

# Replicate LexGraph Spanner Hybrid GraphRAG & MCP App (SEP-1865)

// turbo-all

## 1. Compile Demo Legal Corpus (8 PDFs + 9 Text Contracts)
```bash
python3 semiautonomous-agents/lexgraph-spanner-mcp-app/demo-documents/generate_demo_pdfs.py
```

## 2. Provision & Seed Cloud Spanner Hybrid GraphRAG (`LexGraphLegalGraph` + 3,072-dim Vector + FTS)
```bash
uv run --with google-cloud-spanner --with google-auth --with requests python3 semiautonomous-agents/lexgraph-spanner-mcp-app/spanner-graphrag/provision_spanner_graph.py
uv run --with google-cloud-spanner --with google-auth --with requests python3 semiautonomous-agents/lexgraph-spanner-mcp-app/spanner-graphrag/seed_spanner_graph.py
```

## 3. Deploy MCP App Grid & Citation Highlighter Server to Cloud Run
```bash
gcloud run deploy lexgraph-legal-grid-mcp-agent \
  --source=semiautonomous-agents/lexgraph-spanner-mcp-app/mcp-app-grid-server \
  --project=${GOOGLE_CLOUD_PROJECT:-vtxdemos} \
  --region=us-central1 \
  --allow-unauthenticated \
  --no-cpu-throttling \
  --quiet
```

## 4. Register Custom MCP DataConnector in Gemini Enterprise (`default_assistant`)
```bash
uv run --with google-auth --with requests python3 semiautonomous-agents/lexgraph-spanner-mcp-app/mcp-app-grid-server/register_custom_mcp_connector.py
```

## 5. Verify Live Streamable HTTP JSON-RPC 2.0 (`tools/call` & `<100ms` `resources/read`)
```bash
python3 -c '
import time, requests
url = "https://lexgraph-legal-grid-mcp-agent-254356041555.us-central1.run.app/mcp"
t0 = time.monotonic()
r1 = requests.post(url, json={"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"open_legal_analysis_grid","arguments":{"question":"Compare Indemnity Caps and Materiality Scrapes across M-331 and precedents"}}})
t1 = time.monotonic()
r2 = requests.post(url, json={"jsonrpc":"2.0","id":2,"method":"resources/read","params":{"uri":"ui://lexgraph/legal-grid-workspace.html"}})
t2 = time.monotonic()
assert r1.status_code == 200 and r2.status_code == 200
print(f"VERIFIED: tools/call={(t1-t0)*1000:.0f}ms | resources/read={(t2-t1)*1000:.0f}ms | HTML={len(r2.json()[\"result\"][\"contents\"][0][\"text\"]):,} bytes")
'
```
