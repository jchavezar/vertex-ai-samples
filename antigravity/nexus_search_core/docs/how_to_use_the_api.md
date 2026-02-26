# How to Use the Gemini Enterprise APIs (Advanced Guide)

This guide provides technical implementation details for Vertex AI Agent Builder (formerly Discovery Engine) APIs, including search, conversation, and agentic patterns.

---

## 🔑 Authentication & Setup

All APIs require a Google Cloud Access Token with the `cloud-platform` scope and the `X-Goog-User-Project` header.

```python
import google.auth
import google.auth.transport.requests
import requests

def get_headers(project_number):
    credentials, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    auth_req = google.auth.transport.requests.Request()
    credentials.refresh(auth_req)
    return {
        "Authorization": f"Bearer {credentials.token}",
        "Content-Type": "application/json",
        "X-Goog-User-Project": project_number
    }
```

---

## 🔍 1. Search & Answer Patterns

### Method A: Legacy RAG Answer (Stateless)
Fastest way to get a summarized answer from a datastore.

**Endpoint:** `POST .../servingConfigs/default_search:answer`

```python
payload = {
    "query": {"text": "What is the revenue of Alphabet?"},
    "answerGenerationSpec": {
        "ignoreAdversarialQuery": True,
        "includeCitations": True,
        "modelSpec": {"modelVersion": "stable"}
    }
}
```

### Method B: Streaming Answer (v1beta)
Provides a streaming response for the `answer` method.

**Endpoint:** `POST .../servingConfigs/default_config:streamAnswer`

```python
def stream_answer(url, payload, headers):
    with requests.post(url, json=payload, headers=headers, stream=True) as response:
        for line in response.iter_lines():
            if line:
                print(line.decode('utf-8'))
```

### Method C: Deep Search (with Snippets & Scores)
Use this when you need raw search results instead of a summary.

**Endpoint:** `POST .../servingConfigs/default_search:search`

```python
payload = {
    "query": "financial risks",
    "pageSize": 5,
    "contentSearchSpec": {
        "snippetSpec": {"returnSnippet": True},
        "extractiveContentSpec": {"maxExtractiveAnswerCount": 1}
    },
    "relevanceScoreSpec": {"returnRelevanceScore": True}
}
```

---

## 🤖 2. Agentic Assist (Stateful & Autonomous)

This is the modern way to build agents that can use tools (Web Search, Datastores, APIs).

**Endpoint:** `POST .../assistants/default_assistant:streamAssist`

### Maintaining a Session
To keep track of a conversation, provide a `session` path.

```python
session_id = "user-123-session-456"
project_number = "123456789"
engine_id = "my-engine"

session_path = f"projects/{project_number}/locations/global/collections/default_collection/engines/{engine_id}/sessions/{session_id}"

payload = {
    "query": {"text": "Tell me more about the first point."},
    "session": session_path
}
```

### Forcing Tool Usage (searchSpec)
You can guide how the agent searches its datastores.

```python
payload = {
    "query": {"text": "Search the latest 10-K filings."},
    "searchSpec": {
        "searchParams": {
            "maxReturnResults": 5,
            "filter": "category: \"finance\""
        }
    }
}
```

---

## 🛠️ 3. Agent Management

### Listing Agents in an Engine
Agents (or Reasoning Engines) can be registered within a Discovery Engine app.

```python
# GET .../assistants/default_assistant/agents
def list_ge_agents(url, headers):
    response = requests.get(url, headers=headers)
    return response.json().get("agents", [])
```

### Registering a Reasoning Engine as a GE Agent
This links a custom Vertex AI Reasoning Engine (ADK) to a Gemini Enterprise Assistant.

```python
payload = {
    "displayName": "My Custom Interceptor",
    "description": "Handles complex logic before searching",
    "adk_agent_definition": {
        "provisioned_reasoning_engine": {
            "reasoning_engine": "projects/PROJECT/locations/LOCATION/reasoningEngines/ID"
        }
    }
}
# POST .../assistants/default_assistant/agents
```

---

## 📋 API Summary Table

| API Method | Version | Stream | Best For |
| :--- | :--- | :--- | :--- |
| `search` | `v1alpha` | No | Raw snippets, filtering, and sorting. |
| `answer` | `v1alpha` | No | Quick one-off summaries. |
| `streamAnswer`| `v1beta` | Yes | Interactive RAG experiences. |
| `streamAssist`| `v1beta` | Yes | Full Agentic loops, multi-turn, tool-use. |

---

## 💡 Troubleshooting Tips

1. **403 Permission Denied:** Ensure your service account has `Discovery Engine Viewer/Editor` roles and you are passing `X-Goog-User-Project`.
2. **Empty Answers:** Check `ignoreLowRelevantContent`. If set to `True`, the LLM will refuse to answer if the search results aren't high-confidence.
3. **Session Errors:** Ensure the session ID follows the regex `[a-zA-Z0-9-_]+` and the full path is correctly formatted.
