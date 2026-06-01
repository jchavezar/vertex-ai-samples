#!/usr/bin/env bash
# Deploy the BigQuery-backed flavour of the Vibe Search app.
# Reuses the SAME container image as the Vector Search service
# (multimodal-search/deploy/deploy_app.sh must have been run at least once
# so gcr.io/${PROJECT}/envato-vibe-app:latest exists).
#
# What's different from the Vector Search service:
#   * service name:  envato-vibe-app-bq         (vs envato-vibe-app)
#   * SEARCH_BACKEND=bigquery                   (vs vector-search)
#   * --min-instances=0 + Cloud Scheduler warmup recommended
#   * cheaper: scale-to-zero, no Vector Search endpoint dependency
set -euo pipefail

PROJECT=${GOOGLE_CLOUD_PROJECT:-vtxdemos}
REGION=${GOOGLE_CLOUD_LOCATION:-us-central1}
BUCKET=${ENVATO_GCS_BUCKET:-envato-vibe-demo}
SA="envato-vibe-runner@${PROJECT}.iam.gserviceaccount.com"
SERVICE="envato-vibe-app-bq"
IMAGE="gcr.io/${PROJECT}/envato-vibe-app:latest"   # reuse VS image

BQ_TABLE="${BQ_TABLE:-${PROJECT}.envato_vibe.segments}"

echo "→ Deploying ${SERVICE} from ${IMAGE} with SEARCH_BACKEND=bigquery"

gcloud run deploy "${SERVICE}" \
  --image "${IMAGE}" \
  --region "${REGION}" \
  --project "${PROJECT}" \
  --service-account "${SA}" \
  --memory 2Gi --cpu 2 --timeout 600 \
  --min-instances 0 --max-instances 10 \
  --allow-unauthenticated \
  --set-env-vars "GOOGLE_GENAI_USE_VERTEXAI=True,GOOGLE_CLOUD_PROJECT=${PROJECT},GOOGLE_CLOUD_LOCATION=${REGION},ENVATO_GCS_BUCKET=${BUCKET},SEARCH_BACKEND=bigquery,BQ_TABLE=${BQ_TABLE}"

URL=$(gcloud run services describe "${SERVICE}" --region "${REGION}" --project "${PROJECT}" --format 'value(status.url)')
echo
echo "✓ Deployed.  Service URL: ${URL}"
echo
echo "Hit /api/warmup once to prime: curl -s ${URL}/api/warmup"
echo "Optional Cloud Scheduler keep-alive (every 5 min, near-zero cost):"
echo "  gcloud scheduler jobs create http envato-vibe-bq-warmup \\"
echo "    --project ${PROJECT} --location ${REGION} \\"
echo "    --schedule '*/5 * * * *' --uri ${URL}/api/warmup --http-method GET"
