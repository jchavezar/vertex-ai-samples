# StreamAssist OAuth Flow

> *Custom SharePoint Portal — Gemini Enterprise StreamAssist with per-user OAuth, zero credential storage.*

![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white)
![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=black)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)
![GCP](https://img.shields.io/badge/Google_Cloud-Powered-4285F4?logo=google-cloud&logoColor=white)
![Version](https://img.shields.io/badge/Version-1.0.0-lightgrey)

Search SharePoint documents via StreamAssist **without the Gemini Enterprise UI**. Users sign in with Microsoft, authorize SharePoint once, then ask natural language questions. StreamAssist does **federated search** (real-time, not indexed) with per-user ACL enforcement.

---

## Architecture

```mermaid
flowchart TB
    subgraph Browser["Browser (localhost:5174)"]
        MSAL["MSAL.js<br/>Entra ID Login"]
        Chat["Chat UI<br/>React + Vite"]
    end

    subgraph Backend["FastAPI Backend (localhost:8003)"]
        STS["STS Exchange<br/>Entra JWT → GCP Token"]
        CB["OAuth Callback<br/>Store Refresh Token"]
        SA["StreamAssist Client<br/>Federated Search"]
    end

    subgraph GCP["Google Cloud"]
        WIF["Workforce Identity<br/>Federation"]
        DE["Discovery Engine<br/>StreamAssist API"]
    end

    subgraph Microsoft["Microsoft"]
        Entra["Entra ID<br/>2 App Registrations"]
        SP["SharePoint Online<br/>Per-user ACLs"]
    end

    MSAL --> |"1 · id_token"| STS
    STS --> |"2 · token exchange"| WIF
    WIF --> |"3 · gcp_token"| SA
    SA --> |"4 · streamAssist"| DE
    DE <--> |"5 · federated search"| SP
    Chat --> |"query"| SA
    MSAL --> |"consent popup"| Entra
    Entra --> |"auth code"| CB
    CB --> |"acquireAndStore"| DE

    style Browser fill:#1a1d27,color:#e4e6eb,stroke:#2a2d37
    style Backend fill:#1a2332,color:#e4e6eb,stroke:#2a4d6e
    style GCP fill:#1a2e1a,color:#e4e6eb,stroke:#2a5d2a
    style Microsoft fill:#2e1a1a,color:#e4e6eb,stroke:#5d2a2a
```

---

## Auth Lifecycle

The complete lifecycle from first visit to search results — inspired by the event-driven pattern from [Claude Code Hooks](https://docs.anthropic.com/en/docs/claude-code/hooks).

```mermaid
flowchart LR
    subgraph once["One-Time Consent"]
        direction TB
        A1["MSAL Login<br/>Portal App"] --> A2["Get Auth URL<br/>(stores Entra JWT by nonce)"]
        A2 --> A3["Popup → Microsoft<br/>User grants consent"]
        A3 --> A4["/api/oauth/callback<br/>Receives auth code"]
        A4 --> A5["Nonce → Entra JWT<br/>→ WIF/STS → GCP token"]
        A5 --> A6["acquireAndStore<br/>RefreshToken"]
        A6 --> A7["postMessage → Frontend<br/>SharePoint Connected!"]
    end

    subgraph every["Every Search Query"]
        direction TB
        B1["User types question"] --> B2["acquireTokenSilent<br/>→ fresh Entra JWT"]
        B2 --> B3["STS Exchange<br/>Entra JWT → GCP token"]
        B3 --> B4["StreamAssist API<br/>with dataStoreSpecs"]
        B4 --> B5["Federated Search<br/>uses stored refresh token"]
        B5 --> B6["Grounded answer<br/>+ source citations"]
    end

    once --> every

    style once fill:#1a2332,color:#e4e6eb,stroke:#4a9eff
    style every fill:#1a2e1a,color:#e4e6eb,stroke:#34d399
```

---

## What Makes It Work

These are the non-obvious constraints that aren't in any public documentation. Each one was discovered through trial-and-error.

> [!WARNING]
> **Read these before attempting setup.** Skipping any single item causes silent failures — the API returns HTTP 200 with plausible-looking answers from training data, not your SharePoint.

| # | Constraint | Why It Matters |
|---|-----------|----------------|
| 1 | **WIF token for `acquireAndStoreRefreshToken`** | The token identifies the user. If you use ADC instead of WIF, `acquireAccessToken` later returns 404 because the identity doesn't match. |
| 2 | **`session` field, not `assistToken`** | StreamAssist returns `assistToken` in responses but rejects it as input. Use `sessionInfo.session` (a resource name) for follow-up queries. |
| 3 | **Natural language queries only** | Keyword queries like `"Apex Financial"` are silently skipped (`NON_ASSIST_SEEKING_QUERY_IGNORED`). Always use full questions. |
| 4 | **All 5 entity types in `dataStoreSpecs`** | `file`, `page`, `comment`, `event`, `attachment` — each is a separate data store named `{connector}_{type}`. Missing any means missing results. |
| 5 | **`oauth2AllowIdTokenImplicitFlow: true`** | Required in the Portal App's Entra manifest for WIF to accept the id_token. Without it, STS exchange silently fails. |

---

## Configuration

<details>
<summary><strong>Microsoft Entra ID</strong> — 2 app registrations required</summary>

### Portal App (MSAL login)

The frontend uses this to sign users in and get Entra ID tokens for WIF exchange.

| Setting | Value |
|---------|-------|
| App type | Single-page application |
| Redirect URI | `http://localhost:5174` |
| Supported account types | Single tenant |
| Expose an API | `api://{client-id}/user_impersonation` |
| Manifest flag | `"oauth2AllowIdTokenImplicitFlow": true` |
| Token configuration | Add `email` optional claim to ID token |

### Connector App (SharePoint OAuth)

Discovery Engine uses this to access SharePoint on behalf of users.

| Setting | Value |
|---------|-------|
| App type | Web |
| Redirect URI | `http://localhost:8003/api/oauth/callback` |
| Client secret | Generate one, add to `.env` |
| API permissions | `SharePoint > AllSites.Read`, `SharePoint > Sites.Search.All` |
| Admin consent | Grant admin consent for the tenant |

</details>

<details>
<summary><strong>Google Cloud</strong> — WIF + Discovery Engine</summary>

### Workforce Identity Federation

| Resource | Configuration |
|----------|--------------|
| Pool | Name: `sp-wif-pool-v2`, session duration: 1h |
| Provider | Name: `ge-login-provider`, OIDC, issuer: `https://login.microsoftonline.com/{tenant}/v2.0` |
| Audience | `api://{portal-app-client-id}` (must match Portal App) |
| Attribute mapping | `google.subject = assertion.sub` |
| IAM binding | `principalSet://...` → `roles/discoveryengine.editor` on the project |

### Discovery Engine

| Resource | Configuration |
|----------|--------------|
| Engine | Type: `GENERIC`, name: `gemini-enterprise` |
| Connector | SharePoint connector, ID: `sharepoint-data-def-connector` |
| Data stores | 5 auto-created: `{connector}_file`, `_page`, `_comment`, `_event`, `_attachment` |
| Entity types | All 5 must be included in `dataStoreSpecs` for search |

</details>

<details>
<summary><strong>Environment Variables</strong></summary>

**Backend `.env`**

```env
PROJECT_NUMBER=REDACTED_PROJECT_NUMBER
ENGINE_ID=gemini-enterprise
CONNECTOR_ID=sharepoint-data-def-connector
WIF_POOL_ID=sp-wif-pool-v2
WIF_PROVIDER_ID=ge-login-provider
CONNECTOR_CLIENT_ID=22c127d8-...
TENANT_ID=de46a3fd-...
```

**Frontend `.env`**

```env
VITE_CLIENT_ID=7868d053-...    # Portal App
VITE_TENANT_ID=de46a3fd-...
```

</details>

---

## Quick Start

```bash
# Backend
cd backend && uv sync && uv run uvicorn main:app --reload --port 8003

# Frontend (new terminal)
cd frontend && npm install && npm run dev
# → http://localhost:5174
```

1. Sign in with Microsoft (MSAL popup)
2. Click **Connect SharePoint** (one-time OAuth consent)
3. Ask a natural language question about your documents

---

## API

The backend exposes 5 endpoints. That's it.

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Health check |
| `/api/sharepoint/auth-url` | GET | Generate Microsoft OAuth URL for consent popup |
| `/api/oauth/callback` | GET | OAuth redirect target — stores refresh token via WIF |
| `/api/sharepoint/check-connection` | GET | Verify user has a stored SharePoint token |
| `/api/search` | POST | StreamAssist federated search with session continuity |

---

## Project Structure

```
streamassist-oauth-flow/
├── backend/
│   ├── main.py              # 175 lines — complete backend
│   ├── .env                 # GCP + Entra configuration
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── App.tsx          # 265 lines — chat UI + OAuth flow
│   │   ├── authConfig.ts    # MSAL configuration
│   │   ├── main.tsx         # React entry point
│   │   └── index.css        # Dark theme styles
│   ├── .env                 # VITE_CLIENT_ID + VITE_TENANT_ID
│   └── package.json
└── README.md
```

---

## Identity Chain

Two Entra apps, one WIF pool, one token exchange — zero stored credentials.

```
Portal App (7868d053)           Connector App (22c127d8)
       │                               │
 MSAL login → id_token           OAuth consent → auth code
       │                               │
 STS exchange (WIF)              acquireAndStoreRefreshToken
       │                               │
 GCP access token                stored refresh token
       │                               │
 StreamAssist API  ◄──── uses stored token to query SharePoint
```

| Component | Purpose |
|-----------|---------|
| Portal App | MSAL login — provides Entra JWT for WIF exchange |
| Connector App | SharePoint consent — provides auth code for refresh token storage |
| WIF Pool (`sp-wif-pool-v2`) | Maps Entra JWT `sub` claim to GCP identity |
| Discovery Engine (`gemini-enterprise`) | StreamAssist engine with SharePoint connector |

---

## Key Difference from `sharepoint_wif_portal`

| | `sharepoint_wif_portal` | `streamassist-oauth-flow` |
|---|---|---|
| **Auth flow** | Google's oauth-redirect + postMessage relay | Direct OAuth callback on our backend |
| **Token storage** | ADC or WIF | WIF only (correct identity mapping) |
| **Search** | StreamAssist + Graph Search + Gemini | StreamAssist only (federated) |
| **Backend size** | ~800 lines | 175 lines |
| **Endpoints** | 8+ | 5 |
| **Agent support** | InsightComparator ADK agent | Not needed — StreamAssist handles everything |
