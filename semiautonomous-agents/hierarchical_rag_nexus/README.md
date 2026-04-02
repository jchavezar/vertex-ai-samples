# Hierarchical RAG Nexus

Parent-Child RAG implementation with Cloud SQL pgvector for precision retrieval with full context.

## Architecture

```
Query
  │
  ▼
Vector Search (child embeddings, top-k hits)
  │
  ▼
Parent Lookup (child_id → parent_id → full parent text)
  │
  ▼
Agent Expansion (related_agents → peer context)
  │
  ▼
LLM gets parent context + expanded related segments
```

### Key Concepts

1. **Child Chunks**: Small (100-300 tokens), embedded, used for precision retrieval
2. **Parent Segments**: Large (500-2000 tokens), returned to LLM for full context
3. **Agent Relationships**: Lateral peer connections for cross-component context

## Database Schema

```sql
-- Parent segments: full context blocks
CREATE TABLE parent_segments (
    parent_id TEXT PRIMARY KEY,
    document_name TEXT,
    page_number INTEGER,
    heading TEXT,
    agent_name TEXT,         -- Logical component name
    content TEXT,            -- Full context (500-2000 tokens)
    parent_agent TEXT
);

-- Child chunks: small embedded pieces for retrieval
CREATE TABLE child_chunks (
    chunk_id TEXT PRIMARY KEY,
    parent_id TEXT REFERENCES parent_segments,
    content TEXT,            -- Small chunk (100-300 tokens)
    embedding vector(768),   -- For pgvector search
    ...
);

-- Agent relationships: lateral peer connections
CREATE TABLE segment_relationships (
    source_agent TEXT,
    target_agent TEXT,
    relationship_type TEXT   -- related, depends_on, feeds_into
);
```

## Test Documents

Three interrelated PDF documents about a distributed payment system:

1. **system_architecture.pdf** - Component overview (Orchestrator, Auth, Billing, etc.)
2. **operations_manual.pdf** - Operational procedures referencing architecture
3. **troubleshooting_guide.pdf** - Diagnostic flows referencing both

## Running

### Backend (Port 8003)
```bash
cd backend
uv sync
uv run uvicorn main:app --host 0.0.0.0 --port 8003
```

### Frontend (Port 5174)
```bash
cd frontend
npm install
npm run dev
```

### Generate Test PDFs
```bash
cd backend
uv run python ../test_docs/generate_pdfs.py
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/chat | Upload docs or send queries |
| GET | /api/documents | List indexed documents |
| GET | /api/documents/{name}/data | Get document segments |
| DELETE | /api/documents/{name} | Delete document |
| POST | /api/sql | Execute read-only SQL |

## Features

- **Parent-Child Chunking**: Precision search on children, full context from parents
- **Agent Relationship Expansion**: Pull related peer segments automatically
- **Interactive Graph Visualization**: See agent relationships with color-coded nodes
- **Cloud SQL pgvector**: HNSW index for fast vector search
- **ADK Integration**: Google Agent Development Kit for extraction

## Environment Variables

```env
PROJECT_ID=your_gcp_project
LOCATION=us-central1
DB_HOST=your_cloud_sql_ip
DB_PORT=5432
DB_NAME=hierarchical_rag
DB_USER=your_user
DB_PASSWORD=your_password
```
