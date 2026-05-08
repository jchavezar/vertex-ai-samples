#%%
import asyncio
from typing import Union, Any

from dotenv import load_dotenv
import os
import vertexai
import agent
from vertexai.agent_engines import AdkApp
import importlib

# --- CONFIGURATION ---
# The display name for the Agent Engine in Vertex AI
AGENT_ENGINE_NAME = "jira-mcp-portal"
STAGING_BUCKET = os.getenv(
    "STAGING_BUCKET", "gs://sharepoint-wif-agent-staging"
)

#%%
importlib.reload(agent)

load_dotenv(override=True)

# Initialize Vertex AI SDK
vertexai.init(
    project=os.getenv("GOOGLE_CLOUD_PROJECT"),
    location=os.getenv("GOOGLE_CLOUD_LOCATION"),
)
client = vertexai.Client(
    project=os.getenv("GOOGLE_CLOUD_PROJECT"),
    location=os.getenv("GOOGLE_CLOUD_LOCATION"),
)

# Wrap the agent from agent.py
deployment_app = AdkApp(
    agent=agent.root_agent,
    enable_tracing=True,
)

#%%
# Two auth paths the agent supports:
# 1. Per-user OAuth in production GE chats — GE injects token into session state.
# 2. Atlassian API token (Basic auth) for headless/eval — permanent, no refresh
#    chain, doesn't conflict with OAuth. Set ATLASSIAN_EMAIL +
#    ATLASSIAN_API_TOKEN + ATLASSIAN_SITE_URL in .env.
_env_vars = {}
for _k in (
    "MCP_SERVER_URL",
    "AGENTSPACE_AUTH_ID",
    "ATLASSIAN_CLIENT_ID",
    "ATLASSIAN_CLIENT_SECRET",
    "ATLASSIAN_EMAIL",
    "ATLASSIAN_API_TOKEN",
    "ATLASSIAN_SITE_URL",
):
    _v = os.environ.get(_k)
    if _v:
        _env_vars[_k] = _v
print(f"Env vars on AE: {sorted(_env_vars.keys())}")

# Automatic Deployment (Update or Create)
print(f"Searching for existing Agent Engine: {AGENT_ENGINE_NAME}...")
all_engines = list(client.agent_engines.list())
target_engine = next((e for e in all_engines if e.api_resource.display_name == AGENT_ENGINE_NAME), None)

_config = {
    "display_name": AGENT_ENGINE_NAME,
    "staging_bucket": STAGING_BUCKET,
    "requirements": "requirements.txt",
    "extra_packages": ["agent.py"],
    "env_vars": _env_vars,
}

if target_engine:
    print(f"Found existing engine: {target_engine.api_resource.name}. Updating...")
    remote_app = client.agent_engines.update(
        name=target_engine.api_resource.name,
        agent=deployment_app,
        config=_config,
    )
    print(f"Update complete: {remote_app.api_resource.name}")
else:
    print("No existing engine found. Creating new one...")
    remote_app = client.agent_engines.create(
        agent=deployment_app,
        config=_config,
    )
    print(f"Creation complete: {remote_app.api_resource.name}")


#%%
async def send_message(prompt: str, app: Union[vertexai.agent_engines.AdkApp, Any]):
    session = await app.async_create_session(user_id="jesus_c")
    async for event in app.async_stream_query(
            user_id="jesus_c",
            session_id=session["id"] if "id" in session else session.id,
            message=prompt,
    ):
        print(event)

if __name__ == "__main__":
    # Example usage:
    # asyncio.run(send_message("how many jira issues related to colors are there?, give me a summary and the issue number", app=remote_app))
    pass
