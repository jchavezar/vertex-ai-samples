# Authentication Sequence — Mermaid Diagrams

End-to-end auth chain for the **combined SharePoint + ServiceNow + Google Search** portal.
Both connectors share a **single Discovery Engine app**, a **single backend**, and a
**single shared OAuth callback** that disambiguates connectors via `state.connector`.

> GitHub renders these mermaid blocks automatically.

---

## 1 · Overall — three independent toggles, one streamAssist call

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant Browser
    participant MS as Microsoft Entra
    participant STS as Google STS (WIF)
    participant Backend
    participant DE as Discovery Engine
    participant SP as SharePoint
    participant SN as ServiceNow

    Note over User,MS: PHASE 1 — User identity (every session)
    User->>Browser: Sign in with Microsoft
    Browser->>MS: MSAL loginPopup
    MS-->>Browser: id_token JWT

    Note over Browser,STS: PHASE 2 — STS exchange (every API call)
    Browser->>Backend: GET /api/connectors / X-Entra-Id-Token
    Backend->>STS: token-exchange
    STS-->>Backend: GCP access_token (WIF principal)

    Note over User,SP: PHASE 3 — Per-connector consent (one-time, per user, per connector)
    User->>Browser: Toggle SharePoint ON / Connect
    Browser->>Backend: GET /api/sharepoint/auth-url
    Backend-->>Browser: auth_url + state.connector="sharepoint"
    Browser->>MS: open consent popup
    MS-->>Browser: redirect to vertexaisearch oauth-redirect with code
    Browser->>Backend: POST /api/oauth/exchange { fullRedirectUrl }
    Backend->>Backend: decode state.connector → "sharepoint"
    Backend->>DE: acquireAndStoreRefreshToken on sharepoint connector
    DE-->>Backend: 200 OK (refresh token stored under WIF principal)
    Backend-->>Browser: { success: true, connector: "sharepoint" }

    User->>Browser: Toggle ServiceNow ON / Connect
    Note right of Browser: Same flow as above but state.connector="servicenow"<br/>and the popup goes to SN instead of Microsoft

    Note over User,SN: PHASE 4 — Search (every query)
    User->>Browser: Type query, click Search
    Browser->>Backend: POST /api/search { query, connectors: ["sharepoint","servicenow"] }
    Backend->>DE: streamAssist with UNION of dataStoreSpecs
    DE->>DE: SELECT refresh_tokens WHERE caller=WIF principal AND connector IN (...)
    DE->>SP: query as user
    DE->>SN: query as user
    SP-->>DE: per-user-ACL'd records
    SN-->>DE: per-user-ACL'd records
    DE->>DE: Gemini synthesis grounded in retrieved records
    DE-->>Backend: { answer, references, sessionInfo }
    Backend->>Backend: parse references (handles SharePoint + ServiceNow shapes)
    Backend-->>Browser: { answer, sources: [...with snippets...], session_token, ungrounded }
    Browser-->>User: render answer + per-connector source cards + snippet bubbles
```

---

## 2 · The shared OAuth callback — connector inferred from `state`

```mermaid
flowchart LR
    subgraph BrowserSide["Browser"]
        SPBtn["Connect SharePoint"]
        SNBtn["Connect ServiceNow"]
    end

    subgraph BackendSide["Backend (FastAPI)"]
        SPAuth["GET /api/sharepoint/auth-url<br/>state.connector='sharepoint'"]
        SNAuth["GET /api/servicenow/auth-url<br/>state.connector='servicenow'"]
        Callback["POST /api/oauth/exchange<br/>(decodes state.connector)"]
    end

    subgraph DiscoveryEngine
        SPCon["sharepoint connector<br/>:acquireAndStoreRefreshToken"]
        SNCon["servicenow connector<br/>:acquireAndStoreRefreshToken"]
    end

    SPBtn --> SPAuth
    SNBtn --> SNAuth
    SPAuth -->|opens MS popup| Callback
    SNAuth -->|opens SN popup| Callback
    Callback -->|connector=sharepoint| SPCon
    Callback -->|connector=servicenow| SNCon

    classDef be fill:#e6f4ea,stroke:#34a853,color:#0a2a6b
    classDef de fill:#fff3e0,stroke:#f9ab00,color:#0a2a6b
    class BackendSide be
    class DiscoveryEngine de
```

The browser opens a single OAuth callback URL regardless of which connector
initiated. The connector identity rides in the OAuth `state` parameter
(base64-encoded JSON `{origin, useBroadcastChannel, nonce, connector}`).
When the callback handler receives `code + state`, it decodes
`state.connector` and dispatches `acquireAndStoreRefreshToken` against the
correct connector. This keeps the URL surface small and the routing logic
self-describing.

---

## 3 · Toggle filters → streamAssist `dataStoreSpecs`

```mermaid
flowchart TB
    Toggle1{SharePoint<br/>toggle ON?}
    Toggle2{ServiceNow<br/>toggle ON?}
    Toggle3{Google Search<br/>toggle ON?}

    SP1["+5 SharePoint specs<br/>(file, page, comment, event, attachment)"]
    SN1["+5 ServiceNow specs<br/>(incident, knowledge, catalog, users, attachment)"]
    Web["webGroundingType=GOOGLE_SEARCH<br/>(separate API: PATCH /assistant)"]
    NoWeb["webGroundingType=DISABLED"]

    Build[("dataStoreSpecs[] payload")]
    StreamAssist[/"POST .../streamAssist<br/>{ query, toolsSpec.vertexAiSearchSpec.dataStoreSpecs }"/]

    Toggle1 -->|yes| SP1 --> Build
    Toggle1 -->|no| Build
    Toggle2 -->|yes| SN1 --> Build
    Toggle2 -->|no| Build
    Toggle3 -->|yes| Web
    Toggle3 -->|no| NoWeb

    Build --> StreamAssist
    Web -.assistant config.-> StreamAssist
    NoWeb -.assistant config.-> StreamAssist

    classDef tog fill:#e8f0fe,stroke:#4285f4,color:#0a2a6b
    classDef out fill:#fff3e0,stroke:#f9ab00,color:#0a2a6b
    class Toggle1,Toggle2,Toggle3 tog
    class StreamAssist out
```

The connector toggles change the **request body**; the Google Search toggle
changes the **assistant resource** itself (out-of-band PATCH). Both are
applied to the same `streamAssist` call.

---

## 4 · Citation parsing — SharePoint vs ServiceNow shapes

Discovery Engine returns references in two different shapes depending on the
connector. The combined backend's `_ref_to_source()` handles both:

```mermaid
flowchart LR
    Ref["streamAssist reference"]

    Has{"has<br/>documentMetadata?"}
    SPShape["SharePoint shape:<br/>documentMetadata.uri / .title<br/>content = highlighted snippet<br/>(with &lt;ddd/&gt; ellipses<br/>and &lt;c0&gt;...&lt;/c0&gt; tags)"]
    SNShape["ServiceNow shape:<br/>content = JSON string<br/>{title, url, description,<br/>file_type, entity_type, ...}"]

    Source["Normalized source:<br/>{title, url, snippet, file_type,<br/>entity_type, connector}"]

    Ref --> Has
    Has -->|yes| SPShape --> Source
    Has -->|no| SNShape --> Source

    classDef shape fill:#e6f4ea,stroke:#34a853,color:#0a2a6b
    class SPShape,SNShape shape
```

After parsing, references with the same URL are deduped but their snippets
are merged into a list — so a single source card can show multiple
highlighted excerpts that grounded different parts of the answer.

---

## 5 · Hallucination guard — assistant config + per-call ungrounded flag

```mermaid
flowchart TB
    Query[/"User query"/]

    Assistant["Discovery Engine assistant<br/>generationConfig.systemInstruction.<br/>additionalSystemInstruction:<br/>STRICT GROUNDING RULES — never fabricate IDs"]

    StreamAssist[/"streamAssist call"/]
    Refs{"references<br/>returned?"}

    NoRefs["answer text + sources_count=0<br/>→ backend sets ungrounded=true<br/>→ frontend shows orange warning"]
    Refs2["answer text + 1+ sources<br/>→ ungrounded=false<br/>→ render snippet bubbles"]

    Query --> Assistant
    Assistant --> StreamAssist
    StreamAssist --> Refs
    Refs -->|no| NoRefs
    Refs -->|yes| Refs2

    classDef warn fill:#fff3e0,stroke:#f9ab00,color:#0a2a6b
    classDef ok fill:#e6f4ea,stroke:#34a853,color:#0a2a6b
    class NoRefs warn
    class Refs2 ok
```

Two-layer defense:

1. **Assistant-level (preventive):** `additionalSystemInstruction` forbids
   fabricating CVE IDs, incident numbers, etc., and requires the verbatim
   *"No matching documents were found…"* response when retrieval is empty.
2. **Response-level (detective):** the backend flags `ungrounded=true` when
   the model returns text with no citations, and the frontend shows a
   prominent warning so users can spot model misbehavior even if the
   instruction is partially ignored.

---

## Key takeaways

1. **Three completely separate identity universes still apply.** Microsoft
   Entra (`user@tenant.onmicrosoft.com`), SharePoint (the same Microsoft
   identity, but a different OAuth scope), and ServiceNow (its own user
   table). They are NOT federated to each other. Discovery Engine is the
   bridge that maps a single WIF principal to per-connector refresh tokens.

2. **One backend, one engine, multiple connectors.** Both connectors' data
   stores live on the same Discovery Engine app; the backend issues a single
   `streamAssist` call with the union of selected specs. The toggles are
   pure request-body filters — they don't disconnect anything.

3. **Toggle OFF ≠ disconnect.** Flipping a connector toggle off just removes
   its `dataStoreSpecs` from the request. The refresh token stays stored,
   so flipping back on is instant (no re-consent).

4. **Google Search is assistant-level, not request-level.** It can't be
   passed in the `streamAssist` body — it has to be PATCHed onto the
   `assistant` resource. The backend's `/api/grounding/web` endpoint does
   this round-trip on every toggle click.

5. **Hallucinations are a model problem, not a retrieval problem.** Even
   with perfect retrieval, the model sometimes invents structured
   identifiers to "complete" tables. The strict `additionalSystemInstruction`
   tells it not to; the `ungrounded` warning catches the cases where it
   ignores the instruction anyway.
