#!/bin/bash
set -e

# Configuration
PROJECT_ID="vtxdemos"
REGION="us-central1"
SERVICE_NAME="vibes-nyc"
IMAGE_TAG="gcr.io/$PROJECT_ID/$SERVICE_NAME:latest"
REPO_NAME="vibes-nyc"
DOMAIN="dino-vibes.sonrobots.net"

echo "🚀 Starting Production Deployment for $SERVICE_NAME..."

# 1. Ensure Artifact Registry exists
# (already exists)

FULL_IMAGE="$REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/$SERVICE_NAME"

# 2. Build and Push Docker Image using Cloud Build
# echo "Building and pushing Docker image with Cloud Build..."
gcloud builds submit --tag $FULL_IMAGE .

# 3. Deploy to Cloud Run
echo "Deploying to Cloud Run..."
# Extract key from .env
PLACES_KEY=$(grep GOOGLE_PLACES_API_KEY .env | cut -d'=' -f2)
gcloud run deploy $SERVICE_NAME \
  --image $FULL_IMAGE \
  --region $REGION \
  --platform managed \
  --no-allow-unauthenticated \
  --ingress internal-and-cloud-load-balancing \
  --set-env-vars="PROJECT_ID=$PROJECT_ID,GOOGLE_CLOUD_PROJECT=$PROJECT_ID,GOOGLE_PLACES_API_KEY=$PLACES_KEY" \
  --quiet

# 4. Global Load Balancer & SSL
IP_NAME="$SERVICE_NAME-ip"
if ! gcloud compute addresses describe $IP_NAME --global &>/dev/null; then
  echo "Reserving static IP address..."
  gcloud compute addresses create $IP_NAME --global
fi
STATIC_IP=$(gcloud compute addresses describe $IP_NAME --global --format="value(address)")
echo "✅ Static IP Reserved: $STATIC_IP"

# Managed SSL Certificate
CERT_NAME="dino-vibes-cert"
if ! gcloud compute ssl-certificates describe $CERT_NAME --global &>/dev/null; then
  echo "Creating Managed SSL Certificate for $DOMAIN..."
  gcloud compute ssl-certificates create $CERT_NAME \
    --domains=$DOMAIN \
    --global
fi

# Create Serverless NEG
NEG_NAME="$SERVICE_NAME-neg"
if ! gcloud compute network-endpoint-groups describe $NEG_NAME --region=$REGION &>/dev/null; then
  gcloud compute network-endpoint-groups create $NEG_NAME \
    --region=$REGION \
    --network-endpoint-type=serverless \
    --cloud-run-service=$SERVICE_NAME
fi

# Backend Service
BACKEND_NAME="$SERVICE_NAME-backend"
if ! gcloud compute backend-services describe $BACKEND_NAME --global &>/dev/null; then
  gcloud compute backend-services create $BACKEND_NAME --global --load-balancing-scheme=EXTERNAL
  gcloud compute backend-services add-backend $BACKEND_NAME \
    --global \
    --network-endpoint-group=$NEG_NAME \
    --network-endpoint-group-region=$REGION
fi

# URL Map
URL_MAP_NAME="$SERVICE_NAME-url-map"
if ! gcloud compute url-maps describe $URL_MAP_NAME --global &>/dev/null; then
  gcloud compute url-maps create $URL_MAP_NAME --default-service $BACKEND_NAME
fi

# Target HTTPS Proxy
PROXY_NAME="$SERVICE_NAME-https-proxy"
if ! gcloud compute target-https-proxies describe $PROXY_NAME --global &>/dev/null; then
  gcloud compute target-https-proxies create $PROXY_NAME \
    --url-map=$URL_MAP_NAME \
    --ssl-certificates=$CERT_NAME
else
  # Update existing proxy to use the new cert
  echo "Updating HTTPS proxy with new certificate..."
  gcloud compute target-https-proxies update $PROXY_NAME \
    --ssl-certificates=$CERT_NAME
fi

# Forwarding Rule (HTTPS)
FORWARDING_RULE_NAME="$SERVICE_NAME-forwarding-rule"
if ! gcloud compute forwarding-rules describe $FORWARDING_RULE_NAME --global &>/dev/null; then
  gcloud compute forwarding-rules create $FORWARDING_RULE_NAME \
    --address=$IP_NAME \
    --global \
    --target-https-proxy=$PROXY_NAME \
    --ports=443
fi

# --- HTTP to HTTPS Redirect ---

# 1. Redirect URL Map
REDIRECT_MAP_NAME="$SERVICE_NAME-redirect-map"
if ! gcloud compute url-maps describe $REDIRECT_MAP_NAME --global &>/dev/null; then
  echo "Creating HTTP to HTTPS redirect URL map..."
  # Create a temporary file for the redirect config
  cat <<EOF > redirect.yaml
name: $REDIRECT_MAP_NAME
defaultUrlRedirect:
  redirectResponseCode: MOVED_PERMANENTLY_DEFAULT
  httpsRedirect: true
EOF
  gcloud compute url-maps import $REDIRECT_MAP_NAME --source=redirect.yaml --global --quiet
  rm redirect.yaml
fi

# 2. Target HTTP Proxy
HTTP_PROXY_NAME="$SERVICE_NAME-http-proxy"
if ! gcloud compute target-http-proxies describe $HTTP_PROXY_NAME --global &>/dev/null; then
  gcloud compute target-http-proxies create $HTTP_PROXY_NAME --url-map=$REDIRECT_MAP_NAME
fi

# 3. Forwarding Rule (HTTP Port 80)
HTTP_FORWARDING_RULE_NAME="$SERVICE_NAME-http-forwarding-rule"
if ! gcloud compute forwarding-rules describe $HTTP_FORWARDING_RULE_NAME --global &>/dev/null; then
  gcloud compute forwarding-rules create $HTTP_FORWARDING_RULE_NAME \
    --address=$IP_NAME \
    --global \
    --target-http-proxy=$HTTP_PROXY_NAME \
    --ports=80
fi

# 5. Enable IAP
echo "Configuring Identity-Aware Proxy..."
gcloud iap web enable --resource-type=backend-services --service=$BACKEND_NAME

# Grant access to current user
USER_EMAIL=$(gcloud config get-value account)
gcloud iap web add-iam-policy-binding \
    --resource-type=backend-services \
    --service=$BACKEND_NAME \
    --member="user:$USER_EMAIL" \
    --role="roles/iap.httpsResourceAccessor"

echo "🎉 Deployment complete!"
echo "📍 IP Address for Cloudflare: $STATIC_IP"
echo "⚠️  Please configure your Cloudflare CNAME/A record for $DOMAIN to $STATIC_IP"
echo "⚠️  SSL certificates may take up to 24 hours to provision after DNS is updated."
