# Architecture — report-generator

## Why these choices

### 1. ADK SequentialAgent over a single LlmAgent

A single LlmAgent calling tools in a loop produces inconsistent reports
because it has to hold "research", "outline", and "voice" in one context.
Splitting into a sequential pipeline lets each agent be optimised for one
job (planner: structured decomposition; researcher: search recall; writer:
voice + citations).

### 2. Researcher and writer are SEPARATE agents

ADK's `google_search` tool **cannot** coexist with `output_schema` on the
same `LlmAgent`. The undocumented `bypass_multi_tools_limit=True` flag
exists in `google_search_tool.py` but is brittle. So:

- Researcher: `tools=[google_search]`, no schema, free-text output.
- FindingsParser: schema-typed coercion of researcher output.
- Writer: `output_schema=ResearchReport`, no tools.

This separation is also what the official `google/adk-samples/deep-search`
agent does.

### 3. LoopAgent over fixed-iteration research

The Critic emits a `Critique{grade, comment, follow_up_queries}` JSON. The
`escalation_checker` callback breaks the loop on `pass`. This is more
token-efficient than always running 3 rounds, and produces better coverage
on topics that need it.

### 4. Tag-then-resolve citations

Writers asked to produce numbered `[1]`, `[2]` inline tend to misnumber
under structured-output JSON. The fix:

1. Writer emits `<cite source="src-3"/>` — references the *source id* not
   a footnote number.
2. `citation_replacement_callback` walks every block, rewrites tags, and
   reorders the `sources` list to match citation order. Uncited sources
   move to the end.

This guarantees footnote numbering matches reading order regardless of
what order the writer produced sections in.

### 5. WeasyPrint over ReportLab

WeasyPrint takes HTML+CSS Paged Media. That means:

- Real typography (web fonts, drop-caps, hyphenation).
- TOC with leader dots and page numbers via
  `target-counter(attr(href), page)`.
- Running headers via `string-set` on section headings.
- Cover page is a full-bleed `<section>` with gradient background.

ReportLab would require us to build all of this in Python. WeasyPrint's
only cost is the native lib install (`libpango`, `cairo`, `harfbuzz`).

### 6. Renderer is a BaseAgent, not a tool

PDF rendering is deterministic I/O — no value in spending tokens. A
`BaseAgent._run_async_impl` reads `state['report_for_render']`, calls the
pure `render_report_to_pdf(...)` function, and writes the path back to
state. The same function is what `run_local.py` and tests would import
directly.

## State contract

| Key                 | Producer                | Type              |
|---------------------|-------------------------|-------------------|
| `plan`              | Planner                 | `ResearchPlan`    |
| `findings_raw`      | Researcher              | str               |
| `findings`          | FindingsParser          | `ResearchFindings`|
| `critique`          | Critic                  | `Critique`        |
| `outline`           | SectionPlanner          | str (JSON list)   |
| `report`            | Writer → CitationReplacer | `ResearchReport` |
| `report_for_render` | CitationReplacer        | `ResearchReport`  |
| `pdf_path`          | PdfRenderer             | str               |

## Failure modes

- **Empty grounding** — Gemini occasionally returns no `grounding_chunks`
  (rate-limit or low-confidence query). Critic will grade `fail` and the
  loop retries with rewritten queries.
- **Schema validation error on Writer** — If the writer emits malformed
  JSON, the SequentialAgent surfaces the validation error. Mitigation: keep
  writer prompt strict; use Gemini 3 Flash (more reliable structured
  output than 2.5).
- **WeasyPrint missing native libs** — `OSError: cannot load library
  'libgobject-2.0-0'`. Install via `apt`. Documented in README.

## Extension points

- **Vector retriever** — add a `vector_search` function tool on a separate
  sub-agent for proprietary-doc augmentation. Wrap it as `AgentTool` to
  mix with the `google_search` researcher.
- **Multimodal sources** — add an `image_describer` step that downloads
  representative images per section and embeds them in the PDF.
- **Bibliography format** — swap the renderer for a Typst pipeline if you
  need CSL bibliographies.
- **Charts** — add a `matplotlib` sub-agent that emits SVGs to embed in
  callout blocks.
