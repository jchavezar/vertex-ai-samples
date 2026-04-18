#!/usr/bin/env bash
# Build + deploy the auto-ingest Cloud Run service and wire the Eventarc trigger.
# Idempotent: re-run after code changes.
set -euo pipefail

PROJECT=${GOOGLE_CLOUD_PROJECT:-vtxdemos}
REGION=${GOOGLE_CLOUD_LOCATION:-us-central1}
BUCKET=${ENVATO_GCS_BUCKET:-envato-vibe-demo}
SA="envato-vibe-runner@${PROJECT}.iam.gserviceaccount.com"
SERVICE="envato-vibe-ingest"
TRIGGER="envato-vibe-ingest-trigger"

# Resolve repo root regardless of where this is invoked from.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${REPO_ROOT}"

echo "→ Granting Eventarc/Pub-Sub the right to invoke our service"
PROJECT_NUM=$(gcloud projects describe "${PROJECT}" --format='value(projectNumber)')
GCS_AGENT="service-${PROJECT_NUM}@gs-project-accounts.iam.gserviceaccount.com"
gcloud projects add-iam-policy-binding "${PROJECT}" \
  --member="serviceAccount:${GCS_AGENT}" \
  --role="roles/pubsub.publisher" --condition=None --quiet >/dev/null

echo "→ Building + deploying ${SERVICE}"
gcloud run deploy "${SERVICE}" \
  --source . \
  --region "${REGION}" \
  --project "${PROJECT}" \
  --service-account "${SA}" \
  --memory 2Gi --cpu 2 --timeout 600 \
  --no-allow-unauthenticated \
  --set-env-vars "GOOGLE_CLOUD_PROJECT=${PROJECT},GOOGLE_CLOUD_LOCATION=${REGION},ENVATO_GCS_BUCKET=${BUCKET},GOOGLE_GENAI_USE_VERTEXAI=True"

echo "→ Wiring Eventarc trigger ${TRIGGER}"
if gcloud eventarc triggers describe "${TRIGGER}" --location "${REGION}" --project "${PROJECT}" >/dev/null 2>&1; then
  echo "  trigger already exists — updating destination"
  gcloud eventarc triggers update "${TRIGGER}" \
    --location "${REGION}" --project "${PROJECT}" \
    --destination-run-service "${SERVICE}" \
    --destination-run-region "${REGION}" \
    --service-account "${SA}"
else
  gcloud eventarc triggers create "${TRIGGER}" \
    --location "${REGION}" --project "${PROJECT}" \
    --destination-run-service "${SERVICE}" \
    --destination-run-region "${REGION}" \
    --event-filters "type=google.cloud.storage.object.v1.finalized" \
    --event-filters "bucket=${BUCKET}" \
    --service-account "${SA}"
fi

URL=$(gcloud run services describe "${SERVICE}" --region "${REGION}" --project "${PROJECT}" --format 'value(status.url)')
echo
echo "✓ Deployed.  Service URL: ${URL}"
echo "✓ Trigger:    ${TRIGGER}  (bucket=${BUCKET}, object.finalized)"
echo
echo "Test:  gsutil cp some-photo.jpg gs://${BUCKET}/ingest/"
echo "       Then watch logs:  gcloud run services logs read ${SERVICE} --region ${REGION} --limit 50"
