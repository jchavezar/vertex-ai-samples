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

## Quickstart

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
├── README.md                # this file — overview + sibling diff
├── FLOW.md                  # full end-to-end flow doc (mirrors siblings)
├── tester/
│   ├── index.html           # single-pane HTML: 4 steps left, live API pipeline right
│   └── serve.py             # tiny HTTP server on :5176
├── docs/
│   ├── demo-grounded.png    # screenshot of the grounded SN answer
│   └── screenshots/         # ServiceNow Application Registry setup steps
└── .gitignore
```

## The proof in three signals

1. **Pipeline panel** shows `STS · token-exchange` → `DE · acquireAndStoreRefreshToken` → `DE · streamAssist` all returning `200`
2. **Decoded id_token** has `aud` = the raw Portal App GUID (no `api://` prefix)
3. **streamAssist response** is grounded — `textGroundingMetadata.references[]` populated with ServiceNow records (e.g. `INC0000041`, `KB0010001`)

See [FLOW.md](FLOW.md) for the full step-by-step + the four mandatory configurations easy to miss on a fresh engine.

---

Built by [Jesus Chavez](https://www.linkedin.com/in/jchavezar/) — Customer Engineer, Google Cloud.
