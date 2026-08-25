# Vector Search Canvas

> **Interactive Exploration & Benchmark Lab for Vertex AI Vector Search 2.0**  
> Flip a switch, inspect the exact `find_neighbors()` payload, and measure `recall@k` vs latency in real time.

---

## 🧭 Overview

**Vector Search Canvas** provides a glass-box visual interface for experimenting with **Google Cloud Vertex AI Vector Search**. It exposes all search parameters side-by-side, executing live vector retrieval against both an **Approximate Nearest Neighbor (ANN)** index (`TREE_AH` / ScaNN) and an **Exact Nearest Neighbor (KNN)** index (`BRUTE_FORCE`).

By comparing approximate hits against ground-truth exact hits on the same underlying 3072-dimensional embeddings (`gemini-embedding-2-preview`), developers can immediately visualize:
- **Recall@K Trade-offs**: Understand how index partitioning affects retrieval accuracy.
- **Latency Differences**: Measure ScaNN tree traversal speedups versus brute-force linear scans.
- **Dynamic Restrict Filtering**: Observe namespace token allows and denies.
- **Crowding Constraints**: Enforce diversity across categorical attributes.
- **Runtime Overrides**: Dynamically tune `leaf_nodes_to_search_percent_override` per query.

```
                    ┌───────────────────────────────┐
                    │      FastAPI / Jinja2 UI      │
                    │   (Vector Search Canvas App)  │
                    └──────────────┬────────────────┘
                                   │
               ┌───────────────────┴───────────────────┐
               │ 1. Embed Query via GenAI API          │
               │    (gemini-embedding-2-preview)       │
               │ 2. Concurrent find_neighbors() Calls  │
               └───────────┬───────────────┬───────────┘
                           │               │
                           ▼               ▼
          ┌──────────────────────┐   ┌──────────────────────┐
          │  APPROXIMATE INDEX   │   │     EXACT INDEX      │
          │     (TREE_AH /       │   │    (BRUTE_FORCE      │
          │   ScaNN Algorithm)   │   │     Ground Truth)    │
          └───────────┬──────────┘   └──────────┬───────────┘
                      │                         │
                      └────────────┬────────────┘
                                   ▼
          ┌─────────────────────────────────────────────────┐
          │  recall@k = |approx ∩ exact| / |exact| Overlap  │
          │  Latency (ms) Breakdown & Code Preview          │
          └─────────────────────────────────────────────────┘
```

---

## ✨ Key Features & Interactive Knobs

Every UI toggle maps **1:1** to a keyword argument on `MatchingEngineIndexEndpoint.find_neighbors()`:

| UI Control | `find_neighbors()` Parameter | Description |
| :--- | :--- | :--- |
| **Algorithm** | `deployed_index_id` | Selects `TREE_AH` (approximate), `BRUTE_FORCE` (exact), or runs `both` concurrently to compute recall overlap. |
| **Neighbors ($k$)** | `num_neighbors` | Number of nearest neighbors to retrieve ($1 \le k \le 100$). |
| **Leaf Nodes %** | `leaf_nodes_to_search_percent_override` | Overrides the ScaNN tree partition search depth ($0\text{--}100\%$). Higher values boost recall at the expense of search latency. |
| **Crowding** | `per_crowding_attribute_num_neighbors` | Caps the maximum number of neighbors returned per grouping attribute to ensure diversity. |
| **Restricts (Allow)** | `filter=[Namespace(allow_tokens=[...])]` | Hard filtering constraint restricting matches to specified namespace tags (e.g. `modality: video`). |
| **Restricts (Deny)** | `filter=[Namespace(deny_tokens=[...])]` | Hard negative constraint excluding matching tokens. |
| **Return Full Vector** | `return_full_datapoint=True/False` | Toggles whether the raw 3072-d feature vectors are returned in the response payload. |

---

## 📁 Repository Structure

```
vector-search-canvas/
├── app/
│   ├── main.py              # FastAPI application & Vertex AI search handler
│   ├── requirements.txt     # Python dependencies
│   ├── static/
│   │   ├── canvas.js        # Reactive vanilla JS UI & kwargs code generator
│   │   └── styles.css       # Clean dark-mode stylesheet
│   └── templates/
│       └── index.html       # Single-page search dashboard
├── deploy/
│   ├── create_indexes.py    # Provision TREE_AH & BRUTE_FORCE indexes + public endpoint
│   ├── populate_indexes.py  # Ingest vectors from Firestore or synthetic generator
│   ├── teardown.py          # Safe undeployment & resource deletion utility
│   └── indexes.json         # Generated deployment config with GCP resource URIs
├── dev.sh                   # Local development server launcher (Port 8770)
├── .gitignore               # Ironclad Zero-Leak gitignore rules
├── README.md                # High-level architecture & quickstart
└── REPLICATION.md           # Zero-missing-steps reproduction runbook
```

---

## 🚀 Quickstart

### 1. Prerequisites
- Python 3.10+
- Google Cloud SDK (`gcloud`) installed and authenticated
- A GCP project with Vertex AI API enabled

```bash
gcloud auth application-default login
gcloud config set project <YOUR_PROJECT_ID>
```

### 2. Install Dependencies
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r app/requirements.txt
```

### 3. Provision Indexes & Endpoint (One-Time)
```bash
export GOOGLE_CLOUD_PROJECT="<YOUR_PROJECT_ID>"
export GOOGLE_CLOUD_LOCATION="us-central1"

python deploy/create_indexes.py
```
> ⏱️ *Index creation and endpoint deployment typically takes 25–40 minutes on Vertex AI.*

### 4. Ingest Vectors
```bash
python deploy/populate_indexes.py
```

### 5. Launch the Canvas Dashboard
```bash
./dev.sh
```
Open **[http://127.0.0.1:8770](http://127.0.0.1:8770)** in your browser.

---

## 🔌 API Endpoints

- `GET /`: Serves the interactive search dashboard.
- `GET /api/health`: Health status and deployment readiness for both indexes.
- `GET /api/config`: Current GCP project, region, and index resource IDs.
- `POST /api/search`: Executes vector search against the endpoint.
  ```json
  {
    "query": "cinematic drone footage of mountains",
    "num_neighbors": 20,
    "algorithm": "both",
    "modality_allow": ["video"],
    "modality_deny": [],
    "leaf_nodes_to_search_percent_override": 15,
    "per_crowding_attribute_num_neighbors": 0,
    "return_full_datapoint": false
  }
  ```

---

## 💡 Cost Optimization & Teardown

Vertex AI Vector Search endpoints incur hourly charges per active replica node. When you are done exploring:

- **Keep Indexes & Stop Hourly Endpoint Billing** (Recommended):
  ```bash
  CONFIRM=yes KEEP_INDEXES=yes python deploy/teardown.py
  ```
- **Complete Destruction** (Deletes endpoint and all underlying indexes):
  ```bash
  CONFIRM=yes python deploy/teardown.py
  ```

For detailed replication steps, IAM permissions, and operational troubleshooting, refer to **[REPLICATION.md](REPLICATION.md)**.
