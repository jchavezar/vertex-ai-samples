from vertexai.agent_engines import AdkApp
from google.adk.agents import LlmAgent

agent = LlmAgent(name="test", model="gemini-2.5-flash")
app = AdkApp(agent=agent)
print("Methods in AdkApp:")
print([m for m in dir(app) if not m.startswith('_')])
