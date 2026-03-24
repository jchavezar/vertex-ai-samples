#!/bin/bash
# deploy.sh - Deploys OpenRouter Tracker to Cloud Run + Cloud Scheduler

# Exit on error
set -e

PROJECT_ID="vtxdemos"
REGION="us-central1"
SERVICE_NAME="openrouter-tracker"
IMAGE_NAME="gcr.io/$PROJECT_ID/$SERVICE_NAME"
CRON_JOB_NAME="openrouter-stats-daily"

echo "=========================================================="
echo "🚀 Deploying $SERVICE_NAME to Cloud Run on $PROJECT_ID"
echo "=========================================================="

# 1. Build and push image to Artifact Registry/GCR
echo "📦 Building and pushing Docker container image..."
gcloud builds submit --tag $IMAGE_NAME .

# 2. Deploy to Cloud Run
echo "☁️ Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
    --image $IMAGE_NAME \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 1 \
    --timeout 3600 \
    --no-cpu-throttling \
    --set-env-vars PROJECT_ID=$PROJECT_ID



# Get the URL of the deployed service
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region $REGION --format='value(status.url)')
echo "✅ Cloud Run deployed successfully at: $SERVICE_URL"

# 3. Create Cloud Scheduler Trigger
echo "⏱ SETUP Automatic Cron Trigger (Daily at 1 AM)..."

TRIGGER_URL="$SERVICE_URL/run"

# Check if Cloud Scheduler already exists
if gcloud scheduler jobs describe $CRON_JOB_NAME --location $REGION > /dev/null 2>&1; then
    echo "Updating existing Cloud Scheduler job to 6-hour frequency..."
    gcloud scheduler jobs update http $CRON_JOB_NAME \
        --schedule="0 */6 * * *" \
        --uri=$TRIGGER_URL \
        --http-method=GET \
        --location=$REGION
else
    echo "Creating new Cloud Scheduler job (Every 6 hours)..."
    gcloud scheduler jobs create http $CRON_JOB_NAME \
        --schedule="0 */6 * * *" \
        --uri=$TRIGGER_URL \
        --http-method=GET \
        --location=$REGION
fi



echo "=========================================================="
echo "🎉 DEPLOYMENT COMPLETE!"
echo "📍 API / Trigger Endpoint: $TRIGGER_URL"
echo "📍 Dashboard: Updates Daily at 1:00 AM"
echo "=========================================================="
