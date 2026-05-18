# Option C — Custom MCP Server + Direct GE Integration (Cost-Optimized)

Connect your custom Cloud Run MCP server directly to Gemini Enterprise as a custom MCP datastore, skipping Agent Engine entirely to eliminate ADK API charges.

**What you get:**
- ✅ Your own MCP server (7 tools, controlled)
- ✅ Direct GE assistant calls (no agent routing)
- ✅ Agent Registry governance
- ✅ **Zero Agent Engine costs**

**Trade-offs vs Option A:**
- No ADK agent features (thinking config, before_model_callback, custom prompts)
- GE assistant's default prompts (less control)
- Same tool quality and accuracy as Option A

---

## Architecture

```
User → GE Chat → Custom MCP Datastore → Your MCP (Cloud Run) → Jira REST API
```

**No Agent Engine** - calls go directly from GE to your MCP server.

---

## Prerequisites

- Same Cloud Run MCP server from Option A deployed
- Atlassian OAuth app created (developer.atlassian.com)
- GCP project with Gemini Enterprise

---

## Step 1: Deploy Cloud Run MCP Server

**Reuse from Option A:**

```bash
cd ~/vertex-ai-samples/semiautonomous-agents/atlassian-jira-integration/option-a-custom-mcp-portal/jira_server

export PROJECT_ID=your-project-id
export REGION=us-central1

gcloud builds submit --tag us-central1-docker.pkg.dev/$PROJECT_ID/cloud-run-source-deploy/jira-mcp:latest --project=$PROJECT_ID

gcloud run deploy jira-mcp-server \
  --image us-central1-docker.pkg.dev/$PROJECT_ID/cloud-run-source-deploy/jira-mcp:latest \
  --region=$REGION \
  --project=$PROJECT_ID \
  --allow-unauthenticated \
  --port=8080 \
  --memory=1Gi \
  --cpu=2 \
  --timeout=600
```

**Save the URL** (e.g., `https://jira-mcp-server-123456789.us-central1.run.app`)

---

## Step 2: Register MCP in Agent Registry

Console → **Agent Platform** → **Registry** → **Add MCP Server**

Fill in:
- **Name:** `jira-mcp-custom`
- **MCP Server URL:** `https://jira-mcp-server-YOUR_NUMBER.us-central1.run.app/mcp`
- **Transport:** StreamableHTTP
- **Location:** us-central1

Click **Create**.

**Alternative (API):**

```bash
cd ~/vertex-ai-samples/semiautonomous-agents/atlassian-jira-integration/option-a-custom-mcp-portal

export MCP_SERVER_URL=https://jira-mcp-server-YOUR_NUMBER.us-central1.run.app
export GOOGLE_CLOUD_PROJECT=your-project-id
export GOOGLE_CLOUD_LOCATION=us-central1

python register_mcp_in_registry.py
```

---

## Step 3: Create Custom MCP Data Store in GE

Console → **Gemini Enterprise** → **Apps** → (your app) → **Data stores** → **New data store** → **Custom MCP Server**

Fill in:
- **MCP Server URL:** `https://jira-mcp-server-YOUR_NUMBER.us-central1.run.app/mcp`
- **Authorization URL:** `https://auth.atlassian.com/authorize`
- **Authorization URL Parameters:** `&audience=api.atlassian.com&prompt=consent`
- **Token URL:** `https://auth.atlassian.com/oauth/token`
- **Client ID:** (from Step 1 of Option A - your developer.atlassian.com app)
- **Client Secret:** (from Step 1 of Option A)
- **Scopes:** `read:jira-work write:jira-work read:jira-user offline_access`

**Note:** For custom MCP servers, use standard Atlassian OAuth (`auth.atlassian.com`), NOT the Remote MCP endpoints (`cf.mcp.atlassian.com`) which are for Atlassian's hosted MCP only.

Click **Continue** → **Login**

---

## Step 4: Complete OAuth

- **Atlassian login:** Enter your credentials
- **Site selection:** Choose your Jira site (e.g., yourcompany.atlassian.net)
- **Permissions:** Approve View/Update jira-work
- Popup closes automatically

---

## Step 5: Enable Tools

1. Click your new Custom MCP Server in the data stores list
2. **Actions** tab → **Reload custom actions**
3. Check these tools:
   - `searchJiraIssuesUsingJql`
   - `getJiraIssue`
   - `getVisibleJiraProjects`
   - `summarizeJiraIssues`
   - `getJiraIssuesReport`
4. Click **Enable actions**

---

## Step 6: Test

1. Open GE chat
2. Make sure your MCP datastore toggle is ON in Sources
3. Ask: `"List 5 recent bugs"`

**Expected:** Direct tool calls to your MCP server, formatted responses.

---

## Cost Comparison

| | Option A | Option C |
|---|----------|----------|
| **Agent Engine** | ~$0.10/1K requests | $0 |
| **ADK API calls** | ~$0.02/1K requests | $0 |
| **Cloud Run** | ~$0.05/1K requests | ~$0.05/1K requests |
| **Total** | **~$0.17/1K** | **~$0.05/1K** |

**Savings:** ~70% cost reduction by skipping Agent Engine layer.

---

## What You Lose vs Option A

- **No custom prompts** - GE assistant's defaults only
- **No before_model_callback** - can't bound pagination context
- **No thinking transparency** - GE doesn't expose agent thinking
- **Less control** - formatting is GE's standard output

## What You Keep

- ✅ Same 7 custom tools (your code)
- ✅ Same accuracy potential (depends on GE assistant quality)
- ✅ Agent Registry governance
- ✅ Per-user OAuth (Jira ACLs enforced)

---

## When to Use Option C

**Choose Option C if:**
- Cost is primary concern
- GE assistant's prompts are good enough
- You don't need custom pagination logic
- Simple Jira queries (<50 issues)

**Choose Option A if:**
- You need <2% hallucination (production ticketing)
- Custom prompts/formatting matter
- Handling large result sets (>50 issues)
- Full control over agent behavior

---

## Files

**Reuses from Option A:**
- `option-a-custom-mcp-portal/jira_server/` - MCP server code
- `option-a-custom-mcp-portal/register_mcp_in_registry.py` - Registry registration

**No new code needed** - pure configuration!

---

## Next Steps

After setup:
- Monitor Cloud Run logs for tool calls
- Check GE's Actions tab to see enabled tools
- If cache expires: Actions tab → Reload custom actions

**Troubleshooting:** Same as Option B - see `option-b-direct-remote-mcp/README.md`
