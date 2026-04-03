# Gemini Enterprise Integration

> **Navigation**: [README](../README.md) | [Overview](01-OVERVIEW.md) | [Entra ID](02-ENTRA-ID-SETUP.md) | [WIF](03-WIF-SETUP.md) | [Local Testing](04-LOCAL-TESTING.md) | [Agent Engine](05-AGENT-ENGINE.md) | **GE Setup**

## Working Configuration Reference

| Setting | Value |
|---------|-------|
| AUTH_ID | `sharepointauth2` |
| PROJECT_NUMBER | `440133963879` |
| AS_APP (Agentspace App) | `deloitte-demo` |
| REASONING_ENGINE_RES | `projects/440133963879/locations/us-central1/reasoningEngines/5291219938520858624` |
| AGENT_ID | `583348556074317003` |

---

## Token Flow

```
User in Gemini Enterprise
    ↓
OAuth Consent (Microsoft Entra ID)
    ↓
Agentspace stores token at: session.state["{AUTH_ID}"]
    ↓
ADK Agent extracts token from: tool_context.state["{AUTH_ID}"]
    ↓
WIF Exchange: Microsoft JWT → GCP Access Token
    ↓
Discovery Engine API with user identity
    ↓
Grounded response with SharePoint sources
```

---

## Step 1: Register Authorization

Creates the OAuth config that tells Gemini Enterprise how to authenticate with Microsoft.

**CRITICAL**: Include `offline_access` scope (for refresh tokens) AND your custom API scope.

```bash
export PROJECT_NUMBER="440133963879"
export AUTH_ID="sharepointauth2"
export OAUTH_CLIENT_ID="ecbfa47e-a75c-403c-a13b-f27eff101e4e"
export OAUTH_CLIENT_SECRET="your-client-secret"
export TENANT_ID="de46a3fd-0d68-4b25-8343-6eb5d71afce9"

export OAUTH_TOKEN_URI="https://login.microsoftonline.com/${TENANT_ID}/oauth2/v2.0/token"
export OAUTH_AUTH_URI="https://login.microsoftonline.com/${TENANT_ID}/oauth2/v2.0/authorize?response_type=code&client_id=${OAUTH_CLIENT_ID}&redirect_uri=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Foauth-redirect&scope=openid%20profile%20email%20offline_access%20api%3A%2F%2F${OAUTH_CLIENT_ID}%2Fuser_impersonation&prompt=consent"

curl -X POST \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  -H "Content-Type: application/json" \
  -H "X-Goog-User-Project: ${PROJECT_NUMBER}" \
  "https://discoveryengine.googleapis.com/v1alpha/projects/${PROJECT_NUMBER}/locations/global/authorizations?authorizationId=${AUTH_ID}" \
  -d '{
    "name": "projects/'"${PROJECT_NUMBER}"'/locations/global/authorizations/'"${AUTH_ID}"'",
    "serverSideOauth2": {
      "clientId": "'"${OAUTH_CLIENT_ID}"'",
      "clientSecret": "'"${OAUTH_CLIENT_SECRET}"'",
      "authorizationUri": "'"${OAUTH_AUTH_URI}"'",
      "tokenUri": "'"${OAUTH_TOKEN_URI}"'"
    }
  }'
```

**Scope breakdown**:
| Scope | Purpose |
|-------|---------|
| `openid profile email` | Standard OIDC claims |
| `offline_access` | Get refresh token (required!) |
| `api://{client-id}/user_impersonation` | Custom scope for WIF-compatible audience |

---

## Step 2: Register Agent

**IMPORTANT**: Use `authorization_config.tool_authorizations` (NOT `adk_agent_definition.authorizations`).

```bash
export PROJECT_ID="deloitte-plantas"
export PROJECT_NUMBER="440133963879"
export AS_APP="deloitte-demo"
export AUTH_ID="sharepointauth2"
export REASONING_ENGINE_RES="projects/440133963879/locations/us-central1/reasoningEngines/5291219938520858624"

curl -X POST \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  -H "Content-Type: application/json" \
  -H "x-goog-user-project: ${PROJECT_ID}" \
  "https://discoveryengine.googleapis.com/v1alpha/projects/${PROJECT_NUMBER}/locations/global/collections/default_collection/engines/${AS_APP}/assistants/default_assistant/agents" \
  -d '{
    "displayName": "SharePoint Assistant",
    "description": "AI Assistant with access to SharePoint documents",
    "icon": {
      "uri": "https://upload.wikimedia.org/wikipedia/commons/e/e1/Microsoft_Office_SharePoint_%282019%E2%80%93present%29.svg"
    },
    "adk_agent_definition": {
      "tool_settings": {
        "tool_description": "Use this agent to search SharePoint documents. Always call search_sharepoint for any question."
      },
      "provisioned_reasoning_engine": {
        "reasoning_engine": "'"${REASONING_ENGINE_RES}"'"
      }
    },
    "authorization_config": {
      "tool_authorizations": [
        "projects/'"${PROJECT_NUMBER}"'/locations/global/authorizations/'"${AUTH_ID}"'"
      ]
    }
  }'
```

**Save the agent ID** from response (e.g., `583348556074317003`)

---

## Step 3: Share Agent with Users

By default, agents are not visible. Share with all users:

```bash
export AGENT_RESOURCE_NAME="projects/${PROJECT_NUMBER}/locations/global/collections/default_collection/engines/${AS_APP}/assistants/default_assistant/agents/AGENT_ID"

curl -X PATCH \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  -H "Content-Type: application/json" \
  -H "X-Goog-User-Project: ${PROJECT_ID}" \
  "https://discoveryengine.googleapis.com/v1alpha/${AGENT_RESOURCE_NAME}?updateMask=sharingConfig" \
  -d '{
    "sharingConfig": {
      "scope": "ALL_USERS"
    }
  }'
```

---

## Step 4: Update Authorization Link (if needed)

To link/unlink authorization from existing agent:

```bash
curl -X PATCH \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  -H "Content-Type: application/json" \
  -H "X-Goog-User-Project: ${PROJECT_ID}" \
  "https://discoveryengine.googleapis.com/v1alpha/projects/${PROJECT_NUMBER}/locations/global/collections/default_collection/engines/${AS_APP}/assistants/default_assistant/agents/${AGENT_ID}?updateMask=authorizationConfig" \
  -d '{
    "authorizationConfig": {
      "toolAuthorizations": [
        "projects/'"${PROJECT_NUMBER}"'/locations/global/authorizations/'"${AUTH_ID}"'"
      ]
    }
  }'
```

---

## Verification Commands

### List Agents
```bash
curl -s -X GET \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  -H "X-Goog-User-Project: ${PROJECT_ID}" \
  "https://discoveryengine.googleapis.com/v1alpha/projects/${PROJECT_NUMBER}/locations/global/collections/default_collection/engines/${AS_APP}/assistants/default_assistant/agents" | jq .
```

### List Authorizations
```bash
curl -s -X GET \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  -H "X-Goog-User-Project: ${PROJECT_ID}" \
  "https://discoveryengine.googleapis.com/v1alpha/projects/${PROJECT_NUMBER}/locations/global/authorizations" | jq .
```

### Check Agent Logs
```bash
gcloud logging read 'resource.type="aiplatform.googleapis.com/ReasoningEngine" resource.labels.reasoning_engine_id="5291219938520858624" textPayload:("TOKEN" OR "WIF")' \
  --project=deloitte-plantas \
  --limit=20 \
  --format='value(textPayload)'
```

---

## Delete Commands

### Delete Agent
```bash
curl -X DELETE \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  -H "X-Goog-User-Project: ${PROJECT_ID}" \
  "https://discoveryengine.googleapis.com/v1alpha/projects/${PROJECT_NUMBER}/locations/global/collections/default_collection/engines/${AS_APP}/assistants/default_assistant/agents/${AGENT_ID}"
```

### Delete Authorization (must unlink first)
```bash
# First unlink from agent (set empty toolAuthorizations)
# Then delete:
curl -X DELETE \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  -H "X-Goog-User-Project: ${PROJECT_ID}" \
  "https://discoveryengine.googleapis.com/v1alpha/projects/${PROJECT_NUMBER}/locations/global/authorizations/${AUTH_ID}"
```

---

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| OAuth popup shows then fails | Missing `offline_access` scope | Recreate authorization with scope |
| "Refresh token not found" | Using SPA platform in Entra ID | Add Web platform |
| Token not passed to agent | AUTH_ID mismatch | Ensure agent code AUTH_ID matches |
| Agent not visible | Not shared | Run share command with ALL_USERS |
| GE login fails after agent works | Single WIF provider | Create two providers (see below) |
| "audience does not match" on login | WIF has `api://` prefix | Use login provider without prefix |
| "audience does not match" on agent | WIF missing `api://` prefix | Use agent provider with prefix |

### Two WIF Providers Required

| Provider | Client ID | Purpose |
|----------|-----------|---------|
| `entra-id-oidc-pool-provider-de` | `ecbfa47e-...` | GE login |
| `entra-id-agent-provider` | `api://ecbfa47e-...` | Agent WIF |

Agent `.env` must use: `WIF_PROVIDER_ID=entra-id-agent-provider`
