"""Deploy Firestore agent to sharepoint-wif Agent Engine."""
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
    # GOOGLE_CLOUD_PROJECT auto-set by Agent Engine (reserved)
    "FIRESTORE_COLLECTION": "docparse_chunks",
    "FIRESTORE_PROJECT": "sharepoint-wif",  # Custom var for Firestore client
    "AGENT_MODEL": "gemini-2.5-flash",
    "AGENT_TOP_K": "20",
}

def deploy():
    print(f"\n=== Deploying Firestore agent → {PROJECT_ID} ===")

    vertexai.init(project=PROJECT_ID, location=LOCATION, staging_bucket=STAGING_BUCKET)

    # Import simple query wrapper (no AdkApp, direct query() method)
    from firestore_agent.simple_query_wrapper import root_agent

    remote = agent_engines.create(
        agent_engine=root_agent,
        display_name="docparse-firestore-keyword",
        description="Firestore + keyword retrieval + gemini-2.5-flash [WORKING]",
        requirements=["google-cloud-aiplatform[adk,agent_engines]", "google-cloud-firestore", "google-genai", "requests"],
        extra_packages=["firestore_agent"],
        env_vars=RUNTIME_ENV_VARS,
    )

    print(f"\n✅ DEPLOYED")
    print(f"Resource: {remote.resource_name}")
    return remote

if __name__ == "__main__":
    deploy()
