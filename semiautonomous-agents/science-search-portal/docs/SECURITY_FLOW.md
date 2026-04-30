# Security & Authorization Flow — Amgen Science Search Portal

End-to-end explanation of how a single `streamAssist` request reaches Microsoft SharePoint with per-user ACL enforcement, traversing Microsoft Entra ID, GCP Workload Identity Federation, Discovery Engine, the SharePoint federated connector, Microsoft Graph, and (for the agent path) Vertex AI Agent Engine.

> Use this as the architecture deep-dive companion to the live demo. Pair it with `DEMO_SCRIPT.md`.

---

## 1. The cast

| Component | Role | Owned by |
|---|---|---|
| **Microsoft Entra ID** (formerly Azure AD) | User identity provider for `admin@sockcop.onmicrosoft.com`. Issues OIDC ID tokens and OAuth access tokens. | Microsoft tenant `de46a3fd-0d68-4b25-8343-6eb5d71afce9` |
| **MSAL.js** | Browser OAuth client in the React frontend; opens the popup, holds the user's Entra JWT in memory. | Portal frontend |
| **Portal Backend** (FastAPI) | Bridges the user's Entra JWT into a GCP token and calls Discovery Engine on the user's behalf. | Cloud Run / local |
| **Workload Identity Federation (WIF)** + **GCP STS** | Trust bridge: takes Entra ID tokens (subject) and mints short-lived GCP access tokens that *impersonate the user inside Google Cloud*. No GCP service account keys. | GCP IAM, pool `sp-wif-pool-v2`, provider `entra-provider` |
| **Discovery Engine / Gemini Enterprise** | The search + grounding engine. Owns the `streamAssist` API. Holds the SharePoint federated connector. Enforces per-user ACL at query time. | GCP project `sharepoint-wif-agent` (number `545964020693`) |
| **SharePoint Federated Connector** | Discovery Engine's delegated agent into SharePoint. At connector-create time, an admin granted it `Sites.Read.All / Files.Read.All / Sites.Search.All` against the tenant. | Configured in DE; talks to Microsoft Graph |
| **Microsoft Graph API** | The wire SharePoint speaks. The connector hits Graph endpoints (`/sites/{id}/drive/search`, etc.) on the user's behalf. | Microsoft side |
| **SharePoint Online** | The actual document store. Serves results filtered by the requesting user's per-document ACLs. | Microsoft tenant `sockcop.sharepoint.com` |
| **Vertex AI Agent Engine** | Managed runtime hosting the deployed `AmgenScienceSearch` ADK agent (resource id `1988251824309665792`). Provides per-user `session.state` that carries the Entra JWT into the agent's tool calls. | GCP `us-central1` |
| **Google ADK** (Agent Development Kit) | The agent framework. Defines `compare_insights` tool, system instruction, model. The same `discovery_engine.py` code path the backend uses gets bundled into the deployed agent. | Bundled into the agent package |

### Two Entra app registrations (important nuance)

| App | Client ID | Purpose |
|---|---|---|
| **Portal App** | `7868d053-cf9c-4848-be5a-f9bbf8279234` | User logs in here via MSAL. JWT audience = `api://7868d053-…`. WIF provider `entra-provider` is configured to accept this audience. |
| **Connector App** | `22c127d8-f3e5-4bbe-8b06-c37da3159068` | The identity Discovery Engine impersonates *as the user* against Microsoft Graph (delegated permissions: `Sites.Search.All`, `AllSites.Read`, `Files.Read.All`). |

Two apps, two purposes — splits user identity from the connector's delegated permissions.

---

## 2. Sequence — Chat path (`/api/chat`)

```
┌────────┐  ┌────────┐  ┌─────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
│Browser │  │ MSAL   │  │ Entra   │  │ Backend  │  │ GCP STS  │  │ Discovery│  │SharePoint│
│        │  │        │  │         │  │ FastAPI  │  │  + WIF   │  │  Engine  │  │  + Graph │
└───┬────┘  └───┬────┘  └────┬────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  └───┬──────┘
    │ click Send │            │            │             │             │            │
    │───────────>│            │            │             │             │            │
    │            │ acquireSilent           │             │             │            │
    │            │───────────>│            │             │             │            │
    │            │ Entra JWT  │            │             │             │            │
    │            │<───────────│            │             │             │            │
    │ POST /api/chat                       │             │             │            │
    │ X-Entra-Id-Token: <JWT>              │             │             │            │
    │─────────────────────────────────────>│             │             │            │
    │                                      │ POST sts.googleapis.com/v1/token       │
    │                                      │ subjectToken=<JWT>                     │
    │                                      │ provider=entra-provider                │
    │                                      │────────────>│             │            │
    │                                      │ GCP token (~1h, ~283 chars)            │
    │                                      │<────────────│             │            │
    │                                      │ POST :streamAssist                     │
    │                                      │ Authorization: Bearer <GCP>            │
    │                                      │ body: query.parts, dataStoreSpecs[5]   │
    │                                      │───────────────────────────>│            │
    │                                      │                            │ acquireAccessToken (per-user OAuth)
    │                                      │                            │───────────>│
    │                                      │                            │ user's MS access token
    │                                      │                            │<───────────│
    │                                      │                            │ Graph search
    │                                      │                            │ /sites/{id}/drive/search
    │                                      │                            │───────────>│
    │                                      │                            │ Docs filtered by user's ACL
    │                                      │                            │<───────────│
    │                                      │ stream: answer + grounding refs        │
    │                                      │<───────────────────────────│            │
    │ JSON: {answer, sources[], timings}   │                                         │
    │<─────────────────────────────────────│                                         │
```

### Phase A — Browser ↔ Entra ID (MSAL OAuth popup)

- User authenticates against Entra ID (the Microsoft tenant). MFA happens here if configured.
- MSAL receives an **OIDC ID token (JWT)**, audience = `api://7868d053-…` (the Portal App registration).
- Token is held in browser memory, never persisted to the backend. The backend only sees it for the duration of one HTTP request.

🔒 **Guarantee:** the user proved they are who they claim to be, with Microsoft as the identity provider. Google never sees Microsoft credentials.

### Phase B — Backend ↔ GCP STS (the WIF exchange)

Backend POSTs to `https://sts.googleapis.com/v1/token` with:

```json
{
  "audience": "//iam.googleapis.com/locations/global/workforcePools/sp-wif-pool-v2/providers/entra-provider",
  "grantType": "urn:ietf:params:oauth:grant-type:token-exchange",
  "requestedTokenType": "urn:ietf:params:oauth:token-type:access_token",
  "scope": "https://www.googleapis.com/auth/cloud-platform",
  "subjectToken": "<the user's Entra JWT>",
  "subjectTokenType": "urn:ietf:params:oauth:token-type:jwt"
}
```

GCP IAM validates the JWT signature against Entra's public keys (configured in the WIF provider) and against the audience claim. If valid, it issues a short-lived **GCP access token** that *impersonates the user inside Google Cloud*. The user appears as a `principalSet://` identity in IAM — you can grant Google Cloud roles directly to it.

🔒 **Guarantee:** no GCP service-account key, no impersonation token from a privileged account, no shared secret. The GCP token is bound to *this user* for *this hour*.

### Phase C — Backend ↔ Discovery Engine `streamAssist`

Backend POSTs to:
```
https://discoveryengine.googleapis.com/v1alpha/projects/545964020693/locations/global/collections/default_collection/engines/gemini-enterprise/assistants/default_assistant:streamAssist
```

with the WIF-derived GCP token in `Authorization: Bearer …`. Body uses the **widget shape** captured from the GE console:

```json
{
  "query": {"parts": [{"text": "what is AIMOVIG?"}]},
  "filter": "", "fileIds": [],
  "answerGenerationMode": "NORMAL",
  "userMetadata": {"timeZone": "America/New_York"},
  "assistSkippingMode": "REQUEST_ASSIST",
  "toolsSpec": {
    "vertexAiSearchSpec": {
      "dataStoreSpecs": [
        {"dataStore": ".../sharepoint-data-def-connector_file"},
        {"dataStore": ".../sharepoint-data-def-connector_page"},
        {"dataStore": ".../sharepoint-data-def-connector_comment"},
        {"dataStore": ".../sharepoint-data-def-connector_event"},
        {"dataStore": ".../sharepoint-data-def-connector_attachment"}
      ]
    },
    "toolRegistry": "default_tool_registry",
    "imageGenerationSpec": {}, "videoGenerationSpec": {}
  }
}
```

DE's API checks the caller has `discoveryengine.assistants.assist` on the engine. The WIF identity is in the principalSet that's been granted `roles/discoveryengine.editor`.

> ⚠️ **Critical gotcha:** the simpler `{"query": {"text": "..."}}` form silently returns **zero grounding refs** for federated SharePoint per-user queries. Always use the widget shape with `query.parts[]` and `assistSkippingMode: "REQUEST_ASSIST"`.

🔒 **Guarantee:** DE knows who the caller is at the GCP level, and that identity is the same human who logged into Entra at Phase A — not a shared service account.

### Phase D — Discovery Engine ↔ SharePoint Connector ↔ Graph API

DE looks up the SharePoint federated connector (`sharepoint-data-def-connector`) attached to the engine. It calls its own internal `dataConnector:acquireAccessToken` keyed by **the WIF identity** to retrieve the user's previously-stored OAuth refresh token (bound earlier via `acquireAndStoreRefreshToken` after the user consented to the SharePoint **Connector App**).

The refresh token is exchanged with Entra for a fresh **Microsoft access token** (scopes include `Sites.Read.All`, `Files.Read.All`, `Sites.Search.All`).

DE uses that MS token to hit **Microsoft Graph** — search + read calls against the sites in the connector's `admin_filter.Site` list.

> 📎 **Site scope is enforced here.** The federated connector queries ONLY the sites listed in its `admin_filter.Site` config (currently the tenant root, `/sites/FinancialDocument`, `/sites/Centura`, `/sites/allcompany`). New sites must be added by PATCHing the connector. `recursivelyCrawlNestedSites: false` means sub-sites aren't auto-discovered.

🔒 **Guarantee:** the request to SharePoint is made *as the user*, not as a service account. SharePoint's per-document ACL filtering kicks in naturally — the user only sees what their Microsoft identity is permitted to see.

### Phase E — Graph ↔ SharePoint

SharePoint applies its per-document ACLs. Items the user lacks `Read` on are simply not returned. Snippets and document URLs flow back to DE.

### Phase F — Discovery Engine composes the grounded answer

DE feeds the retrieved snippets to the Gemini model under the engine's serving config, with the engine-level **system instruction** (the "STRICT GROUNDING RULES" block configured on `default_assistant`):

> *"Use ONLY information that appears VERBATIM in the retrieved snippets. Never fabricate identifiers. If retrieval returns no relevant documents, respond exactly: 'No matching documents were found in the selected connectors.'"*

Model emits an answer plus `textGroundingMetadata.references[]` mapping spans of the answer back to specific document URIs. Returned to backend → backend extracts answer + sources + timings → JSON to frontend.

🔒 **End-to-end guarantee:** every byte of the response shown as "grounded" was retrieved live from SharePoint *as that user*. Nothing in the chain ever used a privileged shared identity. The ACL strip in the UI is literally the truth.

---

## 3. Sequence — Agent path (`/api/agent`)

When the user clicks the floating Agent panel, the request goes `/api/agent` → Vertex AI Agent Engine → deployed `AmgenScienceSearch` ADK agent → its tool → **the same Discovery Engine call as Phase C–F above**.

The extra layers:

```
┌────────┐  ┌─────────┐  ┌──────────────┐  ┌──────────────────┐  ┌────────┐
│Browser │  │ Backend │  │ Vertex AI    │  │ Deployed ADK     │  │ DE +   │
│        │  │ FastAPI │  │ Agent Engine │  │ Agent (root_     │  │ Graph  │
│        │  │         │  │ (ReasoningE) │  │ agent + tools)   │  │ + SP   │
└───┬────┘  └────┬────┘  └──────┬───────┘  └────────┬─────────┘  └───┬────┘
    │ POST /api/agent           │                   │                │
    │ X-Entra-Id-Token: <JWT>  │                   │                │
    │───────────────────────────>│                  │                │
    │                            │ vertexai.Client │                │
    │                            │  .agent_engines │                │
    │                            │  .stream_query( │                │
    │                            │    user_id,     │                │
    │                            │    session_state={                │
    │                            │      sharepointauth2: <Entra JWT>│
    │                            │    })           │                │
    │                            │────────────────>│                │
    │                            │                 │ tool: compare_insights(query)
    │                            │                 │  └─> DiscoveryEngineClient
    │                            │                 │      .exchange_wif_token(JWT)  ─> Phase B
    │                            │                 │      .search()                 ─> Phase C–F
    │                            │                 │───────────────────────────────>│
    │                            │                 │ grounded answer + sources       │
    │                            │                 │<───────────────────────────────│
    │ stream events back         │<────────────────│                                │
```

### Key differences from the chat path

- **The Entra JWT is stashed in Agent Engine's per-user `session.state`** (under key `sharepointauth2` or auto-detected `temp:sharepointauth2`). The backend never holds the GCP token; it just hands the Entra JWT to the agent and the agent does its own WIF exchange inside its tool.
- The agent runs with its own service-account identity for the *Vertex AI* layer (you need `aiplatform.reasoningEngines.streamQuery` on the engine), but it does NOT use that SA to call Discovery Engine — it uses the WIF-exchanged user token, just like the chat path.
- The ADK system instruction shapes the answer (compare internal vs external) but does not bypass any ACL — same per-user enforcement applies.

🔒 **Guarantee:** even though there's a managed runtime in the middle, the SharePoint call is still per-user. The Agent Engine's role is orchestration, not impersonation.

---

## 4. The compressed elevator pitch

> "When you click Send, three things happen back-to-back. First, your browser gets an identity token from your Microsoft tenant — same Microsoft you log into Outlook with. Second, that Microsoft identity is exchanged at Google's STS endpoint via Workload Identity Federation — you become a first-class principal inside Google Cloud, *as you*, with no shared service-account keys anywhere. Third, Discovery Engine takes that GCP-side identity, looks up the OAuth refresh token you previously consented to give the SharePoint connector, and calls Microsoft Graph *on your behalf* — which means SharePoint's normal ACLs do the actual filtering. Every grounded citation you see came back from SharePoint with your name on it. Nothing in the chain runs as 'admin'."

That's the elevator pitch. The diagrams cover the depth.

---

## 5. Anticipated audience Q&A

**"Where are credentials stored?"**
Nowhere persistent on the GCP side. The only persisted secret is the user's SharePoint OAuth refresh token, stored encrypted by Discovery Engine, keyed to the WIF identity. Browser holds the Entra ID token in memory only.

**"What if the user is removed from a SharePoint site?"**
Next query, Graph returns nothing for that site. DE has no cached results that bypass ACL. (The 24h `identityScheduleConfig.refreshInterval` is for connector-level identity sync, not for caching documents.)

**"Can a service account read SharePoint by hitting `/api/chat`?"**
Only if it brings an Entra JWT for a real user; the WIF exchange demands one. With ADC fallback (no JWT), DE returns no docs because no per-user OAuth token is bound to that identity.

**"Why two app registrations in Entra?"**
One ("Portal App", `7868d053…`) is for user login + WIF. The other ("Connector App", `22c127d8…`) is the identity Discovery Engine impersonates *as the user* against Microsoft Graph. Two apps, two purposes — splits user identity from the connector's delegated permissions.

**"What's the WIF audience format?"**
`//iam.googleapis.com/locations/global/workforcePools/<pool>/providers/<provider>` — and for `entra-provider` specifically, the JWT's `aud` claim must match `api://<client-id>` of the Portal App. If you point at `ge-login-provider` instead, the audience must be the bare client ID. Mismatched audience = STS rejects with `invalid_grant`.

**"What ensures the GCP token can't be stolen and replayed?"**
It's bound to the WIF identity, expires in ~1h, and DE's IAM check happens on every call. Stealing it is no different from stealing any other GCP access token.

**"How are new SharePoint sites added to scope?"**
PATCH the connector's `dataConnector` resource:
```
PATCH .../collections/sharepoint-data-def-connector/dataConnector?updateMask=params
{"params": {"admin_filter": {"Site": [...full new list...], "Path": []}}}
```
Send only the `admin_filter` subkey; echoing immutable fields like `instance_uri` will trip the param validator.

**"What model is doing the answer composition?"**
Gemini, configured at the Discovery Engine engine level. The `STRICT GROUNDING RULES` system instruction on the default assistant forbids fabrication, demands verbatim grounding, and tells the model to say "No matching documents were found" when retrieval is empty.

---

## 6. Common failure modes and what they mean

| Symptom | Root cause |
|---|---|
| streamAssist returns **answer with zero grounding refs** | Wrong request body shape — using `{"query":{"text":...}}` instead of `{"query":{"parts":[{"text":...}]}}` + `assistSkippingMode: REQUEST_ASSIST`. Model still answers from training data; SharePoint never queried. |
| `acquireAccessToken` returns **404 NOT_FOUND** | No SharePoint OAuth refresh token bound to this WIF identity. User needs to complete the OAuth consent flow once (`acquireAndStoreRefreshToken`). |
| STS exchange returns **`invalid_grant: ID Token issued at … is stale to sign-in`** | The Entra JWT is too old. STS demands fresh tokens for sign-in operations. Have the user re-authenticate in the portal to get a new JWT. |
| `aiplatform.reasoningEngines.get` returns **403** | The caller's identity (often ADC) lacks the role on the agent's project. Either set the right `quota_project_id` on credentials or use a credential with the right role. Don't mutate global ADC. |
| Federated query returns docs from `/sites/Foo` but not `/sites/Bar` | `/sites/Bar` is not in the connector's `admin_filter.Site` allow-list. Add it via PATCH. |

---

## 7. Reference — the actual identifiers

| Thing | Value |
|---|---|
| GCP project | `sharepoint-wif-agent` (`545964020693`) |
| Region | `global` for DE, `us-central1` for Agent Engine |
| Discovery Engine engine | `gemini-enterprise` |
| SharePoint federated connector | `sharepoint-data-def-connector` |
| Entity datastores | `sharepoint-data-def-connector_{file,page,comment,event,attachment}` |
| WIF pool | `sp-wif-pool-v2` |
| WIF providers | `entra-provider` (audience: `api://client-id`), `ge-login-provider` (audience: bare client-id) |
| Entra tenant | `de46a3fd-0d68-4b25-8343-6eb5d71afce9` |
| Portal App | `7868d053-cf9c-4848-be5a-f9bbf8279234` |
| Connector App | `22c127d8-f3e5-4bbe-8b06-c37da3159068` |
| Reasoning Engine | `projects/545964020693/locations/us-central1/reasoningEngines/1988251824309665792` (`AmgenScienceSearch`) |
| SharePoint sites in scope | `https://sockcop.sharepoint.com`, `/sites/FinancialDocument`, `/sites/Centura`, `/sites/allcompany` |

---

*Document built for the Amgen demo. See `DEMO_SCRIPT.md` for the human-script walkthrough.*
