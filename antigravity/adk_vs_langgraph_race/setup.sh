#!/bin/bash
# Setup script for AI Framework Race

set -e

echo "=== AI Framework Race Setup ==="

# Check if we're in the right directory
if [ ! -f "backend/pyproject.toml" ]; then
    echo "Error: Run this script from the project root directory"
    exit 1
fi

# Get project ID
if [ -z "$GOOGLE_CLOUD_PROJECT" ]; then
    GOOGLE_CLOUD_PROJECT=$(gcloud config get-value project 2>/dev/null)
fi

if [ -z "$GOOGLE_CLOUD_PROJECT" ]; then
    echo "Error: Set GOOGLE_CLOUD_PROJECT or run 'gcloud config set project <project-id>'"
    exit 1
fi

echo "Using project: $GOOGLE_CLOUD_PROJECT"

# Create .env file
cat > backend/.env << EOF
GOOGLE_CLOUD_PROJECT=$GOOGLE_CLOUD_PROJECT
GOOGLE_CLOUD_LOCATION=us-central1
EOF

echo "Created backend/.env"

# Setup Python environment
cd backend

if command -v uv &> /dev/null; then
    echo "Installing dependencies with uv..."
    uv sync
else
    echo "Installing dependencies with pip..."
    python -m pip install -e .
fi

echo ""
echo "=== Setup Complete ==="
echo ""
echo "To run the race:"
echo "  cd backend"
echo "  uv run uvicorn main:app --reload --port 8080"
echo ""
echo "Then open: http://localhost:8080"
