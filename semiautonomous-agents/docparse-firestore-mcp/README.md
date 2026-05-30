# Docparse Firestore RAG & MCP Server for Gemini Enterprise

A state-of-the-art solution to ingest PDF-derived Markdowns into **Cloud Firestore** and expose them as a secure **Model Context Protocol (MCP) server** on Cloud Run.

This architecture enables **Gemini Enterprise** to ground answers using clean page-by-page Markdown while retaining high-fidelity links and exact citations back to the original PDF documents.

---

## 🗺️ Architectural Workflow

```mermaid
flowchart LR
    PDF[1. Source PDFs] -->|docparse pipeline| MD[2. Markdown Chunks]
    MD -->|index_to_firestore.py| EMB[3. text-embedding-005]
    EMB -->|Vector + Grounding links| FS[(4. Cloud Firestore)]
    FS <-->|find_nearest vector search| CR[5. Cloud Run MCP Server]
    CR <-->|OIDC Bearer Auth| GE([6. Gemini Enterprise app])

    classDef step fill:#e8f0fe,stroke:#1a73e8,stroke-width:2px,color:#000
    classDef store fill:#fef7e0,stroke:#f9ab00,stroke-width:2px,color:#000
    classDef target fill:#e6f4ea,stroke:#137333,stroke-width:2px,color:#000
    class PDF,MD,EMB step
    class FS store
    class CR,GE target
```

---

## 🚀 Step-by-Step Implementation Guide

Follow these **four simple steps** to deploy and configure this system in any Google Cloud / Gemini Enterprise environment.

### 📍 Step 1: Ingest Markdown & Metadata to Firestore

The ingestion pipeline segments docparse-extracted Markdown files by page and creates 768-dimensional embeddings using Vertex AI.

1. **Configure Environment:** Ensure you have `.env` or set project parameters.
2. **Execute Ingestion Script:**
   ```bash
   uv run pipeline/index_to_firestore.py \
       --project <your-gcp-project-id> \
       --collection docparse_chunks \
       --markdown-bucket gs://<your-project-id>-docparse-out \
       --pdf-bucket gs://<your-project-id>-docparse-in
   ```

> [!TIP]
> **Grounding Magic:** This script automatically builds GCS URIs (`gs://.../file.pdf`) and secure HTTPS grounding URLs (`https://storage.googleapis.com/.../file.pdf#page=N`) on every page chunk, mapping the raw visual layout directly back to original PDF pages inside Gemini Enterprise.

---

### 📍 Step 2: Build & Deploy the MCP Server to Cloud Run

The Cloud Run server runs our custom, secure FastMCP application.

1. **Build Container:**
   ```bash
   gcloud builds submit --tag gcr.io/<your-gcp-project-id>/docparse-firestore-mcp:latest ./mcp_server
   ```
2. **Deploy to Cloud Run:**
   ```bash
   gcloud run deploy docparse-firestore-mcp \
       --image gcr.io/<your-gcp-project-id>/docparse-firestore-mcp:latest \
       --region us-central1 \
       --set-env-vars "FIRESTORE_PROJECT=<your-gcp-project-id>,FIRESTORE_COLLECTION=docparse_chunks" \
       --no-allow-unauthenticated
   ```

---

### 📍 Step 3: Register as an MCP Datastore in Gemini Enterprise

Configure Gemini Enterprise's main chat console to leverage this MCP server as an active grounding datastore using Google's Discovery Engine v1alpha custom data connectors API.

1. **Run Automated Datastore Registration:**
   ```bash
   EXPORT GE_PROJECT_ID="<your-gcp-project-id>"
   EXPORT GE_PROJECT_NUMBER="<your-gcp-project-number>"
   EXPORT GE_ENGINE_ID="<your-gemini-enterprise-engine-id>"
   EXPORT MCP_SERVICE_URL="https://docparse-firestore-mcp-<hash>.run.app"
   
   uv run register_datastore.py
   ```

---

### 📍 Step 4: Register Agent in Gemini Enterprise Panel

Ensure the Firestore RAG agent is active inside the chat sidebar/agent picker panel of Gemini Enterprise.

1. **Deploy ADK Reasoning Engine & Set Variable:**
   Ensure `REASONING_ENGINE_RES` is set in your env.
2. **Run Agent Registration Script:**
   ```bash
   EXPORT AS_APP="<your-gemini-enterprise-app-id>"
   
   uv run register_agent.py
   ```

---

## 📂 Folder Layout

* **`pipeline/index_to_firestore.py`**: Splits Markdowns into pages and indexes them in Firestore with `text-embedding-005` embeddings.
* **`mcp_server/`**: Contains the Starlette app (`server.py`), native vector search module (`firestore_search.py`), and Google OIDC verification middleware (`auth.py`).
* **`register_datastore.py`**: Connects the MCP server as a `custom_mcp` Datastore in Gemini Enterprise.
* **`register_agent.py`**: Adds your agent to the Gemini Enterprise Chat agent picker panel.
* **`RESEARCH_MCP_TOOLBOX.md`**: Comparison and template setups for Google's `mcp-toolbox` (formerly Gen AI Toolbox for Databases) vs. FastMCP.
