import asyncio
import os
from dotenv import load_dotenv
from google.adk import Agent
from google.adk.runners import InMemoryRunner
from google.adk.tools import google_search, AgentTool
from google.adk.agents.sequential_agent import SequentialAgent
from google.genai import types

# Load environment variables
load_dotenv()

async def run_reproduction():
    print(f"Project: {os.getenv('GOOGLE_CLOUD_PROJECT')}")
    print(f"Location: {os.getenv('GOOGLE_CLOUD_LOCATION')}")
    print(f"Use Vertex AI: {os.getenv('GOOGLE_GENAI_USE_VERTEXAI')}")

    # 1. Setup the Search Agent (Leaf Agent)
    search_agent = Agent(
        name="SearchAgent",
        model="gemini-2.5-flash",
        instruction="Use Google Search to answer questions concisely.",
        tools=[google_search]
    )

    # 2. Setup a Sequential Agent with multiple steps
    # For simplicity, we just have one step that does the search, 
    # but it could be multiple steps as per customer description.
    sequential_agent = SequentialAgent(
        name="SequentialAgent",
        sub_agents=[search_agent]
    )

    # 3. Setup the Root Agent with an AgentTool wrapping the SequentialAgent
    agent_tool = AgentTool(agent=sequential_agent)
    
    root_agent = Agent(
        name="RootAgent",
        model="gemini-2.5-flash",
        instruction="You are a dispatcher. Use the SequentialAgent tool to answer the user's request.",
        tools=[agent_tool]
    )

    # 4. Initialize Runner for Root Agent
    runner = InMemoryRunner(agent=root_agent)
    user_id = "customer_user"
    session_id = "customer_session"
    await runner.session_service.create_session(
        app_name=runner.app_name,
        user_id=user_id,
        session_id=session_id
    )

    # 5. Execute query
    query_text = "What is the latest status of the Artemis program? Use Google Search."
    print(f"\nRoot Query: {query_text}\n")
    print("-" * 50)

    new_message = types.Content(
        parts=[types.Part(text=query_text)],
        role="user"
    )

    has_grounding = False

    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=new_message
    ):
        # Print root agent output
        if event.content and event.content.parts:
            print(event)
            for part in event.content.parts:
                if part.text:
                    print(part.text, end="", flush=True)
                if part.function_call:
                    print(f"\n[Root calling tool: {part.function_call.name} with {part.function_call.args}]")
                if part.function_response:
                    print(f"\n[Root received tool response for {part.function_response.name}]")

        # Check for grounding metadata in the final response
        if event.grounding_metadata:
            has_grounding = True
            print("\n\n[FOUND GROUNDING METADATA IN EVENT]")
            if event.grounding_metadata.grounding_chunks:
                print(f"Chunks count: {len(event.grounding_metadata.grounding_chunks)}")
                for gc in event.grounding_metadata.grounding_chunks:
                    if gc.web:
                        print(f"Link: {gc.web.uri}")

    print("\n" + "-" * 50)
    if not has_grounding:
        print("\nRESULT: No grounding metadata found in the Root Agent's output events.")
    else:
        print("\nRESULT: Grounding metadata WAS found (Reproduction failed or ADK behavior changed).")

if __name__ == "__main__":
    # Ensure Vertex AI is used
    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "true"
    os.environ["GOOGLE_CLOUD_LOCATION"] = "us-central1"
    
    asyncio.run(run_reproduction())
