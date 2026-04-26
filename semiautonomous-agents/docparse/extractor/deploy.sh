#!/usr/bin/env bash
# One-shot setup: buckets + service account + Cloud Run + Eventarc trigger.
# Idempotent — re-run after edits.
#
# Run from anywhere — cds to its own directory so the Cloud Build context
# always points at extractor/ (where Dockerfile + src/ live).
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

PROJECT="${PROJECT:-my-project}"
REGION="${REGION:-us-central1}"
INPUT_BUCKET="${INPUT_BUCKET:-my-project-docparse-in}"
OUTPUT_BUCKET="${OUTPUT_BUCKET:-my-project-docparse-out}"
SERVICE="${SERVICE:-docparse}"
SA_NAME="${SA_NAME:-docparse-runner}"
SA_EMAIL="${SA_NAME}@${PROJECT}.iam.gserviceaccount.com"
EVENTARC_SA="${EVENTARC_SA:-${SA_EMAIL}}"  # reuse the same SA for the trigger
TRIGGER_NAME="${TRIGGER_NAME:-docparse-on-pdf-upload}"
IMAGE="${IMAGE:-${REGION}-docker.pkg.dev/${PROJECT}/docparse/${SERVICE}:latest}"
REPO="${REPO:-docparse}"

echo "==> project=${PROJECT}  region=${REGION}"

echo "==> enabling APIs"
gcloud services enable \
  run.googleapis.com \
  eventarc.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  aiplatform.googleapis.com \
  storage.googleapis.com \
  discoveryengine.googleapis.com \
  --project="${PROJECT}"

echo "==> provisioning service identities (first-time-in-project)"
# These calls force-create the GCS, Eventarc, and Discovery Engine service
# agents in the project. Without them, the IAM bindings below fail with
# "Service account ... does not exist."
gcloud beta services identity create --service=storage.googleapis.com    --project="${PROJECT}" >/dev/null 2>&1 || true
gcloud beta services identity create --service=eventarc.googleapis.com   --project="${PROJECT}" >/dev/null 2>&1 || true
gcloud beta services identity create --service=discoveryengine.googleapis.com --project="${PROJECT}" >/dev/null 2>&1 || true

echo "==> creating buckets (idempotent)"
for b in "${INPUT_BUCKET}" "${OUTPUT_BUCKET}"; do
  if ! gcloud storage buckets describe "gs://${b}" --project="${PROJECT}" >/dev/null 2>&1; then
    gcloud storage buckets create "gs://${b}" \
      --project="${PROJECT}" --location="${REGION}" --uniform-bucket-level-access
  else
    echo "  - gs://${b} exists"
  fi
done

echo "==> creating Artifact Registry repo (idempotent)"
if ! gcloud artifacts repositories describe "${REPO}" --location="${REGION}" --project="${PROJECT}" >/dev/null 2>&1; then
  gcloud artifacts repositories create "${REPO}" \
    --repository-format=docker --location="${REGION}" --project="${PROJECT}"
fi

echo "==> creating service account ${SA_EMAIL}"
if ! gcloud iam service-accounts describe "${SA_EMAIL}" --project="${PROJECT}" >/dev/null 2>&1; then
  gcloud iam service-accounts create "${SA_NAME}" --project="${PROJECT}" \
    --display-name="docparse Cloud Run runner"
fi

echo "==> granting IAM"
# Read input bucket
gcloud storage buckets add-iam-policy-binding "gs://${INPUT_BUCKET}" \
  --member="serviceAccount:${SA_EMAIL}" --role="roles/storage.objectViewer" \
  --project="${PROJECT}" >/dev/null
# Write output bucket
gcloud storage buckets add-iam-policy-binding "gs://${OUTPUT_BUCKET}" \
  --member="serviceAccount:${SA_EMAIL}" --role="roles/storage.objectAdmin" \
  --project="${PROJECT}" >/dev/null
# Use Vertex AI / Gemini
gcloud projects add-iam-policy-binding "${PROJECT}" \
  --member="serviceAccount:${SA_EMAIL}" --role="roles/aiplatform.user" --condition=None >/dev/null
# Eventarc needs to invoke our Cloud Run service
gcloud projects add-iam-policy-binding "${PROJECT}" \
  --member="serviceAccount:${SA_EMAIL}" --role="roles/run.invoker" --condition=None >/dev/null
# Eventarc receives events
gcloud projects add-iam-policy-binding "${PROJECT}" \
  --member="serviceAccount:${SA_EMAIL}" --role="roles/eventarc.eventReceiver" --condition=None >/dev/null
# GCS service agent needs pub/sub publish (one-time, harmless if already set)
GCS_SA="$(gcloud storage service-agent --project="${PROJECT}")"
gcloud projects add-iam-policy-binding "${PROJECT}" \
  --member="serviceAccount:${GCS_SA}" --role="roles/pubsub.publisher" --condition=None >/dev/null

# Eventarc service agent needs to read the source bucket to validate trigger creation
PROJECT_NUM="$(gcloud projects describe "${PROJECT}" --format='value(projectNumber)')"
EVENTARC_SA="service-${PROJECT_NUM}@gcp-sa-eventarc.iam.gserviceaccount.com"
gcloud storage buckets add-iam-policy-binding "gs://${INPUT_BUCKET}" \
  --member="serviceAccount:${EVENTARC_SA}" --role="roles/storage.legacyBucketReader" \
  --project="${PROJECT}" >/dev/null

# Default compute SA needs cloudbuild.builds.builder for `gcloud builds submit`
gcloud projects add-iam-policy-binding "${PROJECT}" \
  --member="serviceAccount:${PROJECT_NUM}-compute@developer.gserviceaccount.com" \
  --role="roles/cloudbuild.builds.builder" --condition=None >/dev/null

# Discovery Engine service agent needs storage.admin on the OUTPUT bucket
# specifically to set up Pub/Sub notifications for STREAMING-mode datastores.
# (objectViewer alone fails with "does not have storage.buckets.update access".)
# Harmless if you stick with periodic / one-time mode; required for streaming.
DE_SA="service-${PROJECT_NUM}@gcp-sa-discoveryengine.iam.gserviceaccount.com"
gcloud storage buckets add-iam-policy-binding "gs://${OUTPUT_BUCKET}" \
  --member="serviceAccount:${DE_SA}" --role="roles/storage.admin" \
  --project="${PROJECT}" >/dev/null

echo "==> building and pushing image"
gcloud builds submit \
  --tag "${IMAGE}" \
  --project="${PROJECT}" \
  --region="${REGION}" \
  .

echo "==> deploying Cloud Run service"
gcloud run deploy "${SERVICE}" \
  --image="${IMAGE}" \
  --project="${PROJECT}" \
  --region="${REGION}" \
  --service-account="${SA_EMAIL}" \
  --no-allow-unauthenticated \
  --cpu=2 --memory=2Gi \
  --concurrency=1 \
  --max-instances=10 \
  --timeout=3600 \
  --execution-environment=gen2 \
  --set-env-vars="DOCPARSE_PROJECT=${PROJECT},DOCPARSE_LOCATION=global,OUTPUT_BUCKET=${OUTPUT_BUCKET}"

echo "==> creating Eventarc trigger (idempotent)"
if ! gcloud eventarc triggers describe "${TRIGGER_NAME}" --location="${REGION}" --project="${PROJECT}" >/dev/null 2>&1; then
  gcloud eventarc triggers create "${TRIGGER_NAME}" \
    --location="${REGION}" \
    --project="${PROJECT}" \
    --destination-run-service="${SERVICE}" \
    --destination-run-region="${REGION}" \
    --event-filters="type=google.cloud.storage.object.v1.finalized" \
    --event-filters="bucket=${INPUT_BUCKET}" \
    --service-account="${EVENTARC_SA}"
else
  echo "  - trigger ${TRIGGER_NAME} exists"
fi

echo
echo "==================================================="
echo "  Done."
echo "  Upload:   gcloud storage cp foo.pdf gs://${INPUT_BUCKET}/"
echo "  Result:   gs://${OUTPUT_BUCKET}/foo.md  (and foo.report.json)"
echo "  Logs:     gcloud beta run services logs tail ${SERVICE} --region=${REGION} --project=${PROJECT}"
echo "==================================================="
