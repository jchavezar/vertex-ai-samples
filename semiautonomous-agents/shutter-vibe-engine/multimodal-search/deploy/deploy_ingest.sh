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
# This script lives at multimodal-search/deploy/, so REPO_ROOT is two levels up.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
IMAGE="gcr.io/${PROJECT}/${SERVICE}:latest"
DOCKERFILE_REL="multimodal-search/deploy/Dockerfile.ingest"
GCLOUDIGNORE_SRC="${SCRIPT_DIR}/.gcloudignore.ingest"
cd "${REPO_ROOT}"

if [[ ! -f "${DOCKERFILE_REL}" ]]; then
  echo "ERROR: ${DOCKERFILE_REL} not found under repo root (${REPO_ROOT})." >&2
  exit 1
fi
if [[ ! -f "${GCLOUDIGNORE_SRC}" ]]; then
  echo "ERROR: ${GCLOUDIGNORE_SRC} not found." >&2
  exit 1
fi

# Stage our ingest-specific .gcloudignore at REPO_ROOT for the build, restore after.
RESTORED=0
restore_gcloudignore() {
  if [[ "${RESTORED}" -eq 0 ]]; then
    if [[ -f .gcloudignore.bak ]]; then
      mv .gcloudignore.bak .gcloudignore
    else
      rm -f .gcloudignore
    fi
    RESTORED=1
  fi
}
trap 'restore_gcloudignore; rm -f "${BUILD_CFG:-}"' EXIT

if [[ -f .gcloudignore ]]; then
  cp .gcloudignore .gcloudignore.bak
fi
cp "${GCLOUDIGNORE_SRC}" .gcloudignore

echo "→ Granting Eventarc/Pub-Sub the right to invoke our service"
PROJECT_NUM=$(gcloud projects describe "${PROJECT}" --format='value(projectNumber)')
GCS_AGENT="service-${PROJECT_NUM}@gs-project-accounts.iam.gserviceaccount.com"
gcloud projects add-iam-policy-binding "${PROJECT}" \
  --member="serviceAccount:${GCS_AGENT}" \
  --role="roles/pubsub.publisher" --condition=None --quiet >/dev/null

# Build the image with an explicit Dockerfile path (the auto-detected
# Dockerfile at REPO_ROOT no longer exists after the reorg).
BUILD_CFG="$(mktemp -t vibe-search-ingest-cloudbuild.XXXXXX.yaml)"
cat >"${BUILD_CFG}" <<EOF
steps:
- name: gcr.io/cloud-builders/docker
  args: ['build', '-f', '${DOCKERFILE_REL}', '-t', '${IMAGE}', '.']
images:
- '${IMAGE}'
options:
  logging: CLOUD_LOGGING_ONLY
EOF
trap 'rm -f "${BUILD_CFG}"' EXIT

echo "→ Building image ${IMAGE} (${DOCKERFILE_REL})"
gcloud builds submit . --project "${PROJECT}" --config "${BUILD_CFG}"

echo "→ Deploying ${SERVICE} from ${IMAGE}"
gcloud run deploy "${SERVICE}" \
  --image "${IMAGE}" \
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
