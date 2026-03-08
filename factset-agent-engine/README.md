# FactSet Agent Engine with Gemini Enterprise

This project provides a root agent for Vertex AI Agent Engine that connects to FactSet via a Proxy MCP Server.

## Architecture

1.  **FactSet Proxy Server (Cloud Run)**:
    *   Acts as a standard MCP server for the ADK agent.
    *   Internally connects to the official FactSet MCP server using HTTP/2 and Streamable SSE.
    *   Extracts the user's OAuth token from the `Authorization: Bearer <token>` header and uses it to authenticate with FactSet.
    *   Enriches tool schemas using `factset_tools_schema.json`.

2.  **ADK Agent (Agent Engine)**:
    *   Extracts the OAuth token from Gemini Enterprise's session state (`readonly_context.session.state`).
    *   Uses `MCPToolset` with a custom `header_provider` to send this token to the Proxy Server.

## Deployment

### 1. Deploy the Proxy Server

Build and deploy the `factset_server` folder to Google Cloud Run.
Make sure to enable unauthenticated invocations (or manage IAM if preferred).

### 2. Deploy the Agent

1. Update `adk_agent/agent.py` with the `FACTSET_PROXY_URL`.
2. Run `python adk_agent/deploy.py`.

## Token Handling Logic

The agent extracts the token from the session state:
```python
def get_access_token(readonly_context: ReadonlyContext):
    # Searches for 'eyJ...' string in session state
    ...
```
This token is then passed to the Proxy Server:
```python
def mcp_header_provider(readonly_context: ReadonlyContext):
    token = get_access_token(readonly_context)
    return {"Authorization": f"Bearer {token}"}
```
