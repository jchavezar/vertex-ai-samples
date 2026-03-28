#!/bin/bash
# Test TypeScript Backend
# Usage: ./test-backend.sh [BACKEND_URL] [JWT_TOKEN]

set -e

BACKEND_URL="${1:-http://localhost:8080}"
JWT_TOKEN="${2:-$TEST_JWT_TOKEN}"

echo "================================================"
echo "Testing Backend: $BACKEND_URL"
echo "================================================"

if [ -z "$JWT_TOKEN" ]; then
    echo "WARNING: No JWT token provided."
    echo "Usage: ./test-backend.sh [BACKEND_URL] [JWT_TOKEN]"
    echo "Or set TEST_JWT_TOKEN environment variable"
    echo ""
    echo "Continuing with health check only..."
fi

echo ""
echo "--- Test 1: Health Check ---"
curl -s "$BACKEND_URL/health" | jq .

if [ -n "$JWT_TOKEN" ]; then
    echo ""
    echo "--- Test 2: Chat (creates session + streams response) ---"
    echo "Streaming response:"
    curl -N -X POST "$BACKEND_URL/api/chat" \
        -H "Authorization: Bearer $JWT_TOKEN" \
        -H "Content-Type: application/json" \
        -d '{"message": "What tools do you have available?"}'

    echo ""
    echo ""
    echo "--- Test 3: List Sessions ---"
    curl -s "$BACKEND_URL/api/sessions" | jq .
fi

echo ""
echo "================================================"
echo "Backend tests completed!"
echo "================================================"
