---
name: building-adk-agents
description: Guides the creation of Google ADK (Agent Development Kit) agents. Use when the user asks to create, configure, or understand ADK agents, workflows, or tools.
---

# Building Google ADK Agents

## When to use this skill
- User wants to create a new ADK agent (Sequential, Parallel, Loop, or LLM Agent).
- User needs to configure ADK tools (Google Search, Custom Python Tools).
- User asks about ADK patterns ("Researcher-Writer", "StoryFlow").
- Reference for ADK concepts (Sessions, State, Runners).

## Mandatory Model Versions
**CRITICAL**: You must ONLY use the following models. NO `gemini-1.5` or `gemini-2.0` (unless flash), and NO `text-bison`:
- **Default**: `gemini-3-flash-preview` (Prioritize this)
- **High-Reasoning**: `gemini-3-pro-preview`
- **Fast/Light**: `gemini-2.5-flash`, `gemini-2.5-flash-lite`

## Structured Output (JSON Schema)
When an agent needs to produce structured data (JSON), **ALWAYS** use `output_schema` with a Pydantic model. This enforces strict JSON output from the model.

**Important**: Use `output_key` to automatically store the parsed JSON in the session state.

### Python Example
```python
from pydantic import BaseModel, Field
from google.adk.agents import LlmAgent

# 1. Define Pydantic Schema
class CapitalOutput(BaseModel):
    capital: str = Field(description="The capital of the country.")
    population: int = Field(description="Population of the capital.")

# 2. Register Agent
structured_capital_agent = LlmAgent(
    name="capital_agent",
    model="gemini-3-flash-preview",
    instruction="You are a Capital Information Agent. Given a country, respond ONLY with JSON.",
    output_schema=CapitalOutput,  # Enforces JSON output format
    output_key="found_capital"    # Stores dict result in ctx.session.state['found_capital']
)
```

### TypeScript Example
```typescript
import { z } from 'zod';
import { Schema, Type } from '@google/genai';
import { LlmAgent } from '@google/adk';

// 1. Define Schema using @google/genai types
const CapitalOutputSchema: Schema = {
    type: Type.OBJECT,
    properties: {
        capital: { type: Type.STRING, description: 'The capital city.' },
    },
    required: ['capital'],
};

// 2. Register Agent
const agent = new LlmAgent({
    name: 'capital_agent',
    model: 'gemini-3-flash-preview',
    instruction: 'Respond with JSON.',
    outputSchema: CapitalOutputSchema,
    outputKey: 'found_capital',
});
```

### Java Example
```java
// Define Schema
Schema capitalOutput = Schema.builder()
    .type("OBJECT")
    .properties(Map.of("capital", Schema.builder().type("STRING").build()))
    .build();

LlmAgent agent = LlmAgent.builder()
    .model("gemini-3-flash-preview")
    .outputSchema(capitalOutput)
    .outputKey("found_capital")
    .build();
```

## Search Fallback Policy
**CRITICAL**: If you cannot find the answer in this skill or your existing knowledge, you **MUST** use the `brave_web_search` tool (available via `brave-search` MCP) to find the latest documentation, error fixes, or examples. **Do not hallucinate** API methods.



## Workflow
[ ] **Define Agent Type**: Determine if you need a single `LlmAgent` or a workflow (`SequentialAgent`, `ParallelAgent`, `LoopAgent`).
[ ] **Define Tools**: Identify necessary tools (Google Search, Custom Python Functions, MCP).
[ ] **Create Agent File**: Scaffold the agent class/definition in Python (or requested language).
[ ] **Setup Runner**: Create the `main` entrypoint with `Runner` and `InMemorySessionService` (or other).
[ ] **Validation**: Ensure type hints in tools are correct for auto-schema generation.

## Instructions
1.  **Read the Docs First**: This skill includes a comprehensive documentation file in `resources/adk_docs.md`. **Always** search or read this file for specific implementation details before guessing.
    - Path: `resources/adk_docs.md` (Relative to this skill)
    - Use `grep_search` or `view_file` on `resources/adk_docs.md` to find snippets.

2.  **Core Components**:
    - **`LlmAgent`**: Basic unit. Needs `name`, `instruction`, and optional `tools`.
    - **`SequentialAgent`**: Chain of agents. Output of Agent A -> Context for Agent B.
    - **`ParallelAgent`**: Run multiple agents at once. Good for research.
    - **`LoopAgent`**: Iterative tasks. Needs a completion condition.

3.  **Tooling**:
    - Use `@tool` decorator for custom Python functions.
    - Docstrings and Type Hints are **MANDATORY**. They define the schema.

4.  **State Management**:
    - Use `ctx.session.state` to pass data between agents in a workflow.

## Resources
- [ADK Documentation (Local)](resources/adk_docs.md)
