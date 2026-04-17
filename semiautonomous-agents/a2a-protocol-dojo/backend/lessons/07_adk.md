---
title: "Multi-Agent Pipelines in ADK"
description: "Building agent teams with SequentialAgent and ParallelAgent"
---

# Multi-Agent Pipelines in ADK

## Built-In Multi-Agent Support

In a2a-sdk, orchestrating multiple agents means manually discovering, routing, and aggregating. ADK has **first-class multi-agent support**:

```python
from google.adk.agents import Agent, SequentialAgent, ParallelAgent
```

## SequentialAgent — Pipeline Pattern

Run agents one after another, each building on the previous output:

```python
researcher = Agent(
    name="researcher",
    model="gemini-2.0-flash",
    instruction="Research the given topic thoroughly.",
    tools=[search_web],
)

writer = Agent(
    name="writer",
    model="gemini-2.0-flash",
    instruction="Write a clear summary based on the research.",
)

reviewer = Agent(
    name="reviewer",
    model="gemini-2.0-flash",
    instruction="Review the summary for accuracy and clarity.",
)

# Chain them together
pipeline = SequentialAgent(
    name="research_pipeline",
    sub_agents=[researcher, writer, reviewer],
)
```

```
User Query → [Researcher] → [Writer] → [Reviewer] → Final Output
```

## ParallelAgent — Fan-Out Pattern

Run agents concurrently and combine results:

```python
news_agent = Agent(
    name="news",
    model="gemini-2.0-flash",
    instruction="Find the latest news on the topic.",
)

academic_agent = Agent(
    name="academic",
    model="gemini-2.0-flash",
    instruction="Find academic papers on the topic.",
)

social_agent = Agent(
    name="social",
    model="gemini-2.0-flash",
    instruction="Find social media discussions on the topic.",
)

# Run all three simultaneously
parallel = ParallelAgent(
    name="multi_source_research",
    sub_agents=[news_agent, academic_agent, social_agent],
)
```

```
              ┌─► [News Agent]     ─┐
User Query ───┼─► [Academic Agent] ─┼──► Combined Results
              └─► [Social Agent]   ─┘
```

## Combining Sequential + Parallel

```python
# Stage 1: Gather from multiple sources (parallel)
gatherer = ParallelAgent(
    name="gather",
    sub_agents=[news_agent, academic_agent, social_agent],
)

# Stage 2: Synthesize all findings (sequential after parallel)
synthesizer = Agent(
    name="synthesizer",
    model="gemini-2.0-flash",
    instruction="Combine all research findings into a cohesive report.",
)

# Full pipeline
full_pipeline = SequentialAgent(
    name="full_research",
    sub_agents=[gatherer, synthesizer],
)
```

## Running Multi-Agent Pipelines

```python
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

runner = Runner(
    agent=full_pipeline,  # Pass the top-level agent
    app_name="research_app",
    session_service=InMemorySessionService(),
)

session = await runner.session_service.create_session(
    app_name="research_app", user_id="user-1"
)

async for event in runner.run_async(
    user_id="user-1",
    session_id=session.id,
    new_message=types.Content(
        role="user",
        parts=[types.Part(text="Research the A2A protocol")]
    ),
):
    if event.content:
        print(event.content.parts[0].text)
```

## Comparison: Orchestration

**a2a-sdk** — Manual HTTP-level orchestration:
```python
async def orchestrate(query, agent_urls):
    agents = await discover_agents(agent_urls)
    tasks = [delegate_to_agent(a["url"], query) for a in agents]
    results = await asyncio.gather(*tasks)
    return aggregate(results)
```

**ADK** — Declarative agent composition:
```python
pipeline = SequentialAgent(
    name="pipeline",
    sub_agents=[
        ParallelAgent(
            name="gather",
            sub_agents=[agent_a, agent_b, agent_c],
        ),
        synthesizer,
    ],
)
# Runner handles all orchestration automatically
```

## Deploying as A2A Server

The entire pipeline becomes a single A2A endpoint:

```python
from google.adk.app import AdkApp

app = AdkApp(agent=full_pipeline, port=8003)
app.run()
# Other agents see ONE agent card
# Internal pipeline is opaque (A2A design principle!)
```

This is the power of combining ADK + A2A: build complex internally, expose simple externally.
