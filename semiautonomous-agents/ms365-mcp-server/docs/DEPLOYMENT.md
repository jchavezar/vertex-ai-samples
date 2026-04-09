# Deployment Guide

## Cloud Run Deployment

### 1. Build and Deploy

```bash
# Set variables
export PROJECT_ID=your-project-id
export REGION=us-central1

# Deploy with deploy.sh
./deploy.sh

# Or manually:
gcloud run deploy ms365-mcp \
  --source . \
  --region $REGION \
  --allow-unauthenticated \
  --set-env-vars "MS365_CLIENT_ID=your-client-id" \
  --set-env-vars "MS365_TENANT_ID=your-tenant-id" \
  --set-env-vars "MCP_TRANSPORT=streamable-http"
```

### 2. Get Service URL

```bash
gcloud run services describe ms365-mcp \
  --region $REGION \
  --format 'value(status.url)'
```

## Connect to Claude Code

### Option A: Cloud Run Proxy (Recommended)

```bash
# Start proxy
gcloud run services proxy ms365-mcp --region us-central1 --port=8083

# Add to Claude Code
claude mcp add ms365 --transport http http://localhost:8083/mcp
```

### Option B: Direct URL (if service is public)

```bash
claude mcp add ms365 --transport http https://ms365-mcp-xxx.run.app/mcp
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `MS365_CLIENT_ID` | Yes | Azure App Registration client ID |
| `MS365_TENANT_ID` | Yes | Azure tenant ID (or 'common') |
| `PORT` | No | Server port (default 8080) |
| `MCP_TRANSPORT` | No | Transport: `streamable-http` or `sse` |

## Secret Management

For production, use Secret Manager:

```bash
# Create secrets
echo -n "your-client-id" | gcloud secrets create MS365_CLIENT_ID --data-file=-
echo -n "your-tenant-id" | gcloud secrets create MS365_TENANT_ID --data-file=-

# Deploy with secrets
gcloud run deploy ms365-mcp \
  --source . \
  --region us-central1 \
  --set-secrets "MS365_CLIENT_ID=MS365_CLIENT_ID:latest" \
  --set-secrets "MS365_TENANT_ID=MS365_TENANT_ID:latest"
```

## Dockerfile

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "server.py"]
```

## Token Persistence

In Cloud Run, tokens are stored in memory and persist within container instances. For multi-instance deployments, consider:

1. **Firestore** for token storage
2. **Redis** via Memorystore
3. **Secret Manager** for long-lived refresh tokens

## Troubleshooting

### "Not authenticated" errors
- Run `ms365_login` then `ms365_complete_login`
- Tokens may have expired; re-authenticate

### "Insufficient privileges" 
- Check Azure App permissions
- Admin consent may be required

### Connection refused
- Ensure proxy is running: `gcloud run services proxy ...`
- Check port is correct (default 8083 for proxy)

### Device code expired
- Device codes expire after 15 minutes
- Call `ms365_login` again to get a new code
