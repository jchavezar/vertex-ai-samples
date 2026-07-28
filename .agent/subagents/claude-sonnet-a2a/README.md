# Claude Sonnet 4.6 A2A Agent (with Local MCP Bridge)

This subagent is designed to run on **Vertex AI Agent Runtime (Agent Engine)** under the **A2A (Agent-to-Agent) protocol**. It uses the Claude Sonnet 4.6 model from Model Garden.

By utilizing a **dynamic SSE/MCP bridge**, the cloud-hosted agent can interact directly with your local workspace directory (`~/IdeaProjects/vertex-ai-samples`) to read, write, edit files, and execute shell commands.

---

## Architecture Overview

```
┌───────────────────────────┐
│ Any Antigravity Session   │
└─────────────┬─────────────┘
              │ (Query with A2A client + session state 'MCP_URL')
              ▼
┌───────────────────────────┐
│ Vertex AI Agent Runtime   │ <─── [google_search] (Internet access)
│ (Claude Sonnet 4.6)       │
└───────────────────────────┘
              │ (MCP Calls via HTTPS)
              ▼
┌───────────────────────────┐
│ Public Secure Tunnel      │ (e.g., localtunnel, pinggy, ngrok)
└─────────────┬─────────────┘
              │ (Port forward to localhost:8000)
              ▼
┌───────────────────────────┐
│ Local MCP Server (Laptop) │ <─── Direct Read/Write/Exec on ~/IdeaProjects/vertex-ai-samples
└───────────────────────────┘
```

---

## 🛠️ Step 1: Deployment to Google Cloud

1. **Verify your active Google credentials**:
   Ensure you are logged in with `admin@jesusarguelles.altostrat.com` and have selected project `vtxdemos`:
   ```bash
   gcloud auth application-default login
   gcloud config set project vtxdemos
   ```

2. **Deploy the Agent to Vertex AI**:
   Run the deployment script from this directory:
   ```bash
   uv run deploy.py
   ```
   *Note the final `ReasoningEngine Resource Name` returned in the output.*

---

## 💻 Step 2: Running the Local Workspace Bridge

1. **Start the Local MCP Server**:
   ```bash
   uv run python local_mcp_server.py
   ```
   The server starts locally on port `8000` exposing tools (`list_directory`, `read_file`, `write_file`, `execute_command`).

2. **Start a Public Tunnel**:
   Because Vertex Agent Engine runs in the cloud, it cannot resolve `localhost`. Expose your port `8000` to the internet using your preferred tunneling tool:
   * **Pinggy (Built-in via SSH)**:
     ```bash
     ssh -R 80:localhost:8000 free@pinggy.io
     ```
   * **Localtunnel (NPM)**:
     ```bash
     npx localtunnel --port 8000
     ```
   Copy the generated public URL (e.g., `https://XXXX.localtunnel.me`). Ensure it includes `/sse` at the end when passed to the agent (e.g. `https://XXXX.localtunnel.me/sse`).

---

## 🔗 Step 3: Consuming the Agent via A2A

You can now call the deployed Claude agent from **any** other Antigravity session, script, or orchestrator using the ADK A2A client. 

To enable the agent to speak back to your local filesystem, pass your active public tunnel URL in the `MCP_URL` session state property.

```python
import asyncio
from google.adk.a2a.remote_a2a_agent import RemoteA2aAgent
from google.adk.a2a.clients.vertex_a2a_client import VertexA2aClientFactory
from google.adk.agents import InMemorySessionService, CallbackContext

# 1. Define the remote Claude agent
remote_claude_agent = RemoteA2aAgent(
    name="claude_sonnet_a2a_agent",
    description="Claude Sonnet 4.6 agent with local repository control.",
    agent_card="projects/vtxdemos/locations/us-central1/reasoningEngines/1959763478033989632",
    client_factory=VertexA2aClientFactory()
)

async def query_remote_agent():
    # 2. Setup standard session and input
    session_service = InMemorySessionService()
    session = await session_service.create_session()
    
    # 3. Supply the active tunnel URL in session state
    session.state["MCP_URL"] = "https://your-public-tunnel-url.localtunnel.me/sse"
    
    # 4. Invoke the agent
    response = await remote_claude_agent.query(
        input="List the root directory of the repository and tell me which files are in it.",
        session=session
    )
    print("Agent Response:\n", response)

if __name__ == "__main__":
    asyncio.run(query_remote_agent())
```
