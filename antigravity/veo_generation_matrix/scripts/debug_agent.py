import asyncio
from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from agent import video_expert_agent

load_dotenv()

async def debug_agent_tool_call():
    print("=== DEBUGGING AGENT TOOL CALL ===")
    session_service = InMemorySessionService()
    runner = Runner(agent=video_expert_agent, app_name="debug_agent", session_service=session_service)
    
    session_id = "test-session"
    prompt = "Generate a video of a cat dancing in high quality"
    
    print(f"Sending prompt to agent: {prompt}")
    events = await runner.run_debug(session_id=session_id, user_messages=prompt)
    
    found_text = False
    for event in events:
        print(f"Event detected: {type(event)}")
        if hasattr(event, 'text') and event.text:
            print(f"AGENT TEXT: {event.text}")
            found_text = True
        
        # In ADK, tool calls are often events or reflected in session turns
        # Let's check session after run
    
    session = session_service.sessions.get(session_id)
    if session:
        print(f"Session Turns: {len(session.turns)}")
        for i, turn in enumerate(session.turns):
            print(f"Turn {i} role: {turn.role}")
            if turn.parts:
                for j, part in enumerate(turn.parts):
                    print(f"  Part {j}: {type(part)}")
                    if hasattr(part, 'text'):
                        print(f"    Text: {part.text}")
                    if hasattr(part, 'call'):
                        print(f"    TOOL CALL: {part.call}")

if __name__ == "__main__":
    asyncio.run(debug_agent_tool_call())
