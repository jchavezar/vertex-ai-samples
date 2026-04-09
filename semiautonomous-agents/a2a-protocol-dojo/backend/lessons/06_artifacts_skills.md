---
title: "Artifacts & Skills"
description: "Agent outputs and capability discovery"
hasDemo: true
demoComponent: "SkillsBrowser"
---

# Artifacts & Skills

## Artifacts

An **Artifact** is the output of a task — the actual result the agent produces. Artifacts contain Parts, just like messages:

```json
{
  "artifactId": "art-001",
  "name": "analysis_result",
  "description": "Sentiment analysis output",
  "parts": [
    {"kind": "text", "text": "Positive sentiment (0.92 confidence)"},
    {"kind": "data", "data": {"score": 0.92, "label": "positive"}}
  ]
}
```

### Artifact Fields

| Field | Required | Description |
|-------|----------|-------------|
| `artifactId` | Yes | Unique identifier |
| `parts` | Yes | Content array (text, files, data) |
| `name` | No | Human-readable label |
| `description` | No | What this artifact contains |

## Creating Artifacts (Server Side)

```python
from a2a.types import Artifact, TextPart, DataPart
import uuid

artifact = Artifact(
    artifact_id=str(uuid.uuid4()),
    name="weather_report",
    description="Current weather conditions",
    parts=[
        TextPart(text="San Francisco: 68°F, Partly Cloudy"),
        DataPart(data={
            "temperature": 68,
            "condition": "partly_cloudy",
            "humidity": 72,
        }),
    ],
)
```

## Sending Artifacts via EventQueue

```python
await event_queue.enqueue_event(
    TaskArtifactUpdateEvent(
        task_id=context.task_id,
        context_id=context.context_id,
        artifact=artifact,
        last_chunk=True,  # No more artifacts coming
    )
)
```

### Streaming Artifacts

For long-running tasks, you can send multiple artifact updates. Use `last_chunk=False` for intermediate results:

```python
# Partial result
await event_queue.enqueue_event(
    TaskArtifactUpdateEvent(
        task_id=task_id,
        context_id=ctx_id,
        artifact=partial_artifact,
        last_chunk=False,  # More coming
    )
)

# Final result
await event_queue.enqueue_event(
    TaskArtifactUpdateEvent(
        task_id=task_id,
        context_id=ctx_id,
        artifact=final_artifact,
        last_chunk=True,  # Done
    )
)
```

## Skills in Depth

Skills are how agents advertise their capabilities. A well-defined skill helps clients know exactly what to send:

```python
from a2a.types import AgentSkill

skills = [
    AgentSkill(
        id="summarize",
        name="Text Summarizer",
        description="Condenses long text into key points",
        tags=["nlp", "summarization", "text"],
        examples=[
            "Summarize this article about climate change",
            "Give me the key points from this report",
        ],
    ),
    AgentSkill(
        id="translate",
        name="Language Translator",
        description="Translates text between 50+ languages",
        tags=["nlp", "translation", "language"],
        examples=[
            "Translate 'hello' to Japanese",
            "Convert this paragraph to French",
        ],
    ),
]
```

### Skill Discovery Pattern

A client agent can discover skills from multiple agents and route work accordingly:

```python
import httpx

async def discover_skills():
    agents = ["http://agent-a:8001", "http://agent-b:8002"]
    all_skills = {}

    async with httpx.AsyncClient() as client:
        for url in agents:
            r = await client.get(f"{url}/.well-known/agent-card.json")
            card = r.json()
            for skill in card["skills"]:
                all_skills[skill["id"]] = {
                    "skill": skill,
                    "agent_url": url,
                    "agent_name": card["name"],
                }

    return all_skills
```

## Try It!

Browse all skills across the running agents below. Click on any skill to send a test query and see the response.
