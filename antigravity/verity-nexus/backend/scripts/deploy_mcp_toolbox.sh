#!/bin/bash

# Exit on error
set -e

# Config
REGION="us-central1"
SERVICE_NAME="mcp-ledger-toolbox"
IMAGE="us-central1-docker.pkg.dev/database-toolbox/toolbox/toolbox:latest"

echo "Deploying Gen AI Toolbox for Databases to Cloud Run..."
echo "Service: $SERVICE_NAME"
echo "Image: $IMAGE"

# Since we don't have Artifact Registry push permissions to build a custom image 
# that embeds tools.yaml, we will deploy the official image directly and mount 
# tools.yaml as a Secret or ConfigMap. 
# Cloud Run supports mounting Secrets as files.

# 1. Create a secret for tools.yaml
SECRET_NAME="mcp-ledger-tools-config"

PROJECT="vtxdemos"

echo "Creating/Updating Secret Manager secret '$SECRET_NAME'..."
if gcloud secrets describe $SECRET_NAME --project=$PROJECT >/dev/null 2>&1; then
  echo "Secret exists, adding new version..."
  gcloud secrets versions add $SECRET_NAME --data-file=./tools.yaml --project=$PROJECT
else
  echo "Creating new secret..."
  gcloud secrets create $SECRET_NAME --data-file=./tools.yaml --replication-policy=automatic --project=$PROJECT
fi

# 2. Deploy the official container, mounting the secret as a file
echo "Deploying Cloud Run service..."
gcloud run deploy $SERVICE_NAME \
  --image $IMAGE \
  --project $PROJECT \
  --region $REGION \
  --allow-unauthenticated \
  --port 8080 \
  --add-cloudsql-instances="vtxdemos:us-central1:pg15-pgvector-demo" \
  --set-secrets="/config/tools.yaml=$SECRET_NAME:latest" \
  --command="" \
  --args="--tools-file=/config/tools.yaml,--port=8080,--address=0.0.0.0,--disable-reload"

echo "Deployment complete!"
