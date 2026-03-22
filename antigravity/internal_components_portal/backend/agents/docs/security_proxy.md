# Security Proxy Agent

The primary workhorse for internal enterprise search, gated heavily by the Zero-Leak Governance protocol and the strict enterprise authentication middleware.

## The Objective
This agent relies on the official Model Context Protocol (MCP) to query private SharePoint data. It enforces mandatory data generalizations (numerical fuzzing, entity masking) and aggressively blocks unauthenticated requests via runtime interception.

## Key Logic Snippets

Located in [`agent.py`](../agent.py).

**1. Enterprise Tool Discovery (MCP)**
The agent discovers enterprise capabilities strictly through an active, isolated MCP subprocess spawned dynamically via `uv run` per interaction to guarantee no handle leaks.

```python
    params = mcp_tool.StdioConnectionParams(
        server_params={
            "command": "uv",
            "args": ["run", "python", "-m", "mcp_service.mcp_server"],
            "env": env
        }
    )
    toolset = mcp_tool.McpToolset(connection_params=params)
    mcp_tools = await toolset.get_tools()
```

**2. Multi-Layer Auth Guardians**
We apply interception decorators over the discovered MCP tools *and* provide a `before_agent_callback` to actively reject execution traces if current identity assertions fail.

```python
    async def before_agent_auth_callback(callback_context: CallbackContext) -> types.Content | None:
        current_token = token or get_user_token()
        if not current_token or current_token in ["null", "undefined", "None"]:
            return types.Content(
                role="model",
                parts=[types.Part.from_text(text="🔒 **Access Restricted**: You are currently not signed in.")]
            )
        return None
```

**3. Advanced Reasoning Planners**
Uses ADK's `BuiltInPlanner` tuned with an optimized thinking budget (1024) tailored specially for Flash versions. This forces the model to methodically map out what data is safe to reveal *before* generating output.

```python
    planner = BuiltInPlanner(
        thinking_config=ThinkingConfig(
            include_thoughts=True,
            thinking_budget=1024
        )
    )
```
