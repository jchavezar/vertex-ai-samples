# docparse-firestore-grounding

**PDF-level grounding via Firestore vector search + gemini-embeddings-002**

Experimental variant of docparse that uses:
- **Firestore** for vector storage (not Vertex AI RAG Engine)
- **gemini-embeddings-002** (2048-d, multimodal-optimized)
- **Manual grounding construction** pointing to source PDF pages
- **Optional re-ranker** (Discovery Engine ranking API)

The goal: grounding citations in Gemini Enterprise UI that link to **PDF pages** (not .txt files), with full control over chunking and metadata.

## What's different from docparse/

| Layer | docparse/ | docparse-firestore-grounding/ |
|---|---|---|
| Extraction | Same (gemini-2.5) | Same + outputs .metadata.json (chunk→PDF mapping) |
| Embedding | text-embedding-005 (768-d) | **gemini-embeddings-002 (2048-d)** |
| Storage | Vertex AI RAG Engine corpus | **Firestore collection** |
| Retrieval | ADK VertexAiRagRetrieval | **Custom FunctionTool** (Firestore findNearest) |
| Re-ranker | Optional (in config) | **Optional** (Discovery Engine ranking API) |
| Grounding | None (RAG Engine doesn't populate it) | **Manual** (references point to PDF URIs) |

## Status

🚧 **Under development** — validates if Firestore + manual grounding enables PDF-level citations in GE UI.

See `../docparse/` for the production-ready RAG Engine variant (90.5% composite, deployed).
