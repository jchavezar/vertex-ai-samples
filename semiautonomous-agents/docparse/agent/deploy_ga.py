"""Deploy the GA agent (simple, no re-ranker) to Agent Runtime."""
import os, subprocess, sys
from pathlib import Path
import vertexai
from dotenv import load_dotenv
from vertexai import agent_engines
from vertexai.preview import reasoning_engines

_HERE = Path(__file__).resolve().parent
load_dotenv(_HERE.parent / ".env")

PROJECT_ID = os.environ.get("DEPLOY_PROJECT_ID", "vtxdemos")
LOCATION = os.environ.get("DEPLOY_LOCATION", "us-central1")
STAGING_BUCKET = os.environ.get("DEPLOY_STAGING_BUCKET", f"gs://{PROJECT_ID}-staging-agent-engine")

CORPUS = os.environ.get("RAG_CORPUS_NAME", "projects/254356041555/locations/us-central1/ragCorpora/8338977660029894656")

RUNTIME_ENV_VARS = {
    "GOOGLE_CLOUD_LOCATION": "global",
    "GOOGLE_GENAI_USE_VERTEXAI": "true",
    # GOOGLE_CLOUD_PROJECT is auto-set by Agent Runtime (reserved env var)
    "RAG_CORPUS_NAME": CORPUS,
    "AGENT_MODEL": "gemini-2.5-flash",
    "AGENT_TOP_K": "20",
}

def deploy():
    print(f"\n=== Deploying GA agent → {PROJECT_ID} / {LOCATION} ===")
    print(f"Model: gemini-2.5-flash")
    print(f"Corpus: {CORPUS}\n")
    
    vertexai.init(project=PROJECT_ID, location=LOCATION, staging_bucket=STAGING_BUCKET)

    # Import the GA agent (ensure it's agent_ga, not agent)
    from docparse_agent.agent_ga import root_agent
    
    print(f"Agent name: {root_agent.name}")
    print(f"Tools: {[t.name for t in root_agent.tools]}\n")

    app = reasoning_engines.AdkApp(agent=root_agent, enable_tracing=True)

    remote = agent_engines.create(
        agent_engine=app,
        display_name="docparse-ga-agent",
        description="GA gemini-2.5-flash, 92.1% composite, observability enabled",
        requirements=["google-cloud-aiplatform[adk,agent_engines]"],
        extra_packages=["docparse_agent"],
        env_vars=RUNTIME_ENV_VARS,
    )

    print(f"\n=== Deployed ===")
    print(f"resource: {remote.resource_name}")
    print(f"trace: https://console.cloud.google.com/traces/list?project={PROJECT_ID}")
    return remote

if __name__ == "__main__":
    deploy()
