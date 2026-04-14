# MCP Integration Guide

## Overview

Vertex Cowork supports the Model Context Protocol (MCP) for connecting agents to external tools and resources. MCP provides a standardized way for LLMs to interact with external systems.

## Supported Transports

### 1. STDIO Transport

Run MCP servers as subprocesses. Best for local development and trusted servers.

```json
{
  "server_id": "filesystem",
  "name": "Filesystem Server",
  "transport": "stdio",
  "command": "npx -y @modelcontextprotocol/server-filesystem /path/to/allowed/dir"
}
```

### 2. SSE Transport

Server-Sent Events for real-time streaming. Best for web-based servers.

```json
{
  "server_id": "web-server",
  "name": "Web MCP Server",
  "transport": "sse",
  "url": "http://localhost:3000/mcp/sse"
}
```

### 3. HTTP Transport

Traditional HTTP for request-response patterns.

```json
{
  "server_id": "api-server",
  "name": "API MCP Server",
  "transport": "http",
  "url": "http://localhost:3000/mcp"
}
```

## Common MCP Servers

### Official Servers

| Server | Command | Purpose |
|--------|---------|---------|
| Filesystem | `npx -y @modelcontextprotocol/server-filesystem /path` | File operations |
| GitHub | `npx -y @modelcontextprotocol/server-github` | GitHub API |
| Postgres | `npx -y @modelcontextprotocol/server-postgres` | Database queries |
| Brave Search | `npx -y @modelcontextprotocol/server-brave-search` | Web search |
| Memory | `npx -y @modelcontextprotocol/server-memory` | Persistent memory |

### Custom Servers

Create your own MCP server:

```python
from mcp.server import Server
from mcp.types import Tool, TextContent

server = Server("my-server")

@server.tool()
async def my_tool(query: str) -> str:
    """My custom tool."""
    return f"Result for: {query}"

server.run()
```

## Integration with Agent Frameworks

### ADK Integration

ADK has native MCP support via `McpToolset`:

```python
from google.adk.mcp import McpToolset

# In agent creation
mcp_tools = McpToolset(
    connection_params={
        "command": "npx -y @modelcontextprotocol/server-filesystem /data"
    }
)

agent = LlmAgent(
    name="file-agent",
    model="vertexai/gemini-2.0-flash",
    tools=[mcp_tools],
)
```

### LangGraph Integration

MCP tools are converted to LangChain tools:

```python
# Vertex Cowork automatically converts MCP tools
for mcp_tool in client.get_tools():
    @langchain_tool
    async def tool_func(**kwargs):
        return await mcp_manager.call_tool(server_id, mcp_tool.name, kwargs)
    
    tools.append(tool_func)
```

## API Usage

### Register Server

```bash
curl -X POST http://localhost:8080/api/mcp-servers \
  -H "Content-Type: application/json" \
  -d '{
    "server_id": "my-server",
    "name": "My Server",
    "transport": "stdio",
    "command": "python my_server.py"
  }'
```

### Connect Server

```bash
curl -X POST http://localhost:8080/api/mcp-servers/my-server/connect
```

Response includes discovered tools and resources:

```json
{
  "server_id": "my-server",
  "name": "My Server",
  "transport": "stdio",
  "tools": ["search", "write", "read"],
  "resources": ["file:///data"],
  "connected": true
}
```

### Use in Agent

```bash
curl -X POST http://localhost:8080/api/agents \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "mcp-agent",
    "name": "MCP Agent",
    "model_id": "gemini-2.0-flash",
    "framework": "adk",
    "mcp_servers": ["my-server"]
  }'
```

## Best Practices

### Security

1. **Limit File Access**: Only expose necessary directories
2. **Validate Inputs**: Sanitize all tool arguments
3. **Use Credentials Carefully**: Don't expose API keys to agents
4. **Monitor Usage**: Log all MCP tool calls

### Performance

1. **Connection Pooling**: Reuse MCP connections
2. **Timeout Configuration**: Set appropriate timeouts
3. **Error Handling**: Gracefully handle server failures

### Reliability

1. **Health Checks**: Monitor server availability
2. **Reconnection Logic**: Auto-reconnect on failures
3. **Fallback Tools**: Have alternatives for critical tools

## Troubleshooting

### Server Won't Connect

```bash
# Check if command works directly
npx -y @modelcontextprotocol/server-filesystem /path

# Check permissions
ls -la /path

# Check logs
AGENT_NEXUS_LOG_LEVEL=debug python main.py
```

### Tools Not Discovered

```bash
# Verify tools list endpoint
curl -X POST http://localhost:8080/api/mcp-servers/my-server/connect

# Check server implementation
# Ensure tools/list returns proper format
```

### Tool Calls Failing

```bash
# Enable debug logging
export MCP_DEBUG=true

# Check tool schema matches arguments
# Verify tool implementation handles all cases
```
