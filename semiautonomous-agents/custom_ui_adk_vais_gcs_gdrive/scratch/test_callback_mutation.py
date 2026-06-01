import asyncio
import re
from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.adk.agents.callback_context import CallbackContext
from google.genai.types import Content, Part

print("Designing callback mutation test...")

async def before_agent_callback(callback_context: CallbackContext) -> None:
    print("\n--- CALLBACK START ---")
    print("Initial state:", callback_context.state)
    print("Initial user_content text:")
    text = ""
    for part in callback_context.user_content.parts:
        if part.text:
            text += part.text
    print(repr(text))
    
    # Detect and extract token
    m = re.match(r"^\[ACCESS_TOKEN:(.*?)\]\s*(.*)$", text, re.DOTALL)
    if m:
        token = m.group(1)
        clean_text = m.group(2)
        print(f"-> Found token: {token}")
        print(f"-> Clean text: {repr(clean_text)}")
        
        # Update state dynamically!
        callback_context.state["drive_access_token"] = token
        callback_context.state["temp:drive_access_token"] = token
        
        # Mutate the user content in-place!
        for part in callback_context.user_content.parts:
            if part.text:
                part.text = clean_text
    else:
        print("-> No token pattern matched.")
    print("--- CALLBACK END ---\n")

# Simple tool to verify that the tool sees the state!
def dummy_tool(query: str, tool_context) -> dict:
    """A dummy tool to test search.
    
    Args:
        query: Search query
    """
    token = tool_context.state.get("drive_access_token")
    print(f"\n[TOOL RUNNING] State Token is: {token}\n")
    return {"status": "success", "token_used": token}

test_agent = Agent(
    name="test_mutator",
    model="gemini-3-flash-preview",
    instruction="You are a test helper. Call dummy_tool with the query.",
    tools=[dummy_tool],
    before_agent_callback=before_agent_callback
)

async def run_test():
    runner = InMemoryRunner(agent=test_agent, app_name="mutator_app")
    session = await runner.session_service.create_session(
        app_name="mutator_app",
        user_id="user1",
        state={"drive_access_token": "initial_token"}
    )
    
    print("Sending query with token prefix...")
    msg = "[ACCESS_TOKEN:secret_rotated_oauth_token] search for report 10k"
    content = Content(parts=[Part(text=msg)], role="user")
    
    async for event in runner.run_async(
        user_id="user1",
        session_id=session.id,
        new_message=content
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    print("Agent Text:", part.text)

asyncio.run(run_test())
