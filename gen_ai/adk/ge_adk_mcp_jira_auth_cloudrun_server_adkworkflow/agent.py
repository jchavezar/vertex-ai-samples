import os
import sys
from google.adk.agents import Agent
from google.adk.auth.auth_schemes import OAuth2, OAuthFlows
from fastapi.openapi.models import OAuthFlowAuthorizationCode
from google.adk.auth.auth_credential import AuthCredential, AuthCredentialTypes, OAuth2Auth
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset, SseConnectionParams
from google.adk.agents.readonly_context import ReadonlyContext
from dotenv import load_dotenv

load_dotenv(verbose=True)

AGENTSPACE_AUTH_ID = "jira-auth-mcp_1764305083858"

auth_scheme = OAuth2(
    flows=OAuthFlows(
        authorizationCode=OAuthFlowAuthorizationCode(
            authorizationUrl="https://auth.atlassian.com/authorize",
            tokenUrl="https://auth.atlassian.com/oauth/token",
            scopes={
                "read:jira-work": "View Jira Issues",
                "read:jira-user": "View Jira Users",
                "write:jira-work": "Create and Edit Jira Issues",
                "offline_access": "Auth",
            },
        )
    )
)

auth_credential = AuthCredential(
    auth_type=AuthCredentialTypes.OPEN_ID_CONNECT,
    oauth2=OAuth2Auth(
        client_id=os.getenv("ATLASSIAN_CLIENT_ID"),
        client_secret=os.getenv("ATLASSIAN_CLIENT_SECRET"),
    )
)

def explicit_logger(msg):
    print(f"[MCP LOG] {msg}", file=sys.stdout)

def get_access_token(readonly_context: ReadonlyContext, auth_id: str) -> str | None:
    if hasattr(readonly_context, "session") and hasattr(readonly_context.session, "state"):
        session_state = dict(readonly_context.session.state)
        for key, value in session_state.items():
            if key.startswith(auth_id) and isinstance(value, str) and len(value) > 20:
                return value
    return None

def mcp_header_provider(readonly_context: ReadonlyContext) -> dict[str, str]:
    token = get_access_token(readonly_context, AGENTSPACE_AUTH_ID)

    if token:
        clean_token = token.strip()
        explicit_logger(f"[DEBUG] Found Session Token! Using it. ({clean_token[:6]}...)")
        return {
            "Authorization": f"Bearer {clean_token}",
            "Accept": "text/event-stream",
            "Cache-Control": "no-cache"
        }

    explicit_logger("[DEBUG] No Session Token found. Falling back to Auth Scheme (Popup).")
    return {}

jira_toolset = McpToolset(
    connection_params=SseConnectionParams(
        url="https://jira-mcp-server-254356041555.us-central1.run.app/sse",
        timeout=60,
    ),
    header_provider=mcp_header_provider,
    auth_scheme=auth_scheme,
    auth_credential=auth_credential,

    errlog=explicit_logger
)

root_agent = Agent(
    name="root_agent",
    model="gemini-2.5-flash",
    description="Jira issue tracker",
    instruction="""Always use your available Jira tools to find sales/offers""",
    tools=[jira_toolset]
)