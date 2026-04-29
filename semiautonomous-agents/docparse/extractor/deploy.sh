#!/usr/bin/env bash
# One-shot setup for docparse v6 (Pattern C: Cloud Tasks dedup).
#
# Architecture:
#   PDF upload → Eventarc → Cloud Run /dispatch → Cloud Tasks (named-task dedup)
#                                                       ↓
#                                              Cloud Run /work → Vertex AI extraction
#
# Storm prevention: every (bucket, object, generation) maps to a deterministic
# Cloud Tasks task name. Pub/Sub redelivering the same OBJECT_FINALIZE event
# 100x → 1 task created, 99 ALREADY_EXISTS no-ops. See PRODUCTION_READINESS.md.
#
# Idempotent — safe to re-run after edits.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

PROJECT="${PROJECT:-my-project}"
REGION="${REGION:-us-central1}"
INPUT_BUCKET="${INPUT_BUCKET:-${PROJECT}-docparse-in}"
OUTPUT_BUCKET="${OUTPUT_BUCKET:-${PROJECT}-docparse-out}"
SERVICE="${SERVICE:-docparse}"
SA_NAME="${SA_NAME:-docparse-runner}"
SA_EMAIL="${SA_NAME}@${PROJECT}.iam.gserviceaccount.com"
TRIGGER_NAME="${TRIGGER_NAME:-docparse-on-pdf-upload}"
TASKS_QUEUE="${TASKS_QUEUE:-docparse-extract}"
IMAGE="${IMAGE:-${REGION}-docker.pkg.dev/${PROJECT}/docparse/${SERVICE}:latest}"
REPO="${REPO:-docparse}"

echo "==> project=${PROJECT}  region=${REGION}  queue=${TASKS_QUEUE}"

echo "==> enabling APIs"
gcloud services enable \
  run.googleapis.com \
  eventarc.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  aiplatform.googleapis.com \
  storage.googleapis.com \
  cloudtasks.googleapis.com \
  discoveryengine.googleapis.com \
  --project="${PROJECT}"

echo "==> provisioning service identities"
gcloud beta services identity create --service=storage.googleapis.com    --project="${PROJECT}" >/dev/null 2>&1 || true
gcloud beta services identity create --service=eventarc.googleapis.com   --project="${PROJECT}" >/dev/null 2>&1 || true
gcloud beta services identity create --service=cloudtasks.googleapis.com --project="${PROJECT}" >/dev/null 2>&1 || true
gcloud beta services identity create --service=discoveryengine.googleapis.com --project="${PROJECT}" >/dev/null 2>&1 || true

echo "==> creating buckets"
for b in "${INPUT_BUCKET}" "${OUTPUT_BUCKET}"; do
  if ! gcloud storage buckets describe "gs://${b}" --project="${PROJECT}" >/dev/null 2>&1; then
    gcloud storage buckets create "gs://${b}" --project="${PROJECT}" --location="${REGION}" --uniform-bucket-level-access
  fi
done

echo "==> creating Artifact Registry repo"
gcloud artifacts repositories describe "${REPO}" --location="${REGION}" --project="${PROJECT}" >/dev/null 2>&1 \
  || gcloud artifacts repositories create "${REPO}" --repository-format=docker --location="${REGION}" --project="${PROJECT}"

echo "==> creating Cloud Tasks queue (with bounded retry)"
if ! gcloud tasks queues describe "${TASKS_QUEUE}" --project="${PROJECT}" --location="${REGION}" >/dev/null 2>&1; then
  gcloud tasks queues create "${TASKS_QUEUE}" \
    --project="${PROJECT}" --location="${REGION}" \
    --max-dispatches-per-second=2 \
    --max-concurrent-dispatches=5 \
    --max-attempts=3 \
    --max-retry-duration=1800s \
    --min-backoff=10s --max-backoff=600s
fi

echo "==> creating service account ${SA_EMAIL}"
gcloud iam service-accounts describe "${SA_EMAIL}" --project="${PROJECT}" >/dev/null 2>&1 \
  || gcloud iam service-accounts create "${SA_NAME}" --project="${PROJECT}" --display-name="docparse Cloud Run runner"

echo "==> granting IAM"
PROJECT_NUM="$(gcloud projects describe "${PROJECT}" --format='value(projectNumber)')"

# Worker SA: read input + write output
gcloud storage buckets add-iam-policy-binding "gs://${INPUT_BUCKET}" \
  --member="serviceAccount:${SA_EMAIL}" --role="roles/storage.objectViewer" --project="${PROJECT}" >/dev/null
gcloud storage buckets add-iam-policy-binding "gs://${OUTPUT_BUCKET}" \
  --member="serviceAccount:${SA_EMAIL}" --role="roles/storage.objectAdmin" --project="${PROJECT}" >/dev/null

# Worker SA: Vertex AI + Cloud Tasks enqueue + Cloud Run invoke + Eventarc receive
gcloud projects add-iam-policy-binding "${PROJECT}" \
  --member="serviceAccount:${SA_EMAIL}" --role="roles/aiplatform.user" --condition=None >/dev/null
gcloud projects add-iam-policy-binding "${PROJECT}" \
  --member="serviceAccount:${SA_EMAIL}" --role="roles/cloudtasks.enqueuer" --condition=None >/dev/null
gcloud projects add-iam-policy-binding "${PROJECT}" \
  --member="serviceAccount:${SA_EMAIL}" --role="roles/run.invoker" --condition=None >/dev/null
gcloud projects add-iam-policy-binding "${PROJECT}" \
  --member="serviceAccount:${SA_EMAIL}" --role="roles/eventarc.eventReceiver" --condition=None >/dev/null

# Worker SA needs to act AS itself (Cloud Tasks mints OIDC tokens that hit /work)
gcloud iam service-accounts add-iam-policy-binding "${SA_EMAIL}" \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/iam.serviceAccountUser" --project="${PROJECT}" >/dev/null

# Cloud Tasks needs to mint OIDC tokens AS the worker SA
gcloud iam service-accounts add-iam-policy-binding "${SA_EMAIL}" \
  --member="serviceAccount:service-${PROJECT_NUM}@gcp-sa-cloudtasks.iam.gserviceaccount.com" \
  --role="roles/iam.serviceAccountTokenCreator" --project="${PROJECT}" >/dev/null

# GCS service agent → Pub/Sub publisher (so Eventarc can receive bucket events)
GCS_SA="$(gcloud storage service-agent --project="${PROJECT}")"
gcloud projects add-iam-policy-binding "${PROJECT}" \
  --member="serviceAccount:${GCS_SA}" --role="roles/pubsub.publisher" --condition=None >/dev/null

# Eventarc service agent → read input bucket
EVENTARC_SA="service-${PROJECT_NUM}@gcp-sa-eventarc.iam.gserviceaccount.com"
gcloud storage buckets add-iam-policy-binding "gs://${INPUT_BUCKET}" \
  --member="serviceAccount:${EVENTARC_SA}" --role="roles/storage.legacyBucketReader" --project="${PROJECT}" >/dev/null

# Default compute SA → Cloud Build builder
gcloud projects add-iam-policy-binding "${PROJECT}" \
  --member="serviceAccount:${PROJECT_NUM}-compute@developer.gserviceaccount.com" \
  --role="roles/cloudbuild.builds.builder" --condition=None >/dev/null

# Discovery Engine service agent → output bucket admin (only needed for streaming-mode datastores)
DE_SA="service-${PROJECT_NUM}@gcp-sa-discoveryengine.iam.gserviceaccount.com"
gcloud storage buckets add-iam-policy-binding "gs://${OUTPUT_BUCKET}" \
  --member="serviceAccount:${DE_SA}" --role="roles/storage.admin" --project="${PROJECT}" >/dev/null

echo "==> building image"
gcloud builds submit --tag "${IMAGE}" --project="${PROJECT}" --region="${REGION}" .

WORKER_URL_PLACEHOLDER="https://placeholder-will-update.run.app/work"

echo "==> deploying Cloud Run service (initial)"
gcloud run deploy "${SERVICE}" \
  --image="${IMAGE}" \
  --project="${PROJECT}" --region="${REGION}" \
  --service-account="${SA_EMAIL}" \
  --no-allow-unauthenticated \
  --cpu=2 --memory=2Gi \
  --concurrency=1 \
  --max-instances=10 \
  --timeout=3600 \
  --execution-environment=gen2 \
  --set-env-vars="DOCPARSE_PROJECT=${PROJECT},DOCPARSE_LOCATION=global,OUTPUT_BUCKET=${OUTPUT_BUCKET},GOOGLE_CLOUD_PROJECT=${PROJECT},TASKS_LOCATION=${REGION},TASKS_QUEUE=${TASKS_QUEUE},WORKER_SA=${SA_EMAIL},WORKER_URL=${WORKER_URL_PLACEHOLDER}"

ACTUAL_URL="$(gcloud run services describe "${SERVICE}" --project="${PROJECT}" --region="${REGION}" --format='value(status.url)')"
echo "==> patching WORKER_URL to ${ACTUAL_URL}/work"
gcloud run services update "${SERVICE}" \
  --project="${PROJECT}" --region="${REGION}" \
  --update-env-vars="WORKER_URL=${ACTUAL_URL}/work"

echo "==> creating Eventarc trigger pointing at /dispatch"
if ! gcloud eventarc triggers describe "${TRIGGER_NAME}" --location="${REGION}" --project="${PROJECT}" >/dev/null 2>&1; then
  gcloud eventarc triggers create "${TRIGGER_NAME}" \
    --location="${REGION}" --project="${PROJECT}" \
    --destination-run-service="${SERVICE}" \
    --destination-run-path="/dispatch" \
    --destination-run-region="${REGION}" \
    --event-filters="type=google.cloud.storage.object.v1.finalized" \
    --event-filters="bucket=${INPUT_BUCKET}" \
    --service-account="${SA_EMAIL}"
else
  gcloud eventarc triggers update "${TRIGGER_NAME}" \
    --location="${REGION}" --project="${PROJECT}" \
    --destination-run-path="/dispatch" || true
fi

echo
echo "==================================================="
echo "  docparse deployed (Pattern C: Cloud Tasks dedup)"
echo "  Service URL: ${ACTUAL_URL}"
echo "  Queue:       projects/${PROJECT}/locations/${REGION}/queues/${TASKS_QUEUE}"
echo
echo "  Upload:  gcloud storage cp foo.pdf gs://${INPUT_BUCKET}/"
echo "  Result:  gs://${OUTPUT_BUCKET}/foo.txt"
echo "  Logs:    gcloud beta run services logs tail ${SERVICE} --region=${REGION} --project=${PROJECT}"
echo
echo "  Storm prevention: duplicate Pub/Sub deliveries → ALREADY_EXISTS"
echo "                    Each (bucket, object, generation) extracts exactly once."
echo "==================================================="
