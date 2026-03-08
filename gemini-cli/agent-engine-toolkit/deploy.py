import os
import vertexai
from vertexai.agent_engines import AdkApp
import importlib

# --- CONFIGURATION ---
# We use your preferred engine name
AGENT_ENGINE_NAME = "root_agent_test"
STAGING_BUCKET = "gs://vtxdemos-staging"

def deploy():
    # Initialize Vertex AI SDK
    vertexai.init(
        project="vtxdemos",
        location="us-central1",
    )
    client = vertexai.Client(
        project="vtxdemos",
        location="us-central1",
    )

    # We define the agent inline to ensure AdkApp picks up the correct reference
    from google.adk.agents import LlmAgent
    root_agent = LlmAgent(
        name="root_agent",
        model="gemini-2.5-flash",
        instruction="You are a helpful assistant running on Vertex AI Agent Engine. Respond concisely."
    )

    # Wrap the agent
    deployment_app = AdkApp(
        agent=root_agent,
        enable_tracing=True,
    )

    # Automatic Deployment (Update or Create)
    print(f"Searching for existing Agent Engine: {AGENT_ENGINE_NAME}...")
    all_engines = list(client.agent_engines.list())
    target_engine = next((e for e in all_engines if e.api_resource.display_name == AGENT_ENGINE_NAME), None)

    # Prepare configuration
    # Note: vertexai.Client().agent_engines expects a list for requirements or a path to requirements.txt
    config = {
        "display_name": AGENT_ENGINE_NAME,
        "staging_bucket": STAGING_BUCKET,
        "requirements": ["google-adk", "google-genai", "pydantic"],
    }

    if target_engine:
        print(f"Found existing engine: {target_engine.api_resource.name}. Updating...")
        remote_app = client.agent_engines.update(
            name=target_engine.api_resource.name,
            agent=deployment_app,
            config=config
        )
        print(f"Update complete: {remote_app.api_resource.name}")
    else:
        print("No existing engine found. Creating new one...")
        remote_app = client.agent_engines.create(
            agent=deployment_app,
            config=config
        )
        print(f"Creation complete: {remote_app.api_resource.name}")
    
    return remote_app

if __name__ == "__main__":
    deploy()
