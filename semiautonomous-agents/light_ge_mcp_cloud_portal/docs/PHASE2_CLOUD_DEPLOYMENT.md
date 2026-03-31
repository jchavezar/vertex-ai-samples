# Phase 2: Cloud Deployment

**Prerequisites:** Complete all tests in [Phase 1](PHASE1_LOCAL_TESTING.md) first.

---

## Deployment Order

```
1. MCP Server → Cloud Run (exposes /sse endpoint)
2. Agent → Agent Engine (points to MCP Server URL)
3. Frontend → Configure Agent Engine ID + WIF
```

> **Note:** No separate backend needed - frontend calls Agent Engine directly via Workforce Identity Federation.

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

## Step 3: Configure Frontend

Update `frontend/src/authConfig.ts` with your Agent Engine ID:

```typescript
export const agentConfig = {
  projectId: "your-project-id",
  location: "us-central1",
  agentEngineId: AGENT_ENGINE_ID,  // From Step 2
};
```

```bash
cd ../frontend
npm install
npm run dev
```

Open http://localhost:5173 and test with Microsoft login.

---

## Verification Checklist

- [ ] MCP Server responds at `$MCP_URL`
- [ ] Agent Engine creates sessions with `USER_TOKEN` in state
- [ ] Agent calls MCP tools with JWT in X-User-Token header
- [ ] ServiceNow returns user-scoped data (not Basic Auth fallback)
- [ ] Discovery Engine returns grounded SharePoint responses
- [ ] End-to-end: Frontend → Agent Engine → MCP/Discovery Engine

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
