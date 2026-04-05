#!/bin/bash
# SharePoint WIF Portal - Cloud Run Deployment Script
set -e

# ============================================
# Configuration
# ============================================
export PROJECT_ID=${PROJECT_ID:-"sharepoint-wif-agent"}
export REGION=${REGION:-"us-central1"}
export IMAGE_NAME="sharepoint-portal"
export SERVICE_NAME="sharepoint-portal"
export REPOSITORY="cloud-run-images"

# Environment variables for the service
ENV_VARS=(
    "PROJECT_NUMBER=REDACTED_PROJECT_NUMBER"
    "ENGINE_ID=gemini-enterprise"
    "DATA_STORE_ID=sharepoint-data-def-connector_file"
    "WIF_POOL_ID=sp-wif-pool-v2"
    "WIF_PROVIDER_ID=entra-provider"
    "REASONING_ENGINE_RES=projects/REDACTED_PROJECT_NUMBER/locations/us-central1/reasoningEngines/1988251824309665792"
)

# ============================================
# Functions
# ============================================
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# ============================================
# Pre-flight Checks
# ============================================
log "=========================================="
log "SharePoint WIF Portal - Cloud Run Deploy"
log "=========================================="
log "Project:    ${PROJECT_ID}"
log "Region:     ${REGION}"
log "Service:    ${SERVICE_NAME}"
log "=========================================="

# Check gcloud auth
if ! gcloud auth print-identity-token &>/dev/null; then
    log "ERROR: Not authenticated with gcloud. Run: gcloud auth login"
    exit 1
fi

# Set project
gcloud config set project ${PROJECT_ID}

# ============================================
# Step 1: Create Artifact Registry (if needed)
# ============================================
log "[1/4] Checking Artifact Registry..."

if ! gcloud artifacts repositories describe ${REPOSITORY} --location=${REGION} &>/dev/null; then
    log "Creating Artifact Registry repository..."
    gcloud artifacts repositories create ${REPOSITORY} \
        --repository-format=docker \
        --location=${REGION} \
        --description="Cloud Run container images"
fi

# Configure Docker
gcloud auth configure-docker ${REGION}-docker.pkg.dev --quiet

# ============================================
# Step 2: Build Docker Image
# ============================================
log "[2/4] Building Docker image..."

IMAGE_URI="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/${IMAGE_NAME}:latest"

# Build from project root
cd "$(dirname "$0")/.."
docker build -t ${IMAGE_URI} .

# ============================================
# Step 3: Push to Artifact Registry
# ============================================
log "[3/4] Pushing to Artifact Registry..."

docker push ${IMAGE_URI}

# ============================================
# Step 4: Deploy to Cloud Run
# ============================================
log "[4/4] Deploying to Cloud Run..."

# Join env vars with commas
ENV_VARS_STR=$(IFS=,; echo "${ENV_VARS[*]}")

gcloud run deploy ${SERVICE_NAME} \
    --image=${IMAGE_URI} \
    --platform=managed \
    --region=${REGION} \
    --allow-unauthenticated \
    --port=8080 \
    --memory=1Gi \
    --cpu=1 \
    --min-instances=0 \
    --max-instances=10 \
    --timeout=300 \
    --set-env-vars="${ENV_VARS_STR}"

# ============================================
# Done
# ============================================
log "=========================================="
log "Deployment Complete!"
log "=========================================="

SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} \
    --region=${REGION} \
    --format='value(status.url)')

log "Service URL: ${SERVICE_URL}"
log ""
log "Next steps:"
log "1. Test the service: curl ${SERVICE_URL}/health"
log "2. Set up Load Balancer for custom domain"
log "3. Enable IAP for authentication"
log "=========================================="
