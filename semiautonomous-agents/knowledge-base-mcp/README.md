# Knowledge Base MCP Server

Semantic search over Claude Code conversation transcripts. Extracts problem-solution patterns from JSONL history files, stores them in Firestore with vector embeddings, and serves them via MCP.

## Architecture

```
HOT:   MEMORY.md (always in context, ~2K tokens)
WARM:  Firestore + native vector search (768-dim)
COLD:  Raw JSONL transcripts (local / GCS)

┌──────────────────────┐     ┌─────────────────────┐
│  Extraction Pipeline │     │   MCP Server        │
│                      │     │   (Cloud Run)       │
│  JSONL → Parse       │     │                     │
│       → Chunk        │     │  search_knowledge   │
│       → LLM Extract  │     │  expand_context     │
│       → Embed        │     │  ingest_session     │
│       → Firestore    │     │  ingest_all_sessions│
└──────────────────────┘     │  get_stats          │
                             └─────────────────────┘
```

## How It Works

### Step 1: Parsing

Claude Code stores every conversation as a JSONL transcript file in `~/.claude/projects/`. Each line is a JSON object with fields like `type` (user/assistant/system), `message.content`, `message.model`, `message.usage` (token counts), timestamps, tool names, and more.

The parser streams these files line-by-line (handles 161MB+ files without OOM), extracts plain text from content arrays, strips thinking blocks and base64 images, and yields clean `TranscriptMessage` objects.

### Step 2: Chunking

The chunker splits a conversation into topic-coherent segments of 3-30 messages using heuristics:
- **Time gaps** > 10 minutes between messages
- **Working directory changes** (CWD shift = likely new task)
- **Tool diversity shifts** (e.g., switching from Read/Edit to Bash/Grep)
- **Explicit markers** in user messages ("next", "now let's", "switching to")

No LLM is used for chunking — it's free and fast.

### Step 3: LLM Extraction

Each segment is sent to Gemini 2.5 Flash (or configurable model) with a structured extraction prompt. The LLM determines:
- Was a problem **actually solved**? (skip if no)
- What was the **problem** and **error message**?
- What **failed attempts** were made? (scored 0.0-1.0 by closeness to solution)
- What was the **final solution**? (scored 0.0-1.0 by confidence)
- What are the **anti-patterns** to avoid?

Only resolved patterns are kept. Failed segments are discarded.

### Step 4: Embedding + Storage

Extracted items get a `search_text` field (LLM-generated, optimized for semantic search), which is embedded using Vertex AI `text-embedding-004` (768-dim). Items are stored in Firestore with the embedding as a native vector field for KNN search.

### Step 5: Retrieval

The MCP server exposes `search_knowledge(query)` which:
1. Embeds the query with `text-embedding-004` (RETRIEVAL_QUERY task type)
2. Runs Firestore `find_nearest` (cosine distance KNN)
3. Returns scored results with problem, solution, failed attempts, and expand hints

`expand_context()` retrieves the cleaned conversation messages around a result.

## Scoring Guidelines

| Score | Meaning |
|-------|---------|
| 0.9-1.0 | Solution verified working, clear root cause, generalizable |
| 0.7-0.8 | Appears to work, not fully verified or environment-specific |
| 0.5-0.6 | Partial fix or workaround, root cause unclear |
| 0.3-0.4 | Attempted fix, unclear if it resolved the issue |
| 0.0-0.2 | Guess or suggestion, not actually tested |

Failed attempt scores indicate how close the attempt was to the actual solution (1.0 = almost right, 0.0 = completely wrong approach).

## Firestore Schema

```
sessions/{session_id}
  - date, query_count, model_ids[], source_file
  - total_input_tokens, total_output_tokens

knowledge/{auto_id}
  - session_id, model_id, timestamp
  - problem, error_message
  - solution, solution_score (0.0-1.0)
  - failed_attempts: [{attempt, reason_failed, score}]
  - anti_patterns: [...]
  - services: [], tools_used: []
  - search_text (optimized for embedding)
  - anchor_idx, window: [start, end]
  - embedding: vector(768)
  - expanded_messages: [{role, text, tools_used}]
```

## MCP Tools

### Search Tools
| Tool | Description |
|------|-------------|
| `search_knowledge(query, top_k, service_filter)` | Semantic search for problem-solution patterns |
| `search_playbooks(query, top_k, project_filter, category_filter)` | Search playbooks (architecture, patterns, ideas, recipes) |
| `recent_knowledge(limit, service_filter)` | Get most recent items by timestamp |
| `get_topic_timeline(query, top_k, service_filter)` | **NEW** - Chronological evolution of a topic across sessions |
| `expand_context(session_id, start_idx, end_idx)` | Expand a result to full conversation context |

### Ingestion Tools
| Tool | Description |
|------|-------------|
| `ingest_session(jsonl_path, dry_run)` | Ingest a single JSONL transcript |
| `ingest_all_sessions(sessions_dir, dry_run)` | Batch ingest all JSONLs in a directory |

### Management Tools
| Tool | Description |
|------|-------------|
| `delete_knowledge(title_query, collection)` | Delete entries by title |
| `get_stats()` | Knowledge base statistics |

## Documentation

- [Tools Reference](docs/TOOLS.md) - All 9 tools with examples
- [Architecture](docs/ARCHITECTURE.md) - Pipeline, Firestore, embeddings
- [Deployment](docs/DEPLOYMENT.md) - Cloud Run deployment

## Setup

### Prerequisites
- GCP project with Firestore enabled
- Vertex AI API enabled (for embeddings + Gemini Flash)
- Python 3.12+, uv

### Install

```bash
cd semiautonomous-agents/knowledge-base-mcp

# 1. Create .env
cp .env.example .env
# Edit: GOOGLE_CLOUD_PROJECT=your-project-id

# 2. Install dependencies
uv venv .venv && source .venv/bin/activate
uv pip install -e .

# 3. Create Firestore vector index (one-time)
gcloud firestore indexes composite create \
  --collection-group=knowledge \
  --field-config=vector-config='{"dimension":768,"flat":{}}',field-path=embedding
```

## Usage

### Extract from CLI (recommended for first run)

```bash
# Dry run — extract and review without writing to Firestore
python -m pipeline.run --dry-run --output /tmp/results.json ~/.claude/projects/*/SESSION_ID.jsonl

# Review the output
python -c "import json; d=json.load(open('/tmp/results.json')); [print(f'[{i[\"solution_score\"]}] {i[\"problem\"]}') for i in d['items']]"

# Full run — extract, embed, and load into Firestore
python -m pipeline.run ~/.claude/projects/*/SESSION_ID.jsonl

# Use a different extraction model
EXTRACTION_MODEL=gemini-2.5-pro python -m pipeline.run /path/to/transcript.jsonl
```

### Run MCP Server Locally

```bash
python server.py
# Server starts on http://0.0.0.0:8080/mcp
```

### Ingest via MCP Tool (from Claude Code or Gemini CLI)

Once connected, use the `ingest_session` or `ingest_all_sessions` tools:
```
> ingest_session(jsonl_path="/home/user/.claude/projects/.../session.jsonl", dry_run=True)
> ingest_all_sessions(sessions_dir="/home/user/.claude/projects/my-project/", dry_run=False)
```

## Deploy to Cloud Run

```bash
chmod +x deploy.sh
./deploy.sh
```

## Connect

**Claude Code:**
```bash
# Start proxy (in a separate terminal)
gcloud run services proxy knowledge-base-mcp --region us-central1 --port=8082

# Add MCP server
claude mcp add knowledge-base --transport http http://localhost:8082/mcp
```

**Gemini CLI:**
Add to `~/.gemini/settings.json`:
```json
{"mcpServers": {"knowledge-base": {"url": "http://localhost:8082/mcp"}}}
```

## File Structure

```
knowledge-base-mcp/
├── server.py              # FastMCP entry point (streamable-http)
├── firestore_client.py    # Firestore data access + vector search
├── embeddings.py          # Vertex AI text-embedding-004 wrapper
├── tools/
│   ├── search.py          # search_knowledge + expand_context
│   ├── ingest.py          # ingest_session + ingest_all_sessions
│   └── stats.py           # get_stats
├── pipeline/
│   ├── models.py          # Pydantic models
│   ├── parser.py          # Streaming JSONL parser
│   ├── chunker.py         # Topic segmentation (heuristic)
│   ├── extractor.py       # LLM extraction (Gemini Flash)
│   ├── loader.py          # Firestore batch writer + embeddings
│   └── run.py             # CLI entry point
├── pyproject.toml
├── Dockerfile
├── deploy.sh
└── .env.example
```
