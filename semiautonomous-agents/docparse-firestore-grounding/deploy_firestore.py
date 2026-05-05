"""Deploy Firestore agent to vtxdemos Agent Engine."""
import os
from pathlib import Path
import vertexai
from vertexai import agent_engines
from vertexai.preview import reasoning_engines

PROJECT_ID = "sharepoint-wif"
LOCATION = "us-central1"
STAGING_BUCKET = "gs://sharepoint-wif-agent-staging"

RUNTIME_ENV_VARS = {
    "GOOGLE_CLOUD_LOCATION": "global",
    "GOOGLE_GENAI_USE_VERTEXAI": "true",
    "GOOGLE_CLOUD_PROJECT": "sharepoint-wif",
    "FIRESTORE_COLLECTION": "docparse_chunks",
    "AGENT_MODEL": "gemini-2.5-flash",
    "AGENT_TOP_K": "20",
}

def deploy():
    print(f"\n=== Deploying Firestore agent → {PROJECT_ID} ===")

    vertexai.init(project=PROJECT_ID, location=LOCATION, staging_bucket=STAGING_BUCKET)

    from firestore_agent import root_agent

    app = reasoning_engines.AdkApp(agent=root_agent, enable_tracing=True)

    remote = agent_engines.create(
        agent_engine=app,
        display_name="docparse-firestore",
        description="Firestore + PDF grounding, text-embedding-005, gemini-2.5-flash",
        requirements=["google-cloud-aiplatform[adk,agent_engines]", "google-cloud-firestore", "google-genai", "requests"],
        extra_packages=["firestore_agent"],
        env_vars=RUNTIME_ENV_VARS,
    )

    print(f"\n=== Deployed ===")
    print(f"Resource: {remote.resource_name}")
    return remote

if __name__ == "__main__":
    deploy()
