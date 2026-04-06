#!/bin/bash

# Ensure we are in the right directory
BASE_DIR=$(pwd)
PROJECT_DIR="$BASE_DIR/shroud-harness-v1"

echo ">>> Forcefully clearing port 3000..."
fuser -k 3000/tcp 2>/dev/null

echo ">>> Refreshing GCLOUD_TOKEN..."
TOKEN=$(gcloud auth print-access-token 2>/dev/null)

if [ -z "$TOKEN" ]; then
    echo "!!! Error: Could not get GCLOUD_TOKEN. Refreshing login..."
    gcloud auth login --brief
    TOKEN=$(gcloud auth print-access-token 2>/dev/null)
fi

# Write to .env.local for Next.js to pick up reliably
echo "GCLOUD_TOKEN=$TOKEN" > "$PROJECT_DIR/.env.local"
echo ">>> Token written to $PROJECT_DIR/.env.local"

echo ">>> Starting Shroud Harness on port 3000..."
cd "$PROJECT_DIR"
# Force development on port 3000
PORT=3000 npm run dev
