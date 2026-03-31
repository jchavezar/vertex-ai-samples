# Security & Authentication Flow

[← Back to Main README](../README.md) | [Architecture](architecture.md)

## Token Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 1: USER LOGIN (MSAL + Entra ID)                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   User clicks "Sign in"                                                     │
│         │                                                                   │
│         ▼                                                                   │
│   ┌─────────────┐     ┌─────────────┐     ┌─────────────┐                  │
│   │   MSAL      │────▶│  Entra ID   │────▶│  ID Token   │                  │
│   │   Popup     │     │  Login      │     │  (JWT)      │                  │
│   └─────────────┘     └─────────────┘     └─────────────┘                  │
│                                                 │                           │
│   Token contains:                               │                           │
│   - sub: user identifier                        │                           │
│   - email: user@domain.com                      │                           │
│   - preferred_username                          │                           │
│   - aud: Application Client ID                  │                           │
│                                                 │                           │
└─────────────────────────────────────────────────┼───────────────────────────┘
                                                  │
                                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 2: WORKFORCE IDENTITY FEDERATION (STS Exchange)                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌─────────────┐     ┌─────────────────────────────────┐                  │
│   │  Entra JWT  │────▶│  https://sts.googleapis.com/v1/token               │
│   └─────────────┘     └─────────────────────────────────┘                  │
│                                    │                                        │
│   Request:                         │                                        │
│   - grant_type: token-exchange     │                                        │
│   - subject_token: {Entra JWT}     │                                        │
│   - audience: //iam.googleapis.com/locations/global/                        │
│               workforcePools/{pool}/providers/{provider}                    │
│                                    │                                        │
│                                    ▼                                        │
│   ┌─────────────────────────────────────────────────────────┐              │
│   │  GCP Access Token (scoped to cloud-platform)            │              │
│   │  - Used for Agent Engine API calls                      │              │
│   │  - Identity: principalSet://...workforcePools/...       │              │
│   └─────────────────────────────────────────────────────────┘              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                                  │
                                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 3: AGENT ENGINE SESSION (Token in State)                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   POST /reasoningEngines/{id}:query                                         │
│   Authorization: Bearer {GCP Access Token}                                  │
│   Body: {                                                                   │
│     "class_method": "create_session",                                       │
│     "input": {                                                              │
│       "user_id": "user@domain.com",                                         │
│       "state": {                                                            │
│         "USER_TOKEN": "{Original Entra JWT}"  ◄── Stored for MCP calls     │
│       }                                                                     │
│     }                                                                       │
│   }                                                                         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                                  │
                                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 4: MCP TOOL CALL (header_provider)                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   Agent decides to call MCP tool (e.g., list_incidents)                     │
│         │                                                                   │
│         ▼                                                                   │
│   ┌─────────────────────────────────────────────────────────┐              │
│   │  header_provider(readonly_context) called               │              │
│   │                                                         │              │
│   │  1. Get Cloud Run ID token (service-to-service auth)   │              │
│   │     id_token.fetch_id_token(request, MCP_BASE_URL)      │              │
│   │                                                         │              │
│   │  2. Get USER_TOKEN from session state                   │              │
│   │     readonly_context.session.state["USER_TOKEN"]        │              │
│   │                                                         │              │
│   │  Returns headers:                                       │              │
│   │  {                                                      │              │
│   │    "Authorization": "Bearer {Cloud Run ID token}",      │              │
│   │    "X-User-Token": "{Entra JWT}"                        │              │
│   │  }                                                      │              │
│   └─────────────────────────────────────────────────────────┘              │
│                                                                             │
│   See: [agent/agent.py#L105-L140](../agent/agent.py#L105-L140)             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                                  │
                                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 5: MCP SERVER (Header Extraction)                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   Cloud Run validates Authorization header (IAM check)                      │
│         │                                                                   │
│         ▼                                                                   │
│   ┌─────────────────────────────────────────────────────────┐              │
│   │  _extract_token_from_context(ctx)                       │              │
│   │                                                         │              │
│   │  # For SSE transport, headers are on request object     │              │
│   │  request = ctx.request_context.request                  │              │
│   │  headers = request.headers                              │              │
│   │                                                         │              │
│   │  # Extract user JWT                                     │              │
│   │  user_token = headers.get("x-user-token")               │              │
│   └─────────────────────────────────────────────────────────┘              │
│                                                                             │
│   See: [mcp-server/mcp_server.py#L56-L98](../mcp-server/mcp_server.py#L56-L98) │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                                  │
                                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 6: SERVICENOW API (JWT Authentication)                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   GET /api/now/table/incident                                               │
│   Authorization: Bearer {Entra JWT}                                         │
│         │                                                                   │
│         ▼                                                                   │
│   ┌─────────────────────────────────────────────────────────┐              │
│   │  ServiceNow OIDC Provider                               │              │
│   │                                                         │              │
│   │  1. Validates JWT signature (via OIDC metadata)         │              │
│   │  2. Extracts "email" claim                              │              │
│   │  3. Maps to ServiceNow user (Email field)               │              │
│   │  4. Returns data based on user's ACLs                   │              │
│   └─────────────────────────────────────────────────────────┘              │
│                                                                             │
│   See: [ServiceNow Setup](servicenow-setup.md)                             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Discovery Engine Authentication Flow

```
+------------------------------------------------------------------+
| STEP 4B: DISCOVERY ENGINE (search_sharepoint tool)                |
+------------------------------------------------------------------+
|                                                                  |
|   Agent decides to search SharePoint documents                    |
|         |                                                        |
|         v                                                        |
|   +----------------------------------------------------------+  |
|   |  search_sharepoint(query, tool_context)                   |  |
|   |                                                           |  |
|   |  1. Extract USER_TOKEN from tool_context.state            |  |
|   |     user_token = tool_context.state.get("USER_TOKEN")     |  |
|   |                                                           |  |
|   |  2. Exchange JWT via WIF/STS                              |  |
|   |     gcp_token = exchange_wif_token(user_token)            |  |
|   |     (Same WIF pool/provider as frontend)                  |  |
|   |                                                           |  |
|   |  3. Call streamAssist with USER's GCP token               |  |
|   |     Authorization: Bearer {user_gcp_token}                |  |
|   +----------------------------------------------------------+  |
|         |                                                        |
|         v                                                        |
|   +----------------------------------------------------------+  |
|   |  Discovery Engine (streamAssist API)                      |  |
|   |                                                           |  |
|   |  - Uses user identity for SharePoint ACL checks           |  |
|   |  - Returns only documents user can access                 |  |
|   |  - Grounded response with source citations                |  |
|   +----------------------------------------------------------+  |
|                                                                  |
|   See: [discovery_engine.py#L73-L117](../agent/tools/discovery_engine.py#L73-L117) |
|                                                                  |
+------------------------------------------------------------------+
```

## Multi-Token Architecture

This system uses **multiple tokens** for different purposes:

| Token | Purpose | Issued By | Validated By |
|-------|---------|-----------|--------------|
| **GCP Access Token (Frontend)** | Authenticate to Agent Engine API | GCP STS (via WIF) | Vertex AI |
| **GCP Access Token (Agent)** | User identity for Discovery Engine | GCP STS (via WIF) | Discovery Engine |
| **Cloud Run ID Token** | Service-to-service auth | Agent Engine SA | Cloud Run IAM |
| **User JWT (Entra)** | User identity for ServiceNow | Entra ID | ServiceNow OIDC |
| **Service Account Token** | Admin operations (datastore discovery) | GCP IAM | Discovery Engine |

### Token Flow Diagram

```
                    +-----------------------------+
                    |     Entra ID JWT            |
                    |  (Original User Token)      |
                    |                             |
                    |  WHO: The logged-in user    |
                    |  STORED: session.state      |
                    +--------------+--------------+
                                   |
          +------------------------+------------------------+
          |                        |                        |
          v                        v                        v
+-------------------+  +---------------------+  +---------------------+
| WIF Exchange #1   |  | WIF Exchange #2     |  | Passed as Header    |
| (Frontend)        |  | (Agent)             |  | (MCP Server)        |
+-------------------+  +---------------------+  +---------------------+
|                   |  |                     |  |                     |
| GCP Token         |  | GCP Token           |  | X-User-Token        |
| -> Agent Engine   |  | -> Discovery Engine |  | -> ServiceNow       |
|                   |  |                     |  |                     |
+-------------------+  +---------------------+  +---------------------+
         |                        |                        |
         v                        v                        v
  [Vertex AI API]      [SharePoint via DE]      [ServiceNow OIDC]
```

## Code References

### Frontend Token Exchange

```typescript
// frontend/src/agentService.ts - Line 8-28
export async function exchangeTokenForGcp(entraIdToken: string): Promise<string> {
  const audience = `//iam.googleapis.com/locations/${gcpConfig.location}/workforcePools/${gcpConfig.workforcePoolId}/providers/${gcpConfig.providerId}`;

  const response = await fetch("https://sts.googleapis.com/v1/token", {
    method: "POST",
    body: new URLSearchParams({
      grant_type: "urn:ietf:params:oauth:grant-type:token-exchange",
      audience: audience,
      subject_token: entraIdToken,
      // ...
    }),
  });
}
```

### Agent Header Provider

```python
# agent/agent.py - Line 36-62
def mcp_header_provider(readonly_context: ReadonlyContext) -> dict[str, str]:
    headers = {"Accept": "application/json"}

    # Cloud Run ID token for service auth
    cloud_run_token = id_token.fetch_id_token(request, MCP_BASE_URL)
    headers["Authorization"] = f"Bearer {cloud_run_token}"

    # User JWT for ServiceNow
    user_token = get_user_token(readonly_context)
    if user_token:
        headers["X-User-Token"] = user_token

    return headers
```

### MCP Server Header Extraction

```python
# mcp-server/mcp_server.py - Line 56-98
def _extract_token_from_context(ctx: Context) -> Optional[str]:
    # SSE transport: headers on request_context.request
    if ctx.request_context:
        request = getattr(ctx.request_context, "request", None)
        if request and hasattr(request, "headers"):
            headers = request.headers

    # Extract X-User-Token
    user_token = headers.get("x-user-token")
    if user_token and user_token.startswith("eyJ"):
        return user_token
```

## Related Documentation

- [Architecture Overview](architecture.md) - System component diagram
- [Discovery Engine Setup](discovery-engine-setup.md) - SharePoint grounding configuration
- [LazyMcpToolset Pattern](lazy-mcp-pattern.md) - Solving pickle serialization
- [GCP Infrastructure Setup](gcp-setup.md) - WIF pool/provider configuration
- [Entra ID Setup](entra-id-setup.md) - App registration details
- [ServiceNow Setup](servicenow-setup.md) - OIDC provider configuration
- [Troubleshooting](troubleshooting.md) - Common issues and solutions
