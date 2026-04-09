# Tools Reference

All 9 tools available in the Knowledge Base MCP Server.

---

## Search Tools (5 tools)

### `search_knowledge`
Semantic search for problem-solution patterns.
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | string | Yes | Natural language description |
| `top_k` | int | 3 | Results to return (max 10) |
| `service_filter` | string | "" | Filter by service (e.g., "Cloud Run") |

**Example:**
```
search_knowledge(query="WIF token exchange failing", top_k=5)
```

**Returns:**
- Problem description
- Error message (if any)
- Solution with confidence score
- Failed attempts (what not to try)
- Anti-patterns to avoid
- Expand hint for full context

---

### `search_playbooks`
Search for architecture decisions, design patterns, and recipes.
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | string | Yes | What you're looking for |
| `top_k` | int | 3 | Results (max 10) |
| `project_filter` | string | "" | Filter by project |
| `category_filter` | string | "" | Filter: architecture, pattern, idea, recipe |

**Example:**
```
search_playbooks(query="SharePoint connector setup", category_filter="recipe")
```

---

### `recent_knowledge`
Get most recent items by timestamp.
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | int | 5 | Results (max 20) |
| `service_filter` | string | "" | Filter by service |

**Example:**
```
recent_knowledge(limit=10)
```

---

### `get_topic_timeline`
**NEW** - Get chronological evolution of a topic across multiple sessions.

Unlike `search_knowledge` (ranked by relevance), this returns results sorted by timestamp (oldest first) to show how a topic evolved over time.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | string | Yes | Topic to trace |
| `top_k` | int | 10 | Results (max 20) |
| `service_filter` | string | "" | Filter by service |

**Example:**
```
get_topic_timeline(query="WIF provider configuration", top_k=10)
```

**Returns:**
- Entries sorted by timestamp (oldest first)
- Session ID for each entry
- Shows evolution across multiple conversations

**Use case:** Understanding how a configuration changed over time, what issues led to fixes.

---

### `expand_context`
Get surrounding conversation messages for a search result.
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `session_id` | string | Yes | From search result |
| `start_idx` | int | Yes | Start message index |
| `end_idx` | int | Yes | End message index |

**Example:**
```
expand_context(session_id="7dfa4d08-...", start_idx=4751, end_idx=4780)
```

---

## Ingestion Tools (2 tools)

### `ingest_session`
Ingest a single JSONL transcript.
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `jsonl_path` | string | Yes | Path or gs:// URI |
| `dry_run` | bool | false | Preview without writing |

**Supports:**
- Local paths: `/home/user/.claude/projects/.../session.jsonl`
- GCS paths: `gs://bucket/transcripts/session.jsonl`

**Deduplication:** Sessions already ingested are skipped automatically.

---

### `ingest_all_sessions`
Batch ingest all JSONLs in a directory.
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `sessions_dir` | string | Yes | Directory path |
| `dry_run` | bool | true | Preview (default true for safety) |

**Example:**
```
ingest_all_sessions(sessions_dir="/home/user/.claude/projects/myproject/", dry_run=False)
```

---

## Management Tools (2 tools)

### `delete_knowledge`
Delete entries matching a title query.
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `title_query` | string | Yes | Substring to match |
| `collection` | string | "" | "knowledge" or "playbooks" |

**Example:**
```
delete_knowledge(title_query="test entry", collection="playbooks")
```

---

### `get_stats`
Get knowledge base statistics.

**Returns:**
- Total knowledge items
- Total playbook items
- Total sessions ingested
- Average solution confidence
- Top services
- Model distribution
- Playbook category breakdown

**Example output:**
```
## Knowledge Base Statistics
- Total knowledge items: 482
- Total playbook items: 351
- Total sessions ingested: 53
- Average solution confidence: 0.927

### Playbook Categories:
  - architecture: 110 items
  - recipe: 98 items
  - idea: 92 items
  - pattern: 51 items
```
