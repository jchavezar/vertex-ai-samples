#!/bin/bash
# Test MCP Server locally or remotely
# Usage: ./test-mcp-server.sh [MCP_URL] [JWT_TOKEN]

set -e

MCP_URL="${1:-http://localhost:8080/mcp}"
JWT_TOKEN="${2:-$TEST_JWT_TOKEN}"

echo "================================================"
echo "Testing MCP Server: $MCP_URL"
echo "================================================"

if [ -z "$JWT_TOKEN" ]; then
    echo "WARNING: No JWT token provided."
    echo "Usage: ./test-mcp-server.sh [MCP_URL] [JWT_TOKEN]"
    echo "Or set TEST_JWT_TOKEN environment variable"
    echo ""
    echo "To get a token, open scripts/get-jwt-token.html in a browser"
    echo ""
    echo "Continuing without token (will use Basic Auth fallback if configured)..."
    AUTH_HEADER=""
else
    echo "Using JWT token (length: ${#JWT_TOKEN})"
    AUTH_HEADER="-H \"Authorization: Bearer $JWT_TOKEN\""
fi

echo ""
echo "--- Test 1: List Tools ---"
curl -s -X POST "$MCP_URL" \
    -H "Content-Type: application/json" \
    ${AUTH_HEADER:+-H "Authorization: Bearer $JWT_TOKEN"} \
    -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}' | jq .

echo ""
echo "--- Test 2: List Incidents (limit 3) ---"
curl -s -X POST "$MCP_URL" \
    -H "Content-Type: application/json" \
    ${AUTH_HEADER:+-H "Authorization: Bearer $JWT_TOKEN"} \
    -d '{
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {
            "name": "list_incidents",
            "arguments": {"limit": 3}
        }
    }' | jq .

echo ""
echo "--- Test 3: Query Table ---"
curl -s -X POST "$MCP_URL" \
    -H "Content-Type: application/json" \
    ${AUTH_HEADER:+-H "Authorization: Bearer $JWT_TOKEN"} \
    -d '{
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "query_table",
            "arguments": {"table_name": "incident", "limit": 2}
        }
    }' | jq .

echo ""
echo "================================================"
echo "MCP Server tests completed!"
echo "================================================"
