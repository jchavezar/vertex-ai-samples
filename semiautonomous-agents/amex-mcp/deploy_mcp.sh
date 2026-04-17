#!/bin/bash
# Deploy Amex MCP Server to Cloud Run
set -e

PROJECT_ID="${GCP_PROJECT_ID:-vtxdemos}"
REGION="us-east1"
SERVICE_NAME="amex-mcp-server"
REPO_NAME="cloud-run-source-deploy"

echo "=== Amex MCP Server Deployment ==="
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo "Service: $SERVICE_NAME"

# Build and push container image
echo ""
echo "=== Building container image ==="
IMAGE_URI="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/${SERVICE_NAME}:latest"

gcloud builds submit \
    --project="${PROJECT_ID}" \
    --region="${REGION}" \
    --tag="${IMAGE_URI}" \
    --quiet

# Deploy to Cloud Run
echo ""
echo "=== Deploying to Cloud Run ==="
gcloud run deploy "${SERVICE_NAME}" \
    --project="${PROJECT_ID}" \
    --image="${IMAGE_URI}" \
    --region="${REGION}" \
    --platform=managed \
    --no-allow-unauthenticated \
    --set-env-vars="GCP_PROJECT_ID=${PROJECT_ID}" \
    --memory=1Gi \
    --cpu=1 \
    --min-instances=0 \
    --max-instances=3 \
    --timeout=300

# Get service URL
SERVICE_URL=$(gcloud run services describe "${SERVICE_NAME}" \
    --project="${PROJECT_ID}" \
    --region="${REGION}" \
    --format='value(status.url)')

echo ""
echo "=== Deployment Complete ==="
echo ""
echo "Service URL: ${SERVICE_URL}"
echo ""
echo "To connect from Claude Code:"
echo ""
echo "1. Start the Cloud Run proxy:"
echo "   gcloud run services proxy ${SERVICE_NAME} --region ${REGION} --port=8082"
echo ""
echo "2. Add MCP to Claude Code:"
echo "   claude mcp add amex --transport http http://localhost:8082/mcp"
