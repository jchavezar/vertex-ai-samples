import os
import sys
import asyncio
from google.adk.agents import Agent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai.types import Content, Part, GenerateContentConfig
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset, SseConnectionParams
from google.adk.agents.readonly_context import ReadonlyContext
from dotenv import load_dotenv

load_dotenv(verbose=True)

def explicit_logger(msg):
    print(f"[MCP LOG] {msg}", file=sys.stdout)

def get_access_token(readonly_context: ReadonlyContext) -> str | None:
    """Dynamically retrieves the OAuth access token by scanning the session state."""
    if hasattr(readonly_context, "session") and hasattr(readonly_context.session, "state"):
        session_state = dict(readonly_context.session.state)
        for key, value in session_state.items():
            if isinstance(value, str) and value.startswith("eyJ") and len(value) > 100:
                return value
            if isinstance(value, dict) and "access_token" in value:
                token = value["access_token"]
                if isinstance(token, str) and token.startswith("eyJ"):
                    return token
    return os.getenv("ATLASSIAN_OAUTH_TOKEN")

def mcp_header_provider(readonly_context: ReadonlyContext) -> dict[str, str]:
    token = get_access_token(readonly_context)
    if not token:
        print("[CRITICAL] No Jira/Atlassian token found!", file=sys.stdout)
        return {}
    return {
        "Authorization": f"Bearer {token.strip()}",
        "Accept": "text/event-stream",
        "Cache-Control": "no-cache"
    }

root_agent = Agent(
    name="root_agent",
    model="gemini-2.5-flash",
    description="You are a Jira assistant Agent.",
    instruction="""You are a helpful and proactive Jira Knowledge Assistant.

**Workflow Logic (Strict Rules):**

1.  **Context Discovery**: If the user asks for issues, projects, or any data but hasn't specified a Project Key, you **MUST** first call `getVisibleJiraProjects`.
    
2.  **Handling Project Results**:
    *   **IF ONLY ONE project is returned**: Do **NOT** ask the user for confirmation. Immediately proceed to satisfy the original request using that project key.
    *   **IF MULTIPLE projects are returned**: List the names and keys of the projects and ask the user which one they would like to use.
    *   **IF NO projects are returned**: Inform the user you don't have access to any Jira projects.

3.  **JQL Searching**: 
    *   When searching for keywords (e.g., "ducati"), use the `searchJiraIssuesUsingJql` tool.
    *   Construct the JQL like this: `project = "PROJECT_KEY" AND text ~ "keyword"`.
    *   Default to `maxResults: 5` unless the user specifies a different number.

4.  **Pagination**: 
    *   If the tool output contains a `nextPageToken`, you **MUST** ask the user: "There are more issues available. Would you like to see the next batch?"

5.  **Formatting**: 
    *   Use Markdown bullet points for lists: `* [KEY-123] Summary (Status: Done)`.
    *   Synthesize information from issue descriptions or comments if the user asks a "Why" or "How" question.
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
                if event.is_final_response() and event.content and event.content.parts:
                    final_text = event.content.parts[0].text

            print(final_text)
            print("-" * 20)

        except Exception as e:
            print(f"\nError during execution: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nUser interrupted. Exiting.")