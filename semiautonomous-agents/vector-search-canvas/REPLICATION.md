# Vector Search Canvas — Complete Replication & Runbook

This guide provides a comprehensive, production-grade runbook for replicating the **Vector Search Canvas** environment from scratch in any Google Cloud Platform (GCP) project with zero missing steps.

---

## 📋 Table of Contents

1. [Prerequisites & IAM Permissions](#1-prerequisites--iam-permissions)
2. [Local Environment & Tooling](#2-local-environment--tooling)
3. [Step 1: Vertex AI Infrastructure Provisioning](#3-step-1-vertex-ai-infrastructure-provisioning)
4. [Step 2: Vector Ingestion & Streaming Upsert](#4-step-2-vector-ingestion--streaming-upsert)
5. [Step 3: Running the Application Locally](#5-step-3-running-the-application-locally)
6. [Step 4: Verifying Search & Recall Calculations](#6-step-4-verifying-search--recall-calculations)
7. [Step 5: Resource Teardown & Billing Management](#7-step-5-resource-teardown--billing-management)
8. [Troubleshooting & Reference](#8-troubleshooting--reference)

---

## 1. Prerequisites & IAM Permissions

### 1.1 GCP Project & APIs
Ensure you have an active GCP project with billing enabled. Enable the necessary APIs:

```bash
export PROJECT_ID="vtxdemos"       # Replace with your GCP project ID
export LOCATION="us-central1"     # Supported Vertex AI region

gcloud config set project "${PROJECT_ID}"

gcloud services enable \
    aiplatform.googleapis.com \
    firestore.googleapis.com \
    generativelanguage.googleapis.com \
    compute.googleapis.com
```

### 1.2 Required IAM Roles
Ensure your executing user or Service Account possesses the following roles:
- **Vertex AI Administrator** (`roles/aiplatform.admin`) or **Vertex AI User** (`roles/aiplatform.user`)
- **Storage Object Viewer** (`roles/storage.objectViewer`)
- **Cloud Datastore User** (`roles/datastore.user`) — *if ingesting from Firestore*

Authenticate Application Default Credentials (ADC):
```bash
gcloud auth login
gcloud auth application-default login
```

---

## 2. Local Environment & Tooling

Clone the repository and enter the canvas directory:
```bash
cd /Users/jesusarguelles/IdeaProjects/vertex-ai-samples/semiautonomous-agents/vector-search-canvas
```

Initialize a Python 3.10+ virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r app/requirements.txt
```

Verify installed packages:
- `google-cloud-aiplatform >= 1.71`
- `google-genai >= 0.3`
- `fastapi >= 0.110`
- `uvicorn[standard] >= 0.27`

---

## 3. Step 1: Vertex AI Infrastructure Provisioning

The canvas requires two indexes deployed to a single public endpoint:
1. **Approximate Index (`vs-canvas-tree-ah`)**: ScaNN Tree-AH partition tree with cosine distance and streaming updates.
2. **Exact Index (`vs-canvas-bruteforce`)**: Brute-force linear scan baseline with cosine distance.
3. **Public Index Endpoint (`vs-canvas-endpoint`)**: Publicly accessible routing endpoint.

### Running the Creation Script
```bash
export GOOGLE_CLOUD_PROJECT="${PROJECT_ID}"
export GOOGLE_CLOUD_LOCATION="${LOCATION}"

python deploy/create_indexes.py
```

### What `create_indexes.py` Does:
1. Calls `MatchingEngineIndex.create_tree_ah_index()`:
   - Dimensions: `3072` (matches `gemini-embedding-2-preview`)
   - Distance Measure: `COSINE_DISTANCE`
   - Approximate Neighbors Count: `150`
   - Leaf Node Embedding Count: `500`
   - Leaf Nodes To Search Percent: `10`
   - Index Update Method: `STREAM_UPDATE`
2. Calls `MatchingEngineIndex.create_brute_force_index()`:
   - Dimensions: `3072`
   - Distance Measure: `COSINE_DISTANCE`
   - Index Update Method: `STREAM_UPDATE`
3. Provisions a public `MatchingEngineIndexEndpoint` (`vs-canvas-endpoint`).
4. Kicks off asynchronous index deployment to the endpoint (`vs_canvas_tree_ah` and `vs_canvas_brute`).
5. Generates `deploy/indexes.json` with resource URIs.

### Monitoring Deployment Progress
Vertex AI index deployment takes **20–40 minutes**. Check the deployment status via `gcloud`:
```bash
gcloud ai index-endpoints list \
    --region="${LOCATION}" \
    --project="${PROJECT_ID}"

# Describe the specific endpoint
gcloud ai index-endpoints describe vs-canvas-endpoint \
    --region="${LOCATION}" \
    --project="${PROJECT_ID}" \
    --format="yaml(name,displayName,deployedIndexes)"
```

---

## 4. Step 2: Vector Ingestion & Streaming Upsert

Once both indexes are deployed, populate them with datapoints containing feature vectors and restrict namespace metadata (`modality`, `tempo_bucket`, `length_bucket`).

### Option A: Automatic / Firestore Sampling
If a Firestore collection `segments` and a source multimodal index exist:
```bash
LIMIT=2000 python deploy/populate_indexes.py
```

### Option B: Standalone Synthetic Generation (Zero Dependencies)
If replicating in a fresh GCP project without existing media assets, trigger synthetic dataset generation:
```bash
SOURCE_MODE=synthetic LIMIT=2000 python deploy/populate_indexes.py
```

### Streaming Consistency Notice
Streaming upserts (`upsert_datapoints`) are eventually consistent. Allow **30 to 60 seconds** after the script finishes before expecting queries to return newly added vectors.

---

## 5. Step 3: Running the Application Locally

Launch the local development server using the preconfigured startup script:
```bash
./dev.sh
```

By default, the server binds to `http://127.0.0.1:8770`. You can override host and port if desired:
```bash
PORT=8770 HOST=127.0.0.1 ./dev.sh
```

The script automatically:
- Resolves the virtual environment's `uvicorn` binary.
- Cleans up stale socket bindings on the designated port.
- Configures `GOOGLE_CLOUD_PROJECT` and `GOOGLE_CLOUD_LOCATION`.
- Starts the FastAPI server with auto-reload enabled.

---

## 6. Step 4: Verifying Search & Recall Calculations

### 6.1 Browser Verification
Open `http://127.0.0.1:8770` in your web browser:
1. Verify the top right status chip displays `both indexes deployed ●`.
2. Enter a query in the search bar (e.g., `"sunset over the ocean"`).
3. Toggle between **both (compare)**, **TREE_AH only**, and **BRUTE_FORCE only**.
4. Adjust the **k slider** and **leaf_nodes_to_search % override**.
5. Observe:
   - Live query embedding duration (`embed ms`).
   - Approximate and Exact query latencies (`approx ms`, `exact ms`).
   - Real-time `recall@k` percentage calculated as $\frac{|\text{approx} \cap \text{exact}|}{|\text{exact}|}$.
   - Live Python SDK code snippet dynamically reflecting all kwargs.

### 6.2 cURL API Verification
You can also execute search queries directly against the backend REST API:
```bash
curl -X POST http://127.0.0.1:8770/api/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "cinematic action sequence in rain",
    "num_neighbors": 10,
    "algorithm": "both",
    "modality_allow": ["video"],
    "leaf_nodes_to_search_percent_override": 20
  }' | jq .
```

---

## 7. Step 5: Resource Teardown & Billing Management

Vertex AI Vector Search charges hourly for active deployed replicas on index endpoints (~$0.40/hr per replica). When not actively using the canvas, perform teardown according to your needs.

### 7.1 Keep Indexes & Stop Endpoint Billing (Recommended)
This undeploys the indexes and deletes the endpoint to eliminate running compute charges while **retaining the populated vector indexes** in Vertex AI for future redeployment.

#### Via CLI / gcloud:
```bash
# 1. Undeploy index from endpoint
gcloud ai index-endpoints undeploy-index 2832177026406809600 \
    --deployed-index-id=vs_canvas_tree_ah \
    --region=us-central1 \
    --project=vtxdemos

# 2. Delete index endpoint
gcloud ai index-endpoints delete 2832177026406809600 \
    --region=us-central1 \
    --project=vtxdemos \
    --quiet
```

#### Via Python Script:
```bash
CONFIRM=yes KEEP_INDEXES=yes python deploy/teardown.py
```

### 7.2 Full Teardown (Delete Everything)
To completely delete the endpoint, both vector search indexes, and local state:
```bash
CONFIRM=yes python deploy/teardown.py
```

---

## 8. Troubleshooting & Reference

| Issue | Root Cause | Solution |
| :--- | :--- | :--- |
| `503 Service Unavailable` on `/api/health` | Index endpoint is undeployed or `indexes.json` is missing. | Verify endpoint status with `gcloud ai index-endpoints list` or run `create_indexes.py`. |
| `400 Empty query` | Search query was blank. | Enter non-empty query text in the search input or API payload. |
| `IndexSyncTime` is null | Index has not finished initial replica warm-up. | Wait 5–10 minutes after deploy operation reports `done: true`. |
| Dimension mismatch error | Embeddings generated do not match index dimensions (`3072`). | Ensure `gemini-embedding-2-preview` is used for 3072-d vectors, or adjust `DIMS` in `create_indexes.py`. |
| Restrict filtering returns 0 hits | Namespace tags are case-sensitive or mutually exclusive. | Verify restrict tokens matched between ingestion (`populate_indexes.py`) and search request. |
