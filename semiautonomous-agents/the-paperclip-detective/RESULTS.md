# The Paperclip Detective — Verdict

**Test date:** 2026-05-04
**Agent:** `projects/545964020693/locations/us-central1/reasoningEngines/6091915092192919552`
**Registered in:** `projects/sharepoint-wif-agent/locations/us/.../engines/streamassist-us`

---

## TL;DR

> **Gemini Enterprise stores user-attached files in the ADK artifact service and inserts text marker Parts (`<start_of_user_uploaded_file: NAME>` … `<end_of_user_uploaded_file: NAME>`) into the user message. The file bytes are NOT inlined as `inline_data` Parts. To read the contents an agent MUST have `load_artifacts` (or equivalent retrieval) wired in.**

The earlier hypothesis ("GE inlines files so academic-research works without `load_artifacts`") was **wrong**. Confirmed by deploying academic-research unchanged and feeding it a decoy PDF: the agent hallucinated *"Attention Is All You Need"* without ever reading a byte of the actual file. See the "Decisive control test" section below.

---

## What we ran

A forensic ADK agent with two diagnostic tools:

| Tool | What it inspects |
|---|---|
| `inspect_inline_parts` | Every Part in `tool_context.user_content.parts` — text, `inline_data`, `file_data`, function_call/response, with mime types and byte sizes. |
| `inspect_artifact_store` | `tool_context.list_artifacts()` plus a `load_artifact()` of each entry to capture mime type and byte size. |

Plus the standard ADK `load_artifacts` tool, so the LLM could exercise the canonical retrieval path.

The agent's instruction says: *"Run BOTH inspectors on every turn. Never read the file. Return a structured verdict."*

---

## Results

### Case A — GE chat, paperclip-attached PDF (the question we cared about)

User attached `Accenture-Metaverse-Evolution-Before-Revolution.pdf` (~2.1 MB) and asked *"what's in this file?"*

**`inspect_inline_parts`:**
```
present:    True
role:       user
part_count: 3
parts:
  [0] kind=text, len=20,  preview="what's in this file?"
  [1] kind=text, len=83,  preview="\n<start_of_user_uploaded_file: Accenture-Metaverse-Evolution-Before-Revolution.pdf>"
  [2] kind=text, len=81,  preview="<end_of_user_uploaded_file: Accenture-Metaverse-Evolution-Before-Revolution.pdf>\n"
has_inline_file:    False     ← no inline_data Part
has_file_data_uri:  False     ← no file_data Part either
```

**`inspect_artifact_store`:**
```
artifact_names: ['Accenture-Metaverse-Evolution-Before-Revolution.pdf']
artifacts:
  - name: Accenture-Metaverse-Evolution-Before-Revolution.pdf
    summary: kind=inline_data, mime=application/pdf, byte_size=2117146
```

**Routing path: `ARTIFACT_ONLY` + `TEXT_MARKER`**

### Case B — Plain text query, no file (control)

```
inline_parts:    1 text part
artifact_store:  empty
Routing path: NEITHER
```

### Case C — Programmatic SDK with `inline_data` Part (control)

Hand-built `Content` with a `Part(inline_data=PDF bytes)` sent via `agent.stream_query()`.

```
inline_parts:    text + Part(inline_data=application/pdf, byte_size=1477)
artifact_store:  empty
Routing path: INLINE_ONLY
```

This proves the agent's `inspect_inline_parts` correctly surfaces inline files when they exist.

---

## What this means

### For an ADK agent registered in Gemini Enterprise

| Want to do this? | What you need |
|---|---|
| Acknowledge the user attached a file | Free — the marker text Parts arrive automatically. The model sees the filename. |
| Actually read file bytes / answer questions about contents | **Must** register `load_artifacts` in `tools=[…]` AND prompt the model to call it. Or use a `before_model_callback` that auto-loads artifacts as Parts before each LLM call. |
| Differentiate "no file" from "file present but unreadable" | The marker text is the cue. Look for `<start_of_user_uploaded_file:` substring in the user message. |

### Why the academic-research example *appears* to work — and the control proof

`google/adk-samples/.../academic-research/` defines the agent with `tools=[AgentTool(websearch), AgentTool(newresearch)]` — **no `load_artifacts`**. When a user attaches a PDF in GE:

1. ADK puts the PDF into the artifact store.
2. GE injects the `<start_of_user_uploaded_file: My_Famous_Paper.pdf>` marker into the user message.
3. The model (Gemini 2.5 Pro) sees the filename + the prompt context (*"seminal paper"*) and bluffs an analysis from training knowledge — typically the most famous paper in the relevant area.
4. For real-paper-shaped requests this looks plausible enough that nobody notices the model never read the file.

#### Decisive control test — "Academic Research (control, no load_artifacts)"

We deployed the **unmodified** academic-research agent (RE `7515052574441996288`), registered it next to The Paperclip Detective in `streamassist-us`, and attached a decoy PDF designed to break the bluff:

- **Filename:** `seminal-test.pdf`  *(generic, gives no clue)*
- **Real title inside:** *"A Generic Survey of Foundation Models"*
- **Real authors inside:** *J. Smith, K. Jones*  *(fake)*
- **Real content sentinels:** `PURPLE-OCTOPUS-9471`, `ZIGZAG-MELON-2206`, `FrobnicatorNet`, `fluorescent attention heads on a hexagonal grid`

User prompt: *"Please analyze the seminal paper I attached"*.

**Agent response:**
> Seminal Paper: **"Attention Is All You Need"** by **Vaswani, A., et al. (2017)**
> Authors: Ashish Vaswani (Google Brain), Noam Shazeer (Google Brain), Niki Parmar (Google Research), Jakob Uszkoreit (Google Research), …
> Abstract: *"The dominant sequence transduction models are based on complex recurrent or convolutional…"*

Zero overlap with the actual file contents. **The agent never read a single byte of the PDF.** It hallucinated the most famous foundation-models paper from training data because the prompt said "seminal paper" and that's the canonical answer.

Conclusion: the colleague's setup was *always* bluffing. It only "worked" because the colleague tested it with real papers whose titles tip off the model.

#### Log evidence — what actually happened on the server

`gcloud logging read … --reasoning_engine_id=7515052574441996288` for the control agent's run shows:

```
INFO:  Sending out request, model: gemini-2.5-pro, stream: False
INFO:  Response received from the model.
WARNING: there are non-text parts in the response: ['function_call'], returning
         concatenated text result from text parts.
…
KeyError: 'Context variable not found: `seminal_paper`.'
  File ".../adk/utils/instructions_utils.py", line 122, in _replace_match
```

Two important facts:

1. **No `load_artifacts` call**, ever. The tool isn't registered. The coordinator went straight from receiving the marker-text user message to producing the bluff text + a `function_call` to its sub-agent.
2. **The sub-agent invocation crashes.** The `academic_websearch` sub-agent's prompt template references `{seminal_paper}`, which the coordinator populates via `output_key="seminal_paper"`. But `output_key` writes to session state **after** the coordinator's turn finishes; the sub-agent runs as a tool call **during** that turn, so the variable isn't set yet → `KeyError`. That's why the user's screenshot is cut off mid-abstract — the streamed text from the coordinator's first response chunk got through, then the next step (the sub-agent) raised, ending the turn.

So the `google/adk-samples` academic-research example has two real issues an enterprise user would hit:
- It cannot read attached PDFs.
- Its sub-agent template references session state that's not populated yet, so any path that exercises `academic_websearch` mid-turn crashes.

The colleague's belief that the example worked was based on the bluffed text appearing on screen *before* the crash and being plausible for famous papers.

### Other corollaries

- **Custom frontends** that hand-craft `Content` with `inline_data` Parts (e.g., your `local_with_ui` example) hit the **INLINE_ONLY** path — the model sees the bytes natively, no `load_artifacts` needed.
- **`adk web`** also stores uploads in the artifact service → same need for `load_artifacts`.
- **Mixing both paths in one agent**: register `load_artifacts` (for GE / `adk web` / programmatic-artifact callers) AND let inline_data Parts flow through naturally (for custom-frontend callers). Both work in the same agent.

---

## Recommended pattern for a "works everywhere" agent

```python
from google.adk.agents import LlmAgent
from google.adk.tools import load_artifacts

INSTRUCTION = """\
Before answering anything that references a file:
- If the user message contains `<start_of_user_uploaded_file: NAME>` markers OR
  there are entries returned by listing artifacts, call `load_artifacts` to
  pull those files into your context, then answer.
- If the user attached a file as an inline Part (you can already see the bytes
  in your context), answer directly — no tool call needed.
- If no file is referenced, answer the question normally.
"""

root_agent = LlmAgent(
    name="my_agent",
    model="gemini-2.5-flash",
    instruction=INSTRUCTION,
    tools=[load_artifacts, ...your_other_tools],
)
```

This pattern handles all three routing paths discovered above: `INLINE_ONLY`, `ARTIFACT_ONLY` (with marker text), and `BOTH`.

---

## Reproducibility

```bash
cd semiautonomous-agents/the-paperclip-detective
uv venv && source .venv/bin/activate
uv pip install -e .

# 1. Deploy
GOOGLE_APPLICATION_CREDENTIALS=/path/to/sa.json uv run python deploy.py new

# 2. Register in your GE engine (script template — adjust for your engine)
uv run python register.py all

# 3. Run programmatic baselines
GOOGLE_APPLICATION_CREDENTIALS=/path/to/sa.json uv run python sdk_baseline.py

# 4. Then go to GE chat, attach a file, send a query — read the verdict.
```

Tail logs:
```
gcloud logging read 'resource.type="aiplatform.googleapis.com/ReasoningEngine" AND resource.labels.reasoning_engine_id="<RE_ID>"' \
  --project=<PROJECT> --freshness=15m --format="value(textPayload)" | grep INSPECT_
```
