#!/bin/bash
# Display the exact values to paste into Gemini Enterprise console

echo "=========================================="
echo "COPY THESE VALUES INTO GE CONSOLE"
echo "=========================================="
echo
echo "MCP Server URL:"
echo "  https://mcp.atlassian.com/v1/mcp"
echo
echo "Authorization URL:"
echo "  https://mcp.atlassian.com/v1/authorize"
echo
echo "Authorization URL Parameters:"
echo "  (leave blank)"
echo
echo "Token URL:"
echo "  https://cf.mcp.atlassian.com/v1/token"
echo
echo "Client ID:"
if [ -f /tmp/atlassian_oauth_creds.json ]; then
  cat /tmp/atlassian_oauth_creds.json | python3 -c 'import json,sys; print("  " + json.load(sys.stdin).get("client_id","NOT_FOUND"))'
else
  echo "  (run ./register_oauth_client.sh first)"
fi
echo
echo "Client Secret:"
if [ -f /tmp/atlassian_oauth_creds.json ]; then
  cat /tmp/atlassian_oauth_creds.json | python3 -c 'import json,sys; print("  " + json.load(sys.stdin).get("client_secret","NOT_FOUND"))'
else
  echo "  (run ./register_oauth_client.sh first)"
fi
echo
echo "Scopes:"
echo "  read:jira-work write:jira-work read:jira-user read:me offline_access"
echo
echo "=========================================="
