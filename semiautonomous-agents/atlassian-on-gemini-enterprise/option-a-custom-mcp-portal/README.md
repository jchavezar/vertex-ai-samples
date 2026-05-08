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

Assumed values (substitute yours): project `vtxdemos`, project number `254356041555`, region `us-central1`, GE engine `jira-testing_1778158449701`. Service account `vtxdemos@vtxdemos.iam.gserviceaccount.com` (Owner) — key at `~/.secrets/vtxdemos-sa.json`. Deployment container at `~/vertex-ai-samples/.deployment-container/`.

### 1. Create an Atlassian OAuth 2.0 (3LO) app

`https://developer.atlassian.com/console/myapps/` → **Create** → **OAuth 2.0 integration**.

- **Permissions** → Add **Jira API** → grant `read:jira-work`, `read:jira-user`, `write:jira-work`. (`offline_access` is automatic, not in this list.)
- **Authorization** → Callback URL: `https://vertexaisearch.cloud.google.com/oauth-redirect`. (Add `http://localhost:8765/callback` too if you also want to mint personal tokens locally with `utils/oauth_oneshot.py`.)
- **Settings** → copy `Client ID` and `Secret`.

### 2. Build & deploy the MCP server to Cloud Run

```
PROJECT=vtxdemos
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
GOOGLE_CLOUD_PROJECT=vtxdemos
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_CLOUD_QUOTA_PROJECT=vtxdemos
GOOGLE_GENAI_USE_VERTEXAI=True
MCP_SERVER_URL=https://jira-mcp-server-254356041555.us-central1.run.app/sse
AGENTSPACE_AUTH_ID=jira-mcp-portal-auth
ATLASSIAN_CLIENT_ID=<from step 1>
ATLASSIAN_CLIENT_SECRET=<from step 1>
STAGING_BUCKET=gs://vtxdemos-staging
```

`AGENTSPACE_AUTH_ID` must match the auth resource ID created in step 5.

### 4. Deploy the ADK Agent to Vertex AI Agent Engine

```
cd adk_agent
sudo docker run --rm -v $(pwd):/workspace -w /workspace -v ~/.secrets/vtxdemos-sa.json:/secrets/sa-key.json:ro -e GOOGLE_APPLICATION_CREDENTIALS=/secrets/sa-key.json deployment-container:latest python deploy_agent_engine.py
```

Output ends with the resource name, e.g. `projects/254356041555/locations/us-central1/reasoningEngines/<RE_ID>`. Copy `<RE_ID>` for the next step.

### 5. Register the Atlassian OAuth + agent in Gemini Enterprise

Edit the constants at the top of `register.py` (or set them in `.env`):

```
GE_PROJECT_ID=vtxdemos
GE_PROJECT_NUMBER=254356041555
AS_APP=jira-testing_1778158449701
REASONING_ENGINE_RES=projects/254356041555/locations/us-central1/reasoningEngines/<RE_ID from step 4>
AGENTSPACE_AUTH_ID=jira-mcp-portal-auth   # MUST match adk_agent/.env
```

Run:

```
cd ..
sudo docker run --rm -v $(pwd):/workspace -w /workspace -v ~/.secrets/vtxdemos-sa.json:/secrets/sa-key.json:ro -e GOOGLE_APPLICATION_CREDENTIALS=/secrets/sa-key.json deployment-container:latest python register.py all
```

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
gcloud run services delete jira-mcp-server --region=us-central1 --project=vtxdemos --quiet
curl -X DELETE -H "Authorization: Bearer $(gcloud auth print-access-token)" -H "x-goog-user-project: vtxdemos" "https://us-central1-aiplatform.googleapis.com/v1beta1/projects/254356041555/locations/us-central1/reasoningEngines/<RE_ID>?force=true"
curl -X DELETE -H "Authorization: Bearer $(gcloud auth print-access-token)" -H "x-goog-user-project: vtxdemos" "https://discoveryengine.googleapis.com/v1alpha/projects/254356041555/locations/global/collections/default_collection/engines/jira-testing_1778158449701/assistants/default_assistant/agents/<AGENT_ID>"
curl -X DELETE -H "Authorization: Bearer $(gcloud auth print-access-token)" -H "x-goog-user-project: vtxdemos" "https://discoveryengine.googleapis.com/v1alpha/projects/254356041555/locations/global/authorizations/jira-mcp-portal-auth"
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
