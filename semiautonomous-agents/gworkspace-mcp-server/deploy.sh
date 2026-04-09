#!/bin/bash
# Deploy Google Workspace MCP Server to Cloud Run
set -e

# Configuration
PROJECT_ID="${GCP_PROJECT:-$(gcloud config get-value project)}"
REGION="${GCP_REGION:-us-central1}"
SERVICE_NAME="gworkspace-mcp-server"
REPO_NAME="mcp-servers"

echo "=== Google Workspace MCP Server Deployment ==="
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo "Service: $SERVICE_NAME"

# Check for required environment variables
if [ -z "$GOOGLE_CLIENT_ID" ]; then
    echo ""
    echo "ERROR: GOOGLE_CLIENT_ID environment variable is required."
    echo ""
    echo "Before deploying, you need to:"
    echo "1. Create a Google Cloud OAuth 2.0 client"
    echo "2. Set GOOGLE_CLIENT_ID to the Client ID"
    echo "3. Set GOOGLE_CLIENT_SECRET to the Client Secret"
    echo ""
    echo "Example:"
    echo "  export GOOGLE_CLIENT_ID='your-client-id.apps.googleusercontent.com'"
    echo "  export GOOGLE_CLIENT_SECRET='your-client-secret'"
    echo "  ./deploy.sh"
    exit 1
fi

if [ -z "$GOOGLE_CLIENT_SECRET" ]; then
    echo ""
    echo "ERROR: GOOGLE_CLIENT_SECRET environment variable is required."
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
    --set-env-vars="GOOGLE_CLIENT_ID=$GOOGLE_CLIENT_ID,GOOGLE_CLIENT_SECRET=$GOOGLE_CLIENT_SECRET" \
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
echo "   gcloud run services proxy $SERVICE_NAME --region $REGION --port=8081"
echo ""
echo "2. Add MCP to Claude Code:"
echo "   claude mcp add gworkspace --transport http http://localhost:8081/mcp"
echo ""
echo "3. In Claude Code, run 'gworkspace_login' to authenticate"
