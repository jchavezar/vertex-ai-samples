# 04 — Step-by-Step Zero-to-Production Replication Runbook

Follow this runbook to deploy the entire **LexGraph Cloud Spanner Hybrid GraphRAG & Interactive Legal Grid MCP App (SEP-1865)** into any Google Cloud project and Gemini Enterprise instance in under 10 minutes.

---

## Prerequisites

1. **Google Cloud Project** with Billing enabled (e.g., `vtxdemos`).
2. **Required APIs Enabled**:
   ```bash
   gcloud services enable \
     spanner.googleapis.com \
     run.googleapis.com \
     cloudbuild.googleapis.com \
     aiplatform.googleapis.com \
     discoveryengine.googleapis.com \
     --project=${GOOGLE_CLOUD_PROJECT:-vtxdemos}
   ```
3. **Gemini Enterprise App (`Engine`)** created in Discovery Engine (`global` location, e.g. `default_search` or your enterprise engine ID).

---

## Step 1: Generate the 8 Synthetic Legal PDFs & Text Corpus

```bash
cd semiautonomous-agents/lexgraph-spanner-mcp-app
python3 demo-documents/generate_demo_pdfs.py
```

This generates:
- `demo-documents/pdf/*.pdf` (8 multi-page legal agreements compiled via Headless Chrome)
- `demo-documents/text/*.txt` (9 plain-text contracts & unfiled tax email `EM-9901`)

---

## Step 2: Provision & Seed Cloud Spanner Hybrid GraphRAG

```bash
export GOOGLE_CLOUD_PROJECT="vtxdemos"
export SPANNER_INSTANCE="lexgraph-legal-spanner"
export SPANNER_DATABASE="lexgraph-legal-context"

# 2A. Create Spanner Instance, Database, Search Index, and LexGraphLegalGraph DDL
uv run --with google-cloud-spanner python3 spanner-graphrag/provision_spanner_graph.py

# 2B. Compute 3,072-dim gemini-embedding-2 vectors & seed nodes/edges
uv run --with google-cloud-spanner --with google-auth --with requests python3 spanner-graphrag/seed_spanner_graph.py
```

---

## Step 3: Deploy the MCP App (SEP-1865) Server to Cloud Run

> [!IMPORTANT]
> Always deploy with `--no-cpu-throttling` so background Spanner connection pooling and state caching remain warm between turns.

```bash
gcloud run deploy lexgraph-legal-grid-mcp-agent \
  --source=mcp-app-grid-server \
  --project=${GOOGLE_CLOUD_PROJECT:-vtxdemos} \
  --region=us-central1 \
  --allow-unauthenticated \
  --no-cpu-throttling \
  --quiet
```

Grant the Discovery Engine Service Agent permission to invoke the Cloud Run service:
```bash
PROJECT_NUMBER=$(gcloud projects describe ${GOOGLE_CLOUD_PROJECT:-vtxdemos} --format="value(projectNumber)")
gcloud run services add-iam-policy-binding lexgraph-legal-grid-mcp-agent \
  --region=us-central1 \
  --project=${GOOGLE_CLOUD_PROJECT:-vtxdemos} \
  --member="serviceAccount:service-${PROJECT_NUMBER}@gcp-sa-discoveryengine.iam.gserviceaccount.com" \
  --role="roles/run.invoker"
```

---

## Step 4: Link Custom MCP Connector to Gemini Enterprise's Default Assistant

```bash
uv run --with google-auth --with requests python3 mcp-app-grid-server/register_custom_mcp_connector.py
```

What this script does automatically:
1. Calls `locations/global:setUpDataConnector` (`v1alpha`) to register `lexgraph-legal-grid-mcp-app` (`connectorType: CUSTOM_MCP`) pointing to `https://<CLOUD_RUN_URL>/mcp`.
2. Binds the resulting MCP DataStore (`lexgraph-legal-grid-mcp-app_mcp_tool`) into the Gemini Enterprise Engine's `dataStoreIds` array so it is immediately available inside **Default Assistant (`New chat`)**.

---

## Step 5: Test Live in Gemini Enterprise (`New chat`)

1. Open your **Gemini Enterprise** web app and stay in the default **`New chat`** view (do not switch to a custom A2A agent).
2. Click the **Tools / Sources (Sliders icon)** in the prompt bar and ensure **LexGraph Legal Grid MCP App** is toggled **ON**.
3. Paste any of these test prompts:
   - **Prompt 1 (Full Grid + Citation Highlighter)**:
     > *"Compare Indemnity Caps, Deductible Baskets, Materiality Scrapes, and Skadden Redlines across M-331 and precedents"*
   - **Prompt 2 (Dynamic Question Column Extraction)**:
     > *"What are the Change of Control provisions across M-331 and precedents?"*
   - **Prompt 3 (Live 30-Day Cloud Spanner TeammateGrant Edge Commit)**:
     > *"Commit a 30-day teammate access grant in Cloud Spanner for unfiled tax email EM-9901 on Matter M-331"*
