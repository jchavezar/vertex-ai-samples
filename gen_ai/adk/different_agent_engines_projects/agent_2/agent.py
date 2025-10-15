from google.adk.agents import Agent
from google.adk.tools import google_search

root_agent = Agent(
    name="root_agent",
    model="gemini-2.5-flash",
    description="You are a professional news analyst",
    instruction="""
    Use your `google_search` tool to find relevant, and recent information
    about news.
    Before using your tool create 2 subqueries and use the google search tool twice.
    
    Respond with the subqueries you used and where this information is coming from (citations).
    """,
    tools=[google_search],
)