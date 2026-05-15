# Quick Start: Atlassian MCP + Gemini Enterprise

## TL;DR

1. Run `./register_oauth_client.sh` → get credentials
2. GE Console → New data store → Custom MCP → paste values from `./show_config_values.sh`
3. OAuth login with `admin@jesusarguelles.demo.altostrat.com` → check **Jira only**
4. Actions tab → Reload custom actions → enable 2-5 Jira tools
5. Test in default chat

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

### 5. Test

Open Gemini Enterprise chat → new chat → ask "list 5 jira issues"

The assistant should call the Jira tools and return results from your sockcop.atlassian.net instance.

## Common Errors

- **500 timeout:** Confluence tools enabled but no Confluence scopes → disable all Confluence tools in Actions tab
- **403 FORBIDDEN:** Not logged in as Atlassian admin → use admin@jesusarguelles.demo.altostrat.com
- **Empty results:** No issues exist in Jira, or user lacks Browse Projects permission on sockcop.atlassian.net

## Files

- `register_oauth_client.sh` - Calls Atlassian DCR endpoint, saves credentials
- `show_config_values.sh` - Displays values to paste into GE console
- `README.md` - Full detailed guide
- `GETTING_STARTED.md` - This file
