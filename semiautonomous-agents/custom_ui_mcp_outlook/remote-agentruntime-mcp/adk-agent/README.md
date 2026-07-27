# M365 Outlook Executive Agent - Developer Guide

This directory contains the Python codebase for the **M365 Outlook Executive Agent**, built with the **Google Agent Development Kit (ADK)** and deployed on **Vertex AI Agent Runtime** (Reasoning Engine).

---

## 1. Prerequisites & Environment Setup

### 1.1 Python Environment
We use Python 3.10+ (specifically Python 3.11/3.12 recommended). Initialize your virtual environment and install dependencies:

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 1.2 Configuration (`.env`)
Make sure your `.env` file (stored in the parent directory) contains the following parameters:

```env
# Cloud Run endpoint of the Outlook MCP server
OUTLOOK_MCP_URL=https://ms365-mcp-server-254356041555.us-central1.run.app/mcp

# OAuth client secret registered in Azure AD
CLIENT_SECRET=your_microsoft_graph_client_secret_here
```

---

## 2. Codebase Reference

Our agent codebase is factored, simple, and standard ADK:

### `agent.py`
Defines the `LlmAgent` and M365 Outlook tools (email search, read, flag, move, delete, create event, send email). 

#### Token Selection Logic
The agent intercepts the dynamic `CallbackContext` session state from Gemini Enterprise. It searches all session keys to find the Microsoft Graph OAuth token (key name: `outlookauth_new`) and puts it into the `X-User-Token` header.

```python
        # Extract user JWT from GE state and put in X-User-Token
        for key, val in state_dict.items():
            if isinstance(val, str) and val.startswith("eyJ") and len(val) > 100:
                payload = decode_jwt_payload(val)
                iss = str(payload.get("iss", "")).lower()
                aud = str(payload.get("aud", "")).lower()
                
                is_ms_graph = (
                    "microsoftonline" in iss or 
                    "windows.net" in iss or 
                    "graph.microsoft.com" in aud or 
                    "00000003-0000-0000-c000-000000000000" in aud
                )
                if is_ms_graph:
                    candidates.append((key, val, iss, aud))
```

### `deploy.py`
Packages the agent code, dependencies (`requirements.txt`), and environment variables, and pushes them to Vertex AI Agent Runtime:

```bash
# Trigger redeployment/update of the Reasoning Engine
python3 deploy.py
```

### `register.py`
Handles registration of the OAuth authorization profile and the ADK-backed Agent within the Gemini Enterprise platform via Discovery Engine API:

```bash
# Export the deployed Reasoning Engine ID
export REASONING_ENGINE_ID="123456789"

# Register authorization and agent
python3 register.py
```

---

## 3. Local Diagnostic Commands

### Read Deployed Agent Logs
To monitor token selection and tool-invocation details, run:

```bash
gcloud logging read "resource.type=aiplatform.googleapis.com/ReasoningEngine AND \"[Agent]\"" \
    --project vtxdemos \
    --limit=100 \
    --format="value(textPayload)"
```
