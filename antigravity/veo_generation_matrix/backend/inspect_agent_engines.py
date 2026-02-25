import os
import vertexai
from dotenv import load_dotenv

load_dotenv(os.path.expanduser("~/.env"))

client = vertexai.Client(project=os.getenv("PROJECT_ID", "vtxdemos"), location="us-central1")

print("Methods on client.agent_engines:")
print(dir(client.agent_engines))

first_engine = next(iter(client.agent_engines.list()), None)
if first_engine:
    print(f"\nMethods on the returned AgentEngine list item ({first_engine.api_resource.name}):")
    print(dir(first_engine))
    
    # Try to get it
    remote_app = client.agent_engines.get(name=first_engine.api_resource.name)
    print("\nMethods on remote_app (agent_engines.get):")
    print(dir(remote_app))
else:
    print("No engines found")
