# Google Agent Development Kit (ADK) - Python Guide

This document provides a comprehensive guide to creating agents using the Google ADK in Python. It covers installation, core concepts, basic agent creation, and complex multi-agent workflows.

## Table of Contents
1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Core Concepts](#core-concepts)
4. [Getting Started: Basic LlmAgent](#getting-started-basic-llmagent)
5. [Advanced Workflows](#advanced-workflows)
    - [SequentialAgent](#sequentialagent)
    - [ParallelAgent](#parallelagent)
    - [LoopAgent](#loopagent)
6. [Custom Agents](#custom-agents)
7. [State Management](#state-management)
8. [Verification](#verification)

---

## Introduction

The **Agent Development Kit (ADK)** is a framework for building autonomous agents. An **Agent** is a self-contained execution unit that can perform tasks, interact with users, use tools, and coordinate with other agents.

> **See [ADK_EXAMPLES.md](./ADK_EXAMPLES.md) for a collection of code examples covering Hello World, Sequential workflows, Human-in-the-Loop, MCP, and RAG.**
> **See [ADK_COMPLEX_EXAMPLES.md](./ADK_COMPLEX_EXAMPLES.md) for advanced scenarios like Real-Time Streaming, Automated Triaging, Cache Analysis, and Custom Executors.**
> **See [ADK_WORKFLOW_PATTERNS.md](./ADK_WORKFLOW_PATTERNS.md) for architectural patterns: Mixed Workflows (Parallel inside Sequential), Pipeline State Passing, and Iterative Loops with Escalation.**

## Installation

**Prerequisites:**
- Python 3.10 or later
- A Google Cloud Project (for Vertex AI) or API Key (for Google AI Studio) if using Gemini models.

**Steps:**

1.  **Create and activate a virtual environment:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # macOS/Linux
    # .venv\Scripts\activate   # Windows
    ```

2.  **Install the ADK package:**
    ```bash
    pip install google-adk
    ```

3.  **Set up Environment Variables:**
    Create a `.env` file in your project root:
    ```env
    GOOGLE_API_KEY="your_api_key_here"
    # Or for Vertex AI:
    # GOOGLE_CLOUD_PROJECT="your_project_id"
    # GOOGLE_CLOUD_LOCATION="us-central1"
    ```

---

## Core Concepts

*   **`BaseAgent`**: The foundational class for all agents.
*   **`LlmAgent`**: Uses a Large Language Model (e.g., Gemini) for reasoning and task execution. Best for flexible, natural language tasks.
*   **`SequentialAgent`**: Executes a list of sub-agents one after another.
*   **`ParallelAgent`**: Executes a list of sub-agents concurrently.
*   **`LoopAgent`**: Executes sub-agents repeatedly until a condition is met or max iterations are reached.
*   **Invocation Context**: A shared context object passed between agents to share state and data.

---

## Getting Started: Basic LlmAgent

This example creates a simple agent that can tell the time using a custom tool.

```python
import os
from dotenv import load_dotenv
from google.adk.agents.llm_agent import Agent

# Load environment variables
load_dotenv()

# 1. Define a tool
def get_current_time(city: str) -> dict:
    """Returns the current time in a specified city."""
    # In a real scenario, fetch actual time
    return {"status": "success", "city": city, "time": "10:30 AM"}

# 2. Create the Agent
agent = Agent(
    model='gemini-3-flash-preview',  # Using the latest model
    name='time_agent',
    description="Tells the current time in a specified city.",
    instruction="You are a helpful assistant. Use the 'get_current_time' tool when asked about time.",
    tools=[get_current_time],
)

# 3. Run the agent (CLI mode)
# You can run this file directly or use `adk run` if structured correctly.
if __name__ == "__main__":
    import asyncio
    from google.adk.agents import InvocationContext
    
    async def main():
        # Simple interaction simulation
        print("Agent ready. Type 'exit' to quit.")
        while True:
            user_input = input("User: ")
            if user_input.lower() == 'exit':
                break
            
            # Note: Actual runner logic might differ slightly based on library version updates
            # This is a conceptual run loop.
            # See `adk run` command for production running.
            pass 

    # For standard usage, use the CLI:
    # $ adk run .
```

---

## Example: Multi-Agent Router

This example demonstrates how to use the `BuiltInPlanner` and `agent_tool` to create a "Root Agent" that routes tasks to specialized sub-agents (Google Search, Code Execution, Vertex AI Search).

```python
from google.genai import types
from google.adk.agents import Agent
from google.adk.tools import agent_tool
from google.adk.planners import BuiltInPlanner
from google.adk.tools import google_search
from google.adk.tools.vertex_ai_search_tool import VertexAiSearchTool
from google.adk.code_executors import BuiltInCodeExecutor

# Configure the planner
my_planner = BuiltInPlanner(
    thinking_config=types.ThinkingConfig(
        thinking_budget=0
    )
)

# Initialize Tools
# Replace data_store_id with your actual Vertex AI Search data store ID
vais_tool = VertexAiSearchTool(data_store_id="projects/254356041555/locations/global/collections/default_collection/dataStores/countries-and-their-cultur_1706277976842")

# 1. Google Search Agent
google_search_agent = Agent(
    model="gemini-2.5-flash",
    name="google_search",
    description="Use google search tool to find answers",
    tools=[google_search],
    planner=my_planner
)

# 2. Execution Agent (Code Interpreter)
execution_agent = Agent(
    model="gemini-2.5-flash",
    name="execution_agent",
    description="Use execution tool to get advance answers that required programming",
    tools=[BuiltInCodeExecutor],
    planner=my_planner
)

# 3. Vertex AI Search Agent (RAG)
vais_local_search = Agent(
    model="gemini-2.5-flash",
    name="vais_local_search",
    description="Use local vais search tool to find answers",
    tools=[vais_tool],
    planner=my_planner
)

# 4. Root Agent (Orchestrator)
root_agent = Agent(
    name="root_agent",
    model="gemini-2.5-flash",
    description="God of Agents",
    instruction="""
    Your main task is to answer any question by detecting the intent and use your tools accordingly:
    
    Order of priority:
    1. If its a code generation use 'execution_agent'.
    2. If is any question that requires up to date information from internet use 'google_search_agent'.
    3. If the question is related to Countries and their Culture only use: 'vais_local_search' agent tool.
    3. For the rest use your knowledge based with that data was used during your training.
    
    Add in your response the method/tool used for your response.
    """,
    tools=[
        agent_tool.AgentTool(agent=google_search_agent),
        agent_tool.AgentTool(agent=execution_agent),
        agent_tool.AgentTool(agent=vais_local_search)
    ],
    planner=my_planner
)
```

---

## Advanced Workflows

Complex behaviors are built by composing agents.

### SequentialAgent

Use this when step B depends on step A.

```python
from google.adk.agents import SequentialAgent, LlmAgent

# Step 1: Fetch Data and save it to 'state["raw_data"]'
# 'output_key' automatically saves the agent's final response/result to the shared state
fetcher = LlmAgent(
    model='gemini-3-flash-preview',
    name="Fetcher", 
    instruction="Fetch the latest stock price for Google.",
    output_key="raw_data" 
)

# Step 2: Analyze Data
# This agent's instruction references the data saved by the previous agent
analyzer = LlmAgent(
    model='gemini-3-flash-preview',
    name="Analyzer", 
    instruction="Analyze the following data and provide a summary: {raw_data}."
)

# Create the pipeline
pipeline = SequentialAgent(
    name="StockPipeline", 
    sub_agents=[fetcher, analyzer]
)
```

### ParallelAgent

Use this for independent tasks to save time.

```python
from google.adk.agents import ParallelAgent, LlmAgent

weather_agent = LlmAgent(
    model='gemini-3-flash-preview',
    name="Weather", 
    instruction="Get weather in NY.", 
    output_key="weather_ny"
)

news_agent = LlmAgent(
    model='gemini-3-flash-preview',
    name="News", 
    instruction="Get top tech news.", 
    output_key="tech_news"
)

# Runs both at the same time
dashboard_aggregator = ParallelAgent(
    name="DashboardData", 
    sub_agents=[weather_agent, news_agent]
)
```

### LoopAgent

Use this for iterative tasks like refinement or polling.

```python
from google.adk.agents import LoopAgent, LlmAgent

# An agent that tries to generate code
coder = LlmAgent(
    model='gemini-3-flash-preview',
    name="Coder", 
    instruction="Write a Python function to sort a list."
)

# An agent that reviews the code
reviewer = LlmAgent(
    model='gemini-3-flash-preview',
    name="Reviewer", 
    instruction="Review the code. If it has bugs, say 'FIX'. If good, say 'PERFECT'."
)

# This loop will run Coder -> Reviewer repeatedly
dev_loop = LoopAgent(
    name="DevLoop",
    sub_agents=[coder, reviewer],
    max_iterations=5
)
```

---

## Custom Agents

For logic that isn't just "call an LLM" or "run these in order", you can subclass `BaseAgent`.

```python
from typing import AsyncGenerator
from google.adk.agents import BaseAgent
from google.adk.events import Event, EventActions
from google.adk.agents.invocation_context import InvocationContext

class StopperAgent(BaseAgent):
    """
    Checks a condition in the state and stops a LoopAgent if met.
    """
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        # Check shared state
        status = ctx.session.state.get("review_status", "pending")
        
        # Determine if we should stop the loop (escalate=True)
        should_stop = (status == "APPROVED")
        
        # Yield an event. 'escalate' tells the parent (LoopAgent) to stop.
        yield Event(
            author=self.name, 
            actions=EventActions(escalate=should_stop)
        )
```

## State Management

Agents share data via `InvocationContext` and its `session.state`.

1.  **Writing State:**
    *   **Implicitly:** Use `output_key="my_var"` in `LlmAgent`. The result is saved to `state["my_var"]`.
    *   **Explicitly:** In a custom tool or custom agent, modify `ctx.session.state["my_var"] = value`.

2.  **Reading State:**
    *   **In Prompts:** Use `{my_var}` in your `instruction` string. The ADK replaces it with the value from state.
    *   **In Code:** Access `ctx.session.state.get("my_var")`.

---

## CLI Commands

*   `adk create <name>`: Scaffolds a new agent project.
*   `adk run <path>`: Runs the agent in the terminal.
*   `adk web`: Starts a local web server to interact with the agent UI.

---

## Verification

**Verified Source:** The information in this document, including the use of `google-adk` package and `SequentialAgent`, `ParallelAgent`, `LoopAgent` classes, has been verified against Google's ADK documentation and PyPI package details. The model `gemini-3-flash-preview` is a valid model in the Gemini 3 series, designed for agentic workflows.