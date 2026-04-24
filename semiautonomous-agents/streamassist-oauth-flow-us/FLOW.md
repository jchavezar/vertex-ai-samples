# StreamAssist · US — End-to-End Flow

> Single-file reference for running Gemini Enterprise streamAssist + a federated SharePoint connector + per-user ACLs in a **`us` regional** Discovery Engine, with **raw `client_id` audience** on the Workforce Identity Federation (WIF) provider.

---

## 1. Why this document exists

A customer reported "Gemini Enterprise + SharePoint federated connector + WIF only works when the engine is in `global`." We rebuilt the same setup in `us` regional location and it works end-to-end. The customer's symptom was real but the cause was **not the region** — it was four required configurations that are easy to miss when standing up a fresh engine. This doc captures every step + every gotcha so the next engagement doesn't waste time on the same dead end.

---

## 2. Architecture

```mermaid
flowchart LR
  subgraph G["Global resources (always)"]
    direction TB
    WIFPOOL["Workforce Identity<br/>Pool + OIDC Provider<br/>(audience = raw GUID)"]
    PORTAL["Entra Portal App<br/>(MSAL login)"]
    CONNAPP["Entra Connector App<br/>(SharePoint OAuth)<br/>+ AllPrincipals admin consent"]
  end

  subgraph US["us regional resources"]
    direction TB
    ENGINE["Discovery Engine app<br/>+ workforceIdentityPoolProvider<br/>+ user license"]
    CONN["SharePoint federated connector<br/>+ admin_filter.Site<br/>+ eeeu_enabled=true"]
    DS["5 entity datastores<br/>file/page/comment/event/attachment"]
    ENGINE --> CONN --> DS
  end

  subgraph SP["Microsoft 365"]
    SPSITES["SharePoint sites"]
  end

  Browser["React portal<br/>+ MSAL"] -->|id_token| Backend["FastAPI<br/>:8003"]
  Backend -->|STS exchange| WIFPOOL
  WIFPOOL -->|GCP token<br/>(WIF identity)| Backend
  Backend -->|us-discoveryengine.googleapis.com| ENGINE
  Browser -.MSAL.-> PORTAL
  Browser -.OAuth popup.-> CONNAPP
  DS <-->|federated query<br/>(per-user ACLs)| SPSITES
```

---

## 3. The full request flow, step by step

Numbers correspond to the boxes in `frontend/src/App.tsx`'s debug sidebar (`STAGE_INFO` map).

### Chain A — Identity (every session)

**A1. MSAL Login (`frontend/src/authConfig.ts`, `App.tsx:handleLogin`)**
- User clicks **Sign in with Microsoft**
- MSAL opens a popup pointed at `https://login.microsoftonline.com/<TENANT_ID>/oauth2/v2.0/authorize`
- Scopes requested: `openid profile email` only — **no `api://...` scope**
- Microsoft v2.0 endpoint returns an `id_token` whose `aud` claim is the **raw `<PORTAL_CLIENT_ID>` GUID** (no `api://` prefix)

**A2. STS Token Exchange (`backend/main.py:_exchange_token`)**
- Frontend sends the id_token to backend in `X-Entra-Id-Token` header
- Backend POSTs to `https://sts.googleapis.com/v1/token` with:
  - `grant_type` = `urn:ietf:params:oauth:grant-type:token-exchange`
  - `audience` = `//iam.googleapis.com/locations/global/workforcePools/<POOL_ID>/providers/<PROVIDER_ID>`
  - `subject_token` = the Entra id_token
  - `subject_token_type` = `urn:ietf:params:oauth:token-type:id_token`
- Returns a GCP access_token whose principal is `principal://iam.googleapis.com/locations/global/workforcePools/<POOL_ID>/subject/<sub-hash>` — the user's **WIF identity**

**A3. acquireAccessToken (probe)**
- Backend POSTs to `…/dataConnector:acquireAccessToken` on the SharePoint connector with the user's WIF token
- Returns 404 if the user has no per-user SharePoint refresh token stored on this connector → portal shows the **Connect SharePoint** button

### Chain B — SharePoint consent (one-time per user per connector)

**B1. Get Auth URL (`backend/main.py:get_auth_url`)**
- Backend generates a Microsoft OAuth URL for the **Connector App** (not the Portal App)
- `redirect_uri` is hard-coded to `https://vertexaisearch.cloud.google.com/oauth-redirect`
- `state` is base64-encoded JSON containing `{origin, useBroadcastChannel, nonce}`
- Backend stores the user's id_token under that `nonce` so the callback can later mint a WIF token
- Scope list (the working set we observed):
  ```
  openid offline_access
  https://<TENANT>.sharepoint.com/AllSites.Read
  https://<TENANT>.sharepoint.com/AllSites.Write
  https://<TENANT>.sharepoint.com/Files.Read.All
  https://<TENANT>.sharepoint.com/Files.ReadWrite.All
  https://<TENANT>.sharepoint.com/Sites.Manage.All
  https://<TENANT>.sharepoint.com/Sites.Read.All
  https://<TENANT>.sharepoint.com/Sites.Search.All
  ```

**B2. OAuth Consent Popup**
- Frontend opens the URL in a popup
- User signs in to Microsoft, grants consent
- Microsoft redirects to `vertexaisearch.cloud.google.com/oauth-redirect?code=…&state=<base64>`

**B3. OAuth Redirect → postMessage**
- The `vertexaisearch.cloud.google.com/oauth-redirect` page parses the `code` and `state`, then `postMessage`s `{fullRedirectUrl, code, state}` back to `window.opener`
- COOP gotcha: when the portal is on a different origin (e.g. `localhost:5174` vs `vertexaisearch.cloud.google.com`), the postMessage may be blocked. The code falls back to **popup-closed polling** (`App.tsx:285-310`)

### Convergence

**C. acquireAndStoreRefreshToken (`backend/main.py:oauth_exchange`)**
- Frontend forwards `fullRedirectUrl` to backend `/api/oauth/exchange`
- Backend re-runs the STS exchange with the stored id_token (looked up by `nonce`) → fresh GCP WIF token
- Backend POSTs to `…/dataConnector:acquireAndStoreRefreshToken` with:
  - `Authorization: Bearer <user's WIF GCP token>` ← critical: must be WIF token, not ADC, otherwise Discovery Engine stores under the service account identity and search later 404s
  - body: `{"fullRedirectUri": "<the full callback URL with ?code=… still in it>"}`
- Discovery Engine extracts the auth code, exchanges it for a SharePoint refresh token, stores it **keyed by the user's WIF identity hash**

### Chain D — Search

**D1. Search request**
- Frontend POSTs to `/api/search` with the question text + the cached `X-Entra-Id-Token` header

**D2. STS exchange (re-run, fresh)**
- Same as A2 — produces a fresh GCP WIF token

**D3. streamAssist call (`backend/main.py:_stream_assist`)**
- Backend POSTs to:
  ```
  https://us-discoveryengine.googleapis.com/v1alpha/projects/<PROJECT_NUMBER>/locations/us/collections/default_collection/engines/<ENGINE_ID>/assistants/default_assistant:streamAssist
  ```
- Headers:
  - `Authorization: Bearer <WIF GCP token>`
  - `X-Goog-User-Project: <PROJECT_NUMBER>` ← must be the **numeric project number**, not the project ID
- Body:
  ```json
  {
    "query": {"text": "..."},
    "toolsSpec": {
      "vertexAiSearchSpec": {
        "dataStoreSpecs": [
          {"dataStore": "projects/<PROJECT_NUMBER>/locations/us/collections/default_collection/dataStores/<CONNECTOR_ID>_file"},
          {"dataStore": "projects/<PROJECT_NUMBER>/locations/us/collections/default_collection/dataStores/<CONNECTOR_ID>_page"},
          ... // _comment, _event, _attachment
        ]
      }
    }
  }
  ```
  > `dataStoreSpecs` **must** be nested in `toolsSpec.vertexAiSearchSpec`. Putting it at the root is silently ignored — the response will come back ungrounded. This is the single most common cause of "no SharePoint sources" that isn't a config issue.

**D4. Discovery Engine internals**
- DE looks up the stored SharePoint refresh token using the WIF identity hash from the GCP token
- DE exchanges the refresh token for a fresh SharePoint access token
- DE issues federated SharePoint search queries scoped to that user's ACLs
- DE feeds matching documents into Gemini for grounded synthesis

**D5. Streaming response parsing**
- The response is a JSON array of chunks
- Each chunk's `answer.replies[].groundedContent.content.text` (when not `thought:true`) is the visible answer
- `groundedContent.textGroundingMetadata.references[]` contains the source documents (parse `ref.content` as JSON to get `title`, `url`, `description`, etc.)
- `sessionInfo.session` is the resource name to pass back as `session` in follow-up queries (do **not** use `assistToken` — it's returned but rejected as input)

---

## 4. The four mandatory configurations (the ones that are easy to miss)

If federated search returns 0 documents on a fresh `us` engine, **one of these four is missing**. They're all required regardless of region.

### 4.1. Engine-level `workforceIdentityPoolProvider`

Without this, Discovery Engine has no user identity to forward to SharePoint, so federated queries return 0 results. It's set on the engine's `WidgetConfig`, which is created lazily by Cloud Console the first time you visit the engine's overview page.

**How to set it:**
- Cloud Console → AI Applications → Apps → `<ENGINE_ID>`
- The "Set up your workforce identity" card appears on first load — click **Set up identity**
- Choose **Use a third-party identity provider**
- **Workforce pool ID:** `locations/global/workforcePools/<POOL_ID>`
- **Workforce provider ID:** `<PROVIDER_ID>`
- Click **Confirm Workforce Identity**

You'll see "Authentication configurations have been updated successfully" and "Workforce identity setup complete."

> **Symptom when missing:** streamAssist responds (HTTP 200) with a generic LLM answer that politely says "I couldn't find any information about X in our internal systems" and **NOT GROUNDED** — no sources. This is the silent killer.

### 4.2. Connector `params.admin_filter.Site` populated

The federated connector needs an explicit list of SharePoint site URLs to search. Empty list = nothing to search.

**How to set it (only at connector creation time):**
- Cloud Console wizard auto-populates this when you click "Authorize" on the SharePoint connector form
- Via REST: include in the `params` of `setUpDataConnector`:
  ```json
  "params": {
    "admin_filter": {
      "Site": [
        "https://<TENANT>.sharepoint.com",
        "https://<TENANT>.sharepoint.com/sites/<TARGET_SITE>"
      ],
      "Path": []
    },
    "eeeu_enabled": true,
    ...
  }
  ```

> The PATCH endpoint **does not allow** `admin_filter` to be updated post-creation. If you forgot it, you have to delete the connector (which takes hours to fully purge) and recreate.

### 4.3. Per-user `acquireAndStoreRefreshToken`

Even with `AllPrincipals` admin consent on the Connector App and the engine-level WIF set, each user that searches must have **their own** SharePoint refresh token stored under their WIF identity hash on this specific connector.

**How it gets stored:**
- Normal flow: portal → Connect SharePoint → consent popup → vertexaisearch redirect → postMessage → backend `/api/oauth/exchange` → `…:acquireAndStoreRefreshToken`
- Programmatic / bootstrap flow:
  ```bash
  # 1. Get user's id_token from MSAL (from sessionStorage)
  # 2. Exchange for WIF GCP token via STS
  # 3. Generate Microsoft auth URL (same scopes as in 3·B1) and complete OAuth
  # 4. Capture full redirect URL
  curl -X POST \
    -H "Authorization: Bearer <USER_WIF_GCP_TOKEN>" \
    -H "X-Goog-User-Project: <PROJECT_NUMBER>" \
    -H "Content-Type: application/json" \
    "https://us-discoveryengine.googleapis.com/v1alpha/projects/<PROJECT_NUMBER>/locations/us/collections/<CONNECTOR_ID>/dataConnector:acquireAndStoreRefreshToken" \
    -d '{"fullRedirectUri": "<the vertexaisearch.cloud.google.com/oauth-redirect?code=…&state=…>"}'
  ```
- Verify with `…:acquireAccessToken` (`{}` body) — should return a `refreshTokenInfo` block with the broad scope list, not 404

> **Symptom when missing:** streamAssist responds with "I couldn't find any information about X in SharePoint" — note the **"in SharePoint"** wording difference vs. step 4.1's "in our internal systems"

### 4.4. User license assigned to the engine

Each user querying the engine must hold a `SUBSCRIPTION_TIER_SEARCH_AND_ASSISTANT` license seat for that specific engine.

**How to set it:**
- Cloud Console → AI Applications → Apps → `<ENGINE_ID>` → **Manage subscriptions** → assign the user
- Licenses are per-engine (not project-wide), so a fresh `us` engine starts with zero assignments even if the project's `global` engine already has them

> **Symptom when missing:** API returns HTTP 400 with `LICENSE_WITHOUT_SUBSCRIPTION_TIER` and `requiredSubscriptionTier: "SUBSCRIPTION_TIER_SEARCH_AND_ASSISTANT"`

---

## 5. Replication checklist (greenfield to grounded answer)

```
[ ] GCP project with Discovery Engine API + AI Platform API enabled
[ ] Workforce Identity Pool exists at locations/global/workforcePools/<POOL_ID>
[ ] OIDC Provider in that pool with:
     • client_id = raw GUID of the Portal App (NO api:// prefix)
     • issuer_uri = https://login.microsoftonline.com/<TENANT_ID>/v2.0  (or v1.0 sts.windows.net works too)
     • attribute_mapping: google.subject = assertion.sub
[ ] WIF principalSet has IAM roles on the project:
     • roles/discoveryengine.editor   (covers streamAssist permission)
     • roles/discoveryengine.user
     • roles/discoveryengine.viewer
[ ] Entra Portal App registered as SPA with redirect_uri = http://<frontend-host> ; oauth2AllowIdTokenImplicitFlow = true
[ ] Entra Connector App registered as Web with redirect_uri = https://vertexaisearch.cloud.google.com/oauth-redirect
     • Delegated SharePoint permissions: AllSites.Read, AllSites.Write, Files.Read.All, Files.ReadWrite.All,
       Sites.Manage.All, Sites.Read.All, Sites.Search.All
     • Microsoft Graph: openid, offline_access
     • Admin consent granted (AllPrincipals)
     • Client secret created and saved
[ ] Discovery Engine app created at locations/us with searchTier=ENTERPRISE + searchAddOns=[LLM]
[ ] SharePoint federated connector created via setUpDataConnector with:
     • params.admin_filter.Site populated         ← (config #4.2)
     • params.eeeu_enabled = true
     • params.refresh_token = an admin-bootstrapped SharePoint refresh token
     • actionConfig.actionParams.{tenant_id, client_id, client_secret} set
     • actionConfig.createBapConnection = true
[ ] Engine.dataStoreIds patched to include the 5 connector child datastores (_file, _page, _comment, _event, _attachment)
[ ] Engine workforceIdentityPoolProvider set via Console "Set up identity"   ← (config #4.1)
[ ] Each user assigned a license on this engine                              ← (config #4.4)
[ ] Each user runs the portal Connect SharePoint flow once                   ← (config #4.3)
[ ] Search returns grounded answers
```

---

## 6. Verification — the three signals of success

After running the portal flow end-to-end with a real query:

1. **Network panel** shows requests hitting `us-discoveryengine.googleapis.com` (not `discoveryengine.googleapis.com`)
2. **Decoded id_token** has `aud` = the raw Portal App GUID (no `api://` prefix). Decode at jwt.io.
3. **streamAssist response** has `groundedContent.textGroundingMetadata.references[]` populated → the simple tester shows a green **GROUNDED** badge with source document cards

If all three are true, the proof is closed.

---

## 7. Failure-mode lookup table

| Symptom | Most likely cause | Where to fix |
|---|---|---|
| `LICENSE_WITHOUT_SUBSCRIPTION_TIER` (HTTP 400) | User has no license on this engine | §4.4 |
| `acquireAccessToken` returns 404 "authorization not found" | No per-user refresh token stored | §4.3 |
| streamAssist returns answer, says *"…in our internal systems"*, NOT GROUNDED | Engine-level `workforceIdentityPoolProvider` missing | §4.1 |
| streamAssist returns answer, says *"…in SharePoint"*, NOT GROUNDED | Per-user refresh token missing on this connector | §4.3 |
| Direct datastore search returns empty `summary` block | Connector `admin_filter.Site` empty | §4.2 (recreate connector) |
| HTTP 401 on streamAssist (other endpoints work) | WIF principal missing `roles/discoveryengine.editor` | grant on the project |
| HTTP 500 on streamAssist | `X-Goog-User-Project` header is project ID, not project number | use the numeric project number |
| STS exchange returns "audience does not match" | WIF provider `--client-id` doesn't match the id_token's `aud` claim | re-create the OIDC provider with the correct value (see §4 of the checklist) |
| `Last unit does not have enough valid bits` on the redirect page | The `state` param wasn't base64-encoded JSON | base64-encode `{origin, useBroadcastChannel, nonce}` before passing |
| OAuth popup closes immediately with no consent screen | Cached MSAL session + redirect succeeded silently → postMessage was blocked by COOP | use the popup-closed polling fallback (already implemented) |

---

## 8. Why the "us doesn't work" claim was wrong

The customer's working setup happened to be in `global` only because that engine had been provisioned earlier with §4.1, §4.2, §4.3, §4.4 all completed. When they tried `us`, they created a fresh engine + connector but didn't notice the four post-creation configurations were missing. The region was a red herring. **The same four steps are required in `global`; they just weren't aware of them because their `global` setup was working before they started looking at `us`.**

The technical chain — STS exchange, raw client_id audience, streamAssist API contract, federated SharePoint, per-user ACLs — behaves identically between `global` and `us`. The only code differences are:
- API host: `discoveryengine.googleapis.com` (global) vs `us-discoveryengine.googleapis.com` (regional)
- Resource paths: `/locations/global/` vs `/locations/us/`
- WIF audience path stays at `/locations/global/workforcePools/...` regardless (workforce pools are inherently global)

That's it.
