# Deployment

[<- Back to Main README](../README.md) | [Architecture](architecture.md) | [Troubleshooting](troubleshooting.md)

> **Guide for deploying PGVector Document Nexus to production**

## Overview

This guide covers setting up Cloud SQL with pgvector and deploying the application.

## Prerequisites

- Google Cloud Project with billing enabled
- `gcloud` CLI authenticated
- Cloud SQL Admin API enabled
- Vertex AI API enabled

## 1. Cloud SQL Setup

### Create Instance

```bash
# Set variables
export PROJECT_ID=your-project
export REGION=us-central1
export INSTANCE_NAME=pgvector-nexus

# Create Cloud SQL PostgreSQL 15+ instance
gcloud sql instances create $INSTANCE_NAME \
  --database-version=POSTGRES_15 \
  --cpu=2 \
  --memory=8GB \
  --region=$REGION \
  --root-password=your-secure-password \
  --database-flags=cloudsql.enable_pgvector=on
```

### Create Database

```bash
# Connect to instance
gcloud sql connect $INSTANCE_NAME --user=postgres

# In psql:
CREATE DATABASE document_nexus;
\c document_nexus

-- Enable pgvector
CREATE EXTENSION IF NOT EXISTS vector;

-- Create table
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

-- Create HNSW index
CREATE INDEX ON document_chunks
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);
```

### Get Connection Details

```bash
# Get IP address
gcloud sql instances describe $INSTANCE_NAME \
  --format="value(ipAddresses[0].ipAddress)"
```

## 2. Environment Configuration

Create `.env` file:

```env
# Google Cloud
PROJECT_ID=your-project
LOCATION=us-central1

# Cloud SQL
DB_HOST=your-cloud-sql-ip
DB_PORT=5432
DB_NAME=document_nexus
DB_USER=postgres
DB_PASSWORD=your-secure-password
```

## 3. Local Development

### Backend

```bash
cd backend
uv sync
uv run python main.py
# Running on http://localhost:8002
```

### Frontend

```bash
cd frontend
npm install
npm run dev
# Running on http://localhost:5173
```

## 4. Cloud Run Deployment

### Build Container

```bash
# Backend Dockerfile
cat > backend/Dockerfile << 'EOF'
FROM python:3.12-slim

WORKDIR /app

RUN pip install uv
COPY pyproject.toml .
RUN uv sync --no-dev

COPY . .

CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
EOF

# Build and push
gcloud builds submit backend \
  --tag gcr.io/$PROJECT_ID/pgvector-nexus-backend
```

### Deploy to Cloud Run

```bash
gcloud run deploy pgvector-nexus-backend \
  --image gcr.io/$PROJECT_ID/pgvector-nexus-backend \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --set-env-vars "PROJECT_ID=$PROJECT_ID,LOCATION=$REGION" \
  --set-secrets "DB_PASSWORD=db-password:latest" \
  --add-cloudsql-instances $PROJECT_ID:$REGION:$INSTANCE_NAME
```

## 5. Network Configuration

### VPC Connector (for Cloud Run to Cloud SQL)

```bash
gcloud compute networks vpc-access connectors create pgvector-connector \
  --region=$REGION \
  --range=10.8.0.0/28

# Update Cloud Run service
gcloud run services update pgvector-nexus-backend \
  --vpc-connector=pgvector-connector
```

## 6. IAM Permissions

Required roles for the service account:

- `roles/cloudsql.client`
- `roles/aiplatform.user`
- `roles/storage.objectViewer` (if using GCS)

```bash
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/cloudsql.client"
```

## Related Documentation

- [Main README](../README.md) - Project overview
- [Getting Started](getting-started.md) - Local development setup
- [Architecture](architecture.md) - System design details
- [Troubleshooting](troubleshooting.md) - Common deployment issues
- [Backend README](../backend/README.md) - API implementation
- [Frontend README](../frontend/README.md) - UI documentation
