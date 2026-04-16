# Cortex Retriever

> Agent-only ADK project — no UI, no backend. Deploys to Agent Engine, registers to Gemini Enterprise.

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white)
![ADK](https://img.shields.io/badge/Google_ADK-1.30-4285F4?logo=google&logoColor=white)
![Agent Engine](https://img.shields.io/badge/Agent_Engine-Vertex_AI-34A853?logo=google-cloud&logoColor=white)
![Discovery Engine](https://img.shields.io/badge/Discovery_Engine-StreamAssist-FBBC04?logo=google-cloud&logoColor=black)

Cortex Retriever is a minimal Google ADK agent that searches **internal SharePoint documents** via Discovery Engine and the **public web** via Google Search. It runs inside Gemini Enterprise where users interact with it through the standard chat interface — no custom UI required.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      Gemini Enterprise                          │
│                   (User interacts here)                         │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Agent Engine                               │
│              (Vertex AI Reasoning Engine)                        │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              CortexRetriever (ADK Agent)                  │  │
│  │                  gemini-2.5-flash                         │  │
│  │                                                           │  │
│  │   ┌─────────────────┐    ┌──────────────────────────┐    │  │
│  │   │ search_sharepoint│    │    google_search         │    │  │
│  │   │   (custom tool)  │    │  (ADK built-in tool)     │    │  │
│  │   └────────┬─────────┘    └────────────┬─────────────┘    │  │
│  └────────────┼───────────────────────────┼──────────────────┘  │
│               │                           │                     │
└───────────────┼───────────────────────────┼─────────────────────┘
                │                           │
                ▼                           ▼
┌──────────────────────────┐  ┌──────────────────────────┐
│   Discovery Engine       │  │      Google Search       │
│   StreamAssist API       │  │     (Public Web)         │
│                          │  └──────────────────────────┘
│   ┌──────────────────┐   │
│   │ SharePoint        │   │
│   │ Federated         │   │
│   │ Connector         │   │
│   └────────┬─────────┘   │
└────────────┼─────────────┘
             │
             ▼
┌──────────────────────────┐
│   SharePoint Online      │
│   (User ACLs enforced)   │
└──────────────────────────┘
```

---

## Auth Flow

How a user query in Gemini Enterprise reaches SharePoint with per-user ACLs:

```mermaid
sequenceDiagram
    participant U as User
    participant GE as Gemini Enterprise
    participant AE as Agent Engine<br/>(CortexRetriever)
    participant STS as Google STS
    participant DE as Discovery Engine
    participant SP as SharePoint

    U->>GE: Query + Microsoft login
    GE->>AE: Forward query + Entra JWT in session state
    Note over AE: _detect_auth_id() scans<br/>state for any JWT (eyJ...)
    AE->>STS: Exchange Entra JWT for GCP token
    Note over STS: Workforce Identity Federation<br/>pool + provider validates JWT
    STS-->>AE: GCP access token (user identity)
    AE->>DE: streamAssist(query, dataStoreSpecs)
    Note over DE: Bearer token carries<br/>user identity for ACLs
    DE->>SP: Federated search (per-user access)
    SP-->>DE: Results (only docs user can see)
    DE-->>AE: Grounded answer + source citations
    AE-->>GE: Response with SharePoint references
    GE-->>U: Display answer + clickable sources
```

---

## Step-by-Step Code Walkthrough

### 1. JWT Auto-Detection from Agentspace Session State

When Gemini Enterprise calls the agent, it injects the user's Microsoft JWT into `tool_context.state` using the authorization ID as the key. The agent doesn't need to know the key name — it scans all values for JWT signatures:

```python
# agent/agent.py — _detect_auth_id()

def _detect_auth_id(tool_context: ToolContext) -> tuple[str | None, str | None]:
    state_dict = tool_context.state.to_dict()

    for key, val in state_dict.items():
        if not isinstance(val, str) or len(val) < 100:
            continue
        if val.startswith("eyJ") and "." in val:          # JWT signature
            auth_id = key.removeprefix("temp:")            # strip prefix if present
            return auth_id, val

    return None, None
```

> [!IMPORTANT]
> Agentspace injects tokens with **no consistent prefix** — sometimes `temp:auth_id`, sometimes bare `auth_id`. The `eyJ` + dot + length check catches JWTs regardless of key naming convention. This means you can change the authorization ID freely without touching agent code.

### 2. WIF Token Exchange (Entra JWT → GCP Token)

The Microsoft JWT is exchanged for a GCP access token via Google's Security Token Service. The GCP token carries the user's identity through WIF:

```python
# agent/discovery_engine.py — exchange_wif_token()

def exchange_wif_token(self, microsoft_jwt: str) -> str:
    audience = (
        f"//iam.googleapis.com/locations/global/workforcePools/"
        f"{self.wif_pool_id}/providers/{self.wif_provider_id}"
    )

    payload = {
        "audience": audience,
        "grantType": "urn:ietf:params:oauth:grant-type:token-exchange",
        "requestedTokenType": "urn:ietf:params:oauth:token-type:access_token",
        "scope": "https://www.googleapis.com/auth/cloud-platform",
        "subjectToken": microsoft_jwt,
        "subjectTokenType": "urn:ietf:params:oauth:token-type:jwt",
    }

    response = requests.post(
        "https://sts.googleapis.com/v1/token", json=payload, timeout=10
    )
    return response.json().get("access_token")
```

> [!NOTE]
> If WIF is not configured or the exchange fails, the client falls back to the Agent Engine's service account credentials. This means the agent still works, but searches won't be ACL-aware.

### 3. StreamAssist Search with DataStoreSpecs

The GCP token (now carrying user identity) is used to call Discovery Engine's StreamAssist API. The `dataStoreSpecs` parameter restricts the search to the SharePoint federated connector:

```python
# agent/discovery_engine.py — search()

payload = {"query": {"text": query}}
if datastore_specs:
    payload["toolsSpec"] = {
        "vertexAiSearchSpec": {"dataStoreSpecs": datastore_specs}
    }

response = requests.post(
    f"https://discoveryengine.googleapis.com/v1alpha/"
    f"projects/{self.project_number}/locations/{self.location}/"
    f"collections/default_collection/engines/{self.engine_id}/"
    f"assistants/default_assistant:streamAssist",
    headers={"Authorization": f"Bearer {access_token}", ...},
    json=payload,
)
```

> [!IMPORTANT]
> Without `dataStoreSpecs`, Discovery Engine returns answers from its general model — **not** from SharePoint. There is no error — you just get generic responses with no source citations. This is the most common silent failure.

### 4. Dynamic Datastore Discovery

Instead of hardcoding the full datastore path, the agent first tries to fetch configured datastores from the engine's widget config:

```python
# agent/discovery_engine.py — _get_dynamic_datastores()

url = (
    f"https://discoveryengine.googleapis.com/v1alpha/"
    f"projects/{self.project_number}/locations/{self.location}/"
    f"collections/default_collection/engines/{self.engine_id}/"
    f"widgetConfigs/default_search_widget_config"
)
resp = requests.get(url, headers={"Authorization": f"Bearer {admin_token}", ...})

datastore_specs = []
for comp in resp.json().get("collectionComponents", [{}]):
    for ds_comp in comp.get("dataStoreComponents", []):
        datastore_specs.append({"dataStore": ds_comp["name"]})
```

Falls back to the `DATA_STORE_ID` environment variable if the widget config isn't accessible.

### 5. Google Search (Built-in ADK Tool)

For public web queries, the agent uses ADK's built-in `GoogleSearchTool` — no custom code needed:

```python
# agent/agent.py

from google.adk.tools.google_search_tool import GoogleSearchTool

google_search_tool = GoogleSearchTool(bypass_multi_tools_limit=True)

root_agent = Agent(
    name="CortexRetriever",
    model="gemini-2.5-flash",
    tools=[search_sharepoint, google_search_tool],
)
```

> [!NOTE]
> `bypass_multi_tools_limit=True` is required because ADK doesn't natively support mixing custom tools with built-in tools. This flag makes ADK auto-wrap `google_search` in a sub-agent so both tools work together.

### 6. Agent Registration to Gemini Enterprise

A single script handles OAuth authorization, agent registration, and sharing:

```python
# register.py — register_auth()

payload = {
    "serverSideOauth2": {
        "clientId": OAUTH_CLIENT_ID,
        "clientSecret": OAUTH_CLIENT_SECRET,
        "authorizationUri": auth_uri,   # Microsoft login URL with scopes
        "tokenUri": token_uri,          # Microsoft token endpoint
    },
}
requests.post(
    f"{base_url}/authorizations?authorizationId={AUTH_ID}",
    headers=headers, json=payload,
)

# register.py — register_agent()

payload = {
    "displayName": AGENT_DISPLAY_NAME,
    "adk_agent_definition": {
        "provisioned_reasoning_engine": {
            "reasoning_engine": REASONING_ENGINE_RES
        },
    },
    "authorization_config": {
        "tool_authorizations": [
            f"projects/{PROJECT_NUMBER}/locations/global/authorizations/{AUTH_ID}"
        ]
    },
}
requests.post(
    f"{base_url}/.../assistants/default_assistant/agents",
    headers=headers, json=payload,
)
```

---

## Quick Start

```bash
# 1. Clone and configure
cd cortex-retriever
cp .env.example .env
# Edit .env with your values

# 2. Install dependencies
uv sync

# 3. Test locally (uses service account — no WIF)
uv run python test_local.py

# 4. Deploy to Agent Engine
uv run python deploy.py
# Copy the REASONING_ENGINE_RES output to .env

# 5. Register to Gemini Enterprise + share with everyone
uv run python register.py all
```

After step 5, the agent appears in your Gemini Enterprise instance. Users click the agent, authorize SharePoint access once, then chat.

---

## File Reference

```
cortex-retriever/
├── agent/
│   ├── __init__.py              # Exports root_agent
│   ├── agent.py                 # ADK agent: JWT detection + search_sharepoint tool
│   └── discovery_engine.py      # WIF/STS exchange + StreamAssist API client
├── deploy.py                    # Deploy/update on Vertex AI Agent Engine
├── register.py                  # Register OAuth + agent + share to Agentspace
├── test_local.py                # Local connectivity + agent conversation test
├── .env.example                 # Configuration template
├── pyproject.toml               # Python project (uv)
└── README.md
```

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `PROJECT_ID` | Yes | GCP project hosting Agent Engine |
| `PROJECT_NUMBER` | Yes | Numeric project number |
| `STAGING_BUCKET` | Yes | GCS bucket for Agent Engine artifacts |
| `ENGINE_ID` | Yes | Discovery Engine app ID |
| `DATA_STORE_ID` | Yes | SharePoint federated connector datastore |
| `WIF_POOL_ID` | Yes | Workforce Identity Federation pool |
| `WIF_PROVIDER_ID` | Yes | WIF OIDC provider (must use `api://` audience) |
| `TENANT_ID` | Yes | Microsoft Entra tenant ID |
| `OAUTH_CLIENT_ID` | Yes | Entra app registration client ID |
| `OAUTH_CLIENT_SECRET` | Yes | Entra app client secret |
| `GE_PROJECT_ID` | Yes | Project hosting Gemini Enterprise (can differ from `PROJECT_ID`) |
| `GE_PROJECT_NUMBER` | Yes | Numeric project number for GE project |
| `AS_APP` | Yes | Agentspace app (engine) ID |
| `AUTH_ID` | Yes | Authorization ID for OAuth registration |
| `REASONING_ENGINE_RES` | After deploy | Agent Engine resource name (output of `deploy.py`) |

---

## Key Design Decisions

| Decision | Choice | Why |
|----------|--------|-----|
| No UI | Agent-only, runs inside Gemini Enterprise | Customers already have GE — no need for a separate portal |
| Google Search | ADK built-in `GoogleSearchTool` | Replaces 50+ lines of manual Gemini API + grounding code |
| Tool mixing | `bypass_multi_tools_limit=True` | ADK auto-wraps google_search in a sub-agent |
| JWT detection | Scan all state values for `eyJ` prefix | Zero hardcoded auth IDs — works with any authorization name |
| Dynamic datastores | Fetch from widget config, fallback to env var | Less hardcoding, adapts to connector changes |
| Single registration script | `register.py all` | Consolidates 3 API calls (auth + agent + sharing) into one command |

---

## Prerequisites

<details>
<summary><strong>1. Entra ID App Registration</strong></summary>

The same app registration used for WIF login. Required manifest settings:

```json
{
  "oauth2AllowIdTokenImplicitFlow": true,
  "groupMembershipClaims": "SecurityGroup"
}
```

**Expose an API** with scope `api://{client-id}/user_impersonation`.

**Redirect URIs** must include:
- `https://vertexaisearch.cloud.google.com/oauth-redirect`

</details>

<details>
<summary><strong>2. Workforce Identity Federation (WIF)</strong></summary>

A workforce pool with an OIDC provider pointing to your Entra tenant:

```bash
gcloud iam workforce-pools providers create-oidc YOUR_PROVIDER_ID \
  --workforce-pool=YOUR_POOL_ID \
  --location=global \
  --issuer-uri="https://sts.windows.net/${TENANT_ID}/" \
  --client-id="api://${CLIENT_ID}" \
  --attribute-mapping="google.subject=assertion.sub,google.groups=assertion.groups"
```

> [!IMPORTANT]
> The `--client-id` must use the `api://` prefix. Without it, the STS exchange fails with `invalid_grant: audience does not match`.

**IAM roles** on the WIF pool principal:
- `roles/discoveryengine.viewer` — list datastore IDs
- `roles/discoveryengine.editor` — call StreamAssist
- `roles/serviceusage.serviceUsageConsumer` — API quota

</details>

<details>
<summary><strong>3. Discovery Engine + SharePoint Connector</strong></summary>

- Create a Search App in Discovery Engine
- Add a SharePoint federated connector as a data source
- The connector requires its own Entra app with SharePoint delegated permissions:
  - `Sites.Read.All`, `Sites.Search.All`, `AllSites.Read`, `offline_access`
  - All with admin consent granted

See [`sharepoint_wif_portal/docs/`](../sharepoint_wif_portal/docs/) for detailed setup.

</details>

<details>
<summary><strong>4. Agent Engine IAM</strong></summary>

The Agent Engine service account needs:

```bash
# At project level
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/aiplatform.user"

# At resource level (for the Reasoning Engine)
curl -X POST "https://us-central1-aiplatform.googleapis.com/v1/${REASONING_ENGINE_RES}:setIamPolicy" \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  -d '{"policy":{"bindings":[{"role":"roles/aiplatform.user","members":["serviceAccount:...-compute@..."]}]}}'
```

</details>

---

## Gotchas

| # | Issue | Fix |
|---|-------|-----|
| 1 | Agent returns generic answers with no sources | Missing `dataStoreSpecs` — check `DATA_STORE_ID` is set and the widget config API is accessible |
| 2 | `auth_id=None, token_present=False` in logs | User hasn't authorized SharePoint in GE, or the authorization registration failed |
| 3 | STS returns `invalid_grant` | WIF provider `--client-id` missing `api://` prefix |
| 4 | `FAILED_PRECONDITION` on STS exchange | Entra manifest needs `oauth2AllowIdTokenImplicitFlow: true` |
| 5 | Authorization button in GE stays stuck | Wrong `OAUTH_CLIENT_ID` in `register.py` — must match the Entra app, not the connector app |
| 6 | Agent works locally but not in GE | Agent Engine env vars missing — check `deploy.py` passes all required vars |
| 7 | `sharepointauth2 is used by another agent` | Each agent needs its own `AUTH_ID` — two agents can't share one authorization |

---

## Related Projects

| Project | Relationship |
|---------|-------------|
| [`sharepoint_wif_portal`](../sharepoint_wif_portal/) | Full-stack version with custom React UI + FastAPI backend |
| [`streamassist-oauth-flow`](../streamassist-oauth-flow/) | Custom UI with its own OAuth consent flow (no GE login needed) |
| [`ge-sharepoint-cloudid`](../ge-sharepoint-cloudid/) | Cloud Identity approach (no WIF, uses Google-managed identities) |

---

*Version 1.1.0 — April 2026*
