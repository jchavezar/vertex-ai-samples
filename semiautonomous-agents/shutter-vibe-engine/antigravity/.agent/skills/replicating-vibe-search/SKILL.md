---
name: replicating-vibe-search
description: Orchestrates the replication, environment provisioning, container builds, and deployment of the Shutter Vibe Engine on Google Cloud. Use when the user requests deployment, replication, or troubleshooting of the multimodal vibe search system.
---

# Replicating the Shutter Vibe Engine

## When to use this skill
- **Fresh Bootstrapping**: Setting up the Shutter Vibe Engine in a brand-new, empty workspace.
- **GCP Resource Provisioning**: Creating GCS buckets, binding IAM roles, or enabling APIs.
- **Continuous Deployment**: Building and deploying the Frontend Web App or Ingestion Worker containers.
- **Pipeline Testing & Logs**: Running end-to-end diagnostics and tailing container logs.

---

## 🛠️ The Orchestrator's Pre-Flight Checklist
Before executing any `// turbo` blocks from the workflow, verify the following prerequisites:

- [ ] **Python Package Manager**: Ensure `uv` is installed and active.
- [ ] **Active gcloud CLI**: Check that the developer is logged in:
  ```bash
  gcloud auth list
  ```
- [ ] **Workspace Parameter Check**: Confirm `.env` exists in the workspace root and contains valid project parameters (and is strictly omitted from Git via `.gitignore`).

---

## 🤖 Step-by-Step Deployment Runbook

### 1. Project Initialization & Sourcing
Make sure the target paths match original directories. The workflow `// turbo` block in Phase 1 executes the copy. Verify that the files exist in:
*   `multimodal-search/app/main.py`
*   `multimodal-search/app/templates/index_v2.html`
*   `multimodal-search/app/static/`

### 2. Idempotent Environment Provisioning
When configuring APIs and Service Accounts, always ensure actions are idempotent (check existence first):

*   **API Verification**:
    ```bash
    gcloud services list --enabled --filter="name:(run.googleapis.com OR eventarc.googleapis.com)"
    ```
*   **Service Account Check**:
    ```bash
    gcloud iam service-accounts describe ${ENVATO_SA_NAME}@${GOOGLE_CLOUD_PROJECT}.iam.gserviceaccount.com
    ```

### 3. Parallelized Cloud Container Builds
We compile images using Google Cloud Build with static YAML parameters to prevent local docker engine dependencies:
*   **Web App Builder**: Runs `antigravity/deploy/cloudbuild.app.yaml`.
*   **Worker Builder**: Runs `antigravity/deploy/cloudbuild.ingest.yaml`.

*Always swap the appropriate `.gcloudignore` files before compiling to prevent copying heavy `.venv` folders or temporary local test artifacts!*

---

## 🔍 Validation & Live Diagnostics

### Local Verification
Run the verification harness using `uv run` to assert that all template paths are complete and variable substitutions are complete:
```bash
uv run python antigravity/verify_replication.py
```

### Eventarc Pipeline Trigger Testing
After successful container deployments, instruct the developer to perform a live ingestion test:
1.  **Ingestion Command**:
    ```bash
    gcloud storage cp some-sample.mp4 gs://${ENVATO_GCS_BUCKET}/ingest/
    ```
2.  **Monitor Processing Output**:
    ```bash
    gcloud run services logs read envato-vibe-ingest --region=${GOOGLE_CLOUD_LOCATION} --limit=50
    ```
3.  **Inspect Results**: Check Firestore for the generated embeddings index entry.

---

## 🛑 Common Failure Troubleshooting
- **API Enablement Latency**: Occasionally, newly enabled APIs can take up to 2 minutes to propagate. If a deployment fails immediately after enabling an API, wait 60 seconds and re-run.
- **Eventarc Service Agent Permissions**: If files are finalized in GCS but the ingest worker isn't triggered, check that the GCS service account has `roles/pubsub.publisher` assigned.
- **Memory Allocation Crash**: FFmpeg ingestion can be memory-intensive. Ensure the ingest worker is deployed with `--memory=2Gi` or higher.
