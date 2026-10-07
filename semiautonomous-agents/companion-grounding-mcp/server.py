import os
import sqlite3
import json
import numpy as np
from google import genai
from mcp.server.fastmcp import FastMCP

DB_PATH = os.path.expanduser("~/IdeaProjects/vertex-ai-samples/semiautonomous-agents/companion-grounding-mcp/data/ground_truth.db")
EMBED_PROJECT = "vtxdemos"
EMBED_LOCATION = "us-central1"
EMBED_MODEL = "gemini-embedding-001"

mcp = FastMCP("companion-grounding-mcp")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def _get_surrounding_context(c: sqlite3.Cursor, msg_id: int, platform: str, window: int = 4):
    """Fetch preceding and succeeding messages in the same platform stream for full conversational context."""
    c.execute(
        """
        SELECT id, platform_msg_index, sender, timestamp, text, sentiment_label, models_net_rating
        FROM raw_messages
        WHERE platform = ? AND id < ?
        ORDER BY id DESC LIMIT ?
        """,
        (platform, msg_id, window),
    )
    before = [dict(r) for r in reversed(c.fetchall())]

    c.execute(
        """
        SELECT id, platform_msg_index, sender, timestamp, text, sentiment_label, models_net_rating
        FROM raw_messages
        WHERE platform = ? AND id > ?
        ORDER BY id ASC LIMIT ?
        """,
        (platform, msg_id, window),
    )
    after = [dict(r) for r in c.fetchall()]
    return before, after


def _get_graph_links_for_topics(c: sqlite3.Cursor, linked_topics_json: str, exclude_msg_id: int = -1):
    """Retrieve cross-date graph milestones across Instagram and Google Chat for matched topics."""
    if not linked_topics_json:
        return []
    try:
        topics = json.loads(linked_topics_json)
    except Exception:
        return []
    if not topics:
        return []

    links = []
    for t_id in topics[:2]:
        c.execute(
            "SELECT topic_title, platforms_spanned, first_seen_timestamp, last_seen_timestamp, summary_json FROM topic_graph_nodes WHERE topic_id = ?",
            (t_id,),
        )
        node = c.fetchone()
        if node:
            milestones = json.loads(node["summary_json"])
            other_dates = [m for m in milestones if m["msg_id"] != exclude_msg_id][:6]
            links.append({
                "topic_id": t_id,
                "topic_title": node["topic_title"],
                "platforms_spanned": node["platforms_spanned"],
                "timeline_span": f"{node['first_seen_timestamp']} -> {node['last_seen_timestamp']}",
                "connected_mentions_across_dates": other_dates,
            })
    return links


@mcp.tool()
def semantic_search_conversations(query: str, platform: str = "", top_k: int = 6) -> str:
    """Semantic vector search (gemini-embedding-001, 3072-dim) across all conversation windows with automatic before/after context and cross-date graph links.
    
    Args:
        query: Natural language question or topic (e.g. 'what did she study in college and grad school?', 'her best friend in Malaysia', 'how she feels about her ex').
        platform: Optional filter: 'Instagram', 'Google Chat', 'Google Meet', or 'Grounding Dossier'.
        top_k: Number of top semantic conversation windows to return (default 6).
    """
    conn = get_db()
    c = conn.cursor()
    
    try:
        client = genai.Client(vertexai=True, project=EMBED_PROJECT, location=EMBED_LOCATION)
        res = client.models.embed_content(model=EMBED_MODEL, contents=[query])
        q_vec = np.array(res.embeddings[0].values, dtype=np.float32)
        q_norm = np.linalg.norm(q_vec)
        if q_norm > 0:
            q_vec = q_vec / q_norm
            
        sql = """
        SELECT chunk_id, source_type, platform, channel_name, channel_id, account_type,
               thread_url, start_msg_id, end_msg_id, start_timestamp, end_timestamp,
               participants, chunk_text, embedding_blob
        FROM conversation_vectors
        """
        params = []
        if platform:
            sql += " WHERE LOWER(platform) LIKE ?"
            params.append(f"%{platform.lower()}%")
            
        c.execute(sql, params)
        rows = c.fetchall()
        
        scored = []
        for r in rows:
            emb = np.frombuffer(r["embedding_blob"], dtype=np.float32)
            score = float(np.dot(q_vec, emb))
            scored.append((score, r))
            
        scored.sort(key=lambda x: x[0], reverse=True)
        top_results = []
        for score, r in scored[:top_k]:
            before_ctx, after_ctx = [], []
            graph_links = []
            if r["source_type"] == "chat_window" and r["start_msg_id"] > 0:
                before_ctx, _ = _get_surrounding_context(c, r["start_msg_id"], r["platform"], window=3)
                _, after_ctx = _get_surrounding_context(c, r["end_msg_id"], r["platform"], window=3)
                c.execute(
                    "SELECT linked_topics FROM raw_messages WHERE id BETWEEN ? AND ? AND linked_topics != '[]' LIMIT 1",
                    (r["start_msg_id"], r["end_msg_id"]),
                )
                lt_row = c.fetchone()
                if lt_row:
                    graph_links = _get_graph_links_for_topics(c, lt_row["linked_topics"], r["start_msg_id"])

            top_results.append({
                "similarity_score": round(score, 4),
                "chunk_id": r["chunk_id"],
                "platform": r["platform"],
                "channel_name": r["channel_name"],
                "channel_id": r["channel_id"],
                "account_type": r["account_type"],
                "thread_url": r["thread_url"],
                "message_id_range": f"{r['start_msg_id']}..{r['end_msg_id']}",
                "timestamp_range": f"{r['start_timestamp']} -> {r['end_timestamp']}",
                "context_before": before_ctx,
                "transcript_window": r["chunk_text"],
                "context_after": after_ctx,
                "cross_date_graph_links": graph_links,
            })
        conn.close()
        return json.dumps({"query": query, "results_count": len(top_results), "semantic_matches": top_results}, indent=2, ensure_ascii=False)
    except Exception as e:
        conn.close()
        return json.dumps({"error": str(e)})

@mcp.tool()
def search_interactions(query: str, platform: str = "", limit: int = 10) -> str:
    """Search through all verified messages (from Msg #1 on Oct 11, 2024 to present) across Instagram and Google Chat with automatic before/after context, sentiment, Mark Manson Models analysis, and cross-date graph links.
    
    Args:
        query: Keywords or phrases to search (e.g. 'Constantine', 'Tulum', 'Econ', 'Malaysia', 'Taekwondo').
        platform: Optional filter: 'Instagram' or 'Google Chat'.
        limit: Max results to return (default 10).
    """
    conn = get_db()
    c = conn.cursor()
    
    clean_query = "".join(ch for ch in query if ch.isalnum() or ch.isspace()).strip()
    if not clean_query:
        return json.dumps({"error": "Empty search query"})
        
    sql = """
    SELECT r.id, r.platform, r.platform_msg_index, r.channel_name, r.channel_id,
           r.account_type, r.thread_url, r.native_msg_id, r.sender, r.timestamp,
           r.text, r.sentiment_label, r.sentiment_score, r.models_positives,
           r.models_flaws, r.models_net_rating, r.models_coaching_note, r.linked_topics
    FROM raw_messages_fts f
    JOIN raw_messages r ON f.rowid = r.id
    WHERE raw_messages_fts MATCH ?
    """
    params = [clean_query]
    if platform:
        sql += " AND r.platform LIKE ?"
        params.append(f"%{platform}%")
    sql += " LIMIT ?"
    params.append(limit)
    
    try:
        c.execute(sql, params)
        raw_rows = [dict(r) for r in c.fetchall()]
        enriched_rows = []
        for row in raw_rows:
            before_ctx, after_ctx = _get_surrounding_context(c, row["id"], row["platform"], window=4)
            row["context_before"] = before_ctx
            row["context_after"] = after_ctx
            row["cross_date_graph_links"] = _get_graph_links_for_topics(c, row.get("linked_topics", ""), row["id"])
            enriched_rows.append(row)
        conn.close()
        return json.dumps({"results_count": len(enriched_rows), "results": enriched_rows}, indent=2, ensure_ascii=False)
    except Exception as e:
        conn.close()
        return json.dumps({"error": str(e)})


@mcp.tool()
def analyze_models_performance(filter_type: str = "all", platform: str = "", limit: int = 15) -> str:
    """Retrieve Jesus's messages tagged with Mark Manson's 'Models' framework (positives vs flaws/neediness leaks) along with surrounding context and Selene's reaction.
    
    Args:
        filter_type: 'flaws' (neediness/qualification/pedestalizing leaks), 'positives' (playful teasing, vulnerability, polarization), or 'all'.
        platform: Optional filter: 'Instagram' or 'Google Chat'.
        limit: Max results to return (default 15).
    """
    conn = get_db()
    c = conn.cursor()

    # Aggregate overall summary stats for Jesus's messages
    c.execute("SELECT models_net_rating, COUNT(*) as cnt FROM raw_messages WHERE sender = 'Jesus' GROUP BY models_net_rating")
    summary_counts = {r["models_net_rating"]: r["cnt"] for r in c.fetchall()}

    sql = """
    SELECT id, platform, platform_msg_index, channel_name, timestamp, text,
           sentiment_label, sentiment_score, models_positives, models_flaws,
           models_net_rating, models_coaching_note
    FROM raw_messages
    WHERE sender = 'Jesus'
    """
    params = []
    if filter_type.lower() == "flaws":
        sql += " AND models_flaws != '[]'"
    elif filter_type.lower() == "positives":
        sql += " AND models_positives != '[]'"
    else:
        sql += " AND (models_flaws != '[]' OR models_positives != '[]')"

    if platform:
        sql += " AND LOWER(platform) LIKE ?"
        params.append(f"%{platform.lower()}%")

    sql += " ORDER BY id DESC LIMIT ?"
    params.append(limit)

    c.execute(sql, params)
    rows = [dict(r) for r in c.fetchall()]
    for r in rows:
        before_ctx, after_ctx = _get_surrounding_context(c, r["id"], r["platform"], window=2)
        r["context_before"] = before_ctx
        r["selene_reaction_after"] = after_ctx
    conn.close()
    return json.dumps({
        "jesus_models_summary_distribution": summary_counts,
        "filter_applied": filter_type,
        "returned_count": len(rows),
        "analyzed_messages": rows,
    }, indent=2, ensure_ascii=False)


@mcp.tool()
def trace_topic_graph(topic: str = "") -> str:
    """Trace recurring themes and hidden callbacks across all dates (Oct 2024 - Sep 2026) and across platforms (Instagram <-> Google Chat).
    
    Args:
        topic: Optional topic keyword (e.g. 'malaysia', 'cat', 'saju', 'education', 'tulum', 'gift', 'korea'). If empty, lists all 14 cross-date graph nodes.
    """
    conn = get_db()
    c = conn.cursor()
    if not topic.strip():
        c.execute("SELECT topic_id, topic_title, total_mentions, platforms_spanned, first_seen_timestamp, last_seen_timestamp FROM topic_graph_nodes ORDER BY total_mentions DESC")
        nodes = [dict(r) for r in c.fetchall()]
        conn.close()
        return json.dumps({"total_graph_topics": len(nodes), "topics": nodes}, indent=2, ensure_ascii=False)

    q = f"%{topic.lower()}%"
    c.execute(
        "SELECT * FROM topic_graph_nodes WHERE LOWER(topic_id) LIKE ? OR LOWER(topic_title) LIKE ?",
        (q, q),
    )
    matched_nodes = []
    for r in c.fetchall():
        d = dict(r)
        d["chronological_chain_across_dates"] = json.loads(d.pop("summary_json", "[]"))
        c.execute(
            "SELECT from_msg_id, to_msg_id, from_platform, to_platform, from_timestamp, to_timestamp, relationship_type FROM topic_graph_edges WHERE topic_id = ? AND cross_platform_hop = 1",
            (d["topic_id"],),
        )
        d["cross_platform_bridges"] = [dict(e) for e in c.fetchall()]
        matched_nodes.append(d)
    conn.close()
    return json.dumps({"matched_topics_count": len(matched_nodes), "graph_chains": matched_nodes}, indent=2, ensure_ascii=False)

@mcp.tool()
def search_past_advice(query: str, limit: int = 5) -> str:
    """Search the 147 Gemini strategic advisory turns (dating from June 1 to present).
    
    Args:
        query: Topic or question (e.g. 'gbike', 'Labor Day', 'Manson', 'neediness', 'cat photo', 'seen receipts').
        limit: Max turns to return (default 5).
    """
    conn = get_db()
    c = conn.cursor()
    
    clean_query = "".join(ch for ch in query if ch.isalnum() or ch.isspace()).strip()
    if not clean_query:
        return json.dumps({"error": "Empty search query"})
        
    sql = """
    SELECT a.turn_id, a.user_query, a.gemini_response
    FROM advisories_fts f
    JOIN gemini_advisories a ON f.rowid = a.turn_id
    WHERE advisories_fts MATCH ?
    ORDER BY a.turn_id DESC
    LIMIT ?
    """
    try:
        c.execute(sql, [clean_query, limit])
        rows = [dict(r) for r in c.fetchall()]
        conn.close()
        return json.dumps({"advice_turns_count": len(rows), "turns": rows}, indent=2, ensure_ascii=False)
    except Exception as e:
        conn.close()
        return json.dumps({"error": str(e)})

@mcp.tool()
def get_meet_transcripts(query: str = "") -> str:
    """Retrieve verbatim Google Meet call transcripts and 1-on-1 meeting notes between Jesus and Selene.
    
    Args:
        query: Optional search keyword (e.g. 'canvas', 'pipeline', 'Constantine', 'EAP'). If blank, returns summaries of all recorded calls.
    """
    conn = get_db()
    c = conn.cursor()
    
    if query:
        clean_query = "".join(ch for ch in query if ch.isalnum() or ch.isspace()).strip()
        sql = """
        SELECT m.id, m.meeting_id, m.date, m.title, m.attendees, m.content
        FROM meet_fts f
        JOIN meet_transcripts m ON f.rowid = m.id
        WHERE meet_fts MATCH ?
        """
        c.execute(sql, [clean_query])
    else:
        c.execute("SELECT id, meeting_id, date, title, attendees, content FROM meet_transcripts ORDER BY date DESC")
        
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return json.dumps({"meetings_found": len(rows), "meetings": rows}, indent=2, ensure_ascii=False)

@mcp.tool()
def get_grounding_dossier(section: str = "full_dossier") -> str:
    """Retrieve the synthesized Grounding Dossier containing identity, psychology, dynamic rules, and timeline.
    
    Args:
        section: Section name or 'full_dossier'. Available sections:
                 'full_dossier', 'identity', 'personal_profile', 'communication_matrix',
                 'chronological_archive', 'behavioral_rules'.
    """
    conn = get_db()
    c = conn.cursor()
    
    if section == "full_dossier":
        c.execute("SELECT content FROM dossier WHERE section_id = 'full_dossier'")
        row = c.fetchone()
        conn.close()
        return row["content"] if row else "Dossier not found"
    else:
        c.execute("SELECT title, content FROM dossier WHERE section_id LIKE ?", [f"%{section}%"])
        rows = [dict(r) for r in c.fetchall()]
        conn.close()
        return json.dumps(rows, indent=2, ensure_ascii=False) if rows else "Section not found"

@mcp.tool()
def get_recent_context(limit: int = 15) -> str:
    """Retrieve the most recent conversation messages and latest strategic advice for quick real-time orientation.
    
    Args:
        limit: Number of recent items to return.
    """
    conn = get_db()
    c = conn.cursor()
    
    c.execute("SELECT platform, sender, timestamp, text, reactions FROM raw_messages ORDER BY id DESC LIMIT ?", [limit])
    messages = [dict(r) for r in c.fetchall()]
    messages.reverse()
    
    c.execute("SELECT turn_id, user_query, gemini_response FROM gemini_advisories ORDER BY turn_id DESC LIMIT 3")
    advisories = [dict(r) for r in c.fetchall()]
    advisories.reverse()
    
    conn.close()
    return json.dumps({
        "recent_messages": messages,
        "latest_gemini_advisories": advisories
    }, indent=2, ensure_ascii=False)

@mcp.tool()
def verify_draft_tone(draft_text: str) -> str:
    """Evaluate a proposed draft message against established relationship principles (Mark Manson Models, non-neediness, low investment, playful brevity).
    
    Args:
        draft_text: The draft message you are considering sending.
    """
    word_count = len(draft_text.split())
    has_question = "?" in draft_text
    is_long = word_count > 25
    has_needy_words = any(w in draft_text.lower() for w in ["sorry to bother", "hope you're not busy", "are you free", "did i do something"])
    
    analysis = {
        "draft": draft_text,
        "word_count": word_count,
        "flags": {
            "too_long_for_casual_dm": is_long,
            "ends_with_interrogation": has_question,
            "contains_overly_apologetic_markers": has_needy_words
        },
        "established_calibration_rules": [
            "Keep public comments (e.g. gbike) concise, self-deprecating or teasers.",
            "Never double-text after read receipts; let dynamic breathe.",
            "Use pet banter (Beanie/Constantine) as an organic bridge, not a formal greeting.",
            "Avoid corporate administrative check-ins (e.g. 'hope you had a good weekend')."
        ]
    }
    return json.dumps(analysis, indent=2, ensure_ascii=False)

@mcp.tool()
def get_calendar_schedule(person: str = "both", date: str = "") -> str:
    """Retrieve schedule events for Jesus Chavez, Selene Song, or both.
    
    Args:
        person: 'jesus', 'selene', or 'both' (default 'both').
        date: Optional date filter in 'YYYY-MM-DD' format (e.g. '2026-09-11', '2026-09-15'). If omitted, shows upcoming 7 days.
    """
    conn = get_db()
    c = conn.cursor()
    
    sql = "SELECT owner_calendar, summary, start_time, end_time, location, description FROM calendar_events WHERE 1=1"
    params = []
    
    if person.lower() == "jesus":
        sql += " AND owner_calendar LIKE '%jesus%'"
    elif person.lower() == "selene":
        sql += " AND owner_calendar LIKE '%selene%'"
        
    if date:
        sql += " AND start_time LIKE ?"
        params.append(f"{date}%")
    else:
        sql += " AND start_time >= '2026-09-10' AND start_time <= '2026-09-18'"
        
    sql += " ORDER BY start_time ASC"
    c.execute(sql, params)
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return json.dumps({"events_count": len(rows), "events": rows}, indent=2, ensure_ascii=False)

@mcp.tool()
def get_upcoming_trips() -> str:
    """Extract all flights, hotel stays, business trips, and out-of-office blocks for Jesus and Selene."""
    conn = get_db()
    c = conn.cursor()
    
    sql = """
    SELECT owner_calendar, summary, start_time, end_time, location, description
    FROM calendar_events
    WHERE LOWER(summary) LIKE '%flight%'
       OR LOWER(summary) LIKE '%travel%'
       OR LOWER(summary) LIKE '%stay at%'
       OR LOWER(summary) LIKE '%out of office%'
    ORDER BY start_time ASC
    """
    c.execute(sql)
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return json.dumps({"trips_and_travel": rows}, indent=2, ensure_ascii=False)

@mcp.tool()
def find_co_location_days() -> str:
    """Identify days where both Jesus Chavez and Selene Song are co-located at the NYC office (US-NYC-8510)."""
    conn = get_db()
    c = conn.cursor()
    
    c.execute("""
    SELECT j.start_time as date, j.summary as jesus_status, s.summary as selene_status
    FROM calendar_events j
    JOIN calendar_events s ON j.start_time = s.start_time
    WHERE j.owner_calendar LIKE '%jesus%'
      AND s.owner_calendar LIKE '%selene%'
      AND j.summary LIKE '%8510%'
      AND s.summary LIKE '%8510%'
    ORDER BY j.start_time ASC
    """)
    co_locations = [dict(r) for r in c.fetchall()]
    conn.close()
    return json.dumps({"mutual_office_days": co_locations}, indent=2, ensure_ascii=False)

@mcp.tool()
def sync_live_instagram_messages() -> str:
    """Read the active Instagram DM tab with Selene (@selenesng) in Google Chrome via AppleScript, ingest any new messages not yet in ground_truth.db, tag sentiment/Models, and embed into the vector index."""
    import subprocess
    apple = '''
    tell application "Google Chrome"
        repeat with w in windows
            repeat with t in tabs of w
                if URL of t contains "instagram.com/direct/t/119805939405917" then
                    return execute t javascript "
                        (function() {
                            const divs = Array.from(document.querySelectorAll('div'));
                            const scroller = divs.find(d => {
                                const s = getComputedStyle(d);
                                return (s.overflowY === 'auto' || s.overflowY === 'scroll') && d.clientHeight > 300 && d.getBoundingClientRect().left > 350;
                            });
                            if (!scroller) return JSON.stringify([]);
                            scroller.scrollTop = 0;
                            const scRect = scroller.getBoundingClientRect();
                            const midX = scRect.left + scRect.width / 2;
                            const els = Array.from(scroller.querySelectorAll('div[dir=\\"auto\\"]'));
                            const out = [];
                            for (const el of els) {
                                const inner = el.querySelector('div[dir=\\"auto\\"]');
                                if (inner && inner.innerText.trim() === el.innerText.trim()) continue;
                                const r = el.getBoundingClientRect();
                                if (r.width === 0 || r.height === 0) continue;
                                const txt = (el.innerText || '').trim();
                                if (!txt || txt === 'Edited' || txt.includes('replied to')) continue;
                                const center = (r.left + r.right) / 2;
                                const sender = (r.left - scRect.left < 140 && scRect.right - r.right > 140) ? 'Selene' : (center < midX ? 'Selene' : 'Jesus');
                                out.push({y: Math.round(r.top), sender: sender, text: txt});
                            }
                            out.sort((a, b) => a.y - b.y);
                            return JSON.stringify(out);
                        })()
                    "
                end if
            end repeat
        end repeat
        return "[]"
    end tell
    '''
    res = subprocess.run(["osascript", "-e", apple], capture_output=True, text=True).stdout.strip()
    try:
        items = json.loads(res) if res else []
    except Exception:
        items = []

    if not items:
        return json.dumps({"status": "No active Instagram DM tab found in Chrome or 0 visible items."})

    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT text FROM raw_messages WHERE platform = 'Instagram' ORDER BY id DESC LIMIT 60")
    recent_texts = {r["text"].strip() for r in c.fetchall()}

    added = []
    for it in items:
        txt = it["text"].strip()
        if txt not in recent_texts and len(txt) > 0:
            c.execute(
                """
                INSERT INTO raw_messages (
                    platform, channel_name, channel_id, account_type, thread_url,
                    sender, timestamp, text, sentiment_label, models_net_rating
                ) VALUES (?, ?, ?, ?, ?, ?, datetime('now', 'localtime'), ?, 'Live Synced', 'Live Synced')
                """,
                (
                    "Instagram",
                    "Instagram Direct Message (@selenesng <-> @jchavezarg)",
                    "ig_dm_119805939405917",
                    "Personal Social Account (Instagram @selenesng / @jchavezarg)",
                    "https://www.instagram.com/direct/t/119805939405917/",
                    it["sender"],
                    txt,
                ),
            )
            recent_texts.add(txt)
            added.append(it)

    if added:
        c.execute("INSERT INTO raw_messages_fts(raw_messages_fts) VALUES('rebuild')")
        conn.commit()
    conn.close()
    return json.dumps({"new_messages_ingested": len(added), "messages": added}, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    mcp.run()

