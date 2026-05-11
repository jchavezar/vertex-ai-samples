"""docgen-agent — researches a topic with Google Search, then writes a
summary back to chat. If the user asked for a PDF, also saves a
downloadable artifact that Gemini Enterprise renders as a chip.

    docgen_agent (LlmAgent — name shown in GE)
    ├── tool: AgentTool(search_agent)   — wrapped LlmAgent w/ google_search
    └── tool: generate_pdf_report       — saves PDF artifact

Notes:
* `google_search` cannot share a single LlmAgent with other tools, so
  research lives in its own agent and is invoked via `AgentTool`. Using
  a `SequentialAgent` instead leaks the researcher's full transcript
  (incl. the search response) into the writer's prompt — bloats tokens,
  bleeds the researcher's output format into the chat reply, and
  intermittently times out GE's `widgetStreamAssist`.
* `load_artifacts` is intentionally NOT registered. The chip appears via
  GE's `widgetListSessionFileMetadata?filter=AI_GENERATED` poll — no
  re-injection of the bytes is needed.
* Pinned to `gemini-2.5-flash`. Gemini 3 previews emit a `function_call`
  for the server-side `google_search`; ADK 1.0 tries to dispatch it
  client-side and raises "Tool 'google_search' not found.".
"""
from __future__ import annotations

import os

from google.adk.agents import LlmAgent
from google.adk.tools import google_search
from google.adk.tools.agent_tool import AgentTool

from .tools import generate_pdf_report

AGENT_MODEL = os.environ.get("DOCGEN_AGENT_MODEL", "gemini-2.5-flash")


SEARCH_AGENT_INSTRUCTION = """\
You are a research helper invoked as a tool. Use `google_search` (1–3
focused queries) to gather current facts, then return findings in this
exact format:

TOPIC: <one-line statement of what was researched>
KEY FINDINGS:
- <fact with concrete numbers / names / dates>
- ...
SECTIONS (suggested):
- <section heading>: <what to cover, 1 short sentence>
- ...
SOURCES:
- <Title> | <URL>
- ...

Hard limits: ≤ 8 KEY FINDINGS, ≤ 5 SECTIONS, ≤ 8 SOURCES, ≤ 800 words.
No prose paragraphs, no Markdown, no commentary outside this template.
Do not call any tool except `google_search`.
"""


ROOT_INSTRUCTION = """\
You are Doc Gen. Workflow on every user message:

1. **Call `search_agent`** with the user's question. It returns a
   TOPIC / KEY FINDINGS / SECTIONS / SOURCES block — your only ground
   truth.

2. **Reply in chat** with a clean 2–4 paragraph summary. Cite sources
   inline as `[1]`, `[2]` matching the SOURCES order.

3. **If the user asked for a downloadable file** (triggers: "pdf",
   "report", "document", "downloadable", "export", "save this as",
   "send me a file"), ALSO call `generate_pdf_report` with:
     - `title`: a clean human title (no slugs, no extension).
     - `sections`: 3–6 `{"heading", "body", "bullets"?}` entries built
       from the SECTIONS hints. Body is 1–3 short paragraphs separated
       by blank lines.
     - `sources`: copy SOURCES as `[{"title", "uri"}, ...]`.

   On `status="ok"`, finish with one short sentence naming the report
   in bold, e.g. "I've attached **F1 Miami GP Recap.pdf** — see the
   chip above the input box." Use the `filename` from the tool result;
   GE renames the visible chip to `file_<timestamp>.pdf`, so this
   sentence is the user's only signal of what the document is.

   On `status="error"`, relay the error message verbatim.

Follow-up Q&A ("which teams advanced?") is text-only — no PDF.
Never invent facts. If the search agent returned nothing useful, say so.
"""


search_agent = LlmAgent(
    name="search_agent",
    model=AGENT_MODEL,
    description="Researches a question with Google Search and returns concise structured findings.",
    instruction=SEARCH_AGENT_INSTRUCTION,
    tools=[google_search],
)


root_agent = LlmAgent(
    name="docgen_agent",
    model=AGENT_MODEL,
    description=(
        "Researches a topic with Google Search and replies with a summary. "
        "On request, also generates a downloadable PDF report."
    ),
    instruction=ROOT_INSTRUCTION,
    tools=[
        AgentTool(agent=search_agent),
        generate_pdf_report,
    ],
)
