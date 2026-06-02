---
description: Provision the standalone educational Vertex Vector Search Interactive Playground on Google Cloud
---
# Setting Up the Vector Search Lab Playground

This workflow compiles the unified app server container and deploys it as a dedicated Cloud Run service (`envato-vibe-playground`) running with `PLAYGROUND_ONLY=True` to provide an isolated, interactive learning console.

---

## 1. Copy Files to Replication Workspace
First, copy the updated app source files and template assets to the active replication directory.

// turbo
```bash
mkdir -p multimodal-search/app/templates multimodal-search/deploy
cp antigravity/src/app/main.py multimodal-search/app/
cp antigravity/src/app/templates/playground.html multimodal-search/app/templates/
cp antigravity/deploy/cloudbuild.app.yaml multimodal-search/deploy/
cp antigravity/deploy/.gcloudignore.app multimodal-search/deploy/
```

---

## 2. Build & Push App Image
Build the unified app server container using Google Cloud Build.

// turbo
```bash
set -a; [ -f .env ] && . .env; set +a
cp multimodal-search/deploy/.gcloudignore.app .gcloudignore
gcloud builds submit . --project="$GOOGLE_CLOUD_PROJECT" --config="multimodal-search/deploy/cloudbuild.app.yaml"
rm -f .gcloudignore
```

---

## 3. Deploy Playground Service to Cloud Run
Deploy the playground service with the educational environment variables.

// turbo
```bash
set -a; [ -f .env ] && . .env; set +a
SA_EMAIL="${ENVATO_SA_NAME}@${GOOGLE_CLOUD_PROJECT}.iam.gserviceaccount.com"

gcloud run deploy envato-vibe-playground \
  --image="gcr.io/${GOOGLE_CLOUD_PROJECT}/envato-vibe-app:latest" \
  --region="$GOOGLE_CLOUD_LOCATION" \
  --project="$GOOGLE_CLOUD_PROJECT" \
  --service-account="$SA_EMAIL" \
  --memory="2Gi" --cpu="2" --timeout="600" \
  --allow-unauthenticated \
  --ingress=all \
  --set-env-vars="GOOGLE_GENAI_USE_VERTEXAI=True,PLAYGROUND_ONLY=True,GOOGLE_CLOUD_PROJECT=${GOOGLE_CLOUD_PROJECT},GOOGLE_CLOUD_LOCATION=${GOOGLE_CLOUD_LOCATION},ENVATO_GCS_BUCKET=${ENVATO_GCS_BUCKET},SEARCH_BACKEND=${SEARCH_BACKEND},INDEX_DISPLAY_NAME=${INDEX_DISPLAY_NAME:-vs-canvas-tree-ah},ENDPOINT_DISPLAY_NAME=${ENDPOINT_DISPLAY_NAME:-vs-canvas-endpoint},DEPLOYED_INDEX_ID=${DEPLOYED_INDEX_ID:-vs_canvas_tree_ah},FIRESTORE_DATABASE_ID=${FIRESTORE_DATABASE_ID:-(default)},FIRESTORE_SEGMENTS_COLLECTION=${FIRESTORE_SEGMENTS_COLLECTION:-segments_dev},FIRESTORE_UPLOADS_COLLECTION=${FIRESTORE_UPLOADS_COLLECTION:-uploads_dev},ENV_RESTRICTION=${ENV_RESTRICTION:-dev}"
```

---

## 4. Verify Playground Deployment URL
Fetch the service endpoint and print the confirmation banner.

// turbo
```bash
set -a; [ -f .env ] && . .env; set +a
URL=$(gcloud run services describe envato-vibe-playground --region="$GOOGLE_CLOUD_LOCATION" --project="$GOOGLE_CLOUD_PROJECT" --format="value(status.url)")
echo "=========================================================="
echo " [SUCCESS] Replicated Vector Search Playground Lab is Live!"
echo "----------------------------------------------------------"
echo "  -> URL: $URL"
echo "=========================================================="
```
