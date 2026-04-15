#!/usr/bin/env bash
# Deploy the Amex statement Cloud Run Job
set -euo pipefail

PROJECT_ID="${GCP_PROJECT_ID:-vtxdemos}"
REGION="us-east1"
JOB_NAME="amex-statement-sync"
AR_REPO="${REGION}-docker.pkg.dev/${PROJECT_ID}/cloud-run-source-deploy/${JOB_NAME}"

# OAuth client for Gmail token refresh (same as gworkspace MCP)
GOOGLE_CLIENT_ID="${GOOGLE_CLIENT_ID}"
GOOGLE_CLIENT_SECRET="${GOOGLE_CLIENT_SECRET}"

echo "Building with Cloud Build..."
cd amex_job
gcloud builds submit \
  --project="${PROJECT_ID}" \
  --region="${REGION}" \
  --tag="${AR_REPO}" \
  .
cd ..

echo "Deploying Cloud Run Job..."
gcloud run jobs create "${JOB_NAME}" \
  --project="${PROJECT_ID}" \
  --region="${REGION}" \
  --image="${AR_REPO}" \
  --task-timeout=600 \
  --max-retries=0 \
  --memory=2Gi \
  --set-env-vars="GCP_PROJECT_ID=${PROJECT_ID},FIRESTORE_COLLECTION=amex_statements,GOOGLE_CLIENT_ID=${GOOGLE_CLIENT_ID},GOOGLE_CLIENT_SECRET=${GOOGLE_CLIENT_SECRET}" \
  --service-account="${JOB_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" \
  2>/dev/null || \
gcloud run jobs update "${JOB_NAME}" \
  --project="${PROJECT_ID}" \
  --region="${REGION}" \
  --image="${AR_REPO}" \
  --task-timeout=600 \
  --max-retries=0 \
  --memory=2Gi \
  --set-env-vars="GCP_PROJECT_ID=${PROJECT_ID},FIRESTORE_COLLECTION=amex_statements,GOOGLE_CLIENT_ID=${GOOGLE_CLIENT_ID},GOOGLE_CLIENT_SECRET=${GOOGLE_CLIENT_SECRET}"

echo "Done. Run manually with:"
echo "  gcloud run jobs execute ${JOB_NAME} --region=${REGION} --project=${PROJECT_ID}"
