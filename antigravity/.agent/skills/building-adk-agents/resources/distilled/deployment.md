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
Use `vertexai.Client()` and `AdkApp` for deployment and lifecycle management.

### Deployment Example
```python
import vertexai
from vertexai.agent_engines import AdkApp
from my_agent import root_agent

vertexai.init(project="my-project", location="us-central1")
client = vertexai.Client(project="my-project", location="us-central1")

# Wrap the ADK agent
deployment_app = AdkApp(agent=root_agent, enable_tracing=True)

# Create or Update
remote_app = client.agent_engines.create(
    agent=deployment_app,
    config={
        "display_name": "my-agent-engine",
        "staging_bucket": "gs://my-bucket",
        "requirements": "requirements.txt",
        "extra_packages": ["agent.py"],
    }
)
```

### Lifecycle & Testing
```python
# List Engines
engines = client.agent_engines.list()

# Async Testing
async def test_agent(app):
    session = await app.async_create_session(user_id="test_user")
    async for event in app.async_stream_query(
        user_id="test_user",
        session_id=session.id,
        message="Hello!"
    ):
        print(event)
```

---
*Reference: https://docs.cloud.google.com/agent-builder/agent-engine/deploy*
