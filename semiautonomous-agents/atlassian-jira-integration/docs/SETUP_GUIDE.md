# Atlassian Jira Integration with Gemini Enterprise - Customer Guide

Complete step-by-step guide to connect your Atlassian Jira instance to Google Gemini Enterprise using the Atlassian Remote MCP Server.

## What You'll Get

After setup, users can ask questions in Gemini Enterprise chat like:
- "Show me 10 recent bugs"
- "List issues assigned to me"
- "What's the status of PROJ-123?"
- "Create a new bug for the login issue"

The assistant will search your Jira instance and return real data.

## Prerequisites

- **Atlassian:** Admin access to your Jira Cloud site (e.g., yourcompany.atlassian.net)
- **Google Cloud:** Gemini Enterprise app already created in your GCP project
- **Terminal access:** Ability to run a single curl command
- **Time:** ~15 minutes

## Step 1: Register OAuth Client (One-Time)

Open a terminal and run this command:

```bash
curl -X POST https://cf.mcp.atlassian.com/v1/register \
  -H "Content-Type: application/json" \
  -d '{"redirect_uris":["https://vertexaisearch.cloud.google.com/oauth-redirect"],"client_name":"your-company-gemini-jira","token_endpoint_auth_method":"client_secret_basic","grant_types":["authorization_code","refresh_token"],"response_types":["code"]}'
```

**Save the response** - you'll need `client_id` and `client_secret`. Example:
```json
{
  "client_id": "abc123xyz",
  "client_secret": "secret456def",
  ...
}
```

**Note:** This is NOT creating an app at developer.atlassian.com. The Atlassian Remote MCP server has its own separate OAuth system. Apps from developer.atlassian.com will NOT work.

## Step 2: Create Custom MCP Data Store in Console

1. Go to: [Google Cloud Console](https://console.cloud.google.com) → **Gemini Enterprise** → **Apps**
2. Click your app name
3. Click **Connected data stores** (left sidebar)
4. Click **New data store** button
5. Select: **Custom MCP Server**

## Step 3: Configure the MCP Connection

Fill in these exact values:

| Field | Value |
|-------|-------|
| **MCP Server URL** | `https://mcp.atlassian.com/v1/mcp` |
| **Authorization URL** | `https://mcp.atlassian.com/v1/authorize` |
| **Authorization URL Parameters** | (leave blank) |
| **Token URL** | `https://cf.mcp.atlassian.com/v1/token` |
| **Client ID** | Paste from Step 1 |
| **Client Secret** | Paste from Step 1 |
| **Scopes** | `read:jira-work write:jira-work read:jira-user read:me offline_access` |

**Critical:** The Token URL MUST include `cf.` - using `auth.atlassian.com` will fail with "invalid_client".

Click **Continue**, then **Login**.

## Step 4: Complete OAuth Authorization

Three screens will appear:

**Screen 1: MCP Server Consent**
- Shows "Atlassian Rovo MCP server is requesting access"
- Check: **Jira** ✓
- Optional: Check Confluence if you want Confluence access ✓
- Uncheck: Compass (unless you use it)
- Click **Approve**

**Screen 2: Atlassian Login**
- Enter your Atlassian admin email
- Enter password
- Click **Log in**

**Screen 3: Site & Permissions Consent**
- Select your Atlassian site (e.g., yourcompany.atlassian.net)
- Review requested permissions:
  - View jira-work
  - Update jira-work
  - View me
- Click **Accept**

The popup closes automatically. You should see "Connector created successfully" in the console.

## Step 5: Enable Jira Tools

1. In the data stores list, click your new **Custom MCP Server** connector
2. Click the **Actions** tab
3. Click **Reload custom actions** button (waits ~5-10 seconds)
4. You'll see a list of ~30-37 tools

**Check these essential Jira tools:**
- ✓ `searchJiraIssuesUsingJql` - Search for issues
- ✓ `getJiraIssue` - Get details of specific issue
- ✓ `getVisibleJiraProjects` - List accessible projects
- ✓ `createJiraIssue` - Create new issues (optional)
- ✓ `editJiraIssue` - Update issues (optional)

**Uncheck all Confluence tools** if you don't need Confluence (they require admin permissions).

5. Click **Enable actions** button
6. Should see: "Data connector actions updated successfully"

## Step 6: Test the Integration

1. Go to your Gemini Enterprise chat interface
2. Click **New chat** (important - don't reuse old chats)
3. Ask: `"List 5 recent Jira issues"`

**Expected:** The assistant searches your Jira and returns issue keys, summaries, and status.

**If you get empty results:**
- Make sure the authenticated user can see issues in Jira (check at yourcompany.atlassian.net)
- Try: `"What Jira projects can I access?"` first
- Then: `"Show me 5 issues from project [PROJECT_KEY]"`

## Known Issues & Workarounds

### Tools Stop Working After Hours

**Symptom:** Queries that worked earlier return "Jira connector unavailable" after a few hours.

**Cause:** Tool registry cache expires.

**Fix:**
1. Console → Data stores → (your MCP connector) → Actions tab
2. Click **Reload custom actions**
3. Wait 30 seconds
4. Try your query again (no need to re-enable or re-authenticate)

This is a known limitation of custom MCP servers in Gemini Enterprise.

### 403 Forbidden Errors in Logs

**Symptom:** Queries timeout or fail. Logs show "403 FORBIDDEN" for Confluence API.

**Cause:** Confluence tools are enabled but you don't have Confluence admin permissions.

**Fix:**
- Actions tab → uncheck all Confluence tools → Enable actions again
- Or add Confluence admin scopes during OAuth consent

### "Invalid Client" Error

**Symptom:** OAuth popup shows "The provided client secret is invalid"

**Cause:** Used credentials from developer.atlassian.com instead of dynamic client registration.

**Fix:**
- Re-run Step 1 to get fresh credentials from `cf.mcp.atlassian.com/v1/register`
- Update the connector with new client_id/secret via Re-authenticate dialog

## Architecture Summary

```
Your Users
    ↓
Gemini Enterprise Chat
    ↓
Custom MCP Data Store (configured above)
    ↓
Atlassian Remote MCP Server (mcp.atlassian.com)
    ↓
Your Jira Instance (yourcompany.atlassian.net)
```

**You manage:** Gemini Enterprise app, OAuth credentials  
**Atlassian manages:** The MCP server infrastructure  
**Google manages:** The connector, tool routing, chat UI

## Security Notes

- Each user authenticates with **their own** Atlassian account during first use
- Access tokens are scoped to what that user can see in Jira
- The shared client_id/secret are used only for OAuth handshake
- Tokens refresh automatically every 24 hours

## Support

If issues persist:
- Check connector status: Console → Data stores → (connector) → should show "Active"
- View logs: Click **View logs** link on connector page
- Contact Google Cloud Support with your connector ID

## Complete Files Reference

This guide is part of a larger reference implementation. For automation scripts:
- See: `semiautonomous-agents/atlassian-on-gemini-enterprise/option-b-direct-remote-mcp/`
- Python scripts for API-driven setup
- Evaluation harness for testing

For quick bash version:
- See: `semiautonomous-agents/atlassian-mcp-setup/`  
- Simpler bash scripts
- Quick start guide
