#!/bin/bash
# Teardown script for Shutter Vibe Engine replication resources.
# WARNING: This will delete the Cloud Run services, the GCS bucket,
# the service account, and all bootstrapped local files.

set -e

# Sourcing parameters
if [ -f .env ]; then
  source ./.env
else
  echo "[ERROR] .env file not found. Cannot proceed with automatic teardown."
  exit 1
fi

echo "=========================================================="
echo " Starting Teardown & Cleanup of Shutter Vibe Engine"
echo "=========================================================="

SA_EMAIL="${ENVATO_SA_NAME}@${GOOGLE_CLOUD_PROJECT}.iam.gserviceaccount.com"

# 1. Delete Eventarc GCS trigger
echo "[1/6] Deleting Eventarc trigger..."
gcloud eventarc triggers delete envato-vibe-ingest-trigger \
  --location="$GOOGLE_CLOUD_LOCATION" \
  --project="$GOOGLE_CLOUD_PROJECT" \
  --quiet || true

# 2. Delete Cloud Run services
echo "[2/6] Deleting Cloud Run services..."
gcloud run services delete envato-vibe-app \
  --region="$GOOGLE_CLOUD_LOCATION" \
  --project="$GOOGLE_CLOUD_PROJECT" \
  --quiet || true

gcloud run services delete envato-vibe-ingest \
  --region="$GOOGLE_CLOUD_LOCATION" \
  --project="$GOOGLE_CLOUD_PROJECT" \
  --quiet || true

# 3. Delete GCS bucket (removes all files recursively)
echo "[3/6] Deleting Cloud Storage bucket gs://${ENVATO_GCS_BUCKET}..."
gcloud storage rm -r "gs://${ENVATO_GCS_BUCKET}" --quiet || true

# 4. Remove IAM Role bindings
echo "[4/6] Removing IAM role bindings..."
ROLES=(
  "roles/aiplatform.user"
  "roles/storage.objectAdmin"
  "roles/datastore.user"
  "roles/run.invoker"
  "roles/pubsub.publisher"
  "roles/eventarc.eventReceiver"
  "roles/bigquery.dataViewer"
  "roles/bigquery.jobUser"
)

for role in "${ROLES[@]}"; do
  gcloud projects remove-iam-policy-binding "$GOOGLE_CLOUD_PROJECT" \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="$role" \
    --condition=None \
    --quiet >/dev/null 2>&1 || true
done

# 5. Delete Service Account
echo "[5/6] Deleting Service Account ${SA_EMAIL}..."
gcloud iam service-accounts delete "$SA_EMAIL" \
  --project="$GOOGLE_CLOUD_PROJECT" \
  --quiet || true

# 6. Delete local bootstrapped folders
echo "[6/6] Cleaning local folders..."
rm -rf multimodal-search
rm -rf demos
rm -rf .env
rm -rf .gitignore

echo "=========================================================="
echo " [SUCCESS] Teardown & Cleanup Complete!"
echo "=========================================================="
