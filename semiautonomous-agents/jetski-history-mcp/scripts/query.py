#!/usr/bin/env python3
"""
Jetski History Query CLI & Retreival Engine
Executes sub-10ms Hybrid (Dense Vector + FTS5 BM25 + RRF) search over all indexed Jetski sessions.
"""

import os
import sys
import json
import sqlite3
import argparse
import numpy as np
from typing import List, Dict, Any, Optional

from google import genai

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
DB_PATH = os.path.join(BASE_DIR, "data", "history_index.db")
JETSKI_DIR = os.path.expanduser("~/.gemini/jetski")
BRAIN_DIR = os.path.join(JETSKI_DIR, "brain")

EMBED_PROJECT = os.environ.get("JETSKI_EMBED_PROJECT", "vtxdemos")
EMBED_LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
EMBED_MODEL = "text-embedding-005"


def get_db():
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Database {DB_PATH} not found. Run indexer.py first.")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def hybrid_search(query: str, top_k: int = 5, vector_weight: float = 0.6) -> List[Dict[str, Any]]:
    """
    Executes a high-speed hybrid search combining:
    1. Dense Cosine Similarity (via NumPy in-memory dot product)
    2. BM25 Lexical Matching (via SQLite FTS5)
    3. Reciprocal Rank Fusion (RRF)
    """
    conn = get_db()
    c = conn.cursor()

    # 1. Fetch all vectors and metadata
    c.execute("""
    SELECT conversation_id, title, workspace_path, step_count, last_modified_time, primary_intent, embedding_blob
    FROM conversation_capsules
    """)
    rows = c.fetchall()
    if not rows:
        return []

    cids = [r["conversation_id"] for r in rows]
    meta_dict = {r["conversation_id"]: dict(r) for r in rows}

    # Stack embedding matrix
    vec_list = [np.frombuffer(r["embedding_blob"], dtype=np.float32) for r in rows]
    emb_matrix = np.vstack(vec_list)  # (N, D)

    # 2. Embed the query
    client = genai.Client(vertexai=True, project=EMBED_PROJECT, location=EMBED_LOCATION)
    res = client.models.embed_content(model=EMBED_MODEL, contents=[query])
    q_vec = np.array(res.embeddings[0].values, dtype=np.float32)
    q_norm = np.linalg.norm(q_vec)
    if q_norm > 0:
        q_vec = q_vec / q_norm

    # 3. Dense Cosine Scores (matrix dot product)
    cos_scores = np.dot(emb_matrix, q_vec)
    vector_ranking = np.argsort(cos_scores)[::-1]
    
    vector_rank_map = {}
    for rank, idx in enumerate(vector_ranking):
        vector_rank_map[cids[idx]] = (rank + 1, float(cos_scores[idx]))

    # 4. FTS5 Lexical Search
    # Clean query for FTS tokens (keep alphanumeric and words)
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
        fts_hits = c.fetchall()
        for rank, f_row in enumerate(fts_hits):
            fts_rank_map[f_row["conversation_id"]] = (rank + 1, float(f_row["rank"]))
    except Exception:
        # If query has invalid FTS syntax, fallback to empty
        pass

    # 5. Reciprocal Rank Fusion (RRF)
    # RRF score = sum( 1.0 / (k + rank) ) with k = 60
    rrf_k = 60.0
    combined_scores = []

    for cid in cids:
        v_rank, v_sim = vector_rank_map.get(cid, (9999, 0.0))
        f_rank, f_bm25 = fts_rank_map.get(cid, (9999, 0.0))

        v_score = 1.0 / (rrf_k + v_rank) if v_rank <= len(cids) else 0.0
        f_score = 1.0 / (rrf_k + f_rank) if f_rank < 9999 else 0.0

        final_rrf = (vector_weight * v_score) + ((1.0 - vector_weight) * f_score)
        
        combined_scores.append({
            "conversation_id": cid,
            "rrf_score": final_rrf,
            "cosine_similarity": round(v_sim, 4),
            "fts_match": cid in fts_rank_map,
            "meta": meta_dict[cid]
        })

    combined_scores.sort(key=lambda x: x["rrf_score"], reverse=True)
    conn.close()

    results = []
    for item in combined_scores[:top_k]:
        m = item["meta"]
        results.append({
            "conversation_id": item["conversation_id"],
            "title": m["title"],
            "workspace_path": m["workspace_path"],
            "step_count": m["step_count"],
            "last_modified_time": m["last_modified_time"],
            "primary_intent": m["primary_intent"],
            "cosine_similarity": item["cosine_similarity"],
            "fts_match": item["fts_match"],
            "rrf_score": round(item["rrf_score"], 6),
            "native_link": f"[{m['title']}](conversation://{item['conversation_id']})"
        })

    return results


def get_capsule(cid: str) -> Optional[str]:
    """Retrieve the full compiled markdown capsule for a session."""
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT capsule_markdown FROM conversation_capsules WHERE conversation_id = ?", (cid,))
    row = c.fetchone()
    conn.close()
    if row:
        return row["capsule_markdown"]
    return None


def get_step_details(cid: str, step_indices: List[int]) -> List[Dict[str, Any]]:
    """Retrieve exact detailed content and tool calls for specific steps."""
    tpath = os.path.join(BRAIN_DIR, cid, ".system_generated", "logs", "transcript.jsonl")
    if not os.path.exists(tpath):
        tpath = os.path.join(BRAIN_DIR, cid, "logs", "transcript.jsonl")
        if not os.path.exists(tpath):
            return []

    target_set = set(step_indices)
    extracted = []
    with open(tpath, "r", errors="ignore") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                d = json.loads(line)
            except Exception:
                continue
            idx = d.get("step_index")
            if idx in target_set:
                extracted.append(d)
    return extracted


def list_recent(limit: int = 10) -> List[Dict[str, Any]]:
    """List most recently modified conversations."""
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
    return rows


def main():
    parser = argparse.ArgumentParser(description="Jetski Chat History Hybrid Semantic Search")
    subparsers = parser.add_subparsers(dest="command", help="Sub-commands")

    # Search command
    sp = subparsers.add_parser("search", help="Hybrid semantic + keyword search")
    sp.add_argument("query", type=str, help="Search query or topic")
    sp.add_argument("-k", "--top-k", type=int, default=5, help="Number of results to return")

    # Capsule command
    cp = subparsers.add_parser("capsule", help="View full session capsule")
    cp.add_argument("cid", type=str, help="Conversation ID")

    # Recent command
    rp = subparsers.add_parser("recent", help="List recent sessions")
    rp.add_argument("limit", type=int, nargs="?", default=10, help="Number of items")

    # Landscape command
    lp = subparsers.add_parser("landscape", help="Macro thematic overview of all chat histories")
    lp.add_argument("pillar", type=str, nargs="?", default=None, help="Filter by pillar name")

    # Sync command
    sync_p = subparsers.add_parser("sync", help="Incrementally synchronize chat history index")
    sync_p.add_argument("-f", "--force", action="store_true", help="Force re-indexing all sessions")

    args = parser.parse_args()

    if args.command == "landscape":
        from server import get_history_landscape
        print(get_history_landscape(args.pillar))

    elif args.command == "search":
        hits = hybrid_search(args.query, top_k=args.top_k)
        print(f"\n🔍 Found {len(hits)} matching sessions for: '{args.query}'\n" + "=" * 70)
        for i, h in enumerate(hits, 1):
            print(f"[{i}] {h['title']}")
            print(f"    🔗 Jetski Link: {h['native_link']}")
            print(f"    🆔 CID: {h['conversation_id']} | 📅 Modified: {h['last_modified_time']} | 👣 Steps: {h['step_count']}")
            print(f"    📊 Similarity: {h['cosine_similarity']} | FTS Hit: {h['fts_match']} | RRF Score: {h['rrf_score']}")
            print(f"    🎯 Intent: {h['primary_intent'][:180]}...")
            print("-" * 70)

    elif args.command == "capsule":
        cap = get_capsule(args.cid)
        if cap:
            print(cap)
        else:
            print(f"No capsule found for conversation {args.cid}.")

    elif args.command == "recent":
        rec = list_recent(args.limit)
        print(f"\n🕒 Top {len(rec)} Most Recent Sessions:\n" + "=" * 70)
        for r in rec:
            print(f"• {r['title']}")
            print(f"  ID: {r['conversation_id']} | Date: {r['last_modified_time']} | Steps: {r['step_count']}")
            print(f"  Link: [{r['title']}](conversation://{r['conversation_id']})")

    elif args.command == "sync":
        from indexer import index_all
        index_all(force_refresh=args.force)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
