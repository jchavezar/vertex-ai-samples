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

## Step 5: Test

1. Open your Gemini Enterprise chat
2. Start a new chat
3. Ask: `list 5 jira issues` or `show me recent jira bugs`

Should return issues from sockcop.atlassian.net (e.g., SMP-912, SMP-911, etc.).

If you get "couldn't find any issues", verify:
- Your Atlassian site has issues in accessible projects
- The authenticated user has Browse Projects permission

## Troubleshooting

**"Connector unavailable" error:**
- Check Actions tab shows tools as **Enabled** (green checkmark)
- Click **Reload custom actions** if tools list is empty

**403 FORBIDDEN errors in logs:**
- You enabled Confluence tools but OAuth token only has Jira scopes
- Go back to Actions tab, uncheck all Confluence tools, click Enable actions again

**500 timeout:**
- Too many tools enabled causes slow initial sync
- Disable all but the 2 core tools: `searchJiraIssuesUsingJql` and `getJiraIssue`

**"Couldn't find any issues" (empty results):**
- Verify your Jira site actually has issues: visit sockcop.atlassian.net directly
- Check the authenticated user has Browse Projects permission
- Try a more specific query: "show me issues in project SMP"

**Tools stop working after a few hours:**
- The tool registry cache expires periodically
- **Fix:** Console → (connector) → Actions tab → **Reload custom actions** → wait 30s
- No re-authentication needed - just reload to refresh the tools cache
- This is a known limitation of custom MCP servers in Gemini Enterprise

## Important URLs

- Discovery doc: https://mcp.atlassian.com/.well-known/oauth-authorization-server
- OAuth registration: https://cf.mcp.atlassian.com/v1/register
- MCP endpoint: https://mcp.atlassian.com/v1/mcp

## Saved Configuration

Current working config for agentspace-testing engine:
- Connector collection: `jiramcp_1778106767686`
- Client ID: `E7rKFMHq_CC3dgN9`
- Enabled actions: 2 core Jira tools only
