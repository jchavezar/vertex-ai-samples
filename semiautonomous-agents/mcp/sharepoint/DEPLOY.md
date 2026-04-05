# Cloud Run Deployment

Deploy the Microsoft 365 MCP Server to Google Cloud Run for remote access.

## Prerequisites

- Google Cloud project with billing enabled
- `gcloud` CLI installed and authenticated
- APIs enabled: Cloud Run, Cloud Build, Artifact Registry

```bash
gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com
```

## Deployment Steps

### 1. Set environment variables

```bash
export PROJECT_ID=$(gcloud config get-value project)
export REGION=us-central1
export MS365_CLIENT_ID="your-azure-app-client-id"
export MS365_TENANT_ID="your-azure-tenant-id"
```

### 2. Create Artifact Registry repository

```bash
gcloud artifacts repositories create mcp-servers \
    --repository-format=docker \
    --location=$REGION
```

### 3. Grant permissions

```bash
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')

# Grant Cloud Build permission to push images
gcloud artifacts repositories add-iam-policy-binding mcp-servers \
    --location=$REGION \
    --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
    --role="roles/artifactregistry.repoAdmin"
```

### 4. Deploy

```bash
gcloud run deploy ms365-mcp \
    --source . \
    --region $REGION \
    --no-allow-unauthenticated \
    --set-env-vars="MS365_CLIENT_ID=$MS365_CLIENT_ID,MS365_TENANT_ID=$MS365_TENANT_ID" \
    --memory=512Mi \
    --cpu=1 \
    --min-instances=0 \
    --max-instances=3 \
    --timeout=300
```

### 5. Connect via Cloud Run Proxy

```bash
# Start authenticated proxy
gcloud run services proxy ms365-mcp --region $REGION --port=8080
```

### 6. Add to LLM client

**Claude Code:**
```bash
claude mcp add ms365 --transport http http://localhost:8080/mcp
```

**Gemini CLI:**
```json
{
  "mcpServers": {
    "ms365": {
      "url": "http://localhost:8080/mcp"
    }
  }
}
```

## Architecture

```
LLM Client (local)
    |
    | Cloud Run Proxy (gcloud auth)
    v
Cloud Run MCP Server
    |
    | MSAL device code flow
    v
Microsoft Graph API
    |
    v
SharePoint / OneDrive / Mail / Calendar / Teams
```

## Troubleshooting

### Permission denied on Artifact Registry

Wait 2-3 minutes for IAM propagation, then retry deployment.

### Build fails

Check logs:
```bash
gcloud builds list --limit=1 --format="value(id)" | xargs -I{} gcloud builds log {}
```

### Server not responding

Check Cloud Run logs:
```bash
gcloud run services logs read ms365-mcp --region $REGION --limit=50
```
