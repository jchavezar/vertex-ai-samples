---
title: "Sessions & Runners"
description: "How ADK manages state and execution"
---

# Sessions & Runners

## The Runner Pattern

In a2a-sdk, you implement `AgentExecutor.execute()` and manage task state manually. In ADK, the **Runner** handles execution flow automatically:

```python
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

agent = Agent(
    name="assistant",
    model="gemini-2.0-flash",
    instruction="You are a helpful assistant.",
)

session_service = InMemorySessionService()
runner = Runner(
    agent=agent,
    app_name="my_app",
    session_service=session_service,
)
```

## Sessions = Conversation State

A **Session** tracks the conversation history between a user and an agent:

```python
from google.genai import types

# Create a session
session = await session_service.create_session(
    app_name="my_app",
    user_id="user-123",
)

# Send a message
content = types.Content(
    role="user",
    parts=[types.Part(text="What is A2A?")]
)

response = await runner.run_async(
    user_id="user-123",
    session_id=session.id,
    new_message=content,
)
```

## Session Services

ADK provides different backends for session storage:

| Service | Use Case |
|---------|----------|
| `InMemorySessionService` | Development, testing |
| `DatabaseSessionService` | Production with persistence |
| `VertexAiSessionService` | Managed on Vertex AI |

## Runner vs AgentExecutor

| | ADK Runner | a2a-sdk AgentExecutor |
|--|-----------|----------------------|
| **State management** | Automatic (sessions) | Manual (task states) |
| **Turn handling** | Built-in multi-turn | You implement it |
| **Error handling** | Framework-level | Manual try/catch |
| **Streaming** | Automatic with `run_async` | Manual EventQueue |

## Comparison: Task Lifecycle

**a2a-sdk** — You manage every state transition:
```python
class MyExecutor(AgentExecutor):
    async def execute(self, context, event_queue):
        # Manual: submitted → working
        await event_queue.enqueue_event(
            TaskStatusUpdateEvent(
                task_id=context.task_id,
                status=TaskStatus(state=TaskState.working),
                final=False,
            )
        )
        result = await self.process(context)
        # Manual: working → completed
        await event_queue.enqueue_event(
            TaskStatusUpdateEvent(
                task_id=context.task_id,
                status=TaskStatus(state=TaskState.completed),
                final=True,
            )
        )
```

**ADK** — The Runner handles state transitions:
```python
# Just define the agent — Runner manages lifecycle
agent = Agent(
    name="assistant",
    model="gemini-2.0-flash",
    instruction="You are a helpful assistant.",
)

# Runner handles: session creation, state transitions,
# error handling, streaming — all automatically
response = await runner.run_async(
    user_id="user-123",
    session_id=session.id,
    new_message=content,
)
```
