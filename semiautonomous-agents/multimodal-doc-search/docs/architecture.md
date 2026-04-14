# Architecture

[<- Back to Main README](../README.md) | [Getting Started](getting-started.md) | [Deployment](deployment.md)

> **End-to-end system architecture for PGVector Document Nexus**

## Overview

This document describes the complete architecture of PGVector Document Nexus, a multimodal document intelligence system using Cloud SQL with pgvector for vector storage.

## System Architecture

```
+------------------------------------------------------------------+
|                        FRONTEND (React 19)                        |
|  Aurora Theme | Framer Motion | Vite | Port 5173                 |
|  - Document upload        - Results dashboard                     |
|  - Chat interface         - SQL query explorer                    |
+------------------------------------------------------------------+
                               |
                               | HTTP/REST (/api/*)
                               v
+------------------------------------------------------------------+
|                      FASTAPI BACKEND (Port 8002)                  |
|  - /api/chat          - Document upload & RAG chat                |
|  - /api/sql           - SQL query execution                       |
|  - /api/documents     - Document management                       |
+------------------------------------------------------------------+
          |                    |                    |
          v                    v                    v
+------------------+  +------------------+  +------------------+
|   ADK AGENTS     |  |  VERTEX AI       |  |  CLOUD SQL       |
|  (Extraction)    |  |  (Embeddings)    |  |  (pgvector)      |
|                  |  |                  |  |                  |
| - Page Extractor |  | text-embedding   |  | - HNSW Index     |
| - Gemini 2.5     |  | -004 (768d)      |  | - Cosine Search  |
|   Flash          |  |                  |  |                  |
+------------------+  +------------------+  +------------------+
```

## Component Details

### 1. Frontend (React 19)

**Location**: [`frontend/src/App.tsx`](../frontend/src/App.tsx)

| Feature | Description | Source |
|---------|-------------|--------|
| Upload View | Drag-drop document upload | [`App.tsx#L400-L470`](../frontend/src/App.tsx#L400-L470) |
| Data Tab | Entity table view | [`App.tsx#L508-L530`](../frontend/src/App.tsx#L508-L530) |
| Pages Tab | Annotated images | [`App.tsx#L533-L545`](../frontend/src/App.tsx#L533-L545) |
| SQL Tab | Query explorer | [`App.tsx#L568-L630`](../frontend/src/App.tsx#L568-L630) |
| Chat Panel | RAG conversation | [`App.tsx#L640-L680`](../frontend/src/App.tsx#L640-L680) |

### 2. Backend (FastAPI)

**Location**: [`backend/main.py`](../backend/main.py)

| Endpoint | Function | Source |
|----------|----------|--------|
| `POST /api/chat` | Upload & chat | [`main.py#L70-L239`](../backend/main.py#L70-L239) |
| `POST /api/sql` | SQL queries | [`main.py#L295-L355`](../backend/main.py#L295-L355) |
| `GET /api/documents` | List docs | [`main.py#L241-L244`](../backend/main.py#L241-L244) |

### 3. Pipeline (ADK + pgvector)

**Location**: [`backend/pipeline.py`](../backend/pipeline.py)

| Function | Purpose | Source |
|----------|---------|--------|
| `split_pdf_logically()` | Split PDF into pages | [`pipeline.py#L100-L130`](../backend/pipeline.py#L100-L130) |
| `_create_page_extractor()` | Create ADK agent | [`pipeline.py#L367-L400`](../backend/pipeline.py#L367-L400) |
| `generate_embeddings()` | Vertex AI embeddings | [`pipeline.py#L170-L195`](../backend/pipeline.py#L170-L195) |
| `insert_chunks_to_pgvector()` | Store in Cloud SQL | [`pipeline.py#L240-L270`](../backend/pipeline.py#L240-L270) |
| `search_embeddings_pgvector()` | Vector search | [`pipeline.py#L272-L315`](../backend/pipeline.py#L272-L315) |

### 4. Vector Storage (pgvector)

**Index Type**: HNSW (Hierarchical Navigable Small World)

| Parameter | Value | Purpose |
|-----------|-------|---------|
| Dimensions | 768 | Embedding size |
| Distance | Cosine | Similarity metric |
| m | 16 | Max connections per layer |
| ef_construction | 64 | Build-time search width |

**Table Schema**:

```sql
CREATE TABLE document_chunks (
    id SERIAL PRIMARY KEY,
    chunk_id TEXT UNIQUE NOT NULL,
    document_name TEXT NOT NULL,
    page_number INTEGER NOT NULL,
    entity_type TEXT NOT NULL,       -- TEXT, TABLE, CHART
    content TEXT NOT NULL,
    embedding vector(768),
    box_2d INTEGER[],                -- Bounding box [ymin, xmin, ymax, xmax]
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Data Flow

### Document Upload Flow

```
User uploads PDF
       |
       v
FastAPI receives file (main.py:chat_endpoint)
       |
       v
split_pdf_logically() -> Single-page chunks
       |
       v
pdf_page_to_image() -> JPEG for each page
       |
       v
ADK ParallelAgent runs extractors (max 5 concurrent)
       |
       v
Gemini 2.5 Flash extracts entities + bounding boxes
       |
       v
generate_embeddings() -> text-embedding-004
       |
       v
insert_chunks_to_pgvector() -> Cloud SQL
       |
       v
Return annotated images + traces to frontend
```

### Chat/Search Flow

```
User sends query
       |
       v
Embed query with text-embedding-004
       |
       v
pgvector HNSW search (top 5)
       |
       v
Format context with citations
       |
       v
LlmAgent generates grounded response
       |
       v
Return response + retrieved chunks
```

### SQL Query Flow

```
User enters SQL query
       |
       v
Frontend sends to /api/sql
       |
       v
Backend validates (SELECT only)
       |
       v
Execute against Cloud SQL
       |
       v
Format results (truncate vectors)
       |
       v
Return columns + rows to frontend
```

## Security Considerations

| Layer | Protection |
|-------|------------|
| SQL Endpoint | SELECT-only, keyword blocklist, 10s timeout |
| File Upload | Size limits, PDF/image validation |
| Database | Parameterized queries, connection pooling |
| Network | Cloud SQL authorized networks |

## Performance Characteristics

| Operation | Latency | Notes |
|-----------|---------|-------|
| PDF extraction | 5-30s | Depends on page count |
| Embedding generation | ~100ms/chunk | Batched (50 per call) |
| pgvector insert | ~10ms/row | Bulk load |
| Vector search | 10-50ms | HNSW approximate |
| Chat response | 2-5s | LLM generation |

## Related Documentation

- [Getting Started](getting-started.md) - Setup from scratch
- [Deployment](deployment.md) - Production deployment
- [Troubleshooting](troubleshooting.md) - Debug guide
- [Backend README](../backend/README.md) - API details
- [Frontend README](../frontend/README.md) - UI details
