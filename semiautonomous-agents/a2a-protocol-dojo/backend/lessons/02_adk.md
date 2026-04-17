---
title: "Defining Agents in ADK"
description: "How ADK agents declare capabilities"
---

# Defining Agents in ADK

## Agent Definition

In ADK, you define agents declaratively — no need to manually write Agent Card JSON:

```python
from google.adk.agents import Agent

agent = Agent(
    name="weather_agent",
    model="gemini-2.0-flash",
    description="Provides weather information for any city",
    instruction=(
        "You are a weather specialist. When asked about weather, "
        "use the get_weather tool to fetch current conditions."
    ),
)
```

ADK automatically generates the A2A Agent Card from these fields.

## Agent vs LlmAgent

ADK provides two main agent types:

```python
from google.adk.agents import Agent, LlmAgent

# Agent — shorthand, most common
agent = Agent(
    name="simple_agent",
    model="gemini-2.0-flash",
    instruction="Help users with questions.",
)

# LlmAgent — same class, explicit name
agent = LlmAgent(
    name="explicit_agent",
    model="gemini-2.0-flash",
    instruction="Help users with questions.",
)
```

`Agent` is just an alias for `LlmAgent`. Use whichever reads better.

## Adding Tools

Tools are plain Python functions with type hints:

```python
def get_weather(city: str) -> dict:
    """Get current weather for a city."""
    return {"city": city, "temp": 72, "condition": "sunny"}

agent = Agent(
    name="weather_agent",
    model="gemini-2.0-flash",
    description="Weather information agent",
    instruction="Use get_weather to answer weather questions.",
    tools=[get_weather],
)
```

ADK inspects the function signature and docstring to create the tool schema automatically.

## Auto-Generated Agent Card

When deployed via `AdkApp`, ADK creates the A2A Agent Card:

```json
{
  "name": "weather_agent",
  "description": "Weather information agent",
  "url": "http://localhost:8001",
  "version": "1.0.0",
  "capabilities": { "streaming": true },
  "skills": [
    {
      "id": "weather_agent",
      "name": "weather_agent",
      "description": "Weather information agent"
    }
  ]
}
```

## Comparison: a2a-sdk vs ADK

**a2a-sdk** — You manually define every field:
```python
from a2a.types import AgentCard, AgentCapabilities, AgentSkill

card = AgentCard(
    name="weather_agent",
    description="Weather information agent",
    url="http://localhost:8001",
    version="1.0.0",
    capabilities=AgentCapabilities(streaming=True),
    skills=[AgentSkill(id="weather", name="Weather", ...)],
    default_input_modes=["text/plain"],
    default_output_modes=["text/plain"],
)
```

**ADK** — Agent Card is derived from your agent definition:
```python
agent = Agent(
    name="weather_agent",
    model="gemini-2.0-flash",
    description="Weather information agent",
    instruction="...",
    tools=[get_weather],
)
# Agent Card auto-generated when deployed
```
