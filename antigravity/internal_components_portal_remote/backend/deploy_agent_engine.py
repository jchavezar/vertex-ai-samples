import asyncio
from dotenv import load_dotenv
import os
import vertexai
from vertexai.agent_engines import AdkApp

from agents.router_agent import get_router_agent

# --- CONFIGURATION ---
AGENT_ENGINE_NAME = "ge_adk_portal_router"
STAGING_BUCKET = "gs://vtxdemos-staging" # Shared staging bucket

load_dotenv(override=True)

# Initialize Vertex AI SDK for the Agent Engine deployment context in us-central1
vertexai.init(
    project=os.getenv("GOOGLE_CLOUD_PROJECT", "vtxdemos"),
    location="us-central1",
)
client = vertexai.Client(
    project=os.getenv("GOOGLE_CLOUD_PROJECT", "vtxdemos"),
    location="us-central1",
)

# Instantiate the agent. Note: if gemini-3 is used, the agent dynamically sets a global GenAI client.
# Let's use the preview model to demonstrate the global failover!
print("Initializing the ADK Router Agent with gemini-2.5-flash...")
root_agent = get_router_agent(model="gemini-2.5-flash")

# Wrap the root agent in AdkApp
deployment_app = AdkApp(
    agent=root_agent,
    enable_tracing=True,
)

def deploy():
    print(f"Searching for existing Agent Engine: {AGENT_ENGINE_NAME}...")
    all_engines = list(client.agent_engines.list())
    target_engine = next((e for e in all_engines if e.api_resource.display_name == AGENT_ENGINE_NAME), None)
    
    config = {
        "display_name": AGENT_ENGINE_NAME,
        "staging_bucket": STAGING_BUCKET,
        "requirements": "requirements-adk.txt",
        "extra_packages": ["agents"], # Package the entire agents folder
    }

    if target_engine:
        print(f"Found existing engine: {target_engine.api_resource.name}. Updating...")
        remote_app = client.agent_engines.update(
            name=target_engine.api_resource.name,
            agent=deployment_app,
            config=config
        )
        print(f"Update complete. ReasoningEngine ID: {remote_app.api_resource.name}")
    else:
        print("No existing engine found. Creating new...")
        remote_app = client.agent_engines.create(
            agent=deployment_app,
            config=config
        )
        print(f"Creation complete. ReasoningEngine ID: {remote_app.api_resource.name}")

if __name__ == "__main__":
    deploy()
