# Design — PDF-Level Grounding in Gemini Enterprise

## Goal

When a user asks "What was Q1 2020 mentions?" in Gemini Enterprise, the answer shows:
- The text: "585"
- A globe-icon citation
- Click → opens the **source PDF at page 5** (not a .txt file)

## The Challenge

Vertex AI RAG Engine doesn't auto-populate `grounding_metadata`. Discovery Engine does, but only for its own datastores. To get PDF-level citations, we need:

1. **Custom retrieval** (Firestore) with PDF metadata
2. **Manual grounding construction** in the agent
3. **Correct format** so GE UI renders citations

## Architecture

```
PDF upload
  ↓
docparse extractor (gemini-2.5)
  ↓
markdown.txt + metadata.json (chunk→PDF mapping)
  ↓
Indexer:
  - Embed with gemini-embeddings-002
  - Store in Firestore: {text, embedding[2048], pdf_uri, page, bbox}
  ↓
Agent retrieval tool:
  - Firestore vector search (findNearest)
  - Optional: re-rank via Discovery Engine ranking API
  - Build GroundingMetadata: references point to PDF URIs
  ↓
ADK agent emits Event with grounding_metadata
  ↓
Agent Engine → GE: transforms to textGroundingMetadata
  ↓
GE UI: renders citations linking to gs://bucket/file.pdf#page=5
```

## Implementation Plan

### Phase 1: Firestore indexer (~1 hour)
- Read docparse markdown + metadata
- Embed with gemini-embeddings-002
- Write to Firestore collection

### Phase 2: Custom retrieval tool (~2 hours)
- FunctionTool that queries Firestore
- Returns chunks + PDF metadata
- Builds GroundingMetadata with PDF URIs

### Phase 3: Agent with grounding (~1 hour)
- ADK agent with custom tool
- Post-process to inject grounding into Events
- Deploy to Agent Engine

### Phase 4: Test in GE UI (~30 min)
- Register agent
- Ask test question
- Verify citations appear and link to PDF

### Phase 5: Optional re-ranker (~30 min)
- Add Discovery Engine ranking API call
- Measure if it improves composite

## Open Questions

1. **PDF serving:** How should users open the PDF?
   - Download gs:// URI (requires gcloud)
   - Serve via signed URL from Cloud Run
   - Embed PDF viewer in GE UI (if possible)

2. **Page highlighting:** Can GE UI scroll to a specific page in the PDF?
   - URI fragment: `file.pdf#page=5`
   - Or need custom viewer

3. **Sub-page bboxes:** Do we want citations to highlight specific regions on a page?
   - Would require storing bbox metadata
   - And custom PDF viewer with annotation overlay

## Expected Results

Based on the RAG Engine eval (92.1%), Firestore should perform similarly:
- Composite: ~91-93% (gemini-embeddings-002 might add +1-2 pts)
- Latency: ~10-12s (Firestore adds ~1-2s vs RAG Engine)
- Grounding: ✅ Citations visible in GE UI (if format is correct)

## Fallback

If manual grounding construction doesn't work with GE, fall back to Discovery Engine (grounding auto-works, tested at 81% baseline, likely improvable to ~85-90% with better config).
