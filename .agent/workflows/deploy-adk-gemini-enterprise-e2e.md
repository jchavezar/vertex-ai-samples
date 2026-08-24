---
description: Deploy, verify, and register the ADK Agent in Vertex AI Agent Engine and Gemini Enterprise.
---

1. Run the recipe setup and verification:
// turbo
`uv run agy-recipes/adk-gemini-enterprise-e2e/scripts/setup.py`

2. Run local offline smoke test:
// turbo
`cd semiautonomous-agents/adk-gemini-enterprise-e2e && uv run python scripts/test_local.py`

3. Deploy to Vertex AI Agent Engine:
// turbo
`cd semiautonomous-agents/adk-gemini-enterprise-e2e && uv run python deploy.py`

4. Register the agent in Gemini Enterprise:
// turbo
`cd semiautonomous-agents/adk-gemini-enterprise-e2e && uv run python register.py`
