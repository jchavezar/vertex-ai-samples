---
title: "Messages & Parts"
description: "Building and sending A2A messages"
hasDemo: true
demoComponent: "MessageBuilder"
---

# Messages & Parts

## Message Structure

A **Message** is how clients and agents communicate. Each message has:

```json
{
  "role": "user",
  "parts": [
    {"kind": "text", "text": "What is A2A?"}
  ],
  "messageId": "msg-abc-123"
}
```

| Field | Description |
|-------|-------------|
| `role` | Who sent it: `"user"` or `"agent"` |
| `parts` | Array of content pieces (text, files, data) |
| `messageId` | Unique identifier for this message |
| `contextId` | Optional: links messages in a conversation |
| `taskId` | Optional: associates with an existing task |

## Part Types

Parts are the building blocks of messages. A2A supports three kinds:

### TextPart

The most common — plain text content:

```json
{"kind": "text", "text": "Hello, agent!"}
```

```python
from a2a.types import TextPart

part = TextPart(text="Hello, agent!")
```

### FilePart

For sending files (images, documents, etc.):

```json
{
  "kind": "file",
  "file": {
    "name": "report.pdf",
    "mimeType": "application/pdf",
    "uri": "https://storage.example.com/report.pdf"
  }
}
```

### DataPart

For structured data (JSON objects):

```json
{
  "kind": "data",
  "data": {
    "temperature": 72,
    "unit": "fahrenheit",
    "location": "San Francisco"
  }
}
```

## JSON-RPC Format

A2A uses JSON-RPC 2.0 for all communication. Here's a complete `message/send` request:

```json
{
  "jsonrpc": "2.0",
  "id": "req-001",
  "method": "message/send",
  "params": {
    "message": {
      "role": "user",
      "parts": [
        {"kind": "text", "text": "What is Vertex AI?"}
      ],
      "messageId": "msg-001"
    }
  }
}
```

The response contains a **Task** with the agent's result:

```json
{
  "jsonrpc": "2.0",
  "id": "req-001",
  "result": {
    "id": "task-xyz",
    "status": {"state": "completed"},
    "artifacts": [
      {
        "artifactId": "art-001",
        "parts": [
          {"kind": "text", "text": "Vertex AI is Google Cloud's ML platform..."}
        ]
      }
    ]
  }
}
```

## Building Messages in Python

```python
from a2a.types import Message, TextPart, Role
import uuid

message = Message(
    role=Role.user,
    parts=[TextPart(text="What is machine learning?")],
    message_id=str(uuid.uuid4()),
)
```

## Sending via A2A Client

```python
from a2a.client import A2AClient
import httpx

async with httpx.AsyncClient() as http_client:
    client = await A2AClient.get_client_from_agent_card_url(
        http_client, 'http://localhost:8001'
    )

    request = SendMessageRequest(
        params=MessageSendParams(message=message)
    )

    response = await client.send_message(request)
```

## Try It!

Type a message below, see the JSON-RPC payload that will be sent, and watch the Echo Agent respond!
