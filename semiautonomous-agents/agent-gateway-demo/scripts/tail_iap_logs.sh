#!/usr/bin/env bash
# Live-tail IAP audit logs while you exercise the agent.
set -euo pipefail
source "$(dirname "$0")/../.env"
: "${GOOGLE_CLOUD_PROJECT:?}"

# `gcloud logging tail` requires the alpha component; fall back to a polled read.
if gcloud alpha logging tail --help >/dev/null 2>&1; then
  gcloud alpha logging tail "logName=\"projects/${GOOGLE_CLOUD_PROJECT}/logs/cloudaudit.googleapis.com%2Fdata_access\" AND protoPayload.serviceName=\"iap.googleapis.com\"" --project="${GOOGLE_CLOUD_PROJECT}"
else
  echo "[note] gcloud alpha logging tail unavailable — polling every 5s"
  while sleep 5; do
    gcloud logging read "logName=\"projects/${GOOGLE_CLOUD_PROJECT}/logs/cloudaudit.googleapis.com%2Fdata_access\" AND protoPayload.serviceName=\"iap.googleapis.com\" AND timestamp>=\"$(date -u -d '6 seconds ago' +%Y-%m-%dT%H:%M:%SZ)\"" --project="${GOOGLE_CLOUD_PROJECT}" --limit=10 --format='value(timestamp,protoPayload.authorizationInfo[0].granted,protoPayload.resourceName)'
  done
fi
