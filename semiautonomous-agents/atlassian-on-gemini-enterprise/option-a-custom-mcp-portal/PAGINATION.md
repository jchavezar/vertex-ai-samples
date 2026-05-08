# Pagination in the Jira MCP Portal

How we keep an LLM agent paginating across thousands of Jira issues without blowing up the prompt size or hitting Gemini's per-minute token quota.

---

## 1. The two layers

There are **two independent pagination layers** in this stack. Both must be solved; solving one doesn't solve the other.

| Layer | Where it lives | What it bounds | What happens if you skip it |
|---|---|---|---|
| **Server pagination** | `jira_server/server.py` (MCP tools) | The size of a *single tool response* | One tool call returns 1000+ issues = 5 MB blob, instant context overflow |
| **LLM context pagination** | `adk_agent/agent.py` (`before_model_callback`) | The size of *every prompt* sent to the model | Each turn replays all prior tool responses → quadratic input-token growth → 429 RESOURCE_EXHAUSTED |

The two compose like this:

```
              ┌──────────────────────┐
   user query │  agent (Gemini LLM)  │── decides which tool to call
              └──────────────────────┘
                       │
                       ▼  function_call(getJiraIssuesReport, page=N)
              ┌──────────────────────┐
              │  MCP server (FastAPI)│── server pagination: 50 issues/page
              └──────────────────────┘
                       │
                       ▼  function_response: 50 issues + nextPageToken
              ┌──────────────────────┐
              │   ADK session log    │── stores EVERY response forever
              └──────────────────────┘
                       │
                       ▼  before_model_callback rewrites this slice
              ┌──────────────────────┐
              │  next LLM prompt     │── only the latest page in full + stubs
              └──────────────────────┘
```

---

## 2. Server pagination (already in place)

The MCP server's `getJiraIssuesReport` and `searchJiraIssuesUsingJql` tools page through Jira's REST API server-side and return:

```
METADATA: PageCount=50, HasMore=True, NextToken=CkljcmVhd...
ISSUE: Key=SMP-610 | Status=To Do | ...
ISSUE: Key=SMP-609 | ...
... (50 issues)
```

The agent's instruction tells it to loop:

> If `NextToken != NONE`, call the tool again with `nextPageToken` set to that value. Repeat until `NextToken=NONE`.

Without this, a "list all 1000 Ducati issues" request would return one giant tool response (~120 K tokens) that overflows Gemini in a single shot. With it, each tool *call* is bounded at ~6 K tokens.

Sufficient for one-shot questions. **Not** sufficient for multi-page loops, because of layer 2.

---

## 3. The LLM-context blowup (why server pagination alone isn't enough)

ADK is conversational. On every turn it replays the *full session history* — every prior `function_call` and `function_response` — back into the LLM prompt so the model has continuity. This is what makes "remember what we discussed two messages ago" work.

But during a pagination loop, each turn adds another ~6 K token tool response to the history:

```
Turn 1 input:  [system 3K] [user 0.1K] [tool_call] [tool_resp: 6K]                                    ≈   9 K
Turn 2 input:  [system 3K] [user 0.1K] [tool_call] [tool_resp: 6K] [tool_call] [tool_resp: 6K]        ≈  15 K
Turn 3 input:  ...                     [tool_resp: 6K] [tool_resp: 6K] [tool_resp: 6K]                ≈  21 K
Turn 5 input:                                                                                         ≈  33 K
Turn 10 input:                                                                                        ≈  63 K
```

Cumulative input tokens consumed across N turns ≈ `N(N+1)/2 × 6 K` — **quadratic growth**.

In `vtxdemos`, `gemini-3-flash-preview` falls under the catch-all preview-model TPM bucket (estimated 30–60 K input TPM). At that ceiling:

| Page count | Issues | Cumulative input tok | Status |
|---|---|---|---|
| 2 | 100 | ~25 K | borderline |
| 3 | 150 | ~50 K | hits 429 in this project |
| 5 | 250 | ~110 K | far past quota |

That's exactly what you saw — 87 issues then a stall.

---

## 4. The intuition that doesn't work (and why)

> "ADK has session memory — old pages should stay in memory, not in the LLM context."

This is the most common assumption and it's wrong. ADK has two concepts that sound related but do different things:

| Concept | What it stores | Goes into LLM context? |
|---|---|---|
| **Session** (`InMemorySessionService`, `VertexAiSessionService`) | Every event in the current conversation: tool calls, responses, model outputs | **YES — full replay every turn** |
| **Memory service** | Cross-session long-term recall, vector-store of past sessions | NO, only when explicitly retrieved by a tool |

Neither one automatically trims the current turn's prompt. If you want old data to stay in storage but be omitted from the LLM input, you have to do it yourself with a callback.

---

## 5. The fix: `before_model_callback`

ADK exposes lifecycle hooks. `before_model_callback` is invoked *immediately before* each LLM request and gets a mutable `LlmRequest`. Mutating `llm_request.contents` rewrites what the model sees — without touching the underlying session.

The relevant code in `adk_agent/agent.py`:

```python
PAGINATING_TOOLS = {"getJiraIssuesReport", "searchJiraIssuesUsingJql"}
KEEP_RECENT_FULL = 1   # how many recent paginated responses to keep verbatim

def trim_paginated_history(callback_context, llm_request):
    contents = llm_request.contents or []
    paginating_idxs = []
    for i, content in enumerate(contents):
        for part in (content.parts or []):
            fr = getattr(part, "function_response", None)
            if fr and fr.name in PAGINATING_TOOLS:
                paginating_idxs.append(i)
                break

    # keep the last N in full, stub the rest
    to_stub = paginating_idxs[:-KEEP_RECENT_FULL]
    for i in to_stub:
        for part in (contents[i].parts or []):
            fr = getattr(part, "function_response", None)
            if fr and fr.name in PAGINATING_TOOLS:
                summary = _summarize_tool_response(fr.response)
                fr.response = {"result": f"<earlier {fr.name} page omitted: {summary}>"}
```

Wired on the agent:

```python
root_agent = Agent(
    ...
    tools=[jira_toolset],
    before_model_callback=trim_paginated_history,
)
```

The stub keeps the key range (`SMP-610..SMP-561`) so the model knows what was already fetched and doesn't loop.

After the rewrite, prompts look like this regardless of how many pages have been fetched:

```
Turn 1 input:  [system 3K] [user 0.1K]                                       [tool_resp: 6K full]   ≈  9 K
Turn 2 input:  [system 3K] [user 0.1K] [stub 0.05K]                          [tool_resp: 6K full]   ≈  9 K
Turn 5 input:  [system 3K] [user 0.1K] [stub] [stub] [stub] [stub]           [tool_resp: 6K full]   ≈  9 K
Turn 20 input: [system 3K] [user 0.1K] [stub × 19]                           [tool_resp: 6K full]   ≈ 10 K
```

**Linear in page count, dominated by stubs of ~50 tokens each.** At 1000 pages you're still under 60 K input tokens per turn.

---

## 6. What you keep and what you lose

**Kept:**
- Full session log on disk (Vertex AI Session Service still has every byte; debug, replay, fine-tuning data still intact).
- Key range from each old page (in the stub) → model knows it's covered ground.
- The model's running tally / answer it built up across pages (those are model turns, not tool responses, so the callback doesn't touch them).

**Lost:**
- The model can't re-quote raw descriptions from a stubbed page.
- Cross-page synthesis on raw text ("find common phrases across all 1000 descriptions") is degraded.
- If you bump `KEEP_RECENT_FULL` to 1, only the most recent page is fully in context.

For listing, counting, ID extraction, paginated reporting — fine.
For deep cross-page text analysis — keep more pages full, or run a dedicated summarizer in a follow-up tool call.

---

## 7. Tuning knobs

| Knob | Where | Effect |
|---|---|---|
| `KEEP_RECENT_FULL` | `agent.py` | How many recent pages stay verbatim. Higher = more cross-page reasoning, more tokens. |
| `PAGINATING_TOOLS` | `agent.py` | Which tool names get trimmed. Add new MCP tools here if they paginate. |
| Server `sysparm_limit` | `jira_server/server.py` (`getJiraIssuesReport`) | Issues per server page. Bigger pages = fewer turns, but bigger single response. |
| `_summarize_tool_response` shape | `agent.py` | What the stub looks like. Add aggregate stats here (status counts, project counts) if the model needs them across pages. |

---

## 8. Why not just request a quota increase?

Quota increase is the *cleanest* fix and you should still file one if you can. But:

- It ceilings raise the threshold; they don't change the quadratic shape.
- A 100× quota lets you do ~10× more pages before the same wall.
- The callback fixes the math, not just the ceiling. Prompts stay constant-size at any quota, which is also better for latency and cost — every turn pays for input tokens.

The two are complementary: quota increase + context trimming is the production setup.

---

## 9. Reusable beyond Jira

`trim_paginated_history` is generic — point `PAGINATING_TOOLS` at any MCP tool name that returns paginated chunks (ServiceNow, Confluence search, BigQuery row pages, etc.). Same pattern works.

The summarizer (`_summarize_tool_response`) is tuned to extract `XXX-NNN`-style keys; replace the regex for other domains (e.g., `INC\d+` for ServiceNow).
