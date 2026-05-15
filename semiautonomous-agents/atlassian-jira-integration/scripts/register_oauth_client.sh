#!/bin/bash
# Register OAuth client with Atlassian Remote MCP server for Gemini Enterprise

echo "Registering OAuth client with Atlassian MCP..."
echo

curl -sS -X POST https://cf.mcp.atlassian.com/v1/register \
  -H "Content-Type: application/json" \
  -d '{"redirect_uris":["https://vertexaisearch.cloud.google.com/oauth-redirect"],"client_name":"gemini-enterprise-jira","token_endpoint_auth_method":"client_secret_basic","grant_types":["authorization_code","refresh_token"],"response_types":["code"]}' \
  | tee /tmp/atlassian_oauth_creds.json | python3 -m json.tool

echo
echo "====================================="
echo "Credentials saved to: /tmp/atlassian_oauth_creds.json"
echo
echo "Use these values in Gemini Enterprise console:"
echo "  Client ID: $(cat /tmp/atlassian_oauth_creds.json | python3 -c 'import json,sys; print(json.load(sys.stdin).get("client_id","ERROR"))')"
echo "  Client Secret: $(cat /tmp/atlassian_oauth_creds.json | python3 -c 'import json,sys; print(json.load(sys.stdin).get("client_secret","ERROR"))')"
echo "====================================="
