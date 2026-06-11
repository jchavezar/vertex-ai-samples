---
description: Deploy Jira MCP Direct connectors (Atlassian Rovo + Custom Cloud Run) and wire them to Gemini Enterprise
---

A recipe to deploy a custom MCP server to Cloud Run, dynamically register a DCR client for Rovo, create both Custom MCP datastores in Gemini Enterprise, and wire them to the Gemini Enterprise application engine.

### Step 1: Execute Setup Script
Run the setup script using `uv` to deploy the Cloud Run service and register the datastores:

```bash
uv run agy-recipes/jira-mcp-direct/scripts/setup.py
```

### Step 2: Complete Manual Console Steps
Because Atlassian requires interactive user OAuth consent (3LO), you must complete the final connector auth steps in the Cloud Console:

1. **Atlassian Hosted Rovo Connector (`jiramcp-rovo-recipe`)**:
   * Open the GE Console -> **Data stores** -> select `jiramcp-rovo-recipe_mcp_data` -> **Actions** tab.
   * Click **Reload custom actions** to sync tools.
   * Enable desired tools (e.g. `searchJiraIssuesUsingJql`, `getJiraIssue`).
   * Click **Re-authenticate** and paste DCR Client ID/Secret from `~/.secrets/atlassian-rovo-dcr-ge.json`.
   * Complete the Atlassian consent flow.

2. **Custom Cloud Run MCP Connector (`jiramcp-custom-recipe`)**:
   * Open the GE Console -> **Data stores** -> select `jiramcp-custom-recipe_mcp_data` -> **Actions** tab.
   * Click **Reload custom actions** to sync tools.
   * Enable desired tools and click **Re-authenticate**.
   * Paste your standard Atlassian App Client ID and Secret, and complete the consent flow.

### Step 3: Run E2E Verification
Once both connectors show as **Active** in the Console, run the test script to verify end-to-end connectivity:

```bash
uv run agy-recipes/jira-mcp-direct/scripts/test_recipe.py
```
