from google.genai import types
from google.adk.agents import Agent
from google.adk.tools import agent_tool
from google.adk.planners import BuiltInPlanner
from google.adk.tools import google_search
from google.adk.tools.vertex_ai_search_tool import VertexAiSearchTool
from google.adk.code_executors import BuiltInCodeExecutor

my_planner = BuiltInPlanner(
    thinking_config=types.ThinkingConfig(
        thinking_budget=0
    )
)

vais_tool = VertexAiSearchTool(data_store_id="projects/254356041555/locations/global/collections/default_collection/dataStores/countries-and-their-cultur_1706277976842")

google_search_agent = Agent(
    model="gemini-2.5-flash",
    name="google_search",
    description="Use google search tool to find answers",
    tools=[google_search],
    planner=my_planner
)

execution_agent = Agent(
    model="gemini-2.5-flash",
    name="execution_agent",
    description="Use execution tool to get advance answers that required programming",
    tools=[BuiltInCodeExecutor],
    planner=my_planner
)

vais_local_search = Agent(
    model="gemini-2.5-flash",
    name="vais_local_search",
    description="Use local vais search tool to find answers",
    tools=[vais_tool],
    planner=my_planner
)

root_agent = Agent(
    name="root_agent",
    model="gemini-2.5-flash",
    description="God of Agents",
    instruction="""
    Your main task is to answer any question by detecting the intent and use your tools accordingly:
    
    Order of priority:
    1. If its a code generation use 'execution_agent'.
    2. If is any question that requires up to date information from internet use 'google_search_agent'.
    3. If the question is related to Countries and their Culture only use: 'vais_local_search' agent tool.
    3. For the rest use your knowledge based with that data was used during your training.
    
    Add in your response the method/tool used for your response.
    """,
    tools=[
        agent_tool.AgentTool(agent=google_search_agent),
        agent_tool.AgentTool(agent=execution_agent),
        agent_tool.AgentTool(agent=vais_local_search)
    ],
    planner=my_planner
)
