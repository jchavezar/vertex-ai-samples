---
title: "Agent Cards — Discovery"
description: "How agents advertise their capabilities"
hasDemo: true
demoComponent: "AgentCardViewer"
---

# Agent Cards — Discovery

## What Is an Agent Card?

An **Agent Card** is a JSON document that describes what an agent can do. It's published at a well-known URL:

```
https://your-agent.example.com/.well-known/agent-card.json
```

Think of it as a resume for your agent — other agents read it to understand capabilities before sending work.

## Agent Card Schema

```json
{
  "name": "echo_agent",
  "description": "Echoes messages back to the sender",
  "url": "http://localhost:8001",
  "version": "1.0.0",
  "capabilities": {
    "streaming": true,
    "pushNotifications": false
  },
  "defaultInputModes": ["text/plain"],
  "defaultOutputModes": ["text/plain"],
  "skills": [
    {
      "id": "echo",
      "name": "Echo",
      "description": "Echoes back the user's message",
      "tags": ["echo", "test"],
      "examples": ["Hello!", "What is A2A?"]
    }
  ]
}
```

### Key Fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Unique agent identifier |
| `description` | Yes | Human-readable purpose |
| `url` | Yes | Base URL for JSON-RPC calls |
| `version` | Yes | Semantic version |
| `capabilities` | Yes | What the agent supports (streaming, push) |
| `skills` | Yes | List of things the agent can do |
| `defaultInputModes` | Yes | Accepted MIME types |
| `defaultOutputModes` | Yes | Response MIME types |

## Skills

Skills are the most important part of an Agent Card. They tell clients exactly what the agent can do:

```python
from a2a.types import AgentSkill

skill = AgentSkill(
    id="translate",
    name="Translate Text",
    description="Translates text between languages",
    tags=["translation", "nlp", "language"],
    examples=[
        "Translate 'hello' to Spanish",
        "Convert this paragraph to French"
    ],
)
```

Each skill has:
- **id** — machine-readable identifier
- **name** — human-readable label
- **description** — what it does
- **tags** — for discovery and filtering
- **examples** — sample inputs

## Capabilities

The `capabilities` object declares protocol features:

```json
{
  "streaming": true,
  "pushNotifications": false,
  "stateTransitionHistory": false
}
```

| Capability | Description |
|-----------|-------------|
| `streaming` | Supports SSE streaming responses |
| `pushNotifications` | Can send webhook notifications |
| `stateTransitionHistory` | Tracks full task state history |

## Building an Agent Card in Python

```python
from a2a.types import AgentCard, AgentCapabilities, AgentSkill

agent_card = AgentCard(
    name="my_agent",
    description="An agent that does useful things",
    url="http://localhost:9000",
    version="1.0.0",
    capabilities=AgentCapabilities(streaming=True),
    default_input_modes=["text/plain"],
    default_output_modes=["text/plain"],
    skills=[
        AgentSkill(
            id="summarize",
            name="Summarize",
            description="Summarizes long text into key points",
            tags=["nlp", "summarization"],
            examples=["Summarize this article..."],
        ),
    ],
)
```

## Discovery Flow

```
Client                              Agent Server
  │                                       │
  │  GET /.well-known/agent-card.json     │
  │──────────────────────────────────────►│
  │                                       │
  │  200 OK (Agent Card JSON)             │
  │◄──────────────────────────────────────│
  │                                       │
  │  (Client reads skills, capabilities)  │
  │  (Client decides what to send)        │
  │                                       │
```

## Try It!

Click the button below to fetch the Agent Card from the Echo Agent running on port 8001. You'll see the actual JSON response with all the fields described above.
