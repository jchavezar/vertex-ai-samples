# LazyMcpToolset Pattern

> **Solving Agent Engine Pickle Serialization Issues**

This document explains the LazyMcpToolset pattern - a critical solution for deploying ADK agents with MCP toolsets to Google Cloud Agent Engine.

## The Problem

When deploying an ADK agent to Agent Engine, the agent object is serialized using `cloudpickle`. The `McpToolset` object contains:

- `MCPSessionManager` with async callbacks
- SSE connection state
- Internal thread pools
- Non-serializable socket references

**Result:** Container crashes on startup with errors like:
```
'MCPSessionManager' object has no attribute '_sampling_callback'
TypeError: cannot pickle 'SSLContext' object
```

```
┌─────────────────────────────────────────────────────────────────┐
│                    DEPLOYMENT FAILURE                           │
│                                                                 │
│   agent.py                                                      │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │  toolset = McpToolset(                                  │   │
│   │      connection_params=SseConnectionParams(url=...),    │   │
│   │      header_provider=my_header_provider,                │   │
│   │  )                                                      │   │
│   │                                                         │   │
│   │  agent = LlmAgent(tools=[toolset])  # ❌ FAILS          │   │
│   └─────────────────────────────────────────────────────────┘   │
│                           │                                     │
│                           ▼                                     │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │  cloudpickle.dumps(agent)                               │   │
│   │  └─▶ Tries to serialize McpToolset                      │   │
│   │  └─▶ MCPSessionManager has async callbacks              │   │
│   │  └─▶ SSE connection has SSL context                     │   │
│   │  └─▶ ❌ CRASH: Cannot pickle                            │   │
│   └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## The Solution: LazyMcpToolset

Wrap the `McpToolset` in a lazy wrapper that defers creation until runtime:

```
┌─────────────────────────────────────────────────────────────────┐
│                    DEPLOYMENT SUCCESS                           │
│                                                                 │
│   agent.py                                                      │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │  toolset = LazyMcpToolset(                              │   │
│   │      url="https://mcp-server.run.app/sse",              │   │
│   │      header_provider=my_header_provider,                │   │
│   │  )                                                      │   │
│   │                                                         │   │
│   │  agent = LlmAgent(tools=[toolset])  # ✅ WORKS          │   │
│   └─────────────────────────────────────────────────────────┘   │
│                           │                                     │
│                           ▼                                     │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │  cloudpickle.dumps(agent)                               │   │
│   │  └─▶ LazyMcpToolset.__getstate__() called               │   │
│   │  └─▶ Returns: {url, header_provider, _toolset: None}    │   │
│   │  └─▶ ✅ Serializes successfully (no McpToolset yet)     │   │
│   └─────────────────────────────────────────────────────────┘   │
│                           │                                     │
│                           ▼                                     │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │  AT RUNTIME (when tool is called):                      │   │
│   │  └─▶ LazyMcpToolset.get_tools() called                  │   │
│   │  └─▶ _get_toolset() creates McpToolset lazily           │   │
│   │  └─▶ ✅ MCP connection established                      │   │
│   └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## Implementation

> **Source:** [`agent/agent.py#L105-L200`](../agent/agent.py#L105-L200)

### Complete Code

```python
from google.adk.agents import LlmAgent
from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset, SseConnectionParams
from google.adk.tools.base_toolset import BaseToolset
import logging

logger = logging.getLogger(__name__)


# ============= Header Provider =============
def mcp_header_provider(readonly_context: ReadonlyContext) -> dict[str, str]:
    """
    Provide headers for MCP server connection.
    - Authorization: Cloud Run ID token (service-to-service auth)
    - X-User-Token: User's JWT (for user identity)
    """
    headers = {}

    # Get Cloud Run ID token at runtime for service auth
    MCP_BASE_URL = "https://servicenow-mcp-xxx.us-central1.run.app"
    try:
        import google.auth.transport.requests
        from google.oauth2 import id_token
        request = google.auth.transport.requests.Request()
        cloud_run_token = id_token.fetch_id_token(request, MCP_BASE_URL)
        headers["Authorization"] = f"Bearer {cloud_run_token}"
        logger.info("[MCP] Got Cloud Run ID token")
    except Exception as e:
        logger.warning(f"[MCP] Cloud Run token error: {e}")

    # Pass user JWT via X-User-Token header
    if hasattr(readonly_context, "session") and hasattr(readonly_context.session, "state"):
        session_state = dict(readonly_context.session.state)
        user_token = session_state.get("USER_TOKEN")
        if user_token and user_token.startswith("eyJ"):
            headers["X-User-Token"] = user_token
            logger.info(f"[MCP] Added X-User-Token (length: {len(user_token)})")

    return headers


# ============= Lazy MCP Toolset =============
class LazyMcpToolset(BaseToolset):
    """
    Lazy wrapper for McpToolset that creates the toolset at runtime.
    This avoids pickle serialization issues during Agent Engine deployment.

    Key insight: cloudpickle serializes the agent at deployment time, but
    McpToolset contains non-serializable objects (SSE connections, async
    callbacks). By deferring McpToolset creation to runtime, we avoid this.
    """

    def __init__(self, url: str, header_provider):
        super().__init__()  # REQUIRED: Must call BaseToolset.__init__
        self._url = url
        self._header_provider = header_provider
        self._toolset = None  # Created lazily at runtime

    def _get_toolset(self):
        """Create McpToolset on first access (at runtime, not deployment)."""
        if self._toolset is None:
            logger.info(f"[LazyMCP] Creating McpToolset for {self._url}")
            self._toolset = McpToolset(
                connection_params=SseConnectionParams(url=self._url, timeout=120),
                header_provider=self._header_provider,
                errlog=lambda msg: logger.info(f"[MCP] {msg}"),
            )
        return self._toolset

    async def get_tools(self, readonly_context=None):
        """ADK calls this to get available tools."""
        return await self._get_toolset().get_tools(readonly_context)

    def __getstate__(self):
        """
        Control what gets pickled during deployment.
        We pickle ONLY the URL and header_provider, NOT the toolset.
        """
        return {
            "_url": self._url,
            "_header_provider": self._header_provider,
            "_toolset": None  # Explicitly None - will be created at runtime
        }

    def __setstate__(self, state):
        """Restore from pickled state."""
        self.__init__(state["_url"], state["_header_provider"])


# ============= Usage =============
MCP_URL = "https://servicenow-mcp-xxx.us-central1.run.app/sse"

toolset = LazyMcpToolset(
    url=MCP_URL,
    header_provider=mcp_header_provider,
)

agent = LlmAgent(
    name="MyAgent",
    model="gemini-2.5-flash",
    instruction="Your instruction here...",
    tools=[toolset],  # Now serializable!
)
```

## Key Requirements

### 1. Inherit from BaseToolset

```python
class LazyMcpToolset(BaseToolset):  # ✅ Required
    def __init__(self, url: str, header_provider):
        super().__init__()  # ✅ Must call parent
```

If you don't inherit from `BaseToolset`, ADK validation will fail:
```
ValidationError: tools[0] must be a Tool, Toolset, or callable
```

### 2. Implement `__getstate__` and `__setstate__`

```python
def __getstate__(self):
    # Return ONLY serializable data
    return {
        "_url": self._url,
        "_header_provider": self._header_provider,
        "_toolset": None  # NOT the actual toolset
    }

def __setstate__(self, state):
    # Reconstruct from serialized data
    self.__init__(state["_url"], state["_header_provider"])
```

### 3. Access Session State Correctly

```python
# ✅ Correct: Access via session.state
if hasattr(readonly_context, "session") and hasattr(readonly_context.session, "state"):
    session_state = dict(readonly_context.session.state)
    user_token = session_state.get("USER_TOKEN")

# ❌ Wrong: Direct state access may not work
user_token = readonly_context.state.get("USER_TOKEN")  # May return None
```

## Sequence Diagram

```
┌─────────┐     ┌─────────────┐     ┌───────────────┐     ┌──────────────┐
│ Deploy  │     │ CloudPickle │     │ Agent Engine  │     │ MCP Server   │
│ Script  │     │             │     │ Runtime       │     │              │
└────┬────┘     └──────┬──────┘     └───────┬───────┘     └──────┬───────┘
     │                 │                    │                    │
     │  deploy.py      │                    │                    │
     │─────────────────▶                    │                    │
     │                 │                    │                    │
     │  pickle(agent)  │                    │                    │
     │─────────────────▶                    │                    │
     │                 │                    │                    │
     │         LazyMcpToolset.__getstate__()                     │
     │                 │──────────┐         │                    │
     │                 │          │         │                    │
     │                 │◀─────────┘         │                    │
     │                 │  {url, header_provider, toolset: None}  │
     │                 │                    │                    │
     │  ✅ Serialized  │                    │                    │
     │◀────────────────│                    │                    │
     │                 │                    │                    │
     │                 │   Upload to GCS    │                    │
     │                 │───────────────────▶│                    │
     │                 │                    │                    │
     │                 │                    │                    │
     │                 │    USER QUERY      │                    │
     │                 │                    │◀───────────────────│
     │                 │                    │  "list incidents"  │
     │                 │                    │                    │
     │                 │         get_tools()│                    │
     │                 │                    │──────────┐         │
     │                 │                    │          │         │
     │                 │                    │  _get_toolset()    │
     │                 │                    │  Creates McpToolset│
     │                 │                    │◀─────────┘         │
     │                 │                    │                    │
     │                 │                    │    SSE Connect     │
     │                 │                    │───────────────────▶│
     │                 │                    │                    │
     │                 │                    │    Tool Call       │
     │                 │                    │───────────────────▶│
     │                 │                    │                    │
     │                 │                    │    Response        │
     │                 │                    │◀───────────────────│
     │                 │                    │                    │
```

## Common Errors and Solutions

### Error: `ValidationError: tools[0] must be a Tool, Toolset, or callable`

**Cause:** LazyMcpToolset doesn't inherit from BaseToolset

**Fix:**
```python
class LazyMcpToolset(BaseToolset):  # Add BaseToolset
    def __init__(self, url, header_provider):
        super().__init__()  # Call parent
```

### Error: `'MCPSessionManager' object has no attribute '_sampling_callback'`

**Cause:** Using McpToolset directly instead of LazyMcpToolset

**Fix:** Use the lazy pattern as shown above

### Error: `USER_TOKEN not found in state`

**Cause:** Accessing state incorrectly

**Fix:**
```python
# Use session.state, not direct state access
session_state = dict(readonly_context.session.state)
user_token = session_state.get("USER_TOKEN")
```

## Testing

### Local Testing (Works with direct McpToolset)

```bash
cd agent
uv run python test_local.py "list my incidents"
```

### Deployment Testing

```bash
# Deploy
uv run python deploy.py

# Test via curl
curl -X POST "https://us-central1-aiplatform.googleapis.com/v1/.../reasoningEngines/{id}:streamQuery" \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  -d '{"input": {"session_id": "...", "message": "list my incidents"}}'
```

## Summary

| Aspect | McpToolset (Direct) | LazyMcpToolset |
|--------|---------------------|----------------|
| Local Testing | ✅ Works | ✅ Works |
| Agent Engine Deployment | ❌ Fails (pickle) | ✅ Works |
| When Created | Import time | Runtime (first use) |
| Serializable | ❌ No | ✅ Yes |
| header_provider | ✅ Supported | ✅ Supported |

The LazyMcpToolset pattern is essential for any ADK agent using MCP that will be deployed to Agent Engine.
