import asyncio
from typing import AsyncGenerator
from google.adk.agents import BaseAgent
from google.adk.runners import Runner, RunConfig
from google.genai import types
from google.adk.agents.invocation_context import InvocationContext
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.adk.events.event import Event

# Import the custom plugin
from a2a_interceptor_plugin import AgentEngineInterceptorPlugin

class EchoAgent(BaseAgent):
    """A minimal echo agent to demonstrate the interceptor."""
    def __init__(self):
        super().__init__(name="echo_agent", description="Echoes what you say.")

    async def _run_async_impl(
        self,
        ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        # The initial message that started this invocation is user_content
        user_content = ctx.user_content
        text = ""
        if user_content and user_content.parts:
            for part in user_content.parts:
                if part.text:
                    text += part.text
        print(f"EchoAgent Processing text: {text}")
        
        # In ADK, agents yield events.
        yield Event(
            content=types.Content(parts=[types.Part.from_text(text=f"Echo: {text}")]),
            author=self.name,
        )

async def test_local_interception():
    # 1. Instantiate your Agent
    my_agent = EchoAgent()

    # 2. Instantiate your Interceptor Plugin
    interceptor_plugin = AgentEngineInterceptorPlugin()

    # 3. Create a Runner with the plugin
    runner = Runner(
        agent=my_agent,
        app_name="my_test_agent_engine_app",
        session_service=InMemorySessionService(),
        plugins=[interceptor_plugin]
    )

    # 4. Mock the A2A Input Payload
    user_id = "A2A_USER_12345"
    session_id = "sess-abcde"
    
    # We must ensure the session exists in the session_service, just as `A2aAgentExecutor` does
    session = await runner.session_service.create_session(
        app_name=runner.app_name,
        user_id=user_id,
        session_id=session_id,
        state={}
    )

    run_args = {
        "user_id": user_id,
        "session_id": session_id,
        "new_message": types.Content(
            role="user",
            parts=[types.Part.from_text(text="Hello, Agent Engine!")]
        ),
        "run_config": RunConfig(),
    }

    print("\\n--- Starting test local runner ---")
    async for event in runner.run_async(**run_args):
        pass
    print("--- Finished test local runner ---\\n")

if __name__ == "__main__":
    asyncio.run(test_local_interception())
