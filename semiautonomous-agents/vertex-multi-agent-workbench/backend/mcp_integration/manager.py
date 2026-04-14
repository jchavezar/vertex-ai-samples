"""MCP Server Manager for handling multiple MCP connections."""

from typing import Any

import logging

from core.registry import MCPServerRegistry, MCPServerInfo
from mcp_integration.client import MCPClient

logger = logging.getLogger(__name__)


class MCPManager:
    """Manages multiple MCP server connections."""

    def __init__(self, registry: MCPServerRegistry) -> None:
        self.registry = registry
        self._clients: dict[str, MCPClient] = {}

    async def connect_server(self, server_id: str) -> MCPClient:
        """Connect to an MCP server by ID."""
        if server_id in self._clients:
            return self._clients[server_id]

        server_info = self.registry.get(server_id)
        if not server_info:
            raise ValueError(f"MCP server '{server_id}' not found in registry")

        client = MCPClient(
            server_id=server_info.server_id,
            transport=server_info.transport,
            command=server_info.command,
            url=server_info.url,
            env=server_info.config.get("env", {}),
        )

        await client.connect()
        self._clients[server_id] = client

        # Update registry with discovered tools
        server_info.tools = [t.name for t in client.get_tools()]
        server_info.resources = [r.uri for r in client.get_resources()]

        return client

    async def disconnect_server(self, server_id: str) -> None:
        """Disconnect from an MCP server."""
        if server_id in self._clients:
            await self._clients[server_id].disconnect()
            del self._clients[server_id]

    async def disconnect_all(self) -> None:
        """Disconnect from all MCP servers."""
        for server_id in list(self._clients.keys()):
            await self.disconnect_server(server_id)

    def get_client(self, server_id: str) -> MCPClient | None:
        """Get an existing client connection."""
        return self._clients.get(server_id)

    def list_connected_servers(self) -> list[str]:
        """List all connected server IDs."""
        return list(self._clients.keys())

    def register_server(
        self,
        server_id: str,
        name: str,
        transport: str,
        command: str | None = None,
        url: str | None = None,
        config: dict[str, Any] | None = None,
    ) -> MCPServerInfo:
        """Register a new MCP server."""
        server_info = MCPServerInfo(
            server_id=server_id,
            name=name,
            transport=transport,
            command=command,
            url=url,
            config=config or {},
        )
        self.registry.register(server_info)
        return server_info

    async def call_tool(
        self,
        server_id: str,
        tool_name: str,
        arguments: dict[str, Any],
    ) -> Any:
        """Call a tool on a specific MCP server."""
        client = self._clients.get(server_id)
        if not client:
            client = await self.connect_server(server_id)

        return await client.call_tool(tool_name, arguments)

    def get_all_tools(self) -> dict[str, list[dict[str, Any]]]:
        """Get all tools from all connected servers."""
        return {
            server_id: client.get_tools_for_langgraph()
            for server_id, client in self._clients.items()
        }
