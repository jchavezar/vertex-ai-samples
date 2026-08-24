---
name: replicating-adk-gemini-enterprise-e2e
description: Expert guide for building, testing, deploying, and registering Google ADK Agents to Vertex AI Agent Engine with Cloud Trace, Cloud Logging, and Gemini Enterprise.
---

# Replicating ADK Agent on Vertex AI Agent Engine & Gemini Enterprise

This skill provides step-by-step instructions for Antigravity agents to reproduce, deploy, and verify an enterprise ADK Agent from scratch.

## Step-by-Step Reproduction Blueprint

### 1. Environment & Setup
Verify ADC authentication and staging bucket:
```bash
uv run agy-recipes/adk-gemini-enterprise-e2e/scripts/setup.py
```

### 2. Local Agent Smoke Testing
Run the offline ADK runner to verify tool schemas, function calls, and instruction adherence:
```bash
cd semiautonomous-agents/adk-gemini-enterprise-e2e
uv run python scripts/test_local.py
```

### 3. Deploy to Vertex AI Agent Engine Runtime
Deploys `reasoning_engines.AdkApp` with `enable_tracing=True` for OpenTelemetry, Cloud Trace, and Cloud Logging:
```bash
uv run python deploy.py
```

### 4. Register into Gemini Enterprise
Registers the deployed Reasoning Engine with Discovery Engine v1alpha Assist API and shares it with `ALL_USERS`:
```bash
uv run python register.py
```

### 5. Verification
Test the deployed remote engine via REST SSE stream:
```bash
uv run python scripts/test_remote.py
```
