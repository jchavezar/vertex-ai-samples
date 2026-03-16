import os
import vertexai
from vertexai.agent_engines import AdkApp
from dotenv import load_dotenv

from workflow_agent import root_agent

load_dotenv()

# --- CONFIGURATION ---
AGENT_ENGINE_NAME = "dynamic_workflow_orchestrator_v5"
PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "vtxdemos") 
LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
if LOCATION == "global":
    LOCATION = "us-central1"
STAGING_BUCKET = "gs://vtxdemos-staging"

def deploy():
    print(f"Initializing Vertex AI in Project: {PROJECT_ID}, Location: {LOCATION}")
    vertexai.init(project=PROJECT_ID, location=LOCATION)
    client = vertexai.Client(project=PROJECT_ID, location=LOCATION)

    deployment_app = AdkApp(agent=root_agent, enable_tracing=True)

    print(f"Searching for existing Agent Engine: {AGENT_ENGINE_NAME}...")
    all_engines = list(client.agent_engines.list())
    target_engine = next((e for e in all_engines if e.api_resource.display_name == AGENT_ENGINE_NAME), None)

    # In ADK AdkApp Config, requirements can take arbitrary packages
    config = {
        "display_name": AGENT_ENGINE_NAME,
        "staging_bucket": STAGING_BUCKET,
        "requirements": ["google-adk", "google-genai", "pydantic", "fastapi", "uvicorn", "python-dotenv", "google-cloud-aiplatform", "cloudpickle"],
        "extra_packages": ["workflow_agent.py"]
    }

    if target_engine:
        print(f"Updating existing engine: {target_engine.api_resource.name}")
        remote_app = client.agent_engines.update(
            name=target_engine.api_resource.name,
            agent=deployment_app,
            config=config
        )
    else:
        print("Creating new engine...")
        remote_app = client.agent_engines.create(
            agent=deployment_app,
            config=config
        )
    print(f"Deployment complete: {remote_app.api_resource.name}")

if __name__ == "__main__":
    deploy()
