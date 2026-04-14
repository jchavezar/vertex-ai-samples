# Backend

[<- Back to Main README](../README.md) | [Architecture](../docs/architecture.md) | [Frontend](../frontend/README.md)

> **FastAPI backend with pgvector integration and SQL query support**

## Architecture

```
backend/
├── main.py              # FastAPI server and API endpoints
├── pipeline.py          # ADK extraction + pgvector operations
├── init_db.py           # Database schema initializer
├── pyproject.toml       # Python dependencies (uv)
├── .python-version      # Python 3.12
└── local_data/          # Cached metadata (auto-created)
```

## Files

| File | Description | Key Functions |
|------|-------------|---------------|
| [`main.py`](main.py) | FastAPI app with REST endpoints | `chat_endpoint()`, `execute_sql()` |
| [`pipeline.py`](pipeline.py) | Document processing pipeline | `process_document_pipeline()`, `search_embeddings_pgvector()` |
| [`init_db.py`](init_db.py) | Database initializer | `init_database()` |

## API Endpoints

| Method | Endpoint | Description | Source |
|--------|----------|-------------|--------|
| `POST` | `/api/chat` | Upload documents or chat | [`main.py#L70-L239`](main.py#L70-L239) |
| `POST` | `/api/sql` | Execute SQL queries | [`main.py#L295-L355`](main.py#L295-L355) |
| `GET` | `/api/documents` | List indexed documents | [`main.py#L241-L244`](main.py#L241-L244) |
| `GET` | `/api/documents/{name}/data` | Get document chunks | [`main.py#L246-L279`](main.py#L246-L279) |
| `DELETE` | `/api/documents/{name}` | Delete document | [`main.py#L281-L286`](main.py#L281-L286) |
| `GET` | `/api/health` | Health check | [`main.py#L288-L290`](main.py#L288-L290) |

## Key Components

### Database Connection Pool

Source: [`pipeline.py#L50-L70`](pipeline.py#L50-L70)

```python
async def get_db_pool() -> asyncpg.Pool:
    global _db_pool
    if _db_pool is None:
        _db_pool = await asyncpg.create_pool(
            host=os.environ.get("DB_HOST"),
            database=os.environ.get("DB_NAME"),
            # ...
        )
    return _db_pool
```

### Vector Search with pgvector

Source: [`pipeline.py#L198-L240`](pipeline.py#L198-L240)

Uses pgvector's `<=>` operator for cosine distance:

```sql
SELECT chunk_id, document_name, content,
       1 - (embedding <=> $1::vector) AS similarity
FROM document_chunks
ORDER BY embedding <=> $1::vector
LIMIT $2
```

### ADK Page Extraction

Source: [`pipeline.py#L367-L400`](pipeline.py#L367-L400)

Creates per-page extraction agents:

```python
def _create_page_extractor(page_chunk: dict, page_num: int) -> LlmAgent:
    return LlmAgent(
        name=f"extractor_page_{page_num}",
        model="gemini-2.5-flash",
        instruction="...",
        output_schema=DocumentPageResult,
        before_model_callback=inject_image
    )
```

### SQL Query Endpoint

Source: [`main.py#L295-L355`](main.py#L295-L355)

Security features:
- Only SELECT queries allowed
- Blocks DROP, DELETE, INSERT, UPDATE, ALTER, CREATE
- 10-second statement timeout
- Truncates long embedding vectors in output

## Configuration

Environment variables (via `../.env`):

| Variable | Description | Required |
|----------|-------------|----------|
| `PROJECT_ID` | GCP project ID | Yes |
| `LOCATION` | GCP region | Yes |
| `DB_HOST` | Cloud SQL IP | Yes |
| `DB_PORT` | PostgreSQL port (default: 5432) | No |
| `DB_NAME` | Database name | Yes |
| `DB_USER` | Database user | Yes |
| `DB_PASSWORD` | Database password | Yes |

## Running

```bash
cd backend

# Install dependencies
uv sync

# Initialize database (first time only)
uv run python init_db.py

# Start server
uv run python main.py
# Or with uvicorn directly:
uv run uvicorn main:app --host 0.0.0.0 --port 8002 --reload
```

Server starts on `http://localhost:8002`

## Testing

```bash
# Health check
curl http://localhost:8002/api/health

# List documents
curl http://localhost:8002/api/documents

# Execute SQL query
curl -X POST http://localhost:8002/api/sql \
  -F "query=SELECT document_name, COUNT(*) FROM document_chunks GROUP BY document_name;"

# Upload document
curl -X POST http://localhost:8002/api/chat \
  -F "files=@document.pdf" \
  -F "selected_model=gemini-2.5-flash"

# Chat with document
curl -X POST http://localhost:8002/api/chat \
  -F "message=What is this document about?" \
  -F "selected_model=gemini-2.5-flash"
```

## Database Schema

```sql
CREATE TABLE document_chunks (
    id SERIAL PRIMARY KEY,
    chunk_id TEXT UNIQUE NOT NULL,
    document_name TEXT NOT NULL,
    page_number INTEGER NOT NULL,
    entity_type TEXT NOT NULL,
    content TEXT NOT NULL,
    embedding vector(768),
    box_2d INTEGER[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX document_chunks_embedding_idx
ON document_chunks
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);
```

## Related Documentation

- [Main README](../README.md) - Project overview
- [Architecture](../docs/architecture.md) - Full system design
- [Getting Started](../docs/getting-started.md) - Setup guide
- [Frontend](../frontend/README.md) - UI documentation
- [Troubleshooting](../docs/troubleshooting.md) - Common issues
