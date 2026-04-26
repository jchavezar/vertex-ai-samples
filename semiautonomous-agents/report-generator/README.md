# report-generator

Multi-agent **research → write → render** pipeline that turns a topic into a
fully-cited, magazine-quality PDF. Built on **Google ADK** with **Gemini 3
Flash**, Google Search grounding, and **WeasyPrint** for typography.

The pattern mirrors `google/adk-samples/python/agents/deep-search` and adds a
custom PDF-rendering stage backed by CSS Paged Media.

## Pipeline

```
SequentialAgent: ReportGenerator
├── Planner               LlmAgent  → ResearchPlan         (state['plan'])
├── ResearchLoop  (×3)    LoopAgent
│   ├── Researcher        LlmAgent + google_search          (state['findings_raw'])
│   ├── FindingsParser    LlmAgent  → ResearchFindings      (state['findings'])
│   └── Critic            LlmAgent  → Critique              (state['critique'])
│        └── escalation_checker breaks loop on grade='pass'
├── SectionPlanner        LlmAgent  → outline               (state['outline'])
├── Writer                LlmAgent  → ResearchReport        (state['report'])
├── CitationReplacer      LlmAgent + after_callback         (rewrites <cite> → [N])
└── Renderers             ParallelAgent  (concurrent, no added latency)
    ├── PdfRenderer       BaseAgent (WeasyPrint)            (state['pdf_path'])
    └── DocxRenderer      BaseAgent (python-docx)           (state['docx_path'])
```

Plus a sibling **`IntakeEditor`** (`agent/intake.py`) — a conversational
LlmAgent run by the UI server to gather the `ReportBrief` (topic, audience,
length, tone, visuals, formats, OneDrive flag) before kicking off the
pipeline above.

### Why this shape

- **Researcher must be alone with `google_search`** — ADK forbids mixing the
  built-in `google_search` tool with `output_schema` or other tools (see
  `bypass_multi_tools_limit` in `google_search_tool.py`). So the researcher
  emits free text, and a **separate** `FindingsParser` typed-coerces it
  into `ResearchFindings`.
- **Tag-then-replace citations** — the writer emits `<cite source="src-N"/>`
  inline and a callback rewrites them to `[N]` and reorders the source list
  to match citation order. Same pattern as the official ADK deep-search
  sample.
- **Renderer is a plain `BaseAgent`** — PDF rendering is pure I/O, no need
  to spend tokens on it.

## Quickstart

```bash
cd semiautonomous-agents/report-generator
python -m venv .venv && source .venv/bin/activate

# WeasyPrint native deps (Debian/Ubuntu)
sudo apt-get install -y libpango-1.0-0 libpangoft2-1.0-0 libharfbuzz0b libffi-dev

pip install -r requirements.txt
cp .env.example .env  # then edit for your project

python run_local.py "Vertex AI Vector Search vs. Pinecone in 2026"
# → outputs/20260420-153012-vertex-ai-vector-search-vs-pinecone-in-2026.pdf
```

## ADK web UI

```bash
adk web
# open http://localhost:8000 → pick `report-generator`
```

## Custom UI (chat + live pipeline diagram)

A FastAPI server with SSE streaming + a single-page Tailwind/Cytoscape UI
sits in `server/` and `ui/`:

```bash
.venv/bin/python -m server.main
# → http://localhost:8775
```

What you get:

- **Chat-driven intake** — the `IntakeEditor` agent walks you through topic,
  audience, length, tone, visuals, formats, and OneDrive upload, then emits
  a validated `ReportBrief` JSON the UI captures.
- **Live agent diagram** — Cytoscape graph of the actual ADK topology
  (`/api/agent-graph`); active node highlights and "marching ants" edge
  animation track pipeline progress in real time.
- **Parallel renderer outputs** — PDF and DOCX cards appear when ready,
  one-click download, optional one-click OneDrive upload via the ms365 MCP.

Endpoints:

| Path | Purpose |
|---|---|
| `GET  /` | UI |
| `GET  /api/agent-graph` | Topology JSON `{nodes, edges}` |
| `POST /api/intake` | SSE — conversational intake turns |
| `POST /api/generate` | SSE — pipeline progress + final paths |
| `GET  /api/files/{name}` | Download a generated PDF/DOCX |
| `POST /api/ms365-upload` | On-demand OneDrive upload (separate from pipeline so it never adds render latency) |

The MS365 upload calls the **ms365 MCP** server at `MS365_MCP_URL`
(default `http://localhost:8080/mcp`) using the `sp_upload_file` tool.

## Deploy

```bash
# Local container (recommended — WeasyPrint needs native libs):
#   gcloud builds submit + Cloud Run

# Or managed Agent Engine (PDF rendering disabled — schemas only):
python deploy.py
```

## Configuration (env)

| Var | Default | Notes |
|---|---|---|
| `GOOGLE_GENAI_USE_VERTEXAI` | `True` | required |
| `GOOGLE_CLOUD_PROJECT` | — | required |
| `GOOGLE_CLOUD_LOCATION` | `global` | Gemini 3 preview lives here |
| `REPORT_PLANNER_MODEL` | `gemini-3-flash-preview` | |
| `REPORT_RESEARCH_MODEL` | `gemini-3-flash-preview` | |
| `REPORT_WRITER_MODEL` | `gemini-3-flash-preview` | bump to `gemini-3.1-pro-preview` for harder topics |
| `REPORT_MAX_ITERATIONS` | `3` | research loop cap |
| `REPORT_OUTPUT_DIR` | `./outputs` | PDF destination |

## Files

```
report-generator/
├── agent/
│   ├── agent.py            # SequentialAgent wiring (root_agent)
│   ├── intake.py           # IntakeEditor — conversational ReportBrief gatherer
│   ├── schemas.py          # Pydantic types — pipeline contract (incl. ReportBrief)
│   ├── prompts.py          # All instructions in one place
│   ├── callbacks.py        # escalation_checker, citation_replacement
│   ├── renderer.py         # PdfRendererAgent (WeasyPrint)
│   ├── docx_renderer.py    # DocxRendererAgent (python-docx)
│   └── templates/
│       ├── report.html.j2  # Jinja2 layout
│       └── report.css      # CSS Paged Media — cover, TOC, footnotes
├── server/
│   ├── main.py             # FastAPI: SSE intake + generate, MS365 upload
│   └── graph.py            # Topology extractor for Cytoscape
├── ui/
│   └── index.html          # Chat + live pipeline diagram (Tailwind + Cytoscape CDN)
├── run_local.py            # InMemoryRunner CLI
├── deploy.py               # Vertex Agent Engine deploy
├── requirements.txt
├── .env.example
└── docs/ARCHITECTURE.md
```

## Algorithms used (from the research scan)

- **Outline-first writing** — section_planner runs before writer (STORM,
  ADK deep-search both enforce this).
- **Iterative deepening with reflection** — LoopAgent + Critic +
  EscalationChecker; max 3 iterations.
- **Tag-then-resolve citations** — `<cite source="src-N"/>` → `[N]`,
  driven by `grounding_metadata.grounding_chunks`.
- **Credibility tiering** — `primary | reputable | secondary | unknown`
  rendered as colored badges in the source list.
- **Structured intermediate** — every stage hands off Pydantic JSON; the
  PDF renderer is a pure function of `ResearchReport`.

## Reference reading

- [Google ADK docs](https://adk.dev/)
- [ADK deep-search sample](https://github.com/google/adk-samples/tree/main/python/agents/deep-search)
- [WeasyPrint](https://weasyprint.org/)
- [Gemini grounding with Google Search](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/grounding/grounding-with-google-search)
