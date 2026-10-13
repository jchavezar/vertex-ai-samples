#!/usr/bin/env bash
set -e

PROJECT="vtxdemos"
REGION="us-central1"
IMAGE="gcr.io/vtxdemos/rocket-argon-suite:latest"

declare -A SERVICES=(
  ["rocket-hackathon-portal"]="portal"
  ["rocket-demo-origination"]="sales"
  ["rocket-demo-underwriting"]="ops"
  ["rocket-demo-servicing"]="servicing"
  ["rocket-demo-marketing"]="marketing"
  ["rocket-demo-compliance"]="risk"
  ["rocket-demo-sdlc"]="sdlc"
  ["rocket-demo-moonshots"]="moonshots"
)

pids=()
for svc in "${!SERVICES[@]}"; do
  mode="${SERVICES[$svc]}"
  echo "Deploying $svc (SERVICE_MODE=$mode)..."
  (
    gcloud run deploy "$svc" \
      --image "$IMAGE" \
      --project "$PROJECT" \
      --region "$REGION" \
      --platform managed \
      --allow-unauthenticated \
      --memory 1Gi \
      --cpu 1 \
      --set-env-vars="SERVICE_MODE=${mode},ROCKET_AUTH_USER=rocket,ROCKET_AUTH_PASS=Argon2026!" \
      --quiet
    echo "✅ Deployed $svc"
  ) &
  pids+=($!)
done

for pid in "${pids[@]}"; do
  wait "$pid"
done

echo "🎉 All 8 separated Cloud Run services deployed successfully!"
