# Analytics & Latency Agents

A specialized subgroup of agents working off-line from the primary proxy pathways. These agents are uniquely tasked with digesting their own telemetry data!

## The Objective
In the Observability Nexus, we need to ask intelligent questions about the exact milliseconds and tool execution stacks that govern performance. Instead of writing complex SQL queries against a dashboard, we built "Chat with Latency" agents.

## Key Logic Snippets

Located in [`latency_chat_agent.py`](../latency_chat_agent.py) and [`analyze_latency_agent.py`](../analyze_latency_agent.py).

**1. Data Grounding (In-Memory JSON Injection)**
Instead of relying on an enterprise vector search, these agents are injected with a massive `context_preamble` representing pure raw Execution JSON collected during active proxy flows.

```python
def chat_with_latency_data(messages: list, history_data: list, analysis_result: str = None) -> str:
    ...
    # [Context: History JSON] is pushed into the prompt!
    context_preamble = f"### EXECUTION DATA CONTEXT:\n{json.dumps(history_data, indent=2)}"
    combined_prompt = f"{context_preamble}\n\nUSER QUESTION: {user_prompt}"
```

**2. The Execution Insight Persona**
Strict instructions force the model to behave as an elite performance engineer, ensuring that it attributes slowdowns specifically to TTFT (Time To First Token) or MCP tool roundtrips.

```python
    system_instruction = f"""
You are the "Execution Insight" AI, an expert specialized in analyzing AI performance telemetry for the Internal Zero-Leak Security Proxy.
- **Accuracy**: Base your answers strictly on the provided JSON data. If the user asks about the "slowest step," find the actual duration in the telemetry.
- **Traceability**: Mention specific session IDs or query titles when referring to data.
EXPERT CAPABILITIES:
- Identify bottlenecks: "The SharePoint file read took 4.5s, representing 60% of the total time."
- Compare models: "Flash 2.5 consistently shows 30% lower TTFT than the alternative."
"""
```

**3. Cross-Session Analysis**
Found in `analyze_latency_agent.py`, rather than answering an ad-hoc chat question, this tool generates a structured markdown report by summarizing the `history_data` array to find anomalies across *every* session recorded.
