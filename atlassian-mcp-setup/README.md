# Atlassian MCP + Gemini Enterprise Integration

Complete guide to integrate Atlassian Rovo MCP server (Jira/Confluence) with Gemini Enterprise.

## Prerequisites

- Atlassian account with admin access to your Jira/Confluence site
- Gemini Enterprise app created in vtxdemos project
- Email for Atlassian login: `admin@jesusarguelles.demo.altostrat.com`

## Step 1: Register OAuth Client

Run the script:
```bash
cd ~/semiautonomous-agents/atlassian-mcp-setup
./register_oauth_client.sh
```

This will output:
- `client_id` - copy this
- `client_secret` - copy this

These credentials are saved to `/tmp/atlassian_oauth_creds.json`.

## Step 2: Create Custom MCP Data Store in GE Console

Go to: https://console.cloud.google.com/gemini-enterprise → Apps → (your app) → Data stores → **New data store**

Select: **Custom MCP Server**

Fill the form:
```
MCP Server URL: https://mcp.atlassian.com/v1/mcp
Authorization URL: https://mcp.atlassian.com/v1/authorize
Authorization URL Parameters: (leave blank)
Token URL: https://cf.mcp.atlassian.com/v1/token
Client ID: (paste from step 1)
Client Secret: (paste from step 1)
Scopes: read:jira-work write:jira-work read:jira-user read:me offline_access
```

**IMPORTANT:** Do NOT add Confluence scopes even if you want Confluence access. Confluence requires admin privileges we don't have.

Click **Continue** → **Login**

## Step 3: OAuth Consent Flow

**Screen 1: MCP Consent**
- Check: **Jira** ✓
- Uncheck: **Confluence** ✗
- Uncheck: **Compass** ✗
- Click **Approve**

**Screen 2: Atlassian Login**
- Email: `admin@jesusarguelles.demo.altostrat.com`
- Password: (enter your Argolis password)
- Click **Log in** / **Continue**

**Screen 3: Site Consent**
- Select site: **sockcop.atlassian.net**
- Review permissions (View/Update jira-work, View me)
- Click **Accept**

OAuth popup will close automatically.

## Step 4: Enable Jira Actions

After OAuth completes:

1. Go to: (your connector) → **Actions** tab
2. Click **Reload custom actions** (waits ~5s, discovers 37 tools)
3. **Check ONLY these Jira tools:**
   - `searchJiraIssuesUsingJql` ✓
   - `getJiraIssue` ✓
   - `createJiraIssue` (optional)
   - `editJiraIssue` (optional)
   - `getVisibleJiraProjects` (optional)
4. **Uncheck all Confluence/Compass tools** (they cause 403 errors)
5. Click **Enable actions**

Should see: "Data connector actions updated successfully."

## Step 5: Create Custom Agent (REQUIRED)

**Why:** The default GE assistant has a bug where custom MCP tools don't appear in its tool registry. You must use a custom agent.

1. Go to: Agents → **New agent**
2. Choose: **No-code agent builder**
3. Name: `Jira Assistant`
4. Instructions:
   ```
   You are a Jira assistant. When users ask about Jira issues, tickets, bugs, or projects, use the searchJiraIssuesUsingJql and getJiraIssue tools.
   
   For "list N issues" queries, call searchJiraIssuesUsingJql with JQL like "order by created DESC" and maxResults=N.
   
   Format results as a table with: Key, Summary, Status, Assignee.
   ```
5. Tools: In the dropdown, select your jiramcp connector → check:
   - `searchJiraIssuesUsingJql`
   - `getJiraIssue`
6. Data sources: (none needed for tools)
7. Click **Create**

## Step 6: Test

1. Go to your Gemini Enterprise chat
2. In the left sidebar → **Agents** → click **Jira Assistant**
3. Ask: `list 5 jira issues`

Should return real issues from sockcop.atlassian.net (e.g., SMP-912, SMP-911, etc.).

## Troubleshooting

**"Connector unavailable" error:**
- Check Actions tab shows tools as **Enabled** (green checkmark)
- Confirm you're querying the **custom agent**, not the default chat

**403 FORBIDDEN errors in logs:**
- You enabled Confluence tools but OAuth token only has Jira scopes
- Go back to Actions tab, uncheck all Confluence tools, click Enable actions again

**500 timeout:**
- Too many tools enabled causes slow initial sync
- Disable all but the 2 core tools: `searchJiraIssuesUsingJql` and `getJiraIssue`

**The one-time success mystery:**
- The assistant CAN work occasionally but it's unreliable
- Custom agents are the supported path for MCP tool calling

## Important URLs

- Discovery doc: https://mcp.atlassian.com/.well-known/oauth-authorization-server
- OAuth registration: https://cf.mcp.atlassian.com/v1/register
- MCP endpoint: https://mcp.atlassian.com/v1/mcp

## Saved Configuration

Current working config for agentspace-testing engine:
- Connector collection: `jiramcp_1778106767686`
- Client ID: `E7rKFMHq_CC3dgN9`
- Enabled actions: 2 core Jira tools only
