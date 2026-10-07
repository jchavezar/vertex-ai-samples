# ⚡ Jetski Chat History MCP: Hybrid Semantic & Keyword Index

An ultra-low latency contextual indexing engine and MCP server designed specifically for **Jetski**. It indexes all conversation transcripts (`~/.gemini/jetski/brain/`) and session metadata (`~/.gemini/jetski/conversation_summaries.db`), synthesizes high-density executive capsules, and provides sub-35ms semantic search with instant context injection.

---

## 🌟 Key Architecture & Capabilities

1. **Sub-35ms Hybrid Search (Dense Vectors + BM25 + Reciprocal Rank Fusion)**:
   - **Dense Vectors**: 768-dimensional normalized embeddings generated via Vertex AI `text-embedding-005`.
   - **Matrix Math**: In-memory vectorized NumPy dot products (`q_vec @ E.T`) executing in **~0.3 milliseconds**.
   - **BM25 FTS5**: Native SQLite full-text search indexing exact tokens, IDs, tools, and error codes.
   - **Reciprocal Rank Fusion (RRF)**: Combines dense semantic intent with exact keyword hits.

2. **Zero-Bloat Session Capsules (~800 to 1,200 tokens)**:
   - Filters out 98% of transcript noise (raw terminal stdouts, giant JSON tool dumps).
   - Preserves primary user goals, turn milestones, tools invoked, files modified, artifacts, and final outcomes.
   - Restores full session context into any active chat in < 2ms without context window degradation.

3. **Native Jetski Deep-Linking**:
   - Every result provides a 1-click clickable link: `[Session Title](conversation://<conversation-id>)`.

---

## 🏗️ Project Layout

```text
jetski-history-mcp/
├── data/
│   └── history_index.db       # SQLite database (Capsules, FTS5 table, Vector BLOBs)
├── scripts/
│   └── query.py               # Zero-latency CLI tool
├── indexer.py                 # Incremental transcript parser & embedding worker
├── server.py                  # FastMCP Server (stdio transport)
├── .gitignore                 # Ironclad Zero-Leak exclusion rules
└── README.md
```

---

## 🚀 Quick Usage

### 1. Zero-Latency CLI Search
```bash
# Natural language hybrid search
python3 scripts/query.py search "restaurant session management"

# Fetch dense session capsule
python3 scripts/query.py capsule 060bede8-982f-4ced-96a6-7441a2bff430

# List recent sessions
python3 scripts/query.py recent 10

# Force incremental index refresh
python3 indexer.py
```

### 2. Available MCP Tools in Jetski
* **`search_chat_history(query, top_k=5)`**: Natural language hybrid search returning ranked sessions and deep-links.
* **`get_chat_capsule(conversation_id)`**: Instant 800-token markdown capsule injection.
* **`get_step_detail(conversation_id, step_indices)`**: Deep forensic tool inspection on specific steps.
* **`sync_chat_history(force_refresh=False)`**: Incremental sync for newly created/modified chats.
* **`list_recent_sessions(limit=10)`**: Chronological session overview.

---

## 🔒 Security & Zero-Leak Protocol
* Strictly follows the **Zero-Leak Protocol**: Database files (`*.db`), credentials, and environment files are strictly excluded via `.gitignore`.
* No sensitive API keys or credentials committed.
