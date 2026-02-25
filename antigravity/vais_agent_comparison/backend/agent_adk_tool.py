# Standard ADK Vertex AI Search Tool Implementation
import os
import asyncio
import logging
import uuid
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.tools import VertexAiSearchTool
from google.adk import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

load_dotenv()

# Configuration
# Configuration
DATA_STORE_ID = os.getenv("DATA_STORE_ID")
SEARCH_ENGINE_ID = os.getenv("SEARCH_ENGINE_ID")

# Define the Tool
from vertex_ai_search_tool_custom import VertexAiSearchToolCustom

if SEARCH_ENGINE_ID:
    search_tool = VertexAiSearchToolCustom(
        search_engine_id=SEARCH_ENGINE_ID,
        max_results=5
    )
else:
    # Fallback to Data Store ID (defaulting if not set, for legacy compatibility)
    ds_id = DATA_STORE_ID or "projects/254356041555/locations/global/collections/default_collection/dataStores/factset-datastore_1768933098294"
    search_tool = VertexAiSearchToolCustom(
        data_store_id=ds_id,
        max_results=5
    )

# Define the Agent
root_agent = LlmAgent(
    name="adk_search_agent",
    model="gemini-2.5-flash",
    description="You are a helpful assistant.",
    instruction="""
    Use your 'search_tool' to answer the user's question. 
    If the tool returns no results or empty content, you MUST respond with: 'I could not find any information about that in the data store.' 
    Do NOT use your internal knowledge or invent anything.
    """,
    tools=[search_tool]
)

async def run_query(query: str) -> dict:
    """
    Executes the agent with the given query and returns the response and logs.
    """
    logging.basicConfig(level=logging.INFO)
    session_service = InMemorySessionService()
    runner = Runner(agent=root_agent, session_service=session_service, app_name="adk_search")
    
    user_id = "test_user"
    session_id = str(uuid.uuid4())
    await session_service.create_session(user_id=user_id, session_id=session_id, app_name="adk_search")
    
    logs = []
    response_text = "No response generated."
    
    user_msg = types.Content(role="user", parts=[types.Part(text=query)])
    logs.append(f"User Query: {query}")
    
    try:
        async for event in runner.run_async(
            new_message=user_msg,
            user_id=user_id,
            session_id=session_id
        ):
            # Capture logs (simplified representation of event)
            try:
                # Try pydantic v2 dump
                if hasattr(event, "model_dump_json"):
                    logs.append(event.model_dump_json(indent=2))
                # Try pydantic v1 json
                elif hasattr(event, "json"):
                    logs.append(event.json(indent=2))
                else:
                    logs.append(str(event))
            except Exception:
                logs.append(str(event))
            
            text = getattr(event, "text", None)
            if text:
                response_text = text
                logs.append(f"Agent Response: {text}")
                
    except Exception as e:
        logs.append(f"Error: {e}")
        response_text = f"Error executing agent: {e}"
        
    return {
        "response": response_text,
        "logs": "\n".join(logs)
    }

if __name__ == "__main__":
    import sys
    query = "how was the revenue for factset?"
    if len(sys.argv) > 1:
        query = sys.argv[1]
    result = asyncio.run(run_query(query))
    print(f"Agent: {result['response']}")