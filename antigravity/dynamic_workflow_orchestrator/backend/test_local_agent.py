
import asyncio
from google.adk.agents.invocation_context import InvocationContext
from google.adk.sessions import Session
from workflow_agent import root_agent
from google.genai import types

async def test_workflow():
    session = Session(id="sess1", app_name="test", user_id="user1", state={"workflow_step": "start", "input_text": "This is a long article about space exploration."})
    ctx = InvocationContext(session=session)
    
    print("--- Phase 1: Start ---")
    async for event in root_agent.run_async(ctx):
        print(f"[{event.author}] {event.id}: {event.content.parts[0].text[:50]}...")
        if event.actions and event.actions.state_delta:
            print(f"  Delta: {event.actions.state_delta}")
            session.state.update(event.actions.state_delta)

    print("\nState after Phase 1:", session.state)
    
    # Simulate user sending "Yes"
    session.events.append(types.Content(role="user", parts=[types.Part(text="Yes")]))
    # Note: LlmAgent normally adds user messages to events. 
    # Here we emulate what Runner does.
    
    print("\n--- Phase 2: Continue ---")
    # We need to simulate the user event in the context session events
    # In ADK, ctx.session.events holds the history.
    # We need to be careful with types.
    from google.adk.events.event import Event
    session.events.append(Event(author="user", content=types.Content(role="user", parts=[types.Part(text="Yes")])))
    
    async for event in root_agent.run_async(ctx):
        print(f"[{event.author}] {event.id}: {event.content.parts[0].text[:50]}...")
        if event.actions and event.actions.state_delta:
            print(f"  Delta: {event.actions.state_delta}")
            session.state.update(event.actions.state_delta)

    print("\nState after Phase 2:", session.state)

if __name__ == "__main__":
    asyncio.run(test_workflow())
