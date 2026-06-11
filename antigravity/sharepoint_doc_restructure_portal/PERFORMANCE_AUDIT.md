# Performance Audit Report: SharePoint Document Restructure Pipeline

**Date:** 2026-06-10
**Target Project:** `vtxdemos`
**Model:** `gemini-3.5-flash`
**Region:** `global`
**Iterations:** 5

---

## Executive Summary
This report presents the latency benchmarks for the SharePoint Document Restructure Pipeline. The pipeline consists of three sequential steps: PII Redaction (DLP), Structured Metadata Ingestion, and Dynamic Ontology Mapping. 

The average total pipeline ingestion latency is **17.282 seconds**. While the initial processing (DLP and Gemini extraction) takes under 20 seconds, downstream indexing to search engines introduces significant propagation delays, ranging from seconds (BigQuery) to minutes (Vertex AI Vector Search / Discovery Engine).

---

## Benchmark Results

The pipeline was executed for 5 iterations. Below is the breakdown of the latency (in seconds) for each run.

| Run # | DLP Scan (s) | Structured Ingestion (s) | Ontology Map (s) | Total Latency (s) |
|---|---|---|---|---|
| 1 | 0.150 | 6.820 | 5.854 | 12.824 |
| 2 | 0.150 | 6.232 | 13.842 | 20.224 |
| 3 | 0.150 | 8.324 | 7.487 | 15.961 |
| 4 | 0.150 | 6.777 | 9.860 | 16.787 |
| 5 | 0.150 | 9.636 | 10.826 | 20.612 |
| **Average** | **0.150** | **7.558** | **9.574** | **17.282** |

### Key Observations
* **PII Redaction (DLP Scan):** Constant at **0.150s** due to simulated mock execution.
* **Structured Metadata Extraction:** Averaged **7.558s**, ranging from 6.23s to 9.64s. This represents the time taken by `gemini-3.5-flash` to extract structured JSON metadata against the `ExtractedOntology` schema.
* **Dynamic Ontology Generation:** Averaged **9.574s**, showing higher variance (from 5.85s to 13.84s). This step generates schema definitions and relations using `gemini-3.5-flash` with the `DynamicOntologyMap` schema.

---

## Downstream Sync Estimates (GCP)

Once the metadata package is ingested, downstream systems sync at different rates:

| Downstream Target | Estimated Sync Latency | Type | Description |
|---|---|---|---|
| **Firestore Registry** | ~0.05 - 0.1 seconds | Near Real-Time | State update for document registry. |
| **BigQuery Table** | ~1.00 - 3.0 seconds | Near Real-Time | Streaming ingestion write for analytics. |
| **Vertex AI Vector Search** | ~10.0 - 15.0 minutes | Batch | Requires batch rebuild of index for vector search. |
| **Discovery Engine** | ~10.0 - 20.0 minutes | Incremental | Incremental crawl/update for keyword search. |

---

## Architectural Implications
1. **User Experience:** The ~17-second ingestion time means the document restructure portal must handle ingestion asynchronously. Users should see an "Ingesting..." state and should not block on the UI.
2. **Search Availability:** Although the document state is updated in Firestore almost instantly (~0.1s), the document will not be searchable via Vector Search or Discovery Engine for **10 to 20 minutes**. This delay must be communicated to users, or a hybrid search approach (querying Firestore directly for recent docs) should be considered for immediate availability.
3. **Ontology Variance:** The high variance in Ontology Map generation (up to 13.8s in Run 2) suggests that network conditions or model load can significantly impact total time. A retry or timeout mechanism should be implemented in production.
