# Shutter Vibe Engine

A working customer-demo prototype that re-imagines Shutterstock's discovery
surface on top of Google's latest Gemini embedding models.

> Built for a Shutterstock customer engagement (April 2026). Lead model:
> `gemini-embedding-001` (text, GA) with `gemini-embedding-2-preview`
> (multimodal: text + image + audio + video + PDF) for the cross-modal demos.

## What's inside

```
shutter-vibe-engine/
├── research/                       Deep-dive notes used to build the demo
│   ├── gemini_embeddings_master.md   API, models, pricing, code samples, benchmarks
│   ├── shutterstock_landscape.md     Catalog scale, AI initiatives, pain points
│   └── use_cases.md                  15 ranked demo ideas + meeting narrative
├── data/
│   └── stock_corpus.py             Synthetic Shutterstock-like asset captions
├── demos/                          Runnable capability probes (each is standalone)
│   ├── 01_text_basics.py             First call: embeddings, shape, normalization
│   ├── 02_task_types.py              All 8 task types side-by-side
│   ├── 03_matryoshka.py              Dimension sweep 3072 → 128, recall vs cost
│   ├── 04_vibe_search.py             Headline demo: natural-language asset search
│   ├── 05_multilingual.py            Same brief in EN/ES/JA/DE/AR → same hits
│   ├── 06_brand_safety.py            Zero-shot per-customer policy filtering
│   ├── 07_moodboard_cluster.py       Brief → diverse mood-board clusters
│   ├── 08_code_retrieval.py          Bonus: CODE_RETRIEVAL_QUERY task type
│   └── 09_multimodal_preview.py      Image + text in one vector (gemini-embedding-2)
├── run_all.py                      Orchestrator: runs every demo and tees logs
└── findings/
    └── api_capabilities_report.md  What we observed when we ran them for real
```

## Quickstart

```bash
# project pinned to vtxdemos, region us-central1, account admin@altostrat
gcloud config set project vtxdemos
gcloud config set ai/region us-central1

uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python -r requirements.txt

# Run any single capability
.venv/bin/python demos/04_vibe_search.py

# Or run the whole sweep and save findings
.venv/bin/python run_all.py
```

## How the demo lands the customer story

| Beat | Demo | Why it lands for Shutterstock |
| ---- | ---- | ----------------------------- |
| 1. Wow | `04_vibe_search.py` | Natural-language search instantly beats keyword search |
| 2. Reach | `05_multilingual.py` | One vector space, 100+ languages, no translation pipeline |
| 3. Cross-catalog | `09_multimodal_preview.py` | Photo → Music/3D/Video matching across Pond5 + TurboSquid |
| 4. Curation | `07_moodboard_cluster.py` | Replaces a half-day agency exercise with one click |
| 5. Ops | `06_brand_safety.py` | Zero-shot, per-customer policy with no retraining |
| 6. Scale | `03_matryoshka.py` | 768-dim sweet spot keeps storage cost sane at 600M+ assets |

See `research/use_cases.md` for the full 15 use cases and the suggested
walk-through order.
