import os
import sys
import vertexai
from vertexai.agent_engines import AdkApp

# Add current directory to path to import agent
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from agent import root_agent

# --- CONFIGURATION ---
AGENT_ENGINE_NAME = "claude_sonnet_a2a_agent"
LOCATION = "us-central1"
PROJECT_ID = "vtxdemos"
STAGING_BUCKET = "gs://vtxdemos-staging"

# Initialize Vertex AI
print(f"Initializing Vertex AI for project '{PROJECT_ID}' in location '{LOCATION}'...")
vertexai.init(
    project=PROJECT_ID,
    location=LOCATION,
    staging_bucket=STAGING_BUCKET
)

client = vertexai.Client(
    project=PROJECT_ID,
    location=LOCATION
)

# Wrap in AdkApp for managed execution, tracing and logging
deployment_app = AdkApp(
    agent=root_agent,
    app_name=AGENT_ENGINE_NAME,
    enable_tracing=True
)

def deploy():
    print(f"Searching for existing Agent Engine: {AGENT_ENGINE_NAME}...")
    all_engines = list(client.agent_engines.list())
    target_engine = next((e for e in all_engines if e.api_resource.display_name == AGENT_ENGINE_NAME), None)
    
    config = {
        "display_name": AGENT_ENGINE_NAME,
        "staging_bucket": STAGING_BUCKET,
        "requirements": "requirements.txt",
        "extra_packages": ["agent.py"]
    }

    if target_engine:
        print(f"Found existing engine: {target_engine.api_resource.name}. Updating...")
        remote_app = client.agent_engines.update(
            name=target_engine.api_resource.name,
            agent=deployment_app,
            config=config
        )
        print("\n" + "="*50)
        print(f"SUCCESS: Agent updated.")
        print(f"ReasoningEngine Resource Name:\n{remote_app.api_resource.name}")
        print("="*50 + "\n")
    else:
        print("No existing engine found. Creating new...")
        remote_app = client.agent_engines.create(
            agent=deployment_app,
            config=config
        )
        print("\n" + "="*50)
        print(f"SUCCESS: Agent created.")
        print(f"ReasoningEngine Resource Name:\n{remote_app.api_resource.name}")
        print("="*50 + "\n")

if __name__ == "__main__":
    deploy()
