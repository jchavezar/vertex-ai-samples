# Setup — Amgen Science Search Portal

Bring up a fresh clone of the portal against the **existing** Amgen demo infrastructure (Discovery Engine, SharePoint connector, WIF pool, Entra apps — all reused from `sharepoint_wif_portal`).

> Doing a from-scratch infra build (new GCP project, new Entra app reg, new WIF pool, new SharePoint connector)? Use the original phased docs at [`../../sharepoint_wif_portal/docs/`](../../sharepoint_wif_portal/docs/) — `01-SETUP-GCP.md` through `04-SETUP-DISCOVERY.md`. They are intentionally not duplicated here.

---

## Prerequisites

- Python 3.12+, [`uv`](https://github.com/astral-sh/uv), Node 18+
- `gcloud` CLI authenticated (`gcloud auth login` + `gcloud auth application-default login`)
- IAM access to GCP project `sharepoint-wif-agent` (number `545964020693`) — minimum: `roles/discoveryengine.editor` on the WIF principalSet, `roles/aiplatform.user` for Agent Engine
- An Entra account in tenant `de46a3fd-0d68-4b25-8343-6eb5d71afce9` (e.g. `admin@sockcop.onmicrosoft.com`) that has consented to the Connector App once

Full identifier list: [`SECURITY_FLOW.md` §7](SECURITY_FLOW.md#7-reference-the-actual-identifiers).

---

## 1. Configure environment

```bash
cp .env.example .env
cp frontend/.env.example frontend/.env
```

Fill `.env` from `SECURITY_FLOW.md` §7 — at minimum:

```env
PROJECT_ID=sharepoint-wif-agent
PROJECT_NUMBER=545964020693
LOCATION=us-central1
ENGINE_ID=gemini-enterprise
WIF_POOL_ID=sp-wif-pool-v2
WIF_PROVIDER_ID=entra-provider
TENANT_ID=de46a3fd-0d68-4b25-8343-6eb5d71afce9
OAUTH_CLIENT_ID=7868d053-cf9c-4848-be5a-f9bbf8279234
OAUTH_CLIENT_SECRET=<secret-manager>
GOOGLE_GENAI_USE_VERTEXAI=True
GOOGLE_CLOUD_PROJECT=sharepoint-wif-agent
GOOGLE_CLOUD_LOCATION=us-central1
# REASONING_ENGINE_RES — set after step 4
```

Fill `frontend/.env`:

```env
VITE_CLIENT_ID=7868d053-cf9c-4848-be5a-f9bbf8279234
VITE_TENANT_ID=de46a3fd-0d68-4b25-8343-6eb5d71afce9
```

---

## 2. Run the backend

```bash
cd backend
uv sync
uv run uvicorn main:app --reload --port 8001
```

Verify:

```bash
curl http://localhost:8001/health        # → {"status":"healthy", ...}
curl http://localhost:8001/api/config    # → echoes non-sensitive env
```

---

## 3. Run the frontend

```bash
cd frontend
npm install
npm run dev          # → http://localhost:5173
```

Sign in with your Microsoft account (MSAL popup) → run a query like *"What is AIMOVIG?"* → expect citations from SharePoint. If you get an answer with **zero source chips**, see the failure-mode table in the [README](../README.md#how-auth-actually-works-read-this-first) or [`SECURITY_FLOW.md` §6](SECURITY_FLOW.md#6-common-failure-modes-and-what-they-mean).

---

## 4. (Optional) Deploy / redeploy the agent

Only needed if you change `agent/agent.py` or `agent/discovery_engine.py`.

```bash
uv run python test_local.py     # smoke-test the ADK agent locally
uv run python deploy.py         # deploy to Vertex AI Agent Engine
# → copy reasoningEngines/<id> into REASONING_ENGINE_RES in .env
uv run python test_remote.py    # smoke-test the deployed agent
```

Then register it into Agentspace (so it shows up in the GE UI):

```bash
./scripts/register_auth.sh      # one-time per Agentspace app
./scripts/register_agent.sh
```

The current deployed agent: `projects/545964020693/locations/us-central1/reasoningEngines/1988251824309665792` (`AmgenScienceSearch`).

---

## 5. (Optional) Cloud Run

For the Amgen subdomain deployment (Cloud Run + Global LB + IAP), follow the original at [`../../sharepoint_wif_portal/docs/10-CLOUD-DEPLOYMENT.md`](../../sharepoint_wif_portal/docs/10-CLOUD-DEPLOYMENT.md). Only the env vars and image name change for the Amgen rebrand — the GLB, IAP, and backend service can be reused if you're deploying to the same project.

---

## Troubleshooting

<details>
<summary><b>Quick failure-mode table</b></summary>

| Issue | Fix |
|---|---|
| CORS error in browser | Backend not on `:8001`; restart `uvicorn` |
| `audience does not match` from STS | Wrong WIF provider — portal/agent use `entra-provider` (audience `api://<client-id>`); GE login uses `ge-login-provider` (bare client-id) |
| Answer with no citations | Wrong request body shape — must use `query.parts[]` + `assistSkippingMode: REQUEST_ASSIST` + explicit `dataStoreSpecs` |
| `acquireAccessToken` 404 | User has not yet consented to the SharePoint Connector App; run the OAuth consent flow once |
| `invalid_grant: ID Token is stale` from STS | Re-authenticate in the portal; Entra JWT too old |
| `aiplatform.reasoningEngines.get` 403 | Caller lacks the role; set `quota_project_id` on credentials, don't mutate global ADC |
| Docs missing from `/sites/<X>` | `/sites/<X>` not in connector's `admin_filter.Site`; PATCH the connector |

Full table with root causes: [`SECURITY_FLOW.md` §6](SECURITY_FLOW.md#6-common-failure-modes-and-what-they-mean).

</details>

<details>
<summary><b>Debug logging</b></summary>

```bash
LOG_LEVEL=DEBUG uv run uvicorn main:app --reload --port 8001
# Watch for:
#   [Search] Using 5 datastore(s)
#   [Search] Calling StreamAssist API: https://discoveryengine.googleapis.com/v1alpha/...
#   [Search] Found N source(s)
```

`Found 0 source(s)` with a non-empty answer = you are reading model training data, not SharePoint. Re-check the request body shape.

</details>
