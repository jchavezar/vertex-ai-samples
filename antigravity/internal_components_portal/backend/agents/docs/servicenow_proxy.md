# ServiceNow Proxy Agent

A highly specialized ADK `LlmAgent` designed to manage infrastructure, reporting, and issue escalation natively within the ServiceNow enterprise ecosystem. 

## The Objective
This agent relies on the `servicenow_mcp` server. It requires strict validation from the user before executing destructive or additive actions (like creating or modifying tickets). It is also capable of self-healing or extrapolating technical data by combining its strict ticketing skills with public knowledge `google_search` tool dynamically.

## Key Logic Snippets

Located in [`agent.py`](../agent.py).

**1. Contextual Routing Trigger**
The router agent activates this proxy when it identifies intent keywords: `"ServiceNow"`, `"incident"`, `"ticket"`, `"problem"`, `"gas"`, `"fuel"`, `"tank"`, `"leak"`, or `"recall"` in the context of reporting an issue.

**2. Dynamic Tool Augmentation**
If enabled by the execution context, the `servicenow_agent` dynamically merges the `google_search` adk tool with the core MCP tools extracted from ServiceNow. This creates "Hybrid Intelligences":

```python
    if enable_google_search:
        # Augments local IT skills with global web searches
        agent_tools = mcp_tools + [google_search] 
        SERVICENOW_INSTRUCTIONS = """
    ...
    You also have the `google_search` tool. Use it freely to gather precise technical information from the internet to enrich, validate, or generate content for tickets when specific details are requested but missing in your context.
    """
    else:
        # Strictly limited to IT Systems
        agent_tools = mcp_tools
```

**3. Execution Identity Guarantee**
This agent initializes its underlying MCP using `uv run` to guarantee isolated python environments matching zero-leak architectures.
```python
    params = mcp_tool.StdioConnectionParams(
        server_params={
            "command": "uv",
            "args": ["run", "python", "-m", "servicenow_mcp.mcp_server_servicenow"],
            "env": env
        }
    )
```
