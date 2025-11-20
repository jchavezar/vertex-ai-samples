import asyncio
import os
import concurrent.futures # <--- 1. Add this import
from mcp import StdioServerParameters
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioConnectionParams
from google.adk.auth.auth_schemes import OpenIdConnectWithConfig
from google.adk.auth.auth_credential import AuthCredential, AuthCredentialTypes, OAuth2Auth
from google.adk.tools.openapi_tool.openapi_spec_parser.openapi_toolset import OpenAPIToolset

# --- CONFIGURATION ---
auth_scheme = OpenIdConnectWithConfig(
    authorization_endpoint="https://auth.atlassian.com/authorize",
    token_endpoint="https://auth.atlassian.com/oauth/token",
    scopes=[
        "read:content:confluence",
        "read:page:confluence",
        "read:space:confluence",
        "read:content.metadata:confluence",
        "offline_access"
    ]
)

auth_credential = AuthCredential(
    auth_type=AuthCredentialTypes.OAUTH2,
    oauth2=OAuth2Auth(
        client_id="",
        client_secret="",
    )
)

spec_path = os.path.join(os.path.dirname(__file__), 'confluence_spec.yaml')
with open(spec_path, 'r') as f:
    spec_content = f.read()

confluence_toolset = OpenAPIToolset(
    spec_str=spec_content,
    spec_str_type='yaml',
    auth_scheme=auth_scheme,
    auth_credential=auth_credential,
)

# --- 2. THE FIX: Load tools in a separate thread to bypass uvloop ---
def get_tools_worker():
    # This runs in a separate thread where we can safely create a new loop
    return asyncio.run(confluence_toolset.get_tools())

with concurrent.futures.ThreadPoolExecutor() as executor:
    confluence_tools_list = executor.submit(get_tools_worker).result()

# --- AGENTS SETUP ---
list_files_agent = LlmAgent(
    name="list_files_agent",
    model="gemini-2.5-flash",
    instruction="Use your tool to list directories (use the path of `directory_name`) and read files in it, use pretty output.",
    tools=[
        MCPToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command="npx",
                    args=[
                        "-y",
                        "@modelcontextprotocol/server-filesystem",
                        "/Users/jesusarguelles/Downloads"
                    ]
                )
            )
        )
    ]
)

confluence_agent = LlmAgent(
    name="confluence_agent",
    model="gemini-2.5-flash",
    instruction="""
    You are a Confluence expert. 
    1. Use `get_all_pages` to list pages.
    2. Once you receive the list of pages, output the list immediately.
    3. Do NOT call the tool a second time.
    4. Transfer control back to the root_agent.""",
    tools=confluence_tools_list
)

root_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="root_agent",
    description="A helpful assistant for user questions.",
    instruction="""
    You are a helpful assistant.
    - If the user asks about files, use `list_files_agent`.
    - If the user asks about Confluence/Pages/Docs, use `confluence_agent`.
    - When the sub-agent returns the info, show it to the user and STOP.
    """,
    sub_agents=[list_files_agent, confluence_agent],
    output_key="directory_name"
)