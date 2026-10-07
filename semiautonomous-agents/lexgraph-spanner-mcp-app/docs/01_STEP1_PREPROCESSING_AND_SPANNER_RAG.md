# 01 — Cloud Spanner Hybrid GraphRAG & Intapp Zero-Latency Ethical Wall Architecture

## Executive Summary

When enterprise M&A and Private Equity deal teams analyze precedent agreements across iManage DMS, Intapp Walls, and partner email silos, traditional vector-only RAG fails on three fronts:
1. **Post-Retrieval Ethical Wall Leakage**: Standard vector stores retrieve top-$k$ chunks first and filter permissions afterward, risking metadata leakage or starving the top-$k$ window when conflicted deals are pruned.
2. **Exact Numerical & Section Reference Blindness**: Dense embeddings struggle to distinguish `Section 8.02(b)` (`0.75% Cap`) from `Section 8.04(a)` (`0.50% Cap`) without lexical BM25 scoring.
3. **Multi-Hop Relational Context Loss**: Connecting a partner's unfiled tax email (`EM-9901`) to a temporal 30-day access grant (`TeammateGrants`) and an opposing counsel redline (`DOC-M331-02`) requires transactional graph traversal.

To solve all three in a **single database engine**, this architecture uses **Google Cloud Spanner** (`lexgraph-legal-spanner / lexgraph-legal-context`) combining **ISO GQL Property Graph (`LexGraphLegalGraph`)**, **3,072-dimension `gemini-embedding-2` Vector Search**, **Full-Text Search (`TOKENLIST` / BM25)**, and **Reciprocal Rank Fusion (RRF)** in a single SQL query (`~200–340ms` end-to-end).

---

## Single-Pass Hybrid GraphRAG Architecture

```text
┌──────────────────────────────────────────────────────────────────────────┐
│  LAWYER QUERY + IDENTITY (e.g. s-jenkins@lexgraph.com -> Lawyer L-001)       │
└───────────────────────────────────┬──────────────────────────────────────┘
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  STEP 1: VERTEX AI QUERY EMBEDDING (~90ms)                               │
│  • Model: gemini-embedding-2 (RETRIEVAL_QUERY, 3,072 dimensions, L2 norm)│
└───────────────────────────────────┬──────────────────────────────────────┘
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  STEP 2: CLOUD SPANNER SINGLE-PASS SQL + GQL + RRF (~120ms)              │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │ A. 0-ms Intapp Ethical Wall Pre-Filter (Relational / GQL Join)     │  │
│  │    JOIN LawyerAuthorizedMatter ON lawyer_id = 'L-001'              │  │
│  │    WHERE NOT EXISTS (SELECT 1 FROM EthicalWallBlocks ...)          │  │
│  │    -> Automatically quarantines DOC-M999-WALL at 0ms               │  │
│  ├────────────────────────────────────────────────────────────────────┤  │
│  │ B. Dense Vector Branch (3,072-dim Cosine Similarity)               │  │
│  │    1.0 - COSINE_DISTANCE(c.embedding, @query_vec) AS vec_sim       │  │
│  ├────────────────────────────────────────────────────────────────────┤  │
│  │ C. Lexical Full-Text Search Branch (Spanner TOKENLIST BM25)        │  │
│  │    SCORE(c.fts_tokens, @fts_query) AS bm25_score                   │  │
│  ├────────────────────────────────────────────────────────────────────┤  │
│  │ D. Reciprocal Rank Fusion (RRF)                                    │  │
│  │    (1.0 / (60 + vec_rank)) + (1.0 / (60 + fts_rank)) AS hybrid_rrf │  │
│  └────────────────────────────────────────────────────────────────────┘  │
└───────────────────────────────────┬──────────────────────────────────────┘
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  STEP 3: ACID GRAPH WRITE-BACK (30-Day Teammate Grant for EM-9901)       │
│  • Commits live TeammateGrants edge (L-003 Marcus Thorne -> L-001)       │
│  • Unlocks unfiled Section 338(h)(10) tax email in <50ms                 │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## Property Graph Schema (`LexGraphLegalGraph`)

```text
  (Lawyers: L-001 Sarah Jenkins)
       │
       ├──[:AUTHORIZED_FOR]────────► (Matters: M-331, M-215, M-518, M-402, M-109)
       │                                    │
       │                                    └──► (Documents: DOC-M331-01..04, etc.)
       │                                                │
       │                                                └──► (Clauses: 3072d Vec + FTS)
       │
       ├──[:ETHICAL_WALL_BLOCK]────► (Matters: M-999 Hostile Bid -> QUARANTINED)
       │
       └──[:TEAMMATE_GRANT (30d)]◄── (Lawyers: L-003 Marcus Thorne -> EM-9901)
```

See [`spanner-graphrag/schema.sql`](../spanner-graphrag/schema.sql), [`spanner-graphrag/provision_spanner_graph.py`](../spanner-graphrag/provision_spanner_graph.py), and [`spanner-graphrag/seed_spanner_graph.py`](../spanner-graphrag/seed_spanner_graph.py) for the complete executable DDL and seeding pipeline.
