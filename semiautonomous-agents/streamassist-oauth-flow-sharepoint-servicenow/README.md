# StreamAssist OAuth Flow — SharePoint + ServiceNow + Google Search

Combined Gemini Enterprise StreamAssist demo with **per-user OAuth** for both
SharePoint and ServiceNow, plus an **assistant-level Google Search** toggle.
Each connector has an **independent toggle** in the UI — turn any combination
on to federate searches across whichever data sources you want, with per-user
ACLs enforced via stored refresh tokens. A fourth toggle flips the assistant's
web grounding on/off in real time.

This consolidates the architecture of:
- [`streamassist-oauth-flow-sharepoint`](../streamassist-oauth-flow-sharepoint/) (formerly `streamassist-oauth-flow`)
- [`streamassist-oauth-flow-servicenow`](../streamassist-oauth-flow-servicenow/)

into a single backend + frontend that supports both connectors at once on the
same Discovery Engine app, plus strict anti-hallucination guardrails.

---

## Demo

![Combined portal — three toggles, snippet bubbles, ungrounded warning](docs/demo-overview.png)

Single sign-on via MSAL, then three independent toggles:

| Toggle | Effect on each search |
|---|---|
| **SharePoint** | Adds 5 SharePoint data stores (`file`, `page`, `comment`, `event`, `attachment`) to `dataStoreSpecs` |
| **ServiceNow** | Adds 5 ServiceNow data stores (`incident`, `knowledge`, `catalog`, `users`, `attachment`) to `dataStoreSpecs` |
| **Google Search** | PATCHes the assistant's `webGroundingType` between `WEB_GROUNDING_TYPE_GOOGLE_SEARCH` and `WEB_GROUNDING_TYPE_DISABLED`, plus swaps the system instruction |

Source cards under each answer show the **highlighted snippet** that grounded
the model's response, so you can audit exactly where each fact came from.

---

## Architecture

```
   Microsoft Entra Tenant         GCP Project (WIF + DE)         Connectors
   ─────────────────────          ──────────────────────         ──────────
                                                                 SharePoint
   Portal App (login)  ─id_token─►  WIF Pool / Provider            (per-user
                                          │                         OAuth via
   Connector App (SP)  ─consent──►  Discovery Engine    ◄──refresh──Connector
                                    "gemini-enterprise"            App)
   ServiceNow OAuth   ─consent──►  ┌─────────────────┐
   App (in SN)                     │ default_assistant
                                   │ ├─SharePoint DS  │           ServiceNow
                                   │ ├─ServiceNow DS  │            (per-user
                                   │ └─Google Search  │             OAuth via
                                   │   (toggle)       │             SN OAuth
                                   └─────────────────┘             entry)
```

The OAuth callback handler is shared — the connector that initiated the flow
is encoded in the OAuth `state` param and used by the callback to bind the
refresh token to the correct connector. Search fans out to a single
`streamAssist` call with a union of selected `dataStoreSpecs`.

For deep dives:
- **[FLOW.md](FLOW.md)** — conceptual reference: tokens, identities, the bridge
- **[AUTH_SEQUENCE.md](AUTH_SEQUENCE.md)** — Mermaid sequence diagrams
- **[REPLICATE.md](REPLICATE.md)** — copy-paste commands to set up from scratch

---

## Why this exists (and what it solves)

The two single-connector demos worked but exposed three issues when shown to
customers:

1. **One demo per connector is awkward.** Customers want to see *"the assistant
   queries SharePoint AND ServiceNow"* — not toggle between two separate apps
   pointing at two different engines.
2. **Hallucinations.** The default assistant has `WEB_GROUNDING_TYPE_GOOGLE_SEARCH`
   enabled and no system instruction, so when retrieval returns nothing it
   silently falls back to web/training knowledge — generating fake CVE IDs,
   incident numbers, and contract references that look exactly like the real
   thing.
3. **Opaque grounding.** When the answer included citations, the references
   weren't shown — users had to trust that "this came from a doc" without
   seeing which doc or which snippet.

This combined demo fixes all three:

- **One backend, one engine, multiple connectors.** Both SharePoint and
  ServiceNow data stores are attached to the same engine
  (`gemini-enterprise`), and a single `streamAssist` call queries the union
  selected by the toggles.
- **Strict grounding instruction.** The assistant is patched with explicit
  rules forbidding fabricated identifiers (CVE-XXXX, INC0XXXXXX, ticket #s).
  When retrieval returns nothing, it must respond verbatim with *"No matching
  documents were found in the selected connectors."*
- **Snippet bubbles.** Each source card shows the highlighted text excerpt
  that the model grounded its answer in, with `<c0>...</c0>` highlight tags
  rendered as `<mark>` and `<ddd/>` ellipses preserved.

---

## Setup

### 0 · Prerequisites

You need (or already have, if you ran the single-connector demos):

| Resource | Notes |
|---|---|
| GCP project with Discovery Engine API enabled | Project number, not ID |
| Workforce Identity pool + OIDC provider mapped to your Entra tenant | The provider's `audience` must match your Portal App's `clientId` |
| Microsoft Entra Portal App | For browser MSAL login (`oauth2AllowIdTokenImplicitFlow: true`) |
| Microsoft Entra Connector App | Used by Discovery Engine for SharePoint OAuth |
| ServiceNow OAuth app (Application Registry) | `redirect_uri = https://vertexaisearch.cloud.google.com/oauth-redirect` |
| `gcloud` authenticated as a project admin | Used by the backend's admin endpoints (assistant config patches) |

If you haven't built any of these yet, follow the per-connector REPLICATE
guides first:

- [SharePoint REPLICATE](../streamassist-oauth-flow-sharepoint/README.md) (in the original folder)
- [ServiceNow REPLICATE](../streamassist-oauth-flow-servicenow/REPLICATE.md)

### 1 · Consolidate both connectors into one engine

This combined demo assumes both connectors' data stores are attached to the
**same** engine. If you currently have them on separate engines, run:

```bash
PROJECT_NUMBER=<your-project-number>
ENGINE_ID=<engine-that-has-sharepoint>      # we'll add ServiceNow to this one
SN_CONNECTOR_ID=<servicenow-connector-id>

TOKEN=$(gcloud auth print-access-token)

# Read existing data stores
EXISTING=$(curl -sS -H "Authorization: Bearer $TOKEN" -H "X-Goog-User-Project: $PROJECT_NUMBER" \
  "https://discoveryengine.googleapis.com/v1alpha/projects/$PROJECT_NUMBER/locations/global/collections/default_collection/engines/$ENGINE_ID" \
  | jq -r '[.dataStoreIds[]?] + ["'$SN_CONNECTOR_ID'_incident","'$SN_CONNECTOR_ID'_knowledge","'$SN_CONNECTOR_ID'_catalog","'$SN_CONNECTOR_ID'_users","'$SN_CONNECTOR_ID'_attachment"] | unique | tojson')

# PATCH the engine
curl -sS -X PATCH \
  -H "Authorization: Bearer $TOKEN" -H "X-Goog-User-Project: $PROJECT_NUMBER" -H "Content-Type: application/json" \
  "https://discoveryengine.googleapis.com/v1alpha/projects/$PROJECT_NUMBER/locations/global/collections/default_collection/engines/$ENGINE_ID?updateMask=dataStoreIds" \
  -d "{\"dataStoreIds\": $EXISTING}" | jq '.dataStoreIds'
```

You should see all 10+ data stores returned. Both SharePoint and ServiceNow
data is now reachable from a single `streamAssist` call.

### 2 · Lock down the assistant (the hallucination fix)

The default assistant has web grounding enabled and no system instruction —
that's where the fake CVE IDs come from. Replace both:

```bash
TOKEN=$(gcloud auth print-access-token)
curl -sS -X PATCH \
  -H "Authorization: Bearer $TOKEN" -H "X-Goog-User-Project: $PROJECT_NUMBER" -H "Content-Type: application/json" \
  "https://discoveryengine.googleapis.com/v1alpha/projects/$PROJECT_NUMBER/locations/global/collections/default_collection/engines/$ENGINE_ID/assistants/default_assistant?updateMask=webGroundingType,generationConfig.systemInstruction" \
  -d @- <<'JSON'
{
  "webGroundingType": "WEB_GROUNDING_TYPE_DISABLED",
  "generationConfig": {
    "systemInstruction": {
      "additionalSystemInstruction": "STRICT GROUNDING RULES:\n\n1. Use ONLY information that appears VERBATIM in the retrieved snippets. Do not paraphrase loosely; do not extrapolate; do not embellish.\n\n2. NEVER fabricate identifiers. This includes CVE IDs (e.g. CVE-2024-001), incident numbers (INC0001234), knowledge base IDs (KB0001234), ticket numbers, employee IDs, contract numbers, or ANY structured identifier. If the source describes a vulnerability or item but does not give it an ID, describe it WITHOUT inventing one.\n\n3. NEVER add example IDs, sample data, or placeholder values to make a table or list look more complete.\n\n4. If your answer requires structured data (table, list of incidents, etc.) and the sources do not contain that structured data verbatim, present the information as prose instead, OR say so explicitly: 'The source documents describe these findings but do not assign IDs to them.'\n\n5. If retrieval returns no relevant documents, respond exactly: 'No matching documents were found in the selected connectors. Try rephrasing or enabling another connector.'\n\n6. Do not use prior knowledge, training data, or web sources. Every concrete fact must trace to a snippet."
    }
  }
}
JSON
```

The Google Search toggle in the UI calls `/api/grounding/web` which patches
this same field — flipping the toggle ON re-enables web grounding *and* swaps
to a more permissive instruction (allows web sources but still bans fake IDs).

### 3 · Backend

```bash
cd backend
uv venv --python 3.12
uv pip install -e .
cp .env.example .env
# fill in PROJECT_NUMBER, ENGINE_ID, WIF_*, TENANT_ID,
# SHAREPOINT_*, SERVICENOW_* / SN_OAUTH_* — see .env.example for the full list
uv run python main.py    # listens on $BACKEND_PORT (default 8004)
```

**Important:** the backend's `/api/grounding/web` endpoints use `gcloud auth
print-access-token` (the active gcloud identity) for assistant-config admin
calls — the user's WIF principal usually doesn't have `discoveryengine.assistants.update`.
Run the backend on a host where `gcloud` is authenticated as a project admin,
or replace `_admin_token()` in `main.py` with whatever credential mechanism
fits your deployment.

### 4 · Frontend

```bash
cd frontend
npm install
cp .env.example .env
# fill in VITE_CLIENT_ID (Portal App), VITE_TENANT_ID (Entra tenant)
npm run dev    # serves on http://localhost:5177
```

Open http://localhost:5177.

### 5 · Disable a connector (optional)

Set `SHAREPOINT_ENABLED=false` or `SERVICENOW_ENABLED=false` in
`backend/.env` to hide that connector from the UI entirely. The backend
returns its `enabled` flag from `/api/connectors`, and the frontend only
renders chips for enabled ones.

---

## Using the UI

1. **Sign in** with your Microsoft account (MSAL popup).
2. The header shows three toggle chips. Each connector chip displays:
   - The connector name
   - Status: `ACTIVE` (active+connected), `STANDBY` (off but token stored),
     `Needs consent` (on but never consented), `Authorizing…` (consent in flight)
   - A **Connect** button when consent is needed; a **↻** button to force re-auth
3. Click the toggle ON. If you've never consented, the OAuth popup opens —
   sign in to the IdP (Microsoft for SharePoint, ServiceNow for SN) and click
   **Allow**. The chip flips to ACTIVE green.
4. Toggle the **Google Search** chip on/off any time — it round-trips to
   `/api/grounding/web` which patches the assistant config.
5. Type a question. The request fans out to all *Active* connectors in a
   single `streamAssist` call. Each source card shows:
   - The connector badge (color-coded)
   - The document title + URL
   - One or more **snippet bubbles** showing the highlighted text excerpts
     that grounded the model's answer

If retrieval returns nothing, you'll see the strict response *"No matching
documents were found…"* — the model is forbidden from filling in with
training-knowledge guesses.

---

## Environment variables

### Backend `.env`

| Var | Required | Description |
|---|---|---|
| `PROJECT_NUMBER` | ✓ | GCP project number (numeric) |
| `ENGINE_ID` | ✓ | Discovery Engine ID containing both connectors' data stores |
| `WIF_POOL_ID` | ✓ | Workforce Identity Federation pool |
| `WIF_PROVIDER_ID` | ✓ | OIDC provider in the WIF pool |
| `TENANT_ID` | ✓ | Microsoft Entra tenant (Portal App login) |
| `REDIRECT_URI` | | Hardcoded to Google's redirect; override only if you know what you're doing |
| `BACKEND_PORT` | | Default `8004` |
| `SHAREPOINT_ENABLED` | | `true` (default) / `false` |
| `SHAREPOINT_CONNECTOR_ID` | ✓ if SP enabled | DE SharePoint connector ID |
| `SHAREPOINT_CONNECTOR_CLIENT_ID` | ✓ if SP enabled | Microsoft Connector App client ID |
| `SHAREPOINT_DOMAIN` | ✓ if SP enabled | e.g. `contoso.sharepoint.com` |
| `SERVICENOW_ENABLED` | | `true` (default) / `false` |
| `SERVICENOW_CONNECTOR_ID` | ✓ if SN enabled | DE ServiceNow connector ID |
| `SERVICENOW_INSTANCE_URI` | ✓ if SN enabled | `https://your-instance.service-now.com` |
| `SN_OAUTH_CLIENT_ID` | ✓ if SN enabled | ServiceNow OAuth client ID |
| `SN_OAUTH_CLIENT_SECRET` | ✓ if SN enabled | ServiceNow OAuth client secret |
| `SN_OAUTH_SCOPES` | | Default `useraccount` |

### Frontend `.env`

| Var | Description |
|---|---|
| `VITE_CLIENT_ID` | Portal App client ID (browser-side) |
| `VITE_TENANT_ID` | Microsoft Entra tenant ID |

---

## API surface

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/health` | Health check |
| `GET` | `/api/connectors` | Lists enabled connectors `{name: {enabled, label}}` |
| `GET` | `/api/grounding/web` | Returns `{enabled: bool}` (current assistant `webGroundingType`) |
| `POST` | `/api/grounding/web` | Body `{enabled: bool}` — patches the assistant; swaps system instruction |
| `GET` | `/api/sharepoint/auth-url` | Builds Microsoft OAuth consent URL with state-encoded connector |
| `GET` | `/api/sharepoint/check-connection` | Calls `acquireAccessToken` to verify a refresh token is stored |
| `GET` | `/api/servicenow/auth-url` | Builds ServiceNow OAuth consent URL |
| `GET` | `/api/servicenow/check-connection` | Same as SP, for ServiceNow |
| `GET` | `/api/oauth/callback` | Shared callback — connector inferred from `state.connector` |
| `POST` | `/api/oauth/exchange` | Body `{fullRedirectUrl, connector?}` — calls `acquireAndStoreRefreshToken` |
| `POST` | `/api/search` | Body `{query, session_token?, connectors?}` — runs `streamAssist` over the union of selected data stores |

All `/api/*` endpoints (except `/api/grounding/*`) require the
`X-Entra-Id-Token` header — the WIF JWT, exchanged server-side via STS for a
GCP token bound to the user's WIF principal.

---

## Failure-mode lookup

| Symptom | Likely cause | Fix |
|---|---|---|
| Toggle stuck on `Needs consent` after clicking Connect | Popup blocked | Allow popups for `localhost:5177` |
| Consent popup loads SN/Microsoft but nothing happens after Allow | COOP blocking `postMessage` from `vertexaisearch.cloud.google.com` | The popup-closed polling fallback should still work — wait 2-3 s after the popup closes |
| Source card shows the right doc but a snippet bubble is empty | DE returned a reference with no `content` (rare with SharePoint, expected for some ServiceNow records) | Cosmetic only — the URL is still clickable |
| Answer says *"No matching documents…"* even though docs exist | Toggle is ON but `connected: false` (no refresh token) | Click Connect on the chip and complete consent |
| Hallucinated CVE IDs or incident numbers reappear | Someone reverted the assistant's `additionalSystemInstruction` | Re-run the PATCH in [§2](#2--lock-down-the-assistant-the-hallucination-fix) |
| 63 s response time | `webGroundingType: WEB_GROUNDING_TYPE_GOOGLE_SEARCH` is set | Toggle Google Search OFF (or PATCH `WEB_GROUNDING_TYPE_DISABLED`) |
| `403 discoveryengine.assistants.get denied` from the backend | The active `gcloud` account isn't a project admin | Run `gcloud auth login` as a project admin or override `_admin_token()` |

---

## File layout

```
streamassist-oauth-flow-sharepoint-servicenow/
├── README.md                  ← this file
├── REPLICATE.md               ← copy-paste setup commands
├── AUTH_SEQUENCE.md           ← Mermaid sequence diagrams
├── FLOW.md                    ← conceptual reference (tokens, identities, the bridge)
├── backend/
│   ├── main.py                ← single FastAPI app — both connectors, shared OAuth callback
│   ├── pyproject.toml
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── App.tsx            ← three-toggle UI, snippet bubbles, ungrounded warning
│   │   ├── authConfig.ts      ← MSAL config (Portal App)
│   │   └── index.css
│   ├── package.json
│   ├── vite.config.ts         ← proxies /api → :8004
│   └── .env.example
└── docs/
    └── (screenshots)
```

Pair this with the per-connector demos for deeper-dive material:

- `../streamassist-oauth-flow-sharepoint/` — SharePoint-only, with the
  Playwright `auth_sharepoint.py` bootstrap CLI for headless consent
- `../streamassist-oauth-flow-servicenow/` — ServiceNow-only, with the
  programmatic password-grant flow for CI testing
