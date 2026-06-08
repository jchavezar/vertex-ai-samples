---
description: Tear down the replicated Gemini Enterprise MCP Co-work Portal application folder and metadata
---
# Destroying the Replicated GE MCP Co-work Portal

This workflow removes all folders, files, and local configuration metadata created by the Co-work Portal replication recipe.

---

## 1. Execute Teardown Script
To delete the replicated folder and clean up setup history:

// turbo
```bash
uv run agy-recipes/ge-mcp-cowork/scripts/teardown.py
```
*(This script will prompt you for final confirmation in the terminal before deleting any directories).*
