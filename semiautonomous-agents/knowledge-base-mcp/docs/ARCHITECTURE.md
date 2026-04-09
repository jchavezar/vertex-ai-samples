# Architecture

## Data Flow

```
┌────────────────────────────────────────────────────────────────────┐
│                        INGESTION PIPELINE                          │
│                                                                    │
│  JSONL Transcript                                                  │
│       │                                                            │
│       ▼                                                            │
│  ┌─────────┐    ┌─────────┐    ┌────────────┐    ┌─────────────┐ │
│  │ Parser  │ -> │ Chunker │ -> │ Extractor  │ -> │   Loader    │ │
│  │         │    │         │    │ (Gemini)   │    │ (Firestore) │ │
│  │ Stream  │    │ Split   │    │            │    │             │ │
│  │ JSONL   │    │ topics  │    │ Problem/   │    │ Embed +     │ │
│  │ lines   │    │ 3-30msg │    │ Solution   │    │ Store       │ │
│  └─────────┘    └─────────┘    └────────────┘    └─────────────┘ │
└────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────┐
│                        RETRIEVAL (MCP)                             │
│                                                                    │
│  Query                                                             │
│    │                                                               │
│    ▼                                                               │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────────┐│
│  │ Embed Query  │ -> │ Vector Search│ -> │ Return Results       ││
│  │ (text-emb-  │    │ (Firestore   │    │ + expand_context     ││
│  │  004)       │    │  KNN)        │    │   hints              ││
│  └──────────────┘    └──────────────┘    └──────────────────────┘│
└────────────────────────────────────────────────────────────────────┘
```

## Storage Tiers

| Tier | Storage | Access Time | Content |
|------|---------|-------------|---------|
| **HOT** | MEMORY.md | Instant | Always-loaded summary |
| **WARM** | Firestore | ~100ms | Extracted patterns + vectors |
| **COLD** | JSONL (local/GCS) | Seconds | Raw transcripts |

## Firestore Collections

### `sessions`
Session metadata:
```json
{
  "session_id": "7dfa4d08-...",
  "date": "2026-04-03",
  "query_count": 142,
  "model_ids": ["claude-opus-4-5-20251101"],
  "total_input_tokens": 1234567,
  "total_output_tokens": 234567
}
```

### `knowledge`
Problem-solution patterns:
```json
{
  "session_id": "7dfa4d08-...",
  "timestamp": "2026-04-03T04:20:58",
  "problem": "WIF token exchange failing...",
  "error_message": "audience mismatch...",
  "solution": "Update provider to expect api:// prefix",
  "solution_score": 1.0,
  "failed_attempts": [
    {"attempt": "...", "reason_failed": "...", "score": 0.2}
  ],
  "anti_patterns": ["Using single provider..."],
  "services": ["WIF", "Entra ID"],
  "tools_used": ["Bash"],
  "search_text": "WIF audience mismatch api:// prefix",
  "embedding": [/* 768-dim vector */],
  "window": [4751, 4780],
  "expanded_messages": [/* cleaned conversation */]
}
```

### `playbooks`
How-to guides and patterns:
```json
{
  "title": "Configure SharePoint Federated Connector",
  "category": "recipe",
  "project": "sharepoint-wif-portal",
  "content": "## Steps...",
  "tags": ["sharepoint", "federated-connector"],
  "rejected": ["Using Application permissions..."],
  "search_text": "...",
  "embedding": [/* 768-dim vector */],
  "timestamp": "2026-04-07T..."
}
```

## Embedding Model

- **Model:** `text-embedding-004` (Vertex AI)
- **Dimensions:** 768
- **Task types:**
  - `RETRIEVAL_DOCUMENT` for storing
  - `RETRIEVAL_QUERY` for searching

## Extraction Model

- **Default:** `gemini-2.5-flash`
- **Configurable:** Set `EXTRACTION_MODEL` env var
- **Output:** Structured JSON with problem/solution/failed attempts

## Deduplication

Knowledge items are deduplicated by `session_id + problem` hash. Playbooks are deduplicated by title (case-insensitive).

## Vector Search

Uses Firestore's native vector search:
```python
query = collection.find_nearest(
    vector_field="embedding",
    query_vector=Vector(query_embedding),
    distance_measure=DistanceMeasure.COSINE,
    limit=top_k,
)
```

Requires composite index:
```bash
gcloud firestore indexes composite create \
  --collection-group=knowledge \
  --field-config=vector-config='{"dimension":768,"flat":{}}',field-path=embedding
```
