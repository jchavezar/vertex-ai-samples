import asyncio
import os
from dotenv import load_dotenv
from google.adk import Agent
from google.adk.runners import InMemoryRunner
from google.adk.tools import google_search
from google.adk.agents.sequential_agent import SequentialAgent
from google.genai import types
from typing import AsyncIterator
from google.adk.events import Event

# Load environment variables
load_dotenv()

class GroundingAwareAgent(Agent):
    """
    A custom Agent that wraps another agent and intercepts events
    to capture grounding metadata into the session state WITHOUT creating a new session.
    
    Instead of being a 'Tool', this is a 'Delegated Agent'.
    """
    def __init__(self, target_agent: Agent):
        # Initialize with the target agent's properties
        super().__init__(
            name=target_agent.name,
            description=target_agent.description,
            instruction=target_agent.instruction,
            tools=target_agent.tools,
            sub_agents=target_agent.sub_agents
        )
        self.target_agent = target_agent

    async def _run_async_impl(self, ctx) -> AsyncIterator[Event]:
        """
        Overrides the internal execution logic. 
        'ctx' is the InvocationContext which contains the ALREADY EXISTING session.
        """
        print(f"\n[GroundingAwareAgent] Intercepting execution for {self.name} in existing session...")
        
        all_grounding_metadata = []
        
        # Delegate to the target agent's implementation using the SAME context
        # This keeps the history and state unified.
        async for event in self.target_agent._run_async_impl(ctx):
            # Intercept metadata as it flows through
            if event.grounding_metadata:
                all_grounding_metadata.append(event.grounding_metadata)
            
            # Yield the event so it reaches the root runner
            yield event
            
        # Store collected metadata in the shared session state
        if all_grounding_metadata:
            ctx.session.state["last_tool_grounding"] = [gm.model_dump() for gm in all_grounding_metadata]
            print(f"[GroundingAwareAgent] Saved {len(all_grounding_metadata)} grounding entries to session state.")

async def run_test():
    # 1. Leaf Agent
    search_agent = Agent(
        name="SearchAgent",
        model="gemini-2.5-flash",
        instruction="Use Google Search to answer.",
        tools=[google_search]
    )

    # 2. Sequential Agent (the logic we want to wrap)
    seq_agent = SequentialAgent(
        name="SequentialAgent",
        sub_agents=[search_agent]
    )

    # 3. WRAP with our Custom Agent Class
    # This replaces the need for GroundingAwareAgentTool class
    wrapped_seq_agent = GroundingAwareAgent(target_agent=seq_agent)

    # 4. Root Agent using Delegation (sub_agents) instead of Tools
    root_agent = Agent(
        name="RootAgent",
        model="gemini-2.5-flash",
        instruction="Transfer to SequentialAgent. If you see 'last_tool_grounding' in your state, mention you found sources.",
        sub_agents=[wrapped_seq_agent] 
    )

    # Root Runner
    runner = InMemoryRunner(agent=root_agent)
    runner.auto_create_session = True

    print("Querying with GroundingAwareAgent (Delegation)...")
    new_message = types.Content(parts=[types.Part(text="What is the status of Artemis II?")], role="user")
    
    async for event in runner.run_async(
        user_id="u", session_id="s", 
        new_message=new_message
    ):
        if event.content:
            for p in event.content.parts:
                if p.text: print(p.text, end="", flush=True)

    # Verify state in the same session
    session = await runner.session_service.get_session(app_name=runner.app_name, user_id="u", session_id="s")
    print("\n" + "="*50)
    print("CHECKING SHARED SESSION STATE:")
    if "last_tool_grounding" in session.state:
        gms = session.state["last_tool_grounding"]
        print(f"Found {len(gms)} grounding metadata entries in state.")
        # The root agent can now see this state in the next turn of the conversation
    else:
        print("No grounding metadata found in session state.")
    print("="*50)

if __name__ == "__main__":
    # Ensure Vertex AI is enabled for grounding
    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "true"
    asyncio.run(run_test())
