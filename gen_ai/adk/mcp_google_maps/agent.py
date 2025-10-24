import os
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

google_maps_api_key = os.environ.get("GOOGLE_MAPS_API_KEY")

# noinspection PyTypeChecker
root_agent = LlmAgent(
    name="root_agent",
    model="gemini-2.5-flash",
    description="""
    You are a helpful assistant that can provide information about locations,
    directions, and points of interest using Google Maps data.
    Use your MCPToolset to access Google Maps functionalities.
    """,
    instruction="""
    Help the user with mapping, directions, and finding places using Google Maps tools.
    """,
    tools=[
        MCPToolset(
            connection_params=StdioConnectionParams(
                server_params = StdioServerParameters(
                    command='npx',
                    args=[
                        "-y",
                       "@modelcontextprotocol/server-google-maps",
                    ],
                    env={
                        "GOOGLE_MAPS_API_KEY": google_maps_api_key
                   }
               ),
           ),
      )
  ],
)