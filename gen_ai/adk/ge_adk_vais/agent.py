from google.adk.agents import Agent
from google.adk.tools import VertexAiSearchTool, AgentTool

DATASTORE_PATH = "projects/254356041555/locations/global/collections/default_collection/dataStores/ap-datastore"
vertex_search_tool = VertexAiSearchTool(data_store_id=DATASTORE_PATH)

vertex_search_agent_tool = Agent(
    name='vertex_search_agent_tool',
    model='gemini-2.5-flash',
    description="""
    Your main mission is to use your `vertex_search_tool` to get the most recent and relevant information to answer 
    user queries.
    
    ** ALWAYS ** follow the next sequence:
    
    1. Get the original query from the user, and create 2-3 expanded search sub-queries.
    2. Use the `vertex_search_tool` to search for each of the sub-queries.
    3. Collect the results from the searches, and synthesize a final answer to the user query based on the search 
    results.
    
    Do not bring your own knowledge base.
    
    Response needs to come with date:
    [Source: <source_name>, Date: <date>]
    """,
    tools=[vertex_search_tool],
)

root_agent = Agent(
    name='root_agent',
    model='gemini-2.5-flash',
    instruction="You are a helpful assistant that answers any user queries **ONLY** using your tools.",
    description="""
    Use your `vertex_search_agent_tool` tool to answer any question, do not use your knowledge base.
    """,
    tools=[AgentTool(vertex_search_agent_tool)],
)