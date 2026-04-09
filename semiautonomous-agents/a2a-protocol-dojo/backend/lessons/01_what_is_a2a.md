---
title: "What is A2A?"
description: "Understanding the Agent-to-Agent protocol"
hasDemo: false
demoComponent: null
---

# What is A2A?

## The Problem

AI agents are everywhere — built with different frameworks (LangChain, CrewAI, ADK, AutoGen), running on different platforms (Cloud Run, Vertex AI, Azure, AWS). But they can't talk to each other.

Without a standard protocol, connecting N agents requires N×N custom integrations:

```
Agent A ──custom──► Agent B
Agent A ──custom──► Agent C
Agent B ──custom──► Agent C
Agent B ──custom──► Agent D
  ... (N × N integrations)
```

## The Solution: A2A

**A2A (Agent-to-Agent)** is an open protocol by Google that lets agents from any vendor, framework, or organization communicate through a standard interface.

```
Agent A ──┐                ┌── Agent B
Agent C ──┤  A2A Protocol  ├── Agent D
Agent E ──┘  (standard)    └── Agent F
```

A2A is built on proven web standards:
- **HTTP/HTTPS** — transport layer
- **JSON-RPC 2.0** — message format
- **Server-Sent Events (SSE)** — streaming

## Core Concepts

A2A has five key building blocks:

| Concept | What It Is |
|---------|-----------|
| **Agent Card** | JSON metadata describing an agent's capabilities, published at `/.well-known/agent-card.json` |
| **Task** | The fundamental unit of work, with a lifecycle (submitted → working → completed) |
| **Message** | A communication unit containing Parts, with a role (user/agent) |
| **Part** | The smallest content unit: text, file, or structured data |
| **Artifact** | Output produced by a completed task |

## How A2A Works

```
1. DISCOVERY
   Client fetches Agent Card from /.well-known/agent-card.json
   → Learns what the agent can do (skills, capabilities)

2. COMMUNICATION
   Client sends a Message via JSON-RPC
   → Agent creates a Task and starts processing

3. RESPONSE
   Agent returns results as Artifacts
   → Synchronous, streaming (SSE), or push notifications
```

## Design Principles

| Principle | Description |
|-----------|-------------|
| **Opacity** | Agents don't expose internal state, memory, or tools |
| **Security** | HTTPS required in production; supports OAuth2, API Keys, mTLS |
| **Modality Agnostic** | Supports text, files, audio, video, structured data |
| **Async-First** | Designed for long-running tasks and human-in-the-loop |

## A2A vs MCP

These protocols are complementary, not competing:

| | A2A | MCP |
|--|-----|-----|
| **Purpose** | Agent-to-Agent communication | Agent-to-Tool integration |
| **Who talks** | Agent ↔ Agent | Agent → Tool/Service |
| **Protocol** | JSON-RPC 2.0 over HTTP | JSON-RPC 2.0 over stdio/HTTP |
| **Key feature** | Agent Cards, Tasks, Skills | Tool definitions, Resources |

**A2A** = how agents collaborate with each other
**MCP** = how agents use tools and services

## What You'll Build in This Tutorial

Over the next 6 lessons, you'll:

1. **Fetch an Agent Card** from a live A2A agent
2. **Watch tasks** progress through their lifecycle
3. **Build and send messages** with the JSON-RPC format
4. **Stream responses** using Server-Sent Events
5. **Browse agent skills** and invoke them
6. **Orchestrate multiple agents** working together

All with interactive demos running against real A2A agents!

## Resources

- [Official A2A Specification](https://a2a-protocol.org/latest/specification/)
- [A2A Python SDK](https://github.com/a2aproject/a2a-python)
- [Google Blog: A2A Announcement](https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability/)
