#!/bin/bash
# Deploy Microsoft 365 MCP Server to Cloud Run
set -e

# Configuration
PROJECT_ID="${GCP_PROJECT:-$(gcloud config get-value project)}"
REGION="${GCP_REGION:-us-central1}"
SERVICE_NAME="ms365-mcp-server"
REPO_NAME="mcp-servers"

echo "=== Microsoft 365 MCP Server Deployment ==="
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo "Service: $SERVICE_NAME"

# Check for required environment variables
if [ -z "$MS365_CLIENT_ID" ]; then
    echo ""
    echo "ERROR: MS365_CLIENT_ID environment variable is required."
    echo ""
    echo "Before deploying, you need to:"
    echo "1. Create an Azure AD app registration"
    echo "2. Set MS365_CLIENT_ID to the Application (client) ID"
    echo "3. Optionally set MS365_TENANT_ID (defaults to 'common')"
    echo ""
    echo "Example:"
    echo "  export MS365_CLIENT_ID='your-app-client-id'"
    echo "  export MS365_TENANT_ID='your-tenant-id'"
    echo "  ./deploy.sh"
    exit 1
fi

# Create Artifact Registry repository if it doesn't exist
echo ""
echo "=== Creating Artifact Registry repository ==="
gcloud artifacts repositories create $REPO_NAME \
    --repository-format=docker \
    --location=$REGION \
    --description="MCP Server container images" \
    2>/dev/null || echo "Repository already exists"

# Build and push container image
echo ""
echo "=== Building and pushing container image ==="
IMAGE_URI="$REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/$SERVICE_NAME:latest"

gcloud builds submit \
    --tag $IMAGE_URI \
    --quiet

# Deploy to Cloud Run
echo ""
echo "=== Deploying to Cloud Run ==="
gcloud run deploy $SERVICE_NAME \
    --image $IMAGE_URI \
    --region $REGION \
    --platform managed \
    --no-allow-unauthenticated \
    --set-env-vars="MS365_CLIENT_ID=$MS365_CLIENT_ID,MS365_TENANT_ID=${MS365_TENANT_ID:-common}" \
    --memory=512Mi \
    --cpu=1 \
    --min-instances=0 \
    --max-instances=3 \
    --timeout=300

# Get service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
    --region $REGION \
    --format='value(status.url)')

echo ""
echo "=== Deployment Complete ==="
echo ""
echo "Service URL: $SERVICE_URL"
echo ""
echo "To connect from Claude Code:"
echo ""
echo "1. Start the Cloud Run proxy:"
echo "   gcloud run services proxy $SERVICE_NAME --region $REGION --port=8080"
echo ""
echo "2. Add MCP to Claude Code:"
echo "   claude mcp add ms365 --transport http http://localhost:8080/mcp"
echo ""
echo "3. In Claude Code, run 'ms365_login' to authenticate"
