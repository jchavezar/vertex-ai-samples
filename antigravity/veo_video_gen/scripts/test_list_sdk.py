import os
import vertexai
from vertexai import agent_engines

os.environ["GOOGLE_CLOUD_PROJECT"] = "vtxdemos"
os.environ["GOOGLE_CLOUD_LOCATION"] = "us-central1"

vertexai.init(project="vtxdemos", location="us-central1")
agents = agent_engines.list()
print(f"Total agents: {len(agents)}")
for a in agents:
    print(f"Name: {a.display_name}, Resource: {a.resource_name}")
