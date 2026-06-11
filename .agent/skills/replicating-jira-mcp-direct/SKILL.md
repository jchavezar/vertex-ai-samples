---
name: replicating-jira-mcp-direct
description: Orchestrates setup, testing, and teardown of the jira-mcp-direct recipe under agy-recipes/. Use when the user requests deployment, replication, or testing of the two direct Atlassian Jira MCP connectors (Rovo hosted + Custom Cloud Run).
---

# Replicating Jira MCP Direct Integration Recipe

This skill guides the agent and user through deploying, validating, and destroying the direct Atlassian Jira MCP integration connectors in Gemini Enterprise.

## 📋 Pre-Flight Checklist

1. Ensure a `.env` file exists in `agy-recipes/jira-mcp-direct/` with:
   * `GE_PROJECT_ID` (GCP Project ID, e.g. `vtxdemos`)
   * `GE_PROJECT_NUMBER` (GCP Project Number, e.g. `254356041555`)
   * `GE_ENGINE_ID` (Gemini Enterprise Engine ID, e.g. `jira-testing_1778158449701`)
   * `ATLASSIAN_CLIENT_ID` (Standard Atlassian App Client ID, for Option C)
   * `ATLASSIAN_CLIENT_SECRET` (Standard Atlassian App Client Secret, for Option C)
2. Ensure you have active `gcloud` credentials authorized for your target project.

---

## 🚀 Setup & Deploy

Execute the setup script:
```bash
uv run agy-recipes/jira-mcp-direct/scripts/setup.py
```

### Required Manual Console Steps (OAuth Consent)
Because Atlassian requires interactive user authorization (3LO), you must complete the final wiring in the Cloud Console:

1. **Atlassian Hosted Rovo Connector (`jiramcp-rovo-recipe`)**:
   * Open the GE Console -> **Data stores** -> select `jiramcp-rovo-recipe_mcp_data` -> **Actions** tab.
   * Click **Reload custom actions** to sync tools.
   * Enable desired tools (e.g. `searchJiraIssuesUsingJql`, `getJiraIssue`).
   * Click **Re-authenticate** and paste DCR Client ID/Secret from `~/.secrets/atlassian-rovo-dcr-ge.json`.
   * Complete the Atlassian consent flow for your Jira site (Jira only, uncheck Confluence/Compass).

2. **Custom Cloud Run MCP Connector (`jiramcp-custom-recipe`)**:
   * Open the GE Console -> **Data stores** -> select `jiramcp-custom-recipe_mcp_data` -> **Actions** tab.
   * Click **Reload custom actions** to sync tools.
   * Enable desired tools and click **Re-authenticate**.
   * Paste your standard Atlassian App Client ID and Secret, and complete the consent flow.

---

## 🧪 E2E Verification

Once both connectors are active (showing green checks in the console), run the test script:
```bash
uv run agy-recipes/jira-mcp-direct/scripts/test_recipe.py
```

---

## 🧹 Cleanup & Teardown

To delete all resources created by this recipe:
```bash
uv run agy-recipes/jira-mcp-direct/scripts/teardown.py
```
This cleanly removes both datastores in Gemini Enterprise, detaches them from the engine, and deletes the Cloud Run server.
