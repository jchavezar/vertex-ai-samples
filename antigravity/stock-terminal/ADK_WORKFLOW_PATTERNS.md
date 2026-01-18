# ADK Workflow Patterns

This document details advanced workflow patterns available in the Google Agent Development Kit (ADK). These patterns demonstrate how to compose agents to build complex, robust applications.

> **Note:** All examples use `gemini-3-flash-preview` as the model.

## Table of Contents
1. [Mixed Workflow: Parallel Workers in Sequence](#mixed-workflow-parallel-workers-in-sequence)
2. [Sequential Pipeline: State Passing](#sequential-pipeline-state-passing)
3. [Loop Workflow: Iteration with Escalation](#loop-workflow-iteration-with-escalation)

---

## Mixed Workflow: Parallel Workers in Sequence

This pattern orchestrates a **ParallelAgent** (performing independent tasks concurrently) within a **SequentialAgent** (executing steps in order). It also demonstrates **Conditional Execution** using `before_agent_callback`.

**Scenario:** A planning agent determines which workers (Math or Code) are needed. The workers run in parallel. Finally, a summary agent aggregates the results.

```python
from typing import Optional
from google.adk.agents import Agent, ParallelAgent, SequentialAgent
from google.adk.agents.base_agent import BeforeAgentCallback
from google.adk.agents.callback_context import CallbackContext
from google.adk.agents.readonly_context import ReadonlyContext
from google.genai import types

# --- 1. Define Callback for Conditional Execution ---
def check_relevance(agent_name: str) -> BeforeAgentCallback:
    """Callback to skip an agent if it's not in the 'execution_agents' state list."""
    def callback(ctx: CallbackContext) -> Optional[types.Content]:
        # 'execution_agents' would be populated by an upstream planner (omitted here)
        # or set manually in the session state.
        if agent_name not in ctx.state.get("execution_agents", []):
            return types.Content(parts=[types.Part(text=f"Skipping {agent_name}.")])
        return None
    return callback

# --- 2. Define Worker Agents ---
code_agent = Agent(
    model="gemini-3-flash-preview",
    name="code_agent",
    instruction="You generate Python code. Ignore other requests.",
    before_agent_callback=check_relevance("code_agent"),
    output_key="code_agent_output", # Save output to shared state
)

math_agent = Agent(
    model="gemini-3-flash-preview",
    name="math_agent",
    instruction="You perform math calculations. Ignore other requests.",
    before_agent_callback=check_relevance("math_agent"),
    output_key="math_agent_output", # Save output to shared state
)

# --- 3. Create Parallel Group ---
# These agents run concurrently if activated
worker_parallel_agent = ParallelAgent(
    name="worker_parallel_agent",
    sub_agents=[code_agent, math_agent],
)

# --- 4. Define Summary Agent ---
def summary_instruction(ctx: ReadonlyContext) -> str:
    """Dynamic instruction accessing state from previous agents."""
    activated = ctx.state.get("execution_agents", [])
    prompt = f"Summarize the execution of: {', '.join(activated)}.\n\n"
    
    if "code_agent" in activated:
        prompt += f"Code Output:\n{ctx.state.get('code_agent_output', '')}\n\n"
    if "math_agent" in activated:
        prompt += f"Math Output:\n{ctx.state.get('math_agent_output', '')}\n\n"
        
    return prompt

execution_summary_agent = Agent(
    model="gemini-3-flash-preview",
    name="execution_summary_agent",
    instruction=summary_instruction,
)

# --- 5. Create Root Sequential Agent ---
# Execution Order: Workers (Parallel) -> Summary (Sequential)
root_agent = SequentialAgent(
    name="plan_execution_agent",
    sub_agents=[worker_parallel_agent, execution_summary_agent],
)
```

---

## Sequential Pipeline: State Passing

This pattern demonstrates a strict 3-stage pipeline where each agent relies on the output of the previous one, utilizing ADK's shared state management.

**Scenario:** Code Generation Pipeline: Writer -> Reviewer -> Refactorer.

```python
from google.adk.agents import Agent, SequentialAgent

# --- Stage 1: Code Writer ---
code_writer = Agent(
    name="CodeWriter",
    model="gemini-3-flash-preview",
    instruction="Write Python code based on the user's request. Output only code.",
    output_key="generated_code", # Writes to state['generated_code']
)

# --- Stage 2: Code Reviewer ---
code_reviewer = Agent(
    name="CodeReviewer",
    model="gemini-3-flash-preview",
    # Reads state['generated_code'] using {placeholder} syntax
    instruction="""
    Review the following code:
    ```python
    {generated_code}
    ```
    Provide a list of improvements or say "No issues".
    """,
    output_key="review_comments", # Writes to state['review_comments']
)

# --- Stage 3: Code Refactorer ---
code_refactorer = Agent(
    name="CodeRefactorer",
    model="gemini-3-flash-preview",
    # Reads both previous outputs
    instruction="""
    Refactor the original code based on the review.
    
    Original:
    ```python
    {generated_code}
    ```
    
    Comments:
    {review_comments}
    
    Output only the refactored code.
    """,
    output_key="refactored_code",
)

# --- Pipeline Orchestrator ---
root_agent = SequentialAgent(
    name="CodePipeline",
    sub_agents=[code_writer, code_reviewer, code_refactorer],
    description="A pipeline that writes, reviews, and refactors code.",
)
```

---

## Loop Workflow: Iteration with Escalation

This pattern uses **LoopAgent** to repeat a task until a condition is met or a limit is reached. It demonstrates how to break the loop early using `EventActions(escalate=True)`.

**Scenario:** A "Poller" loop that runs a task and checks for completion.

```python
from typing import AsyncGenerator
from google.adk.agents import Agent, BaseAgent, LoopAgent, InvocationContext
from google.adk.events import Event, EventActions
from google.genai import types

# --- 1. The Worker Agent ---
worker_agent = Agent(
    name="Worker",
    model="gemini-3-flash-preview",
    instruction="Attempt to solve the user's problem. If you need more information, ask.",
)

# --- 2. The Condition Checker (Custom Agent) ---
class CompletionChecker(BaseAgent):
    """Checks if the task is done and stops the loop."""
    
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        # Logic to determine completion (e.g., check state, last message)
        # For this example, we assume completion if the session state has 'status': 'DONE'
        # or if the user said "stop".
        
        is_done = ctx.session.state.get("status") == "DONE"
        
        if is_done:
            yield Event(
                author=self.name,
                content=types.Content(parts=[types.Part(text="Task completed. Stopping loop.")]),
                # 'escalate=True' tells the parent LoopAgent to stop iterating
                actions=EventActions(escalate=True) 
            )
        else:
             yield Event(
                author=self.name,
                content=types.Content(parts=[types.Part(text="Task ongoing. Continuing loop.")])
            )

checker_agent = CompletionChecker(name="Checker")

# --- 3. The Loop Orchestrator ---
root_agent = LoopAgent(
    name="PollingLoop",
    max_iterations=5, # Safety limit
    sub_agents=[worker_agent, checker_agent],
    # Execution: Worker -> Checker -> Worker -> Checker ...
    # Stops if max_iterations is reached OR Checker emits escalate=True
)
```