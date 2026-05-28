#!/usr/bin/env bash
# Deploy the SharePoint MCP server to Cloud Run in project vtxdemos.
set -euo pipefail

PROJECT_ID="${GOOGLE_CLOUD_PROJECT:-vtxdemos}"
REGION="${GOOGLE_CLOUD_LOCATION:-us-central1}"
SERVICE_NAME="${SERVICE_NAME:-ge-custom-sharepoint-mcp}"

gcloud run deploy "$SERVICE_NAME" --source . --project "$PROJECT_ID" --region "$REGION" --platform managed --no-allow-unauthenticated --memory=1Gi --cpu=2 --min-instances=0 --max-instances=5 --timeout=300

SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" --project "$PROJECT_ID" --region "$REGION" --format='value(status.url)')
echo ""
echo "Service URL : $SERVICE_URL"
echo "MCP endpoint: $SERVICE_URL/mcp"
