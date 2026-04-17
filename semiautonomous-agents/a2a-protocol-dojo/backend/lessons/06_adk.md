---
title: "Tools & Function Calling in ADK"
description: "How ADK agents use tools and produce outputs"
---

# Tools & Function Calling in ADK

## Tools in ADK

In a2a-sdk, agent capabilities are described as "skills" in the Agent Card. In ADK, capabilities are **tools** — actual Python functions the agent can call:

```python
from google.adk.agents import Agent

def calculate_tax(amount: float, rate: float) -> dict:
    """Calculate tax for a given amount and rate.

    Args:
        amount: The base amount
        rate: Tax rate as a percentage (e.g., 8.5)
    """
    tax = amount * (rate / 100)
    return {"amount": amount, "rate": rate, "tax": tax, "total": amount + tax}

agent = Agent(
    name="tax_calculator",
    model="gemini-2.0-flash",
    description="Calculates taxes and financial figures",
    instruction="Use the calculate_tax tool to help with tax questions.",
    tools=[calculate_tax],
)
```

## How Function Calling Works

1. User sends a message
2. Model decides to call a tool (based on the query)
3. ADK executes the Python function
4. Result is fed back to the model
5. Model generates the final response

```
User: "What's the tax on $500 at 8.5%?"
  │
  ▼
Model → tool_call: calculate_tax(amount=500, rate=8.5)
  │
  ▼
ADK executes → {"amount": 500, "rate": 8.5, "tax": 42.5, "total": 542.5}
  │
  ▼
Model → "The tax on $500 at 8.5% is $42.50, making the total $542.50."
```

## Multiple Tools

Agents can have multiple tools:

```python
def get_weather(city: str) -> dict:
    """Get current weather for a city."""
    return {"city": city, "temp": 72, "condition": "sunny"}

def get_time(timezone: str) -> str:
    """Get current time in a timezone."""
    return "2024-01-15 14:30:00 PST"

agent = Agent(
    name="info_agent",
    model="gemini-2.0-flash",
    instruction="Help users with weather and time questions.",
    tools=[get_weather, get_time],
)
```

## MCP Tools Integration

ADK can use MCP (Model Context Protocol) tools via `McpToolset`:

```python
from google.adk.tools.mcp_tool import McpToolset, SseServerParams

mcp_tools, cleanup = await McpToolset.from_server(
    connection_params=SseServerParams(url="http://localhost:3000/sse")
)

agent = Agent(
    name="mcp_agent",
    model="gemini-2.0-flash",
    instruction="Use available tools to help users.",
    tools=mcp_tools,
)
```

## Comparison: Skills vs Tools

**a2a-sdk** — Skills are metadata only (descriptions for discovery):
```python
skill = AgentSkill(
    id="calculate_tax",
    name="Tax Calculator",
    description="Calculates tax amounts",
    tags=["finance", "tax"],
    examples=["What's the tax on $500?"],
)
# You implement the logic separately in AgentExecutor
```

**ADK** — Tools are executable Python functions:
```python
def calculate_tax(amount: float, rate: float) -> dict:
    """Calculate tax for a given amount and rate."""
    tax = amount * (rate / 100)
    return {"tax": tax, "total": amount + tax}

agent = Agent(
    name="tax_agent",
    tools=[calculate_tax],  # Directly executable
)
```

## Key Difference

- **a2a-sdk Skills** = "here's what I can do" (metadata for discovery)
- **ADK Tools** = "here's how I do it" (actual executable functions)

Both are needed: ADK tools power the agent, A2A skills advertise the capabilities.
