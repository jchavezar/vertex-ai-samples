# Executive Assistant & Outlook StreamAssist — Complete Flow Guide

This document provides a comprehensive end-to-end breakdown of the authentication, connector consent, identity federation, real-time `streamAssist` interaction, and approval inbox architecture implemented in this project.

---

## 1. High-Level Architecture Flow

```mermaid
flowchart LR
    subgraph A["Phase 1: User Identity (WIF)"]
        direction TB
        A1["User Login (MSAL)"] --> A2["Entra ID JWT"]
        A2 --> A3["GCP STS Exchange"]
        A3 --> A4["GCP WIF Bearer Token"]
    end

    subgraph B["Phase 2: Connector Consent"]
        direction TB
        B1["Connect Outlook"] --> B2["Microsoft Consent Popup"]
        B2 --> B3["Auth Code & State Redirect"]
    end

    subgraph C["Phase 3: Refresh Token Storage"]
        direction TB
        C1["acquireAndStoreRefreshToken"] --> C2["Discovery Engine Vault"]
    end

    subgraph D["Phase 4: Real-time Assistant Stream"]
        direction TB
        D1["streamAssist API (v1alpha)"] --> D2["SSE Delta Stream"]
        D2 --> D3["Deduplicated UI Output + Citations"]
    end

    A --> C
    B --> C
    C --> D
```

---

## 2. Detailed Sequence Diagram

```mermaid
sequenceDiagram
    actor User
    participant FE as React Frontend (Vite)
    participant BE as FastAPI Backend
    participant WIF as GCP WIF (STS)
    participant MS as Microsoft Entra ID
    participant DE as Google Discovery Engine

    note over User,DE: Phase 1 — User Identity Authentication (WIF)
    User->>FE: Click "Sign in with Microsoft"
    FE->>MS: MSAL loginPopup (scope: user_impersonation)
    MS-->>User: Microsoft login prompt
    User->>MS: Authenticate
    MS-->>FE: id_token (Entra ID JWT)

    note over User,DE: Phase 2 — Connector Consent (Outlook / SharePoint)
    User->>FE: Click "Connect Outlook"
    FE->>BE: GET /api/outlook/auth-url (Header: X-Entra-Id-Token)
    BE-->>FE: Microsoft OAuth URL + Nonce
    FE->>MS: Open Popup (login.microsoftonline.com)
    MS-->>User: Grant Mail.Read, Calendars.Read, User.Read
    User->>MS: Confirm Consent
    MS-->>BE: GET /api/oauth/callback?code=...&state=...

    note over User,DE: Phase 3 — Convergence & Token Vaulting
    BE->>BE: Lookup Entra JWT by state nonce
    BE->>WIF: POST sts.googleapis.com/v1/token (Entra JWT)
    WIF-->>BE: GCP WIF access_token
    BE->>DE: POST dataConnector:acquireAndStoreRefreshToken
    DE-->>BE: 200 OK (Refresh Token Stored under WIF Identity)
    BE-->>FE: PostMessage: Outlook Connected!

    note over User,DE: Phase 4 — Real-time Assistant Streaming (streamAssist)
    User->>FE: Ask question ("what's the address of David Sung Park")
    FE->>BE: POST /api/search (Query + Session Token)
    BE->>WIF: Exchange Entra JWT -> GCP WIF access_token
    BE->>DE: POST :streamAssist (REQUEST_ASSIST mode, 14 dataStoreSpecs)
    loop SSE Stream Processing
        DE-->>BE: Raw SSE Chunk (JSON)
        BE->>BE: Inspect active reply (replies[-1]), filter '0' artifacts
        BE-->>FE: data: {"type": "text", "text": "...", "is_cumulative": true}
        BE-->>FE: data: {"type": "metrics", "metrics": {...}}
        BE-->>FE: data: {"type": "suggestions", "questions": [...]}
    end
    FE-->>User: Render Clean Markdown + Grounding Cards + Follow-up Chips
```

---

## 3. Key Backend Endpoints Reference

| Endpoint | Method | Description | Colab Notebook Alignment |
| :--- | :--- | :--- | :--- |
| `/api/outlook/auth-url` | `GET` | Generates the Microsoft OAuth authorization URL with required scopes. | **Step 2 (Get Widget Config / Auth URIs)** |
| `/api/oauth/callback` | `GET` | Handles the OAuth redirect code & exchanges Entra JWT for GCP WIF token. | **Step 3 & 4 (Retrieve Auth Code & Post Token)** |
| `/api/oauth/exchange` | `POST` | Posts `fullRedirectUri` to `dataConnector:acquireAndStoreRefreshToken`. | **Step 4 (Acquire & Store Refresh Token)** |
| `/api/outlook/check-connection` | `GET` | Calls `dataConnector:acquireAccessToken` to verify active connection. | **Step 5 (Check Connector Auth State)** |
| `/api/search` | `POST` | Streams assistant responses via `streamAssist` across 14 dataStores. | **Step 7 (Assistant Execution)** |
| `/api/approvals` | `GET` | Scans user inbox for pending approvals using `streamAssist`. | **Action Items Inbox Pipeline** |
| `/api/approvals/act` | `POST` | Executes automated email reply on Outlook via Microsoft Graph API. | **Executive Action Execution** |

---

## 4. Alignment with `[external]fed_connector_authflow.ipynb`

This codebase implements 100% of the connector lifecycle described in Google's official Discovery Engine Federated Search Connector notebook:

1. **WIF Identity Delegation:** User identity is asserted using Entra ID tokens transformed into GCP access tokens via STS without storing service account keys.
2. **Dynamic DataStore Resolution:** Automatically resolves engine dataStore specifications across SharePoint, Outlook, and ServiceNow.
3. **SSE Deduplication Guarantee:** Processes `replies[-1]` per chunk and uses cumulative text synchronization (`is_cumulative: True`) to eliminate duplicate lines and mangled headers.
