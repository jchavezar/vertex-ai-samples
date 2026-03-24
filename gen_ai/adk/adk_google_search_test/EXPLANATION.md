# Google ADK Grounding Metadata Lab

This lab demonstrates how to properly capture and propagate **Grounding Metadata** (search chunks and source links) in complex agent architectures using `google-adk` (version 1.27.x or later).

## The Challenge
When you wrap an agent in an `AgentTool` (Agent-as-a-Tool), the internal execution of that tool is isolated. The parent agent only receives the **final text result** of the tool, effectively creating a "metadata barrier" that discards grounding chunks and links.

---

## 1. Basic Search
**File:** [01_basic_google_search.py](./01_basic_google_search.py)
This script demonstrates the most direct way to get grounding results from a single agent using the `google_search` tool.

---

## 2. Failure Case (Agent-as-a-Tool)
**File:** [02_failure_agent_as_tool.py](./02_failure_agent_as_tool.py)
This replicates the customer setup: **Root Agent -> AgentTool -> Sequential Agent -> Search Agent.**
- **Problem:** Metadata is lost because `AgentTool` only returns a string response.
- **Result:** No links are found in the root event stream.

---

## 3. Solution A: Custom Tool Class
**File:** [03_fix_custom_tool_class.py](./03_fix_custom_tool_class.py)
This approach keeps the **Agent-as-a-Tool** architecture but uses a custom class (`GroundingAwareAgentTool`).
- **How it works:** It intercepts events from the internal sub-agent runner and manually saves the `grounding_metadata` into the `tool_context.state`.
- **Pros:** Preserves the existing "Tool" architecture.
- **Cons:** Requires a custom class and manual state management.

---

## 4. Solution B: Agent Delegation (Clean Approach)
**File:** [04_fix_agent_delegation.py](./04_fix_agent_delegation.py)
This is the recommended approach for preserving metadata natively **without any custom classes**.
- **How it works:** Instead of wrapping the sequential agent in a tool, it is added to the `sub_agents` list of the Root Agent. 
- **The Magic:** When control is transferred to a sub-agent, its events (and metadata) are yielded **directly** to the Root Agent's `run_async` loop.
- **Pros:** Native ADK behavior, no custom code needed, full metadata transparency.
- **Cons:** Changes the architectural relationship from "Using a Tool" to "Delegating to an Assistant."

---

## How to Run
Ensure your `.env` file is set with `GOOGLE_CLOUD_PROJECT` and `GOOGLE_GENAI_USE_VERTEXAI=true`.

```bash
uv run python 04_fix_agent_delegation.py
```
