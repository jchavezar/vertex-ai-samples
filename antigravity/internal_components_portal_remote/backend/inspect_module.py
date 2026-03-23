import vertexai.agent_engines
from vertexai.agent_engines import AdkApp

print("Methods on AdkApp class:")
print([m for m in dir(AdkApp) if not m.startswith("_")])

print("\nMethods on vertexai.agent_engines:")
print([m for m in dir(vertexai.agent_engines) if not m.startswith("_")])
