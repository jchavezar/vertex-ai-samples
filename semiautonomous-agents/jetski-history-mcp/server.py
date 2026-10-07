#!/usr/bin/env python3
"""
Jetski Chat History MCP Server
Provides instant semantic + keyword hybrid search, session capsule extraction,
and deep transcript inspection across all Jetski chat histories.
"""

import os
import sys
import json
import sqlite3
import numpy as np
from typing import List, Dict, Any, Optional

from mcp.server.fastmcp import FastMCP
from google import genai

# Import indexing logic
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from indexer import index_all, DB_PATH, BRAIN_DIR, EMBED_PROJECT, EMBED_LOCATION, EMBED_MODEL

# Initialize FastMCP Server
mcp = FastMCP("jetski-history-mcp")


def get_db():
    if not os.path.exists(DB_PATH):
        # Auto-initialize if database does not exist yet
        index_all(force_refresh=False)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@mcp.tool()
def search_chat_history(query: str, top_k: int = 5) -> str:
    """
    Superfast hybrid (semantic vector + BM25 keyword) search across all past Jetski conversations.
    Finds sessions by conceptual meaning, past topics, tools used, or specific error messages.

    Args:
        query: Natural language query (e.g. 'restaurant order memory bank', 'sfdc oauth disallowed scopes', 'how we deployed world cup demo').
        top_k: Number of matching sessions to return (default: 5).
    """
    try:
        conn = get_db()
        c = conn.cursor()

        c.execute("""
        SELECT conversation_id, title, workspace_path, step_count, last_modified_time, primary_intent, embedding_blob
        FROM conversation_capsules
        """)
        rows = c.fetchall()
        if not rows:
            return "No conversations indexed yet. Call sync_chat_history() first."

        cids = [r["conversation_id"] for r in rows]
        meta_dict = {r["conversation_id"]: dict(r) for r in rows}

        vec_list = [np.frombuffer(r["embedding_blob"], dtype=np.float32) for r in rows]
        emb_matrix = np.vstack(vec_list)

        # Generate query vector
        client = genai.Client(vertexai=True, project=EMBED_PROJECT, location=EMBED_LOCATION)
        res = client.models.embed_content(model=EMBED_MODEL, contents=[query])
        q_vec = np.array(res.embeddings[0].values, dtype=np.float32)
        q_norm = np.linalg.norm(q_vec)
        if q_norm > 0:
            q_vec = q_vec / q_norm

        # Cosine ranking
        cos_scores = np.dot(emb_matrix, q_vec)
        vector_ranking = np.argsort(cos_scores)[::-1]
        vector_rank_map = {cids[idx]: (rank + 1, float(cos_scores[idx])) for rank, idx in enumerate(vector_ranking)}

        # FTS5 ranking
        fts_tokens = [w for w in query.replace('"', '').replace("'", '').split() if len(w) > 1]
        fts_query = " OR ".join(fts_tokens) if fts_tokens else query
        fts_rank_map = {}
        try:
            c.execute("""
            SELECT conversation_id, rank
            FROM conversation_fts
            WHERE conversation_fts MATCH ?
            ORDER BY rank
            LIMIT 50
            """, (fts_query,))
            for rank, f_row in enumerate(c.fetchall()):
                fts_rank_map[f_row["conversation_id"]] = (rank + 1, float(f_row["rank"]))
        except Exception:
            pass

        # RRF Fusion (60% dense vector, 40% lexical)
        rrf_k = 60.0
        combined = []
        for cid in cids:
            v_rank, v_sim = vector_rank_map.get(cid, (9999, 0.0))
            f_rank, _ = fts_rank_map.get(cid, (9999, 0.0))
            v_score = 1.0 / (rrf_k + v_rank) if v_rank <= len(cids) else 0.0
            f_score = 1.0 / (rrf_k + f_rank) if f_rank < 9999 else 0.0
            rrf = (0.6 * v_score) + (0.4 * f_score)
            combined.append((rrf, v_sim, cid in fts_rank_map, meta_dict[cid]))

        combined.sort(key=lambda x: x[0], reverse=True)
        conn.close()

        output_lines = [f"### 🔍 Found {min(top_k, len(combined))} Relevant Jetski Conversations for: '{query}'\n"]
        for rank, (rrf, v_sim, f_hit, m) in enumerate(combined[:top_k], 1):
            cid = m["conversation_id"]
            title = m["title"]
            last_mod = m["last_modified_time"]
            steps = m["step_count"]
            intent = m["primary_intent"][:220].replace("\n", " ")

            output_lines.append(f"**{rank}. [{title}](conversation://{cid})**")
            output_lines.append(f"- **ID**: `{cid}` | **Modified**: {last_mod} | **Steps**: {steps}")
            output_lines.append(f"- **Relevance**: Semantic {round(v_sim, 3)} | Keyword Match: {'Yes' if f_hit else 'No'} | RRF Score: {round(rrf, 5)}")
            output_lines.append(f"- **Initial Goal**: {intent}...")
            output_lines.append(f"- **Action**: Call `get_chat_capsule(conversation_id='{cid}')` to inject full context.\n")

        return "\n".join(output_lines)
    except Exception as e:
        return f"Error executing hybrid search: {str(e)}"


@mcp.tool()
def get_chat_capsule(conversation_id: str) -> str:
    """
    Instantly returns the dense executive session capsule (~800 tokens) for a conversation.
    Includes primary objectives, turn milestones, tools used, files touched, and final outcome.

    Args:
        conversation_id: The UUID of the conversation (e.g. '060bede8-982f-4ced-96a6-7441a2bff430').
    """
    try:
        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT capsule_markdown FROM conversation_capsules WHERE conversation_id = ?", (conversation_id,))
        row = c.fetchone()
        conn.close()
        if not row:
            return f"Conversation capsule not found for ID: {conversation_id}. Check ID or run sync_chat_history()."
        return row["capsule_markdown"]
    except Exception as e:
        return f"Error retrieving capsule: {str(e)}"


@mcp.tool()
def get_step_detail(conversation_id: str, step_indices: List[int]) -> str:
    """
    Extracts forensic details (exact user prompt, thinking, tool calls, and outputs)
    for specific step numbers from the session transcript.

    Args:
        conversation_id: The UUID of the conversation.
        step_indices: List of integer step indices (e.g. [0, 1, 15]).
    """
    tpath = os.path.join(BRAIN_DIR, conversation_id, ".system_generated", "logs", "transcript.jsonl")
    if not os.path.exists(tpath):
        tpath = os.path.join(BRAIN_DIR, conversation_id, "logs", "transcript.jsonl")
        if not os.path.exists(tpath):
            return f"Transcript file not found for conversation {conversation_id}."

    target_set = set(step_indices)
    extracted = []
    try:
        with open(tpath, "r", errors="ignore") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    d = json.loads(line)
                except Exception:
                    continue
                if d.get("step_index") in target_set:
                    extracted.append(d)
        return json.dumps(extracted, indent=2)
    except Exception as e:
        return f"Error reading transcript steps: {str(e)}"


@mcp.tool()
def sync_chat_history(force_refresh: bool = False) -> str:
    """
    Incrementally synchronizes the Jetski history index with all local session transcripts.
    Only processes newly created or updated sessions.

    Args:
        force_refresh: If True, re-indexes and re-embeds all conversations from scratch.
    """
    try:
        index_all(force_refresh=force_refresh)
        return "Jetski chat history index synchronization complete."
    except Exception as e:
        return f"Error during synchronization: {str(e)}"


@mcp.tool()
def list_recent_sessions(limit: int = 10) -> str:
    """
    Lists the most recently active Jetski conversations with titles, timestamps, and deep links.

    Args:
        limit: Number of recent conversations to list (default: 10).
    """
    try:
        conn = get_db()
        c = conn.cursor()
        c.execute("""
        SELECT conversation_id, title, workspace_path, step_count, last_modified_time
        FROM conversation_capsules
        ORDER BY last_modified_time DESC
        LIMIT ?
        """, (limit,))
        rows = [dict(r) for r in c.fetchall()]
        conn.close()

        lines = [f"### 🕒 Top {len(rows)} Most Recent Jetski Sessions\n"]
        for r in rows:
            cid = r["conversation_id"]
            title = r["title"]
            lines.append(f"- **[{title}](conversation://{cid})**")
            lines.append(f"  ID: `{cid}` | Modified: {r['last_modified_time']} | Steps: {r['step_count']}")
        return "\n".join(lines)
    except Exception as e:
        return f"Error listing recent sessions: {str(e)}"


@mcp.tool()
def get_history_landscape(filter_pillar: Optional[str] = None) -> str:
    """
    Returns the comprehensive macro-level thematic landscape of all 125+ Jetski chat histories.
    Groups conversations into 6 core pillars with session counts, key architectural topics, and native deep links.

    Args:
        filter_pillar: Optional filter by pillar name ('multi-agent', 'connectors', 'demos', 'personal', 'finance', 'diagnostics').
    """
    try:
        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT conversation_id, title, primary_intent, last_modified_time, step_count FROM conversation_capsules ORDER BY last_modified_time DESC")
        rows = [dict(r) for r in c.fetchall()]
        conn.close()

        pillars_def = [
            {
                "id": "multi-agent",
                "name": "1. Multi-Agent Systems & Universal Context",
                "desc": "Google ADK, A2A protocol orchestration, multi-runtime sessions, universal memory banks (:8010-:8013), and agent registries.",
                "keywords": ["agent", "adk", "a2a", "memory bank", "memorybank", "topology", "mesh", "runtime", "registry", "workflow", "orchestrat", "order", "session management"]
            },
            {
                "id": "connectors",
                "name": "2. Enterprise MCP & Cloud Connectors",
                "desc": "Salesforce (SFDC) OAuth connector, SharePoint WIF & StreamAssist, Google Workspace (Gmail/Drive/Docs), and ServiceNow integrations.",
                "keywords": ["mcp", "sfdc", "salesforce", "sharepoint", "workspace", "servicenow", "oauth", "wif", "streamassist", "connector", "outlook", "jira", "one-drive", "onedrive"]
            },
            {
                "id": "demos",
                "name": "3. Executive Demos & Client Showcases",
                "desc": "Weil Gotshal EBC legal showcase, FIFA World Cup 2026 Grounded Agent & Quiniela, Libertad Financiera modernization, and Motorola enterprise POC.",
                "keywords": ["weil", "worldcup", "world cup", "quiniela", "libertad", "motorola", "ebc", "showcase", "demo", "presentation", "partner"]
            },
            {
                "id": "finance",
                "name": "4. Data Analytics, RAG & Finance",
                "desc": "Tax-efficient stock liquidation (4% yield savings), BigQuery Conversational Agent (BQCA), Excel spreadsheet RAG, Alphabet 60-day catalysts, and spending audits.",
                "keywords": ["stock", "tax", "bigquery", "bqca", "spreadsheet", "excel", "alphabet", "rag", "revenue", "portfolio", "fund", "capital", "finance", "spending", "activity"]
            },
            {
                "id": "personal",
                "name": "5. Companion Grounding & Personal Context",
                "desc": "Selene Song supermemory (Instagram sync, Meet transcripts, Calendar co-location, Manson Models audit), Q4 MyGrad check-ins, and personal profile bio.",
                "keywords": ["selene", "instagram", "models", "mygrad", "boxing", "bio", "profile", "checkin", "check in", "meet", "trip", "travel", "calendar", "birthday"]
            },
            {
                "id": "diagnostics",
                "name": "6. System Engineering, UI/UX & Tooling",
                "desc": "Claude-Code shrinking ink animations, Vercel monochrome design systems, error remediation hub, latency probes, and terminal CLI benchmarks.",
                "keywords": ["ui/ux", "ink", "theme", "monochrome", "latency", "error", "debug", "benchmark", "terminal", "cli", "search", "index", "probe", "token", "cache", "icon", "incognito"]
            }
        ]

        buckets = {p["id"]: [] for p in pillars_def}
        uncategorized = []

        for r in rows:
            combined = f"{r['title']} {r['primary_intent']}".lower()
            matched = False
            for p in pillars_def:
                if any(k in combined for k in p["keywords"]):
                    buckets[p["id"]].append(r)
                    matched = True
                    break
            if not matched:
                uncategorized.append(r)

        output = ["# 🌐 Jetski Chat History Landscape (125+ Sessions Indexed)\n"]
        for p in pillars_def:
            if filter_pillar and filter_pillar.lower() not in p["id"] and filter_pillar.lower() not in p["name"].lower():
                continue
            items = buckets[p["id"]]
            output.append(f"## {p['name']} ({len(items)} Sessions)")
            output.append(f"*{p['desc']}*\n")
            output.append("**Representative Anchor Sessions:**")
            for item in items[:4]:
                output.append(f"- [{item['title']}](conversation://{item['conversation_id']}) — *{item['last_modified_time'][:10]} ({item['step_count']} steps)*")
            output.append("")

        if not filter_pillar and uncategorized:
            output.append(f"## 7. General Exploration & Miscellaneous ({len(uncategorized)} Sessions)")
            for item in uncategorized[:4]:
                t = item['title'] if item['title'] and item['title'] != 'Untitled Conversation' else item['primary_intent'][:40]
                output.append(f"- [{t}](conversation://{item['conversation_id']}) — *{item['last_modified_time'][:10]}*")
            output.append("")

        output.append("💡 *Tip: Call `get_chat_capsule(conversation_id)` on any session above to inject its complete context into this chat.*")
        return "\n".join(output)
    except Exception as e:
        return f"Error building history landscape: {str(e)}"


if __name__ == "__main__":
    # Start FastMCP standard I/O transport
    mcp.run(transport="stdio")
