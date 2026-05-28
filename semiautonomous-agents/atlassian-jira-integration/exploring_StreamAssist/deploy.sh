#!/usr/bin/env bash
# Deploy to Cloud Run in vtxdemos. Reuses the runtime SA from option-f-adk-rovo-wrapper.
set -euo pipefail

PROJECT=vtxdemos
REGION=us-central1
SERVICE=exploring-streamassist
SA=254356041555-compute@developer.gserviceaccount.com

cd "$(dirname "$0")"

# ---- OAuth client ID (Option 2 end-user OAuth) ----
# The OAuth Web Application client must be created manually in the GCP
# console first (see README "Manual setup needed"). Save its client_id to
# .oauth_client_id (one line, gitignored). If missing we still deploy in
# SA-only mode but the Sign-In button will show "OAuth client not found".
OAUTH_CLIENT_ID=""
if [[ -f .oauth_client_id ]]; then
  OAUTH_CLIENT_ID=$(tr -d '\n\r \t' < .oauth_client_id)
fi

if [[ -z "$OAUTH_CLIENT_ID" ]]; then
  echo "WARN: .oauth_client_id is missing or empty."
  echo "      Deploying in service-account-only mode. End-user sign-in will not work."
  echo "      Create an OAuth Web client in vtxdemos (see README) and run:"
  echo "        echo 'YOUR_CLIENT_ID' > .oauth_client_id && bash deploy.sh"
else
  echo "Using OAUTH_CLIENT_ID=${OAUTH_CLIENT_ID:0:24}…"
fi

# ---- Session signing secret (stable across revisions) ----
# We keep this stable so sessions survive redeploys. Persisted alongside
# the OAuth client id, also gitignored. Auto-generated on first deploy.
if [[ ! -f .session_secret ]]; then
  python3 -c "import secrets,sys; sys.stdout.write(secrets.token_urlsafe(48))" > .session_secret
  echo "Generated .session_secret (gitignored)"
fi
SESSION_SECRET=$(tr -d '\n\r \t' < .session_secret)

ENV_VARS="ENGINE_RESOURCE=projects/254356041555/locations/global/collections/default_collection/engines/jira-testing_1778158449701"
ENV_VARS+=",GE_USER_PROJECT=vtxdemos"
ENV_VARS+=",SESSION_SECRET=${SESSION_SECRET}"
if [[ -n "$OAUTH_CLIENT_ID" ]]; then
  ENV_VARS+=",OAUTH_CLIENT_ID=${OAUTH_CLIENT_ID}"
fi

gcloud --billing-project=vtxdemos run deploy "$SERVICE" \
  --source . \
  --region "$REGION" \
  --project "$PROJECT" \
  --allow-unauthenticated \
  --service-account "$SA" \
  --memory 1Gi \
  --cpu 1 \
  --timeout 600 \
  --set-env-vars "$ENV_VARS"
