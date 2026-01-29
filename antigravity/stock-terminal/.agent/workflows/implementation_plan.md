---
description: Deep Debugging and Latency Optimization Plan
---
# Implementation Plan - Gemini 2.5 Upgrade & Deep Debugging

The goal is to ensure all models are Gemini 2.5+, remove Live API, fix the chat "hangs", and provide real-time terminal debugging for latency optimization.

## Current Status
- Gemini 2.5 models enforced in `main.py` and frontend.
- Live API removed.
- Chat "Analyze Apple" returns recommendations, but "Full Analysis" hangs for 4+ mins with empty workflow/trace.

## Tasks

### 1. Deep Debugging System (Terminal)
- [ ] Create a `latency_logger.py` utility to print high-visibility debug info to the terminal.
- [ ] Integrate `latency_logger` into `main.py` (chat endpoint, agent creation).
- [ ] Integrate `latency_logger` into `factset_agent.py` (tool calls, SSE status).
- [ ] Add "Phase" markers (e.g., "[PHASE] Auth", "[PHASE] Topology", "[PHASE] Execution") to trace the request lifecycle.

### 2. Fix "Full Analysis" Hang & Workflow Visibility
- [ ] Investigate why `ParallelAgent` execution doesn't emit initial events (topology/status) quickly.
- [ ] Ensure the `event_generator` in `main.py` is not blocking on heavy initialization before starting the stream.
- [ ] Check if `SequentialAgent` (used in parallel workflow) is delaying the first event.
- [ ] Verify frontend `handleSendChat` correctly parses multiple events in a single chunk (though `ndjson` should handle this).

### 3. Latency Optimization
- [ ] Identify bottlenecks via the new debugging system.
- [ ] Check if FactSet token refresh or agent cache is causing delays.
- [ ] Add TTFT (Time to First Token) logging.

## Implementation Details

### Debugging Utility
I will add a high-visibility terminal logging system using colors (if possible) or just clear prefixes.

```python
# Proposed format
[TRACE][12:00:01.450] Request Received: "Full Analysis Apple"
[TRACE][12:00:01.455] Auth: Validating FactSet Token...
[TRACE][12:00:01.550] Auth: Token Valid (Refreshed in 95ms)
[TRACE][12:00:01.560] Routing: Parallel Workflow Selected
[TRACE][12:00:01.800] Topology: Generated (15 nodes, 22 edges)
[TRACE][12:00:02.000] Stream Start: Sending initial topology...
```

### Fixing the Hang
The empty Workflow tab suggests the `topology` event is missing.
In `main.py`, I'll check:
```python
# line ~1350 in main.py
if agent:
    topology = generate_topology(agent)
    yield json.dumps({"type": "topology", "content": topology}) + "\n"
    # ...
```
If `generate_topology` is called BEFORE the first yield, it might be slow if the agent structure is complex. I'll move it into the generator or wrap it.

Actually, the subagent showed 180s+ thinking and NO workflow. This implies the generator might not even be starting or is stuck inside `agent.run_async`.

Wait, the screenshot `apple_analysis_recommendations` SHOWED recommendations? No, the subagent said: "The assistant responded promptly with a set of recommendations".
Then "full analysis" caused the hang.

If "full analysis" is a text message, it should hit `run_parallel_comparison` tool or the `SWITCH_TO_PARALLEL_WORKFLOW` logic.

Let's check `SWITCH_TO_PARALLEL_WORKFLOW` logic in `main.py`.
