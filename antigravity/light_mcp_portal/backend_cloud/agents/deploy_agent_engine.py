import asyncio
from typing import Union, Any
from dotenv import load_dotenv
import os
import vertexai
import agent
from vertexai.agent_engines import AdkApp
import importlib

# --- CONFIGURATION ---
AGENT_ENGINE_NAME = "servicenow_mcp_agent_prod"
STAGING_BUCKET = "gs://vtxdemoslab-vtxdemos-unique" # Using a bucket in vtxdemos project

importlib.reload(agent)
load_dotenv(override=True)

# Initialize Vertex AI SDK
vertexai.init(
    project=os.getenv("GOOGLE_CLOUD_PROJECT"),
    location="us-central1",
)
client = vertexai.Client(
    project=os.getenv("GOOGLE_CLOUD_PROJECT"),
    location="us-central1",
)

# Wrap the formally exported root_agent
deployment_app = AdkApp(
    agent=agent.root_agent,
    enable_tracing=True,
)

# Ensure env_vars is defined
env_vars = {
    "SERVICENOW_MCP_URL": os.getenv("SERVICENOW_MCP_URL", "https://servicenow-mcp-prod-254356041555.us-central1.run.app/sse")
}

# We use create to make a NEW engine, as the old one is missing or invalid
remote_app = client.agent_engines.create(
    agent=deployment_app,
    config={
        "display_name": AGENT_ENGINE_NAME,
        "staging_bucket": STAGING_BUCKET,
        "requirements": "requirements.txt",
        "extra_packages": ["agent.py"],
        "env_vars": env_vars
    }
)
print(f"Deployment complete: {remote_app.api_resource.name}")

if __name__ == "__main__":
    print(f"\n✅ Successfully synced {AGENT_ENGINE_NAME} to Vertex AI Agent Engine.")
    print(f"Run backend_cloud/main.py with AGENT_ENGINE_ID={remote_app.api_resource.name} to connect.")
