# Deployment Guide

[← Back to Main README](../README.md)

## Prerequisites Checklist

- [ ] Google Cloud project with billing enabled
- [ ] `gcloud` CLI authenticated (`gcloud auth login`)
- [ ] Microsoft Entra ID tenant with app registration
- [ ] ServiceNow instance with OIDC configured
- [ ] Python 3.11+ with [uv](https://docs.astral.sh/uv/)
- [ ] Node.js 18+

## Step 1: Configure Environment

### Set Variables

```bash
# GCP Configuration
export PROJECT_ID="your-project-id"
export PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
export REGION="us-central1"

# ServiceNow Configuration
export SERVICENOW_INSTANCE="https://your-instance.service-now.com"

# Entra ID Configuration
export ENTRA_TENANT_ID="your-tenant-id"
export ENTRA_CLIENT_ID="your-client-id"

# Workforce Identity Federation
export WIF_POOL_ID="entra-id-oidc-pool"
export WIF_PROVIDER_ID="entra-id-provider"
```

### Enable APIs

```bash
gcloud config set project $PROJECT_ID

gcloud services enable \
  aiplatform.googleapis.com \
  run.googleapis.com \
  iam.googleapis.com \
  sts.googleapis.com \
  cloudbuild.googleapis.com
```

## Step 2: Deploy MCP Server

```bash
cd mcp-server

# Create .env file
cat > .env << EOF
SERVICENOW_INSTANCE_URL=$SERVICENOW_INSTANCE
PORT=8080
MCP_TRANSPORT=sse
EOF

# Deploy to Cloud Run
gcloud run deploy servicenow-mcp \
  --source . \
  --region $REGION \
  --no-allow-unauthenticated \
  --set-env-vars="SERVICENOW_INSTANCE_URL=$SERVICENOW_INSTANCE"

# Get MCP URL
export MCP_URL="https://servicenow-mcp-$PROJECT_NUMBER.$REGION.run.app/sse"
echo "MCP URL: $MCP_URL"
```

### Grant IAM Access

```bash
# Allow Agent Engine to invoke MCP Server
gcloud run services add-iam-policy-binding servicenow-mcp \
  --member="serviceAccount:service-$PROJECT_NUMBER@gcp-sa-aiplatform-re.iam.gserviceaccount.com" \
  --role="roles/run.invoker" \
  --region=$REGION
```

## Step 3: Deploy Agent Engine

```bash
cd ../agent

# Create .env file
cat > .env << EOF
GOOGLE_CLOUD_PROJECT=$PROJECT_ID
GOOGLE_CLOUD_LOCATION=$REGION
STAGING_BUCKET=gs://$PROJECT_ID-staging
SERVICENOW_MCP_URL=$MCP_URL
EOF

# Create staging bucket if needed
gsutil mb -l $REGION gs://$PROJECT_ID-staging 2>/dev/null || true

# Grant required IAM roles
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
  --role="roles/aiplatform.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
  --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:service-$PROJECT_NUMBER@gcp-sa-aiplatform-re.iam.gserviceaccount.com" \
  --role="roles/aiplatform.admin"

# Deploy
uv run python deploy.py

# Note the Agent Engine ID from output
export AGENT_ENGINE_ID="<id-from-output>"
```

## Step 4: Configure Frontend

```bash
cd ../frontend

# Install dependencies
npm install --registry=https://registry.npmjs.org
```

### Update Configuration

Edit `src/authConfig.ts`:

```typescript
export const msalConfig: Configuration = {
  auth: {
    clientId: "YOUR_ENTRA_CLIENT_ID",
    authority: "https://login.microsoftonline.com/YOUR_ENTRA_TENANT_ID",
    redirectUri: window.location.origin,
  },
};

export const gcpConfig = {
  workforcePoolId: "YOUR_WIF_POOL_ID",
  providerId: "YOUR_WIF_PROVIDER_ID",
  location: "global",
};

export const agentConfig = {
  projectId: "YOUR_PROJECT_ID",
  location: "us-central1",
  agentEngineId: "YOUR_AGENT_ENGINE_ID",
};
```

## Step 5: Test Locally

```bash
# Start frontend dev server
npm run dev
```

Open http://localhost:3000 and test:
1. Click "Sign in with Microsoft"
2. Authenticate with Entra ID
3. Send a message like "list 3 incidents"

## Step 6: Deploy Frontend (Optional)

```bash
# Build
npm run build

# Deploy to Cloud Run
gcloud run deploy servicenow-portal \
  --source . \
  --region $REGION \
  --allow-unauthenticated
```

Update Entra ID redirect URIs to include the production URL.

## Verification Commands

```bash
# Check MCP Server
gcloud run services describe servicenow-mcp --region=$REGION

# Check Agent Engine
gcloud ai reasoning-engines list --region=$REGION

# Check Cloud Run logs
gcloud run services logs read servicenow-mcp --region=$REGION --limit=20

# Check IAM bindings
gcloud projects get-iam-policy $PROJECT_ID --format=json | \
  jq '.bindings[] | select(.role | contains("aiplatform"))'
```

## Troubleshooting

### MCP Server 401/403

```bash
# Verify IAM binding
gcloud run services get-iam-policy servicenow-mcp --region=$REGION

# Should show:
# - serviceAccount:service-XXX@gcp-sa-aiplatform-re.iam.gserviceaccount.com
#   role: roles/run.invoker
```

### Agent Engine Permission Denied

```bash
# Grant missing permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:service-$PROJECT_NUMBER@gcp-sa-aiplatform-re.iam.gserviceaccount.com" \
  --role="roles/aiplatform.admin"
```

### STS Token Exchange Failed

1. Verify WIF pool exists:
   ```bash
   gcloud iam workforce-pools providers describe $WIF_PROVIDER_ID \
     --workforce-pool=$WIF_POOL_ID --location=global
   ```

2. Check provider Client ID matches Entra app

### ServiceNow 401

1. Check OIDC configuration in ServiceNow
2. Verify user exists with matching email
3. Check JWT claims with: https://jwt.io

## Environment Files Summary

| File | Purpose |
|------|---------|
| `mcp-server/.env` | ServiceNow instance URL |
| `agent/.env` | GCP project, MCP URL |
| `frontend/src/authConfig.ts` | MSAL, WIF, Agent Engine config |

## Next Steps

- [Security Flow](security-flow.md) - Understand authentication
- [Architecture](architecture.md) - System design details
- [ServiceNow Setup](servicenow-setup.md) - OIDC configuration
