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
    if hasattr(readonly_context, "session") and hasattr(readonly_context.session, "state"):
        session_state = dict(readonly_context.session.state)
        for key, value in session_state.items():
            if key.startswith(auth_id) and isinstance(value, str) and len(value) > 20:
                return value
    # Fallback for local testing
    return os.getenv("ATLASSIAN_OAUTH_TOKEN")

def mcp_header_provider(readonly_context: ReadonlyContext) -> dict[str, str]:
    token = get_access_token(readonly_context, AGENTSPACE_AUTH_ID)
    if not token:
        print("[CRITICAL] Token is missing!", file=sys.stdout)
        return {}
    clean_token = token.strip()
    print(f"[DEBUG] Using Token Prefix: {clean_token[:6]}... (Length: {len(clean_token)})", file=sys.stdout)
    return {
        "Authorization": f"Bearer {clean_token}",
        "Accept": "text/event-stream",
        "Cache-Control": "no-cache"
    }

root_agent = Agent(
    name="root_agent",
    model="gemini-2.5-flash",
    description="You are a Jira assistant Agent.",
    instruction="""You are a helpful, friendly, and communicative Jira assistant. Your goal is to guide the user clearly through their data, explaining your steps.

**Core Guidelines:**

1.  **Friendly Project Check**: When the user asks for "all issues", DO NOT just list them immediately.
    *   First, call `getVisibleJiraProjects`.
    *   **If you find one project**: Tell the user, "I found one project named '[Project Name]'. I'll search for issues there." THEN perform the search.
    *   **If you find multiple**: List them and ask, "I found multiple projects: [List]. Which one would you like to view?"
    *   **Why?**: The user wants to know what you are doing. Be verbose and helpful.

2.  **Format with Markdown**:
    *   Always present lists of issues using Markdown bullet points for readability.
    *   Example:
        * `[KEY-1] Summary of the issue (Status: To Do)`
        * `[KEY-2] Another issue (Status: Done)`

3.  **Interactive Pagination**:
    *   The search tool returns 15 results at a time.
    *   **CRITICAL**: Check the tool output for the text `[SYSTEM NOTICE: There are more issues available...]`.
    *   **If you see this notice**, you **MUST** end your response with a clear, friendly question on its own line:
        "**That was the first 15. Would you like to see the next batch?**"
    *   If you do *not* see the notice, assume you have listed all issues.

4.  **Tone**: Be conversational. If you are searching, say "Searching now...". If you found nothing, say "I couldn't find any issues matching that." Don't be a robot; be a helpful assistant.
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
    print("Initializing session...")
    session = await session_service.get_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
    )
    if session is None:
        session = await session_service.create_session(
            app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
        )
    print(f"Session initialized (ID: {SESSION_ID}). Ready to chat!")
    print("Type 'exit' or 'quit' to end the conversation.\n")

    while True:
        try:
            user_text = input("User: ")
        except EOFError:
            break

        if user_text.lower() in ("exit", "quit"):
            print("Exiting...")
            break

        if not user_text.strip():
            continue

        user_content = Content(
            role="user", parts=[Part(text=user_text)]
        )

        print("Agent: ", end="", flush=True)
        final_text = ""
        try:
            async for event in runner.run_async(
                    user_id=USER_ID, session_id=SESSION_ID, new_message=user_content
            ):
                # Attempt to stream the response if parts are available immediately
                # Note: The ADK runner behavior depends on the specific event types.
                # Here we capture the final response to ensure we get the complete message.
                if event.is_final_response() and event.content and event.content.parts:
                     # Clear the "Agent: " prompt if we want to print the whole block, 
                     # or just print the text. The previous code printed only final.
                     # Let's print the final text.
                     final_text = event.content.parts[0].text
            
            print(final_text)
            print("-" * 20)
            
        except Exception as e:
            print(f"\nError during execution: {e}")

if __name__ == "__main__":
    import asyncio
    # Ensure Windows compatibility for asyncio loop if needed, though we are on Darwin
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nUser interrupted. Exiting.")