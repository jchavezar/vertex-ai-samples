# docgen-agent

A small Google ADK agent that:

1. Researches a topic with the built-in `google_search` tool.
2. Writes a grounded summary back to the chat.
3. *On request*, generates a PDF and saves it as a session artifact so
   **Gemini Enterprise renders a download chip** in the chat bubble.

```
docgen_agent (LlmAgent — name shown in GE)
├── tool: AgentTool(search_agent)   ← LlmAgent w/ google_search
└── tool: generate_pdf_report       ← saves PDF artifact (reportlab)
```

## Why this shape (and not SequentialAgent)

`google_search` cannot share a single `LlmAgent` with other tools, so
research must live in its own agent.

A `SequentialAgent(researcher → writer)` was the first attempt and
failed: the writer step inherited the researcher's full transcript
(function_call + ~11k-token search response). The writer either
mimicked the researcher's rigid output format in the chat reply,
refused to call its own tools, or pushed Gemini Enterprise's
`widgetStreamAssist` past its ~60–120s timeout.

Wrapping the researcher in `AgentTool` instead isolates the search
trace — the orchestrator only sees the clean text return value. End-to-
end latency dropped from a 4-minute timeout to ~22s.

## How the chip appears in GE

`tool_context.save_artifact(...)` lands the PDF in Agent Engine's
managed artifact store. GE's chat UI polls
`widgetListSessionFileMetadata?filter=file_origin_type=AI_GENERATED` and
renders the new file as a download chip with a `downloadUri`. No
`load_artifacts` call is needed; including it just re-injects the bytes
into the model context for no benefit.

> **Chip-label limitation.** GE always names the visible chip
> `file_<microsecond_timestamp>.pdf`, regardless of the filename we set
> on `save_artifact` or `Blob.display_name`. The agent compensates by
> stating the logical filename in bold in its chat reply (e.g.
> "I've attached **f1_miami_recap.pdf** below."). Renaming the chip
> itself would require a private GE upload endpoint not exposed in the
> public Discovery Engine SDK.

## Why `gemini-2.5-flash`, not `gemini-3-flash-preview`

ADK 1.0 doesn't yet handle Gemini 3's server-side `google_search` return
shape. The model emits a `function_call` for `google_search` as
metadata; ADK tries to dispatch it client-side and raises:

```
ValueError: Tool 'google_search' not found.
Available tools:
```

`gemini-2.5-flash` keeps the legacy grounding contract that ADK
understands. Switch back to `gemini-3-flash-preview` once ADK ships the
fix.

## Layout

```
docgen-agent/
├── agent/
│   ├── __init__.py        # exports root_agent
│   ├── agent.py           # search_agent + root_agent (LlmAgent + AgentTool)
│   ├── tools.py           # generate_pdf_report FunctionTool
│   └── pdf.py             # reportlab renderer (pure Python)
├── scripts/
│   ├── test_local.py      # InMemoryRunner end-to-end
│   └── test_remote.py     # stream_query smoke test against deployed AE
├── deploy.py              # vertexai.agent_engines.create / .update
├── register.py            # Discovery Engine v1alpha agent registration
├── pyproject.toml
├── .env.example
└── README.md
```

## Setup

```bash
cd semiautonomous-agents/docgen-agent
cp .env.example .env       # edit GOOGLE_CLOUD_PROJECT, staging bucket, GE engine
uv sync
```

Required env (see `.env.example`):

| Var                       | Example                                       |
|---------------------------|-----------------------------------------------|
| `GOOGLE_CLOUD_PROJECT`    | `vtxdemos`                                    |
| `DEPLOY_LOCATION`         | `us-central1` (Agent Engine region)           |
| `DEPLOY_STAGING_BUCKET`   | `gs://vtxdemos-staging`                       |
| `RUNTIME_GENAI_LOCATION`  | `global` (mapped to `GOOGLE_CLOUD_LOCATION`)  |
| `DOCGEN_AGENT_MODEL`      | `gemini-2.5-flash`                            |
| `GE_PROJECT_ID`           | `vtxdemos`                                    |
| `GE_PROJECT_NUMBER`       | `254356041555`                                |
| `GE_ENGINE_ID`            | your GE engine ID                             |
| `AGENT_ENGINE_RESOURCE`   | filled in after the first `deploy.py` run     |

> **Reserved env warning** — never set `GOOGLE_CLOUD_PROJECT` inside
> `deploy.py`'s `RUNTIME_ENV`. Agent Engine sets it automatically;
> setting it yourself fails the deploy.

## Local sanity check

The PDF renderer is pure Python — exercise it without hitting the LLM:

```bash
uv run python -c "
from agent.pdf import render_pdf, slugify
pdf = render_pdf(
    title='Smoke test',
    sections=[{'heading': 'Hello', 'body': 'world.', 'bullets': ['a', 'b']}],
    sources=[{'title': 'Example', 'uri': 'https://example.com'}],
)
open('out.pdf', 'wb').write(pdf)
"
file out.pdf   # → PDF document, version 1.4
```

End-to-end agent run (requires Vertex AI predict perms on your project,
or run inside the deployment container):

```bash
uv run python scripts/test_local.py "summarize Liga MX this weekend and create a pdf report"
# Writes the produced PDF to ./out/<slug>.pdf
```

## Deploy

The shared deployment container at `.deployment-container/` solves the
two-account credential split (interactive ADC vs. deploy SA):

```bash
sudo docker run --rm \
  -v $(pwd):/workspace \
  -v ~/.secrets/vtxdemos-sa.json:/secrets/sa-key.json:ro \
  -e GOOGLE_APPLICATION_CREDENTIALS=/secrets/sa-key.json \
  -e GOOGLE_CLOUD_PROJECT=vtxdemos \
  -w /workspace --entrypoint /bin/bash \
  deployment-container -c "pip install -q reportlab && python deploy.py new"
```

`reportlab` is installed inline because the base container image doesn't
include it. To bake it in, add `reportlab` to
`.deployment-container/Dockerfile`.

After a successful create, paste the printed `resource_name` back into
`.env` as `AGENT_ENGINE_RESOURCE`. Subsequent runs without `new` call
`agent_engines.update(...)` against that resource.

The deployed `RUNTIME_ENV`:

```python
{
  "GOOGLE_GENAI_USE_VERTEXAI": "true",
  "GOOGLE_CLOUD_LOCATION": "global",
  "DOCGEN_AGENT_MODEL": "gemini-2.5-flash",
}
```

## Register in Gemini Enterprise

```bash
sudo docker run --rm \
  -v $(pwd):/workspace \
  -v ~/.secrets/vtxdemos-sa.json:/secrets/sa-key.json:ro \
  -e GOOGLE_APPLICATION_CREDENTIALS=/secrets/sa-key.json \
  -e GOOGLE_CLOUD_PROJECT=vtxdemos \
  -w /workspace --entrypoint /bin/bash \
  deployment-container -c "python register.py"
```

This `POST`s to:

```
https://discoveryengine.googleapis.com/v1alpha/projects/{GE_PROJECT_NUMBER}
  /locations/global/collections/default_collection/engines/{GE_ENGINE_ID}
  /assistants/default_assistant/agents
```

with body:

```json
{
  "displayName": "Doc Gen",
  "description": "...",
  "icon": {"uri": "..."},
  "adk_agent_definition": {
    "tool_settings": {"tool_description": "..."},
    "provisioned_reasoning_engine": {
      "reasoning_engine": "<AGENT_ENGINE_RESOURCE>"
    }
  }
}
```

then `PATCH ?updateMask=sharingConfig` with `{"sharingConfig": {"scope":
"ALL_USERS"}}` so the agent shows up in everyone's picker.

The SA used to register **must** request the cloud-platform OAuth scope:

```python
google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
```

Without that, the JWT refresh fails with `invalid_scope`.

## Verify in GE

1. Open the GE engine in your browser.
2. Pick **Doc Gen** from the agent list.
3. Send: `give me a summary of what happened this weekend in liga mx and create a pdf report`.
4. Expect a streamed text reply followed by a PDF chip with a download
   icon. The chip label is `file_<timestamp>.pdf` (GE behavior); the
   logical filename is in the agent's reply text.

## Gotchas applied

- **Tool exceptions silently kill `stream_query`.** `generate_pdf_report`
  wraps everything in `try/except → return {"status": "error", ...}`.
- **`GOOGLE_CLOUD_PROJECT` is reserved by Agent Engine** — never set it
  in `RUNTIME_ENV`. Agent Engine injects it.
- **`google_search` cannot share an `LlmAgent` with other tools** — wrap
  it in its own `LlmAgent` and expose via `AgentTool`.
- **Shell `GOOGLE_CLOUD_LOCATION` defaults to a region** that may not
  serve `gemini-3-*` previews. The local test runner overrides it to
  `global` for safety.
- **Discovery Engine REST from a service account** needs the
  cloud-platform OAuth scope explicitly.

## References

- ADK artifacts API: <https://google.github.io/adk-docs/artifacts/>
- ADK builtin tools: <https://github.com/google/adk-python/tree/main/src/google/adk/tools>
- ADK samples (artifact pattern):
  <https://github.com/google/adk-samples/blob/main/python/agents/brand-aligned-presentations/presentation_agent/tools/artifact_utils.py>
