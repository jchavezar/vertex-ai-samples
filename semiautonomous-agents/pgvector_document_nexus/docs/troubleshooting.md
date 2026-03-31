# Troubleshooting

[<- Back to Main README](../README.md) | [Architecture](architecture.md) | [Deployment](deployment.md)

> **Common issues and solutions for PGVector Document Nexus**

## Database Connection Issues

### Error: `asyncpg.exceptions.ConnectionDoesNotExistError`

**Cause**: Cannot connect to Cloud SQL instance.

**Solutions**:
1. Verify `DB_HOST` is correct (use private IP if on VPC)
2. Check Cloud SQL instance is running
3. Verify firewall rules allow connection
4. For local dev, ensure Cloud SQL Proxy is running

```bash
# Start Cloud SQL Proxy
cloud_sql_proxy -instances=$PROJECT_ID:$REGION:$INSTANCE_NAME=tcp:5432
```

### Error: `extension "vector" does not exist`

**Cause**: pgvector extension not enabled.

**Solution**:
```sql
-- Connect to database and run:
CREATE EXTENSION IF NOT EXISTS vector;
```

For Cloud SQL, ensure the instance was created with `cloudsql.enable_pgvector=on`.

## Embedding Generation Issues

### Error: `404 Model not found`

**Cause**: Embedding model not available in region.

**Solution**: Ensure `GOOGLE_CLOUD_LOCATION` is set to a region with `text-embedding-004`:
- `us-central1`
- `europe-west1`
- `asia-northeast1`

### Error: `429 Resource exhausted`

**Cause**: Hitting Vertex AI rate limits.

**Solution**: The pipeline uses a semaphore (max 5 concurrent requests). If still hitting limits:
1. Reduce batch size in `generate_embeddings()`
2. Add exponential backoff
3. Request quota increase

## ADK Extraction Issues

### Error: `Gemini 3 Flash Preview not available`

**Cause**: Preview model requires specific location.

**Solution**: Set location to `global` for preview models:
```python
os.environ["GOOGLE_CLOUD_LOCATION"] = "global"
os.environ["GOOGLE_GENAI_LOCATION"] = "global"
```

### No Entities Extracted

**Causes**:
1. PDF is image-only without OCR
2. Very low resolution images
3. Unsupported file format

**Solutions**:
1. Ensure PDF has selectable text or clear images
2. Check terminal logs for ADK agent errors
3. Try with a different test PDF

## Search/RAG Issues

### Empty Search Results

**Causes**:
1. No documents indexed yet
2. Query embedding dimension mismatch
3. HNSW index not created

**Debug**:
```sql
-- Check document count
SELECT COUNT(*) FROM document_chunks;

-- Check embedding dimensions
SELECT array_length(embedding, 1) FROM document_chunks LIMIT 1;

-- Verify index exists
SELECT indexname FROM pg_indexes WHERE tablename = 'document_chunks';
```

### Slow Search Performance

**Cause**: HNSW index parameters too conservative.

**Solution**: Tune index parameters:
```sql
-- Drop and recreate with higher values
DROP INDEX document_chunks_embedding_idx;

CREATE INDEX ON document_chunks
USING hnsw (embedding vector_cosine_ops)
WITH (m = 32, ef_construction = 128);
```

## Frontend Issues

### CORS Errors

**Cause**: Backend CORS not configured for frontend origin.

**Solution**: Already configured in `main.py` with `allow_origins=["*"]`. If deploying to different domains, specify exact origins.

### Processing Overlay Stuck

**Cause**: Backend request timed out or failed silently.

**Debug**:
1. Check browser DevTools Network tab
2. Check backend terminal for errors
3. Verify backend is running on port 8002

## Debug Checklist

- [ ] `.env` file exists with all required variables
- [ ] `uv sync` completed successfully
- [ ] Cloud SQL instance is running and accessible
- [ ] pgvector extension is enabled
- [ ] HNSW index is created
- [ ] Vertex AI API is enabled
- [ ] ADC (Application Default Credentials) is configured
- [ ] Backend running on port 8002
- [ ] Frontend running on port 5173

## Getting Logs

```bash
# Backend logs
uv run python main.py 2>&1 | tee backend.log

# Cloud Run logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=pgvector-nexus-backend" --limit=50
```

## Related Documentation

- [Main README](../README.md) - Project overview
- [Getting Started](getting-started.md) - Local development setup
- [Architecture](architecture.md) - System design for context
- [Deployment](deployment.md) - Setup and deployment guide
- [Backend README](../backend/README.md) - API implementation
- [Frontend README](../frontend/README.md) - UI documentation
