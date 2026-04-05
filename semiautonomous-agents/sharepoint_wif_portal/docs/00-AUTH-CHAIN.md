# The Authentication Chain

**Version:** 1.0.0 | **Last Updated:** 2026-04-05

**Navigation**: [README](../README.md) | **00-Auth Chain** | [Index](00-INDEX.md)

---

## Why This Document Exists

This is the document that took **5 days and multiple LLMs to figure out** because the product team does not currently maintain public documentation for this authentication flow.

Every other document in this guide covers things you can find on Google — how to create a GCP project, register an Entra app, deploy Cloud Run. **This document covers what you cannot find anywhere else**: the exact chain of requirements that makes `streamAssist` work with a federated SharePoint connector under a real user's identity.

If you skip this and go straight to setup, you will get one of these symptoms:
- `streamAssist` returns a response but with zero SharePoint sources
- Gemini responds from its training data instead of your documents
- `FAILED_PRECONDITION` or `PERMISSION_DENIED` errors with no clear cause
- STS returns `invalid_grant` or audience mismatch errors

**Read this first. Set up second.**

---

## The Core Chain

There are exactly **3 steps** that must happen in sequence for every `streamAssist` call to reach SharePoint under the user's identity. All 3 are required. Missing any one of them silently breaks the chain.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    THE STREAMASSIST AUTHENTICATION CHAIN                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   STEP 1: Microsoft JWT (Entra ID)                                          │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │  User logs in via MSAL → receives ID Token                          │   │
│   │                                                                     │   │
│   │  Scope:    api://{client-id}/user_impersonation                     │   │
│   │  Audience: api://{client-id}  ← MUST match WIF provider audience   │   │
│   │                                                                     │   │
│   │  ⚠️  Requires oauth2AllowIdTokenImplicitFlow: true in Entra         │   │
│   │     Without this, WIF cannot validate the token                     │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                       │                                     │
│                                       ▼                                     │
│   STEP 2: Exchange JWT for GCP Token via STS                                │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │  POST https://sts.googleapis.com/v1/token                           │   │
│   │  {                                                                  │   │
│   │    "audience": "//iam.googleapis.com/locations/global/             │   │
│   │                 workforcePools/{POOL_ID}/providers/{PROVIDER_ID}", │   │
│   │    "grantType": "urn:ietf:params:oauth:grant-type:token-exchange", │   │
│   │    "requestedTokenType": "urn:ietf:params:oauth:token-type:        │   │
│   │                           access_token",                           │   │
│   │    "subjectToken": "<microsoft-jwt>",                              │   │
│   │    "subjectTokenType": "urn:ietf:params:oauth:token-type:jwt",    │   │
│   │    "scope": "https://www.googleapis.com/auth/cloud-platform"      │   │
│   │  }                                                                  │   │
│   │                                                                     │   │
│   │  Returns: GCP access token that carries the user's identity        │   │
│   │  This token is what enforces SharePoint ACLs downstream            │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                       │                                     │
│                                       ▼                                     │
│   STEP 3: Call streamAssist with dataStoreSpecs                             │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │  POST /engines/{ENGINE_ID}/assistants/default_assistant:streamAssist│   │
│   │  Authorization: Bearer {GCP_TOKEN_FROM_STEP_2}                      │   │
│   │                                                                     │   │
│   │  ⚠️  dataStoreSpecs is REQUIRED — this is the #1 silent failure    │   │
│   │                                                                     │   │
│   │  Without dataStoreSpecs → Gemini responds from training data only  │   │
│   │  With dataStoreSpecs    → Gemini searches your SharePoint docs     │   │
│   │                                                                     │   │
│   │  ⚠️  To get the dataStore IDs you need IAM permissions (see below) │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

> **Code:** [`backend/main.py#L44`](https://github.com/jchavezar/vertex-ai-samples/blob/main/semiautonomous-agents/sharepoint_wif_portal/backend/main.py#L44) — `exchange_token()` — the exact STS call (Steps 1→2)
> [`agent/discovery_engine.py#L103`](https://github.com/jchavezar/vertex-ai-samples/blob/main/semiautonomous-agents/sharepoint_wif_portal/agent/discovery_engine.py#L103) — same exchange inside the ADK agent
> [`agent/discovery_engine.py#L254`](https://github.com/jchavezar/vertex-ai-samples/blob/main/semiautonomous-agents/sharepoint_wif_portal/agent/discovery_engine.py#L254) — `streamAssist` call with `dataStoreSpecs` (Step 3)

---

## Requirement 1: Entra ID Must Issue ID Tokens

**What most guides miss:** By default, Entra ID does not include groups or allow ID token implicit flow. Both are required for WIF to validate the token and enforce SharePoint ACLs.

Set this in the Entra app manifest:

```json
{
  "oauth2AllowIdTokenImplicitFlow": true,
  "groupMembershipClaims": "SecurityGroup",
  "optionalClaims": {
    "idToken": [{"name": "groups", "essential": false}],
    "accessToken": [{"name": "groups", "essential": false}]
  }
}
```

And in **Authentication → Implicit grant and hybrid flows**, check:
- ✓ **ID tokens (used for implicit and hybrid flows)**

**What breaks without it:** WIF receives the token and rejects it with `FAILED_PRECONDITION`. The error message does not tell you that `oauth2AllowIdTokenImplicitFlow` is the cause.

> **Code:** [`frontend/src/authConfig.ts#L31`](https://github.com/jchavezar/vertex-ai-samples/blob/main/semiautonomous-agents/sharepoint_wif_portal/frontend/src/authConfig.ts#L31) — scope definition (`api://{client-id}/user_impersonation`)

---

## Requirement 2: Two WIF Providers — Not One

**What most guides miss:** Entra ID issues tokens with different audiences depending on the flow. A single WIF provider cannot handle both.

| Flow | Token type | Audience | WIF Provider |
|------|-----------|----------|--------------|
| Gemini Enterprise user login | ID token | `{client-id}` (no prefix) | `entra-login-provider` |
| Custom portal / ADK agent | Access token | `api://{client-id}` | `entra-agent-provider` |

If you use the wrong provider for a flow, STS returns:
```
invalid_grant: The audience in ID Token does not match the configured audience
```

The `api://` prefix is not optional — it is how Entra distinguishes ID tokens from access tokens in the audience claim. WIF validates this exactly.

**Provider 1 — GE user login (no prefix):**
```bash
gcloud iam workforce-pools providers create-oidc entra-login-provider \
  --workforce-pool=$POOL_ID \
  --issuer-uri="https://sts.windows.net/${TENANT_ID}/" \
  --client-id="${CLIENT_ID}" \                        # NO api:// prefix
  --web-sso-response-type="CODE"
```

**Provider 2 — Agent WIF exchange (WITH api:// prefix):**
```bash
gcloud iam workforce-pools providers create-oidc entra-agent-provider \
  --workforce-pool=$POOL_ID \
  --issuer-uri="https://sts.windows.net/${TENANT_ID}/" \
  --client-id="api://${CLIENT_ID}" \                  # WITH api:// prefix
  --web-sso-response-type="CODE"
```

> **Important:** The issuer URI must be `https://sts.windows.net/{tenant}/` (v1.0 format). Using `login.microsoftonline.com` (v2.0) causes token validation failures.

> **Code:** [`docs/03-SETUP-WIF.md`](03-SETUP-WIF.md) — full provider creation commands and IAM bindings

---

## Requirement 3: `dataStoreSpecs` is REQUIRED

**What most guides miss:** The `streamAssist` API does not automatically know which data store to search. Without `dataStoreSpecs` in the payload, Discovery Engine answers from Gemini's training data only — no SharePoint, no grounding, no sources. The API returns HTTP 200 with a plausible-looking answer. There is no error.

```python
# ❌ WITHOUT dataStoreSpecs — HTTP 200 but no SharePoint
payload = {
    "query": {"text": query},
    "session": session_name
}
# Result: Gemini responds from training data. Zero SharePoint sources.

# ✅ WITH dataStoreSpecs — grounded from SharePoint
payload = {
    "query": {"text": query},
    "session": session_name,
    "toolsSpec": {
        "vertexAiSearchSpec": {
            "dataStoreSpecs": [
                {
                    "dataStore": "projects/{PROJECT_NUMBER}/locations/global"
                                 "/collections/default_collection"
                                 "/dataStores/{DATA_STORE_ID}"
                }
            ]
        }
    }
}
# Result: Grounded answer citing SharePoint documents with ACL enforcement
```

> **Code:** [`agent/discovery_engine.py#L254`](https://github.com/jchavezar/vertex-ai-samples/blob/main/semiautonomous-agents/sharepoint_wif_portal/agent/discovery_engine.py#L254) — full `streamAssist` payload construction

---

## Requirement 4: IAM Permissions to List DataStore IDs

**What most guides miss:** You need the `DATA_STORE_ID` to build `dataStoreSpecs`. To fetch it programmatically (rather than hardcoding it from the console), the calling identity needs `discoveryengine.viewer`. Without it, the list API returns `PERMISSION_DENIED` — and if you swallow that error, `dataStoreSpecs` ends up empty, which lands you back in Requirement 3's failure mode.

```bash
# Grant to the WIF pool principal (covers all federated users)
export MEMBER="principalSet://iam.googleapis.com/locations/global/workforcePools/${POOL_ID}/*"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="$MEMBER" \
  --role="roles/discoveryengine.viewer"   # list dataStores

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="$MEMBER" \
  --role="roles/discoveryengine.user"     # call streamAssist
```

| Role | What it unlocks |
|------|----------------|
| `roles/discoveryengine.viewer` | `GET /dataStores` — list store IDs to build `dataStoreSpecs` |
| `roles/discoveryengine.user` | `streamAssist` — the actual search call |
| `roles/discoveryengine.admin` | Full control — needed only for creating/modifying stores |

Fetching the dataStore ID programmatically:

```python
def get_datastores(project_number: str, gcp_token: str) -> list:
    url = (
        f"https://discoveryengine.googleapis.com/v1alpha/projects/"
        f"{project_number}/locations/global/collections/"
        f"default_collection/dataStores"
    )
    resp = requests.get(url, headers={"Authorization": f"Bearer {gcp_token}"})
    if resp.ok:
        return [ds["name"] for ds in resp.json().get("dataStores", [])]
    return []
```

> **Code:** [`backend/main.py#L44`](https://github.com/jchavezar/vertex-ai-samples/blob/main/semiautonomous-agents/sharepoint_wif_portal/backend/main.py#L44) — `exchange_token()` produces the GCP token passed here

---

## Failure Mode Reference

| Symptom | Root Cause | Fix |
|---------|-----------|-----|
| `streamAssist` returns answer with no SharePoint sources | Missing `dataStoreSpecs` | Add `toolsSpec.vertexAiSearchSpec.dataStoreSpecs` to payload |
| `dataStoreSpecs` is empty at runtime | Missing `discoveryengine.viewer` IAM role | Grant role to WIF pool principal |
| `invalid_grant: audience does not match` | Wrong WIF provider for token type | Use `entra-agent-provider` (with `api://`) for access tokens |
| `FAILED_PRECONDITION` on STS exchange | `oauth2AllowIdTokenImplicitFlow` is false | Set to `true` in Entra manifest |
| `PERMISSION_DENIED` on streamAssist | Missing `discoveryengine.user` role | Grant role to WIF pool principal |
| Token exchange succeeds but SharePoint returns 403 | WIF provider audience mismatch | Verify `api://` prefix in `entra-agent-provider` client ID |
| Gemini answers from training data (no citations) | `dataStoreSpecs` missing or empty | Check `DATA_STORE_ID` env var and IAM permissions |

---

## Where to Go Next

This document covers the chain. The setup guides implement it:

| Document | Implements |
|----------|-----------|
| [02-SETUP-ENTRA.md](02-SETUP-ENTRA.md) | `oauth2AllowIdTokenImplicitFlow`, scopes, redirect URIs |
| [03-SETUP-WIF.md](03-SETUP-WIF.md) | Two WIF providers, IAM bindings |
| [04-SETUP-DISCOVERY.md](04-SETUP-DISCOVERY.md) | SharePoint connector, dataStore IDs |
| [05-LOCAL-DEV.md](05-LOCAL-DEV.md) | Running the full chain locally end-to-end |
| [08-ADK-AGENT.md](08-ADK-AGENT.md) | Same chain inside the ADK agent |
