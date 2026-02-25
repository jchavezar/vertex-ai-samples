
import os
import vertexai
from vertexai.preview import reasoning_engines
from dotenv import load_dotenv

load_dotenv(dotenv_path="../.env")

PROJECT_ID = os.getenv("PROJECT_ID")
LOCATION = os.getenv("LOCATION", "us-central1")

print(f"Project: {PROJECT_ID}")
print(f"Location: {LOCATION}")

vertexai.init(project=PROJECT_ID, location=LOCATION)

try:
    agents = reasoning_engines.ReasoningEngine.list()
    print(f"Found {len(agents)} agents:")
    for agent in agents:
        print(f"  - Resource Name: {agent.resource_name}")
        print(f"  - Display Name: {getattr(agent, 'display_name', 'N/A')}")
except Exception as e:
    print(f"Error listing agents: {e}")
