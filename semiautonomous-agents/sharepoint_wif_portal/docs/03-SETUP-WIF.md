# Workforce Identity Federation Setup

> **Version**: 1.0.0 | **Last Updated**: 2026-04-03

**Navigation**: [README](../README.md) | [GCP Setup](01-SETUP-GCP.md) | [Entra ID](02-SETUP-ENTRA.md) | **WIF** | [Discovery](04-SETUP-DISCOVERY.md) | [Local Dev](05-LOCAL-DEV.md) | [Agent Engine](06-AGENT-ENGINE.md)

---

## Overview

Workforce Identity Federation (WIF) exchanges Microsoft tokens for GCP tokens, preserving user identity for ACL-aware access.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      TWO PROVIDERS REQUIRED                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   Workforce Pool: sharepoint-wif-pool                                       │
│   ├── Provider 1: entra-login-provider                                      │
│   │   └── Client ID: {client-id}           ← For Gemini Enterprise login   │
│   │                                                                          │
│   └── Provider 2: entra-agent-provider                                      │
│       └── Client ID: api://{client-id}     ← For agent WIF exchange        │
│                                                                             │
│   WHY TWO PROVIDERS?                                                        │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │ GE Login:  ID token    → aud: "client-id"        → Provider 1      │   │
│   │ Agent WIF: Access token → aud: "api://client-id" → Provider 2      │   │
│   │                                                                     │   │
│   │ Single provider = one flow breaks!                                  │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

![WIF Pool with Providers](../assets/wif-pool-providers.png)

*Workforce pool with two OIDC providers - one for login, one for agent WIF*

![Agent Provider Details](../assets/wif-agent-provider-details.png)

*Agent provider showing `api://` prefix in Client ID - critical for WIF exchange*

---

## Prerequisites

From previous steps:
- `TENANT_ID`: Your Microsoft Entra tenant ID
- `CLIENT_ID`: Your app registration client ID
- `CLIENT_SECRET`: Your client secret
- `ORG_ID`: Your GCP organization ID

---

## Step 1: Create Workforce Identity Pool

```bash
export ORG_ID=your-org-id
export POOL_ID=sharepoint-wif-pool

gcloud iam workforce-pools create $POOL_ID \
  --location=global \
  --organization=$ORG_ID \
  --display-name="SharePoint WIF Pool" \
  --description="Workforce pool for SharePoint document access"
```

---

## Step 2: Create Login Provider (No api:// prefix)

For Gemini Enterprise login flow:

```bash
export POOL_ID=sharepoint-wif-pool
export TENANT_ID=your-tenant-id
export CLIENT_ID=your-client-id          # NO api:// prefix
export CLIENT_SECRET=your-client-secret

gcloud iam workforce-pools providers create-oidc entra-login-provider \
  --workforce-pool=$POOL_ID \
  --location=global \
  --issuer-uri="https://sts.windows.net/${TENANT_ID}/" \
  --client-id="$CLIENT_ID" \
  --client-secret-value="$CLIENT_SECRET" \
  --attribute-mapping="google.subject=assertion.email.lowerAscii(),google.groups=assertion.groups,google.display_name=assertion.given_name" \
  --display-name="Entra Login Provider" \
  --web-sso-response-type="CODE" \
  --web-sso-assertion-claims-behavior="MERGE_USER_INFO_OVER_ID_TOKEN_CLAIMS"
```

**Note**: Issuer must be `https://sts.windows.net/{tenant}/` (v1.0 format), NOT `login.microsoftonline.com` (v2.0).

---

## Step 3: Create Agent Provider (WITH api:// prefix)

For ADK agent WIF token exchange:

```bash
export POOL_ID=sharepoint-wif-pool
export TENANT_ID=your-tenant-id
export CLIENT_ID_API="api://your-client-id"  # WITH api:// prefix
export CLIENT_SECRET=your-client-secret

gcloud iam workforce-pools providers create-oidc entra-agent-provider \
  --workforce-pool=$POOL_ID \
  --location=global \
  --issuer-uri="https://sts.windows.net/${TENANT_ID}/" \
  --client-id="$CLIENT_ID_API" \
  --client-secret-value="$CLIENT_SECRET" \
  --attribute-mapping="google.subject=assertion.email.lowerAscii(),google.groups=assertion.groups,google.display_name=assertion.given_name" \
  --display-name="Entra Agent Provider" \
  --description="WIF provider for agent token exchange with api:// audience" \
  --web-sso-response-type="CODE" \
  --web-sso-assertion-claims-behavior="MERGE_USER_INFO_OVER_ID_TOKEN_CLAIMS"
```

---

## Step 4: Grant IAM Permissions (ALL REQUIRED)

> **Critical**: Missing IAM bindings cause `FAILED_PRECONDITION` errors. Grant ALL roles below.

```bash
export PROJECT_ID=sharepoint-wif-agent
export POOL_ID=sharepoint-wif-pool
export MEMBER="principalSet://iam.googleapis.com/locations/global/workforcePools/$POOL_ID/*"

# All required roles for Gemini Enterprise + SharePoint
for role in \
  roles/aiplatform.user \
  roles/discoveryengine.admin \
  roles/discoveryengine.editor \
  roles/discoveryengine.user \
  roles/discoveryengine.viewer \
  roles/discoveryengine.notebookLmUser; do
  echo "Adding $role..."
  gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="$MEMBER" \
    --role="$role" --quiet
done
```

| Role | Purpose |
|------|---------|
| `roles/aiplatform.user` | Required for AI/assistant functionality |
| `roles/discoveryengine.admin` | Full Discovery Engine access |
| `roles/discoveryengine.editor` | Edit data stores and engines |
| `roles/discoveryengine.user` | Use search and assist APIs |
| `roles/discoveryengine.viewer` | Read-only access |
| `roles/discoveryengine.notebookLmUser` | NotebookLM features |

---

## Verification

### List Providers

```bash
gcloud iam workforce-pools providers list \
  --workforce-pool=sharepoint-wif-pool \
  --location=global
```

**Expected output:**

```
NAME                    DISPLAY_NAME           STATE
entra-login-provider    Entra Login Provider   ACTIVE
entra-agent-provider    Entra Agent Provider   ACTIVE
```

### Describe Provider Details

```bash
gcloud iam workforce-pools providers describe entra-agent-provider \
  --workforce-pool=sharepoint-wif-pool \
  --location=global
```

---

## Configuration Summary

```env
# WIF Configuration
WIF_POOL_ID=sharepoint-wif-pool
WIF_PROVIDER_ID=entra-agent-provider  # Use agent provider (with api:// client-id)
```

---

## Troubleshooting

| Error | Cause | Solution |
|-------|-------|----------|
| `issuer does not match` | Provider has v2.0 URL | Use `sts.windows.net` not `login.microsoftonline.com` |
| `audience does not match` (agent) | Provider missing `api://` | Use agent provider with api:// prefix |
| `audience does not match` (login) | Provider has `api://` | Use login provider without prefix |
| `PERMISSION_DENIED` | Missing IAM binding | Grant discoveryengine roles to pool |

---

## Next Step

→ [04-SETUP-DISCOVERY.md](04-SETUP-DISCOVERY.md) - Configure Discovery Engine with SharePoint
