from google.genai import types
from sub_agents.database import *
from google.adk.planners import BuiltInPlanner
from google.adk.agents import Agent, LlmAgent

my_planner = BuiltInPlanner(
    thinking_config=types.ThinkingConfig(
        thinking_budget=0
    )
)

researcher_agent_1 = Agent(
    name="researcher_agent_1",
    model="gemini-2.0-flash-001",
    description="Any information about Illya",
    instruction=f"""You are an AI Research Assistant grounding with the following information from Illya: {illya_doc}'.
    Do a extensively research with that information to support the root agent.
    """,
    output_key="illya_info"
)

researcher_agent_2 = Agent(
    name="researcher_agent_2",
    model="gemini-2.0-flash-001",
    instruction=f"""You are an AI Research Assistant grounding with the following information from Luis: {luis_doc}'.
    Do a extensively research with that information to support the root agent.
    """,
    description="Information about Luis",
    output_key="luis_info"
)

root_agent = Agent(
    name="ParallelWebResearchAgent",
    model="gemini-2.5-flash-preview-04-17",
    sub_agents=[researcher_agent_1, researcher_agent_2],
    description="You are a profile researcher answering any question about profiles.",  # Added description
    instruction="""
    1. Use the 'researcher_agent_1' to gather every single detail about Illya.
    2. Use the 'researcher_agent_2' to gather every single detail about Luis.
    
    With that information answer any question if you do not know the answer just say so.
    """,
    planner=my_planner
)
