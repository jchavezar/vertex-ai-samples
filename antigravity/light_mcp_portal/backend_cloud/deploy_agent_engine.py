import os
import vertexai
from vertexai.preview import reasoning_engines
from agents.agent import root_agent

# Initialize Vertex AI
PROJECT_ID = os.environ.get("PROJECT_ID", "vtxdemos")
LOCATION = os.environ.get("LOCATION", "us-central1")

print(f"Initializing Vertex AI for project {PROJECT_ID} and location {LOCATION}...")
vertexai.init(project=PROJECT_ID, location=LOCATION)

# Hardcoded fallback for ServiceNow MCP URL
SERVICENOW_MCP_URL = "https://servicenow-mcp-prod-254356041555.us-central1.run.app"

print(f"Deploying root_agent to Reasoning Engine...")
print(f"Using SERVICENOW_MCP_URL: {SERVICENOW_MCP_URL}")

try:
    # Use the root_agent from agents/agent.py
    remote_app = reasoning_engines.ReasoningEngine.create(
        root_agent,
        display_name="ge_adk_portal_router_fresh",
        requirements=[
            "google-adk[voice]",
            "fastmcp",
            "requests",
            "pytest",
        ],
        extra_packages=[
            "agents", # Include the agents package
        ],
    )

    print("\n✅ Reasoning Engine deployed successfully!")
    print(f"Resource Name: {remote_app.resource_name}")
    print(f"Display Name: {remote_app.display_name}")
    
    # Update .env file
    env_path = "../.env"
    if os.path.exists(env_path):
        print(f"Updating {env_path} with new AGENT_ENGINE_ID...")
        with open(env_path, "r") as f:
            lines = f.readlines()
        
        with open(env_path, "w") as f:
            found = False
            for line in lines:
                if line.startswith("AGENT_ENGINE_ID="):
                    f.write(f"AGENT_ENGINE_ID={remote_app.resource_name}\n")
                    found = True
                else:
                    f.write(line)
            if not found:
                f.write(f"\nAGENT_ENGINE_ID={remote_app.resource_name}\n")
    else:
        print(f"Creating {env_path} with AGENT_ENGINE_ID...")
        with open(env_path, "w") as f:
            f.write(f"AGENT_ENGINE_ID={remote_app.resource_name}\n")

except Exception as e:
    print(f"\n❌ Deployment failed: {e}")
