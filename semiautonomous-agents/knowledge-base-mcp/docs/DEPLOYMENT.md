# Deployment Guide

## Cloud Run Deployment

### 1. Prerequisites

```bash
# Enable APIs
gcloud services enable firestore.googleapis.com
gcloud services enable aiplatform.googleapis.com
gcloud services enable run.googleapis.com

# Create Firestore vector index (one-time)
gcloud firestore indexes composite create \
  --collection-group=knowledge \
  --field-config=vector-config='{"dimension":768,"flat":{}}',field-path=embedding

gcloud firestore indexes composite create \
  --collection-group=playbooks \
  --field-config=vector-config='{"dimension":768,"flat":{}}',field-path=embedding
```

### 2. Deploy

```bash
# Deploy with deploy.sh
./deploy.sh

# Or manually:
gcloud run deploy knowledge-base-mcp \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars "GOOGLE_CLOUD_PROJECT=your-project" \
  --set-env-vars "MCP_TRANSPORT=streamable-http"
```

### 3. Get Service URL

```bash
gcloud run services describe knowledge-base-mcp \
  --region us-central1 \
  --format 'value(status.url)'
```

## Connect to Claude Code

### Option A: Cloud Run Proxy (Recommended)

```bash
# Start proxy
gcloud run services proxy knowledge-base-mcp --region us-central1 --port=8082

# Add to Claude Code
claude mcp add knowledge-base --transport http http://localhost:8082/mcp
```

### Option B: Direct URL

```bash
claude mcp add knowledge-base --transport http https://knowledge-base-mcp-xxx.run.app/mcp
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GOOGLE_CLOUD_PROJECT` | Yes | GCP project ID |
| `PORT` | No | Server port (default 8080) |
| `MCP_TRANSPORT` | No | `streamable-http` or `sse` |
| `EXTRACTION_MODEL` | No | Gemini model (default gemini-2.5-flash) |

## IAM Permissions

The Cloud Run service account needs:

```bash
# Firestore access
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:SERVICE_ACCOUNT" \
  --role="roles/datastore.user"

# Vertex AI (embeddings + Gemini)
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:SERVICE_ACCOUNT" \
  --role="roles/aiplatform.user"
```

## Proxy Management

For convenience, create a startup script:

```bash
#!/bin/bash
# ~/start_mcp_proxies.sh

pkill -f "gcloud run services proxy" || true
sleep 2

nohup gcloud run services proxy knowledge-base-mcp --region us-central1 --port=8082 > /tmp/kb-proxy.log 2>&1 &
nohup gcloud run services proxy gworkspace-mcp --region us-central1 --port=8081 > /tmp/gw-proxy.log 2>&1 &
nohup gcloud run services proxy ms365-mcp --region us-central1 --port=8083 > /tmp/ms-proxy.log 2>&1 &

echo "Proxies started on ports 8081, 8082, 8083"
```

## Troubleshooting

### "No knowledge items found"
- Check Firestore has data: `get_stats()`
- Verify vector index exists
- Try `recent_knowledge()` to see if anything is stored

### "Embedding failed"
- Check Vertex AI API is enabled
- Verify service account has `aiplatform.user` role

### "Session already ingested"
- This is expected - deduplication working
- Use `dry_run=True` to preview without storing

### Vector index not ready
Wait a few minutes after creating the index. Check status:
```bash
gcloud firestore indexes composite list
```
