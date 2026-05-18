# Option A — Custom MCP Portal (your code, your agent)

You run the MCP server, you run the agent (Vertex AI Agent Engine + ADK), Gemini Enterprise just routes chats to it. Maximum control, maximum customisation.

See the [parent README](../README.md) for the comparison vs Option B (direct remote MCP).
For the deep dive on context-bounded pagination, see [PAGINATION.md](./PAGINATION.md).

---

## Architecture

```
                        ┌──────────────────────────┐
   user in GE chat ───▶ │  Gemini Enterprise app   │
                        │  (jira-testing engine)   │
                        └────────────┬─────────────┘
                                     │  routes to registered agent
                                     ▼
                        ┌──────────────────────────┐
                        │  Vertex AI Agent Engine  │  ◀── deploy_agent_engine.py
                        │  (ADK, gemini-3-flash)   │
                        │  ─ before_model_callback │  (PAGINATION.md)
                        │  ─ thinking_config       │
                        └────────────┬─────────────┘
                                     │  MCP/SSE + Authorization: Bearer <jira-oauth>
                                     ▼
                        ┌──────────────────────────┐
                        │  Cloud Run MCP server    │  ◀── jira_server/Dockerfile
                        │  (FastAPI + atlassian-py)│
                        │  Multi-tenant per-token  │
                        └────────────┬─────────────┘
                                     │  api.atlassian.com/ex/jira/{cloudId}
                                     ▼
                              Atlassian Cloud
```

OAuth: Gemini Enterprise drives an Atlassian 3LO popup the first time a user asks the agent a question (server-side OAuth, registered in Discovery Engine via `register.py`). The token is injected into the ADK session state and the agent passes it to the MCP server in the `Authorization` header.

---

## Project layout

```
option-a-custom-mcp-portal/
├── README.md                       ← you are here
├── PAGINATION.md                   ← context-bounding callback explained
├── register.py                     ← registers Atlassian OAuth + agent in GE
├── adk_agent/
│   ├── agent.py                    ← ADK Agent + before_model_callback
│   ├── deploy_agent_engine.py      ← create/update the Agent Engine
│   ├── requirements.txt
│   ├── .env                        ← project / region / OAuth client id+secret
│   └── .atlassian_token            ← (optional) personal token for local test
├── jira_server/
│   ├── server.py                   ← MCP server (FastAPI + SSE)
│   ├── Dockerfile
│   ├── requirements.txt
│   └── start_server.sh             ← local-dev runner
└── utils/
    ├── oauth_oneshot.py            ← one-shot OAuth flow → ATLASSIAN_OAUTH_TOKEN
    └── get_access_token.py         ← original tkinter version
```

---

## Step-by-step setup

**Replace these placeholders with your values:**
- `YOUR_PROJECT_ID` - Your Google Cloud project ID
- `YOUR_PROJECT_NUMBER` - Your project number (get via: `gcloud projects describe YOUR_PROJECT_ID --format="value(projectNumber)"`)
- `YOUR_GE_ENGINE_ID` - Your Gemini Enterprise engine ID
- Region: `us-central1` (or your preferred region)

### 1. Create an Atlassian OAuth 2.0 (3LO) app

`https://developer.atlassian.com/console/myapps/` → **Create** → **OAuth 2.0 integration**.

- **Permissions** → Add **Jira API** → grant `read:jira-work`, `read:jira-user`, `write:jira-work`. (`offline_access` is automatic, not in this list.)
- **Authorization** → Callback URL: `https://vertexaisearch.cloud.google.com/oauth-redirect`. (Add `http://localhost:8765/callback` too if you also want to mint personal tokens locally with `utils/oauth_oneshot.py`.)
- **Settings** → copy `Client ID` and `Secret`.

### 2. Build & deploy the MCP server to Cloud Run

```
PROJECT=YOUR_PROJECT_ID
REGION=us-central1
IMAGE=us-central1-docker.pkg.dev/$PROJECT/cloud-run-source-deploy/jira-mcp-server:latest
cd jira_server
gcloud builds submit --tag $IMAGE --project=$PROJECT --region=$REGION
gcloud run deploy jira-mcp-server --image=$IMAGE --region=$REGION --project=$PROJECT --allow-unauthenticated --port=8080 --memory=1Gi --cpu=2 --timeout=600 --max-instances=5
```

The server is multi-tenant — it reads the per-request `Authorization: Bearer <token>` header and uses that token to call Jira. No secret to embed at deploy time. (If your org policy forbids `--allow-unauthenticated`, deploy private and grant `roles/run.invoker` to the Agent Engine service accounts; you'll also need to add a Cloud Run ID-token auth path in the agent.)

Note the service URL — typically `https://jira-mcp-server-<project_number>.us-central1.run.app`.

### 3. Configure `adk_agent/.env`

```
GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_CLOUD_QUOTA_PROJECT=YOUR_PROJECT_ID
GOOGLE_GENAI_USE_VERTEXAI=True
MCP_SERVER_URL=https://jira-mcp-server-YOUR_PROJECT_NUMBER.us-central1.run.app/sse
AGENTSPACE_AUTH_ID=jira-mcp-portal-auth
ATLASSIAN_CLIENT_ID=<from step 1>
ATLASSIAN_CLIENT_SECRET=<from step 1>
STAGING_BUCKET=gs://YOUR_PROJECT_ID-staging
```

`AGENTSPACE_AUTH_ID` must match the auth resource ID created in step 5.

### 4. Deploy the ADK Agent to Vertex AI Agent Engine

```bash
cd adk_agent
python deploy_agent_engine.py
```

**Save the Reasoning Engine ID** from the output (e.g., `1234567890123456789`).

### 5. Register in Gemini Enterprise

```bash
cd ..
python register.py agent
```

**When prompted, enter:**
- Reasoning Engine ID (from Step 4)
- Atlassian Client ID (from Step 1)
- Atlassian Client Secret (from Step 1)

This does three things:

1. **`register_auth`** — creates a Discovery Engine `Authorization` resource pointing at Atlassian's OAuth endpoints with your client credentials.
2. **`register_agent`** — registers your reasoning engine as a GE agent under the `jira-testing` engine, wiring `authorization_config.tool_authorizations` to that auth resource. This is what triggers the consent popup on first user request.
3. **`share_agent`** — sets sharing scope to `ALL_USERS` so the agent shows up in everyone's picker.

### 6. Test in the GE web UI

1. Open the GE app `jira-testing` in the cloud console.
2. Pick **"Jira MCP Portal"** in the agent picker.
3. Ask "List 5 Jira issues created this week."
4. Atlassian consent popup → log in → choose your Jira site → accept.
5. Answer comes back with issue keys as clickable Markdown links.

### 7. (Optional) Local end-to-end test

Without going through GE — useful while iterating on `agent.py`:

```
cd utils
python3 oauth_oneshot.py     # opens a browser, mints a token, saves to adk_agent/.atlassian_token
cd ../adk_agent
python3 agent.py             # interactive REPL against the deployed Cloud Run MCP
```

The agent loads `.atlassian_token` (when present) as the `ATLASSIAN_OAUTH_TOKEN` env-var fallback used by `get_access_token` in `agent.py`.

### 8. (Optional) Register MCP Server in Agent Registry

**Why:** Enables Agent Gateway governance, IAP enforcement, and cross-agent reuse.

**Not required** for the agent to work - this adds enterprise governance capabilities.

```bash
export MCP_SERVER_URL=https://jira-mcp-server-YOUR_PROJECT_NUMBER.us-central1.run.app
export GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID
export GOOGLE_CLOUD_LOCATION=us-central1
export MCP_SERVICE_DISPLAY_NAME=jira-mcp

python register_mcp_in_registry.py
```

Saves the registry resource name to add to your `.env`:
```
MCP_SERVICE_RESOURCE=projects/YOUR_PROJECT_NUMBER/locations/us-central1/services/jira-mcp
```

**Benefits:**
- **Agent Gateway:** Enforce IAP/VPC-SC on MCP calls (requires gateway setup - see `agent-gateway-demo` project)
- **Discoverability:** Other agents can find and reuse this MCP server
- **Audit:** Centralized logging of all MCP tool calls

**Trade-off:** Adds governance overhead. Only use if you need multi-agent orchestration or compliance controls.

For full Agent Gateway setup (IAP egressor, auth manager, DPoP), see: `semiautonomous-agents/agent-gateway-demo/`

---

## How OAuth is wired (one-paragraph mental model)

The Discovery Engine `authorizations/jira-mcp-portal-auth` resource holds your Atlassian client_id/secret + auth and token URLs. When a user first asks the agent a question, GE sees `authorization_config.tool_authorizations` on the agent registration, checks if that user has a valid token for that auth resource, and if not opens the popup. After consent it stores the token and injects it into the ADK session state under a key prefixed with the auth ID. The agent's `get_access_token()` (in `agent.py`) finds it (auto-detects the prefix or scans for JWT-shaped strings) and `mcp_header_provider()` puts it into the MCP request as `Authorization: Bearer <token>`. The MCP server's `AuthMiddleware` extracts it and calls Jira on behalf of that user — fully multi-tenant, ACL-aware.

---

## Updating the agent later

Edit `adk_agent/agent.py` → re-run step 4 (the script does an in-place update of the same display name). No need to re-register on the GE side.

Edit the MCP server (`jira_server/`) → re-run step 2 (Cloud Run accepts a new revision; the agent picks it up immediately, no AE redeploy needed).

Change OAuth scopes / endpoints → re-run `register.py auth` to PATCH the auth resource. New users get the new flow on first use.

---

## Cleanup

```
gcloud run services delete jira-mcp-server --region=us-central1 --project=YOUR_PROJECT_ID --quiet
curl -X DELETE -H "Authorization: Bearer $(gcloud auth print-access-token)" -H "x-goog-user-project: YOUR_PROJECT_ID" "https://us-central1-aiplatform.googleapis.com/v1beta1/projects/YOUR_PROJECT_NUMBER/locations/us-central1/reasoningEngines/<RE_ID>?force=true"
curl -X DELETE -H "Authorization: Bearer $(gcloud auth print-access-token)" -H "x-goog-user-project: YOUR_PROJECT_ID" "https://discoveryengine.googleapis.com/v1alpha/projects/YOUR_PROJECT_NUMBER/locations/global/collections/default_collection/engines/YOUR_GE_ENGINE_ID/assistants/default_assistant/agents/<AGENT_ID>"
curl -X DELETE -H "Authorization: Bearer $(gcloud auth print-access-token)" -H "x-goog-user-project: YOUR_PROJECT_ID" "https://discoveryengine.googleapis.com/v1alpha/projects/YOUR_PROJECT_NUMBER/locations/global/authorizations/jira-mcp-portal-auth"
```

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Empty answer, `state: SUCCEEDED`, no popup | Both `auth_scheme` on MCPToolset AND `tool_authorizations` on agent — they conflict | Remove `auth_scheme`/`auth_credential` from MCPToolset (this repo already does this) |
| `'MCPSessionManager' object has no attribute '_session_lock'` | `google-adk` < 1.32 has a runtime bug | Pin `google-adk>=1.32.0` in `adk_agent/requirements.txt` |
| `429 RESOURCE_EXHAUSTED` after a few pagination pages | Per-minute Gemini TPM exhausted by replayed tool history | See [PAGINATION.md](./PAGINATION.md) — `before_model_callback` is the fix |
| Generic LLM answer instead of Jira data ("here are 5 dog training issues") | Tools didn't load (check AE error logs) — agent fell back to base-model knowledge | Tail `gcloud logging read 'resource.type="aiplatform.googleapis.com/ReasoningEngine"' ...` |
| `invalid_client` from Atlassian | You used DCR (`cf.mcp.atlassian.com/v1/register`) credentials with `auth.atlassian.com` URLs | Option A uses standard developer.atlassian.com creds with `auth.atlassian.com` URLs. DCR is for Option B only |
| `404 Publisher Model gemini-3-flash-preview not found` in `us-central1` | Preview models are not provisioned in every region — `gemini-3-flash-preview` is `global`-only as of 2026-05 | `agent.py` overrides `os.environ["GOOGLE_CLOUD_LOCATION"] = "global"` after `load_dotenv` so the model client hits the global endpoint. The AE itself stays in `us-central1`; the deploy script's later `load_dotenv(override=True)` restores `us-central1` for the Agent Engine create/update API. |
