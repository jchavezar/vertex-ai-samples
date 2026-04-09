"""
Cross-Project ADK Agent
Simple agent deployed in sharepoint-wif-portal, registered in vtxdemos Gemini Enterprise.
"""
from google.adk.agents import Agent


root_agent = Agent(
    name="cross_project_assistant",
    model="gemini-2.5-flash",
    description="A helpful assistant that answers questions using its knowledge",
    instruction="""You are a helpful assistant deployed across GCP projects.

You answer user questions clearly and concisely.
When you don't know something, say so honestly.

Always structure your responses with:
- A direct answer first
- Supporting details if needed
- Sources or caveats when relevant
""",
)
