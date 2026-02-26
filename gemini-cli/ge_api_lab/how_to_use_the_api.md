# How to Use the Gemini Enterprise APIs

This guide explains how to integrate and use the two primary API patterns available in Vertex AI Agent Builder: **Legacy RAG Answer** and **Agentic Assist**.

## 🔑 Authentication

Both APIs require a Google Cloud Access Token with the `cloud-platform` scope.

```python
import google.auth
import google.auth.transport.requests

credentials, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
auth_req = google.auth.transport.requests.Request()
credentials.refresh(auth_req)
access_token = credentials.token
```

Include this token in your headers:
```python
headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json",
    "X-Goog-User-Project": PROJECT_NUMBER
}
```

---

## 🛠️ Method 1: Legacy RAG Answer
**Use case:** Passive, linear search-and-summarize tasks where you need a quick answer from a specific datastore.

### Endpoint
`POST https://discoveryengine.googleapis.com/v1alpha/projects/{PROJECT_NUMBER}/locations/global/collections/default_collection/engines/{ENGINE_ID}/servingConfigs/default_search:answer`

### Payload Structure
```json
{
    "query": {"text": "Your query here"},
    "relatedQuestionsSpec": {"enable": true},
    "answerGenerationSpec": {
        "ignoreAdversarialQuery": true,
        "ignoreNonAnswerSeekingQuery": false,
        "ignoreLowRelevantContent": false, 
        "includeCitations": true,
        "modelSpec": {"modelVersion": "stable"}
    }
}
```

### Implementation Example
```python
import requests

def get_rag_answer(project_number, engine_id, query, headers):
    url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{project_number}/locations/global/collections/default_collection/engines/{engine_id}/servingConfigs/default_search:answer"
    payload = {
        "query": {"text": query},
        "answerGenerationSpec": {"modelSpec": {"modelVersion": "stable"}}
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json().get("answer", {}).get("answerText")
```

---

## 🤖 Method 2: Agentic Assist (Modern)
**Use case:** Autonomous, conversational interactions where the agent needs to route intent, use tools, or ask for clarification.

### Endpoint
`POST https://discoveryengine.googleapis.com/v1beta/projects/{PROJECT_NUMBER}/locations/global/collections/default_collection/engines/{ENGINE_ID}/assistants/default_assistant:streamAssist`

### Payload Structure
```json
{
    "query": {"text": "Your query here"}
}
```

### Implementation Example (Streaming)
The Agentic Assist API supports streaming (SSE).

```python
import requests
import json

def stream_agentic_assist(project_number, engine_id, query, headers):
    url = f"https://discoveryengine.googleapis.com/v1beta/projects/{project_number}/locations/global/collections/default_collection/engines/{engine_id}/assistants/default_assistant:streamAssist"
    payload = {"query": {"text": query}}

    with requests.post(url, json=payload, headers=headers, stream=True) as response:
        for line in response.iter_lines():
            if line:
                decoded_line = line.decode('utf-8').strip()
                # Extract text from the "text" field in the streaming response
                if decoded_line.startswith('"text":'):
                    # Basic parsing logic for demo purposes
                    chunk = json.loads("{" + decoded_line.rstrip(',') + "}")
                    print(chunk.get("text", ""), end="", flush=True)
```

---

## 📋 Summary Comparison

| Feature | Legacy RAG | Agentic Assist |
| :--- | :--- | :--- |
| **API Version** | `v1alpha` | `v1beta` |
| **Streaming** | No | Yes |
| **Persona Support** | No | Yes (via Assistant config) |
| **Tool Use** | No | Yes (Web Search, Extensions) |
| **Stateful** | No | Yes (Session-based) |
| **Behavior** | Passive | Proactive / Autonomous |
