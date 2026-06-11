#!/usr/bin/env bash
# Build + deploy the demos.sonrobots.net hub to Cloud Run.
# Ingress = internal-and-cloud-load-balancing (only reachable via GLB+IAP).
set -euo pipefail

PROJECT=${GOOGLE_CLOUD_PROJECT:-vtxdemos}
REGION=${GOOGLE_CLOUD_LOCATION:-us-central1}
SERVICE="demos-hub"
IMAGE="gcr.io/${PROJECT}/${SERVICE}:latest"
SA="254356041555-compute@developer.gserviceaccount.com"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SVC_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${SVC_ROOT}"

BUILD_CFG="$(mktemp -t demos-hub-cloudbuild.XXXXXX.yaml)"
trap 'rm -f "${BUILD_CFG}"' EXIT
cat >"${BUILD_CFG}" <<EOF
steps:
- name: gcr.io/cloud-builders/docker
  args: ['build', '-f', 'deploy/Dockerfile', '-t', '${IMAGE}', '.']
images:
- '${IMAGE}'
options:
  logging: CLOUD_LOGGING_ONLY
EOF

echo "→ Building ${IMAGE}"
gcloud builds submit . --project "${PROJECT}" --config "${BUILD_CFG}"

echo "→ Deploying ${SERVICE}"
gcloud run deploy "${SERVICE}" \
  --image "${IMAGE}" \
  --region "${REGION}" \
  --project "${PROJECT}" \
  --service-account "${SA}" \
  --ingress internal-and-cloud-load-balancing \
  --no-allow-unauthenticated \
  --memory 512Mi --cpu 1 --timeout 60 \
  --min-instances 0 --max-instances 5

URL=$(gcloud run services describe "${SERVICE}" --region "${REGION}" --project "${PROJECT}" --format 'value(status.url)')
echo
echo "✓ Deployed (internal-only). Cloud Run URL: ${URL}"
echo "  Public URL after GLB plumbing: https://demos.sonrobots.net/"
