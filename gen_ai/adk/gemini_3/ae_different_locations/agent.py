from google.adk.agents import LlmAgent

root_agent = LlmAgent(
    name="root_agent",
    model="projects/vtxdemos/locations/global/publishers/google/models/gemini-3-pro-preview",
    description="Respond to any question"
)