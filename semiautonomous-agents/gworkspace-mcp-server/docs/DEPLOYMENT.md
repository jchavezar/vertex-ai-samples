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
gcloud run deploy gworkspace-mcp \
  --source . \
  --region $REGION \
  --allow-unauthenticated \
  --set-env-vars "GOOGLE_CLIENT_ID=your-client-id" \
  --set-env-vars "GOOGLE_CLIENT_SECRET=your-secret" \
  --set-env-vars "MCP_TRANSPORT=streamable-http"
```

### 2. Get Service URL

```bash
gcloud run services describe gworkspace-mcp \
  --region $REGION \
  --format 'value(status.url)'
```

## Connect to Claude Code

### Option A: Cloud Run Proxy (Recommended)

```bash
# Start proxy
gcloud run services proxy gworkspace-mcp --region us-central1 --port=8081

# Add to Claude Code
claude mcp add gworkspace --transport http http://localhost:8081/mcp
```

### Option B: Direct URL (if service is public)

```bash
claude mcp add gworkspace --transport http https://gworkspace-mcp-xxx.run.app/mcp
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GOOGLE_CLIENT_ID` | Yes | OAuth client ID |
| `GOOGLE_CLIENT_SECRET` | No | OAuth client secret (not needed for TVs type) |
| `PORT` | No | Server port (default 8080) |
| `MCP_TRANSPORT` | No | Transport type: `streamable-http` or `sse` |

## Secret Management

For production, use Secret Manager:

```bash
# Create secrets
echo -n "your-client-id" | gcloud secrets create GOOGLE_CLIENT_ID --data-file=-
echo -n "your-secret" | gcloud secrets create GOOGLE_CLIENT_SECRET --data-file=-

# Deploy with secrets
gcloud run deploy gworkspace-mcp \
  --source . \
  --region us-central1 \
  --set-secrets "GOOGLE_CLIENT_ID=GOOGLE_CLIENT_ID:latest" \
  --set-secrets "GOOGLE_CLIENT_SECRET=GOOGLE_CLIENT_SECRET:latest"
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

## Health Check

The server exposes `/mcp` endpoint. Cloud Run health checks will use this.

## Troubleshooting

### "Not authenticated" errors
- Run `gworkspace_login` to authenticate
- Check that OAuth credentials are valid

### "Permission denied" errors
- Verify APIs are enabled in your GCP project
- Check that OAuth scopes are correct

### Connection refused
- Ensure proxy is running: `gcloud run services proxy ...`
- Check port is correct (default 8081 for proxy)
