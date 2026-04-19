#!/usr/bin/env bash
# Build + deploy the user-facing Envato Vibe v2 FastAPI app to Cloud Run.
# Idempotent: re-run after code changes.
#
# Notes
#   * `gcloud run deploy --source .` does not accept a custom Dockerfile path,
#     so we do it in two steps:
#       1) gcloud builds submit . --tag <image>   (using a Cloud Build config
#          that points at Dockerfile.app)
#       2) gcloud run deploy --image=<image>
#   * The repo's existing .gcloudignore is tailored to the *ingest* build and
#     EXCLUDES app_v2.py / templates/ / static/.  We temporarily swap in
#     .gcloudignore.app for the duration of `builds submit`, then restore.
set -euo pipefail

PROJECT=${GOOGLE_CLOUD_PROJECT:-vtxdemos}
REGION=${GOOGLE_CLOUD_LOCATION:-us-central1}
BUCKET=${ENVATO_GCS_BUCKET:-envato-vibe-demo}
SA="envato-vibe-runner@${PROJECT}.iam.gserviceaccount.com"
SERVICE="envato-vibe-app"
IMAGE="gcr.io/${PROJECT}/${SERVICE}:latest"

# Resolve repo root regardless of where this is invoked from.
# This script lives at envato/deploy/, so REPO_ROOT is two levels up.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
DOCKERFILE_REL="envato/deploy/Dockerfile.app"
GCLOUDIGNORE_SRC="${SCRIPT_DIR}/.gcloudignore.app"
cd "${REPO_ROOT}"

if [[ ! -f "${DOCKERFILE_REL}" ]]; then
  echo "ERROR: ${DOCKERFILE_REL} not found under repo root (${REPO_ROOT})." >&2
  exit 1
fi
if [[ ! -f "${GCLOUDIGNORE_SRC}" ]]; then
  echo "ERROR: ${GCLOUDIGNORE_SRC} not found." >&2
  exit 1
fi

# Generate an inline Cloud Build config that points at envato/deploy/Dockerfile.app.
BUILD_CFG="$(mktemp -t envato-vibe-app-cloudbuild.XXXXXX.yaml)"
cat >"${BUILD_CFG}" <<EOF
steps:
- name: gcr.io/cloud-builders/docker
  args: ['build', '-f', '${DOCKERFILE_REL}', '-t', '${IMAGE}', '.']
images:
- '${IMAGE}'
options:
  logging: CLOUD_LOGGING_ONLY
EOF

# .gcloudignore is auto-detected from the source root. Stage our app-specific
# ignore for the duration of `builds submit`, then restore.
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
  rm -f "${BUILD_CFG}"
}
trap restore_gcloudignore EXIT

if [[ -f .gcloudignore ]]; then
  cp .gcloudignore .gcloudignore.bak
fi
cp "${GCLOUDIGNORE_SRC}" .gcloudignore

echo "→ Building image ${IMAGE} (Dockerfile.app)"
gcloud builds submit . \
  --project "${PROJECT}" \
  --config "${BUILD_CFG}"

# Restore the original ignore file before deploying so subsequent ingest
# builds keep working.
restore_gcloudignore

echo "→ Deploying ${SERVICE} from ${IMAGE}"
gcloud run deploy "${SERVICE}" \
  --image "${IMAGE}" \
  --region "${REGION}" \
  --project "${PROJECT}" \
  --service-account "${SA}" \
  --memory 2Gi --cpu 2 --timeout 600 \
  --allow-unauthenticated \
  --set-env-vars "GOOGLE_GENAI_USE_VERTEXAI=True,GOOGLE_CLOUD_PROJECT=${PROJECT},GOOGLE_CLOUD_LOCATION=${REGION},ENVATO_GCS_BUCKET=${BUCKET}"

URL=$(gcloud run services describe "${SERVICE}" --region "${REGION}" --project "${PROJECT}" --format 'value(status.url)')
echo
echo "✓ Deployed.  Service URL: ${URL}"
