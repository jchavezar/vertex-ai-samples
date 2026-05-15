"""Deploy the Discovery Engine agent to test grounding citations."""
import os, sys
from pathlib import Path
import vertexai
from dotenv import load_dotenv
from vertexai import agent_engines
from vertexai.preview import reasoning_engines

_HERE = Path(__file__).resolve().parent
load_dotenv(_HERE.parent / ".env")

PROJECT_ID = os.environ["DEPLOY_PROJECT_ID"]
LOCATION = os.environ.get("DEPLOY_LOCATION", "us-central1")
STAGING_BUCKET = os.environ.get("DEPLOY_STAGING_BUCKET", f"gs://{PROJECT_ID}-staging-agent-engine")

# DE-specific env vars passed to the agent
RUNTIME_ENV_VARS = {
    "GOOGLE_CLOUD_LOCATION": "global",
    "GOOGLE_GENAI_USE_VERTEXAI": "true",
    "DE_DATASTORE_ID": os.environ["DE_DATASTORE_ID"],
    "DE_PROJECT": os.environ.get("DE_PROJECT", "sharepoint-wif"),
    "DE_LOCATION": os.environ.get("DE_LOCATION", "global"),
    "AGENT_MODEL": os.environ.get("AGENT_MODEL", "gemini-3-flash-preview"),
}

def deploy():
    print(f"\n=== Deploying DE agent → {PROJECT_ID} / {LOCATION} ===\n")
    vertexai.init(project=PROJECT_ID, location=LOCATION, staging_bucket=STAGING_BUCKET)
    
    # Import here so env vars are loaded
    sys.path.insert(0, str(_HERE))
    from agent_de import root_agent
    
    app = reasoning_engines.AdkApp(agent=root_agent, enable_tracing=True)
    remote = agent_engines.create(
        agent_engine=app,
        display_name="docparse-de-agent",
        description="Discovery Engine variant of docparse agent — tests grounding citations",
        requirements=["google-cloud-aiplatform[adk,agent_engines]"],
        extra_packages=[],  # agent_de.py is standalone
        env_vars=RUNTIME_ENV_VARS,
    )
    print(f"\n=== Deployed ===")
    print(f"resource_name: {remote.resource_name}")
    return remote

if __name__ == "__main__":
    deploy()
