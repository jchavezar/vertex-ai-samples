# 🚀 ADK Quickstart & Distilled Guide

Welcome to the distilled ADK documentation. This directory provides high-density, code-centric reference for building AI agents.

## 🛠️ Main Components
- **`core_concepts.md`**: Defining `LlmAgent`, Session management, and State.
- **`orchestration.md`**: Building Multi-Agent systems and Workflows (Sequential, Parallel, Loop).
- **`tooling.md`**: Creating custom Tools, using Built-in tools, and connecting via MCP.
- **`deployment.md`**: Deploying to Cloud Run or Vertex AI Agent Engine.

## 🐍 Python Quickstart (Minimal)
```python
import os
# Mandatory for Gemini 3 and Vertex AI routing
os.environ["GOOGLE_CLOUD_LOCATION"] = "global"
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "true"

from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# 1. Define your tool
def get_status(target: str) -> str:
    """Gets the status of a specific target."""
    return f"Target {target} is active."

# 2. Define your agent
agent = LlmAgent(
    name="status_checker",
    model="gemini-3-flash-preview",
    instruction="You are a status assistant. Use the tool to check targets.",
    tools=[get_status]
)

# 3. Create a Runner (Mandatory: use app_name and auto_create_session)
runner = Runner(
    app_name="my_status_app",
    agent=agent,
    session_service=InMemorySessionService(),
    auto_create_session=True
)

# 4. Run it (Mandatory: use types.Content)
result = runner.run(
    user_id="user_123",
    session_id="session_456",
    new_message=types.Content(parts=[types.Part(text="Check firewall")], role="user")
)

# Robust Event Collection
full_text = ""
for event in result:
    if hasattr(event, 'text') and event.text:
        full_text += event.text
    elif hasattr(event, 'content') and event.content:
        for part in getattr(event.content, 'parts', []):
            if hasattr(part, 'text') and part.text:
                full_text += part.text
print(f"Final Outcome: {full_text}")
```

## 🏗️ Project Structure Context
- **`.env`**: Store your `GOOGLE_API_KEY` or `GOOGLE_CLOUD_PROJECT`.
- **`agent.py`**: Standard entry point for agent logic.
- **`adk run <dir>`**: CLI for interactive testing.
- **`adk web`**: Dev UI for debugging (port 8000).

---
*Created from distilled analysis of adk_docs.md*
