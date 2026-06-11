#!/usr/bin/env bash
# ==============================================================================
# TEARDOWN WORKFLOW: SHAREPOINT DOCUMENT RESTRUCTURE PORTAL
# ==============================================================================
# This script deletes all GCP resources provisioned for this system.
# RUN WITH CAUTION. This action is irreversible and deletes metadata databases.
# ==============================================================================

set -o errexit
set -o pipefail

# --- CONFIGURATION ---
PROJECT_ID=$(gcloud config get-value project)
LOCATION="us-central1"
SERVICE_NAME="sharepoint-restructure-worker"
DISCOVERY_SERVICE_NAME="sharepoint-discovery-service"
QUEUE_NAME="sharepoint-ingest-queue"
REDIS_INSTANCE="sharepoint-rate-limiter"
FIRESTORE_DATABASE="(default)" # Standard default firestore db
GCS_BUCKET="sharepoint-transient-docs-${PROJECT_ID}"
BQ_DATASET="sharepoint_catalog_ds"
VECTOR_INDEX_NAME="sharepoint_doc_index"
DATAPLEX_TAXONOMY="sharepoint_governance_taxonomy"

echo "====================================================="
echo "WARNING: Deleting all resources in project: ${PROJECT_ID}"
echo "Location: ${LOCATION}"
echo "====================================================="
read -p "Are you absolutely sure you want to destroy everything? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    echo "Teardown aborted."
    exit 1
fi

# 1. Delete Vertex AI Vector Search Index
echo "[1/8] Checking and deleting Vertex AI Index..."
INDEX_ID=$(gcloud ai indexes list --region="${LOCATION}" --filter="displayName=${VECTOR_INDEX_NAME}" --format="value(name)" 2>/dev/null || true)
if [ -n "${INDEX_ID}" ]; then
    echo "Deleting Vector Index: ${INDEX_ID}..."
    gcloud ai indexes delete "${INDEX_ID}" --region="${LOCATION}" --quiet
else
    echo "No vector index found."
fi

# 2. Delete Cloud Run Services
echo "[2/8] Deleting Cloud Run services..."
gcloud run services delete "${SERVICE_NAME}" --region="${LOCATION}" --quiet 2>/dev/null || echo "Service '${SERVICE_NAME}' not found."
gcloud run services delete "${DISCOVERY_SERVICE_NAME}" --region="${LOCATION}" --quiet 2>/dev/null || echo "Service '${DISCOVERY_SERVICE_NAME}' not found."

# 3. Delete Cloud Tasks Queue
echo "[3/8] Deleting Cloud Tasks Ingestion Queue..."
gcloud tasks queues delete "${QUEUE_NAME}" --location="${LOCATION}" --quiet 2>/dev/null || echo "Cloud Task queue '${QUEUE_NAME}' not found."

# 4. Delete Redis Instance
echo "[4/8] Deleting MemoryStore Redis rate limiter..."
gcloud redis instances delete "${REDIS_INSTANCE}" --region="${LOCATION}" --quiet 2>/dev/null || echo "Redis instance '${REDIS_INSTANCE}' not found."

# 5. Delete Transient GCS Bucket
echo "[5/8] Deleting transient GCS bucket..."
if gsutil ls -b "gs://${GCS_BUCKET}" &>/dev/null; then
    echo "Emptying and deleting bucket gs://${GCS_BUCKET}..."
    gsutil rm -r "gs://${GCS_BUCKET}"
else
    echo "Bucket gs://${GCS_BUCKET} not found."
fi

# 6. Delete BigQuery Dataset (Cascades metadata tables)
echo "[6/8] Deleting BigQuery Dataset..."
bq rm -r -f -d "${PROJECT_ID}:${BQ_DATASET}" 2>/dev/null || echo "BigQuery dataset '${BQ_DATASET}' not found."

# 7. Delete Dataplex Policy Tags / Taxonomy
echo "[7/8] Deleting Dataplex Policy Tag Taxonomy..."
TAXONOMY_ID=$(gcloud beta datacatalog taxonomies list --location="${LOCATION}" --filter="displayName=${DATAPLEX_TAXONOMY}" --format="value(name)" 2>/dev/null || true)
if [ -n "${TAXONOMY_ID}" ]; then
    gcloud beta datacatalog taxonomies delete "${TAXONOMY_ID}" --location="${LOCATION}" --quiet
else
    echo "Dataplex Taxonomy not found."
fi

# 8. Firestore Data Cleanup Hint
echo "[8/8] Firestore database cleanup..."
echo "NOTE: Firestore default database data cannot be deleted via simple gcloud command without"
echo "deleting the entire database. If you wish to purge documents, do it via the console UI"
echo "or run a custom deletion script against the Firestore client."

echo "====================================================="
echo "TEARDOWN COMPLETE. All major GCP elements removed."
echo "====================================================="
