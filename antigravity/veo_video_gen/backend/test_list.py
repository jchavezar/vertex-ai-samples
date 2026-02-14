import vertexai
from vertexai import agent_engines
vertexai.init(project="vtxdemos", location="us-central1")
l = agent_engines.list()
for e in l:
    print(f"{e.gca_resource.display_name}: {e.gca_resource.name}")
