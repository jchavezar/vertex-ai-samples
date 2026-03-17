#!/bin/bash
set -e

# ==============================================================================
# Cloud Run + Google Global Load Balancer + IAP Deployment Script
# ==============================================================================
# This script deploys the application as a container to Cloud Run, sets up a 
# Global External HTTPS Load Balancer with a self-signed certificate (or 
# managed certificate), and enables Identity-Aware Proxy (IAP) for access
# control, limiting access to a specific email address.
#
# PREREQUISITES:
# 1. OAuth Consent Screen must be configured in your GCP Project.
# 2. You must create an OAuth Client ID for Web Application.
# 3. Export these variables before running the script:
#    export OAUTH_CLIENT_ID="your-client-id.apps.googleusercontent.com"
#    export OAUTH_CLIENT_SECRET="your-client-secret"
# ==============================================================================

# Variables
PROJECT_ID=$(gcloud config get-value project)
APP_NAME="global-tax-intel"
REGION="us-central1"
SERVICE_NAME="${APP_NAME}-service"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${APP_NAME}"
ALLOWED_EMAIL="admin@jesusarguelles.altostrat.com"

# GLB & IAP Variables
NEG_NAME="${APP_NAME}-serverless-neg"
BACKEND_SERVICE="${APP_NAME}-backend"
URL_MAP="${APP_NAME}-url-map"
HTTP_PROXY="${APP_NAME}-http-proxy"
HTTPS_PROXY="${APP_NAME}-https-proxy"
FORWARDING_RULE="${APP_NAME}-forwarding-rule"
HTTPS_FORWARDING_RULE="${APP_NAME}-https-forwarding-rule"
IP_ADDRESS_NAME="${APP_NAME}-ip"
CERT_NAME="${APP_NAME}-cert"

echo "==================================================================="
echo "Starting Deployment for $APP_NAME in project $PROJECT_ID"
echo "==================================================================="

# 1. Enable Required APIs
echo "[1] Enabling required Google Cloud APIs..."
gcloud services enable \
    run.googleapis.com \
    compute.googleapis.com \
    cloudbuild.googleapis.com \
    iap.googleapis.com

# 2. Build and Deploy to Cloud Run
echo "[2] Building and Deploying to Cloud Run from source..."
gcloud run deploy "$SERVICE_NAME" \
    --source . \
    --region "$REGION" \
    --platform managed \
    --ingress internal-and-cloud-load-balancing \
    --allow-unauthenticated \
    --quiet

# We allow unauthenticated at the Cloud Run level because IAP will handle
# authentication at the Load Balancer level. The ingress rule restricts traffic 
# to just the load balancer.

# 3. Reserve a Global Static IP Address
echo "[4] Reserving Global Static IP Address..."
if ! gcloud compute addresses describe "$IP_ADDRESS_NAME" --global >/dev/null 2>&1; then
    gcloud compute addresses create "$IP_ADDRESS_NAME" \
        --network-tier=PREMIUM \
        --ip-version=IPV4 \
        --global
fi
IP_ADDRESS=$(gcloud compute addresses describe "$IP_ADDRESS_NAME" --global --format="value(address)")
echo "Reserved IP: $IP_ADDRESS"

# 4. Create Serverless NEG
echo "[5] Creating Serverless Network Endpoint Group (NEG)..."
if ! gcloud compute network-endpoint-groups describe "$NEG_NAME" --region="$REGION" >/dev/null 2>&1; then
    gcloud compute network-endpoint-groups create "$NEG_NAME" \
        --region="$REGION" \
        --network-endpoint-type=serverless \
        --cloud-run-service="$SERVICE_NAME"
fi

# 5. Create Backend Service
echo "[6] Creating Backend Service..."
if ! gcloud compute backend-services describe "$BACKEND_SERVICE" --global >/dev/null 2>&1; then
    gcloud compute backend-services create "$BACKEND_SERVICE" \
        --global
fi

echo "[7] Adding NEG to Backend Service..."
if ! gcloud compute backend-services get-health "$BACKEND_SERVICE" --global >/dev/null 2>&1; then
    gcloud compute backend-services add-backend "$BACKEND_SERVICE" \
        --global \
        --network-endpoint-group="$NEG_NAME" \
        --network-endpoint-group-region="$REGION" || true
fi

# 6. Create URL Map
echo "[8] Creating URL Map..."
if ! gcloud compute url-maps describe "$URL_MAP" >/dev/null 2>&1; then
    gcloud compute url-maps create "$URL_MAP" \
        --default-service "$BACKEND_SERVICE"
fi

# 7. Create Self-Signed SSL Certificate for HTTPS (for immediate testing without a domain)
echo "[9] Generating Temporary Self-Signed SSL Certificate..."
if ! gcloud compute ssl-certificates describe "$CERT_NAME" --global >/dev/null 2>&1; then
    mkdir -p .tmp-testing
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout .tmp-testing/tls.key -out .tmp-testing/tls.crt \
        -subj "/CN=$IP_ADDRESS.nip.io"
    
    gcloud compute ssl-certificates create "$CERT_NAME" \
        --certificate=.tmp-testing/tls.crt \
        --private-key=.tmp-testing/tls.key \
        --global
fi

# 8. Create HTTPS Target Proxy
echo "[10] Creating Target HTTPS Proxy..."
if ! gcloud compute target-https-proxies describe "$HTTPS_PROXY" >/dev/null 2>&1; then
    gcloud compute target-https-proxies create "$HTTPS_PROXY" \
        --ssl-certificates="$CERT_NAME" \
        --url-map="$URL_MAP"
fi

# 9. Create Global Forwarding Rule for HTTPS
echo "[11] Creating Forwarding Rule..."
if ! gcloud compute forwarding-rules describe "$HTTPS_FORWARDING_RULE" --global >/dev/null 2>&1; then
    gcloud compute forwarding-rules create "$HTTPS_FORWARDING_RULE" \
        --address="$IP_ADDRESS_NAME" \
        --target-https-proxy="$HTTPS_PROXY" \
        --global \
        --ports=443
fi

# 10. Enable IAP on Backend Service
echo "[12] Configuring Identity-Aware Proxy (IAP)..."

# Ensure the OAuth Credentials are provided
if [ -z "$OAUTH_CLIENT_ID" ] || [ -z "$OAUTH_CLIENT_SECRET" ]; then
    echo "WARNING: OAUTH_CLIENT_ID and OAUTH_CLIENT_SECRET are not set."
    echo "IAP was NOT enabled. Please set these variables and run this script again."
    echo "Or run manually: gcloud compute backend-services update $BACKEND_SERVICE --global --iap=enabled,oauth2-client-id=\$OAUTH_CLIENT_ID,oauth2-client-secret=\$OAUTH_CLIENT_SECRET"
else
    echo "Enabling IAP on backend service..."
    gcloud compute backend-services update "$BACKEND_SERVICE" \
        --global \
        --iap=enabled,oauth2-client-id="$OAUTH_CLIENT_ID",oauth2-client-secret="$OAUTH_CLIENT_SECRET"
        
    echo "[13] Granting access to $ALLOWED_EMAIL..."
    gcloud iap web add-iam-policy-binding \
        --resource-type=backend-services \
        --service="$BACKEND_SERVICE" \
        --member="user:$ALLOWED_EMAIL" \
        --role="roles/iap.httpsResourceAccessor"
fi

echo "==================================================================="
echo "Deployment Complete!"
echo "Global Tax Intelligence is deploying behind a Global Load Balancer."
echo "Access URL: https://$IP_ADDRESS.nip.io"
echo "(Note: You may see an SSL warning if using a self-signed certificate, which is expected. In a production environment, you should buy a domain name and create a Google Managed SSL Certificate.)"
echo "If IAP is enabled, only $ALLOWED_EMAIL can access it."
echo "It may take up to 10-15 minutes for the Load Balancer and IAP to fully propagate."
echo "==================================================================="
