# Replicating & Deploying the Vector Search Playground Lab

This guide outlines how to compile and deploy the dedicated **Vertex AI Vector Search Lab Playground** as a standalone, isolated Cloud Run service (`envato-vibe-playground`), distinct from your main app.

---

## 1. Interactive Configuration Sourcing

The playground uses your existing Firestore database `(default)` and your streaming vector index `vs-canvas-tree-ah`.

Make sure your local `.env` file in the root directory is fully configured with the following:

```env
GOOGLE_CLOUD_PROJECT=vtxdemos
GOOGLE_CLOUD_LOCATION=us-central1
ENVATO_GCS_BUCKET=vtxdemos-multimodal-vibe-search-data
ENVATO_SA_NAME=envato-vibe-runner
SEARCH_BACKEND=vector-search
INDEX_DISPLAY_NAME=vs-canvas-tree-ah
ENDPOINT_DISPLAY_NAME=vs-canvas-endpoint
DEPLOYED_INDEX_ID=vs_canvas_tree_ah
FIRESTORE_DATABASE_ID="(default)"
FIRESTORE_SEGMENTS_COLLECTION=segments_dev
FIRESTORE_UPLOADS_COLLECTION=uploads_dev
ENV_RESTRICTION=dev
```

---

## 2. Compile & Build the App Container

We build a single, unified application container image. The runtime behavior is toggled entirely by environment variables, allowing us to deploy the same container as both the production search frontend and the educational playground.

Run the Cloud Build compilation:

```bash
set -a; [ -f .env ] && . .env; set +a
cp antigravity/deploy/.gcloudignore.app .gcloudignore
gcloud builds submit . --project="$GOOGLE_CLOUD_PROJECT" --config="antigravity/deploy/cloudbuild.app.yaml"
rm -f .gcloudignore
```

---

## 3. Deploy Dedicated Cloud Run Playground Resource

Deploy the new, dedicated Cloud Run service named **`envato-vibe-playground`**. 

Notice that we pass the **`PLAYGROUND_ONLY=True`** environment variable to force this service instance to mount the interactive playground at the root `/` URL:

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

## 4. Extract Playground URL

Retrieve the newly deployed playground service URL:

```bash
set -a; [ -f .env ] && . .env; set +a
URL=$(gcloud run services describe envato-vibe-playground --region="$GOOGLE_CLOUD_LOCATION" --project="$GOOGLE_CLOUD_PROJECT" --format="value(status.url)")
echo "=========================================================="
echo " [SUCCESS] Vector Search Lab Playground Deployed!"
echo "----------------------------------------------------------"
echo "  -> Interactive Lab URL:  $URL"
echo "=========================================================="
```
