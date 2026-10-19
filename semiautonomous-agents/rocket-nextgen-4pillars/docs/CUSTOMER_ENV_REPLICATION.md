# ⚡ Quick Customer Environment Replication Guide (`< 3 Minutes`)

> **Target Audience:** Rocket Companies (Redfin · Rocket Mortgage · Mr. Cooper · Rocket Money) & Enterprise Cloud Engineers replicating the **Next-Gen 5-Pillar AI Studio (`v35`)** inside their own Google Cloud project.

---

## 1. Customer Environment Variables Matrix

All 5 Pillars and the FastAPI gateway (`app.py`) read configuration directly from standard environment variables with zero code changes required:

| Variable | Pillar(s) | Example Customer Value | Purpose |
| :--- | :---: | :--- | :--- |
| **`GCP_PROJECT_ID`** | All (`P1`–`P5`) | `rocket-ai-prod-01` | Target Google Cloud Project ID for Vertex AI, BigQuery, and Places API (New). |
| **`GCP_LOCATION`** | `P2`, `P3`, `P4`, `P5` | `global` | Vertex AI endpoint for `gemini-3.8-flash`, `gemini-3.1-flash-lite`, `gemini-4-argon`, `gemini-3.1-flash-image`, and `veo-3.1-generate-001`. |
| **`GCP_LIVE_LOCATION`** | `P4`, `P5` | `us-central1` | Regional endpoint for `gemini-3.8-live` (`BidiGenerateContent` WebSocket), `imagen-4.0-generate-001`, `gemini-embedding-001`, and `multimodalembedding@001`. |
| **`BQ_DATASET_ID`** | `P1` (TimesFM) | `rocket_nextgen_timesfm` | BigQuery dataset holding weekly servicing & Redfin demand time-series. |
| **`BQ_TABLE_ID`** | `P1` (TimesFM) | `portfolio_metrics` | BigQuery table queried by `AI.FORECAST` (`TimesFM 2.0`). |
| **`GCS_MEDIA_BUCKET`** | `P2`, `P5` | `rocket-re-media-cdn` | Cloud Storage bucket hosting the 108-home photo catalog, pre-rendered 720p cinematic tours, and Veo 3.1 walkthrough MP4s. |
| **`ROCKET_USER`** | Studio Gateway | `rocket` | Username for the studio login gate. |
| **`ROCKET_PASS`** | Studio Gateway | `YourStrongPassword!` | Password for the studio login gate. |
| **`ROCKET_SECRET`** | Studio Gateway | `your-hmac-signing-secret` | HMAC-SHA256 secret used to sign session cookies and `?auth_token=` links. |

---

## 2. Step-by-Step Replication in 4 Commands

### Step 1: Configure Your Customer Variables (`.env`)

```bash
cd semiautonomous-agents/rocket
cp .env.example .env

# Edit .env or export directly in your shell:
export GCP_PROJECT_ID="your-gcp-project-id"
export GCP_LOCATION="global"
export GCP_LIVE_LOCATION="us-central1"
export BQ_DATASET_ID="rocket_nextgen_timesfm"
export BQ_TABLE_ID="portfolio_metrics"
export GCS_MEDIA_BUCKET="your-gcs-media-bucket"
export ROCKET_USER="rocket"
export ROCKET_PASS="ReplaceWithStrongPassword!"
export ROCKET_SECRET="$(openssl rand -hex 16)"
```

### Step 2: Enable Required Google Cloud APIs & IAM Roles

```bash
gcloud config set project "${GCP_PROJECT_ID}"

gcloud services enable \
  aiplatform.googleapis.com \
  bigquery.googleapis.com \
  bigquerystorage.googleapis.com \
  places.googleapis.com \
  storage.googleapis.com \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com
```

### Step 3: Seed the BigQuery ML `TimesFM 2.0` Dataset (Pillar 1)

```bash
bq --project_id="${GCP_PROJECT_ID}" mk -d --if_exists "${BQ_DATASET_ID}"

python3 -c '
import os
from google.cloud import bigquery
import importlib.util
spec = importlib.util.spec_from_file_location("p1", "pillar-1-bqml-timesfm/engine.py")
p1 = importlib.util.module_from_spec(spec); spec.loader.exec_module(p1)
print("Testing Pillar 1 Forecast:", p1.run_timesfm_forecast()["kpis"])
'
```

### Step 4: Run Locally or Deploy to Cloud Run (`--timeout 3600` for Live WebSockets)

#### Local Run:
```bash
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 8080
```

#### Production Cloud Run Deployment:
```bash
gcloud run deploy rocket-polymorphic-search \
  --source . \
  --region us-central1 \
  --project "${GCP_PROJECT_ID}" \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 3600 \
  --set-env-vars="GCP_PROJECT_ID=${GCP_PROJECT_ID},GCP_LOCATION=${GCP_LOCATION},GCP_LIVE_LOCATION=${GCP_LIVE_LOCATION},BQ_DATASET_ID=${BQ_DATASET_ID},BQ_TABLE_ID=${BQ_TABLE_ID},GCS_MEDIA_BUCKET=${GCS_MEDIA_BUCKET},ROCKET_USER=${ROCKET_USER},ROCKET_PASS=${ROCKET_PASS},ROCKET_SECRET=${ROCKET_SECRET}"
```
