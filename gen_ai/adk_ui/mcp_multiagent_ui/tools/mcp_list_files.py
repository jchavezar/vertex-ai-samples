import os
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

list_files_tool = MCPToolset(
    connection_params=StdioConnectionParams(
        server_params = StdioServerParameters(
            command='npx',
            args=[
                "-y",  # Argument for npx to auto-confirm install
                "@modelcontextprotocol/server-filesystem",
                # IMPORTANT: This MUST be an ABSOLUTE path to a folder the
                # npx process can access.
                # Replace with a valid absolute path on your system.
                # For example: "/Users/youruser/accessible_mcp_files"
                # or use a dynamically constructed absolute path:
                "/Users/jesusarguelles/Downloads",
            ],
        ),
    ),
    # Optional: Filter which tools from the MCP server are exposed
    # tool_filter=['list_directory', 'read_file']
)