# SecretOps — ADK + Secret Manager + ServiceNow MCP

> Semiautonomous IT operations agent that securely loads credentials from Google Secret Manager, connects to ServiceNow via MCP, and searches the web with Google Search grounding.

**Python 3.12** | **Google ADK** | **Secret Manager** | **FastMCP** | **ServiceNow**

![SecretOps Demo](assets/demo.gif)

## The Pattern

```
┌──────────────────────────────────────────────────────────────────────────┐
│  Google Cloud (vtxdemos)                                                 │
│                                                                          │
│  ┌──────────────┐    ┌──────────────────────────────────────────────┐    │
│  │ Secret       │    │ ADK LlmAgent (Gemini 2.5 Flash)             │    │
│  │ Manager      │    │                                              │    │
│  │              │    │  Tools:                                       │    │
│  │ servicenow-  │    │  ┌─────────────────┐  ┌──────────────────┐   │    │
│  │ credentials  │──► │  │ web_search()    │  │ MCP Tools (x6)   │   │    │
│  │              │    │  │ Google Search   │  │ list_incidents    │   │    │
│  └──────────────┘    │  │ Grounding       │  │ search_incidents  │   │    │
│                      │  │                 │  │ get_incident      │   │    │
│                      │  └────────┬────────┘  │ create_incident   │   │    │
│                      │           │           │ update_incident   │   │    │
│                      │           │           │ add_work_note     │   │    │
│                      │           │           └────────┬──────────┘   │    │
│                      └───────────┼────────────────────┼──────────────┘    │
│                                  │                    │                   │
│         ┌────────────────────────┘                    │                   │
│         ▼                                             ▼                   │
│  ┌──────────────┐                            ┌──────────────┐            │
│  │ Vertex AI    │                            │ ServiceNow   │            │
│  │ Gemini API   │                            │ MCP Server   │            │
│  │ + Google     │                            │ (FastMCP/SSE)│            │
│  │   Search     │                            │ port 9090    │            │
│  └──────────────┘                            └──────┬───────┘            │
│                                                     │                    │
└─────────────────────────────────────────────────────┼────────────────────┘
                                                      │
                                                      ▼
   ┌──────────────────┐                        ┌──────────────┐
   │ React Frontend   │◄──── SSE ────────────► │ ServiceNow   │
   │ (Vite + TS)      │     FastAPI :8001      │ Instance     │
   │ port 5185        │                        │ (REST API)   │
   └──────────────────┘                        └──────────────┘
```

## How It Works

1. **Startup** — `agent/agent.py` fetches ServiceNow credentials from Secret Manager and injects them as environment variables.
2. **MCP Server** — A FastMCP subprocess starts on port 9090, exposing 6 ServiceNow tools (list, search, get, create, update, add work note) via SSE transport.
3. **ADK Agent** — `LlmAgent` (Gemini 2.5 Flash) is configured with both MCP tools and a custom `web_search` tool.
4. **Web Search** — The `web_search` tool makes a separate Gemini API call with Google Search grounding, avoiding the Gemini limitation that prevents mixing grounding tools with function-calling tools in the same request.
5. **Streaming** — FastAPI streams SSE events to a React frontend with markdown rendering.

## Project Structure

```
adk-secret-snow-demo/
├── agent/
│   ├── __init__.py
│   └── agent.py              # ADK agent — Secret Manager + MCP + web_search
├── servicenow_mcp/
│   ├── __init__.py
│   └── server.py             # FastMCP server — 6 ServiceNow tools (SSE transport)
├── main.py                   # FastAPI server — SSE streaming to frontend
├── frontend/
│   ├── src/
│   │   ├── App.tsx            # Chat UI with markdown table rendering
│   │   ├── App.css            # Light modern theme
│   │   └── main.tsx
│   ├── package.json
│   └── vite.config.ts         # Dev server on port 5185
├── assets/
│   └── demo.gif
├── pyproject.toml
└── README.md
```

## Prerequisites

| Requirement | Details |
|---|---|
| Python | 3.10+ |
| Node.js | 18+ |
| `uv` | Python package manager ([install](https://docs.astral.sh/uv/)) |
| GCP Project | Vertex AI API + Secret Manager API enabled |
| ServiceNow | Developer instance ([free](https://developer.servicenow.com/)) |

## Setup

### 1. Google Cloud Authentication

```bash
gcloud auth application-default login
```

### 2. Create the ServiceNow Secret

Store your ServiceNow credentials in Secret Manager. The agent expects a JSON secret with three fields:

```bash
# Create the secret
echo '{"instance_url":"https://YOUR_INSTANCE.service-now.com","username":"admin","password":"YOUR_PASSWORD"}' \
  | gcloud secrets create servicenow-credentials \
      --project=YOUR_PROJECT_ID \
      --data-file=- \
      --replication-policy=automatic

# Verify it works
gcloud secrets versions access latest \
  --secret=servicenow-credentials \
  --project=YOUR_PROJECT_ID
```

The secret JSON schema:

```json
{
  "instance_url": "https://devNNNNNN.service-now.com",
  "username": "admin",
  "password": "..."
}
```

### 3. Environment Variables

No `.env` file is needed — the agent reads everything from defaults and Secret Manager. Override if needed:

| Variable | Default | Purpose |
|---|---|---|
| `GOOGLE_CLOUD_PROJECT` | `vtxdemos` | GCP project with Secret Manager + Vertex AI |
| `GOOGLE_CLOUD_LOCATION` | `us-central1` | Required for Google Search grounding |
| `SERVICENOW_SECRET_ID` | `servicenow-credentials` | Secret Manager secret name |
| `MCP_PORT` | `9090` | Port for the MCP server subprocess |

### 4. Install Dependencies

```bash
# Backend
cd semiautonomous-agents/adk-secret-snow-demo
uv sync

# Frontend
cd frontend
npm install
```

## Running

```bash
# Terminal 1 — Backend (starts MCP server automatically)
uv run python main.py

# Terminal 2 — Frontend
cd frontend
npm run dev
```

Open http://localhost:5185 in your browser.

## MCP Server Configuration

The ServiceNow MCP server (`servicenow_mcp/server.py`) is a FastMCP server that exposes 6 tools via SSE transport:

| Tool | Description |
|---|---|
| `list_incidents` | List incidents with optional state filter |
| `search_incidents` | Full-text search by description |
| `get_incident` | Get details for a specific incident number |
| `create_incident` | Create a new incident (short_description, description, priority) |
| `update_incident` | Update fields on an existing incident |
| `add_work_note` | Add a work note to an incident |

The MCP server reads credentials from environment variables (injected by the agent via Secret Manager):

```
SERVICENOW_INSTANCE_URL  — Full instance URL
SERVICENOW_BASIC_AUTH_USER — Username
SERVICENOW_BASIC_AUTH_PASS — Password
```

Connection from the ADK agent:

```python
McpToolset(
    connection_params=SseConnectionParams(url="http://localhost:9090/sse")
)
```

## Google Search Workaround

Gemini's API does not allow mixing `google_search` (grounding tool) with function-calling tools in the same request. The workaround is a custom `web_search` function tool that makes a **separate** Gemini API call with grounding enabled:

```python
async def web_search(query: str) -> str:
    client = genai.Client(vertexai=True, project=PROJECT_ID, location="us-central1")
    response = await client.aio.models.generate_content(
        model=MODEL,
        contents=query,
        config=genai_types.GenerateContentConfig(
            tools=[genai_types.Tool(google_search=genai_types.GoogleSearch())],
        ),
    )
    return response.text
```

This lets the agent use web search alongside MCP tools in the same conversation — search the web, then create a ServiceNow incident with the findings.

## Security Model

| Principle | Implementation |
|---|---|
| Zero-leak credentials | ServiceNow creds stored in Secret Manager, never in code or config files |
| Just-in-time access | Credentials loaded at startup, injected as env vars to subprocess |
| Application Default Credentials | Backend authenticates to Vertex AI and Secret Manager via ADC |
| Tool isolation | Agent accesses ServiceNow only through MCP tools, not direct API calls |

## Troubleshooting

| Issue | Solution |
|---|---|
| `Secret Manager unavailable` | Run `gcloud auth application-default login` and verify project access |
| `MCP server connection refused` | Check port 9090 is free, or set `MCP_PORT` to another port |
| `Multiple tools are supported only when they are all search tools` | Ensure `web_search` is a function tool (not `google_search` grounding) — see agent.py |
| `CORS error in browser` | Backend allows `http://localhost:5185` — check `main.py` CORS config |
| Tables render as raw text | Ensure `remark-gfm` is installed: `cd frontend && npm install remark-gfm` |

---

<div align="center">

```
     _/\_
    ( o.o )
     > ^ <
    /|   |\
   (_|   |_)
```

**Made with** :pray: **by Jesus**

*"Let there be incidents... and they were resolved."*

</div>

## Author

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Jesus%20Chavez-0A66C2?logo=linkedin)](https://www.linkedin.com/in/jchavezar)
