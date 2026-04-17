---
title: "What is Google ADK?"
description: "The Agent Development Kit for building AI agents"
---

# What is Google ADK?

## From Protocol to Framework

While A2A defines the **protocol** for agent communication, **Google ADK (Agent Development Kit)** is the **framework** for building the agents themselves.

Think of it this way:
- **A2A** = the language agents speak (HTTP + JSON-RPC)
- **ADK** = the toolkit to build agents that speak it

## ADK at a Glance

ADK is a Python framework that provides:

| Component | Purpose |
|-----------|---------|
| `Agent` / `LlmAgent` | Define agent behavior with model + instructions |
| `Runner` | Execute agent logic and manage turns |
| `SessionService` | Track conversation state |
| `ToolContext` | Give agents access to functions/APIs |
| `SequentialAgent` | Chain agents in order |
| `ParallelAgent` | Run agents concurrently |

## Your First ADK Agent

```python
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

agent = Agent(
    name="greeter",
    model="gemini-2.0-flash",
    description="A friendly greeter agent",
    instruction="You are a friendly agent. Greet the user warmly.",
)

session_service = InMemorySessionService()
runner = Runner(agent=agent, app_name="my_app", session_service=session_service)
```

## ADK vs a2a-sdk

| | ADK | a2a-sdk |
|--|-----|---------|
| **Focus** | Building agent logic | Implementing A2A protocol |
| **Abstraction** | High-level (Agent, Runner) | Low-level (JSON-RPC, EventQueue) |
| **Model integration** | Built-in (Gemini, etc.) | Bring your own |
| **Multi-agent** | SequentialAgent, ParallelAgent | Manual orchestration |
| **Deployment** | AdkApp → Cloud Run / Vertex AI | Starlette / any ASGI |
| **A2A support** | Built-in via `AdkApp` | Native |

## How ADK Connects to A2A

ADK agents can be exposed as A2A-compatible servers using `AdkApp`:

```python
from google.adk.app import AdkApp

app = AdkApp(agent=agent, port=8001)
app.run()
# Now serves at /.well-known/agent-card.json
# Accepts message/send, message/stream JSON-RPC calls
```

## Key Takeaway

**ADK handles the "how to build"**, while **A2A handles the "how to communicate"**. They work together — build with ADK, communicate with A2A.
