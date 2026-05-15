"""Deploy GA agent to sharepoint-wif Agent Runtime.

Uses existing corpus in vtxdemos (cross-project access).
"""
import os
from pathlib import Path
import vertexai
from dotenv import load_dotenv
from vertexai import agent_engines
from vertexai.preview import reasoning_engines

_HERE = Path(__file__).resolve().parent
load_dotenv(_HERE.parent / ".env")

PROJECT_ID = "sharepoint-wif"
LOCATION = "us-central1"
STAGING_BUCKET = f"gs://{PROJECT_ID}-staging-agent-engine"
# Corpus stays in vtxdemos (cross-project)
CORPUS = os.environ.get("RAG_CORPUS_NAME", "projects/254356041555/locations/us-central1/ragCorpora/8338977660029894656")

RUNTIME_ENV_VARS = {
    "GOOGLE_CLOUD_LOCATION": "global",
    "GOOGLE_GENAI_USE_VERTEXAI": "true",
    "RAG_CORPUS_NAME": CORPUS,
    "AGENT_MODEL": "gemini-2.5-flash",
    "AGENT_TOP_K": "20",
}

def deploy():
    print(f"\n=== Deploying GA agent → {PROJECT_ID} / {LOCATION} ===")
    print(f"Corpus: {CORPUS}")

    vertexai.init(project=PROJECT_ID, location=LOCATION, staging_bucket=STAGING_BUCKET)
    from docparse_agent.agent_ga import root_agent

    app = reasoning_engines.AdkApp(agent=root_agent, enable_tracing=True)

    remote = agent_engines.create(
        agent_engine=app,
        display_name="docparse-ga-agent",
        description="GA gemini-2.5-flash, 92.1% composite",
        requirements=["google-cloud-aiplatform[adk,agent_engines]"],
        extra_packages=["docparse_agent"],
        env_vars=RUNTIME_ENV_VARS,
    )

    print(f"\n=== Deployed ===")
    print(f"resource: {remote.resource_name}")
    return remote

if __name__ == "__main__":
    deploy()
