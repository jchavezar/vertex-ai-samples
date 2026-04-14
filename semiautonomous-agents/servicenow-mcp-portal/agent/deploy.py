"""
Deploy ServiceNow Agent to Vertex AI Agent Engine.
Run this once to deploy/update the agent.

Usage:
    python deploy.py
"""
import os
import importlib
from dotenv import load_dotenv
import vertexai
from vertexai.agent_engines import AdkApp

# Load environment
load_dotenv(override=True)

# Configuration
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "deloitte-plantas")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
STAGING_BUCKET = os.getenv("STAGING_BUCKET", f"gs://{PROJECT_ID}-staging")
AGENT_ENGINE_NAME = os.getenv("AGENT_ENGINE_NAME", "servicenow-light-mcp-agent")

# MCP Server URL (must be deployed first)
MCP_URL = os.getenv("SERVICENOW_MCP_URL", "")

print(f"""
========================================
Agent Engine Deployment
========================================
Project:        {PROJECT_ID}
Location:       {LOCATION}
Agent Name:     {AGENT_ENGINE_NAME}
Staging Bucket: {STAGING_BUCKET}
MCP Server URL: {MCP_URL}
========================================
""")

if not MCP_URL:
    print("WARNING: SERVICENOW_MCP_URL not set. Deploy MCP server first!")
    print("The agent will use the default URL in agent.py")

# Initialize Vertex AI
vertexai.init(project=PROJECT_ID, location=LOCATION)

# Import and reload agent module
import agent
importlib.reload(agent)

# Create client
client = vertexai.Client(project=PROJECT_ID, location=LOCATION)

# Wrap the agent
deployment_app = AdkApp(
    agent=agent.root_agent,
    enable_tracing=True,
)

# Check for existing engine
print(f"Searching for existing Agent Engine: {AGENT_ENGINE_NAME}...")
all_engines = list(client.agent_engines.list())
target_engine = next(
    (e for e in all_engines if e.api_resource.display_name == AGENT_ENGINE_NAME),
    None
)

# Get project number for service account
import subprocess
project_number = subprocess.run(
    ["gcloud", "projects", "describe", PROJECT_ID, "--format=value(projectNumber)"],
    capture_output=True, text=True
).stdout.strip()
SERVICE_ACCOUNT = f"{project_number}-compute@developer.gserviceaccount.com"
print(f"Using service account: {SERVICE_ACCOUNT}")

# Deploy configuration
deploy_config = {
    "display_name": AGENT_ENGINE_NAME,
    "staging_bucket": STAGING_BUCKET,
    "requirements": "requirements.txt",
    "extra_packages": ["agent.py"],
    "env_vars": {
        "SERVICENOW_MCP_URL": MCP_URL,
    },
    "service_account": SERVICE_ACCOUNT,  # Use compute SA for Cloud Run auth
}

if target_engine:
    print(f"Found existing engine: {target_engine.api_resource.name}. Updating...")
    remote_app = client.agent_engines.update(
        name=target_engine.api_resource.name,
        agent=deployment_app,
        config=deploy_config
    )
    print(f"Update complete: {remote_app.api_resource.name}")
else:
    print("No existing engine found. Creating new one...")
    remote_app = client.agent_engines.create(
        agent=deployment_app,
        config=deploy_config
    )
    print(f"Creation complete: {remote_app.api_resource.name}")

# Extract resource ID
resource_name = remote_app.api_resource.name
resource_id = resource_name.split("/")[-1]

print(f"""
========================================
Deployment Complete!
========================================
Resource Name: {resource_name}
Resource ID:   {resource_id}

Add this to your backend .env:
AGENT_ENGINE_ID={resource_id}

Test with:
curl -X POST https://{LOCATION}-aiplatform.googleapis.com/v1/{resource_name}:query \\
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \\
  -H "Content-Type: application/json" \\
  -d '{{"class_method": "async_create_session", "input": {{"user_id": "test"}}}}'
========================================
""")

# Save to .env file
env_path = os.path.join(os.path.dirname(__file__), "..", "backend", ".env")
try:
    with open(env_path, "a") as f:
        f.write(f"\n# Deployed {AGENT_ENGINE_NAME}\n")
        f.write(f"AGENT_ENGINE_ID={resource_id}\n")
    print(f"Added AGENT_ENGINE_ID to {env_path}")
except Exception as e:
    print(f"Could not update .env: {e}")
