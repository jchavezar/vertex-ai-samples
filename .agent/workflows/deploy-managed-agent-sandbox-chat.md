---
description: Deploy and verify the Vertex AI Managed Agent Sandbox Chat & A2A Wire-Tap platform.
---

1. Run the recipe setup script:
// turbo
`uv run agy-recipes/managed-agent-sandbox-chat/scripts/setup.py`

2. Run the interaction verification test:
// turbo
`uv run agy-recipes/managed-agent-sandbox-chat/scripts/test_recipe.py`

3. Start the application servers:
// turbo
`./antigravity-sandbox-chat/start.sh`
