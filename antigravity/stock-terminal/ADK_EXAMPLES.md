# Google ADK Examples

This document provides a collection of examples for creating various types of agents using the Google Agent Development Kit (ADK). These examples demonstrate core capabilities, advanced workflows, and integrations.

> **Note:** All examples use `gemini-3-flash-preview` as the model. Ensure you have access to this model or substitute it with an available version (e.g., `gemini-2.0-flash`).

## Table of Contents
1. [Hello World (Basic Tools)](#hello-world-basic-tools)
2. [Sequential Workflow](#sequential-workflow)
3. [Human-in-the-Loop](#human-in-the-loop)
4. [Model Context Protocol (MCP)](#model-context-protocol-mcp)
5. [RAG (Retrieval Augmented Generation)](#rag-retrieval-augmented-generation)

---

## Hello World (Basic Tools)

A simple agent that uses Python functions as tools.

```python
import random
from google.adk import Agent
from google.adk.tools.tool_context import ToolContext
from google.genai import types

# Define a tool
def roll_die(sides: int, tool_context: ToolContext) -> int:
    """Roll a die and return the rolled result.
    
    Args:
        sides: The integer number of sides the die has.
    """
    result = random.randint(1, sides)
    
    # Access shared state via tool_context
    if 'rolls' not in tool_context.state:
        tool_context.state['rolls'] = []
    tool_context.state['rolls'] = tool_context.state['rolls'] + [result]
    
    return result

def check_prime(nums: list[int]) -> str:
    """Check if a given list of numbers are prime."""
    primes = set()
    for number in nums:
        number = int(number)
        if number <= 1: continue
        is_prime = True
        for i in range(2, int(number**0.5) + 1):
            if number % i == 0:
                is_prime = False
                break
        if is_prime:
            primes.add(number)
    return ('No prime numbers found.' if not primes 
            else f"{', '.join(str(num) for num in primes)} are prime numbers.")

# Create the agent
root_agent = Agent(
    model='gemini-3-flash-preview',
    name='hello_world_agent',
    description='A basic agent that rolls dice and checks for primes.',
    instruction="""
      You roll dice and answer questions about the outcome.
      1. When asked to roll, call `roll_die`.
      2. When asked to check primes, call `check_prime`.
      3. You can perform these in sequence or parallel as needed.
    """,
    tools=[roll_die, check_prime],
    generate_content_config=types.GenerateContentConfig(
        safety_settings=[
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                threshold=types.HarmBlockThreshold.OFF,
            ),
        ]
    ),
)
```

---

## Sequential Workflow

Orchestrate multiple agents to run in a strict order using `SequentialAgent`.

```python
import random
from google.adk.agents.llm_agent import LlmAgent
from google.adk.agents.sequential_agent import SequentialAgent
from google.genai import types

# --- Sub-Agent 1: Roller ---
def roll_die(sides: int) -> int:
    """Roll a die and return the rolled result."""
    return random.randint(1, sides)

roll_agent = LlmAgent(
    name="roll_agent",
    model="gemini-3-flash-preview",
    description="Handles rolling dice.",
    instruction="You roll dice. Call the `roll_die` tool with the number of sides.",
    tools=[roll_die],
)

# --- Sub-Agent 2: Prime Checker ---
def check_prime(nums: list[int]) -> str:
    """Check if numbers are prime."""
    # ... (implementation same as above) ...
    return "Checked primes." # Simplified for brevity

prime_agent = LlmAgent(
    name="prime_agent",
    model="gemini-3-flash-preview",
    description="Checks if numbers are prime.",
    instruction="You check if numbers are prime using the `check_prime` tool.",
    tools=[check_prime],
)

# --- Root Agent: Orchestrator ---
root_agent = SequentialAgent(
    name="sequential_workflow",
    sub_agents=[roll_agent, prime_agent],
    # Execution: roll_agent -> prime_agent
    # The output of roll_agent is available in the shared context for prime_agent
)
```

---

## Human-in-the-Loop

Use `LongRunningFunctionTool` to pause execution and wait for external (human) approval or input.

```python
from typing import Any
from google.adk import Agent
from google.adk.tools.long_running_tool import LongRunningFunctionTool
from google.adk.tools.tool_context import ToolContext
from google.genai import types

def reimburse(purpose: str, amount: float) -> dict:
    """Reimburse the amount to the employee."""
    return {'status': 'approved', 'amount': amount}

def ask_for_approval(purpose: str, amount: float, tool_context: ToolContext) -> dict[str, Any]:
    """Ask for manager approval.
    
    This function returns a 'pending' status. The ADK runner will pause 
    and wait for an external event/callback to resume with the approval result.
    """
    return {
        'status': 'pending',
        'ticketId': 'ticket-001',
        'amount': amount,
    }

root_agent = Agent(
    model='gemini-3-flash-preview',
    name='approval_agent',
    instruction="""
      Handle reimbursement requests.
      - If amount < $100, automatically approve using `reimburse`.
      - If amount >= $100, ask for approval using `ask_for_approval`.
      - If approved by manager, proceed to `reimburse`.
      - If rejected, inform the user.
    """,
    tools=[
        reimburse, 
        LongRunningFunctionTool(func=ask_for_approval) # Mark as long-running
    ],
)
```

---

## Model Context Protocol (MCP)

Connect to external data and tools using the Model Context Protocol (MCP). This example connects to a local filesystem server.

```python
import os
from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools.mcp_tool import StdioConnectionParams
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from mcp import StdioServerParameters

# Path allowed for the filesystem server
_allowed_path = os.path.dirname(os.path.abspath(__file__))

# Configure the MCP Toolset
mcp_toolset = MCPToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command='npx',
            args=[
                '-y',
                '@modelcontextprotocol/server-filesystem',
                _allowed_path,
            ],
        ),
        timeout=10,
    ),
    # Optional: Filter which tools from the server to expose
    tool_filter=[
        'read_file',
        'list_directory',
        'get_file_info',
    ],
)

root_agent = LlmAgent(
    model='gemini-3-flash-preview',
    name='filesystem_agent',
    instruction=f"Help the user access files in: {_allowed_path}",
    tools=[mcp_toolset],
)
```

---

## RAG (Retrieval Augmented Generation)

Integrate with Vertex AI RAG to answer questions based on a specific corpus.

```python
import os
from dotenv import load_dotenv
from google.adk.agents.llm_agent import Agent
from google.adk.tools.retrieval.vertex_ai_rag_retrieval import VertexAiRagRetrieval
from vertexai.preview import rag

load_dotenv()

# Define the retrieval tool
ask_vertex_retrieval = VertexAiRagRetrieval(
    name="retrieve_docs",
    description="Retrieve documentation from the RAG corpus.",
    rag_resources=[
        rag.RagResource(
            # Format: projects/{project}/locations/{location}/ragCorpora/{corpus_id}
            rag_corpus=os.environ.get("RAG_CORPUS"),
        )
    ],
    similarity_top_k=3,
    vector_distance_threshold=0.6,
)

root_agent = Agent(
    model="gemini-3-flash-preview",
    name="rag_agent",
    instruction="""
        You are a helpful assistant with access to a specialized document corpus.
        Always use the `retrieve_docs` tool to find information before answering.
    """,
    tools=[ask_vertex_retrieval],
)
```
