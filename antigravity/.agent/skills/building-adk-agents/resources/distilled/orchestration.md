# ⛓️ ADK Orchestration & Multi-Agent Workflows

## 1. Multi-Agent Hierarchy
Agents can be nested. A "Sub-Agent" looks like a tool to the parent.

```python
lead_agent = LlmAgent(
    name="manager",
    sub_agents=[coder_agent, reviewer_agent],
    instruction="Coordinate the creation and review of the feature."
)
```

## 2. Workflow Agents (Deterministic)
Use these when logic should be strictly controlled, not just "decided" by an LLM.

### SequentialAgent
Runs agents A, then B, then C.
```python
from google.adk.agents import SequentialAgent

pipeline = SequentialAgent(
    name="writing_pipeline",
    agents=[research_agent, writer_agent, editor_agent]
)
```

### ParallelAgent
Runs all agents simultaneously.
```python
from google.adk.agents import ParallelAgent

competitors = ParallelAgent(
    name="market_research",
    agents=[google_researcher, bing_researcher, internal_db_searcher],
    instruction="Compare results from different sources."
)
```

### LoopAgent
Iterative logic until a condition is met.
```python
from google.adk.agents import LoopAgent

refiner = LoopAgent(
    name="code_fixer",
    agent=debug_agent,
    completion_condition=lambda ctx: ctx.session.state.get("is_fixed", False),
    max_loops=3
)
```

## 3. Custom Agents
For ultimate control, extend `BaseAgent` and implement `_call_internal`. This allows you to write standard Python code to decide which sub-agent to call.

---
*Reference: adk-docs/docs/agents/multi-agents.md*
