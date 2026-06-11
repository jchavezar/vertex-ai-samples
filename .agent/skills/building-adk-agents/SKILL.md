---
name: building-adk-agents
description: Expert guide for building, deploying, and debugging Google ADK (Agent Development Kit) agents. Use for creating LLM agents, workflows, tools, and multi-agent systems.
---

# Building Google ADK Agents (Expert Mode)

## When to use this skill
- **New Agent Creation**: Scaffolding `Agent`, `SequentialAgent`, `ParallelAgent`, or `LoopAgent`.
- **Tool Development**: Creating custom tools, `MCP` integrations, or `FunctionTool` wrappers.
- **Advanced Workflows**: Implementing "Researcher-Writer", "Router", or hierarchical multi-agent systems.
- **Infrastructure**: Setting up `Artifacts` (file storage), `Sessions` (state), or `Callbacks` (observability).
- **Deployment**: Preparing agents for Cloud Run, GKE, or Vertex AI Agent Engine.

## 🚨 Critical Mandates
1.  **Model Selection**:
    - **Complex Reasoning**: `gemini-3.5-flash` (Default for logic/orchestration)
    - **Speed/Efficiency**: `gemini-3.1-flash-lite` (Default for simple tasks/summarization)
    - **Legacy**: Avoid `gemini-1.5`, `gemini-2.0` unless specifically requested.
2.  **Structured Output**:
    - ALWAYS use Pydantic (Python) or Zod (TS) for structured data extraction.
    - NEVER rely on prompt engineering alone for JSON. Use `output_schema`.
3.  **Code Quality**:
    - **Type Hints**: Mandatory for all Python tool functions (used for schema generation).
    - **Docstrings**: Mandatory for all tools (used for LLM tool descriptions).
    - **Error Handling**: Wrap tool execution in try/except blocks.
4.  **Environment & Execution**:
    - **ALWAYS use `uv`**: Mandated for project initialization (`uv init`), dependency management (`uv add`), and execution (`uv run`).
    - **No Orphan Environments**: Do not create or use non-uv venvs or global python environments.

## 🧠 Knowledge Base
This skill is backed by the full ADK documentation.
- Location: `resources/adk_docs.md` and `resources/llms.txt`
- Usage: If you are unsure about an API signature, import, or pattern, **SEARCH** these files first.
  - `grep "class Agent" resources/adk_docs.md`
  - `grep "def save_artifact" resources/adk_docs.md`

## 🛠️ Implementation Patterns

### 1. Structured Output (JSON)
Enforce strict schema adherence for reliable downstream processing.

```python
from pydantic import BaseModel, Field
from google.adk.agents import Agent

# 1. Define Schema
class ResearchResult(BaseModel):
    summary: str = Field(description="Executive summary of findings")
    sources: list[str] = Field(description="List of URLs cited")

# 2. Configure Agent (Consolidated Agent class)
agent = Agent(
    name="researcher",
    model="gemini-3.1-flash-lite",
    instruction="Analyze the given topic and return structured data.",
    output_schema=ResearchResult,  # <--- CRITICAL
    output_key="research_data"     # <--- Stores in ctx.session.state['research_data']
)
```

### 2. State & Artifacts
Manage conversation context and binary files (PDFs, Images).

```python
from google.adk.agents import CallbackContext

async def my_tool(ctx: CallbackContext, data: str):
    # Access Session State
    user_id = ctx.session.state.get("user_id")
    
    # Save Binary Artifact (e.g., generated PDF)
    await ctx.save_artifact(
        filename="report.pdf", 
        artifact=pdf_bytes, 
        mime_type="application/pdf"
    )
```

### 3. Workflow Construction
Compose agents into deterministic or dynamic flows.

- **Sequential**: `A -> B -> C`. Output of A becomes context for B.
- **Parallel**: `[A, B, C]`. Run all at once, aggregate results.
- **Loop**: `A -> condition? -> A`. Repeat until done.

```python
from google.adk.agents import SequentialAgent

workflow = SequentialAgent(
    name="blog_post_workflow",
    agents=[researcher_agent, writer_agent, editor_agent],
    output_key="final_post"
)
```

## ✅ Development Checklist

1.  **Define Strategy**:
    - Single Agent vs. Multi-Agent?
    - Stateful (needs memory) or Stateless?
2.  **Scaffold**:
    - Create `main.py` with `Runner`.
    - Initialize `InMemorySessionService` and `InMemoryArtifactService` (for local dev).
3.  **Implement Tools**:
    - Use `@tool` decorator.
    - Annotate args with `Annotated[type, "description"]` if using advanced typing.
4.  **Verify**:
    - Run the agent locally using `uv run`.
    - Check logs for tool calling errors.

### 4. Next-Gen Agent Engine Deployment
Utilize the `vertexai.Client` and `vertexai.agent_engines.AdkApp` pattern for robust Cloud deployments.

```python
import vertexai
from vertexai.agent_engines import AdkApp

# 1. Initialize with Client
client = vertexai.Client(project="PROJ", location="LOC")

# 2. Wrap Agent
deployment_app = AdkApp(agent=root_agent, enable_tracing=True)

# 3. Idempotent Update or Create
all_engines = list(client.agent_engines.list())
target = next((e for e in all_engines if e.api_resource.display_name == "MY_APP"), None)

if target:
    remote_app = client.agent_engines.update(
        name=target.api_resource.name,
        agent=deployment_app,
        config={"display_name": "MY_APP", "staging_bucket": "gs://...", "requirements": "requirements.txt", "extra_packages": ["agent.py"]}
    )
else:
    remote_app = client.agent_engines.create(
        agent=deployment_app,
        config={"display_name": "MY_APP", "staging_bucket": "gs://...", "requirements": "requirements.txt", "extra_packages": ["agent.py"]}
    )
```

## 🛑 Common Pitfalls to Avoid
- **Missing `output_key`**: If you don't set this in a workflow, the parent agent won't get the result.
- **Missing Tool Types**: The LLM cannot call a tool if the arguments are not typed (e.g., `def func(x)` vs `def func(x: int)`).
- **Ignoring Model Version**: Using an old model (`gemini-1.0`) will result in poor instruction following.
- **Missing Local Serialization Dependency (`cloudpickle`)**: Local deployment using the `Client` from `vertexai.agent_engines` requires the `cloudpickle` package to serialize the agent state (e.g. `agent_engine.pkl`). Make sure `cloudpickle` is listed in your local dependencies (`pyproject.toml`).
- **Missing Cloud Container Dependencies (`mcp`, `anthropic`, `google-cloud-aiplatform`)**: If the agent uses the `McpToolset` or custom model integrations, those dependencies must be specified in the cloud deployment configuration's `requirements.txt` file, otherwise container loading fails at runtime.
- **PyPI 401 Authentication Bypasses**: When running deployment commands in environments utilizing authenticated private indices with expired tokens, force dependencies to resolve from public PyPI using `uv run --default-index https://pypi.org/simple` or `pip install --index-url https://pypi.org/simple`.
- **Default App Name ValidationError**: If `AdkApp` is initialized without an explicit `app_name` (e.g. `AdkApp(agent=root_agent)`), on remote deployment the template runner defaults the app name to the numeric `GOOGLE_CLOUD_AGENT_ENGINE_ID` of the container. Because this starts with a digit, it fails the ADK `App` name Pydantic validation. Always pass `app_name=AGENT_ENGINE_NAME` explicitly when initializing `AdkApp`.
- **Forcing Global Location for Model Routing**: Models that serve from the `global` region (such as preview models or `gemini-3.5-flash`) or third-party models (such as `claude-sonnet-4-6@default` which is only servable in `us-east5` or `global` regions, and not in `us-central1` where Agent Engine runs) require routing location override. To achieve this, set `os.environ["GOOGLE_CLOUD_LOCATION"] = "global"` inside `agent.py` at import time, or pass it via `env_vars={"GOOGLE_CLOUD_LOCATION": "global"}` in the deployment configuration dict.
- **Sub-Agent Search Tool Delegation**: The built-in `google_search` tool is only supported for Gemini models. If you have a root agent using Claude (or any non-Gemini model), you can delegate search tasks to a Gemini sub-agent (e.g. `gemini-2.5-flash`) equipped with `google_search` by wrapping the sub-agent in `AgentTool` and providing it to the root agent's tools list.
- **AdkApp Client Query Method Bug (`Unsupported api mode`)**: If querying a deployed `AdkApp` reasoning engine, the Python SDK client (`ReasoningEngine`) will fail to register the query methods and throw `object has no attribute 'query'` because `AdkApp` exposes `async_stream_query` (which contains `async` in its name, rejected as an invalid mode by the SDK). Bypass this by performing a direct authenticated HTTP POST request to the REST endpoint: `https://{LOCATION}-aiplatform.googleapis.com/v1/{REASONING_ENGINE_RES}:streamQuery?alt=sse`.
- **Gemini-Only Built-In Tools**: The built-in `google_search` tool is only supported for Gemini models. If configuring a third-party Model Garden model (like Claude Sonnet 4.6), using `google_search` will raise a runtime `ValueError: Google search tool is not supported for model ...`. For third-party models, write a custom python tool or use Brave Search MCP instead, or delegate to a Gemini search sub-agent.

## Resources
- [Full ADK Documentation (Local)](resources/adk_docs.md)
- [Latest ADK Release Documentation (Local)](resources/llms.txt)