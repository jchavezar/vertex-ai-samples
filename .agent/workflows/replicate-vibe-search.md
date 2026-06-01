---
description: Replicate the Shutter Vibe Engine premium frontend and serverless cloud ingestion pipeline on GCP
---
# Replicating the Multimodal Vibe Search Application

This workflow outlines the automated, sequential, and parallel steps to clone the Shutter Vibe Engine, provision cloud resources, build containers, and deploy the entire serverless ingestion pipeline on Google Cloud.

To start this deployment, follow the phases below.

---

## 1. Workspace Bootstrapping (Self-Copy)
Populate the empty target workspace with the pre-packaged application files to structure the repository correctly.

// turbo
```bash
mkdir -p multimodal-search/app/templates multimodal-search/app/static multimodal-search/pipeline demos multimodal-search/backends
cp -r antigravity/src/app/* multimodal-search/app/
cp -r antigravity/src/templates/* multimodal-search/app/templates/
cp -r antigravity/src/static/* multimodal-search/app/static/
cp -r antigravity/src/pipeline/* multimodal-search/pipeline/
cp -r antigravity/src/demos/* demos/
cp -r antigravity/src/backends/* multimodal-search/backends/
```

---

## 2. Interactive Parameter Configuration
The agent will prompt you for the following environment parameters and write them to a local `.env` file in the root directory:

*   **GOOGLE_CLOUD_PROJECT**: Your target Google Cloud Project ID.
*   **GOOGLE_CLOUD_LOCATION**: The target deployment region (e.g., `us-central1`).
*   **ENVATO_GCS_BUCKET**: The Cloud Storage bucket name (e.g., `your-project-vibe-engine-data`).
*   **ENVATO_SA_NAME**: The name of the Service Account (e.g., `envato-vibe-runner`).
*   **SEARCH_BACKEND**: The database backend (`vector-search` or `bigquery`).

If running manually, execute this command block to create a default `.env` file:

// turbo
```bash
cat <<EOF > .env
GOOGLE_CLOUD_PROJECT=\$(gcloud config get-value project 2>/dev/null || echo "your-project-id")
GOOGLE_CLOUD_LOCATION=us-central1
ENVATO_GCS_BUCKET=\$(gcloud config get-value project 2>/dev/null || echo "your-project-id")-vibe-engine-data
ENVATO_SA_NAME=envato-vibe-runner
SEARCH_BACKEND=vector-search
EOF
echo ".env file generated successfully. Please verify its values."
```

---

## 3. Enable Google Cloud APIs
Enable all required APIs on Google Cloud in a single, parallelized operations call.

// turbo
```bash
set -a; [ -f .env ] && . .env; set +a
gcloud config set project "\$GOOGLE_CLOUD_PROJECT"
gcloud services enable \\
  run.googleapis.com \
  eventarc.googleapis.com \
  firestore.googleapis.com \
  aiplatform.googleapis.com \
  cloudbuild.googleapis.com \
  --quiet
```

---

## 4. Provision Service Account & Bind IAM Roles
Create the runner service account and bind the required permissions for AI Platform, Cloud Storage, Datastore, Eventarc, and Pub/Sub.

// turbo
```bash
set -a; [ -f .env ] && . .env; set +a
SA_EMAIL="\${ENVATO_SA_NAME}@\${GOOGLE_CLOUD_PROJECT}.iam.gserviceaccount.com"

# Create service account if not exists
if ! gcloud iam service-accounts describe "\$SA_EMAIL" --project="\$GOOGLE_CLOUD_PROJECT" >/dev/null 2>&1; then
  gcloud iam service-accounts create "\$ENVATO_SA_NAME" \
    --display-name="Shutter Vibe Runner" \
    --project="\$GOOGLE_CLOUD_PROJECT" \
    --quiet
fi

# Bind Roles
ROLES=(
  "roles/aiplatform.user"
  "roles/storage.objectAdmin"
  "roles/datastore.user"
  "roles/run.invoker"
  "roles/pubsub.publisher"
  "roles/eventarc.eventReceiver"
)

for role in "\${ROLES[@]}"; do
  gcloud projects add-iam-policy-binding "\$GOOGLE_CLOUD_PROJECT" \
    --member="serviceAccount:\${SA_EMAIL}" \
    --role="\$role" \
    --quiet >/dev/null
done

# Authorize GCS system service agent for Eventarc triggers
PROJECT_NUM=\$(gcloud projects describe "\$GOOGLE_CLOUD_PROJECT" --format="value(projectNumber)")
GCS_AGENT="service-\${PROJECT_NUM}@gs-project-accounts.iam.gserviceaccount.com"
gcloud projects add-iam-policy-binding "\$GOOGLE_CLOUD_PROJECT" \
  --member="serviceAccount:\${GCS_AGENT}" \
  --role="roles/pubsub.publisher" \
  --quiet >/dev/null
```

---

## 5. Create Cloud Storage Schema
Provision the GCS Bucket (if it doesn't exist) and initialize the folder structure schema (`ingest/`, `originals/`, `thumbnails/`, `segments/`).

// turbo
```bash
set -a; [ -f .env ] && . .env; set +a

# Create Bucket if not exists
if ! gcloud storage buckets describe "gs://\${ENVATO_GCS_BUCKET}" --project="\$GOOGLE_CLOUD_PROJECT" >/dev/null 2>&1; then
  gcloud storage buckets create "gs://\${ENVATO_GCS_BUCKET}" \
    --location="\$GOOGLE_CLOUD_LOCATION" \
    --project="\$GOOGLE_CLOUD_PROJECT" \
    --quiet
fi

# Generate folder structure schema
echo -n "" > /tmp/vibe_placeholder
gcloud storage cp /tmp/vibe_placeholder "gs://\${ENVATO_GCS_BUCKET}/ingest/.placeholder" --quiet
gcloud storage cp /tmp/vibe_placeholder "gs://\${ENVATO_GCS_BUCKET}/originals/.placeholder" --quiet
gcloud storage cp /tmp/vibe_placeholder "gs://\${ENVATO_GCS_BUCKET}/thumbnails/.placeholder" --quiet
gcloud storage cp /tmp/vibe_placeholder "gs://\${ENVATO_GCS_BUCKET}/segments/.placeholder" --quiet
rm /tmp/vibe_placeholder
```

---

## 6. Compile & Build App Server Container
Build and push the main FastAPI web application image to GCR via Cloud Build using the static `cloudbuild.app.yaml` config.

// turbo
```bash
set -a; [ -f .env ] && . .env; set +a
cp antigravity/deploy/.gcloudignore.app .gcloudignore
gcloud builds submit . --project="\$GOOGLE_CLOUD_PROJECT" --config="antigravity/deploy/cloudbuild.app.yaml"
rm -f .gcloudignore
```

---

## 7. Deploy App Server to Cloud Run
Deploy the main FastAPI frontend web application service to Cloud Run.

// turbo
```bash
set -a; [ -f .env ] && . .env; set +a
SA_EMAIL="\${ENVATO_SA_NAME}@\${GOOGLE_CLOUD_PROJECT}.iam.gserviceaccount.com"

gcloud run deploy envato-vibe-app \
  --image="gcr.io/\${GOOGLE_CLOUD_PROJECT}/envato-vibe-app:latest" \
  --region="\$GOOGLE_CLOUD_LOCATION" \
  --project="\$GOOGLE_CLOUD_PROJECT" \
  --service-account="\$SA_EMAIL" \
  --memory="2Gi" --cpu="2" --timeout="600" \
  --allow-unauthenticated \
  --set-env-vars="GOOGLE_GENAI_USE_VERTEXAI=True,GOOGLE_CLOUD_PROJECT=\${GOOGLE_CLOUD_PROJECT},GOOGLE_CLOUD_LOCATION=\${GOOGLE_CLOUD_LOCATION},ENVATO_GCS_BUCKET=\${ENVATO_GCS_BUCKET},SEARCH_BACKEND=\${SEARCH_BACKEND}"
```

---

## 8. Compile & Build Ingest Worker Container
Build and push the event-driven ingest worker image to GCR via Cloud Build using the static `cloudbuild.ingest.yaml` config.

// turbo
```bash
set -a; [ -f .env ] && . .env; set +a
cp antigravity/deploy/.gcloudignore.ingest .gcloudignore
gcloud builds submit . --project="\$GOOGLE_CLOUD_PROJECT" --config="antigravity/deploy/cloudbuild.ingest.yaml"
rm -f .gcloudignore
```

---

## 9. Deploy Ingest Worker to Cloud Run & Setup Trigger
Deploy the ingest worker service to Cloud Run and configure Eventarc to trigger it automatically when new files are finalized in the GCS bucket.

// turbo
```bash
set -a; [ -f .env ] && . .env; set +a
SA_EMAIL="\${ENVATO_SA_NAME}@\${GOOGLE_CLOUD_PROJECT}.iam.gserviceaccount.com"

# Deploy service
gcloud run deploy envato-vibe-ingest \
  --image="gcr.io/\${GOOGLE_CLOUD_PROJECT}/envato-vibe-ingest:latest" \
  --region="\$GOOGLE_CLOUD_LOCATION" \
  --project="\$GOOGLE_CLOUD_PROJECT" \
  --service-account="\$SA_EMAIL" \
  --memory="2Gi" --cpu="2" --timeout="600" \
  --no-allow-unauthenticated \
  --set-env-vars="GOOGLE_CLOUD_PROJECT=\${GOOGLE_CLOUD_PROJECT},GOOGLE_CLOUD_LOCATION=\${GOOGLE_CLOUD_LOCATION},ENVATO_GCS_BUCKET=\${ENVATO_GCS_BUCKET},GOOGLE_GENAI_USE_VERTEXAI=True"

# Configure Eventarc GCS Trigger
TRIGGER_NAME="envato-vibe-ingest-trigger"
if gcloud eventarc triggers describe "\$TRIGGER_NAME" --location="\$GOOGLE_CLOUD_LOCATION" --project="\$GOOGLE_CLOUD_PROJECT" >/dev/null 2>&1; then
  gcloud eventarc triggers update "\$TRIGGER_NAME" \
    --location="\$GOOGLE_CLOUD_LOCATION" --project="\$GOOGLE_CLOUD_PROJECT" \
    --destination-run-service="envato-vibe-ingest" \
    --destination-run-region="\$GOOGLE_CLOUD_LOCATION" \
    --service-account="\$SA_EMAIL"
else
  gcloud eventarc triggers create "\$TRIGGER_NAME" \
    --location="\$GOOGLE_CLOUD_LOCATION" --project="\$GOOGLE_CLOUD_PROJECT" \
    --destination-run-service="envato-vibe-ingest" \
    --destination-run-region="\$GOOGLE_CLOUD_LOCATION" \
    --event-filters="type=google.cloud.storage.object.v1.finalized" \
    --event-filters="bucket=\${ENVATO_GCS_BUCKET}" \
    --service-account="\$SA_EMAIL"
fi
```

---

## 10. UI Replication & Integrity Verification
Execute local verification checks to validate files are structured perfectly.

// turbo
```bash
python antigravity/verify_replication.py
```

---

## 11. Print App URL & Log Monitoring
Query and print the deployed Web Service URL and show logs.

// turbo
```bash
set -a; [ -f .env ] && . .env; set +a
URL=\$(gcloud run services describe envato-vibe-app --region="\$GOOGLE_CLOUD_LOCATION" --project="\$GOOGLE_CLOUD_PROJECT" --format="value(status.url)")
echo "=========================================================="
echo " [SUCCESS] Replication and Deployment Complete!"
echo "----------------------------------------------------------"
echo "  -> Web Frontend URL:  \$URL"
echo "  -> Cloud Storage:     gs://\${ENVATO_GCS_BUCKET}/"
echo "  -> Direct Ingest URL: gs://\${ENVATO_GCS_BUCKET}/ingest/"
echo "=========================================================="
```
