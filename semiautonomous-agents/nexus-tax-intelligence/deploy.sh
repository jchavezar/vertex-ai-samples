#!/bin/bash
set -euo pipefail

PROJECT_ID="${GOOGLE_CLOUD_PROJECT:-$(gcloud config get-value project)}"
REGION="${REGION:-us-central1}"
SERVICE_NAME="pwc-tax-intelligence-service"
NEG_NAME="pwc-tax-intelligence-serverless-neg"
BACKEND_NAME="pwc-tax-intelligence-backend"
URL_MAP="global-tax-intel-url-map"

echo "=== Building & Deploying ${SERVICE_NAME} ==="

# 1. Deploy to Cloud Run via source
echo "[1/4] Deploying to Cloud Run..."
gcloud run deploy "${SERVICE_NAME}" \
  --source . \
  --region "${REGION}" \
  --platform managed \
  --allow-unauthenticated \
  --ingress internal-and-cloud-load-balancing \
  --memory 512Mi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 10 \
  --set-env-vars "GOOGLE_CLOUD_PROJECT=${PROJECT_ID},PROJECT_ID=${PROJECT_ID},VAIS_PROJECT_ID=${PROJECT_ID}" \
  --project "${PROJECT_ID}" \
  --quiet

# 2. Create serverless NEG (skip if exists)
echo "[2/4] Creating Serverless NEG..."
if ! gcloud compute network-endpoint-groups describe "${NEG_NAME}" --region="${REGION}" --project="${PROJECT_ID}" &>/dev/null; then
  gcloud compute network-endpoint-groups create "${NEG_NAME}" \
    --region="${REGION}" \
    --network-endpoint-type=serverless \
    --cloud-run-service="${SERVICE_NAME}" \
    --project="${PROJECT_ID}"
  echo "  Created NEG: ${NEG_NAME}"
else
  echo "  NEG already exists: ${NEG_NAME}"
fi

# 3. Create backend service (skip if exists)
echo "[3/4] Creating Backend Service..."
if ! gcloud compute backend-services describe "${BACKEND_NAME}" --global --project="${PROJECT_ID}" &>/dev/null; then
  gcloud compute backend-services create "${BACKEND_NAME}" \
    --global \
    --load-balancing-scheme=EXTERNAL \
    --project="${PROJECT_ID}"

  gcloud compute backend-services add-backend "${BACKEND_NAME}" \
    --global \
    --network-endpoint-group="${NEG_NAME}" \
    --network-endpoint-group-region="${REGION}" \
    --project="${PROJECT_ID}"
  echo "  Created backend: ${BACKEND_NAME}"
else
  echo "  Backend already exists: ${BACKEND_NAME}"
fi

# 4. Add /pwc path rule to the existing URL map
echo "[4/4] Adding /pwc path to URL map: ${URL_MAP}..."

# Export current URL map, add pwc path rule, and import
TEMP_FILE=$(mktemp /tmp/url-map-XXXXXX.yaml)
gcloud compute url-maps export "${URL_MAP}" \
  --global \
  --destination="${TEMP_FILE}" \
  --project="${PROJECT_ID}"

# Check if /pwc already exists
if grep -q "/pwc" "${TEMP_FILE}"; then
  echo "  /pwc path rule already exists in URL map"
else
  # Add the pwc path rule to the existing path matcher
  python3 -c "
import yaml, sys

with open('${TEMP_FILE}', 'r') as f:
    config = yaml.safe_load(f)

for pm in config.get('pathMatchers', []):
    rules = pm.get('pathRules', [])
    rules.append({
        'paths': ['/pwc', '/pwc/*'],
        'service': 'projects/${PROJECT_ID}/global/backendServices/${BACKEND_NAME}'
    })
    pm['pathRules'] = rules
    break

with open('${TEMP_FILE}', 'w') as f:
    yaml.dump(config, f, default_flow_style=False)
"

  gcloud compute url-maps import "${URL_MAP}" \
    --global \
    --source="${TEMP_FILE}" \
    --project="${PROJECT_ID}" \
    --quiet

  echo "  Added /pwc path rule to ${URL_MAP}"
fi

rm -f "${TEMP_FILE}"

echo ""
echo "=== Deployment Complete ==="
echo "URL: https://tax.sonrobots.net/pwc/"
