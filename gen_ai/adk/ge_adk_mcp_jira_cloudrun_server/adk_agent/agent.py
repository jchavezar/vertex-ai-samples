import os
import sys
import asyncio
from datetime import datetime
from google.adk.agents import Agent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai.types import Content, Part, GenerateContentConfig
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseConnectionParams
from google.adk.agents.readonly_context import ReadonlyContext
from dotenv import load_dotenv

load_dotenv(verbose=True)
current_date = datetime.now().strftime("%Y-%m-%d")

def explicit_logger(msg):
    print(f"[MCP LOG] {msg}", file=sys.stdout)

def get_access_token(readonly_context: ReadonlyContext) -> str | None:
    if hasattr(readonly_context, "session") and hasattr(readonly_context.session, "state"):
        session_state = dict(readonly_context.session.state)
        print(f"[DEBUG] Session State Keys: {list(session_state.keys())}", file=sys.stdout)
        
        for key, value in session_state.items():
            # Direct string token check
            if isinstance(value, str) and value.startswith("eyJ") and len(value) > 100:
                print(f"[DEBUG] Found direct token in key: {key}", file=sys.stdout)
                return value
            
            # Nested dictionary check (e.g. 'authorizations' -> 'access_token')
            if isinstance(value, dict):
                if "access_token" in value:
                    token = value["access_token"]
                    if isinstance(token, str) and token.startswith("eyJ"):
                        print(f"[DEBUG] Found nested token in key: {key}", file=sys.stdout)
                        return token
                else:
                    # Deep inspection for debugging
                    print(f"[DEBUG] Inspecting dict key '{key}': {list(value.keys())}", file=sys.stdout)

    print("[DEBUG] No token found in session state. Falling back to env var.", file=sys.stdout)
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
    description="You are a Jira assistant Agent capable of deep data analysis.",
    instruction=f"""You are a helpful and proactive Jira Knowledge Assistant. 
Today's date is {current_date}.

**CORE LOGIC - Tool Selection & Analysis:**
1. **Detailed Reports (Root Cause, Duration, etc.)**: 
   - Use `getJiraIssuesReport` for retrieving large lists of issues. 
   - **Pagination**: ALWAYS set `maxResults: 2000`. Check the tool output for `METADATA: NextToken=...`. If a token exists (and is not 'NONE'), you MUST call `getJiraIssuesReport` again with `nextPageToken` set to that value to get the next batch. Repeat until `NextToken=NONE`.
   - **Analysis**: When analyzing the output, DO NOT describe the process (e.g., "I gathered data..."). Instead, synthesize the CONTENT (e.g., "The primary root causes were...").

2. **High-Level Stats ONLY**:
   - Use `summarizeJiraIssues` ONLY if the user asks for simple counts (e.g., "How many bugs?", "Status distribution?") and DOES NOT need details like descriptions or root causes.

**Data Interpretation:**
- **Root Cause**: Extract insights from the `Desc` field. The tool now returns extracted text from ADF.
- **Duration**: Calculate `ResolutionDate - Created`. Both are provided as ISO timestamps (YYYY-MM-DDTHH:MM:SS).

**Formatting Rules:**
- **Sequential Numbering**: When listing multiple issues, ALWAYS start with a sequential number (e.g., 1., 2., 3...). 
- **Tables**: Use Markdown tables if appropriate: | # | Key | Summary | Duration | Root Cause |
- **Lists**: If using a list, format as: `1. [KEY](URL) - Summary (Duration)`
- Do NOT output huge markdown tables for hundreds of issues (chunk them if needed).
- If specific issues are interesting, highlight them.

**JQL Rules & Universal Date Handling:**
- Always use `maxResults: 50`.
- Always order by `created DESC` unless asked otherwise.

**Date & Time Logic (JQL):**
You must translate natural language timeframes into precise JQL functions or literals.
- **"This Week"**: `created >= startOfWeek()` (or `resolutiondate` if asking about completions).
- **"Last Week"**: `created >= startOfWeek("-1w") AND created <= endOfWeek("-1w")`.
- **"This Month"**: `created >= startOfMonth()`.
- **"Last Month"**: `created >= startOfMonth("-1M") AND created <= endOfMonth("-1M")`.
- **"This Year"**: `created >= startOfYear()`.
- **"Recently" / "Recent"**: Default to `created >= -30d` unless context implies otherwise.
- **"In the last X days/hours"**: `created >= -Xd` or `created >= -Xh`.
- **"Since [Date]"**: Convert [Date] to "YYYY-MM-DD". e.g., `created >= "2023-10-01"`.
- **"Before [Date]"**: `created < "YYYY-MM-DD"`.
- **"Older than X"**: `created <= -30d` (for > 30 days old).
- **"Completed/Resolved..."**: Apply the date logic to `resolutiondate` or `status changed to Done`.
    - E.g., "Completed this month": `status = Done AND resolutiondate >= startOfMonth()`.

**General Logic:**
- If the user specifies a point in time (e.g., "October 2023"), calculate the range: `created >= "2023-10-01" AND created <= "2023-10-31"`.
- Use `startOfDay()`, `endOfDay()` for "today" or "yesterday" logic.
""",
    generate_content_config=GenerateContentConfig(temperature=0.0),
    tools=[
        MCPToolset(
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
runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=session_service)

async def main():
    print(f"Agent Initialized (Today: {current_date}).")
    session = await session_service.get_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
    if session is None:
        await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)

    while True:
        try:
            user_text = input("User: ")
        except EOFError: break
        if user_text.lower() in ("exit", "quit"): break
        if not user_text.strip(): continue

        user_content = Content(role="user", parts=[Part(text=user_text)])
        print("Agent thinking...", end="\r", flush=True)
        try:
            async for event in runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=user_content):
                if event.is_final_response() and event.content and event.content.parts:
                    print("\n" + event.content.parts[0].text)
            print("\n" + "-" * 20)
        except Exception as e:
            print(f"\nError: {e}")

if __name__ == "__main__":
    try: asyncio.run(main())
    except KeyboardInterrupt: pass
