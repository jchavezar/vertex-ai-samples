#!/usr/bin/env bash
# Tail IAP audit logs for the gateway so we can confirm allow/deny patterns
# before flipping enforce mode.
set -euo pipefail

source "$(dirname "$0")/../.env"
: "${GOOGLE_CLOUD_PROJECT:?}"

LIMIT="${1:-50}"

echo "[infra/99] last ${LIMIT} IAP entries on this project:"
gcloud logging read "logName=\"projects/${GOOGLE_CLOUD_PROJECT}/logs/cloudaudit.googleapis.com%2Fdata_access\" AND protoPayload.serviceName=\"iap.googleapis.com\"" --project="${GOOGLE_CLOUD_PROJECT}" --limit="${LIMIT}" --format='value(timestamp,protoPayload.authorizationInfo[0].granted,protoPayload.resourceName,protoPayload.request.attributes.request.auth.principal,protoPayload.methodName)'
