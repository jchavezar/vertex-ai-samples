# Gemini Embeddings — Master Notes (April 2026)

## Models at a glance

| Model | Status | Modalities | Max input | Output dims (Matryoshka) | Languages |
| ----- | ------ | ---------- | --------- | ------------------------ | --------- |
| `gemini-embedding-2-preview` | Preview (Nov 2025) | Text, Image, Audio, Video, PDF | 8 192 tokens; ≤6 images, ≤80 s audio, ≤120 s video, ≤6 PDF pages | 128 / 768 / 1536 / 3072 | 100+ |
| `gemini-embedding-001` | GA (Jul 14 2025) | Text only | 2 048 tokens | 128 / 768 / 1536 / 3072 | 100+ |
| `text-embedding-005` | GA (May 20 2025) | Text only | 2 048 tokens | up to 768 | English + code |
| `text-multilingual-embedding-002` | Stable | Text only | 2 048 tokens | up to 768 | 80+ |
| `multimodalembedding@001` | Stable (Vertex) | Image, Text, Video | 32 tokens text | 128 / 256 / 512 / 1408 | English |

Spaces between Gemini Embedding 1 and 2 are **incompatible** — re-embed when migrating.

## Pricing (Gemini API)

* `gemini-embedding-001` — text $0.15 / 1M input tokens (Batch $0.075)
* `gemini-embedding-2-preview` —
  * Text $0.20 / 1M tok
  * Image $0.45 / 1M tok ($0.00012 / image)
  * Audio $6.50 / 1M tok ($0.00016 / sec)
  * Video $12.00 / 1M tok ($0.00079 / frame)

Free tiers exist for both models with stricter rate limits.

## Vertex AI quotas

* 5 000 000 tokens / minute / project / region
* 250 inputs and 20 000 tokens per request
* 2 048 tokens hard cap per text (silent truncation if `autoTruncate=true`)
* `gemini-embedding-001` on Vertex: **one input per call** (older `text-embedding-005` allows 5)
* Batch prediction endpoint accepts up to 30 000 prompts per job (one job at a time)

## Task types (only on `gemini-embedding-001`; not on `-2-preview`)

| Task | When to use | Pairs with |
| ---- | ----------- | ---------- |
| `RETRIEVAL_QUERY` | Search query side | `RETRIEVAL_DOCUMENT` |
| `RETRIEVAL_DOCUMENT` | Corpus side, indexed assets | self |
| `SEMANTIC_SIMILARITY` | Recommendations, dedup, clone-finder | symmetric |
| `CLASSIFICATION` | Sentiment / brand-safety / topic | symmetric |
| `CLUSTERING` | Mood-boards, segmentation | symmetric |
| `QUESTION_ANSWERING` | Real questions ("Why is the sky blue?") | with `RETRIEVAL_DOCUMENT` |
| `FACT_VERIFICATION` | Statement → evidence search | with `RETRIEVAL_DOCUMENT` |
| `CODE_RETRIEVAL_QUERY` | Natural language → code | with `RETRIEVAL_DOCUMENT` |

For Gemini Embedding 2 (multimodal) there is no `task_type` — encode the
intent in the prompt itself ("Represent this asset for retrieval:").

## Matryoshka behaviour

Trained with Matryoshka Representation Learning, so prefixes are meaningful.
Reported MTEB scores for `gemini-embedding-001`:

| Dim | MTEB (Multilingual mean) |
| --- | ------------------------ |
| 2048 | 68.16 |
| 1536 | 68.17 |
| **768** | **67.99 ← sweet spot** |
| 512 | 67.55 |
| 256 | 66.19 |
| 128 | 63.31 |

Always L2-normalize after truncation:

```python
import numpy as np
v = np.array(embedding.values)
v = v / np.linalg.norm(v)
```

## MTEB benchmarks (Gemini Embedding paper, arXiv 2503.07891)

| Model | MTEB Multilingual | MTEB Eng v2 | MTEB Code |
| ----- | ----------------- | ----------- | --------- |
| **Gemini Embedding** | **68.32** | **73.30** | **74.66** |
| OpenAI text-embedding-3-large | 58.92 | — | 58.95 |
| NV-Embed-v2 | — | 65.0 | 59.4 |
| Cohere embed-multilingual-v3.0 | 61.10 | — | 51.94 |
| voyage-3 | — | — | 67.3 |

## Canonical code samples

### Gemini API — Python (`google-genai` ≥ 1.73)

```python
from google import genai
from google.genai import types

client = genai.Client()  # picks up GEMINI_API_KEY or Vertex via env

result = client.models.embed_content(
    model="gemini-embedding-001",
    contents=["coffee shop on a rainy afternoon", "espresso art latte foam"],
    config=types.EmbedContentConfig(
        task_type="RETRIEVAL_DOCUMENT",
        output_dimensionality=768,
        title="stock photo captions",
    ),
)
for e in result.embeddings:
    print(len(e.values))
```

### Vertex AI — same SDK, different env

```bash
export GOOGLE_GENAI_USE_VERTEXAI=True
export GOOGLE_CLOUD_PROJECT=vtxdemos
export GOOGLE_CLOUD_LOCATION=us-central1
```

```python
from google import genai
client = genai.Client()  # now hits Vertex
```

### Multimodal (preview)

```python
from google import genai
from google.genai import types

client = genai.Client()
with open("logo.png", "rb") as f:
    img = f.read()

result = client.models.embed_content(
    model="gemini-embedding-2-preview",
    contents=[
        "Brand visual identity",
        types.Part.from_bytes(data=img, mime_type="image/png"),
    ],
)
# Single fused embedding combining both inputs
```

### REST — Gemini API

```bash
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-001:embedContent" \
  -H "Content-Type: application/json" \
  -H "x-goog-api-key: $GEMINI_API_KEY" \
  -d '{
        "content": {"parts": [{"text": "What is the meaning of life?"}]},
        "taskType": "RETRIEVAL_QUERY",
        "outputDimensionality": 768
      }'
```

### REST — Vertex AI

```bash
curl -X POST \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  -H "Content-Type: application/json" \
  https://us-central1-aiplatform.googleapis.com/v1/projects/vtxdemos/locations/us-central1/publishers/google/models/gemini-embedding-001:predict \
  -d '{
        "instances": [{
          "content": "Stock photo of a sunrise over Mt Fuji",
          "task_type": "RETRIEVAL_DOCUMENT",
          "title": "landscape photography"
        }],
        "parameters": {"autoTruncate": true, "outputDimensionality": 768}
      }'
```

## Best practices we'll demo

1. Choose 768 dims unless you need ground-truth quality (3072) or extreme scale (256)
2. L2-normalize after truncation
3. Use task types: queries get `RETRIEVAL_QUERY`, corpus gets `RETRIEVAL_DOCUMENT`
4. Batch via Batch API for backfill (50 % cheaper)
5. Keep `autoTruncate=true` in production but `False` during eval to catch over-length inputs
6. Re-embed corpus when bumping models (1 → 2 spaces are incompatible)

## Sources

* https://ai.google.dev/gemini-api/docs/embeddings
* https://cloud.google.com/vertex-ai/generative-ai/docs/embeddings/get-text-embeddings
* https://cloud.google.com/vertex-ai/generative-ai/docs/embeddings/get-multimodal-embeddings
* https://cloud.google.com/vertex-ai/generative-ai/docs/embeddings/task-types
* https://cloud.google.com/vertex-ai/generative-ai/docs/embeddings/batch-prediction-genai-embeddings
* https://ai.google.dev/api/embeddings
* https://ai.google.dev/pricing
* https://arxiv.org/abs/2503.07891  (Gemini Embedding paper)
* https://developers.googleblog.com/en/gemini-embedding-available-gemini-api/
* https://github.com/google-gemini/cookbook/blob/main/quickstarts/Embeddings.ipynb
