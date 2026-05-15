# spatial_on_ge — Spatial Understanding agent for Gemini Enterprise

ADK agent that detects objects in user-attached images and renders an
annotated copy (coloured bounding boxes + labels) **inline in the Gemini
Enterprise chat UI**.

This is the modern rewrite of [`gen_ai/adk/spatial_understanding`](../../gen_ai/adk/spatial_understanding/).
The original used `gemini-1.5-flash` (deprecated) and reinvented image
plumbing with a custom `prepare_image_for_analysis` tool. This version uses
the canonical ADK pattern that GE actually understands: **artifacts +
`load_artifacts`**.

```
        ┌─────────────────────────────────────────────────────────────┐
        │  Gemini Enterprise chat (paperclip → image upload)          │
        └────────────────────────────┬────────────────────────────────┘
                                     │ streamAssist
                                     ▼
        ┌─────────────────────────────────────────────────────────────┐
        │  Vertex AI Agent Engine  (this repo, deploy.py)             │
        │                                                             │
        │   user_message = "find the cats" + <start_of_user_uploaded… │
        │   artifact_store = {"cats.jpg": image/jpeg, 850 KB}         │
        │                                                             │
        │   1. detect_objects("cats")                                 │
        │      ├─ load_artifact("cats.jpg")                           │
        │      ├─ Gemini 2.5 Flash → JSON bounding boxes              │
        │      ├─ PIL draws boxes                                     │
        │      └─ save_artifact("annotated_cats.jpeg")                │
        │   2. load_artifacts(["annotated_cats.jpeg"])                │
        │      └─ ADK appends inline_data Part to next LLM turn       │
        │   3. LLM emits the inline_data Part in its reply            │
        └────────────────────────────┬────────────────────────────────┘
                                     │ inline_data, mime=image/jpeg
                                     ▼
        ┌─────────────────────────────────────────────────────────────┐
        │  GE chat renders the JPEG inline (mime starts with image/)  │
        └─────────────────────────────────────────────────────────────┘
```

---

## The "trick": rendering a generated image in the GE chat

We confirmed the routing experimentally with [`the-paperclip-detective`](../the-paperclip-detective/RESULTS.md):

> Gemini Enterprise stores user-attached files in the ADK artifact service and
> inserts text marker Parts (`<start_of_user_uploaded_file: NAME>` …
> `<end_of_user_uploaded_file: NAME>`) into the user message. The file bytes
> are **NOT** inlined as `inline_data` Parts. To read the contents an agent
> MUST have `load_artifacts` (or equivalent retrieval) wired in.

The same machinery works in **reverse** for sending images back:

1. A tool calls `await tool_context.save_artifact("annotated.jpeg", types.Part.from_bytes(data=jpeg_bytes, mime_type="image/jpeg"))`.
2. ADK auto-injects an "artifacts available: [annotated.jpeg]" notice into the
   next LLM turn (this is what `load_artifacts_tool` does under the hood).
3. The model calls `load_artifacts(["annotated.jpeg"])`.
4. ADK appends a `Part(inline_data=jpeg_bytes, mime_type="image/jpeg")` to the
   LLM context for that turn.
5. The model echoes that Part in its response.
6. The Discovery Engine `streamAssist` v1alpha schema carries
   `groundedContent.content.parts[].inlineData{data, mimeType}` natively, and
   the GE chat renders any part whose mime starts with `image/` inline.

There is **no special "attachment" wrapper** to set, no signed URLs, no base64
markdown, no GCS public buckets. Just `save_artifact` + `load_artifacts`.

---

## Layout

```
spatial_on_ge/
├── agent/
│   ├── __init__.py            # exports root_agent
│   └── agent.py               # detect_objects tool + LlmAgent
├── scripts/
│   └── test_local.py          # offline smoke test (no Agent Engine, no GE)
├── deploy.py                  # → Vertex AI Agent Engine
├── register.py                # → Gemini Enterprise (Discovery Engine v1alpha)
├── pyproject.toml
├── .env.example
└── README.md
```

---

## End-to-end deploy (vtxdemos)

### 0. Prerequisites

- ADC configured for `vtxdemos` (`gcloud auth application-default login`)
- `uv` installed
- A Gemini Enterprise app exists in `vtxdemos`. We use
  `agentspace-testing_1748446185255` by default.

### 1. Install

```bash
cd vertex-ai-samples/semiautonomous-agents/spatial_on_ge
uv venv && source .venv/bin/activate
uv pip install -e .
```

### 2. Configure

```bash
cp .env.example .env
$EDITOR .env
```

Defaults already point at `vtxdemos` (project number `254356041555`) and the
`agentspace-testing` engine. The only field you'll add later is
`AGENT_ENGINE_RESOURCE`, after step 3.

### 3. Deploy to Agent Engine

```bash
uv run python deploy.py new
```

When the script finishes, it prints the resource name. Paste it into `.env`:

```
AGENT_ENGINE_RESOURCE="projects/254356041555/locations/us-central1/reasoningEngines/<id>"
```

Future code or instruction tweaks are applied in place:

```bash
uv run python deploy.py             # auto-detects AGENT_ENGINE_RESOURCE → update
uv run python deploy.py update      # explicit
```

### 4. Register in Gemini Enterprise

```bash
uv run python register.py           # registers + shares with ALL_USERS
# or:
uv run python register.py agent     # register only
uv run python register.py share <agent-resource-name>
```

This POSTs to:

```
POST https://discoveryengine.googleapis.com/v1alpha/projects/{GE_PROJECT_NUMBER}
     /locations/global/collections/default_collection/engines/{AS_APP}
     /assistants/default_assistant/agents
```

with the standard `adk_agent_definition.provisioned_reasoning_engine` payload.

### 5. Try it

1. Open the GE app in the chat UI:
   `https://vertexaisearch.cloud.google.com/home/cid/...` (the URL for
   `agentspace-testing` in `vtxdemos`).
2. Choose **Spatial Object Detector** from the agent picker.
3. Click the paperclip, attach an image, and ask
   *"find every car"* (or whatever you want detected).
4. The agent calls `detect_objects`, then `load_artifacts`, and the chat
   renders the annotated image inline. A short text summary follows.

---

## Local smoke test (no Agent Engine round-trip)

```bash
uv run python scripts/test_local.py path/to/photo.jpg "find the dogs"
```

Streams the agent's events to stdout and writes any `annotated_*.jpeg` it
produces to disk so you can eyeball the boxes.

---

## How `detect_objects` works

```python
async def detect_objects(object_description: str, tool_context: ToolContext) -> dict:
    # 1. Find the most recent user-uploaded image artifact (skips our own outputs).
    name, part = await _pick_source_image(tool_context)
    image_bytes = part.inline_data.data

    # 2. Ask Gemini for normalised 2-D bounding boxes (0..1000).
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[f"Detect: {object_description}", types.Part.from_bytes(...)],
        config=GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=list[BoundingBox],
            ...,
        ),
    )

    # 3. Draw boxes with PIL.
    for bbox in response.parsed:
        # box_2d is [y_min, x_min, y_max, x_max] normalised to 0..1000
        draw.rectangle(...)
        draw.text(...)

    # 4. Save the annotated image as a NEW artifact.
    await tool_context.save_artifact(
        filename="annotated_<source>.jpeg",
        artifact=types.Part.from_bytes(data=jpeg_bytes, mime_type="image/jpeg"),
    )

    return {"status": "ok", "count": N, "annotated_artifact": "annotated_..."}
```

The agent's instruction tells the model to call `load_artifacts` after a
successful detection, passing the `annotated_artifact` name from the tool
result. ADK does the rest.

---

## Differences vs the original `gen_ai/adk/spatial_understanding`

| | Original | This version |
|---|---|---|
| Model | `gemini-1.5-flash` (deprecated) | `gemini-2.5-flash` (env-overridable) |
| Image input pattern | Custom `prepare_image_for_analysis` that read `tool_context.user_content.parts` looking for `inline_data`, then renamed it to `user_uploaded_image.jpeg` | Direct `tool_context.list_artifacts()` + `load_artifact()` — matches the actual GE delivery path (artifact + text marker) |
| Image output rendering | Saved `image_with_bounding_boxes.jpeg` artifact and then ran a Flet desktop UI (`main.py`) to fetch and display it | `save_artifact` + built-in `load_artifacts` tool → GE renders the inline_data Part natively in chat |
| GE registration | Inline in `to_agentspace.py` next to deployment | Separate `register.py` driven by `.env` |
| Frontend | Required Flet desktop app | None — the GE chat is the frontend |
| Region | us-central1 hardcoded | Deploy region configurable; runtime model location pinned via `GOOGLE_CLOUD_LOCATION` env (defaults to `global`) |
| Update flow | Append-only script with manual `agent_engines.list(filter=…)` lookup | `deploy.py update` / auto-update when `AGENT_ENGINE_RESOURCE` set |

---

## Operational notes

- **Artifact service in production.** Agent Engine wires up a managed artifact
  service automatically. No `GcsArtifactService` configuration is required in
  this repo; saved artifacts persist for the session and survive across turns.
- **Model location.** `gemini-2.5-flash` works in `us-central1` and `global`.
  If you swap in `gemini-3-flash-preview` or `gemini-3.1-pro-preview`, set
  `RUNTIME_GENAI_LOCATION=global` in `.env` (already the default) and redeploy.
- **Reserved env vars.** Agent Engine sets `GOOGLE_CLOUD_PROJECT` itself. Do
  NOT pass it via `env_vars=` in `agent_engines.create(...)` or the deploy
  will reject it.
- **Logs.**
  ```bash
  RE_ID=<reasoning_engines/<id>>
  gcloud logging read \
    'resource.type="aiplatform.googleapis.com/ReasoningEngine"
     AND resource.labels.reasoning_engine_id="'$RE_ID'"' \
    --project=vtxdemos --freshness=15m \
    --format="value(textPayload)" | grep -E "spatial-on-ge|ERROR"
  ```
- **Sharing.** `register.py` defaults to sharing with `ALL_USERS` of the GE
  app. To restrict, edit the `share()` payload (`sharingConfig.scope`).
- **Turning the model into the orchestrator.** The agent itself uses
  `SPATIAL_AGENT_MODEL`. Detection runs on `SPATIAL_DETECTION_MODEL`. Both
  default to `gemini-2.5-flash` so nothing surprises you on first run.

---

## Background

- ADK Artifacts: <https://adk.dev/artifacts/>
- `load_artifacts_tool` source: <https://github.com/google/adk-python/blob/main/src/google/adk/tools/load_artifacts_tool.py>
- Reference image-out sample (`logo_create`): <https://github.com/google/adk-samples/blob/main/python/agents/marketing-agency/marketing_agency/sub_agents/logo_create/agent.py>
- GE forensics on file routing: [`semiautonomous-agents/the-paperclip-detective/RESULTS.md`](../the-paperclip-detective/RESULTS.md)
- streamAssist request-shape gotchas: see project memory `streamassist_request_shape.md`
