# GCP Architecture Mapping: SharePoint Document Restructure Portal

This document outlines the purpose and architectural role of every Google Cloud Platform (GCP) component required to deploy the **SharePoint Document Restructure & AI Governance Portal** at scale.

---

## Architecture Diagram Overview

```
 [ SharePoint Online ]
         │ (Graph API delta check)
         ▼
 ┌────────────────────────────────────────────────────────┐
 │ 1. Ingestion Layer                                     │
 │  - Cloud Run (Discovery Service)                       │
 │  - Cloud Tasks (Distributed Pacing Queue)              │
 │  - MemoryStore Redis (Global Rate Limit Tracker)       │
 └───────────────────────┬────────────────────────────────┘
                         │ (In-memory chunking / Transient upload)
                         ▼
 ┌────────────────────────────────────────────────────────┐
 │ 2. AI Enrichment & DLP Layer                           │
 │  - Gemini 2.5 Flash / Pro (Metadata, Confidence)       │
 │  - Sensitive Data Protection (DLP API)                 │
 └───────────────────────┬────────────────────────────────┘
                         │ (Write state)
                         ▼
 ┌────────────────────────────────────────────────────────┐
 │ 3. Stateful Storage & Workflows                        │
 │  - Firestore (State Machine, Exclusions, Rules)        │
 │  - React QA Console on Cloud Run                       │
 └───────────────────────┬────────────────────────────────┘
                         │ (Final approved metadata sync)
                         ▼
 ┌────────────────────────────────────────────────────────┐
 │ 4. Registry & Governance                               │
 │  - BigQuery (Metadata Catalog + Action Audit Logs)     │
 │  - Dataplex (Policy Tags, Column Masking, Lineage)     │
 │  - Vertex AI Vector Search (Index + ACL Pre-filters)   │
 └────────────────────────────────────────────────────────┘
```

---

## Component Breakdown & Justification

### 1. Ingestion & Pacing Components

#### A. Cloud Run (Ingestion & Worker Services)
*   **Why we need it:** We need a serverless, highly-scalable execution environment to host our Graph API connectors. 
*   **Role:**
    *   **Discovery Service:** Triggers on SharePoint webhooks or scheduler timers, calls Microsoft Graph API to find modified files, and enqueues tasks.
    *   **Processing Worker:** Downloads files in-memory, sends them to Gemini/DLP, and saves extraction state.
*   **Alternative considered:** Cloud Functions. (Rejected because Cloud Run allows for containerized execution environments, longer timeout thresholds, and better local emulation/docker parity).

#### B. Cloud Tasks (Paced Task Queue)
*   **Why we need it:** Microsoft Graph API throttles aggressively when QPS bursts. Cloud Tasks allows us to buffer downloads and pace them to a strict, maximum tenant limit (e.g., 10 QPS).
*   **Role:** Buffers individual document ingestion payloads. If a task fails due to a `429 Too Many Requests` status, Cloud Tasks reads the `Retry-After` header and delays retry execution automatically.

#### C. MemoryStore for Redis (Rate Limiting)
*   **Why we need it:** A shared, low-latency cache is required to track actual API request throughput across all parallel Cloud Run workers.
*   **Role:** Acts as a centralized rate-limiter, preventing worker instances from concurrently exceeding the SharePoint tenant limits.

---

### 2. AI Enrichment & Data Protection

#### A. Gemini 2.5 Flash & Pro (Vertex AI API)
*   **Why we need it:** To classify document types, extract compliance rules, identify entities (Client, Sector), and generate metadata.
*   **Role:** 
    *   **Gemini 2.5 Flash:** Fast, cheap classification and structured tag extraction.
    *   **Gemini 2.5 Pro:** Used for complex legal clauses, like analyzing signing status or flagging non-standard liability limits.
    *   **Explainability:** Structured JSON response schema includes reasoning/rationale strings alongside tags for audit QA.

#### B. Sensitive Data Protection (DLP API)
*   **Why we need it:** To prevent compliance failures, we must scan metadata and chunks for PII (names, SSNs, credit cards) before they are indexed into search stores or returned in chat answers.
*   **Role:** Acts as an automatic post-extraction masking gate and a pre-response chat guardrail.

---

### 3. Stateful Workflows & Storage

#### A. Firestore (State & Configuration Database)
*   **Why we need it:** We need a flexible, document-based transactional database to store ingestion configurations, taxonomy mappings, and human-in-the-loop validation queue states.
*   **Role:** 
    *   Tracks document state machine steps (`PENDING_QA`, `APPROVED`, etc.).
    *   Stores taxonomy lists, confidence thresholds, and client exclusion tables.
*   **Alternative considered:** Cloud SQL. (Firestore is preferred for its sub-millisecond document lookups, lack of schema lock, and native real-time websocket sync capabilities for UI updates).

#### B. Google Cloud Storage (GCS)
*   **Why we need it:** Transient storage for large documents (>15MB) that cannot be parsed in Cloud Run memory.
*   **Role:** Hosts transient files. Configured with a 1-day **Lifecycle Management Policy** to automatically delete raw files post-extraction.

---

### 4. Governance & Semantic Search

#### A. BigQuery (Metadata Catalog & Audit Ledger)
*   **Why we need it:** To serve as the canonical enterprise metadata repository and secure compliance registry.
*   **Role:**
    *   Stores structured document catalogs.
    *   Enforces Row-Level Security (RLS) to restrict users to documents matching their customer scope.
    *   Acts as an append-only, tamper-evident audit log for all user actions (approvals, tag edits, overrides).

#### B. Dataplex (Data Governance)
*   **Why we need it:** For unified data governance across files (GCS) and tables (BigQuery).
*   **Role:**
    *   **Policy Tags:** Applied to sensitive columns (e.g., PII columns) in BigQuery to restrict access based on GCP user identity.
    *   **Lineage API:** Tracks document transformations from ingestion source to downstream catalog.

#### C. Vertex AI Vector Search
*   **Why we need it:** To provide semantic, semantic-density-aware search results for the chat interface.
*   **Role:** Indexes text chunks and matches them using cosine similarity. It enforces **ACL Pre-Filtering** at query time using Entra ID Security Group IDs stored as metadata tags.
