"""Deploy the flash-lite variant of the Option A ADK agent to a NEW
Agent Engine resource (display name `jira-mcp-portal-flashlite`).

Leaves the existing `jira-mcp-portal` AE (gemini-3-flash-preview) untouched
so the user can roll back. Uses the same env-var bundle as the production
deploy script.
"""
import os
import vertexai
import agent_flashlite as agent
from dotenv import load_dotenv
from vertexai.agent_engines import AdkApp


AGENT_ENGINE_NAME = "jira-mcp-portal-flashlite"
STAGING_BUCKET = os.getenv("STAGING_BUCKET", "gs://vtxdemos-staging")

load_dotenv(override=True)


# Use the gcloud-user token (admin@jesusarguelles.altostrat.com via
# GCLOUD_ACCOUNT env var) to avoid the local ADC quota-project trap that
# blocks aiplatform.reasoningEngines.* on this machine.
def _user_credentials():
    import subprocess
    from datetime import datetime, timedelta
    from google.oauth2.credentials import Credentials

    acct = os.environ.get("GCLOUD_ACCOUNT")

    def _fresh_token() -> str:
        args = ["gcloud", "auth", "print-access-token"]
        if acct:
            args += ["--account", acct]
        return subprocess.run(args, capture_output=True, text=True, check=True).stdout.strip()

    class _GcloudCredentials(Credentials):
        def refresh(self, request):  # type: ignore[override]
            self.token = _fresh_token()
            self.expiry = datetime.utcnow() + timedelta(minutes=50)

    creds = _GcloudCredentials(token=_fresh_token())
    creds.expiry = datetime.utcnow() + timedelta(minutes=50)
    return creds


_user_creds = _user_credentials()

vertexai.init(
    project=os.getenv("GOOGLE_CLOUD_PROJECT", "vtxdemos"),
    location=os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1"),
    credentials=_user_creds,
)
client = vertexai.Client(
    project=os.getenv("GOOGLE_CLOUD_PROJECT", "vtxdemos"),
    location=os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1"),
    credentials=_user_creds,
)

deployment_app = AdkApp(
    agent=agent.root_agent,
    enable_tracing=True,
)

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

print(f"Searching for existing Agent Engine: {AGENT_ENGINE_NAME}...")
all_engines = list(client.agent_engines.list())
target_engine = next(
    (e for e in all_engines if e.api_resource.display_name == AGENT_ENGINE_NAME),
    None,
)

_config = {
    "display_name": AGENT_ENGINE_NAME,
    "staging_bucket": STAGING_BUCKET,
    "requirements": "requirements.txt",
    "extra_packages": ["agent_flashlite.py"],
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

print(f"\nRESOURCE_NAME={remote_app.api_resource.name}")
# Extract numeric ID for OPTION_A_FLASHLITE_AGENT_ID
_rid = remote_app.api_resource.name.rsplit("/", 1)[-1]
print(f"RESOURCE_ID={_rid}")
