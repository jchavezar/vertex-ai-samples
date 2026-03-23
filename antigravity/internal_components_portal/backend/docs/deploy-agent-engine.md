# Agent Engine Deployment Guide: Internal Zero Leak Portal

This guide provides instructions for deploying the `router_agent` to Google Cloud's Next-Generation Agent Engine (ReasoningEngine).

## Prerequisites
1. Ensure you have the `vtxdemos` GCP project configured.
2. The `uv` package manager must be installed.
3. Your local environment must be authenticated with Google Cloud (`gcloud auth application-default login`).
4. Ensure the `gs://vtxdemos-staging` Cloud Storage bucket exists for upload staging.

## Why Deploy to Agent Engine?
Currently, the major reason this backend deploys a proxy Agent Engine is to unlock the capability to use the **Vertex AI Memory Bank** (`VertexAiSessionService`). Memory Bank strictly enforces that an active Agent Engine `ReasoningEngine` ID is supplied to store historical session information on GCP instead of ephemeral in-memory storage.

## Dynamic Regional Failover
This deployment incorporates a seamless global interception protocol:
Deploying to Agent Engine requires targeting standard regions (like `us-central1`). However, advanced models like `gemini-3-flash-preview` often operate on `global` or restricted regions in preview states.
To safely allow Agent Engine to boot the agent inside `us-central1` while calling `gemini-3`, the `get_router_agent()` initialization actively intercepts the model string, and if "gemini-3" is detected, dynamically anchors the `LlmAgent` to a customized `google.genai.Client` operating in `global`.

## Deployment Steps

1. Navigate to the `backend` directory.
2. Ensure dependencies are satisfied:
   ```bash
   uv sync
   ```
3. Execute the automatic deployment script:
   ```bash
   uv run python deploy_agent_engine.py
   ```

### Console Validation
- The terminal will indicate `Updating...` or `Creating new...`.
- Creating a completely new Agent Engine container image usually takes **5–7 minutes**.
- Once complete, the terminal will output the literal `ReasoningEngine ID` (e.g. `projects/123/locations/us-central1/reasoningEngines/456`).
- Copy this ID! You will need to insert it into `main.py` when initializing `VertexAiSessionService()`.

## Validation and Testing
Test the connectivity by executing:
```bash
uv run python -c "from google.adk.sessions import VertexAiSessionService; print(VertexAiSessionService(project='vtxdemos', location='us-central1', agent_engine_id='YOUR_ID'))"
```
