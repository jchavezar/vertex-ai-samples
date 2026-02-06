# Custom Discovery Engine Client Implementation
import os
import asyncio
import logging
import uuid
from dotenv import load_dotenv
from google.api_core.client_options import ClientOptions
from google.cloud import discoveryengine_v1 as discoveryengine
from google.adk.agents import LlmAgent
from google.adk import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

load_dotenv()

# Explicitly use the project and location from environment or hardcode
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "vtxdemos")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")

# Explicitly set env vars for google.genai
os.environ["GOOGLE_CLOUD_PROJECT"] = PROJECT_ID
os.environ["GOOGLE_CLOUD_LOCATION"] = LOCATION

async def search_data_store(query: str) -> str:
    """
    Searches the Vertex AI Search data store for the given query using the Discovery Engine Client.
    Return "No results found." if the search returns no documents.
    """
    print(f"\n[Tool] Searching Data Store for: '{query}'")

    project_id = "254356041555"
    location = "global"
    data_store_id = "factset-datastore_1768933098294"
    collection_id = "default_collection"

    client_options = (
        ClientOptions(api_endpoint=f"{location}-discoveryengine.googleapis.com")
        if location != "global"
        else None
    )
    
    try:
        # Create a client
        client = discoveryengine.SearchServiceClient(client_options=client_options)

        # The full resource name of the search app serving config
        serving_config = f"projects/{project_id}/locations/{location}/collections/{collection_id}/dataStores/{data_store_id}/servingConfigs/default_search"

        req = discoveryengine.SearchRequest(
            serving_config=serving_config,
            query=query,
            page_size=5,
            query_expansion_spec=discoveryengine.SearchRequest.QueryExpansionSpec(
                condition=discoveryengine.SearchRequest.QueryExpansionSpec.Condition.AUTO,
            ),
            spell_correction_spec=discoveryengine.SearchRequest.SpellCorrectionSpec(
                mode=discoveryengine.SearchRequest.SpellCorrectionSpec.Mode.AUTO
            ),
             content_search_spec=discoveryengine.SearchRequest.ContentSearchSpec(
                snippet_spec=discoveryengine.SearchRequest.ContentSearchSpec.SnippetSpec(
                    return_snippet=True
                ),
            )
        )

        response = client.search(req)
        
        results = []
        for result in response.results:
            doc = result.document
            derived = doc.derived_struct_data
            title = derived.get("title", "No Title")
            link = derived.get("link", "N/A")
            
            snippet = ""
            if extracted_snippets := derived.get("snippets"):
                snippet = extracted_snippets[0].get("snippet", "")
            
            results.append(f"Title: {title}\nLink: {link}\nSnippet: {snippet}")

        if not results:
             print("[Tool] Search returned 0 results.")
             return "No results found."

        output = "\n---\n".join(results)
        print(f"[Tool] Found {len(results)} results.")
        return output

    except Exception as e:
        print(f"[Tool] Error during search: {e}")
        return f"Error executing search: {str(e)}"

# Define the Agent
root_agent = LlmAgent(
    name="custom_client_agent",
    model="gemini-2.5-flash",
    description="I am a helpful assistant that searches the internal knowledge base.",
    instruction="""
    You are a helpful assistant. 
    1. ALWAYS use the `search_data_store` tool to find information about the user's question.
    2. If the tool returns "No results found.", honestly tell the user: "I searched the data store but found no relevant information."
    3. If the tool returns results, you MUST generate a text response summarizing the top 3 results.
    4. Do NOT stop after using the tool. You must answer the user.
    5. Do NOT invent information.
    """,
    tools=[search_data_store]
)

async def run_query(query: str) -> dict:
    """
    Executes the agent with the given query and returns the response and logs.
    """
    logging.basicConfig(level=logging.INFO)
    session_service = InMemorySessionService()
    runner = Runner(
        agent=root_agent,
        session_service=session_service,
        app_name="custom_search"
    )
    
    session_id = str(uuid.uuid4())
    user_id = "user@example.com"
    await session_service.create_session(user_id=user_id, session_id=session_id, app_name="custom_search")
    
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
            try:
                if hasattr(event, "model_dump_json"):
                    logs.append(event.model_dump_json(indent=2))
                elif hasattr(event, "json"):
                    logs.append(event.json(indent=2))
                else:
                    logs.append(str(event))
            except Exception:
                logs.append(str(event))
            
            text = None
            if hasattr(event, "content") and event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        text = part.text
                        break
            
            if not text:
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
