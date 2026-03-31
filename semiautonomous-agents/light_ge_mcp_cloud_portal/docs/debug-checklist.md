# Debug Checklist

[<- Back to Main README](../README.md) | [Troubleshooting](troubleshooting.md)

Use this checklist when things aren't working. Work through each section in order.

---

## Phase 1: Infrastructure Verification

```
+------------------------------------------------------------------+
|                    INFRASTRUCTURE CHECKLIST                       |
+------------------------------------------------------------------+
|                                                                  |
|  GCP PROJECT                                                     |
|  [ ] Project ID correct in .env                                  |
|  [ ] APIs enabled:                                               |
|      [ ] Vertex AI API                                           |
|      [ ] Discovery Engine API                                    |
|      [ ] IAM Service Account Credentials API                     |
|      [ ] Cloud Run Admin API                                     |
|                                                                  |
|  AGENT ENGINE                                                    |
|  [ ] Agent deployed successfully                                 |
|  [ ] Agent Engine ID saved                                       |
|  [ ] Service account has required roles                          |
|                                                                  |
|  CLOUD RUN (MCP Server)                                          |
|  [ ] Service deployed and healthy                                |
|  [ ] IAM allows invoker access                                   |
|  [ ] URL matches SERVICENOW_MCP_URL in agent/.env                |
|                                                                  |
|  DISCOVERY ENGINE                                                |
|  [ ] App created with correct ENGINE_ID                          |
|  [ ] SharePoint federated connector configured                   |
|  [ ] Widget config returns datastores                            |
|                                                                  |
+------------------------------------------------------------------+
```

### Verification Commands

```bash
# Check enabled APIs
gcloud services list --enabled | grep -E "aiplatform|discoveryengine|run|iam"

# Check Agent Engine deployment
gcloud ai reasoning-engines list --region=us-central1

# Check Cloud Run service
gcloud run services describe servicenow-mcp --region=us-central1 --format="value(status.url)"

# Check service account roles
gcloud projects get-iam-policy $PROJECT_ID \
    --flatten="bindings[].members" \
    --filter="bindings.members:compute@developer.gserviceaccount.com"
```

---

## Phase 2: Authentication Flow

```
+------------------------------------------------------------------+
|                    AUTHENTICATION CHECKLIST                       |
+------------------------------------------------------------------+
|                                                                  |
|  STEP 1: ENTRA ID LOGIN                                          |
|  [ ] User can log in via MSAL popup                              |
|  [ ] ID token returned (starts with "eyJ")                       |
|  [ ] Token contains email claim                                  |
|                                                                  |
|  STEP 2: WIF TOKEN EXCHANGE                                      |
|  [ ] STS endpoint returns access_token                           |
|  [ ] Pool ID matches: WIF_POOL_ID                                |
|  [ ] Provider ID matches: WIF_PROVIDER_ID                        |
|  [ ] Audience format correct                                     |
|                                                                  |
|  STEP 3: SESSION CREATION                                        |
|  [ ] Session created successfully                                |
|  [ ] USER_TOKEN stored in session state                          |
|  [ ] Session ID returned                                         |
|                                                                  |
|  STEP 4: HEADER PROVIDER                                         |
|  [ ] Cloud Run ID token generated                                |
|  [ ] USER_TOKEN extracted from session.state                     |
|  [ ] Both headers added to request                               |
|                                                                  |
+------------------------------------------------------------------+
```

### Test Each Step

```javascript
// Step 1: Test MSAL login (browser console)
const response = await msalInstance.loginPopup({ scopes: ["openid", "profile", "email"] });
console.log("ID Token:", response.idToken.substring(0, 50) + "...");

// Step 2: Test WIF exchange
const stsResponse = await fetch("https://sts.googleapis.com/v1/token", {
    method: "POST",
    body: new URLSearchParams({
        grant_type: "urn:ietf:params:oauth:grant-type:token-exchange",
        audience: `//iam.googleapis.com/locations/global/workforcePools/${poolId}/providers/${providerId}`,
        subject_token: idToken,
        subject_token_type: "urn:ietf:params:oauth:token-type:id_token",
        requested_token_type: "urn:ietf:params:oauth:token-type:access_token",
        scope: "https://www.googleapis.com/auth/cloud-platform"
    })
});
const data = await stsResponse.json();
console.log("GCP Token:", data.access_token?.substring(0, 50) + "...");
```

---

## Phase 3: Tool Execution

```
+------------------------------------------------------------------+
|                    TOOL EXECUTION CHECKLIST                       |
+------------------------------------------------------------------+
|                                                                  |
|  MCP SERVER CONNECTION                                           |
|  [ ] SSE connection established                                  |
|  [ ] Tools list returned                                         |
|  [ ] No timeout errors                                           |
|                                                                  |
|  MCP TOOL CALL                                                   |
|  [ ] Authorization header present (Cloud Run token)              |
|  [ ] X-User-Token header present (Entra JWT)                     |
|  [ ] ServiceNow returns 200                                      |
|  [ ] Data returned correctly                                     |
|                                                                  |
|  DISCOVERY ENGINE CALL                                           |
|  [ ] Datastores discovered (> 0)                                 |
|  [ ] WIF token exchanged for user                                |
|  [ ] streamAssist API returns 200                                |
|  [ ] textGroundingMetadata present                               |
|  [ ] Source citations included                                   |
|                                                                  |
+------------------------------------------------------------------+
```

### Test MCP Server Directly

```bash
# Health check
curl https://servicenow-mcp-xxx.us-central1.run.app/health

# Test SSE with auth (requires Cloud Run invoker permission)
curl -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
     https://servicenow-mcp-xxx.us-central1.run.app/sse
```

### Test Discovery Engine Directly

```bash
# Test streamAssist API
curl -X POST "https://discoveryengine.googleapis.com/v1alpha/projects/PROJECT_NUM/locations/global/collections/default_collection/engines/ENGINE_ID/servingConfigs/default_search:streamAssist" \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  -H "Content-Type: application/json" \
  -d '{
    "query": {"text": "test query"},
    "session": "projects/PROJECT_NUM/locations/global/collections/default_collection/engines/ENGINE_ID/sessions/-"
  }'
```

---

## Phase 4: Data Flow Verification

```
+------------------------------------------------------------------+
|                    DATA FLOW VERIFICATION                         |
+------------------------------------------------------------------+
|                                                                  |
|  Request Flow:                                                   |
|                                                                  |
|  Frontend                                                        |
|    |                                                             |
|    | 1. USER_TOKEN in session state                              |
|    v                                                             |
|  Agent Engine                                                    |
|    |                                                             |
|    | 2. header_provider extracts USER_TOKEN                      |
|    | 3. Generates Cloud Run ID token                             |
|    | 4. Adds both to headers                                     |
|    v                                                             |
|  MCP Server                                                      |
|    |                                                             |
|    | 5. Validates Cloud Run token (IAM)                          |
|    | 6. Extracts X-User-Token                                    |
|    | 7. Passes to ServiceNow                                     |
|    v                                                             |
|  ServiceNow                                                      |
|    |                                                             |
|    | 8. Validates JWT (OIDC)                                     |
|    | 9. Maps to user                                             |
|    | 10. Returns user-scoped data                                |
|                                                                  |
+------------------------------------------------------------------+
```

### Add Logging at Each Point

```python
# agent/agent.py - Point 2,3,4
def mcp_header_provider(readonly_context):
    print(f"[2] Session state: {dict(readonly_context.session.state)}")
    print(f"[3] Cloud Run token: {cloud_run_token[:50]}...")
    print(f"[4] Headers: {headers}")
    return headers

# mcp-server/mcp_server.py - Point 5,6,7
def _extract_token_from_context(ctx):
    print(f"[5] Request received")
    print(f"[6] X-User-Token: {user_token[:50] if user_token else 'MISSING'}")
    print(f"[7] Calling ServiceNow with token")
```

---

## Quick Reference: Common Fixes

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| Pickle error on deploy | McpToolset not lazy | Use LazyMcpToolset |
| 401 from Cloud Run | Missing invoker role | Grant roles/run.invoker |
| USER_TOKEN None | Wrong state access | Use session.state |
| Discovery returns empty | No datastores found | Fix _get_dynamic_datastores |
| ServiceNow 401 | OIDC not configured | Setup OIDC provider |
| WIF exchange fails | Wrong audience | Check pool/provider IDs |

---

## Log Collection Commands

```bash
# Collect all relevant logs
echo "=== Cloud Run Logs ===" > debug_logs.txt
gcloud run services logs read servicenow-mcp --region=us-central1 --limit=50 >> debug_logs.txt

echo -e "\n=== Agent Engine Logs ===" >> debug_logs.txt
gcloud logging read 'resource.type="aiplatform.googleapis.com/ReasoningEngine"' --limit=50 >> debug_logs.txt

echo -e "\n=== Recent Deployments ===" >> debug_logs.txt
gcloud ai reasoning-engines list --region=us-central1 >> debug_logs.txt
```

---

## Related Documentation

- [Troubleshooting Guide](troubleshooting.md) - Detailed error solutions
- [Security Flow](security-flow.md) - Token flow diagrams
- [Architecture](architecture.md) - System overview
