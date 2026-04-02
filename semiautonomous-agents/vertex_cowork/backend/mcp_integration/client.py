"""MCP client for connecting to MCP servers using official SDK."""

import asyncio
import os
from dataclasses import dataclass
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import httpx
import logging

logger = logging.getLogger(__name__)


@dataclass
class MCPTool:
    """Represents an MCP tool."""

    name: str
    description: str
    input_schema: dict[str, Any]


@dataclass
class MCPResource:
    """Represents an MCP resource."""

    uri: str
    name: str
    description: str
    mime_type: str | None = None


class MCPClient:
    """Client for connecting to MCP servers using official SDK."""

    def __init__(
        self,
        server_id: str,
        transport: str,
        command: str | None = None,
        url: str | None = None,
        env: dict[str, str] | None = None,
    ) -> None:
        self.server_id = server_id
        self.transport = transport
        self.command = command
        self.url = url
        self.env = env or {}
        self._session: ClientSession | None = None
        self._http_client: httpx.AsyncClient | None = None
        self._tools: list[MCPTool] = []
        self._resources: list[MCPResource] = []
        self._connected = False
        self._stdio_context = None
        self._session_context = None

    async def connect(self) -> None:
        """Connect to the MCP server."""
        if self.transport == "stdio":
            await self._connect_stdio()
        elif self.transport in ("sse", "http"):
            await self._connect_http()
        else:
            raise ValueError(f"Unsupported transport: {self.transport}")

        self._connected = True
        logger.info(f"MCP client connected: {self.server_id}")

    async def _connect_stdio(self) -> None:
        """Connect via stdio transport using official SDK."""
        if not self.command:
            raise ValueError("Command required for stdio transport")

        # Merge with current environment (needed for PATH, etc.)
        process_env = os.environ.copy()
        process_env.update(self.env)

        cmd_parts = self.command.split()
        logger.info(f"Starting MCP server: {cmd_parts}")

        # Create server parameters
        server_params = StdioServerParameters(
            command=cmd_parts[0],
            args=cmd_parts[1:] if len(cmd_parts) > 1 else [],
            env=process_env,
        )

        # Create and enter the stdio client context
        self._stdio_context = stdio_client(server_params)
        read, write = await self._stdio_context.__aenter__()

        # Create and enter the session context
        self._session_context = ClientSession(read, write)
        self._session = await self._session_context.__aenter__()

        # Initialize the session
        await self._session.initialize()

        # Refresh tools and resources
        await self._refresh_capabilities()

    async def _connect_http(self) -> None:
        """Connect via HTTP/SSE transport."""
        if not self.url:
            raise ValueError("URL required for HTTP transport")

        # HTTP/SSE support would need additional implementation
        # For now, mark as connected with no tools
        self._http_client = httpx.AsyncClient(base_url=self.url, timeout=30.0)
        logger.warning(f"HTTP transport for MCP not fully implemented yet: {self.server_id}")

    async def _refresh_capabilities(self) -> None:
        """Refresh the list of tools and resources from the server."""
        if not self._session:
            return

        # Get tools
        tools_result = await self._session.list_tools()
        self._tools = [
            MCPTool(
                name=t.name,
                description=t.description or "",
                input_schema=t.inputSchema if hasattr(t, "inputSchema") else {},
            )
            for t in tools_result.tools
        ]

        # Get resources (may not be supported by all servers)
        try:
            resources_result = await self._session.list_resources()
            self._resources = [
                MCPResource(
                    uri=str(r.uri),
                    name=r.name,
                    description=r.description or "",
                    mime_type=r.mimeType if hasattr(r, "mimeType") else None,
                )
                for r in resources_result.resources
            ]
        except Exception as e:
            logger.debug(f"Resources not supported by {self.server_id}: {e}")
            self._resources = []

        logger.info(f"MCP capabilities: {self.server_id} - {len(self._tools)} tools, {len(self._resources)} resources")

    async def call_tool(self, tool_name: str, arguments: dict[str, Any]) -> Any:
        """Call a tool on the MCP server."""
        if not self._connected or not self._session:
            raise RuntimeError("Not connected to MCP server")

        result = await self._session.call_tool(tool_name, arguments)
        logger.info(f"MCP tool called: {self.server_id}/{tool_name}")
        return result

    async def read_resource(self, uri: str) -> Any:
        """Read a resource from the MCP server."""
        if not self._connected or not self._session:
            raise RuntimeError("Not connected to MCP server")

        result = await self._session.read_resource(uri)
        return result

    def get_tools(self) -> list[MCPTool]:
        """Get available tools."""
        return self._tools

    def get_resources(self) -> list[MCPResource]:
        """Get available resources."""
        return self._resources

    def get_tools_for_adk(self) -> list[dict[str, Any]]:
        """Get tools in ADK-compatible format."""
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.input_schema,
            }
            for tool in self._tools
        ]

    def get_tools_for_langgraph(self) -> list[dict[str, Any]]:
        """Get tools in LangGraph-compatible format."""
        return [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.input_schema,
                },
            }
            for tool in self._tools
        ]

    async def disconnect(self) -> None:
        """Disconnect from the MCP server."""
        if self._session_context:
            try:
                await self._session_context.__aexit__(None, None, None)
            except Exception as e:
                logger.debug(f"Error closing session: {e}")
            self._session_context = None
            self._session = None

        if self._stdio_context:
            try:
                await self._stdio_context.__aexit__(None, None, None)
            except Exception as e:
                logger.debug(f"Error closing stdio: {e}")
            self._stdio_context = None

        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None

        self._connected = False
        logger.info(f"MCP client disconnected: {self.server_id}")
