# Phase 2: Cloud Deployment

**Prerequisites:** Complete all tests in [Phase 1](PHASE1_LOCAL_TESTING.md) first.

---

## Deployment Order

```
1. MCP Server → Cloud Run (exposes /mcp endpoint)
2. Agent → Agent Engine (points to MCP Server URL)
3. Backend → Cloud Run (calls Agent Engine)
4. Frontend → Update API URL
```

---

## Step 1: Deploy MCP Server to Cloud Run

```bash
cd mcp-server

gcloud run deploy servicenow-mcp \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars "SERVICENOW_INSTANCE_URL=https://dev289493.service-now.com"
```

**Capture the URL:**
```bash
MCP_URL=$(gcloud run services describe servicenow-mcp \
  --region us-central1 \
  --format 'value(status.url)')/mcp

echo "MCP Server URL: $MCP_URL"
# Example: https://servicenow-mcp-xxxxx.us-central1.run.app/mcp
```

---

## Step 2: Deploy Agent to Agent Engine

```bash
cd agent

# Update .env with MCP URL
echo "SERVICENOW_MCP_URL=$MCP_URL" >> .env

# Deploy
uv run python deploy.py
```

**Capture the Agent ID:**
```bash
# The deploy script outputs this:
AGENT_ENGINE_ID=<your-new-agent-id>
```

---

## Step 3: Deploy TypeScript Backend

```bash
cd backend

# Update .env
echo "AGENT_ENGINE_ID=$AGENT_ENGINE_ID" >> .env

# Deploy
gcloud run deploy portal-backend \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars "GOOGLE_CLOUD_PROJECT=deloitte-plantas,AGENT_ENGINE_ID=$AGENT_ENGINE_ID"
```

**Capture the URL:**
```bash
BACKEND_URL=$(gcloud run services describe portal-backend \
  --region us-central1 \
  --format 'value(status.url)')

echo "Backend URL: $BACKEND_URL"
```

---

## Step 4: Test Cloud Deployment

```bash
export TEST_JWT_TOKEN="eyJ..."

curl -X POST "$BACKEND_URL/api/chat" \
  -H "Authorization: Bearer $TEST_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "List 3 incidents"}'
```

---

## Step 5: Update Frontend

Update your frontend's API URL:

```typescript
// frontend/.env or config
VITE_API_URL=https://portal-backend-xxxxx.us-central1.run.app
```

---

## Verification Checklist

- [ ] MCP Server responds at `$MCP_URL`
- [ ] Agent Engine creates sessions with `USER_TOKEN` in state
- [ ] Agent calls MCP tools with JWT in Authorization header
- [ ] ServiceNow returns user-scoped data (not Basic Auth fallback)
- [ ] End-to-end: Frontend → Backend → Agent → MCP → ServiceNow

---

## Rollback

If something breaks:

```bash
# Revert to previous MCP server
gcloud run services update-traffic servicenow-mcp \
  --to-revisions=<previous-revision>=100

# Delete problematic agent
gcloud ai reasoning-engines delete <AGENT_ID> --region=us-central1
```

---

## Production Hardening

For production:

1. **Authentication:** Add IAM authentication to Cloud Run services
2. **Secrets:** Use Secret Manager for ServiceNow credentials
3. **Monitoring:** Enable Cloud Logging and Error Reporting
4. **Scaling:** Configure min-instances=1 to avoid cold starts
