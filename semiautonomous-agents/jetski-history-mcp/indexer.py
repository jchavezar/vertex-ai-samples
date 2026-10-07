#!/usr/bin/env python3
"""
Jetski Chat History Incremental Hybrid Indexer
Extracts high-density session capsules from Jetski brain transcripts and creates
a dual-engine (Semantic Vector + FTS5 Full Text) SQLite database for sub-10ms retrieval.
"""

import os
import sys
import json
import re
import glob
import sqlite3
import numpy as np
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

from google import genai

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "history_index.db")
JETSKI_DIR = os.path.expanduser("~/.gemini/jetski")
SUMMARIES_DB = os.path.join(JETSKI_DIR, "conversation_summaries.db")
BRAIN_DIR = os.path.join(JETSKI_DIR, "brain")

# Vertex AI Embedding Config
EMBED_PROJECT = os.environ.get("JETSKI_EMBED_PROJECT", "vtxdemos")
EMBED_LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
EMBED_MODEL = "text-embedding-005"
BATCH_SIZE = 20


def init_db(conn: sqlite3.Connection):
    """Initialize the SQLite tables for capsules, vectors, and FTS5."""
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS conversation_capsules (
        conversation_id TEXT PRIMARY KEY,
        title TEXT,
        workspace_path TEXT,
        step_count INTEGER,
        last_modified_time TEXT,
        primary_intent TEXT,
        capsule_markdown TEXT,
        embedding_blob BLOB,
        last_indexed_time TIMESTAMP
    )
    """)
    
    # FTS5 virtual table for lightning-fast keyword & token searches
    c.execute("""
    CREATE VIRTUAL TABLE IF NOT EXISTS conversation_fts USING fts5(
        conversation_id UNINDEXED,
        title,
        workspace_path,
        primary_intent,
        capsule_markdown,
        tokenize = 'unicode61 remove_diacritics 2'
    )
    """)
    conn.commit()


def clean_text(text: str) -> str:
    """Strip XML markup, system instructions, and redundant metadata from prompts."""
    if not text:
        return ""
    # Strip <USER_REQUEST>, <ADDITIONAL_METADATA>, etc.
    text = re.sub(r'</?USER_REQUEST>', '', text)
    text = re.sub(r'<ADDITIONAL_METADATA>.*?</ADDITIONAL_METADATA>', '', text, flags=re.DOTALL)
    text = re.sub(r'<SYSTEM_MESSAGE>.*?</SYSTEM_MESSAGE>', '', text, flags=re.DOTALL)
    text = re.sub(r'```.*?```', '[Code snippet]', text, flags=re.DOTALL)
    # Collapse multiple whitespaces
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def extract_capsule(cid: str, meta: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Parse transcript.jsonl and build a high-density executive capsule."""
    cpath = os.path.join(BRAIN_DIR, cid)
    tpath = os.path.join(cpath, ".system_generated", "logs", "transcript.jsonl")
    if not os.path.exists(tpath):
        # Fallback check
        tpath = os.path.join(cpath, "logs", "transcript.jsonl")
        if not os.path.exists(tpath):
            return None

    user_inputs: List[str] = []
    tools_used = set()
    files_touched = set()
    final_response = ""
    step_count = meta.get("step_count", 0)

    try:
        with open(tpath, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    d = json.loads(line)
                except Exception:
                    continue

                step_type = d.get("type")
                if step_type == "USER_INPUT":
                    raw_content = str(d.get("content", ""))
                    cleaned = clean_text(raw_content)
                    if cleaned and cleaned not in user_inputs:
                        user_inputs.append(cleaned)
                elif step_type == "PLANNER_RESPONSE":
                    for tc in d.get("tool_calls", []):
                        name = tc.get("name")
                        if name:
                            tools_used.add(name)
                        args = tc.get("args", {})
                        if isinstance(args, str):
                            try:
                                args = json.loads(args)
                            except Exception:
                                pass
                        if isinstance(args, dict):
                            tf = args.get("TargetFile") or args.get("AbsolutePath") or args.get("TargetDirectory")
                            if tf and isinstance(tf, str):
                                files_touched.add(os.path.basename(tf))
                    content = d.get("content")
                    if content and isinstance(content, str) and content.strip():
                        final_response = content.strip()
    except Exception as e:
        print(f"  [Warning] Error parsing {cid}: {e}", file=sys.stderr)
        return None

    # Discover any markdown artifacts generated in the brain directory
    artifacts = []
    for art in glob.glob(f"{cpath}/*.md"):
        artifacts.append(os.path.basename(art))

    title = meta.get("title") or "Untitled Conversation"
    workspace = meta.get("workspace_uris") or ""
    last_mod = meta.get("last_modified_time") or ""

    primary_intent = user_inputs[0] if user_inputs else meta.get("preview", "No initial prompt recorded.")
    
    # Format Key User Turns (up to 6 prominent turns)
    turns_md = ""
    if len(user_inputs) > 1:
        turns_list = [f"- **Turn {i+1}**: {clean_text(p)[:350]}" for i, p in enumerate(user_inputs[1:7])]
        turns_md = "\n".join(turns_list)
    else:
        turns_md = "- Single-turn interaction"

    # Preserve rich outcome summary (up to 4000 characters to provide full architectural answers)
    cleaned_final = clean_text(final_response)
    if len(cleaned_final) > 4000:
        cleaned_final = cleaned_final[:4000] + "\n...(summary continued in transcript)"

    tools_str = ", ".join(sorted(list(tools_used))[:8]) if tools_used else "None recorded"
    files_str = ", ".join(sorted(list(files_touched))[:10]) if files_touched else "None recorded"
    artifacts_str = ", ".join(artifacts[:6]) if artifacts else "None"

    capsule_markdown = f"""# Session: {title}
- **Conversation ID**: `{cid}`
- **Last Modified**: {last_mod} | **Steps**: {step_count}
- **Workspace**: `{workspace}`
- **Tools Invoked**: {tools_str}
- **Artifacts**: {artifacts_str}

### Primary Objective
{primary_intent[:500]}

### Key Milestones & Follow-ups
{turns_md}

### Files Touched
{files_str}

### Outcome Summary
{cleaned_final if cleaned_final else 'Session completed.'}
"""

    # Semantic text for embedding
    embed_text = f"Title: {title}\nWorkspace: {workspace}\nObjective: {primary_intent[:500]}\nTopics: {' | '.join([u[:200] for u in user_inputs[:6]])}\nSummary: {cleaned_final[:800]}"

    return {
        "conversation_id": cid,
        "title": title,
        "workspace_path": workspace,
        "step_count": step_count,
        "last_modified_time": last_mod,
        "primary_intent": primary_intent,
        "capsule_markdown": capsule_markdown.strip(),
        "embed_text": embed_text.strip()
    }


def get_existing_index_timestamps(conn: sqlite3.Connection) -> Dict[str, str]:
    """Retrieve last_modified_time for currently indexed sessions."""
    c = conn.cursor()
    c.execute("SELECT conversation_id, last_modified_time FROM conversation_capsules")
    return dict(c.fetchall())


def index_all(force_refresh: bool = False):
    """Main incremental indexing orchestrator."""
    os.makedirs(os.path.join(BASE_DIR, "data"), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    init_db(conn)

    # 1. Fetch metadata from Jetski's conversation_summaries.db
    if not os.path.exists(SUMMARIES_DB):
        print(f"Error: {SUMMARIES_DB} not found.", file=sys.stderr)
        return

    sum_conn = sqlite3.connect(SUMMARIES_DB)
    sum_conn.row_factory = sqlite3.Row
    sc = sum_conn.cursor()
    sc.execute("SELECT conversation_id, title, preview, step_count, last_modified_time, workspace_uris FROM conversation_summaries")
    all_sessions = [dict(r) for r in sc.fetchall()]
    sum_conn.close()

    existing_times = {} if force_refresh else get_existing_index_timestamps(conn)

    # 2. Identify sessions requiring new extraction & embedding
    to_process = []
    for s in all_sessions:
        cid = s["conversation_id"]
        last_mod = s.get("last_modified_time", "")
        if force_refresh or cid not in existing_times or existing_times.get(cid) != last_mod:
            capsule = extract_capsule(cid, s)
            if capsule:
                to_process.append(capsule)

    print(f"Found {len(all_sessions)} total sessions in Jetski.")
    print(f"Sessions requiring indexing/update: {len(to_process)}")

    if not to_process:
        print("Index is already completely up to date. (0 sessions to embed)")
        conn.close()
        return

    # 3. Batch generate embeddings using Vertex AI
    print(f"Initializing Vertex AI embedding client (model: {EMBED_MODEL}, project: {EMBED_PROJECT})...")
    client = genai.Client(vertexai=True, project=EMBED_PROJECT, location=EMBED_LOCATION)

    now_iso = datetime.now(timezone.utc).isoformat()
    cursor = conn.cursor()

    for i in range(0, len(to_process), BATCH_SIZE):
        batch = to_process[i:i + BATCH_SIZE]
        texts = [b["embed_text"] for b in batch]
        
        print(f"  Embedding batch {i // BATCH_SIZE + 1}/{(len(to_process) + BATCH_SIZE - 1) // BATCH_SIZE} ({len(batch)} items)...")
        try:
            res = client.models.embed_content(model=EMBED_MODEL, contents=texts)
            embeddings = res.embeddings
        except Exception as e:
            print(f"  [Error] Failed to embed batch: {e}", file=sys.stderr)
            continue

        for item, emb in zip(batch, embeddings):
            vec = np.array(emb.values, dtype=np.float32)
            norm = np.linalg.norm(vec)
            if norm > 0:
                vec = vec / norm
            blob = vec.tobytes()

            # Insert or replace in main capsule table
            cursor.execute("""
            INSERT OR REPLACE INTO conversation_capsules
            (conversation_id, title, workspace_path, step_count, last_modified_time, primary_intent, capsule_markdown, embedding_blob, last_indexed_time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                item["conversation_id"],
                item["title"],
                item["workspace_path"],
                item["step_count"],
                item["last_modified_time"],
                item["primary_intent"],
                item["capsule_markdown"],
                blob,
                now_iso
            ))

            # Update FTS5 table
            cursor.execute("DELETE FROM conversation_fts WHERE conversation_id = ?", (item["conversation_id"],))
            cursor.execute("""
            INSERT INTO conversation_fts (conversation_id, title, workspace_path, primary_intent, capsule_markdown)
            VALUES (?, ?, ?, ?, ?)
            """, (
                item["conversation_id"],
                item["title"],
                item["workspace_path"],
                item["primary_intent"],
                item["capsule_markdown"]
            ))

        conn.commit()

    conn.close()
    print("Indexing completed successfully!")


if __name__ == "__main__":
    force = "--force" in sys.argv or "-f" in sys.argv
    index_all(force_refresh=force)
