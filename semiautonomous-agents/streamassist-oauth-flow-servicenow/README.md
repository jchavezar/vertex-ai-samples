# StreamAssist · ServiceNow · WIF

> *Gemini Enterprise streamAssist + **ServiceNow federated connector** + per-user ACLs, with Entra WIF identity (raw `client_id` audience).*

![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white)
![ServiceNow](https://img.shields.io/badge/ServiceNow-OAuth_2.0-81B5A1?logo=servicenow&logoColor=white)
![GCP](https://img.shields.io/badge/Google_Cloud-Discovery_Engine-4285F4?logo=google-cloud&logoColor=white)

**Full flow doc:** [FLOW.md](FLOW.md) — end-to-end reference (auth chain, the four mandatory configs, and ServiceNow-vs-SharePoint deltas)

---

## Why this project exists

Sister project to [`streamassist-oauth-flow`](../streamassist-oauth-flow) and [`streamassist-oauth-flow-us`](../streamassist-oauth-flow-us). Same WIF identity chain (Entra → STS → GCP), same Discovery Engine app contract — just **ServiceNow** swapped in for SharePoint as the federated data source.

End-to-end proof: a WIF-authenticated user signs in once with Microsoft Entra, grants ServiceNow consent once, then asks natural-language questions and gets **grounded answers from ServiceNow records** (incidents, knowledge articles, catalog items) with per-user ACLs enforced by ServiceNow's Table API.

## Interactive flow diagram

For a click-through visual explanation of how WIF/Entra and ServiceNow identities get bridged via Discovery Engine: open [`docs/flow-diagram.html`](docs/flow-diagram.html) in a browser. 6 phases, animated swim lanes for each identity universe, code samples for every step, and a live bridge-table visualization showing how `acquireAndStoreRefreshToken` links the two universes.

```bash
# serve docs/ on a separate port
python3 -m http.server 5177 --directory docs &
open http://localhost:5177/flow-diagram.html
```

## Demo

![Demo](docs/demo-grounded.png)

End-to-end: MSAL login → STS exchange → ServiceNow OAuth consent → grounded streamAssist answer with ServiceNow source citations. Sensitive identifiers redacted. The right-side **Live API Pipeline** panel shows each call's endpoint, input, and output as you progress through the steps.

## What's different from the SharePoint siblings

| | This project | streamassist-oauth-flow* |
|---|---|---|
| Federated data source | **ServiceNow** Table API | SharePoint Online |
| OAuth provider for the connector | **ServiceNow Application Registry** | Microsoft Entra Connector App |
| `dataSource` enum | `servicenow` | `sharepoint` |
| Connector params | `instance_uri`, `client_id`, `client_secret`, `user_account`, `password` | `tenant_id`, `instance_uri`, `admin_filter.Site`, `eeeu_enabled`, … |
| OAuth scope passed to user | *(none — leave empty in Application Registry)* | `AllSites.Read`, `Sites.Search.All`, `Files.Read.All`, … |
| Datastores | `_incident`, `_knowledge`, `_catalog`, `_users`, `_attachment` | `_file`, `_page`, `_comment`, `_event`, `_attachment` |
| Per-user ACL enforcement | Native ServiceNow ACLs/roles via Table API | SharePoint per-user permissions via Microsoft Graph |
| **Identical otherwise** | WIF pool/provider, Entra Portal App, MSAL flow, STS exchange, engine `workforceIdentityPoolProvider`, license seats, `acquireAndStoreRefreshToken`, streamAssist payload shape | … |

## Two ways to run

### A) Quick demo — single-pane HTML tester (no backend)

Vanilla JS, runs entirely in the browser. Best for understanding the API contract.

```bash
cd tester
cp .env.example .env       # fill in 10 values
python3 serve.py           # → http://localhost:5176
```

### B) Full app — FastAPI backend + React/MSAL frontend

Same architecture as `streamassist-oauth-flow` but pointed at ServiceNow.

```bash
# Backend (port 8003)
cd backend
cp .env.example .env       # fill in PROJECT_NUMBER, ENGINE_ID, CONNECTOR_ID,
                           #         WIF_*, TENANT_ID, SERVICENOW_*, SN_OAUTH_*
uv sync
uv run python main.py

# Frontend (port 5174)
cd ../frontend
cp .env.example .env       # fill in VITE_CLIENT_ID, VITE_TENANT_ID
npm install
npm run dev
```

## Quickstart (tester only)

```bash
cd tester
cp .env.example .env       # then fill in your values (10 keys — see below)
python3 serve.py           # → http://localhost:5176
```

`serve.py` reads `.env` at request time and injects the values into `index.html` as it serves the page. **Never commit a real `.env`** — it's in `.gitignore`.

### Required `.env` keys

| Key | Where to get it |
|---|---|
| `PORTAL_APP_CLIENT_ID` | The MSAL Portal App client_id (raw GUID, no `api://` prefix). Same as the SharePoint siblings |
| `TENANT_ID` | Your Microsoft Entra tenant ID |
| `PROJECT_NUMBER` | Your GCP project number (numeric) |
| `WIF_POOL_ID` | Workforce Identity Pool ID (at `locations/global/`) |
| `WIF_PROVIDER_ID` | OIDC Provider ID inside the pool — must have `--client-id="<RAW_PORTAL_GUID>"` (no `api://`) |
| `ENGINE_ID` | Discovery Engine app ID |
| `LOCATION` | `global` or `us` |
| `SERVICENOW_CONNECTOR_ID` | The collection ID from `setUpDataConnector` (e.g. `servicenow-connector-1777047657`) |
| `SERVICENOW_INSTANCE_URI` | `https://YOUR_INSTANCE.service-now.com` |
| `SN_OAUTH_CLIENT_ID` | client_id of the OAuth app you registered in ServiceNow → System OAuth → Application Registry |

### Use the page

Open `http://localhost:5176`, click through the 4 steps:
1. **Login** with Microsoft (MSAL)
2. **Exchange** JWT → GCP token (WIF/STS)
3. **Connect** ServiceNow (per-user OAuth consent — one-time per user)
4. Type a question → **Search** — watch the live timer + grounded answer with SN source citations

## What you need to provision

| | Where | Who creates it |
|---|---|---|
| **Entra Portal App** (MSAL login) | Microsoft Entra ID | Reuse from `streamassist-oauth-flow*` if you have it; else follow the original setup |
| **WIF Pool + OIDC Provider** (raw `client_id` audience) | GCP Workforce Identity Federation | Reuse from `streamassist-oauth-flow*` |
| **ServiceNow OAuth app** (this is the new piece) | ServiceNow → System OAuth → Application Registry | New — see [FLOW.md §1](FLOW.md#1-servicenow-oauth-app-application-registry) |
| **Discovery Engine app** (must have `workforceIdentityPoolProvider` set) | GCP Discovery Engine | Reuse existing engine; verify identity is wired |
| **ServiceNow federated connector** (attached to the engine) | GCP Discovery Engine | New — `setUpDataConnector` REST call |

## Layout

```
streamassist-oauth-flow-servicenow/
├── README.md                  # this file — overview + sibling diff
├── FLOW.md                    # full end-to-end flow doc
├── REPLICATE.md               # copy-paste shell commands to reproduce everything
├── AUTH_SEQUENCE.md           # mermaid sequence + bridge diagrams
│
├── backend/                   # FastAPI backend (port 8003)
│   ├── main.py                # STS exchange, /api/servicenow/auth-url, /api/oauth/callback,
│   │                          # /api/oauth/exchange (acquireAndStoreRefreshToken),
│   │                          # /api/servicenow/check-connection, /api/search (streamAssist)
│   ├── .env.example
│   ├── pyproject.toml
│   └── uv.lock
│
├── frontend/                  # React + MSAL (port 5174)
│   ├── src/
│   │   ├── App.tsx            # MSAL login + 4-step UI + debug sidebar
│   │   ├── authConfig.ts      # MSAL config (no api:// scope — raw client_id)
│   │   └── main.tsx
│   ├── .env.example
│   ├── index.html
│   ├── package.json
│   └── vite.config.ts
│
├── tester/                    # alternative single-pane HTML tester (port 5176)
│   ├── index.html             # vanilla JS, no backend needed, live pipeline panel
│   ├── serve.py               # tiny HTTP server with .env value injection
│   └── .env.example
│
└── docs/
    ├── demo-grounded.png      # screenshot of grounded SN answer
    └── flow-diagram.html      # interactive click-through visual diagram
```

## The proof in three signals

1. **Pipeline panel** shows `STS · token-exchange` → `DE · acquireAndStoreRefreshToken` → `DE · streamAssist` all returning `200`
2. **Decoded id_token** has `aud` = the raw Portal App GUID (no `api://` prefix)
3. **streamAssist response** is grounded — `textGroundingMetadata.references[]` populated with ServiceNow records (e.g. `INC0000041`, `KB0010001`)

See [FLOW.md](FLOW.md) for the full step-by-step + the four mandatory configurations easy to miss on a fresh engine.

---

Built by [Jesus Chavez](https://www.linkedin.com/in/jchavezar/) — Customer Engineer, Google Cloud.
