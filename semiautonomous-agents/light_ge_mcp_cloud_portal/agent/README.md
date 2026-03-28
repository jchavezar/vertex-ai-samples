# Agent Engine

[← Back to Main README](../README.md)

ADK agent deployed to Vertex AI Agent Engine with MCP toolset for ServiceNow integration.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     AGENT ENGINE                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │  LlmAgent   │─▶│   Gemini    │─▶│   McpToolset            │  │
│  │  (ADK)      │  │  2.5 Flash  │  │   (SSE + header_provider)│  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Files

| File | Purpose |
|------|---------|
| [`agent.py`](agent.py) | Agent definition with MCP toolset |
| [`deploy.py`](deploy.py) | Deployment script for Agent Engine |
| [`requirements.txt`](requirements.txt) | Python dependencies |

## Configuration

Create `.env` file:

```bash
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1
STAGING_BUCKET=gs://your-project-staging
SERVICENOW_MCP_URL=https://servicenow-mcp-xxx.us-central1.run.app/sse
```

## Key Components

### Agent Definition ([`agent.py`](agent.py))

```python
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset, SseConnectionParams

root_agent = LlmAgent(
    name="ServiceNowAgentCloud",
    model="gemini-2.5-flash",
    instruction=INSTRUCTIONS,
    tools=[
        McpToolset(
            connection_params=SseConnectionParams(
                url=MCP_URL,
                timeout=120,
            ),
            header_provider=mcp_header_provider,  # Dynamic headers
            errlog=explicit_logger,
        )
    ]
)
```

### Header Provider ([`agent.py`](agent.py) lines 36-62)

The `header_provider` callback adds authentication headers to MCP requests:

```python
def mcp_header_provider(readonly_context: ReadonlyContext) -> dict[str, str]:
    headers = {}

    # 1. Cloud Run ID token (service-to-service auth)
    cloud_run_token = id_token.fetch_id_token(request, MCP_BASE_URL)
    headers["Authorization"] = f"Bearer {cloud_run_token}"

    # 2. User JWT from session state (for ServiceNow)
    user_token = get_user_token(readonly_context)
    if user_token:
        headers["X-User-Token"] = user_token

    return headers
```

### Session State Access

```python
def get_user_token(readonly_context: ReadonlyContext) -> str | None:
    """Extract USER_TOKEN from session state."""
    if hasattr(readonly_context, "session"):
        session_state = dict(readonly_context.session.state)
        token = session_state.get("USER_TOKEN")
        if token and token.startswith("eyJ"):
            return token
    return None
```

## Deployment

```bash
# Install dependencies
uv sync

# Deploy to Agent Engine
uv run python deploy.py
```

### Deploy Script ([`deploy.py`](deploy.py))

The script:
1. Wraps the agent in `AdkApp`
2. Checks for existing engine (update) or creates new
3. Configures environment variables and service account

```python
deployment_app = AdkApp(
    agent=agent.root_agent,
    enable_tracing=True,
)

config = {
    "display_name": AGENT_ENGINE_NAME,
    "staging_bucket": STAGING_BUCKET,
    "requirements": "requirements.txt",
    "extra_packages": ["agent.py"],
    "env_vars": {"SERVICENOW_MCP_URL": MCP_URL},
    "service_account": SERVICE_ACCOUNT,
}
```

## IAM Requirements

The compute service account needs:

```bash
# Session management
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
  --role="roles/aiplatform.admin"

# Gemini API access
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
  --role="roles/aiplatform.user"
```

## Testing

```python
import asyncio
import vertexai

vertexai.init(project="your-project", location="us-central1")
client = vertexai.Client()

agent = client.agent_engines.get(name="projects/.../reasoningEngines/ID")

# Create session
session = await agent.async_create_session(
    user_id="test",
    state={"USER_TOKEN": "eyJ..."}
)

# Query
async for event in agent.async_stream_query(
    session_id=session["id"],
    user_id="test",
    message="list incidents"
):
    print(event)
```

## Related Documentation

- [MCP Server](../mcp-server/README.md) - Tool implementations
- [Security Flow](../docs/security-flow.md) - Token flow
- [GCP Setup](../docs/gcp-setup.md) - IAM configuration
