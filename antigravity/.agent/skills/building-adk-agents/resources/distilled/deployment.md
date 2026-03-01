# 🚀 Distilled Deployment Guide

## 1. Local Development
Use the CLI to test:
```bash
# Interactive chat
adk run agent.py

# Web UI (Interactive Debugging)
adk web --port 8000
```

## 2. Vertex AI Agent Engine (Recommended)
Use `google.genai.Client()` for deployment and lifecycle management.

```python
from google.genai import Client
from my_agent import root_agent

client = Client(vertexai=True, project="my-project", location="us-central1")

remote_agent = client.agent_engines.create(
    agent=root_agent,
    config={
        "display_name": "my-adk-agent",
        "requirements": ["google-adk", "google-genai"],
        "env_vars": {"GOOGLE_GENAI_USE_VERTEXAI": "true"}
    }
)
```

### Lifecycle Commands
- **List**: `client.agent_engines.list()`
- **Get**: `client.agent_engines.get(name="agent-id")`
- **Delete**: `client.agent_engines.delete(name="agent-id")`

---
*Reference: https://docs.cloud.google.com/agent-builder/agent-engine/deploy*
