from google.adk.agents import LlmAgent

# Basic ADK Agent using gemini-2.5-flash
# This is the "root_agent" that will be deployed to Agent Engine
root_agent = LlmAgent(
    name="root_agent",
    model="gemini-2.5-flash",
    instruction="You are a helpful assistant running on Vertex AI Agent Engine. Respond concisely."
)
