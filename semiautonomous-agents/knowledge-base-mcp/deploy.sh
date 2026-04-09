#!/bin/bash
set -e

PROJECT_ID="${GCP_PROJECT:-$(gcloud config get-value project 2>/dev/null)}"
REGION="${GCP_REGION:-us-central1}"
SERVICE_NAME="knowledge-base-mcp"
REPO_NAME="mcp-servers"

echo "=== Knowledge Base MCP Server Deployment ==="
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo "Service: $SERVICE_NAME"
echo ""

# Create Artifact Registry repository if it doesn't exist
gcloud artifacts repositories create $REPO_NAME \
    --repository-format=docker \
    --location=$REGION \
    --description="MCP Server container images" \
    2>/dev/null || echo "Repository already exists"

# Build and push
IMAGE_URI="$REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/$SERVICE_NAME:latest"
echo "Building image: $IMAGE_URI"
gcloud builds submit --tag $IMAGE_URI --quiet

# Deploy to Cloud Run
echo "Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
    --image $IMAGE_URI \
    --region $REGION \
    --platform managed \
    --no-allow-unauthenticated \
    --set-env-vars="GOOGLE_CLOUD_PROJECT=$PROJECT_ID,GOOGLE_CLOUD_LOCATION=$REGION" \
    --memory=1Gi \
    --cpu=1 \
    --min-instances=0 \
    --max-instances=3 \
    --timeout=300

SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
    --region $REGION \
    --format='value(status.url)')

echo ""
echo "=== Deployment Complete ==="
echo "Service URL: $SERVICE_URL"
echo ""
echo "=== Connect from Claude Code ==="
echo "  gcloud run services proxy $SERVICE_NAME --region $REGION --port=8082"
echo "  claude mcp add knowledge-base --transport http http://localhost:8082/mcp"
echo ""
echo "=== Connect from Gemini CLI ==="
echo "  Add to ~/.gemini/settings.json:"
echo "  {\"mcpServers\": {\"knowledge-base\": {\"url\": \"http://localhost:8082/mcp\"}}}"
echo ""
echo "=== Create Firestore Vector Index (one-time) ==="
echo "  gcloud firestore indexes composite create \\"
echo "    --collection-group=knowledge \\"
echo "    --field-config=vector-config='{\"dimension\":768,\"flat\":{}}',field-path=embedding"
