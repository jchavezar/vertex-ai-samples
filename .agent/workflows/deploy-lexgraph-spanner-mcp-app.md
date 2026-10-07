---
description: End-to-end automated deployment and verification of the LexGraph Cloud Spanner Hybrid GraphRAG & Interactive Legal Grid MCP App (SEP-1865) in Gemini Enterprise.
---

# Deploy LexGraph Spanner Hybrid GraphRAG & MCP App (SEP-1865)

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
