#%%
import os
import sys
from google.adk.agents import Agent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai.types import Content, Part, GenerateContentConfig
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset, SseConnectionParams
from google.adk.agents.readonly_context import ReadonlyContext
from dotenv import load_dotenv

load_dotenv(verbose=True)

AGENTSPACE_AUTH_ID = "jira-auth-mcp_1764305083858"

def explicit_logger(msg):
    print(f"[MCP LOG] {msg}", file=sys.stdout)

def get_access_token(readonly_context: ReadonlyContext, auth_id: str) -> str | None:
    """Retrieves the OAuth access token from the Agentspace session state."""
    # print("Context")
    # print(readonly_context)
    if hasattr(readonly_context, "session") and hasattr(readonly_context.session, "state"):
        session_state = dict(readonly_context.session.state)
        # print("There's a session state:")
        # print(session_state)

        # Check keys for exact match or prefix match (e.g. "auth-id_12345")
        for key, value in session_state.items():
            # print(f"Key: {key}, Value: {value}  ")
            if key.startswith(auth_id) and isinstance(value, str) and len(value) > 20:
                return value
            else:
                print("Local keys sending over...")
                try:
                    local_access_token = os.getenv("ATLASSIAN_OAUTH_TOKEN")
                    return local_access_token
                except Exception as e:
                    print("Error: {e}")
                    return None

    return None

def mcp_header_provider(readonly_context: ReadonlyContext) -> dict[str, str]:
    # 1. Retrieve token
    token = get_access_token(readonly_context, AGENTSPACE_AUTH_ID)
    
    if not token:
        # Fallback to env for local testing if needed, but usually strictly from context
        token = os.getenv("ATLASSIAN_OAUTH_TOKEN")

    if not token:
        print("[CRITICAL] Token is missing!", file=sys.stdout)
        return {}

    # 2. CRITICAL: Strip whitespace.
    # Python reads env vars with potential newlines; Node.js usually trims them.
    clean_token = token.strip()

    # 3. DEBUG: Verify we have the "Working" Client ID (Start of token payload)
    # This helps verify you aren't using the "Failing" Confluence token by mistake
    print(f"[DEBUG] Using Token Prefix: {clean_token[:6]}... (Length: {len(clean_token)})", file=sys.stdout)

    return {
        "Authorization": f"Bearer {clean_token}",
        "Accept": "text/event-stream", # Required for SSE handshakes
        "Cache-Control": "no-cache"
    }

root_agent = Agent(
    name="root_agent",
    model="gemini-2.5-flash",
    description="You are a Jira assistant Agent.",
    instruction="""
        You are a Jira assistant Agent.
        1. Use JQL (e.g. text ~ "colors").
        2. Return key, summary, and status.
        """,
    generate_content_config=GenerateContentConfig(
        temperature=0.0,
    ),
    tools=[
        McpToolset(
            connection_params=SseConnectionParams(
                url='https://jira-mcp-server-254356041555.us-central1.run.app/sse',
                timeout=120
            ),
            header_provider=mcp_header_provider,
            errlog=explicit_logger
        )
    ],
)

APP_NAME = "sockcop1"
USER_ID = "sockcop1"
SESSION_ID = "jajajaplantas"

session_service = InMemorySessionService()

runner = Runner(
    agent=root_agent,
    app_name=APP_NAME,
    session_service=session_service
)

async def main():
    session = await session_service.get_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
    )
    if session is None:
        session = await session_service.create_session(
            app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
        )

    user_content = Content(
        role="user", parts=[Part(text="how many jira issues related to colors are there?, give me a summary and the issue number")]
    )

    final_response_content = "No response"
    async for event in runner.run_async(
            user_id=USER_ID, session_id=SESSION_ID, new_message=user_content
    ):
        if event.is_final_response() and event.content and event.content.parts:
            final_response_content = event.content.parts[0].text

    print(final_response_content)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())