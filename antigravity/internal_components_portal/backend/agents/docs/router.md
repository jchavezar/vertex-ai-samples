# Intent Router & Orchestrator

The nerve center of the Internal Components Portal. The router architecture consists of two main pieces: a lightweight **Intent Classifier** and a robust **Stateful Orchestrator**.

## The Architecture
Instead of hardcoding rules, we use `gemini-2.5-flash` for lightning-fast zero-shot intent classification. Once the classifier determines the user's need, the `DeloitteRouterAgent` (a custom Google ADK `BaseAgent`) dynamically pipes the user's execution Context to the appropriately specialized Proxy loop.

## Key Logic Snippets

**1. The Lightning-Fast Classifier**
Located in [`router_agent.py`](../router_agent.py). This agent exists strictly to evaluate history and return a single structural string (`SEARCH`, `ACTION`, or `SERVICENOW`).

```python
    system_instruction = """
You are a highly efficient Intent Router for an Enterprise Security Proxy. You evaluate the full conversation history to determine the user's current intent.

- **SEARCH**: ...
- **ACTION**: ...
- **SERVICENOW**: ...
"""
    agent = LlmAgent(
        name="router_agent",
        model="gemini-2.5-flash",
        instruction=system_instruction
    )
```

**2. The ADK 2.0 Custom Workflow Orchestrator**
Located in [`agent.py`](../agent.py). The `DeloitteRouterAgent` subclasses `BaseAgent` directly, letting us write Python code that intercepts the execution path asynchronously without losing context.

```python
class DeloitteRouterAgent(BaseAgent):
    """
    Stateful Router Agent orchestrating ServiceNow and Search using ADK 2.0
    """
    @override
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        
        # We implicitly run the classifier in the background
        async for event in self.classifier_agent.run_async(ctx):
            pass # Suppressed from the UI
            
        intent_result = ctx.session.state.get("detected_intent")
        intent = intent_result.intent if intent_result else "SEARCH"
        
        # Route processing natively based on Intent!
        if intent == "SERVICENOW":
            ctx.session.state["current_route"] = "SERVICENOW"
            async for event in self.servicenow_agent.run_async(ctx):
                yield event # Piped to the UI!
```
