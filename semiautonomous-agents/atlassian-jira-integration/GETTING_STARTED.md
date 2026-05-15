# Getting Started - Atlassian Jira + Gemini Enterprise

Step-by-step guide to integrate Jira with Gemini Enterprise using a custom Cloud Run MCP server + ADK agent.

**Time:** ~2 hours  
**Accuracy:** 94.5% composite, 1% hallucination  
**What you'll build:** Production-grade Jira assistant

---

## Prerequisites

- **Google Cloud Project** with Gemini Enterprise enabled
- **Atlassian Jira Cloud** site with admin access
- **Terminal** access with `gcloud` configured
- **Python 3.10+** installed

## Architecture Overview

```
User → Gemini Enterprise → ADK Agent (Agent Engine) → MCP Server (Cloud Run) → Jira REST API
```

You'll deploy 2 components:
1. **Cloud Run MCP Server** - FastAPI service that wraps Jira REST API
2. **ADK Agent** - Intelligent agent deployed to Vertex AI Agent Engine

---

## Step 1: Create Atlassian OAuth App

Go to: https://developer.atlassian.com/console/myapps/

1. Click **Create** → **OAuth 2.0 integration**
2. Name: `gemini-jira-agent`
3. **Permissions** → Add **Jira API** → Grant:
   - `read:jira-work`
   - `write:jira-work`  
   - `read:jira-user`
4. **Authorization** → Callback URL: `https://vertexaisearch.cloud.google.com/oauth-redirect`
5. **Settings** → Copy:
   - **Client ID** (save for Step 5)
   - **Secret** (save for Step 5)

---

## Step 2: Deploy Cloud Run MCP Server

```bash
cd ~/vertex-ai-samples/semiautonomous-agents/atlassian-jira-integration/option-a-custom-mcp-portal/jira_server

# Set your project
export PROJECT_ID=your-project-id
export REGION=us-central1

# Build and deploy
gcloud builds submit --tag us-central1-docker.pkg.dev/$PROJECT_ID/cloud-run-source-deploy/jira-mcp:latest --project=$PROJECT_ID

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

**Save the URL** shown after deployment (e.g., `https://jira-mcp-server-123456789.us-central1.run.app`)

---

## Step 3: Register MCP Server in Agent Registry (Optional)

**Purpose:** Enables governance, IAP enforcement, cross-agent reuse.

**Skip if:** You just want it working quickly (can add later).

```bash
cd ~/vertex-ai-samples/semiautonomous-agents/atlassian-jira-integration/option-a-custom-mcp-portal

export MCP_SERVER_URL=https://jira-mcp-server-YOUR_NUMBER.us-central1.run.app
export GOOGLE_CLOUD_PROJECT=your-project-id
export GOOGLE_CLOUD_LOCATION=us-central1

python register_mcp_in_registry.py
```

Copy the `MCP_SERVICE_RESOURCE` value shown (you'll add to `.env` next).

---

## Step 4: Configure Environment

```bash
cd ~/vertex-ai-samples/semiautonomous-agents/atlassian-jira-integration/option-a-custom-mcp-portal/adk_agent

# Create .env file
cat > .env <<EOF
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_PROJECT_NUMBER=your-project-number
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_CLOUD_QUOTA_PROJECT=your-project-id
GOOGLE_GENAI_USE_VERTEXAI=True

MCP_SERVER_URL=https://jira-mcp-server-YOUR_NUMBER.us-central1.run.app/sse
ATLASSIAN_CLIENT_ID=your-client-id-from-step-1
ATLASSIAN_CLIENT_SECRET=your-secret-from-step-1

# If you did Step 3:
MCP_SERVICE_RESOURCE=projects/YOUR_NUMBER/locations/us-central1/services/jira-mcp
EOF
```

**Get your project number:**
```bash
gcloud projects describe your-project-id --format="value(projectNumber)"
```

---

## Step 5: Deploy ADK Agent to Agent Engine

```bash
cd ~/vertex-ai-samples/semiautonomous-agents/atlassian-jira-integration/option-a-custom-mcp-portal/adk_agent

# Install dependencies
pip install -r requirements.txt

# Deploy agent
python deploy_agent_engine.py
```

This deploys the agent to Vertex AI Agent Engine. **Save the Reasoning Engine ID** shown (e.g., `1234567890123456789`).

---

## Step 6: Register Agent in Gemini Enterprise

```bash
cd ~/vertex-ai-samples/semiautonomous-agents/atlassian-jira-integration/option-a-custom-mcp-portal

# Register OAuth + Agent
python register.py agent

# When prompted, enter:
# - Reasoning Engine ID (from Step 5)
# - Atlassian Client ID (from Step 1)
# - Atlassian Client Secret (from Step 1)
```

This registers:
1. Atlassian OAuth configuration in GE
2. The agent as a callable tool in your GE app

**Save the Agent ID** shown (e.g., `987654321`).

---

## Step 7: Test

1. Open your Gemini Enterprise chat
2. Left sidebar → **Agents** → find **Jira Assistant**
3. Click it to start chatting with the agent
4. Ask: `"List 5 recent bugs"`

**First time:** OAuth popup appears → log in with Atlassian → approve permissions → popup closes

**Subsequent:** Agent answers immediately with real Jira data.

---

## Expected Results

```
Here are 5 recent bugs from your Jira:

1. SMP-16 - Bug: Dropdown value reset after update()
   Status: To Do
   Assigned: Unassigned

2. SMP-12 - Bug: flet build apk fails with Gradle 7.5 error  
   Status: In Progress
   Assigned: Jesus Chavez

3. SMP-11 - Bug: FilePicker ignores initial_directory on Windows
   Status: To Do
   Assigned: Unassigned

...
```

---

## Troubleshooting

**"Agent not found in sidebar"**
- Wait 2-3 minutes after Step 6 (propagation delay)
- Refresh the GE page
- Check: Console → Agents tab shows your agent as Active

**Empty results despite Jira having data**
- Check Cloud Run logs: `gcloud run logs read jira-mcp-server --project=your-project --region=us-central1 --limit=50`
- Verify OAuth token is reaching the MCP server (look for "Authorization: Bearer" in logs)
- Test MCP server directly: See `option-a-custom-mcp-portal/README.md` Step 7

**429 RESOURCE_EXHAUSTED after pagination**
- This is expected with >50 issues - the agent has pagination built-in
- See: `option-a-custom-mcp-portal/PAGINATION.md` for technical details

---

## Architecture Benefits (vs Direct Remote MCP)

| Feature | Custom MCP (Option A) | Atlassian Remote (Option B) |
|---------|----------------------|---------------------------|
| **Accuracy** | 94.5% | 87.1% |
| **Hallucination** | **1.0%** | 68.9% |
| **Control** | Full (you write prompts, format output) | Zero (Atlassian controls) |
| **Latency** | ~24s | ~5-10s |
| **Setup** | 2h | 15min |
| **Maintenance** | Cloud Run + Agent Engine | None |

**Why Option A is better:** 1% hallucination vs 69% means production-ready. Fake Jira keys break workflows.

---

## Next Steps

**Production deployment:**
- Enable Agent Gateway for IAP enforcement (see: `agent-gateway-demo/`)
- Set up monitoring: `gcloud logging` + Cloud Monitoring dashboards
- Configure rate limits on Cloud Run

**Customization:**
- Edit `adk_agent/agent.py` to change prompts, add tools, modify formatting
- Edit `jira_server/server.py` to add custom Jira queries or fields
- Redeploy: Re-run Steps 2 & 5 (no Step 6 needed)

**Evaluation:**
- Run the 500-question benchmark: See `eval/README.md`
- Generate your own test questions: `eval/generate_questions.py`

---

## Files Reference

| File | Purpose |
|------|---------|
| `option-a-custom-mcp-portal/jira_server/server.py` | FastAPI MCP server |
| `option-a-custom-mcp-portal/adk_agent/agent.py` | ADK agent logic |
| `option-a-custom-mcp-portal/register.py` | Registers in GE |
| `option-a-custom-mcp-portal/register_mcp_in_registry.py` | Agent Registry (optional) |

For detailed technical docs: `option-a-custom-mcp-portal/README.md`
