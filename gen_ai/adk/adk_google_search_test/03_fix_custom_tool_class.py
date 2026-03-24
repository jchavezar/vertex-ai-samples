import asyncio
import os
from dotenv import load_dotenv
from google.adk import Agent
from google.adk.runners import InMemoryRunner
from google.adk.tools import google_search, AgentTool
from google.adk.agents.sequential_agent import SequentialAgent
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.tools._forwarding_artifact_service import ForwardingArtifactService
from google.genai import types
from typing import Any
from typing_extensions import override

# Load environment variables
load_dotenv()

class GroundingAwareAgentTool(AgentTool):
    """
    A custom AgentTool that propagates grounding metadata from the sub-agent
    to the parent session via the tool state.
    """
    @override
    async def run_async(
        self,
        *,
        args: dict[str, Any],
        tool_context: ToolContext,
    ) -> Any:
        # Standard AgentTool setup
        if self.skip_summarization:
            tool_context.actions.skip_summarization = True

        # Handle input
        from google.adk.agents.llm_agent import LlmAgent
        if isinstance(self.agent, LlmAgent) and self.agent.input_schema:
            input_value = self.agent.input_schema.model_validate(args)
            content = types.Content(
                role='user',
                parts=[types.Part.from_text(text=input_value.model_dump_json(exclude_none=True))],
            )
        else:
            content = types.Content(
                role='user',
                parts=[types.Part.from_text(text=args['request'])],
            )

        # Internal Runner - version 1.27.x signature
        runner = Runner(
            app_name=self.agent.name,
            agent=self.agent,
            artifact_service=ForwardingArtifactService(tool_context),
            session_service=InMemorySessionService(),
            memory_service=InMemoryMemoryService(),
        )
        # Enable auto_create_session for the internal runner
        runner.auto_create_session = True

        last_event = None
        all_grounding_metadata = []

        async for event in runner.run_async(
            user_id='tmp_user', session_id='tmp_session', new_message=content
        ):
            if event.actions.state_delta:
                tool_context.state.update(event.actions.state_delta)
            
            # --- CUSTOM LOGIC: CAPTURE GROUNDING METADATA ---
            if event.grounding_metadata:
                all_grounding_metadata.append(event.grounding_metadata)
            
            last_event = event

        # Store collected grounding metadata in state so it can be accessed if needed
        if all_grounding_metadata:
            # We store it in a special state key
            tool_context.state["last_tool_grounding"] = [gm.model_dump() for gm in all_grounding_metadata]
            print(f"\n[GroundingAwareAgentTool] Captured {len(all_grounding_metadata)} grounding metadata objects.")

        if not last_event or not last_event.content or not last_event.content.parts:
            return ''
        
        merged_text = '\n'.join(p.text for p in last_event.content.parts if p.text)
        return merged_text

async def run_test():
    # 1. Leaf Agent
    search_agent = Agent(
        name="SearchAgent",
        model="gemini-2.5-flash",
        instruction="Use Google Search to answer.",
        tools=[google_search]
    )

    # 2. Sequential Agent
    seq_agent = SequentialAgent(
        name="SequentialAgent",
        sub_agents=[search_agent]
    )

    # 3. Root Agent with GroundingAwareAgentTool
    agent_tool = GroundingAwareAgentTool(agent=seq_agent)
    
    root_agent = Agent(
        name="RootAgent",
        model="gemini-2.5-flash",
        instruction="Use the SequentialAgent tool. Mention the sources if you see 'last_tool_grounding' in your state.",
        tools=[agent_tool]
    )

    # Initialize Root Runner
    runner = InMemoryRunner(agent=root_agent)
    runner.auto_create_session = True

    print("Querying with GroundingAwareAgentTool...")
    # Use role='user' for the root message as well
    new_message = types.Content(parts=[types.Part(text="What is Artemis status?")], role="user")
    
    async for event in runner.run_async(
        user_id="u", session_id="s", 
        new_message=new_message
    ):
        if event.content:
            for p in event.content.parts:
                if p.text: print(p.text, end="", flush=True)
        
        if event.grounding_metadata:
            print("\n[ROOT RECEIVED GROUNDING!]")

    # Print what we captured in the root session state
    session = await runner.session_service.get_session(app_name=runner.app_name, user_id="u", session_id="s")
    print("\n" + "="*50)
    print("CHECKING ROOT SESSION STATE FOR CAPTURED GROUNDING:")
    if "last_tool_grounding" in session.state:
        gms = session.state["last_tool_grounding"]
        print(f"Found {len(gms)} grounding metadata entries in state.")
        for i, gm in enumerate(gms):
            if "grounding_chunks" in gm:
                for chunk in gm["grounding_chunks"]:
                    if "web" in chunk and "uri" in chunk["web"]:
                        print(f"Link {i+1}: {chunk['web']['uri']}")
    else:
        print("No grounding metadata found in root session state.")
    print("="*50)

if __name__ == "__main__":
    asyncio.run(run_test())
