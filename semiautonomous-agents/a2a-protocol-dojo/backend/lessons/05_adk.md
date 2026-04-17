---
title: "Streaming in ADK"
description: "Real-time responses with ADK's built-in streaming"
---

# Streaming in ADK

## Built-In Streaming

In a2a-sdk, you manually enqueue events to an `EventQueue`. In ADK, streaming is built into the Runner — just iterate over the response:

```python
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

agent = Agent(
    name="streamer",
    model="gemini-2.0-flash",
    instruction="Explain topics clearly and thoroughly.",
)

runner = Runner(
    agent=agent,
    app_name="my_app",
    session_service=InMemorySessionService(),
)

session = await runner.session_service.create_session(
    app_name="my_app", user_id="user-1"
)

# Streaming response — async iteration
async for event in runner.run_async(
    user_id="user-1",
    session_id=session.id,
    new_message=types.Content(
        role="user",
        parts=[types.Part(text="Explain A2A protocol")]
    ),
):
    if event.content and event.content.parts:
        for part in event.content.parts:
            if part.text:
                print(part.text, end="", flush=True)
```

## A2A SSE via AdkApp

When deployed with `AdkApp`, ADK automatically handles the SSE protocol:

```python
from google.adk.app import AdkApp

app = AdkApp(agent=agent, port=8002)
app.run()
```

Clients can call `message/stream` and receive standard A2A SSE events:

```
POST / HTTP/1.1
Content-Type: application/json
Accept: text/event-stream

{"jsonrpc": "2.0", "method": "message/stream", ...}

---
event: TaskStatusUpdateEvent
data: {"kind": "status-update", "status": {"state": "working"}}

event: TaskArtifactUpdateEvent
data: {"kind": "artifact-update", "artifact": {"parts": [{"text": "The A2A..."}]}}

event: TaskStatusUpdateEvent
data: {"kind": "status-update", "status": {"state": "completed"}}
```

## Streaming with Tools

ADK streams tool calls and results as events too:

```python
def search_web(query: str) -> str:
    """Search the web for information."""
    return f"Results for: {query}"

agent = Agent(
    name="researcher",
    model="gemini-2.0-flash",
    instruction="Research topics using web search.",
    tools=[search_web],
)

# Events include tool calls:
# 1. status: working
# 2. tool_call: search_web("A2A protocol")
# 3. tool_result: "Results for: A2A protocol"
# 4. content: "Based on my research..."
# 5. status: completed
```

## Comparison: Streaming Implementation

**a2a-sdk** — Manual event queue management:
```python
class StreamingExecutor(AgentExecutor):
    async def execute(self, context, event_queue):
        await event_queue.enqueue_event(
            TaskStatusUpdateEvent(
                task_id=context.task_id,
                final=False,
                status=TaskStatus(state=TaskState.working),
            )
        )
        for word in text.split():
            full_text += word + " "
            await event_queue.enqueue_event(
                TaskArtifactUpdateEvent(
                    task_id=context.task_id,
                    artifact=Artifact(
                        parts=[TextPart(text=full_text)],
                    ),
                    last_chunk=False,
                )
            )
        await event_queue.enqueue_event(
            TaskStatusUpdateEvent(
                task_id=context.task_id,
                final=True,
                status=TaskStatus(state=TaskState.completed),
            )
        )
```

**ADK** — Streaming is automatic:
```python
agent = Agent(
    name="streamer",
    model="gemini-2.0-flash",
    instruction="Explain topics clearly.",
)
# That's it — Runner handles all SSE events automatically
```
