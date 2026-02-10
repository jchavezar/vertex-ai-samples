# 🧠 ADK Core Concepts (Python)

## 1. The `LlmAgent`
The primary unit of reasoning.

```python
from google.adk.agents import LlmAgent
from pydantic import BaseModel, Field

class AnalysisResult(BaseModel):
    summary: str = Field(description="Brief summary of findings")
    severity: int = Field(description="Risk level 1-10")

analyst = LlmAgent(
    name="risk_analyst",
    model="gemini-3-flash-preview",
    instruction="Analyze the provided logs for security risks.",
    output_schema=AnalysisResult,
    output_key="analysis" # Result stored as dict in session state
)
```

## 2. Session & State
ADK uses sessions to maintain context.
- **`ctx.session.events`**: List of all events (User input, Agent responses, Tool calls).
- **`ctx.session.state`**: A flat dictionary for storing variables available to all agents in a workflow.
- **`ctx.session.artifacts`**: Versioned file storage (binary data, PDFs, etc.).

## 3. The Runner
Executes the agent logic.
- **`InMemorySessionService`**: State lost after process exits (Best for testing).
- **`FirestoreSessionService`**: Persistent state (Best for production apps).

**CRITICAL**: You must set `GOOGLE_CLOUD_LOCATION="global"` and `GOOGLE_GENAI_USE_VERTEXAI="true"` for Gemini 3.

```python
import os
os.environ["GOOGLE_CLOUD_LOCATION"] = "global"
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "true"

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

runner = Runner(
    app_name="my_app",
    agent=my_agent,
    session_service=InMemorySessionService(),
    auto_create_session=True # Avoids 'Session Not Found' errors
)

# Execution returns a generator of Events. 
# Use run_async for better compatibility with async frameworks (FastAPI).
result = runner.run_async(
    user_id="user_id",
    session_id="session_id",
    new_message=types.Content(parts=[types.Part(text="Hi")], role="user")
)

# Robust Event Parsing
full_text = ""
async for event in result:
    if hasattr(event, 'text') and event.text:
        full_text += event.text
    elif hasattr(event, 'content') and event.content:
        for part in getattr(event.content, 'parts', []):
            if hasattr(part, 'text') and part.text:
                full_text += part.text
```

## 4. Models
**Mandatory Versions:**
- `gemini-3-flash-preview` (Fastest, default)
- `gemini-3-pro-preview` (Reasoning heavy)
- `gemini-2.5-flash`

**Cloud vs API Key:**
- ADK automatically detects `GOOGLE_API_KEY` for AI Studio.
- Use `GOOGLE_CLOUD_PROJECT` for Vertex AI (requires `gcloud auth`).

---
*Reference: adk-docs/docs/agents/llm-agents.md*
