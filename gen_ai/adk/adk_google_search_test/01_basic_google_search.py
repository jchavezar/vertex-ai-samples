import asyncio
import os
from dotenv import load_dotenv
from google.adk import Agent
from google.adk.runners import InMemoryRunner
from google.adk.tools import google_search
from google.genai import types

# Load environment variables
load_dotenv()

async def run_google_search_test():
    # Ensure environment variables are set
    project = os.getenv("GOOGLE_CLOUD_PROJECT")
    location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    
    print(f"Project: {project}")
    print(f"Location: {location}")
    print(f"Use Vertex AI: {os.getenv('GOOGLE_GENAI_USE_VERTEXAI')}")

    # 1. Define the Agent
    # Using gemini-2.5-flash which is the specific model ID on Vertex AI
    agent = Agent(
        name="SearchAgent",
        model="gemini-2.5-flash",
        instruction="You are a helpful assistant. Use Google Search to find the latest information.",
        tools=[google_search]
    )

    # 2. Initialize Runner
    runner = InMemoryRunner(agent=agent)

    # 3. Create a session
    user_id = "test_user"
    session_id = "test_session"
    await runner.session_service.create_session(
        app_name=runner.app_name,
        user_id=user_id,
        session_id=session_id
    )

    # 4. Execute with streaming
    query_text = "What are the latest news about Gemini 2.0? Give me some links."
    print(f"\nQuerying: {query_text}\n")
    print("-" * 50)

    new_message = types.Content(
        parts=[types.Part(text=query_text)],
        role="user"
    )

    grounding_links = set()

    try:
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=new_message
        ):
            print("\n\n")
            print(event)
            # Print text content
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        print(part.text, end="", flush=True)
            
            # Grounding metadata
            if event.grounding_metadata:
                if event.grounding_metadata.grounding_chunks:
                    for gc in event.grounding_metadata.grounding_chunks:
                        if gc.web and gc.web.uri:
                            grounding_links.add(gc.web.uri)
    except Exception as e:
        print(f"\n\nError during execution: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "-" * 50)
    print("\n--- Identified Grounding Links ---")
    if grounding_links:
        for link in sorted(list(grounding_links)):
            print(f"- {link}")
    else:
        print("No grounding links found.")

if __name__ == "__main__":
    asyncio.run(run_google_search_test())
