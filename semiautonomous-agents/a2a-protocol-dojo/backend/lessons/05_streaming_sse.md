---
title: "Streaming with SSE"
description: "Real-time responses with Server-Sent Events"
hasDemo: true
demoComponent: "StreamViewer"
---

# Streaming with SSE

## Why Streaming?

Some tasks take time. Without streaming, you wait in silence until the agent finishes. With streaming, you get real-time updates:

- Token-by-token text generation
- Progress updates during long tasks
- Partial results as they become available

## Server-Sent Events (SSE)

A2A uses **SSE** for streaming. The client sends a `message/stream` request and the server responds with a stream of events:

```
Client                              Agent
  │  POST / (message/stream)          │
  │──────────────────────────────────►│
  │                                   │
  │  event: status-update             │
  │  data: {"state": "working"}       │
  │◄──────────────────────────────────│
  │                                   │
  │  event: artifact-update           │
  │  data: {"text": "The A2A..."}     │
  │◄──────────────────────────────────│
  │                                   │
  │  event: artifact-update           │
  │  data: {"text": "The A2A proto"}  │
  │◄──────────────────────────────────│
  │                                   │
  │  event: status-update             │
  │  data: {"state": "completed"}     │
  │◄──────────────────────────────────│
```

## Streaming Request

The JSON-RPC method is `message/stream` instead of `message/send`:

```json
{
  "jsonrpc": "2.0",
  "id": "req-001",
  "method": "message/stream",
  "params": {
    "message": {
      "role": "user",
      "parts": [{"kind": "text", "text": "Explain A2A"}],
      "messageId": "msg-001"
    }
  }
}
```

## SSE Event Types

### TaskStatusUpdateEvent

Reports state changes:

```
event: TaskStatusUpdateEvent
data: {
  "kind": "status-update",
  "taskId": "task-123",
  "contextId": "ctx-456",
  "final": false,
  "status": {"state": "working"}
}
```

### TaskArtifactUpdateEvent

Delivers content incrementally:

```
event: TaskArtifactUpdateEvent
data: {
  "kind": "artifact-update",
  "taskId": "task-123",
  "contextId": "ctx-456",
  "artifact": {
    "artifactId": "art-001",
    "parts": [{"kind": "text", "text": "The A2A protocol enables..."}]
  },
  "lastChunk": false
}
```

## Server Implementation

```python
class StreamingExecutor(AgentExecutor):
    async def execute(self, context, event_queue):
        # Signal working
        await event_queue.enqueue_event(
            TaskStatusUpdateEvent(
                task_id=context.task_id,
                context_id=context.context_id,
                final=False,
                status=TaskStatus(state=TaskState.working),
            )
        )

        # Stream content word by word
        full_text = ""
        for word in response_text.split():
            full_text += word + " "
            await event_queue.enqueue_event(
                TaskArtifactUpdateEvent(
                    task_id=context.task_id,
                    context_id=context.context_id,
                    artifact=Artifact(
                        artifact_id=str(uuid.uuid4()),
                        parts=[TextPart(text=full_text)],
                    ),
                    last_chunk=False,
                )
            )

        # Final artifact + completed
        await event_queue.enqueue_event(
            TaskStatusUpdateEvent(
                task_id=context.task_id,
                context_id=context.context_id,
                final=True,
                status=TaskStatus(state=TaskState.completed),
            )
        )
```

## Client-Side Streaming

```python
async with httpx.AsyncClient() as client:
    async with client.stream(
        "POST", "http://localhost:8002/",
        json=streaming_request,
        headers={"Accept": "text/event-stream"}
    ) as response:
        async for line in response.aiter_lines():
            if line.startswith("data:"):
                event = json.loads(line[5:])
                print(event)
```

## Try It!

Send a query to the Gemini Agent and watch the streaming response appear in real-time. The left panel shows the text, and the right panel shows the raw SSE events.
