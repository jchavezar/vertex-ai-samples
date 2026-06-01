# Custom Skill: Shutter Vibe Engine Development Guide

This skill file defines the mandatory coding guidelines, technical stack, and security protocols for any Antigravity AI coding assistant working on the Shutter Vibe Engine project.

---

## 1. Core Technology Stack

All modifications, enhancements, or rebuilds of this system must adhere strictly to these core technologies:
* **Backend**: FastAPI (Python 3.12+), Uvicorn.
* **Frontend Structure**: HTML5 (semantic layout only, no layout tables).
* **Frontend Logic**: Vanilla modern JavaScript (ES6+).
* **Frontend Styling**: Vanilla modern CSS (custom properties, HSL color palettes, flexbox/grid layouts). No TailwindCSS or external component libraries unless explicitly requested.
* **Data Storage**: Google Cloud Firestore (documents & collections) and Google Cloud Storage (GCS).
* **Database Backends**: Pluggable dispatcher supporting:
  - **Vertex AI Vector Search** (TREE_AH ANN index endpoints).
  - **Google BigQuery** (`VECTOR_SEARCH` table-valued function, COSINE distance).
* **AI Models**: Google GenAI SDK (Vertex AI enabled):
  - Text Embeddings: `gemini-embedding-001` (GA)
  - Multimodal Embeddings: `gemini-embedding-2-preview`
  - Image/Audio Captioning: `gemini-3.1-flash-lite-preview`
  - Video Captioning: `gemini-3-flash-preview`
  - Fallback/Chat Assist: `gemini-2.5-flash`

---

## 2. API & SDK Integration Guidelines

* **Vertex AI Enforcer**: Always set `GOOGLE_GENAI_USE_VERTEXAI = "True"` in environment variables before initializing the `genai.Client()`.
* **Cosine Similarity**: All embeddings must be L2-normalized immediately after extraction:
  ```python
  normalized_vector = vector / np.linalg.norm(vector, axis=-1, keepdims=True)
  ```
  This guarantees that Cosine Similarity can be calculated via simple, ultra-fast dot product multiplication (`a @ b.T`).
* **Asymmetric Task Types**: Always pair search query embeddings (`RETRIEVAL_QUERY`) against document embeddings (`RETRIEVAL_DOCUMENT`) to maximize separation gaps. Do not use symmetric semantic similarity for asymmetric query-passage lookup.

---

## 3. Secure Development Rules (Zero-Leak)

* **Secrets Management**: Under no circumstances commit API keys, service account keys, `.env` files, or `.pem` files to Git repositories.
* **Git Exclusions**: Ensure that `.gitignore` includes the following sections to prevent accidental leakages:
  ```gitignore
  .env
  .env.*
  *.json
  !manifest.json
  *.key
  *.pem
  ```
* **Authentication**: Use Google Cloud Application Default Credentials (ADC) for local testing, and IAM Service Accounts for Cloud Run / Cloud Batch deployments.

---

## 4. Code Preservation & Testing

* **Preserve Docstrings**: Maintain all existing docstrings, class constructors, and metadata configurations unless refactoring is explicitly requested.
* **Probe-First Verification**: Before writing or modifying large components, write a minimal, standalone capability script in the `demos/` directory to test connection strings, credential validity, and API shapes synchronously.
