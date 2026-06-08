---
description: Tear down the replicated Gemini Enterprise MCP Co-work Portal application folder and metadata
---
# Destroying the Replicated GE MCP Co-work Portal

This workflow removes all folders, files, and local configuration metadata created by the Co-work Portal replication recipe.

---

## 1. Clean up Workspace and Files
Run the following commands to delete the replicated application directory and clean up the active workspace's local `.agent` folder configurations:

// turbo
```bash
# 1. Terminate any active backend/frontend portal processes
kill -9 $(lsof -t -i:8001) 2>/dev/null || true
kill -9 $(lsof -t -i:5173) 2>/dev/null || true

# 2. Delete the replicated folder
rm -rf ./ge-mcp-cowork-portal

# 3. Clean up the registered workflows/skills from the active workspace root
rm -rf ./.agent/skills/replicating-ge-mcp-cowork
rm -f ./.agent/workflows/deploy-ge-mcp-cowork.md
rm -f ./.agent/workflows/destroy-ge-mcp-cowork.md
```

