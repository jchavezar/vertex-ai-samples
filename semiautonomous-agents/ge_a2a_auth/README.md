# ge_a2a_auth

Bridge a **Gemini Enterprise** chat surface to an **ADK agent on Vertex AI Agent Runtime** through the **Custom-A2A** registration path, gated by an OAuth2 Authorization with the Google IdP.

```
GE chat
  └─ OAuth2 consent (Google IdP, cloud-platform scope)
       └─ Authorization: Bearer ya29.<user_token>
            └─ {LOCATION}-aiplatform.googleapis.com/.../reasoningEngines/{ID}/a2a
                 └─ A2aAgent → ADK Runner → LlmAgent(gemini-2.5-flash, google_search)
```

The agent answers with Google Search grounding and exposes a `whoami` skill that dumps the JWT claims the container actually receives.

> **Identity note.** GE's OAuth gate proves the caller holds a Google account and `aiplatform.user` on the engine. The Vertex AI proxy then re-signs the call as the Agent Runtime service account before it reaches the container — the *original* user OAuth token does not transit. So tools inside the agent call Google APIs as the SA, not as the end user. The `whoami` skill is the proof.

## Prereqs

- A Google Cloud project, a GCS bucket, and a Gemini Enterprise app (Engine ID).
- `gcloud`, `python>=3.11`, `uv` (or pip+venv) on your shell.
- ADC available locally (e.g. `gcloud auth application-default login` or a SA key).

## Variables

Copy `.env.example` to `.env` and fill these:

```
PROJECT_ID=<gcp-project-id>
PROJECT_NUMBER=<gcp-project-number>
LOCATION=us-central1
STORAGE_BUCKET=gs://<your-bucket>
GEMINI_ENTERPRISE_APP_ID=<ge-engine-id, e.g. jira-testing_1778158449701>
```

`OAUTH_*`, `AGENT_AUTHORIZATION`, `REASONING_ENGINE_ID`, `A2A_URL` are filled in by the steps below.

## Steps

### 1. Enable APIs

```bash
gcloud services enable aiplatform.googleapis.com discoveryengine.googleapis.com --project=${PROJECT_ID}
```

### 2. Install deps

```bash
cd semiautonomous-agents/ge_a2a_auth
uv venv && source .venv/bin/activate
uv pip install -r agent/requirements.txt python-dotenv httpx requests
```

### 3. Deploy the agent to Agent Runtime

```bash
python deploy.py
```

Writes `REASONING_ENGINE_ID` and `A2A_URL` back into `.env`, and saves `agent_card.json` (consumed by step 6). First deploy takes ~5 min.

### 4. Smoke-test the A2A endpoint with your ADC

```bash
python test_a2a.py
```

Expect a 200 with the agent's reply. This proves any Google bearer with `cloud-platform` scope reaches the agent — which is exactly what GE will do post-OAuth.

### 5. Create the OAuth2 client (one-time, UI)

`gcloud` cannot create web OAuth clients. In the Console:

1. Open `https://console.cloud.google.com/apis/credentials?project=${PROJECT_ID}` → **+ CREATE CREDENTIALS → OAuth client ID**.
2. **Application type:** Web application. Name: `ge-a2a-auth`.
3. **Authorized redirect URIs** — add both:
   - `https://vertexaisearch.cloud.google.com/oauth-redirect`
   - `https://discoveryengine.googleapis.com/v1alpha/authorizations/oauthredirect`
4. Create, then paste the client id/secret into `.env`:

```
OAUTH_CLIENT_ID=...
OAUTH_CLIENT_SECRET=...
```

5. On the OAuth consent screen, make sure the app is **Internal** (or Published) and lists scope `https://www.googleapis.com/auth/cloud-platform`.

### 6. Create the GE Authorization resource

```bash
python create_authorization.py
```

Then **manually edit `.env`** so `AGENT_AUTHORIZATION` uses the **project number** form (GE rejects the project-id form):

```
AGENT_AUTHORIZATION=projects/${PROJECT_NUMBER}/locations/global/authorizations/ge-a2a-auth-oauth
```

### 7. Register the agent in GE

```bash
python register_ge_agent.py
```

Posts to `discoveryengine.googleapis.com/v1alpha/.../assistants/default_assistant/agents` with the agent card and the Authorization resource. Records the agent ID in `register.log`.

### 8. Use it

Open `https://console.cloud.google.com/gemini-enterprise/locations/global/engines/${GEMINI_ENTERPRISE_APP_ID}/agentic/agents?project=${PROJECT_ID}` → pick **GE A2A Auth Diagnostic** → first prompt triggers the OAuth consent screen.

Try:
- `whoami` → dumps the JWT claims (you'll see `sub=<SA-numeric-id>` because the proxy re-signs).
- `What was the last major Vertex AI release?` → Google-Search-grounded answer.

## Iteration

After editing `agent/agent.py` or `agent/agent_executor.py`:

```bash
python update.py
```

This re-deploys in place against the same `REASONING_ENGINE_ID` (~2 min, no new resource).

## Layout

```
agent/
  agent.py            LlmAgent + google_search + whoami instruction template
  agent_executor.py   A2A → ADK bridge; decodes the inbound JWT into session state
  requirements.txt    Pinned: a2a-sdk==0.3.26 (matches vertexai's A2aAgent template)
deploy.py             Creates the ReasoningEngine, saves agent_card.json
update.py             In-place re-deploy
create_authorization.py
register_ge_agent.py
test_a2a.py           Direct REST round-trip using ADC
```

## Gotchas

- `agent_card.url` must be the **public** `{region}-aiplatform.googleapis.com/v1beta1/.../a2a` URL — `deploy.py` overwrites whatever the SDK fills in.
- `GEMINI_ENTERPRISE_APP_ID` engine must be in `global`. Agent Runtime can be regional.
- `AGENT_AUTHORIZATION` must use `projects/${PROJECT_NUMBER}/...`, not the id.
- The A2A wire is **proto JSON** (`request.message_id`, `request.content[].text`, `ROLE_USER`), not the pydantic camelCase of a2a-sdk's internal types. See `test_a2a.py`.
- vertexai SDK 1.153.x has a version skew: the `A2aAgent` template imports `TransportProtocol` (only in a2a-sdk 0.x) while the deploy path calls `MessageToDict` (proto-only). `deploy.py` monkey-patches `MessageToDict` to fall back to `.model_dump()` for pydantic models, and pins `a2a-sdk==0.3.26`.
