# Getting Started

[<- Back to Main README](../README.md) | [Architecture](architecture.md) | [Deployment](deployment.md)

> **Complete guide to setting up PGVector Document Nexus from scratch**

This guide walks you through creating a Cloud SQL instance with pgvector, configuring the environment, and running the application.

## Prerequisites

- Google Cloud SDK (`gcloud`) authenticated with a project
- Python 3.12+
- Node.js 20+
- `uv` package manager (will be installed if missing)

## 1. Cloud SQL Setup

### 1.1 Create Cloud SQL PostgreSQL Instance

If you don't have an existing Cloud SQL instance with pgvector:

```bash
# Set your project
export PROJECT_ID=your-project-id
export REGION=us-central1
export INSTANCE_NAME=pgvector-nexus

gcloud config set project $PROJECT_ID

# Create PostgreSQL 15 instance with pgvector enabled
gcloud sql instances create $INSTANCE_NAME \
  --database-version=POSTGRES_15 \
  --cpu=2 \
  --memory=8GB \
  --region=$REGION \
  --root-password=your-secure-password \
  --database-flags=cloudsql.enable_pgvector=on

# This takes 5-10 minutes
```

### 1.2 Create Database

```bash
# Create the database
gcloud sql databases create pgvector_doc_nexus --instance=$INSTANCE_NAME
```

### 1.3 Create Database User

```bash
# Create a user for the application
gcloud sql users create emb-admin \
  --instance=$INSTANCE_NAME \
  --password=your-db-password
```

### 1.4 Authorize Your IP

```bash
# Get your current public IP
MY_IP=$(curl -s ifconfig.me)
echo "Your IP: $MY_IP"

# Authorize it for Cloud SQL access
gcloud sql instances patch $INSTANCE_NAME \
  --authorized-networks=$MY_IP/32 \
  --quiet
```

### 1.5 Get Instance IP Address

```bash
# Get the Cloud SQL public IP
gcloud sql instances describe $INSTANCE_NAME \
  --format="value(ipAddresses[0].ipAddress)"
```

Save this IP - you'll need it for the `.env` file.

## 2. Project Setup

### 2.1 Clone and Navigate

```bash
cd vertex-ai-samples/semiautonomous-agents/pgvector_document_nexus
```

### 2.2 Create Environment File

Create `.env` in the project root:

```bash
cat > .env << 'EOF'
# Google Cloud Configuration
PROJECT_ID=your-project-id
LOCATION=us-central1

# Cloud SQL Configuration
DB_HOST=your-cloud-sql-ip
DB_PORT=5432
DB_NAME=pgvector_doc_nexus
DB_USER=emb-admin
DB_PASSWORD=your-db-password
EOF
```

Replace placeholders with your actual values.

## 3. Install Dependencies

### 3.1 Install uv (if not installed)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"
```

### 3.2 Backend Dependencies

```bash
cd backend
uv sync
```

### 3.3 Frontend Dependencies

```bash
cd ../frontend
npm install
```

## 4. Initialize Database

The database schema is automatically created on first run, but you can also initialize it manually:

```bash
cd backend
uv run python init_db.py
```

Expected output:
```
Connecting to Cloud SQL...
Connected! Initializing schema...
  - pgvector extension enabled
  - document_chunks table created
  - HNSW index created

pgvector version: 0.8.1
Current document chunks: 0

Database initialized successfully!
```

## 5. Run the Application

### 5.1 Start Backend (Terminal 1)

```bash
cd backend
uv run uvicorn main:app --host 0.0.0.0 --port 8002
```

The backend starts on `http://localhost:8002`

### 5.2 Start Frontend (Terminal 2)

```bash
cd frontend
npm run dev
```

The frontend starts on `http://localhost:5173`

## 6. Test the Application

### 6.1 Health Check

```bash
curl http://localhost:8002/api/health
# Expected: {"status":"healthy","vector_store":"pgvector"}
```

### 6.2 Open the UI

Open `http://localhost:5173` in your browser.

### 6.3 Upload a Document

1. Click the upload zone or drag a PDF file
2. Watch the processing overlay show extraction progress
3. View the indexed chunks in the Data tab
4. Check the Pages tab for annotated images

### 6.4 Test Chat

1. Type a question about your uploaded document
2. The system will:
   - Embed your query using Vertex AI
   - Search pgvector for similar chunks
   - Generate a grounded response with citations
3. Citations like `[1]`, `[2]` link to source chunks

## 7. Verify Database

Check that data is stored in pgvector:

```bash
# Using psql (if installed)
PGPASSWORD='your-db-password' psql -h your-cloud-sql-ip -U emb-admin -d pgvector_doc_nexus -c "
SELECT document_name, COUNT(*) as chunks,
       array_length(embedding, 1) as embedding_dim
FROM document_chunks
GROUP BY document_name;
"
```

Or via the API:
```bash
curl http://localhost:8002/api/documents
```

## Troubleshooting

### Connection Timeout

**Symptom**: `TimeoutError` when connecting to Cloud SQL

**Solutions**:
1. Verify your IP is authorized:
   ```bash
   gcloud sql instances describe $INSTANCE_NAME \
     --format="yaml(settings.ipConfiguration.authorizedNetworks)"
   ```
2. Re-authorize if your IP changed:
   ```bash
   MY_IP=$(curl -s ifconfig.me)
   gcloud sql instances patch $INSTANCE_NAME \
     --authorized-networks=$MY_IP/32
   ```

### Password Authentication Failed

**Symptom**: `InvalidPasswordError`

**Solution**: Reset the user password:
```bash
gcloud sql users set-password emb-admin \
  --instance=$INSTANCE_NAME \
  --password='new-password'
```
Then update `.env` with the new password.

### Model Not Found

**Symptom**: `404 NOT_FOUND` for Gemini model

**Solution**: The pipeline uses `gemini-2.5-flash` which is available in `us-central1`. Ensure your `LOCATION` in `.env` is set correctly.

### Port Already in Use

**Symptom**: `Address already in use` error

**Solution**:
```bash
# Find and kill process on port 8002
lsof -ti:8002 | xargs kill -9
```

## Quick Commands Reference

```bash
# Start everything (from project root)
cd backend && uv run uvicorn main:app --host 0.0.0.0 --port 8002 &
cd ../frontend && npm run dev &

# Stop everything
lsof -ti:8002 | xargs kill -9
lsof -ti:5173 | xargs kill -9

# Check logs
tail -f /tmp/pgvector_server.log

# Re-initialize database
cd backend && uv run python init_db.py
```

## Related Documentation

- [Main README](../README.md) - Project overview
- [Architecture](architecture.md) - System design details
- [Deployment](deployment.md) - Production deployment
- [Troubleshooting](troubleshooting.md) - More debugging help
- [Backend README](../backend/README.md) - API implementation
- [Frontend README](../frontend/README.md) - UI documentation
