#!/bin/bash
set -e

echo "🚀 Deploying Security Proxy Backend to Cloud Run..."

# Set Google GenAI variables specifically for the cloud deployment
# This will prevent the "Missing key inputs" error in the SDK
export GOOGLE_GENAI_USE_VERTEXAI="1"

# Load local .env variables
if [ -f ../.env ]; then
  source ../.env
fi

# Fallbacks for necessary Google Cloud Project settings
PROJECT_ID=${GOOGLE_CLOUD_PROJECT:-vtxdemos}
LOCATION=${GOOGLE_CLOUD_LOCATION:-us-central1}
if [ "$LOCATION" = "global" ]; then LOCATION="us-central1"; fi

echo "Deploying to Project: $PROJECT_ID ($LOCATION)"

# We construct the set-env-vars string explicitly using ^@^ as a delimiter
# because SITE_ID contains commas that break the default syntax
ENV_VARS="^@^GOOGLE_GENAI_USE_VERTEXAI=1"
ENV_VARS="${ENV_VARS}@GOOGLE_CLOUD_PROJECT=${PROJECT_ID}"
ENV_VARS="${ENV_VARS}@GOOGLE_CLOUD_LOCATION=${LOCATION}"

if [ -n "$TENANT_ID" ]; then
  ENV_VARS="${ENV_VARS}@TENANT_ID=${TENANT_ID}"
fi
if [ -n "$CLIENT_ID" ]; then
  ENV_VARS="${ENV_VARS}@CLIENT_ID=${CLIENT_ID}"
fi
if [ -n "$SITE_ID" ]; then
  ENV_VARS="${ENV_VARS}@SITE_ID=${SITE_ID}"
fi
if [ -n "$DRIVE_ID" ]; then
  ENV_VARS="${ENV_VARS}@DRIVE_ID=${DRIVE_ID}"
fi
if [ -n "$DATA_STORE_LOCATION" ]; then
  ENV_VARS="${ENV_VARS}@DATA_STORE_LOCATION=${DATA_STORE_LOCATION}"
fi
if [ -n "$DATA_STORE_PROJECT_ID" ]; then
  ENV_VARS="${ENV_VARS}@DATA_STORE_PROJECT_ID=${DATA_STORE_PROJECT_ID}"
fi
if [ -n "$FINANCIAL_DATA_STORE_ID" ]; then
  ENV_VARS="${ENV_VARS}@FINANCIAL_DATA_STORE_ID=${FINANCIAL_DATA_STORE_ID}"
fi

# Deploying with --allow-unauthenticated because MSAL authentication
# is enforced strictly by zero-leak validation in main.py
gcloud run deploy mcp-sharepoint-server \
  --source . \
  --project $PROJECT_ID \
  --region $LOCATION \
  --allow-unauthenticated \
  --set-env-vars="$ENV_VARS" \
  --min-instances=0 \
  --max-instances=5 \
  --quiet

echo "✅ Backend deployed successfully."
