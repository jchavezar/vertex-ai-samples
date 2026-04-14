#!/bin/bash
# Test Agent Engine directly via REST API
# Usage: ./test-agent-engine.sh [JWT_TOKEN]

set -e

# Configuration (override via environment)
PROJECT="${GOOGLE_CLOUD_PROJECT:-your-project-id}"
LOCATION="${GOOGLE_CLOUD_LOCATION:-us-central1}"
AGENT_ID="${AGENT_ENGINE_ID:-your-agent-id}"
JWT_TOKEN="${1:-$TEST_JWT_TOKEN}"

AGENT_PATH="projects/$PROJECT/locations/$LOCATION/reasoningEngines/$AGENT_ID"
BASE_URL="https://$LOCATION-aiplatform.googleapis.com/v1beta1/$AGENT_PATH"

echo "================================================"
echo "Testing Agent Engine"
echo "================================================"
echo "Project:  $PROJECT"
echo "Location: $LOCATION"
echo "Agent ID: $AGENT_ID"
echo "================================================"

# Get GCP access token
GCP_TOKEN=$(gcloud auth print-access-token 2>/dev/null)
if [ -z "$GCP_TOKEN" ]; then
    echo "ERROR: Could not get GCP access token. Run: gcloud auth login"
    exit 1
fi

if [ -z "$JWT_TOKEN" ]; then
    echo "WARNING: No JWT token provided."
    echo "Usage: ./test-agent-engine.sh [JWT_TOKEN]"
    echo "Or set TEST_JWT_TOKEN environment variable"
    echo ""
    echo "The agent will not be able to authenticate to ServiceNow!"
    JWT_TOKEN=""
fi

echo ""
echo "--- Test 1: Create Session with JWT Token ---"
SESSION_RESPONSE=$(curl -s -X POST "$BASE_URL/sessions" \
    -H "Authorization: Bearer $GCP_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{
        \"userId\": \"test_user\",
        \"agentSession\": {
            \"state\": {
                \"USER_TOKEN\": \"$JWT_TOKEN\"
            }
        }
    }")

echo "$SESSION_RESPONSE" | jq .

# Extract session ID
SESSION_NAME=$(echo "$SESSION_RESPONSE" | jq -r '.name // empty')
if [ -z "$SESSION_NAME" ]; then
    echo "ERROR: Could not create session"
    exit 1
fi

SESSION_ID=$(echo "$SESSION_NAME" | rev | cut -d'/' -f1 | rev)
echo "Session ID: $SESSION_ID"

echo ""
echo "--- Test 2: Query Agent (non-streaming) ---"
QUERY_URL="https://$LOCATION-aiplatform.googleapis.com/v1/$AGENT_PATH:query"

curl -s -X POST "$QUERY_URL" \
    -H "Authorization: Bearer $GCP_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{
        \"class_method\": \"async_stream_query\",
        \"input\": {
            \"user_id\": \"test_user\",
            \"session_id\": \"$SESSION_ID\",
            \"message\": \"List 2 incidents\"
        }
    }" | jq .

echo ""
echo "--- Test 3: Stream Query ---"
STREAM_URL="https://$LOCATION-aiplatform.googleapis.com/v1/$AGENT_PATH:streamQuery?alt=sse"

echo "Streaming response (Ctrl+C to stop):"
curl -N -X POST "$STREAM_URL" \
    -H "Authorization: Bearer $GCP_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{
        \"class_method\": \"async_stream_query\",
        \"input\": {
            \"user_id\": \"test_user\",
            \"session_id\": \"$SESSION_ID\",
            \"message\": \"What ServiceNow tools do you have?\"
        }
    }"

echo ""
echo "================================================"
echo "Agent Engine tests completed!"
echo "================================================"
