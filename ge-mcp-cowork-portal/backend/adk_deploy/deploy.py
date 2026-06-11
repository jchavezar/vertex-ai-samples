import os
import importlib
import sys
import subprocess
from dotenv import load_dotenv
import vertexai
from vertexai.agent_engines import AdkApp

# Add current folder to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables manually
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".env")
load_dotenv(dotenv_path=env_path, override=True)

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "vtxdemos")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
if LOCATION == "global":
    # Agent Engine deployments run inside us-central1 (default Location for Reasoning Engine)
    # but the model location override is handled via the env var GOOGLE_CLOUD_LOCATION.
    LOCATION = "us-central1"
    
STAGING_BUCKET = "gs://vtxdemos_staging"
AGENT_ENGINE_NAME = "jira-mcp-agent-engine"

# Load Atlassian settings
JIRA_URL = os.getenv("JIRA_MCP_URL", "https://jira-mcp-server-254356041555.us-central1.run.app/mcp")
email = os.getenv("ATLASSIAN_EMAIL", "")
token = os.getenv("ATLASSIAN_API_TOKEN", "")
site_url = os.getenv("ATLASSIAN_SITE_URL", "")

print(f"""
========================================
Agent Engine Deployment - Jira Agent
========================================
Project:           {PROJECT_ID}
Location:          {LOCATION}
Agent Name:        {AGENT_ENGINE_NAME}
Staging Bucket:    {STAGING_BUCKET}
========================================
""")

# Initialize Vertex AI
vertexai.init(project=PROJECT_ID, location=LOCATION)

# Import agent
import agent
importlib.reload(agent)

# Create client
client = vertexai.Client(project=PROJECT_ID, location=LOCATION)

# Wrap agent
deployment_app = AdkApp(
    agent=agent.root_agent,
    enable_tracing=True,
    app_name=AGENT_ENGINE_NAME
)

# Search for existing engine
print(f"Searching for existing Agent Engine: {AGENT_ENGINE_NAME}...")
all_engines = list(client.agent_engines.list())
target_engine = next(
    (e for e in all_engines if e.api_resource.display_name == AGENT_ENGINE_NAME),
    None
)

# Get project number
project_number = subprocess.run(
    ["gcloud", "projects", "describe", PROJECT_ID, "--format=value(projectNumber)"],
    capture_output=True, text=True
).stdout.strip()
SERVICE_ACCOUNT = f"{project_number}-compute@developer.gserviceaccount.com"

# Deploy configuration
deploy_config = {
    "display_name": AGENT_ENGINE_NAME,
    "staging_bucket": STAGING_BUCKET,
    "requirements": "requirements.txt",
    "extra_packages": ["agent.py"],
    "env_vars": {
        "GOOGLE_CLOUD_LOCATION": "global", # route models to global region
        "GOOGLE_GENAI_USE_VERTEXAI": "true",
        "JIRA_MCP_URL": JIRA_URL,
        "ATLASSIAN_EMAIL": email,
        "ATLASSIAN_API_TOKEN": token,
        "ATLASSIAN_SITE_URL": site_url,
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

print(f"\nResource ID: {remote_app.api_resource.name.split('/')[-1]}")
