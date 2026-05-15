#!/usr/bin/env bash
# Deploy the GCS->Firestore indexer as a Cloud Run job.
set -euo pipefail

PROJECT="${PROJECT:-sharepoint-wif}"
REGION="${REGION:-us-central1}"
COLLECTION="${COLLECTION:-mcp_docs}"
MARKDOWN_BUCKET="${MARKDOWN_BUCKET:-gs://sharepoint-wif-docparse-out}"
PDF_BUCKET="${PDF_BUCKET:-gs://sharepoint-wif-docparse-in}"
IMAGE="${REGION}-docker.pkg.dev/${PROJECT}/docparse/firestore-rag-mcp-indexer:latest"

echo "=== Build indexer image ==="
gcloud builds submit --tag "$IMAGE" --project="$PROJECT" --region="$REGION" .

echo "=== Create/update Cloud Run job ==="
gcloud run jobs create firestore-rag-mcp-indexer --image="$IMAGE" --project="$PROJECT" --region="$REGION" --task-timeout=1800 --max-retries=1 --set-env-vars="GOOGLE_CLOUD_PROJECT=${PROJECT}" --args="--markdown-bucket,${MARKDOWN_BUCKET},--pdf-bucket,${PDF_BUCKET},--project,${PROJECT},--collection,${COLLECTION}" 2>/dev/null || gcloud run jobs update firestore-rag-mcp-indexer --image="$IMAGE" --project="$PROJECT" --region="$REGION" --set-env-vars="GOOGLE_CLOUD_PROJECT=${PROJECT}" --args="--markdown-bucket,${MARKDOWN_BUCKET},--pdf-bucket,${PDF_BUCKET},--project,${PROJECT},--collection,${COLLECTION}"

echo
echo "Run with:"
echo "  gcloud run jobs execute firestore-rag-mcp-indexer --region=$REGION --project=$PROJECT"
