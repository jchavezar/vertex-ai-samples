#!/bin/bash
# Deployment container entrypoint
# Usage: docker run -v /path/to/code:/workspace -v /path/to/sa.json:/secrets/sa-key.json deployment-container [command]
set -euo pipefail

# Verify service account is present
if [ ! -f /secrets/sa-key.json ]; then
  echo "❌ Service account key not found at /secrets/sa-key.json"
  echo "Mount it with: -v /path/to/sa.json:/secrets/sa-key.json"
  exit 1
fi

# Activate service account
gcloud auth activate-service-account --key-file=/secrets/sa-key.json --quiet

# Run the command passed to the container
exec "$@"
