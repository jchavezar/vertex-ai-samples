# 🚀 Distilled Deployment Guide

## 1. Local Development
Use the CLI to test:
```bash
# Interactive chat
adk run agent.py

# Web UI (Interactive Debugging)
adk web --port 8000
```

## 2. Cloud Run (Serverless)
Standard containerized deployment.
```bash
# General flow
gcloud run deploy my-agent --source .
```
- Ensure `.env` variables are mapped to Cloud Run env secrets.

## 3. Vertex AI Agent Engine
High-scale, managed hosting specifically for ADK agents.
```python
from google.adk.deploy import AgentEngine

deployment = AgentEngine(
    name="prod-agent",
    root_agent=my_agent
)
deployment.deploy()
```
*Note: Requires billing enabled and specific Vertex AI permissions.*

---
*Reference: adk-docs/docs/deploy/cloud-run.md*
