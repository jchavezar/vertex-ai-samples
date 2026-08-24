# Recipe: ADK Agent on Vertex AI Agent Engine & Gemini Enterprise

This recipe automates the provisioning, local verification, cloud runtime deployment, and Gemini Enterprise registration of an enterprise Google ADK agent.

## Architecture
- **Framework**: Google Agent Development Kit (ADK) `LlmAgent` (`gemini-2.5-flash`).
- **Runtime**: Vertex AI Agent Engine (`reasoning_engines.AdkApp`) with `enable_tracing=True` (Cloud Trace & Cloud Logging).
- **Registration**: Gemini Enterprise Discovery Engine v1alpha Assist API (`/assistants/default_assistant/agents`) with `ALL_USERS` sharing.

## Required Google Cloud APIs
- `aiplatform.googleapis.com` (Vertex AI API)
- `discoveryengine.googleapis.com` (Discovery Engine / Gemini Enterprise API)
- `cloudtrace.googleapis.com` (Cloud Trace API)
- `logging.googleapis.com` (Cloud Logging API)

## IAM Roles Required
- `roles/aiplatform.user`
- `roles/discoveryengine.admin`
- `roles/storage.objectAdmin` (for staging bucket)

## Reproduction Workflow
```bash
# 1. Setup & Environment Validation
uv run agy-recipes/adk-gemini-enterprise-e2e/scripts/setup.py

# 2. Local Offline Smoke Test
cd semiautonomous-agents/adk-gemini-enterprise-e2e && uv run python scripts/test_local.py

# 3. Deploy to Vertex AI Agent Engine (with Cloud Trace & Logging)
uv run python deploy.py

# 4. Register in Gemini Enterprise
uv run python register.py

# 5. Teardown
uv run agy-recipes/adk-gemini-enterprise-e2e/scripts/teardown.py
```
