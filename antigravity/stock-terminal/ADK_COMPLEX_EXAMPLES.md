# Advanced ADK Examples

This document explores complex, production-ready scenarios using the Google Agent Development Kit (ADK). These examples demonstrate advanced patterns like real-time streaming, complex orchestration, optimization, and extending core capabilities.

> **Note:** These examples use `gemini-3-flash-preview` (or compatible Gemini Live models) to leverage the latest agentic capabilities.

## Table of Contents
1. [Real-Time Bi-Directional Streaming (Multi-Agent)](#real-time-bi-directional-streaming-multi-agent)
2. [Automated Issue Triaging (Real-World Workflow)](#automated-issue-triaging-real-world-workflow)
3. [Cache Analysis & Research Assistant](#cache-analysis--research-assistant)
4. [Custom Code Execution (Extending Capabilities)](#custom-code-execution-extending-capabilities)

---

## Real-Time Bi-Directional Streaming (Multi-Agent)

This example demonstrates a **voice-enabled, multi-agent system** capable of real-time interaction. It uses specialized sub-agents ("Roll Agent" and "Prime Agent") orchestrated by a root agent, all communicating via the Gemini Live API with specific voice configurations.

**Key Features:**
*   **Gemini Live API Integration:** Uses `gemini-live-2.5-flash-native-audio` (or similar) for low-latency voice interaction.
*   **Voice Configuration:** Assigns distinct voices ("Kore", "Puck", "Zephyr") to different agents for auditory distinction.
*   **Multi-Agent Delegation:** The root agent routes requests to specialized sub-agents based on user intent (rolling dice vs. checking primes).

```python
import random
from google.adk.agents.llm_agent import Agent
from google.adk.models.google_llm import Gemini
from google.genai import types

# --- Sub-Agent 1: Roll Agent ---
def roll_die(sides: int) -> int:
    """Roll a die and return the rolled result."""
    return random.randint(1, sides)

roll_agent = Agent(
    name="roll_agent",
    model=Gemini(
        model="gemini-live-3-flash-preview", 
        speech_config=types.SpeechConfig(
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Kore")
            )
        ),
    ),
    description="Handles rolling dice.",
    instruction="Roll dice using the `roll_die` tool.",
    tools=[roll_die],
)

# --- Sub-Agent 2: Prime Agent ---
def check_prime(nums: list[int]) -> str:
    """Check if numbers are prime."""
    # ... (implementation omitted for brevity) ...
    return "Checked primes."

prime_agent = Agent(
    name="prime_agent",
    model=Gemini(
        model="gemini-live-3-flash-preview",
        speech_config=types.SpeechConfig(
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Puck")
            )
        ),
    ),
    description="Checks prime numbers.",
    instruction="Check if numbers are prime using `check_prime`.",
    tools=[check_prime],
)

# --- Root Agent ---
def get_current_weather(location: str):
    return "Sunny" if location == "New York" else "Raining"

root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model="gemini-live-3-flash-preview",
        speech_config=types.SpeechConfig(
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Zephyr")
            )
        ),
    ),
    instruction="""
      You are a helpful assistant.
      - Delegate dice rolling to `roll_agent`.
      - Delegate prime checking to `prime_agent`.
      - Check weather yourself using `get_current_weather`.
    """,
    sub_agents=[roll_agent, prime_agent],
    tools=[get_current_weather],
)
```

---

## Automated Issue Triaging (Real-World Workflow)

This agent acts as a **GitHub Issue Triage Assistant**. It interacts with the GitHub API to list untriaged issues, apply labels, assign owners, and change issue types based on predefined rules and component mappings.

**Key Features:**
*   **Real-World Tool Integration:** Uses `requests` to interact with the GitHub REST API.
*   **Complex Logic:** Implements logic to determine "needs_component_label" and "needs_owner" states.
*   **Safety & Interactivity:** Includes flags (`IS_INTERACTIVE`) to control whether the agent applies changes automatically or asks for user approval.

```python
# (Simplified structure)
from google.adk.agents.llm_agent import Agent
# ... imports for GitHub API tools ...

LABEL_TO_OWNER = {
    "core": "Jacksunwei",
    "web": "wyf7107",
    # ... mapping ...
}

def list_untriaged_issues(issue_count: int) -> dict:
    """Fetches issues needing triage from GitHub."""
    # Logic to fetch issues and filter by missing labels/assignees
    pass

def add_label_to_issue(issue_number: int, label: str) -> dict:
    """Adds a label to a GitHub issue."""
    pass

def add_owner_to_issue(issue_number: int, label: str) -> dict:
    """Assigns an owner based on the applied label."""
    pass

root_agent = Agent(
    model="gemini-3-flash-preview",
    name="triage_bot",
    instruction="""
      You are a GitHub triage bot.
      1. Fetch untriaged issues using `list_untriaged_issues`.
      2. For issues missing a component label, analyze the content and apply the best label using `add_label_to_issue`.
      3. For issues with a 'planned' label but no owner, assign the owner based on the component using `add_owner_to_issue`.
      
      Always summarize your actions and justify your labeling decisions.
    """,
    tools=[
        list_untriaged_issues,
        add_label_to_issue,
        add_owner_to_issue,
    ],
)
```

---

## Cache Analysis & Research Assistant

This agent is designed for **heavy-duty analysis tasks** that benefit from **Context Caching**. It defines a rich set of simulation tools (research, benchmarking, security analysis) and is configured with an explicit caching policy to optimize performance and cost for long sessions.

**Key Features:**
*   **Context Caching:** Configures `ContextCacheConfig` with TTL and token thresholds, crucial for agents handling large amounts of data or long histories.
*   **Rich Toolset:** Demonstrates an agent with a comprehensive suite of domain-specific tools (Data Analysis, Security, Architecture).
*   **App Pattern:** Uses the `App` class wrapper to apply configurations (like caching) to the root agent.

```python
from google.adk import Agent
from google.adk.apps.app import App
from google.adk.agents.context_cache_config import ContextCacheConfig

# ... (Definitions for tools: analyze_data_patterns, research_literature, etc.) ...

cache_analysis_agent = Agent(
    name="research_assistant",
    model="gemini-3-flash-preview",
    instruction="""
      You are an expert Research and Analysis Assistant.
      Use your tools to conduct deep system analysis, performance benchmarking, 
      and security assessments.
    """,
    tools=[
        analyze_data_patterns,
        research_literature,
        benchmark_performance,
        # ... other tools
    ],
)

# Wrap in an App to configure Context Caching
cache_analysis_app = App(
    name="cache_analysis_app",
    root_agent=cache_analysis_agent,
    context_cache_config=ContextCacheConfig(
        min_tokens=4096,      # Only cache if context exceeds this
        ttl_seconds=600,      # Cache time-to-live
        cache_intervals=3,    # Refresh interval
    ),
)
```

---

## Custom Code Execution (Extending Capabilities)

This example shows how to **extend the ADK's core functionality**. It creates a `CustomCodeExecutor` by subclassing `VertexAiCodeExecutor` to inject custom setup code (in this case, installing Japanese fonts) into every execution environment transparently.

**Key Features:**
*   **Class Inheritance:** Subclassing `VertexAiCodeExecutor` to modify behavior.
*   **Method Overriding:** Overriding `execute_code` to intercept and modify the code execution payload.
*   **Custom Environment Setup:** Automating environment prerequisites (like fonts or libraries) without user intervention.

```python
from google.adk.agents.llm_agent import Agent
from google.adk.code_executors.vertex_ai_code_executor import VertexAiCodeExecutor
from google.adk.code_executors.code_execution_utils import InvocationContext, CodeExecutionInput, CodeExecutionResult, File
from typing_extensions import override

class CustomCodeExecutor(VertexAiCodeExecutor):
    """Extends the default executor to setup Japanese fonts."""

    @override
    def execute_code(
        self,
        invocation_context: InvocationContext,
        code_execution_input: CodeExecutionInput,
    ) -> CodeExecutionResult:
        # 1. Logic to download/prepare the font file
        font_file = ... # (Download logic) 
        
        # 2. Inject setup code
        setup_code = """
import matplotlib.font_manager as fm
# ... setup logic ...
print("Japanese font enabled.")
"""
        code_execution_input.code = f"{setup_code}\n\n{code_execution_input.code}"
        
        # 3. Add file to execution environment
        if font_file:
            code_execution_input.input_files.append(font_file)

        # 4. Delegate to parent implementation
        return super().execute_code(invocation_context, code_execution_input)

root_agent = Agent(
    name="data_science_agent",
    model="gemini-3-flash-preview",
    instruction="You are a data science assistant. You can execute Python code to analyze data.",
    # Use the custom executor
    code_executor=CustomCodeExecutor(),
)
```