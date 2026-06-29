# Google ADK Agent // Bain Financial Analysis Agent

This directory contains the Google Agent Development Kit (ADK) implementation of the **Bain Financial Analysis Agent**, configured to run on Vertex AI Agent Runtime with full OpenTelemetry tracing enabled (`enable_tracing=True`).

## Features & Enterprise Guardrails

1. **Two-Pillar Authentication**:
   - **Pillar A (End-User Delegation)**: Extracts the end-user Microsoft Graph OAuth token from the session state key `sharepointauth_new`, passing it via the `X-User-Token` header to ensure native SharePoint access control list (ACL) enforcement at the source.
   - **Pillar B (Service-to-Service Ingress)**: Automatically generates a Google Cloud OIDC identity token for the runtime service account, passing it via `Authorization: Bearer` to authorize secure ingress into the private Cloud Run SharePoint MCP server.
2. **Strict Grounding & Two-Step Verification Mandate**:
   - The agent is instructed to avoid pre-trained hallucinations entirely. When queried about a company or individual (e.g., Meridian Technologies or Jennifer Walsh), it must first call `search` to locate relevant files from the `sockcop` SharePoint site, and then call `read_file` or `fetch` to read the actual text content before answering.
3. **Rigorous Clickable Citations**:
   - Every factual claim must conclude with a direct markdown link formatted exactly as `[Document Title](webUrl)`.
4. **Structured Output Support**:
   - Built on `gemini-2.5-pro` with Pydantic output schema definitions for streaming clean financial tables and widget data directly to the frontend.

---

## Developer Setup & Execution

### 1. Initialize Python Environment (`uv`)
We mandate `uv` for all Python project management, environment handling, and execution to ensure maximum speed and complete environment isolation.

```bash
# Initialize virtual environment
uv venv

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
uv pip install -r requirements.txt
```

### 2. Local Execution & Verification
You can easily test the agent locally before cloud deployment using either terminal streaming (`async_stream`) or the built-in ADK Web UI (`adk web`):

#### Method A: Terminal Streaming (`async_stream`)
You can verify the agent's initialization banner and test its query streaming directly from your terminal:
```bash
# Verify initialization & loaded tools
uv run agent.py
```

To run an interactive streaming query in Python:
```python
import asyncio
from agent import root_agent

async def test():
    async for chunk in root_agent.async_stream("Retrieve financial summary for Meridian Technologies"):
        print(chunk.text, end="", flush=True)

asyncio.run(test())
```

#### Method B: ADK Web UI (`adk web`)
You can launch the built-in ADK web testing harness to interact with your agent in a browser view:
```bash
# Launch ADK local web server
uv run adk web --agent agent:root_agent --port 8025
```
*(Remember to forward port `8025` to your local machine if testing over SSH).*


### 3. Deploy to Vertex AI Agent Runtime
Deploy the agent to the GKE-backed Vertex AI Agent Runtime. The deployment script packages `agent.py`, wraps it in `AdkApp(enable_tracing=True)` for full observability, and uploads it to Google Cloud:

```bash
uv run deploy.py
```

*Note the resulting `REASONING_ENGINE_ID` printed in the terminal console.*

### 4. (Optional) Register in Gemini Enterprise
*Note: If you are interacting exclusively through the Minimalist Custom UI, you do NOT need to execute this step. The Custom UI invokes the Reasoning Engine / Agent Gateway directly.*

```bash
# Only required if attaching to the Gemini Enterprise Chat UI
export REASONING_ENGINE_ID="8655608971282874368"
export CLIENT_SECRET="your_entra_client_secret_here"
uv run register.py
```

