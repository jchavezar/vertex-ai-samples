# Quick Start: Atlassian MCP + Gemini Enterprise

## TL;DR

1. Run `./register_oauth_client.sh` → get credentials
2. GE Console → New data store → Custom MCP → paste values from `./show_config_values.sh`
3. OAuth login with `admin@jesusarguelles.demo.altostrat.com` → check **Jira only**
4. Actions tab → Reload custom actions → enable 2-5 Jira tools
5. **Must create custom agent** (default assistant won't work)

## Full Steps

### 1. Register OAuth Client

```bash
cd ~/semiautonomous-agents/atlassian-mcp-setup
./register_oauth_client.sh
```

Output shows `client_id` and `client_secret`.

### 2. Create Data Store

GE Console → Apps → (your app) → Data stores → **New data store** → **Custom MCP Server**

Run this to see values:
```bash
./show_config_values.sh
```

Copy/paste into the form.

### 3. OAuth Login

- MCP screen: Check **Jira**, uncheck Confluence/Compass
- Atlassian login: `admin@jesusarguelles.demo.altostrat.com`
- Site consent: sockcop.atlassian.net → Accept

### 4. Enable Tools

Connector → Actions tab → **Reload custom actions** → check:
- `searchJiraIssuesUsingJql`
- `getJiraIssue`

Click **Enable actions**.

### 5. Create Agent

**CRITICAL:** Default assistant doesn't support custom MCP. You MUST create an agent.

Agents → New agent → Name: "Jira" → Tools: select jiramcp connector → Create

### 6. Test

Chat with **Jira agent** (not default chat) → ask "list 5 jira issues"

## Why It Failed Without Agent

Custom MCP tools don't populate in the default assistant's `toolRegistry`. They show "Enabled" in console but `widgetListTools` returns empty. Only custom agents can call them.

## Common Errors

- **500 timeout:** Confluence tools enabled but no Confluence scopes → disable them
- **403 FORBIDDEN:** Not logged in as Atlassian admin → use admin@jesusarguelles.demo.altostrat.com
- **Empty results:** Querying default assistant instead of custom agent

## Files

- `register_oauth_client.sh` - Calls Atlassian DCR endpoint, saves credentials
- `show_config_values.sh` - Displays values to paste into GE console
- `README.md` - Full detailed guide
- `GETTING_STARTED.md` - This file
