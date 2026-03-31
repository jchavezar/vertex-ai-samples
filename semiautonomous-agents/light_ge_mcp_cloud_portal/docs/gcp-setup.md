# GCP Infrastructure Setup

[← Back to Main README](../README.md) | [Security Flow](security-flow.md)

## Overview

This guide covers all GCP infrastructure required for the ServiceNow Agent Portal.

## Prerequisites

- Google Cloud project with billing enabled
- `gcloud` CLI authenticated
- Required APIs enabled

```bash
# Enable required APIs
gcloud services enable \
  aiplatform.googleapis.com \
  run.googleapis.com \
  iam.googleapis.com \
  sts.googleapis.com \
  iamcredentials.googleapis.com
```

## 1. Workforce Identity Federation

WIF allows the frontend to exchange Entra ID tokens for GCP credentials without storing secrets.

### Create Workforce Pool

```bash
# Set variables
export ORG_ID="your-organization-id"
export POOL_ID="entra-id-oidc-pool"
export PROVIDER_ID="entra-id-provider"
export ENTRA_TENANT_ID="your-tenant-id"
export ENTRA_CLIENT_ID="your-client-id"

# Create workforce pool
gcloud iam workforce-pools create $POOL_ID \
  --organization=$ORG_ID \
  --location=global \
  --display-name="Entra ID OIDC Pool"
```

### Create OIDC Provider

```bash
# Create provider with Entra ID configuration
gcloud iam workforce-pools providers create-oidc $PROVIDER_ID \
  --workforce-pool=$POOL_ID \
  --location=global \
  --issuer-uri="https://login.microsoftonline.com/$ENTRA_TENANT_ID/v2.0" \
  --client-id=$ENTRA_CLIENT_ID \
  --attribute-mapping="google.subject=assertion.sub,google.display_name=assertion.preferred_username"
```

### Grant IAM Permissions

```bash
export PROJECT_ID="your-project-id"

# Allow WIF users to use Vertex AI
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="principalSet://iam.googleapis.com/locations/global/workforcePools/$POOL_ID/*" \
  --role="roles/aiplatform.user"
```

### Verify Configuration

```bash
# List pools
gcloud iam workforce-pools list --organization=$ORG_ID --location=global

# List providers
gcloud iam workforce-pools providers list \
  --workforce-pool=$POOL_ID \
  --location=global
```

## 2. Cloud Run (MCP Server)

### Deploy MCP Server

```bash
cd mcp-server

# Deploy with authentication required
gcloud run deploy servicenow-mcp \
  --source . \
  --region us-central1 \
  --no-allow-unauthenticated \
  --set-env-vars="SERVICENOW_INSTANCE_URL=https://your-instance.service-now.com"
```

### Configure IAM for Agent Engine

The Agent Engine service account needs permission to invoke the MCP server.

```bash
export PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")

# Grant Cloud Run invoker to Agent Engine SA
gcloud run services add-iam-policy-binding servicenow-mcp \
  --member="serviceAccount:service-$PROJECT_NUMBER@gcp-sa-aiplatform-re.iam.gserviceaccount.com" \
  --role="roles/run.invoker" \
  --region=us-central1
```

### Add Environment Variables (Optional)

For Basic Auth fallback during testing:

```bash
gcloud run services update servicenow-mcp \
  --region=us-central1 \
  --update-env-vars="SERVICENOW_BASIC_AUTH_USER=admin,SERVICENOW_BASIC_AUTH_PASS=your-password"
```

## 3. Agent Engine (Vertex AI)

### Required IAM Roles

Grant these roles to the compute service account:

```bash
# For Agent Engine session management
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
  --role="roles/aiplatform.admin"

# For Gemini API access
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
  --role="roles/aiplatform.user"

# Grant to Agent Engine service account
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:service-$PROJECT_NUMBER@gcp-sa-aiplatform-re.iam.gserviceaccount.com" \
  --role="roles/aiplatform.admin"
```

### Deploy Agent

```bash
cd agent

# Set environment
export GOOGLE_CLOUD_PROJECT=$PROJECT_ID
export GOOGLE_CLOUD_LOCATION=us-central1
export SERVICENOW_MCP_URL="https://servicenow-mcp-$PROJECT_NUMBER.us-central1.run.app/sse"

# Deploy
uv run python deploy.py
```

### Verify Deployment

```bash
# List agent engines
gcloud ai reasoning-engines list --region=us-central1

# Get specific engine
gcloud ai reasoning-engines describe AGENT_ENGINE_ID --region=us-central1
```

## 4. IAM Summary

### Service Accounts

| Service Account | Purpose |
|-----------------|---------|
| `PROJECT_NUMBER-compute@developer.gserviceaccount.com` | Default compute SA, runs Agent Engine |
| `service-PROJECT_NUMBER@gcp-sa-aiplatform-re.iam.gserviceaccount.com` | Agent Engine internal SA |

### Required Bindings

```bash
# Summary of all IAM bindings needed

# 1. WIF users → Vertex AI
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="principalSet://iam.googleapis.com/locations/global/workforcePools/$POOL_ID/*" \
  --role="roles/aiplatform.user"

# 2. Compute SA → AI Platform Admin (for sessions)
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
  --role="roles/aiplatform.admin"

# 3. Agent Engine SA → Cloud Run Invoker
gcloud run services add-iam-policy-binding servicenow-mcp \
  --member="serviceAccount:service-$PROJECT_NUMBER@gcp-sa-aiplatform-re.iam.gserviceaccount.com" \
  --role="roles/run.invoker" \
  --region=us-central1

# 4. Agent Engine SA → AI Platform Admin
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:service-$PROJECT_NUMBER@gcp-sa-aiplatform-re.iam.gserviceaccount.com" \
  --role="roles/aiplatform.admin"
```

## 5. Environment Variables Reference

### MCP Server (Cloud Run)

| Variable | Description | Example |
|----------|-------------|---------|
| `SERVICENOW_INSTANCE_URL` | ServiceNow instance URL | `https://dev12345.service-now.com` |
| `SERVICENOW_BASIC_AUTH_USER` | Fallback username (optional) | `admin` |
| `SERVICENOW_BASIC_AUTH_PASS` | Fallback password (optional) | `password` |
| `PORT` | Server port | `8080` (default) |
| `MCP_TRANSPORT` | Transport type | `sse` (default) |

### Agent Engine

| Variable | Description | Example |
|----------|-------------|---------|
| `GOOGLE_CLOUD_PROJECT` | GCP project ID | `my-project` |
| `GOOGLE_CLOUD_LOCATION` | Region | `us-central1` |
| `SERVICENOW_MCP_URL` | MCP server SSE endpoint | `https://xxx.run.app/sse` |
| `STAGING_BUCKET` | GCS bucket for deployment | `gs://my-project-staging` |

## Troubleshooting

### Check IAM Bindings

```bash
# View all project IAM
gcloud projects get-iam-policy $PROJECT_ID --format=json | jq '.bindings[] | select(.role | contains("aiplatform"))'

# View Cloud Run IAM
gcloud run services get-iam-policy servicenow-mcp --region=us-central1
```

### Check Agent Engine Logs

```bash
gcloud logging read 'resource.type="aiplatform.googleapis.com/ReasoningEngine"' \
  --project=$PROJECT_ID --limit=50
```

### Check Cloud Run Logs

```bash
gcloud run services logs read servicenow-mcp --region=us-central1 --limit=50
```

## Related Documentation

- [Security Flow](security-flow.md) - Token flow diagrams
- [Entra ID Setup](entra-id-setup.md) - Microsoft app registration
- [Deployment Guide](deployment.md) - Step-by-step deployment
- [Architecture](architecture.md) - E2E system diagram
- [Discovery Engine Setup](discovery-engine-setup.md) - SharePoint grounding
