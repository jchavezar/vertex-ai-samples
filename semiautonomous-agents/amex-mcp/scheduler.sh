#!/usr/bin/env bash
# Create Cloud Scheduler job to trigger Amex statement sync monthly
set -euo pipefail

PROJECT_ID="${GCP_PROJECT_ID:-vtxdemos}"
REGION="us-east1"
JOB_NAME="amex-statement-sync"

echo "Creating Cloud Scheduler job..."
gcloud scheduler jobs create http "${JOB_NAME}-trigger" \
  --project="${PROJECT_ID}" \
  --location="${REGION}" \
  --schedule="0 6 1 * *" \
  --time-zone="America/New_York" \
  --uri="https://${REGION}-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/${PROJECT_ID}/jobs/${JOB_NAME}:run" \
  --http-method=POST \
  --oauth-service-account-email="${JOB_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" \
  2>/dev/null || \
gcloud scheduler jobs update http "${JOB_NAME}-trigger" \
  --project="${PROJECT_ID}" \
  --location="${REGION}" \
  --schedule="0 6 1 * *" \
  --time-zone="America/New_York" \
  --uri="https://${REGION}-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/${PROJECT_ID}/jobs/${JOB_NAME}:run" \
  --http-method=POST \
  --oauth-service-account-email="${JOB_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

echo "Done. Scheduler set for 1st of every month at 6:00 AM ET."
echo "Test with: gcloud scheduler jobs run ${JOB_NAME}-trigger --project=${PROJECT_ID} --location=${REGION}"
