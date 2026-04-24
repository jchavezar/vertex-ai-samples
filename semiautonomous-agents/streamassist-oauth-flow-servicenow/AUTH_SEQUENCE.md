# Authentication Sequence — Mermaid Diagrams

End-to-end auth chain for **Microsoft Entra (WIF)** → **Google Discovery Engine** → **ServiceNow** federated search.

> GitHub renders these mermaid blocks automatically.

---

## 1. The full sequence — from MSAL login to grounded ServiceNow answer

```mermaid
sequenceDiagram
    autonumber
    actor User as User
    participant Browser as Browser (tester)
    participant MS as Microsoft Entra
    participant STS as Google STS (WIF)
    participant DE as Discovery Engine
    participant SN as ServiceNow

    Note over User,MS: PHASE 1 — User identity (every session)
    User->>Browser: Click Login with Microsoft
    Browser->>MS: MSAL loginPopup with scopes openid profile email
    MS-->>Browser: id_token JWT (aud equals raw GUID, sub is MS user)

    Note over Browser,STS: PHASE 2 — STS exchange (WIF)
    Browser->>STS: POST /v1/token (subject_token equals id_token)
    STS->>STS: validate JWT signature, map id_token sub to WIF principal
    STS-->>Browser: GCP access_token (opaque, identity is WIF principal)

    Note over User,SN: PHASE 3 — SN consent (one-time per user)
    User->>Browser: Click Connect ServiceNow
    Browser->>SN: open popup at /oauth_auth.do (client_id, redirect_uri)
    SN-->>User: SN login form (its own user table)
    User->>SN: SN credentials (admin / password)
    SN-->>User: consent screen Allow access?
    User->>SN: Click Allow
    SN-->>Browser: redirect to vertexaisearch oauth-redirect with code

    Note over Browser,SN: PHASE 4 — acquireAndStoreRefreshToken — THE BRIDGE
    Browser->>DE: POST acquireAndStoreRefreshToken (Bearer GCP token, fullRedirectUri)
    DE->>DE: A. decode Bearer, caller is WIF principal
    DE->>SN: B. POST /oauth_token.do (grant_type authorization_code)
    SN-->>DE: sn_refresh_token (for SN user admin)
    DE->>DE: C. INSERT bridge row (WIF principal to sn_refresh_token)
    DE-->>Browser: 200 OK

    Note over User,SN: PHASE 5 — streamAssist (every search)
    User->>Browser: Type question, click Search
    Browser->>DE: POST streamAssist (Bearer SAME GCP token, query, dataStoreSpecs)
    DE->>DE: decode Bearer, caller is WIF principal
    DE->>DE: SELECT sn_refresh_token WHERE caller equals WIF principal
    DE->>SN: POST /oauth_token.do (grant_type refresh_token)
    SN-->>DE: fresh sn_access_token
    DE->>SN: GET /api/now/table/incident (Bearer sn_access_token)
    SN->>SN: ACL check (as user admin)
    SN-->>DE: matching records
    DE->>DE: Gemini synthesis, grounded answer
    DE-->>Browser: answer plus sources
    Browser-->>User: render grounded answer with source citations
```

---

## 2. Just the bridge — where the two universes get linked

```mermaid
flowchart LR
    subgraph MS["Microsoft Entra Universe"]
        MSUser["MS User<br/>jchavez@contoso"]
        MSToken["id_token JWT<br/>aud equals raw GUID"]
        MSUser -- "MSAL login" --> MSToken
    end

    subgraph WIF["Google WIF Universe"]
        GCPToken["GCP access_token<br/>principal at subject sha256 of MS sub"]
        MSToken -- "STS token-exchange" --> GCPToken
    end

    subgraph DE["Discovery Engine"]
        Bridge[("Bridge Table<br/>WIF principal to sn_refresh_token")]
        GCPToken -- "Bearer header in<br/>acquireAndStoreRefreshToken" --> Bridge
    end

    subgraph SN["ServiceNow Universe"]
        SNUser["SN User<br/>admin (own identity)"]
        SNCode["sn_auth_code<br/>(single-use)"]
        SNRefresh["sn_refresh_token<br/>(long-lived)"]
        SNUser -- "click Allow in popup" --> SNCode
        SNCode -- "DE exchanges via /oauth_token.do" --> SNRefresh
        SNRefresh -- "DE stores in bridge" --> Bridge
    end

    classDef ms fill:#1a2845,stroke:#5d8cf7,color:#e7ebf5
    classDef wif fill:#0d3340,stroke:#6dd3ff,color:#e7ebf5
    classDef de fill:#2a1d4a,stroke:#a78bfa,color:#e7ebf5
    classDef sn fill:#3d2f0a,stroke:#fbbf24,color:#e7ebf5
    class MS ms
    class WIF wif
    class DE de
    class SN sn
```

---

## 3. After the bridge exists — every search uses the SAME WIF token

```mermaid
sequenceDiagram
    autonumber
    actor User as User
    participant Browser as Browser
    participant DE as Discovery Engine
    participant SN as ServiceNow

    Note over Browser: gcpToken from STS already in memory (no re-login needed within ~1h)

    User->>Browser: list open incidents
    Browser->>DE: POST streamAssist (Bearer gcpToken, query, dataStoreSpecs)

    Note over DE: Server-side, DE does ALL of this transparently
    DE->>DE: decode Bearer to WIF principal
    DE->>DE: SELECT sn_refresh_token FROM bridge WHERE caller equals WIF principal

    DE->>SN: POST /oauth_token.do (refresh)
    SN-->>DE: sn_access_token (1h life)

    DE->>SN: GET /api/now/table/incident (Bearer sn_access_token)
    SN->>SN: ACLs run as user admin
    SN-->>DE: visible incidents

    DE->>DE: feed records to Gemini
    DE-->>Browser: grounded answer plus sources

    Note over User,SN: Browser never sees any SN tokens. DE handles the entire SN side server-side.
```

---

## Key takeaways

1. **Two completely separate identity universes**: Microsoft Entra has a user like `jchavez@contoso.onmicrosoft.com`; ServiceNow has its own user (e.g. `admin`). They are NOT federated to each other. They never know about each other.

2. **Discovery Engine is the bridge**: it stores a `{WIF principal → SN refresh_token}` mapping created during `acquireAndStoreRefreshToken`. This is the *only* place in the world that knows the two are linked.

3. **The browser ONLY ever sends the WIF GCP token** (after the bridge exists). DE looks up the SN refresh_token internally, refreshes it, queries SN — all server-side. No SN tokens ever leave DE.

4. **SN ACLs apply as the SN user that consented**: when the WIF user logged in to ServiceNow as `admin` during the consent popup, they implicitly said "act as `admin` against SN whenever I (this WIF principal) ask". Different WIF users could attach to different SN users by consenting differently.

5. **`acquireAndStoreRefreshToken` is per-user, one-time**: each WIF user must do this once per connector. If never done → `acquireAccessToken` returns 404 → streamAssist gets no SN data.
