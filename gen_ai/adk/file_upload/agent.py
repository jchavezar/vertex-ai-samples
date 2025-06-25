#%%
from google.adk.agents import LlmAgent
from google.adk.tools import load_artifacts

root_agent = LlmAgent(
    name="root_agent",
    model="gemini-2.5-flash",
    instruction="Answer any question, ALWAYS use your artifacts from load_artifacts tool",
    tools=[load_artifacts],
)
