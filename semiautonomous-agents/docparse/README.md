<div align="center">

# docparse

**Chart-aware PDF → Markdown → RAG agent inside Gemini Enterprise**

A two-stage pipeline that turns PDF reports into a Gemini Enterprise agent: a Cloud Run service extracts each page (preserving chart structure as Markdown tables), and an ADK agent answers questions over the extracted markdown via Vertex AI RAG Engine. Deployed end-to-end with one script.

[![composite](https://img.shields.io/badge/eval%20composite-92.9%25-137333?style=for-the-badge)](./eval/RESULTS.md)
[![vs DE streamAssist](https://img.shields.io/badge/vs%20DE%20streamAssist-%2B11.9pts-1A73E8?style=for-the-badge)](./eval/RESULTS.md)
[![one-button deploy](https://img.shields.io/badge/-./deploy.sh-EA8600?style=for-the-badge)](./deploy.sh)

</div>

---

## TL;DR

```bash
cp .env.example .env && $EDITOR .env       # fill in PROJECT
./deploy.sh                                 # provisions everything
gcloud storage cp ~/Reports/*.pdf gs://${PROJECT}-docparse-in/
                                            # ...then chat in your Gemini Enterprise app
```

That's the whole flow. `deploy.sh` runs eight steps (buckets → extractor → ingestion → chunking → RAG corpus → agent → registration), each idempotent. **The full eval that justifies this stack lives in [`eval/RESULTS.md`](./eval/RESULTS.md)**.

---

## Why this exists

Gemini Enterprise's first-party **GCS connector** routes PDFs through Document AI Layout Parser. As of April 2026, it produces "a descriptive block of text" for charts — no axes, no series, no values. A 100-cell stacked bar chart becomes useless prose, and questions like *"What was Q1 2020 mentions?"* can never be answered.

`docparse` does two things instead:

1. **Extract** every page with the Gemini 3 family — region detection, body OCR, **structured chart tables**, photo captions, diagram-as-mermaid. Output is one Markdown file per PDF.
2. **Serve** that markdown through an ADK agent backed by Vertex AI RAG Engine, registered cross-project in your Gemini Enterprise app.

We benchmarked this stack against 7 alternatives on a 216-question eval. **It scored 92.9% composite — +12 points over Discovery Engine `streamAssist` on the same markdown, +29 points over raw-PDF ingestion.** [Full table here](./eval/RESULTS.md).

---

## Folder layout

```
docparse/
├── README.md           ← you are here
├── deploy.sh           ← one-button orchestrator (extractor + corpus + agent + GE registration)
├── .env.example        ← every env var; copy to .env
│
├── extractor/          ← stage 1: PDF → Markdown (Cloud Run + Eventarc)
│   ├── deploy.sh           ← step 1-3 of deploy.sh
│   ├── Dockerfile
│   ├── pyproject.toml
│   └── src/docparse/...
│
├── agent/              ← stage 2: Markdown → answers (ADK + Agent Engine + GE)
│   ├── deploy.py           ← step 7 of deploy.sh
│   ├── register_agent.py   ← step 8 of deploy.sh
│   ├── pyproject.toml
│   └── docparse_agent/
│       └── agent.py        ← the actual ADK Agent (~30 lines)
│
└── eval/               ← evaluation harness + the leaderboard that justifies the stack
    ├── RESULTS.md          ← 8 strategies × 216 questions, with sample answers
    ├── questions.json      ← 216 ground-truth Q&A pairs
    ├── run_rag_engine.py   ← strategy runner
    ├── judge.py            ← Claude-based grader
    ├── build_per_page.py   ← markdown → per-page chunks (used by deploy.sh too)
    └── build_results_md.py ← regenerates RESULTS.md from judged/ JSONs
```

---

## Architecture

```mermaid
flowchart LR
    USER([end user]) -->|chat| GE[Gemini Enterprise app]
    GE -->|streamAssist| AGENT
    AGENT -->|VertexAiRagRetrieval| RAG[(RAG Engine corpus<br/>per-page chunks)]
    RAG --> AGENT
    AGENT -->|grounded answer| GE

    subgraph EXTRACTION[Stage 1 · extractor — Cloud Run]
        IN[(GCS in)] -->|object.finalized| EA{{Eventarc}}
        EA --> CR[docparse service<br/>region-detect, chart-extract,<br/>photo-caption, page-OCR<br/>via Gemini 3]
        CR --> OUT[(GCS out<br/>foo.txt + foo.report.json)]
    end

    OUT -.deploy.sh: split per-page + import.-> RAG

    subgraph SERVE[Stage 2 · agent — Vertex AI Agent Engine]
        AGENT[ADK agent<br/>gemini-3-flash-preview]
    end

    classDef bucket fill:#e8f0fe,stroke:#1a73e8,color:#000
    classDef service fill:#fef7e0,stroke:#f9ab00,color:#000
    classDef ge fill:#e6f4ea,stroke:#137333,color:#000
    class IN,OUT,RAG bucket
    class CR,AGENT service
    class GE ge
```

**The two stages are decoupled.** You can use the extractor on its own (the markdown is in your GCS bucket), or you can point the agent at a corpus of markdown you produced some other way. `deploy.sh all` provisions both; `deploy.sh extractor` and `deploy.sh agent` run them independently.

---

## Why this configuration won — the eval in 60 seconds

We tested 8 combinations of extraction × indexing × retrieval. Headline numbers:

| Stack | Composite |
|---|---:|
| 🥇 **docparse markdown + per-page chunks → RAG Engine → Gemini 3 flash** *(this repo)* | **92.9%** |
| docparse markdown + whole-doc chunks → RAG Engine → Gemini 3 flash | 87.4% |
| docparse markdown → Discovery Engine `streamAssist` (any parser config) | 75–81% |
| **raw PDFs** → RAG Engine → Gemini 3 flash *(no docparse)* | **63.8%** |

Two axes, both matter independently:
- **Extraction layer:** docparse vs raw PDF = +29 pts
- **Retrieval layer:** RAG Engine + Gemini vs Discovery Engine `streamAssist` = +6 pts on the same markdown

Per-question type, the win is concentrated in math (+18 pts) and chart-cell lookups (+16 pts) — the two categories that defeat naive RAG. Page-anchored questions are also +3 because the per-page chunker prepends `# <doc> — Page N` so "on page 11" matches via plain embedding.

**Full eval (leaderboard, per-category, 6 sample showcases, all 216 questions with verdicts): [`eval/RESULTS.md`](./eval/RESULTS.md)**.

---

## Deploy

### Prerequisites

- A GCP project with billing enabled.
- An authenticated `gcloud` session: `gcloud auth login && gcloud auth application-default login`.
- `uv` installed: `curl -LsSf https://astral.sh/uv/install.sh | sh`.
- (Optional) A Gemini Enterprise app you want to register the agent in.

### Steps

```bash
cd docparse
cp .env.example .env
$EDITOR .env                    # set PROJECT, optionally GE_PROJECT_ID + AS_APP

./deploy.sh                     # all eight steps end-to-end
```

The script writes `RAG_CORPUS_NAME` and `REASONING_ENGINE_RES` back into `.env` after creation, so subsequent runs are idempotent (no duplicate corpora, agent updates instead of recreating).

### Use the pipeline

After `./deploy.sh`:

```bash
gcloud storage cp ~/your-report.pdf gs://${PROJECT}-docparse-in/
# Eventarc fires → Cloud Run extracts → markdown lands in gs://${PROJECT}-docparse-out/
# Re-run the agent step to import new pages and update the corpus:
./deploy.sh agent
```

Then open your Gemini Enterprise app — the `docparse RAG agent` is in the agent picker, shared with `ALL_USERS`. Citations link straight back to the source GCS URI for the page that grounded each fact.

### Run just one stage

```bash
./deploy.sh extractor    # buckets, IAM, Cloud Run, Eventarc
./deploy.sh agent        # per-page split → RAG corpus → Agent Engine
./deploy.sh register     # cross-project register in Gemini Enterprise
```

---

## How the agent passes grounding back to the chat UI

There's no special grounding API between layers. Each layer treats grounding as a first-class structured field and just preserves it.

```
RAG retrieval API
   ↓ chunks[] = { text, source_metadata{ uri, ... } }
ADK tool wrapper (VertexAiRagRetrieval)
   ↓ packages chunks as a function_response
Gemini 3 flash
   ↓ answer text + groundingMetadata{ chunks, supports → segment offsets }
ADK Event
   ↓ groundingMetadata preserved verbatim
Agent Engine stream_query
   ↓ JSON event to caller
Gemini Enterprise streamAssist
   ↓ rewrites to textGroundingMetadata{ references[], segments[] }
GE web UI
   ↓ footnote markers + globe-icon citation chips with source GCS URI
```

If the model didn't actually use any retrieved chunk, no `groundingMetadata` is emitted, no citations appear in the UI. The absence of a citation is a real signal — not a UI bug.

---

## Critical gotcha: Gemini 3 preview is `global`-only

Agent Engine deploys to a regional endpoint (e.g. `us-central1`). If you set `model="gemini-3-flash-preview"` and don't override the runtime location, the genai client builds the API URL from `us-central1` and 404s. Fix is in [`agent/deploy.py`](./agent/deploy.py):

```python
RUNTIME_ENV_VARS = {
    "GOOGLE_CLOUD_LOCATION": "global",
    "GOOGLE_GENAI_USE_VERTEXAI": "true",
    ...
}
```

These env vars are **not** persisted by `agent_engines.update()` — re-supply on every update call. Verify with:

```bash
gcloud ai reasoning-engines describe <id> --region=<region>
# look for deploymentSpec.env — both vars must be present
```

---

## Observability

`enable_tracing=True` on the ADK app emits OpenTelemetry spans to Cloud Trace:

```
https://console.cloud.google.com/traces/list?project=<DEPLOY_PROJECT_ID>
```

Filter by service name containing `reasoning` or `agent`, time range last 15 min. You'll see a span waterfall: agent root → tool call to RAG retrieval → Gemini generate. Each model call shows tokens, latency, prompt/response.

---

## Re-running the eval

The eval is a one-off harness against a specific corpus, not production code. To benchmark a new strategy:

```bash
cd eval/

# 1. Run your strategy through the 216 questions → runs/<your-label>.json
uv run --with google-genai python run_rag_engine.py \
    "projects/.../locations/us-central1/ragCorpora/..." your-label

# 2. Judge it with Claude → judged/<your-label>.json
uv run --with 'anthropic[vertex]' python judge.py runs/your-label.json your-label

# 3. Regenerate the leaderboard markdown
python build_results_md.py
```

The 216 ground-truth Q&A pairs in `questions.json` are tied to two specific PDFs (Accenture-Metaverse + SE-Competitive-Intelligence). To eval against a different corpus, replace `questions.json` with your own ground truth and the harness still works.

---

## What's not covered (honest limits)

- **Live vision at query time.** The agent answers chart and photo questions from text retrieved at runtime, not by looking at pixel data. Vision work happens once at extraction. If docparse misreads a chart cell, the agent will confidently repeat the wrong value.
- **Cross-document reasoning.** Questions in the eval are mostly within-doc lookups. "Compare X in report A vs report B" hasn't been stress-tested.
- **Languages other than English.** Not in the eval.
- **Scanned / handwritten / low-quality PDFs.** Docparse expects clean digital reports.

The next ~5pt improvement would come from a re-ranker on top of `top_k=20` retrieval — see the [`eval/RESULTS.md` "what's not covered"](./eval/RESULTS.md) section for the headroom analysis.
