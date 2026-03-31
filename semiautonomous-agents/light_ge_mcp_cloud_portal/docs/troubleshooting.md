# Troubleshooting Guide

[<- Back to Main README](../README.md) | [Debug Checklist](debug-checklist.md)

## Quick Diagnostics

```
+------------------------------------------------------------------+
|                    TROUBLESHOOTING DECISION TREE                  |
+------------------------------------------------------------------+
|                                                                  |
|  ERROR OCCURRED                                                  |
|       |                                                          |
|       v                                                          |
|  Is it during DEPLOYMENT?                                        |
|       |                                                          |
|   YES |              NO                                          |
|       v               v                                          |
|  +---------+    Is it during LOGIN?                              |
|  | Pickle  |         |                                           |
|  | Error   |     YES |              NO                           |
|  | See #1  |         v               v                           |
|  +---------+    +---------+    Is it during QUERY?               |
|                 | Auth    |         |                            |
|                 | Error   |     YES |              NO            |
|                 | See #2  |         v               v            |
|                 +---------+    +---------+    +---------+        |
|                                | Query   |    | Tool    |        |
|                                | Error   |    | Error   |        |
|                                | See #3  |    | See #4  |        |
|                                +---------+    +---------+        |
|                                                                  |
+------------------------------------------------------------------+
```

---

## 1. Deployment Errors

### 1.1 Pickle Serialization Failed

```
ERROR: 'MCPSessionManager' object has no attribute '_sampling_callback'
ERROR: TypeError: cannot pickle 'SSLContext' object
```

**Root Cause:** McpToolset contains non-serializable objects (SSE connections, async callbacks)

**Solution:** Use LazyMcpToolset pattern

```python
# WRONG - Direct McpToolset
root_agent = LlmAgent(
    tools=[McpToolset(connection_params=SseConnectionParams(url=URL))]  # FAILS
)

# CORRECT - LazyMcpToolset
class LazyMcpToolset(BaseToolset):
    def __init__(self, url, header_provider):
        super().__init__()
        self._url = url
        self._header_provider = header_provider
        self._toolset = None  # Created at runtime, not deployment

    def __getstate__(self):
        return {"_url": self._url, "_header_provider": self._header_provider, "_toolset": None}

    def __setstate__(self, state):
        self.__init__(state["_url"], state["_header_provider"])

root_agent = LlmAgent(tools=[LazyMcpToolset(url=URL, header_provider=fn)])  # WORKS
```

See: [LazyMcpToolset Pattern](lazy-mcp-pattern.md)

### 1.2 Validation Error - Not a Tool

```
ValidationError: tools[0] must be a Tool, Toolset, or callable
```

**Root Cause:** LazyMcpToolset doesn't inherit from BaseToolset

**Solution:**
```python
from google.adk.tools.base_toolset import BaseToolset

class LazyMcpToolset(BaseToolset):  # Must inherit
    def __init__(self, ...):
        super().__init__()  # Must call parent
```

---

## 2. Authentication Errors

### 2.1 WIF Token Exchange Failed

```
ERROR: STS exchange failed: invalid_grant
```

**Diagnostic Diagram:**
```
+------------------------------------------------------------------+
|                    WIF TOKEN EXCHANGE FAILURE                     |
+------------------------------------------------------------------+
|                                                                  |
|  Entra JWT                                                       |
|       |                                                          |
|       v                                                          |
|  +---------------------------------------------------------+    |
|  | Check 1: Is JWT valid?                                   |    |
|  |   - Not expired (exp claim)                              |    |
|  |   - Correct audience (aud = your client ID)              |    |
|  +---------------------------------------------------------+    |
|       |                                                          |
|       v                                                          |
|  +---------------------------------------------------------+    |
|  | Check 2: Is WIF pool configured?                         |    |
|  |   - Pool ID matches                                      |    |
|  |   - Provider ID matches                                  |    |
|  |   - Issuer URL = https://login.microsoftonline.com/{tid}|    |
|  +---------------------------------------------------------+    |
|       |                                                          |
|       v                                                          |
|  +---------------------------------------------------------+    |
|  | Check 3: Is audience correct?                            |    |
|  |   - Format: //iam.googleapis.com/locations/global/       |    |
|  |            workforcePools/{pool}/providers/{provider}    |    |
|  +---------------------------------------------------------+    |
|                                                                  |
+------------------------------------------------------------------+
```

**Verify WIF Configuration:**
```bash
# List workforce pools
gcloud iam workforce-pools list --location=global

# Describe provider
gcloud iam workforce-pools providers describe {provider-id} \
    --workforce-pool={pool-id} \
    --location=global
```

### 2.2 Cloud Run 401 Unauthorized

```
ERROR: 401 Unauthorized - Could not authenticate request
```

**Root Cause:** Missing or invalid Cloud Run ID token

**Diagnostic:**
```python
# In header_provider
try:
    cloud_run_token = id_token.fetch_id_token(request, MCP_BASE_URL)
    print(f"Got token: {cloud_run_token[:50]}...")
except Exception as e:
    print(f"Token fetch failed: {e}")  # This is the problem
```

**Solution:** Ensure service account has `roles/run.invoker`:
```bash
gcloud run services add-iam-policy-binding servicenow-mcp \
    --member="serviceAccount:{project-number}-compute@developer.gserviceaccount.com" \
    --role="roles/run.invoker" \
    --region=us-central1
```

---

## 3. Query Errors

### 3.1 Response Not Grounded (Generic LLM Response)

**Symptom:**
```
Query: "What is the CFO salary?"
Response: "A CFO's salary typically ranges from $150,000 to $500,000..."
          (Generic answer, no specific names, no citations)
```

**Root Cause:** Missing or incorrectly structured `dataStoreSpecs`

**Diagnostic:**
```
+------------------------------------------------------------------+
|           GROUNDING NOT WORKING - DIAGNOSTIC CHECKLIST            |
+------------------------------------------------------------------+
|                                                                  |
|  [ ] 1. Is dataStoreSpecs in the payload?                        |
|      Check logs: "[DE] Dynamic datastores found: N"              |
|      If N = 0, datastores are not being passed                   |
|                                                                  |
|  [ ] 2. Is dataStoreSpecs nested correctly?                      |
|      WRONG:  {"dataStoreSpecs": [...]}                           |
|      RIGHT:  {"toolsSpec": {"vertexAiSearchSpec":                |
|                 {"dataStoreSpecs": [...]}}}                      |
|                                                                  |
|  [ ] 3. Check response for textGroundingMetadata                 |
|      If missing -> grounding did not trigger                     |
|      If present but empty -> no matching documents               |
|                                                                  |
|  [ ] 4. Is user token valid for SharePoint access?               |
|      ACLs may prevent access to documents                        |
|                                                                  |
+------------------------------------------------------------------+
```

**Solution:**
```python
# Ensure dataStoreSpecs is wrapped in toolsSpec.vertexAiSearchSpec
payload = {
    "query": {"text": query},
    "toolsSpec": {
        "vertexAiSearchSpec": {
            "dataStoreSpecs": [
                {"dataStore": "projects/.../dataStores/your-datastore"}
            ]
        }
    }
}
```

### 3.2 Discovery Engine 400 Bad Request

```
ERROR: 400 Bad Request - Invalid JSON payload received. Unknown name "description"
```

**Root Cause:** Invalid field in dataStoreSpecs

**Solution:** Remove description field:
```python
# WRONG
dataStoreSpecs = [
    {"dataStore": "...", "description": "SharePoint"}  # Invalid
]

# CORRECT
dataStoreSpecs = [
    {"dataStore": "..."}  # Only dataStore field
]
```

### 3.2 Discovery Engine Returns No Results

```
[DE] Answer: I don't have information about that
[DE] Sources: []
```

**Diagnostic Checklist:**
```
+------------------------------------------------------------------+
|                    NO RESULTS DIAGNOSTIC                          |
+------------------------------------------------------------------+
|                                                                  |
|  [ ] 1. Are datastores being discovered?                         |
|      - Check logs: "[DE] Dynamic datastores found: N"            |
|      - N should be > 0                                           |
|                                                                  |
|  [ ] 2. Is user token being passed?                              |
|      - Check logs: "[DE] Using WIF token exchange"               |
|      - Token should start with "eyJ"                             |
|                                                                  |
|  [ ] 3. Does user have SharePoint access?                        |
|      - Test same query in SharePoint directly                    |
|      - Check ACLs on documents                                   |
|                                                                  |
|  [ ] 4. Are documents indexed?                                   |
|      - Check Discovery Engine console                            |
|      - Verify sync status is ACTIVE                              |
|                                                                  |
+------------------------------------------------------------------+
```

### 3.3 USER_TOKEN Not Found in State

```
[Agent] USER_TOKEN not found in session state
```

**Root Cause:** Accessing state incorrectly or token not passed in session

**Solution:**
```python
# WRONG - Direct state access
user_token = readonly_context.state.get("USER_TOKEN")  # May be None

# CORRECT - Access via session.state
if hasattr(readonly_context, "session") and hasattr(readonly_context.session, "state"):
    session_state = dict(readonly_context.session.state)
    user_token = session_state.get("USER_TOKEN")
```

---

## 4. Tool Errors

### 4.1 MCP Connection Timeout

```
ERROR: MCP connection timeout after 120s
```

**Root Cause:** MCP server not responding or URL incorrect

**Diagnostic:**
```bash
# Test MCP server health
curl -v https://servicenow-mcp-xxx.us-central1.run.app/health

# Check Cloud Run logs
gcloud run services logs read servicenow-mcp --region=us-central1 --limit=50
```

### 4.2 ServiceNow 401 From MCP Server

```
[MCP] ServiceNow API error: 401 Unauthorized
```

**Root Cause:** JWT not being passed or ServiceNow OIDC misconfigured

**Diagnostic Flow:**
```
+------------------------------------------------------------------+
|                    SERVICENOW 401 DIAGNOSTIC                      |
+------------------------------------------------------------------+
|                                                                  |
|  [ ] 1. Is X-User-Token header being sent?                       |
|      - Add logging in header_provider                            |
|      - Check MCP server logs for incoming headers                |
|                                                                  |
|  [ ] 2. Is MCP server extracting token correctly?                |
|      - Check _extract_token_from_context() logs                  |
|      - Verify SSE transport header access                        |
|                                                                  |
|  [ ] 3. Is ServiceNow OIDC provider configured?                  |
|      - Check System OIDC > OIDC Provider Entity                  |
|      - Verify issuer URL matches Entra ID                        |
|      - Check user field mapping (email)                          |
|                                                                  |
|  [ ] 4. Does mapped user exist in ServiceNow?                    |
|      - Check sys_user table for email match                      |
|                                                                  |
+------------------------------------------------------------------+
```

---

## 5. Environment Issues

### 5.1 Missing Environment Variable

```
ERROR: SERVICENOW_MCP_URL environment variable is required
```

**Solution:**
```bash
# Check current env vars
cat agent/.env

# Ensure required vars are set
echo "SERVICENOW_MCP_URL=https://servicenow-mcp-xxx.us-central1.run.app/sse" >> agent/.env
```

### 5.2 Wrong Project/Location

```
ERROR: Resource not found in project X
```

**Solution:** Verify configuration:
```bash
# Check gcloud config
gcloud config get-value project
gcloud config get-value compute/region

# Update .env to match
GOOGLE_CLOUD_PROJECT=correct-project
GOOGLE_CLOUD_LOCATION=us-central1
```

---

## Logging Best Practices

### Enable Debug Logging

```python
# agent/agent.py
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def mcp_header_provider(readonly_context):
    logger.debug(f"[header_provider] Called with context: {type(readonly_context)}")
    logger.debug(f"[header_provider] Session state keys: {list(readonly_context.session.state.keys())}")
    # ...
```

### Check Cloud Run Logs

```bash
# MCP Server logs
gcloud run services logs read servicenow-mcp --region=us-central1 --limit=100

# Agent Engine logs (via Cloud Logging)
gcloud logging read 'resource.type="aiplatform.googleapis.com/ReasoningEngine"' --limit=50
```

---

## Related Documentation

- [Debug Checklist](debug-checklist.md) - Step-by-step debugging
- [LazyMcpToolset Pattern](lazy-mcp-pattern.md) - Deployment serialization fix
- [Security Flow](security-flow.md) - Token flow understanding
