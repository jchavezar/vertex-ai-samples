---
description: Tear down and clean up the Vertex AI Managed Agent Sandbox Chat & A2A Wire-Tap platform.
---

1. Terminate any running local servers on port 8090 and 5174:
// turbo
`kill -9 $(lsof -t -i:8090 -i:5174) 2>/dev/null || true`

2. Run the recipe teardown script:
// turbo
`uv run agy-recipes/managed-agent-sandbox-chat/scripts/teardown.py`
