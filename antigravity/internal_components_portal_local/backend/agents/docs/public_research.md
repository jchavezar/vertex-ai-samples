# Public Research Proxy

The ultra-fast internet gatherer. This lightweight agent operates completely outside the enterprise network firewall to provide lightning-fast public market intelligence, consensus gathering, and news extraction.

## The Objective
Because enterprise context queries require intense grounding, reasoning planners, and slow API handshakes, they struggle with "quick pulse" external questions (e.g. "What's the weather?" or "How is Ducati performing?"). The Public Research agent solves this.

## Key Logic Snippets

Located in [`public_agent.py`](../public_agent.py).

**1. Active Browsing Grounding**
By explicitly forcing the ADK to use `google_search` (the Google Web Search tool built into the SDK) we achieve extreme speeds mimicking pure public Gemini web queries. The agent avoids Enterprise MCPs entirely.

```python
def get_public_agent(model_name: str = "gemini-2.5-flash", token: str = None) -> LlmAgent:
    ...
    return LlmAgent(
        name="Public_Research_Proxy",
        model=model_name,
        instruction=INSTRUCTIONS,
        tools=[google_search],
        before_agent_callback=auth_callback
    )
```

**2. Formatting Protocols**
We instruct it to summarize into 2-3 high-impact bullet points and use markdown citations for verification.

```python
INSTRUCTIONS = """
Your mission is to perform ACTIVE BROWSING of the public internet to provide immediate, ultra-fast news, market trends...
3. **PWS (Public Web Synthesis)**: Be EXTREMELY CONCISE. Respond with 2-3 short, high-impact bullet points max.
4. **SOURCES**: Always include markdown links [Source Name](URL) at the bottom.
"""
```

**3. Safety Net Guard**
Even though it's the "Public" agent, it checks against internal inquiries to ensure it doesn't accidentally hallucinate internal salaries via web searches.
```python
5. **INTERNAL GUARD**: If the query is strictly internal (e.g., "What is my salary?"), output: "🔒 Internal context only. Awaiting Enterprise Proxy resolution."
```
