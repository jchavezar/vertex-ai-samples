import os
import importlib
from dotenv import load_dotenv
import vertexai
from vertexai.agent_engines import AdkApp

# Load environment from parent directory if needed
load_dotenv(dotenv_path="../.env", override=True)

# Configuration
PROJECT_ID = "vtxdemos"
LOCATION = "us-central1"
STAGING_BUCKET = "gs://vtxdemos_staging"
AGENT_ENGINE_NAME = os.getenv("AGENT_ENGINE_NAME", "sharepoint-hosted-mcp-explorer-agent")
MCP_URL = os.getenv("SHAREPOINT_MCP_URL", "https://agent365.svc.cloud.microsoft/agents/servers/mcp_SharePointRemoteServer")

print(f"""
========================================
Agent Engine Deployment - Hosted SharePoint Agent
========================================
Project:           {PROJECT_ID}
Location:          {LOCATION}
Agent Name:        {AGENT_ENGINE_NAME}
Staging Bucket:    {STAGING_BUCKET}
MCP URL:           {MCP_URL}
========================================
""")

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
        "GOOGLE_CLOUD_LOCATION": "global",
        "GOOGLE_GENAI_USE_VERTEXAI": "true",
        "SHAREPOINT_MCP_URL": MCP_URL,
        "PROJECT_NUMBER": project_number,
    },
    "service_account": SERVICE_ACCOUNT,
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
========================================
""")
