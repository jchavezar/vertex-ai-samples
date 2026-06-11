---
description: Destroy Jira MCP Direct connectors and clean up all resources
---

A recipe to cleanly remove both registered Jira MCP datastores from Gemini Enterprise, detach them from the application engine, and delete the custom MCP server from Google Cloud Run.

### Step 1: Execute Teardown Script
Run the teardown script using `uv` to delete all created resources and configuration files:

```bash
uv run agy-recipes/jira-mcp-direct/scripts/teardown.py
```
