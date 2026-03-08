import os
import sys
from datetime import datetime
from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseConnectionParams
from google.adk.agents.readonly_context import ReadonlyContext
from google.genai.types import GenerateContentConfig

# --- TOKEN HANDLING ---

def get_access_token(readonly_context: ReadonlyContext) -> str | None:
    if hasattr(readonly_context, "session") and hasattr(readonly_context.session, "state"):
        session_state = dict(readonly_context.session.state)
        if "token" in session_state:
            return session_state["token"]
        if "access_token" in session_state:
            return session_state["access_token"]
        for key, value in session_state.items():
            if isinstance(value, str) and value.startswith("eyJ") and len(value) > 100:
                return value
    return os.getenv("FACTSET_OAUTH_TOKEN")

def mcp_header_provider(readonly_context: ReadonlyContext) -> dict[str, str]:
    token = get_access_token(readonly_context)
    if not token:
        return {}
    return {
        "Authorization": f"Bearer {token.strip()}",
        "x-custom-auth": token.strip(),
        "Accept": "text/event-stream",
        "Cache-Control": "no-cache"
    }

# --- AGENT DEFINITION ---

current_date = datetime.now().strftime("%Y-%m-%d")
PROXY_SERVER_URL = os.getenv("FACTSET_PROXY_URL", "http://localhost:8080/sse")

root_agent = Agent(
    name="factset_root_agent",
    model="gemini-2.5-flash",
    description="FactSet Intelligence Agent.",
    instruction=f"You are the FactSet Smart Terminal Agent. Today's date is {current_date}.",
    generate_content_config=GenerateContentConfig(temperature=0.0),
    tools=[], # Temporarily empty
)

# --- PATCHES (APPLY ONLY ON LOAD) ---
def apply_patches():
    import httpx
    from contextlib import asynccontextmanager
    import mcp.client.sse
    from mcp.client.streamable_http import streamablehttp_client
    import nest_asyncio

    try:
        nest_asyncio.apply()
    except:
        pass

    def custom_http_client_factory(headers=None, auth=None, timeout=None, http2=True):
        return httpx.AsyncClient(headers=headers, auth=auth, timeout=timeout, http2=http2, follow_redirects=True)

    @asynccontextmanager
    async def patched_streamable_client(url, headers=None, timeout=300.0, sse_read_timeout=3600.0, httpx_client_factory=None, auth=None):
        async with streamablehttp_client(
            url=url, headers=headers, timeout=timeout, sse_read_timeout=sse_read_timeout,
            httpx_client_factory=custom_http_client_factory, auth=auth, terminate_on_close=True
        ) as (read_stream, write_stream, get_session_id):
            yield read_stream, write_stream

    mcp.client.sse.sse_client = patched_streamable_client

apply_patches()
