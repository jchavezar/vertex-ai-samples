# PGVector Document Nexus

> **Multimodal document intelligence platform using Cloud SQL with pgvector for semantic search and grounded chat.**

A production-ready document processing system that extracts entities from PDFs (text, tables, charts), generates embeddings via Vertex AI, and stores them in Cloud SQL with pgvector for fast semantic retrieval. Features a modern "Aurora" UI theme with purple/teal gradients.

## What This Project Does

```
+------------------------------------------------------------------+
|                  USER UPLOADS: document.pdf                       |
+------------------------------------------------------------------+
                               |
                               v
+------------------------------------------------------------------+
|  ADK PARALLEL EXTRACTION                                          |
|  - Split PDF into pages                                           |
|  - Gemini 2.5 Flash extracts text, tables, charts with bounding   |
|    boxes from each page concurrently                              |
+------------------------------------------------------------------+
                               |
                               v
+------------------------------------------------------------------+
|  VERTEX AI EMBEDDINGS                                             |
|  - text-embedding-004 generates 768-dim vectors                   |
|  - Batch processing with rate limiting                            |
+------------------------------------------------------------------+
                               |
                               v
+------------------------------------------------------------------+
|  CLOUD SQL PGVECTOR                                               |
|  - Store chunks with embeddings in PostgreSQL                     |
|  - HNSW index for fast approximate nearest neighbor search        |
+------------------------------------------------------------------+
                               |
                               v
+------------------------------------------------------------------+
|  GROUNDED CHAT + SQL EXPLORER                                     |
|  - User query embedded and searched via pgvector                  |
|  - Top-k chunks injected as context                               |
|  - Gemini generates response with citations [1], [2]              |
|  - Interactive SQL tab for direct database queries                |
+------------------------------------------------------------------+
```

## Key Features

| Feature | Description | Status |
|---------|-------------|--------|
| **Multimodal Extraction** | Extract text, tables, and charts with spatial bounding boxes | Done |
| **pgvector Storage** | Cloud SQL PostgreSQL with vector extension | Done |
| **HNSW Indexing** | Fast approximate nearest neighbor search (~10-50ms) | Done |
| **Grounded RAG Chat** | LLM responses with document citations | Done |
| **SQL Query Tab** | Interactive SQL explorer for database inspection | Done |
| **Aurora UI Theme** | Modern glassmorphic design with purple/teal gradients | Done |

## Quick Start

### Prerequisites

- Python 3.12+
- Node.js 20+
- Google Cloud SDK with authenticated ADC
- Cloud SQL PostgreSQL instance with pgvector extension

### Setup

```bash
# 1. Navigate to project
cd semiautonomous-agents/pgvector_document_nexus

# 2. Create .env file (see docs/getting-started.md for details)
cat > .env << 'EOF'
PROJECT_ID=your-project
LOCATION=us-central1
DB_HOST=your-cloud-sql-ip
DB_PORT=5432
DB_NAME=pgvector_doc_nexus
DB_USER=emb-admin
DB_PASSWORD=your-password
EOF

# 3. Backend
cd backend && uv sync && uv run python main.py

# 4. Frontend (new terminal)
cd frontend && npm install && npm run dev
```

### Access

| Service | URL |
|---------|-----|
| **Frontend** | http://localhost:5173 |
| **Backend API** | http://localhost:8002 |
| **Health Check** | http://localhost:8002/api/health |

---

## Documentation

```mermaid
graph LR
    README[README] --> GS[Getting Started]
    README --> ARCH[Architecture]
    README --> DEPLOY[Deployment]
    README --> TROUBLE[Troubleshooting]

    GS --> ARCH
    ARCH --> DEPLOY
    DEPLOY --> TROUBLE

    README --> BE[Backend README]
    README --> FE[Frontend README]

    click GS "https://github.com/jchavezar/vertex-ai-samples/blob/main/semiautonomous-agents/pgvector_document_nexus/docs/getting-started.md" _self
    click ARCH "https://github.com/jchavezar/vertex-ai-samples/blob/main/semiautonomous-agents/pgvector_document_nexus/docs/architecture.md" _self
    click DEPLOY "https://github.com/jchavezar/vertex-ai-samples/blob/main/semiautonomous-agents/pgvector_document_nexus/docs/deployment.md" _self
    click TROUBLE "https://github.com/jchavezar/vertex-ai-samples/blob/main/semiautonomous-agents/pgvector_document_nexus/docs/troubleshooting.md" _self
    click BE "https://github.com/jchavezar/vertex-ai-samples/blob/main/semiautonomous-agents/pgvector_document_nexus/backend/README.md" _self
    click FE "https://github.com/jchavezar/vertex-ai-samples/blob/main/semiautonomous-agents/pgvector_document_nexus/frontend/README.md" _self
```

### Start Here

| Document | Description |
|----------|-------------|
| [Getting Started](docs/getting-started.md) | Complete setup guide from scratch |
| [Architecture](docs/architecture.md) | E2E system diagram and component overview |

### Setup & Deployment

| Document | Description |
|----------|-------------|
| [Deployment](docs/deployment.md) | Cloud SQL setup and production deployment |
| [Troubleshooting](docs/troubleshooting.md) | Common issues and solutions |

### Component Documentation

| Component | Description |
|-----------|-------------|
| [Backend](backend/README.md) | FastAPI server with pgvector integration |
| [Frontend](frontend/README.md) | React 19 Aurora-themed UI |

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/chat` | Upload documents or send chat messages |
| `POST` | `/api/sql` | Execute read-only SQL queries |
| `GET` | `/api/documents` | List indexed documents |
| `GET` | `/api/documents/{name}/data` | Get document chunks |
| `DELETE` | `/api/documents/{name}` | Delete document |
| `GET` | `/api/health` | Health check |

---

## Architecture Comparison

| Aspect | BigQuery Version | pgvector Version |
|--------|------------------|------------------|
| **Vector Store** | BigQuery VECTOR_SEARCH | Cloud SQL pgvector |
| **Index Type** | IVF (built-in) | HNSW (configurable) |
| **Query Latency** | ~200-500ms | ~10-50ms |
| **Scaling** | Serverless | Instance-based |
| **Cost Model** | Per-query | Per-instance |

---

## Project Structure

```
pgvector_document_nexus/
├── README.md                      # This file
├── .env                           # Environment config (gitignored)
├── .gitignore
├── docs/
│   ├── getting-started.md         # Complete setup guide
│   ├── architecture.md            # System design
│   ├── deployment.md              # Production deployment
│   └── troubleshooting.md         # Debug guide
├── backend/
│   ├── README.md                  # Backend documentation
│   ├── main.py                    # FastAPI server
│   ├── pipeline.py                # ADK extraction + pgvector
│   ├── init_db.py                 # Database initializer
│   └── pyproject.toml
└── frontend/
    ├── README.md                  # Frontend documentation
    ├── src/
    │   ├── App.tsx                # Main React component
    │   └── index.css              # Aurora theme styles
    └── package.json
```

---

*Built with Google ADK, Vertex AI, and Cloud SQL pgvector*
