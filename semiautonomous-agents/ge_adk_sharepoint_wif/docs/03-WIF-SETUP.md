# Workforce Identity Federation Setup

> **Navigation**: [README](../README.md) | [Overview](01-OVERVIEW.md) | [Entra ID](02-ENTRA-ID-SETUP.md) | **WIF** | [Local Testing](04-LOCAL-TESTING.md) | [Agent Engine](05-AGENT-ENGINE.md) | [GE Setup](06-GEMINI-ENTERPRISE.md)

## Working Configuration Reference

**IMPORTANT**: Two WIF providers are needed - one for GE login, one for agent WIF exchange.

| Provider | Client ID | Purpose |
|----------|-----------|---------|
| `entra-id-oidc-pool-provider-de` | `ecbfa47e-a75c-403c-a13b-f27eff101e4e` | Gemini Enterprise login |
| `entra-id-agent-provider` | `api://ecbfa47e-a75c-403c-a13b-f27eff101e4e` | Agent WIF exchange |

Both use:
- **Pool ID**: `entra-id-oidc-pool-d`
- **Issuer URI**: `https://sts.windows.net/de46a3fd-0d68-4b25-8343-6eb5d71afce9/`

---

## Why Two Providers?

| Flow | Token Audience | Provider Needed |
|------|---------------|-----------------|
| GE Login | `ecbfa47e-...` (no prefix) | Original provider |
| Agent WIF | `api://ecbfa47e-...` (with prefix) | Agent provider |

- **GE Login**: Uses ID tokens with standard audience (client ID only)
- **Agent WIF**: Uses access tokens with custom scope audience (`api://` prefix)

If you use only one provider, one flow will break.

---

## Step 1: Create Workforce Identity Pool

```bash
export ORG_ID=your-org-id
export POOL_ID=entra-id-oidc-pool-d

gcloud iam workforce-pools create $POOL_ID \
    --location=global \
    --organization=$ORG_ID \
    --display-name="Entra ID OIDC Pool"
```

---

## Step 2: Create Login Provider (for GE Login)

```bash
export POOL_ID=entra-id-oidc-pool-d
export TENANT_ID=de46a3fd-0d68-4b25-8343-6eb5d71afce9
export CLIENT_ID=ecbfa47e-a75c-403c-a13b-f27eff101e4e
export CLIENT_SECRET=your-client-secret

gcloud iam workforce-pools providers create-oidc entra-id-oidc-pool-provider-de \
    --workforce-pool=$POOL_ID \
    --location=global \
    --issuer-uri="https://sts.windows.net/${TENANT_ID}/" \
    --client-id="$CLIENT_ID" \
    --client-secret-value="$CLIENT_SECRET" \
    --attribute-mapping="google.subject=assertion.sub" \
    --display-name="Entra ID Provider" \
    --web-sso-response-type="CODE" \
    --web-sso-assertion-claims-behavior="MERGE_USER_INFO_OVER_ID_TOKEN_CLAIMS"
```

---

## Step 3: Create Agent Provider (for Agent WIF)

**CRITICAL**: Client ID must have `api://` prefix.

```bash
export POOL_ID=entra-id-oidc-pool-d
export TENANT_ID=de46a3fd-0d68-4b25-8343-6eb5d71afce9
export CLIENT_ID=api://ecbfa47e-a75c-403c-a13b-f27eff101e4e
export CLIENT_SECRET=your-client-secret

gcloud iam workforce-pools providers create-oidc entra-id-agent-provider \
    --workforce-pool=$POOL_ID \
    --location=global \
    --issuer-uri="https://sts.windows.net/${TENANT_ID}/" \
    --client-id="$CLIENT_ID" \
    --client-secret-value="$CLIENT_SECRET" \
    --attribute-mapping="google.subject=assertion.sub" \
    --display-name="Entra ID Agent Provider" \
    --description="WIF provider for ADK agents with custom API scope" \
    --web-sso-response-type="CODE" \
    --web-sso-assertion-claims-behavior="MERGE_USER_INFO_OVER_ID_TOKEN_CLAIMS"
```

---

## Step 4: Grant IAM Permissions

```bash
export PROJECT_ID=deloitte-plantas
export POOL_ID=entra-id-oidc-pool-d

# Grant Discovery Engine access to all pool members
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="principalSet://iam.googleapis.com/locations/global/workforcePools/$POOL_ID/*" \
    --role="roles/discoveryengine.viewer"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="principalSet://iam.googleapis.com/locations/global/workforcePools/$POOL_ID/*" \
    --role="roles/discoveryengine.editor"
```

---

## Verify Providers

```bash
# List all providers
gcloud iam workforce-pools providers list \
  --workforce-pool=entra-id-oidc-pool-d \
  --location=global

# Check login provider
gcloud iam workforce-pools providers describe entra-id-oidc-pool-provider-de \
  --workforce-pool=entra-id-oidc-pool-d \
  --location=global

# Check agent provider
gcloud iam workforce-pools providers describe entra-id-agent-provider \
  --workforce-pool=entra-id-oidc-pool-d \
  --location=global
```

---

## Environment Variables

```env
WIF_POOL_ID=entra-id-oidc-pool-d
WIF_PROVIDER_ID=entra-id-agent-provider
```

**Note**: Agent uses `entra-id-agent-provider`, NOT `entra-id-oidc-pool-provider-de`.

---

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `issuer does not match` | Provider has v2.0 URL | Update to `sts.windows.net` |
| `audience does not match` (agent) | Provider missing `api://` | Use agent provider with prefix |
| `audience does not match` (login) | Provider has `api://` | Use login provider without prefix |
| GE login fails after agent works | Using single provider | Create two separate providers |
