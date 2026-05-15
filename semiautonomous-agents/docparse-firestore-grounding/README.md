# docparse-firestore-grounding

**Production agents with PDF-level citations in Gemini Enterprise**

Two agents deployed to sharepoint-wif, both using gemini-2.5-flash (GA) with clickable PDF citations:

## Status

✅ **PRODUCTION** — Two agents deployed to sharepoint-wif Gemini Enterprise with working PDF citations.

**Features:**
- ✓ Gemini 2.5 Flash (GA) throughout - customer can ship
- ✓ Clickable PDF citations in GE responses
- ✓ All components in sharepoint-wif project
- ✓ Tested and working with sample queries

**Test in GE:** https://vertexaisearch.cloud.google.com/home/cid/28bd98ae-eaa9-456c-96a5-39f0d804a5c1

**Evaluation results:** See `../docparse/eval/RESULTS.md` for comprehensive benchmarks (90.5% composite on 298 questions).

## Deployed Agents

### 1. ✅ Firestore Citations (us-central1)
- **Retrieval:** Keyword-based Firestore search (fallback from vector search issue)
- **Embedding:** text-embedding-005 (768-d) - indexed but find_nearest() returns 0 results
- **Model:** gemini-2.5-flash (GA)
- **Citations:** ✓ Clickable links to PDF in GCS (LLM-generated markdown citations)
- **RE:** `projects/984359513632/locations/us-central1/reasoningEngines/2302663771341979648`
- **Agent ID:** `9366656747084426439`

### 2. ✅ RAG Engine + Citations (us-west1)
- **Retrieval:** Semantic vector search via RAG corpus
- **Embedding:** text-embedding-005 (768-d, managed by RAG Engine)
- **Model:** gemini-2.5-flash (GA)
- **Citations:** ✓ Clickable links to PDF sources
- **Corpus:** `projects/984359513632/locations/us-west1/ragCorpora/6917529027641081856`
- **RE:** `projects/984359513632/locations/us-west1/reasoningEngines/1990036881437360128`
- **Agent ID:** `9214915046835903932`

## Architecture

**Firestore agent:**
```
User query → streaming_agent_run_with_events() 
  → Keyword search Firestore (72 chunks) 
  → Gemini 2.5 Flash generates answer with markdown citations
  → LLM adds [Document - Page X](gs://...) links to response
```

**RAG Engine agent:**
```
User query → streaming_agent_run_with_events()
  → RAG corpus retrieval_query (semantic search)
  → Gemini 2.5 Flash generates answer
  → Grounding from RAG contexts
```

## What Works

✓ Both agents answer questions correctly from Firestore and RAG corpus data  
✓ Clickable citation links appear in GE responses  
✓ gemini-2.5-flash (GA) models throughout  
✓ All components in single project (sharepoint-wif)  
✓ Streaming support for GE UI compatibility

## Known Limitations

1. **Firestore vector search** - `find_nearest()` returns 0 results despite READY index; using keyword search fallback
2. **Citation format** - Citations render as LLM-generated text links, not GE's native structured grounding sidebar (would require `textGroundingMetadata` in streamAssist response)

## Deployment

Both agents deployed via Docker container with SA credentials (solves 2-account ADC split):

```bash
cd ~/vertex-ai-samples/semiautonomous-agents/docparse-firestore-grounding
sudo docker run --rm \
  -v $(pwd):/workspace \
  -v ~/.secrets/paperclip-detective-sa.json:/secrets/sa-key.json:ro \
  -e GOOGLE_APPLICATION_CREDENTIALS=/secrets/sa-key.json \
  deployment-container:latest \
  python deploy_firestore.py  # or deploy_rag_agent.py
```

## Files

- `deploy_firestore.py` - Deploy Firestore agent
- `deploy_rag_agent.py` - Deploy RAG Engine agent  
- `firestore_agent/simple_query_wrapper.py` - Agent code with streaming methods
- `indexer/index_to_firestore.py` - Embed and index markdown to Firestore
- `create_rag_corpus.py` - Create RAG corpus and import PDFs

## Testing

Test in GE: https://vertexaisearch.cloud.google.com/home/cid/28bd98ae-eaa9-456c-96a5-39f0d804a5c1

Select either agent and ask:
- "what is the metaverse?" → Returns definition with citations
- "bring me all the statistics for milenial gen?" → Returns all 10 data points with citations

## Related Projects

- **`../docparse/`** - Comprehensive docparse evaluation suite with 8 RAG strategies tested, GA model benchmarks, and detailed accuracy analysis (90.5% composite on 298 questions). See `../docparse/eval/RESULTS.md` for full results.
