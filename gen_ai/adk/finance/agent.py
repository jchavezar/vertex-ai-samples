import os
from google import genai
from google.genai import types
from google.cloud import storage
from google.adk.tools import google_search
from google.adk.agents import Agent, LlmAgent
from google.adk.planners import BuiltInPlanner
from google.adk.tools.agent_tool import AgentTool

project_id = "vtxdemos"
bucket = "vtxdemos-datasets-public"

storage_client = storage.Client(project=project_id)
bucket = storage_client.bucket(bucket_name=bucket)

my_planner = BuiltInPlanner(
    thinking_config=types.ThinkingConfig(
        thinking_budget=0
    )
)

def read_file_content(file_name: str):
    """
    Read the content of a file.
    :param file_name:
    :return:
    """
    print(file_name)
    try:
        blob = bucket.blob(f"finance/{file_name}")
        _text = blob.download_as_text()
        return _text
    except Exception as e:
        return f"Error reading file: {e}"


holding_agent = LlmAgent(
    name="holding_agent",
    model="gemini-2.5-flash-preview-05-20",
    description="You are an financial agent analyst specialized in holdings",
    instruction="""
    User your tool to get information about holdings.
    
    Note:
    Your tool has a file_name requirement that you can fulfill with file_name: synthetic_data_holdings.json
    """,
    tools=[read_file_content],
    planner=my_planner
)

events_agent = LlmAgent(
    name="events_agent",
    model="gemini-2.5-flash-preview-05-20",
    description="You are an financial agent analyst specialized in events",
    instruction="""
    Use your tool to get information about events like new ratings or financial efficiency.
    
    Note:
    Your tool has a fila_name requirement that you can fulfill with file_name: synthetic_data_events.json
    """,
    tools=[read_file_content],
    planner=my_planner
)

google_agent = LlmAgent(
    name="google_agent",
    model="gemini-2.5-flash-preview-05-20",
    description="An Agent to do internet research.",
    instruction="Answer any question regarding market trends.",
    tools=[google_search],
    planner=my_planner
)


root_agent = LlmAgent(
    name="root_agent",
    model="gemini-2.5-flash-preview-05-20",
    description="You are an Orchestrator Agent with multiple agents to answer any question",
    instruction="""
    Use your agents to answer any question according:
    
    `holding_agent`:
       - purpose: to answer questions related to holdings or portfolio only.
       - data available in this agent: company_id, company name, sector, current_holding_usd, risk_profile
    `events_agent` 
       - purpose: to answer questions related to new events like ratings or positive/negative outlook and sentiment only.
       - data available in this agent: company_id, rating, outlook, credit_opinion, financial_changes.
       
    `google_agent`
       - purpose: to answer any questions related to trends and latest news using google search/web.
    
    Thinking layer:
     - If you cant find data in one agent try in the other agent.
     - Use data available in one agent to match with data available in the other agent.
    """,
    tools=[
        AgentTool(agent=holding_agent),
        AgentTool(agent=events_agent),
        AgentTool(agent=google_agent),
    ]
)
