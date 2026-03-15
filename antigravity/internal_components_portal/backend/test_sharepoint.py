import asyncio
from google.genai import types
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from agents.agent import get_agent_with_mcp_tools
from google.adk.runners import Runner
from dotenv import load_dotenv
load_dotenv("../.env")

async def test():
    token = "fake"
    agent, _ = await get_agent_with_mcp_tools(token=token)
    ss = InMemorySessionService()
    sess = await ss.create_session(app_name="PWC_Security_Proxy", user_id="default", session_id="123")
    runner = Runner(app_name="PWC_Security_Proxy", agent=agent, session_service=ss)
    from google.adk.events import Event
    messages = [
        {"role": "user", "content": "What is anti-gravity?"},
        {"role": "model", "content": "It is a secret project."},
        {"role": "user", "content": "Find the architecture diagram of project anti-gravity inside my google drive."}
    ]
    if len(messages) > 1:
        for msg in messages[:-1]:
            role = "user" if msg.get("role") == "user" else "model"
            part = types.Part.from_text(text=msg.get("content", ""))
            content_obj = types.Content(role=role, parts=[part])
            evt = Event(author=role, content=content_obj)
            sess.events.append(evt)
    
    msg_obj = types.Content(role="user", parts=[types.Part.from_text(text="Find the architecture diagram of project anti-gravity inside my google drive.")])
    print("Running...")
    try:
        async for e in runner.run_async(user_id="default", session_id="123", new_message=msg_obj):
            print("Event:", e.author, e.content)
            if e.content and hasattr(e.content, 'parts'):
                for p in e.content.parts:
                    if p.function_call:
                        print("  tool call:", p.function_call.name)
    except Exception as exc:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())
