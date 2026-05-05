#!/usr/bin/env bash
# Deploy Firestore indexer as a Cloud Run job
set -euo pipefail

PROJECT="${PROJECT:-sharepoint-wif}"
REGION="${REGION:-us-central1}"
IMAGE="${REGION}-docker.pkg.dev/${PROJECT}/docparse/firestore-indexer:latest"

echo "=== Build indexer image ==="
gcloud builds submit --tag "$IMAGE" --project="$PROJECT" --region="$REGION" .

echo "=== Create Cloud Run job ==="
gcloud run jobs create docparse-firestore-indexer \
  --image="$IMAGE" \
  --project="$PROJECT" \
  --region="$REGION" \
  --task-timeout=1800 \
  --max-retries=1 \
  --set-env-vars="GOOGLE_CLOUD_PROJECT=${PROJECT}" \
  --args="--markdown-bucket,gs://sharepoint-wif-docparse-out,--project,${PROJECT},--collection,docparse_chunks" \
  2>/dev/null || echo "Job exists, updating..."

gcloud run jobs update docparse-firestore-indexer \
  --image="$IMAGE" \
  --project="$PROJECT" \
  --region="$REGION" 2>&1 | tail -5

echo
echo "=== To run: ==="
echo "  gcloud run jobs execute docparse-firestore-indexer --region=$REGION --project=$PROJECT"
