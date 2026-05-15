#!/usr/bin/env bash
# Enable every API the demo needs. Idempotent — safe to re-run.
set -euo pipefail

source "$(dirname "$0")/../.env"
: "${GOOGLE_CLOUD_PROJECT:?set in .env}"

echo "[infra/00] enabling APIs in ${GOOGLE_CLOUD_PROJECT}…"

gcloud services enable aiplatform.googleapis.com agentregistry.googleapis.com networkservices.googleapis.com iap.googleapis.com modelarmor.googleapis.com compute.googleapis.com run.googleapis.com artifactregistry.googleapis.com cloudbuild.googleapis.com iam.googleapis.com iamconnectors.googleapis.com --project="${GOOGLE_CLOUD_PROJECT}"

echo "[infra/00] done."
