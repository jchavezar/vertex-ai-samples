#!/usr/bin/env bash
set -euo pipefail

PROJECT_ID="vtxdemos"
REGION="us-central1"
IMAGE="us-central1-docker.pkg.dev/${PROJECT_ID}/cloud-run-source-deploy/mike-gcp-platform:v3.4.0"
COMMON_ENV="GOOGLE_CLOUD_PROJECT=${PROJECT_ID},VERTEX_PROJECT_ID=${PROJECT_ID},VERTEX_LOCATION=global,SPANNER_INSTANCE=lexgraph-legal-spanner,SPANNER_DATABASE=lexgraph-legal-context,DEFAULT_CHAT_MODEL=gemini-3.8-flash,REASONING_CHAT_MODEL=gemini-3.7-flash,OTEL_TO_CLOUD=true"

echo "=== Building ${IMAGE} via Cloud Build ==="
gcloud builds submit /usr/local/google/home/jesusarguelles/lexgraph --project="${PROJECT_ID}" --tag="${IMAGE}" --quiet

echo "=== Deploying all 5 Cloud Run services in parallel from ${IMAGE} ==="

gcloud run deploy mike-gcp-platform \
  --project="${PROJECT_ID}" --region="${REGION}" --image="${IMAGE}" --platform="managed" \
  --memory="2Gi" --cpu="2" --concurrency="80" --min-instances="1" --max-instances="10" --timeout="300" \
  --set-env-vars="${COMMON_ENV},DEFAULT_STUDIO_VIEW=tabular-view,DEFAULT_MCP_RESOURCE_URI=ui://mike-gcp/workspace.html" \
  --allow-unauthenticated --quiet &

gcloud run deploy lexgraph-redline-word-agent \
  --project="${PROJECT_ID}" --region="${REGION}" --image="${IMAGE}" --platform="managed" \
  --memory="2Gi" --cpu="2" --concurrency="80" --min-instances="0" --max-instances="5" --timeout="300" \
  --set-env-vars="${COMMON_ENV},DEFAULT_STUDIO_VIEW=redline-view,DEFAULT_MCP_RESOURCE_URI=ui://mike-gcp/redline-studio.html" \
  --allow-unauthenticated --quiet &

gcloud run deploy lexgraph-funds-antitrust-agent \
  --project="${PROJECT_ID}" --region="${REGION}" --image="${IMAGE}" --platform="managed" \
  --memory="2Gi" --cpu="2" --concurrency="80" --min-instances="0" --max-instances="5" --timeout="300" \
  --set-env-vars="${COMMON_ENV},DEFAULT_STUDIO_VIEW=funds-view,DEFAULT_MCP_RESOURCE_URI=ui://mike-gcp/funds-antitrust.html" \
  --allow-unauthenticated --quiet &

gcloud run deploy lexgraph-governance-wall-agent \
  --project="${PROJECT_ID}" --region="${REGION}" --image="${IMAGE}" --platform="managed" \
  --memory="2Gi" --cpu="2" --concurrency="80" --min-instances="0" --max-instances="5" --timeout="300" \
  --set-env-vars="${COMMON_ENV},DEFAULT_STUDIO_VIEW=governance-view,DEFAULT_MCP_RESOURCE_URI=ui://mike-gcp/governance-wall.html" \
  --allow-unauthenticated --quiet &

gcloud run deploy lexgraph-inbox-calendar-agent \
  --project="${PROJECT_ID}" --region="${REGION}" --image="${IMAGE}" --platform="managed" \
  --memory="2Gi" --cpu="2" --concurrency="80" --min-instances="0" --max-instances="5" --timeout="300" \
  --set-env-vars="${COMMON_ENV},DEFAULT_STUDIO_VIEW=inbox-view,DEFAULT_MCP_RESOURCE_URI=ui://mike-gcp/inbox-calendar.html" \
  --allow-unauthenticated --quiet &

wait
echo "=== All 5 Cloud Run Services Deployed Successfully! ==="
for svc in mike-gcp-platform lexgraph-redline-word-agent lexgraph-funds-antitrust-agent lexgraph-governance-wall-agent lexgraph-inbox-calendar-agent; do
  url=$(gcloud run services describe "$svc" --project="${PROJECT_ID}" --region="${REGION}" --format="value(status.url)")
  echo "  -> $svc : $url"
done
