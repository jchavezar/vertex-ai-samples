import os
from google.genai import Client
from src.agent_definition import root_agent

# Configuration
PROJECT = "vtxdemos"
LOCATION = "us-central1"

def deploy_to_agent_engine():
    """
    Deploys the root_agent to Vertex AI Agent Engine using the 
    genai.Client().agent_engines.create() method for maximum flexibility.
    """
    client = Client(
        vertexai=True,
        project=PROJECT,
        location=LOCATION
    )

    print(f"Deploying agent to Project: {PROJECT}, Location: {LOCATION}...")

    # Define deployment configuration
    # This approach allows for detailed control over the deployment environment
    config = {
        "display_name": "root-agent-engine-test",
        "description": "Deployment of a basic root agent using Google GenAI SDK",
        "requirements": [
            "google-adk",
            "google-genai",
            "pydantic"
        ],
        "env_vars": {
            "GOOGLE_GENAI_USE_VERTEXAI": "true",
            "GOOGLE_CLOUD_PROJECT": PROJECT,
            "GOOGLE_CLOUD_LOCATION": LOCATION
        }
    }

    try:
        # The recommended new way to deploy agents
        remote_agent = client.agent_engines.create(
            agent=root_agent,
            config=config
        )
        
        print(f"✅ Agent successfully deployed!")
        print(f"Agent Engine Resource Name: {remote_agent.name}")
        return remote_agent
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        return None

if __name__ == "__main__":
    deploy_to_agent_engine()
