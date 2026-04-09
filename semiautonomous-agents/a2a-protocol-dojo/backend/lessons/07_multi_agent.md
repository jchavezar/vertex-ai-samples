---
title: "Multi-Agent Orchestration"
description: "Agents collaborating on complex tasks"
hasDemo: true
demoComponent: "OrchestrationFlow"
---

# Multi-Agent Orchestration

## The Real Power of A2A

A single agent is useful. Multiple agents working together are powerful. A2A enables **orchestration** — one agent discovering and delegating work to others.

```
                  ┌─────────────────┐
                  │  Orchestrator   │
                  │  (Client Agent) │
                  └───────┬─────────┘
                          │
              ┌───────────┼───────────┐
              │           │           │
    ┌─────────▼──┐ ┌──────▼────┐ ┌───▼──────────┐
    │ Echo Agent │ │ Gemini    │ │ Future Agent │
    │ (port 8001)│ │ (port 8002│ │ (any port)   │
    └────────────┘ └───────────┘ └──────────────┘
```

## Orchestration Pattern

### Step 1: Discovery

The orchestrator fetches Agent Cards from known agents:

```python
import httpx

async def discover_agents(agent_urls):
    agents = []
    async with httpx.AsyncClient() as client:
        for url in agent_urls:
            try:
                r = await client.get(
                    f"{url}/.well-known/agent-card.json"
                )
                card = r.json()
                agents.append({
                    "url": url,
                    "name": card["name"],
                    "skills": card["skills"],
                })
            except Exception:
                pass  # Agent not available
    return agents
```

### Step 2: Routing

Based on skills, the orchestrator decides which agent handles what:

```python
def route_task(query, agents):
    """Route a query to the best agent based on skills."""
    for agent in agents:
        for skill in agent["skills"]:
            # Simple keyword matching
            for tag in skill.get("tags", []):
                if tag in query.lower():
                    return agent
    # Default: use first available agent
    return agents[0] if agents else None
```

### Step 3: Delegation

The orchestrator sends the task via JSON-RPC:

```python
async def delegate_to_agent(agent_url, message_text):
    payload = {
        "jsonrpc": "2.0",
        "id": str(uuid.uuid4()),
        "method": "message/send",
        "params": {
            "message": {
                "role": "user",
                "parts": [{"kind": "text", "text": message_text}],
                "messageId": str(uuid.uuid4()),
            }
        },
    }
    async with httpx.AsyncClient() as client:
        r = await client.post(f"{agent_url}/", json=payload)
        return r.json()
```

### Step 4: Aggregation

Collect results from all agents:

```python
async def orchestrate(query, agent_urls):
    # 1. Discover
    agents = await discover_agents(agent_urls)

    # 2. Fan-out: send to all agents
    tasks = []
    for agent in agents:
        task = delegate_to_agent(agent["url"], query)
        tasks.append(task)

    # 3. Fan-in: collect results
    results = await asyncio.gather(*tasks)

    # 4. Aggregate
    combined = []
    for agent, result in zip(agents, results):
        artifacts = result.get("result", {}).get("artifacts", [])
        for art in artifacts:
            for part in art.get("parts", []):
                if "text" in part:
                    combined.append({
                        "agent": agent["name"],
                        "response": part["text"]
                    })

    return combined
```

## Error Handling

When orchestrating multiple agents, handle failures gracefully:

```python
async def safe_delegate(agent_url, message):
    try:
        return await delegate_to_agent(agent_url, message)
    except httpx.ConnectError:
        return {"error": f"Agent at {agent_url} not reachable"}
    except httpx.TimeoutException:
        return {"error": f"Agent at {agent_url} timed out"}
```

## Security Considerations

When agents call other agents:

- **Authentication**: Use API keys or OAuth2 between agents
- **Authorization**: Verify the calling agent is allowed to use the skill
- **Input validation**: Sanitize all messages (prevent prompt injection)
- **Rate limiting**: Prevent one agent from overwhelming another

## What's Next

After mastering A2A locally, you can:

1. **Deploy agents to Cloud Run** with proper HTTPS
2. **Register in Gemini Enterprise** via Discovery Engine API
3. **Add authentication** between agents
4. **Build a registry** for agent discovery at scale

## Try It!

Click "Run Orchestration" below to watch the orchestrator discover agents, delegate work to each one, and aggregate the results.
