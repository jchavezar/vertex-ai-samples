import asyncio
import os
from dotenv import load_dotenv
from google.adk import Agent
from google.adk.runners import InMemoryRunner
from google.adk.tools import google_search
from google.adk.agents.sequential_agent import SequentialAgent
from google.genai import types

# Load environment variables
load_dotenv()

async def run_delegation_test():
    # 1. Search Agent (Leaf)
    search_agent = Agent(
        name="SearchAgent",
        model="gemini-2.5-flash",
        instruction="Use Google Search to answer.",
        tools=[google_search]
    )

    # 2. Sequential Agent
    # We define it as a standard agent
    sequential_agent = SequentialAgent(
        name="SequentialAgent",
        description="Handles complex multi-step research tasks.",
        sub_agents=[search_agent]
    )

    # 3. Root Agent using SUB_AGENTS (Delegation) instead of TOOLS
    # By putting it in sub_agents, the events will flow to the main loop.
    root_agent = Agent(
        name="RootAgent",
        model="gemini-2.5-flash",
        instruction="Transfer to SequentialAgent to answer the user's question.",
        sub_agents=[sequential_agent] 
    )

    runner = InMemoryRunner(agent=root_agent)
    runner.auto_create_session = True

    query = "What is the current status of Artemis missions?"
    print(f"Query: {query}\n")
    print("-" * 50)

    # Standard run_async loop
    async for event in runner.run_async(
        user_id="u", session_id="s", 
        new_message=types.Content(parts=[types.Part(text=query)], role="user")
    ):
        # 1. Print text as it streams
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    print(part.text, end="", flush=True)

        # 2. READ CHUNKS DIRECTLY FROM THE MAIN EVENT
        # This works now because events from sub-agents are yielded to the main loop!
        if event.grounding_metadata:
            print("\n\n[MAIN EVENT] Grounding Metadata Detected!")
            if event.grounding_metadata.grounding_chunks:
                print(f"Found {len(event.grounding_metadata.grounding_chunks)} chunks.")
                for gc in event.grounding_metadata.grounding_chunks:
                    if gc.web:
                        print(f"Source Link: {gc.web.uri}")
            print("-" * 50)

if __name__ == "__main__":
    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "true"
    asyncio.run(run_delegation_test())
