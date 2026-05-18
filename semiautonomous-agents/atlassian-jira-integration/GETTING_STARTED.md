# Getting Started - Atlassian Jira + Gemini Enterprise

Complete deployment guide for production-ready Jira integration with Gemini Enterprise.

**What you'll build:**
- Cloud Run MCP server (7 Jira tools)
- ADK agent on Vertex AI Agent Engine  
- Registered in Gemini Enterprise
- Registered in Agent Registry for governance

**Time:** ~2 hours  
**Result:** 94.5% accuracy, 1% hallucination rate

---

## Prerequisites

- Google Cloud project with Gemini Enterprise enabled
- Atlassian Jira Cloud site with admin access
- `gcloud` CLI configured with Owner role
- Python 3.10+ with pip

---

## Step 1: Create Atlassian OAuth App

1. Go to: https://developer.atlassian.com/console/myapps/
2. Click **Create** → **OAuth 2.0 integration**
3. Name: `gemini-jira-agent`
4. **Permissions** → Add **Jira API** → Grant:
   - `read:jira-work`
   - `write:jira-work`
   - `read:jira-user`
5. **Authorization** → Callback URL: `https://vertexaisearch.cloud.google.com/oauth-redirect`
6. **Settings** → Copy **Client ID** and **Secret**

---

## Step 2: Deploy Cloud Run MCP Server

```bash
cd ~/vertex-ai-samples/semiautonomous-agents/atlassian-jira-integration/option-a-custom-mcp-portal/jira_server

export PROJECT_ID=your-project-id
export REGION=us-central1

# Build image
gcloud builds submit --tag us-central1-docker.pkg.dev/$PROJECT_ID/cloud-run-source-deploy/jira-mcp:latest --project=$PROJECT_ID

# Deploy to Cloud Run
gcloud run deploy jira-mcp-server \
  --image us-central1-docker.pkg.dev/$PROJECT_ID/cloud-run-source-deploy/jira-mcp:latest \
  --region=$REGION \
  --project=$PROJECT_ID \
  --allow-unauthenticated \
  --port=8080 \
  --memory=1Gi \
  --cpu=2 \
  --timeout=600 \
  --max-instances=5
```

**Save the service URL** (e.g., `https://jira-mcp-server-123456789.us-central1.run.app`)

---

## Step 3: Register MCP in Agent Registry

```bash
cd ~/vertex-ai-samples/semiautonomous-agents/atlassian-jira-integration/option-a-custom-mcp-portal

export MCP_SERVER_URL=https://jira-mcp-server-YOUR_NUMBER.us-central1.run.app
export GOOGLE_CLOUD_PROJECT=your-project-id
export GOOGLE_CLOUD_LOCATION=us-central1
export MCP_SERVICE_DISPLAY_NAME=jira-mcp

python register_mcp_in_registry.py
```

**Copy the output:**
```
MCP_SERVICE_RESOURCE=projects/YOUR_NUMBER/locations/us-central1/services/jira-mcp
```

---

## Step 4: Configure Environment

```bash
cd ~/vertex-ai-samples/semiautonomous-agents/atlassian-jira-integration/option-a-custom-mcp-portal/adk_agent

cat > .env <<EOF
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_PROJECT_NUMBER=your-project-number
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_CLOUD_QUOTA_PROJECT=your-project-id
GOOGLE_GENAI_USE_VERTEXAI=True

MCP_SERVER_URL=https://jira-mcp-server-YOUR_NUMBER.us-central1.run.app/sse
MCP_SERVICE_RESOURCE=projects/YOUR_NUMBER/locations/us-central1/services/jira-mcp
ATLASSIAN_CLIENT_ID=your-client-id-from-step-1
ATLASSIAN_CLIENT_SECRET=your-secret-from-step-1
EOF
```

**Get project number:**
```bash
gcloud projects describe your-project-id --format="value(projectNumber)"
```

---

## Step 5: Deploy ADK Agent

```bash
cd ~/vertex-ai-samples/semiautonomous-agents/atlassian-jira-integration/option-a-custom-mcp-portal/adk_agent

pip install -r requirements.txt
python deploy_agent_engine.py
```

**Save the Reasoning Engine ID** (e.g., `1234567890123456789`)

---

## Step 6: Register in Gemini Enterprise

```bash
cd ~/vertex-ai-samples/semiautonomous-agents/atlassian-jira-integration/option-a-custom-mcp-portal

python register.py agent
```

**When prompted, enter:**
- Reasoning Engine ID (from Step 5)
- Atlassian Client ID (from Step 1)
- Atlassian Client Secret (from Step 1)

**Save the Agent ID** shown (e.g., `987654321`)

---

## Step 7: Test

1. Open Gemini Enterprise chat
2. Left sidebar → **Agents** → **Jira Assistant**
3. Ask: `"List 5 recent bugs"`

**First time:** OAuth popup → log in with Atlassian → approve → popup closes  
**After:** Immediate answers with real Jira data

---

## Expected Output

```
Here are 5 recent bugs:

1. SMP-16 - Dropdown value reset after update()
   Status: To Do | Assigned: Unassigned

2. SMP-12 - flet build apk fails with Gradle 7.5 error
   Status: In Progress | Assigned: Jesus Chavez

3. SMP-11 - FilePicker ignores initial_directory
   Status: To Do | Assigned: Unassigned
...
```

---

## Troubleshooting

**Agent not found in sidebar**
- Wait 2-3 minutes (propagation delay)
- Refresh GE page
- Check: Console → Agents tab shows Active

**Empty results**
- Check Cloud Run logs: `gcloud run logs read jira-mcp-server --region=us-central1 --limit=50`
- Verify OAuth token in logs: Look for "Authorization: Bearer"

**429 RESOURCE_EXHAUSTED**
- Expected with >50 issues
- Agent has pagination built-in
- See: [option-a-custom-mcp-portal/PAGINATION.md](option-a-custom-mcp-portal/PAGINATION.md)

---

## What You Get

✅ **94.5% accuracy** across 500 test questions  
✅ **1% hallucination** (vs 69% with alternatives)  
✅ **7 Jira tools:** search, projects, summarize, reports, comments, worklogs, links  
✅ **Multi-tenant:** Each user's OAuth token enforces Jira ACLs  
✅ **Paginated:** Handles large result sets  
✅ **Observable:** Full Cloud Logging + traces  

---

## Next Steps

**Production readiness:**
- Set up monitoring dashboards
- Configure Cloud Run autoscaling limits
- Enable Agent Gateway for IAP (see: [agent-gateway-demo](../agent-gateway-demo/))

**Customization:**
- Edit `adk_agent/agent.py` for custom prompts
- Edit `jira_server/server.py` to add tools
- Redeploy: Steps 2 & 5 only

**Evaluation:**
- Run 500-question benchmark: [eval/README.md](eval/README.md)
- Compare vs Atlassian Remote MCP: [eval/sample-run/report.html](eval/sample-run/report.html)

---

**Need help?** See [option-a-custom-mcp-portal/README.md](option-a-custom-mcp-portal/README.md) for technical details.
