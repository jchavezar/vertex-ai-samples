#!/bin/bash
set -e

PROJECT=vtxdemos
REGION=us-central1
SERVICE=vais-gdrive-search
IMAGE=gcr.io/$PROJECT/$SERVICE

echo "Building and pushing container image..."
CLOUDSDK_CORE_ACCOUNT=admin@jesusarguelles.altostrat.com CLOUDSDK_CORE_PROJECT=$PROJECT gcloud builds submit --tag $IMAGE .

echo "Deploying to Cloud Run..."
CLOUDSDK_CORE_ACCOUNT=admin@jesusarguelles.altostrat.com gcloud run deploy $SERVICE \
  --image $IMAGE \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --port 8080 \
  --project $PROJECT \
  --set-env-vars "PROJECT_ID=254356041555,ENGINE_ID=vais-workspace_1779830576232,GOOGLE_OAUTH_CLIENT_ID=254356041555-9b04u6obh8efjp6erog7fj12fnviop71.apps.googleusercontent.com"

echo ""
echo "Deployment complete."
echo "IMPORTANT: If this is your first deploy, copy the Cloud Run URL shown above and:"
echo "  1. Add it as an Authorized JavaScript Origin in your OAuth 2.0 client"
echo "  2. Update GOOGLE_OAUTH_CLIENT_ID in this script (replace 254356041555-9b04u6obh8efjp6erog7fj12fnviop71.apps.googleusercontent.com)"
echo "  3. Update window.APP_CONFIG.clientId in static/index.html"
echo "  4. Re-run this script to apply changes"
