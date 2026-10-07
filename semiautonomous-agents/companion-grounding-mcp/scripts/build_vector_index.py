import os
import json
import sqlite3
import time
import numpy as np
from google import genai

DB_PATH = os.path.expanduser(
    "~/IdeaProjects/vertex-ai-samples/semiautonomous-agents/companion-grounding-mcp/data/ground_truth.db"
)
PROJECT_ID = "vtxdemos"
LOCATION = "us-central1"
EMBEDDING_MODEL = "gemini-embedding-001"


def enrich_raw_messages_metadata(conn: sqlite3.Connection):
    """Add explicit channel, thread, and account metadata columns to raw_messages."""
    c = conn.cursor()
    existing_cols = {r[1] for r in c.execute("PRAGMA table_info(raw_messages)").fetchall()}

    new_cols = {
        "channel_name": "TEXT",
        "channel_id": "TEXT",
        "account_type": "TEXT",
        "thread_url": "TEXT",
        "native_msg_id": "TEXT",
    }
    for col, dtype in new_cols.items():
        if col not in existing_cols:
            c.execute(f"ALTER TABLE raw_messages ADD COLUMN {col} {dtype}")

    # Normalize sender names ("You" / "Jesus Chavez" -> "Jesus", "Selene Song" / "selenesng" -> "Selene")
    c.execute(
        "UPDATE raw_messages SET sender = 'Jesus' WHERE LOWER(sender) IN ('you', 'jesus chavez', 'jchavezarg', 'jesus')"
    )
    c.execute(
        "UPDATE raw_messages SET sender = 'Selene' WHERE LOWER(sender) IN ('selene song', 'selenesng', 'selene')"
    )

    # Enrich Instagram rows
    c.execute(
        """
        UPDATE raw_messages
        SET channel_name = 'Instagram Direct Message (@selenesng <-> @jchavezarg)',
            channel_id = 'ig_dm_119805939405917',
            account_type = 'Personal Social Account (Instagram @selenesng / @jchavezarg)',
            thread_url = 'https://www.instagram.com/direct/t/119805939405917/',
            native_msg_id = 'ig_msg_' || id
        WHERE platform = 'Instagram'
        """
    )

    # Enrich Google Chat rows
    c.execute(
        """
        UPDATE raw_messages
        SET channel_name = 'Google Chat 1:1 DM (selenesong@google.com <-> jesusarguelles@google.com | spaces/jeWaL0AAAAE)',
            channel_id = 'spaces/jeWaL0AAAAE',
            account_type = 'Corporate Google Workspace (selenesong@google.com / jesusarguelles@google.com)',
            thread_url = 'https://chat.google.com/dm/jeWaL0AAAAE'
        WHERE platform = 'Google Chat'
        """
    )

    # Extract native Google Chat message ID if stored in raw_json
    c.execute("SELECT id, raw_json FROM raw_messages WHERE platform = 'Google Chat'")
    for row_id, raw_json_str in c.fetchall():
        native_id = f"gchat_msg_{row_id}"
        if raw_json_str:
            try:
                j = json.loads(raw_json_str)
                if isinstance(j, dict) and "name" in j:
                    native_id = j["name"]
            except Exception:
                pass
        c.execute("UPDATE raw_messages SET native_msg_id = ? WHERE id = ?", (native_id, row_id))

    # Rebuild FTS5 index
    c.execute("INSERT INTO raw_messages_fts(raw_messages_fts) VALUES('rebuild')")
    conn.commit()
    print("Enriched all raw_messages with platform, channel_name, channel_id, account_type, thread_url, and native_msg_id.")


def build_chunks(conn: sqlite3.Connection):
    """Build overlapping conversational windows across Instagram, Google Chat, Google Meet, and Dossier."""
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS conversation_vectors (
            chunk_id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_type TEXT,
            platform TEXT,
            channel_name TEXT,
            channel_id TEXT,
            account_type TEXT,
            thread_url TEXT,
            start_msg_id INTEGER,
            end_msg_id INTEGER,
            start_timestamp TEXT,
            end_timestamp TEXT,
            participants TEXT,
            chunk_text TEXT,
            embedding_blob BLOB
        )
        """
    )
    c.execute("DELETE FROM conversation_vectors")
    conn.commit()

    chunks = []

    # 1. Chunk raw_messages per platform (sliding window of 8 messages, stride of 4)
    for platform in ["Google Chat", "Instagram"]:
        c.execute(
            """
            SELECT id, platform, channel_name, channel_id, account_type, thread_url, sender, timestamp, text, reactions, media_desc
            FROM raw_messages
            WHERE platform = ?
            ORDER BY id ASC
            """,
            (platform,),
        )
        rows = c.fetchall()
        window_size = 8
        stride = 4
        for i in range(0, len(rows), stride):
            window = rows[i : i + window_size]
            if not window:
                break
            first = window[0]
            last = window[-1]
            lines = [
                f"[Platform: {first[1]} | Channel: {first[2]} | Account: {first[4]} | Space/Thread ID: {first[3]}]"
            ]
            for r in window:
                msg_id, plat, ch_name, ch_id, acc_type, url, sender, ts, txt, react, media = r
                ts_label = f" ({ts})" if ts else ""
                extra = []
                if react and react not in ("[]", ""):
                    extra.append(f"reactions={react}")
                if media:
                    extra.append(f"media={media}")
                extra_str = f" [{' | '.join(extra)}]" if extra else ""
                lines.append(f"[{msg_id}]{ts_label} {sender}: {txt}{extra_str}")

            chunk_text = "\n".join(lines)
            chunks.append(
                {
                    "source_type": "chat_window",
                    "platform": first[1],
                    "channel_name": first[2],
                    "channel_id": first[3],
                    "account_type": first[4],
                    "thread_url": first[5],
                    "start_msg_id": first[0],
                    "end_msg_id": last[0],
                    "start_timestamp": first[7] or "",
                    "end_timestamp": last[7] or "",
                    "participants": "Jesus Chavez, Selene Song",
                    "chunk_text": chunk_text,
                }
            )

    # 2. Add Google Meet transcripts chunks
    c.execute("SELECT id, meeting_id, date, title, attendees, content FROM meet_transcripts")
    for m_id, meet_code, m_date, title, attendees, content in c.fetchall():
        paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
        # Group every 4 paragraphs
        for i in range(0, max(1, len(paragraphs)), 3):
            group = "\n\n".join(paragraphs[i : i + 4])
            header = f"[Platform: Google Meet Video Call | Meeting Title: {title} | Meeting ID: {meet_code} | Date: {m_date} | Account: Corporate Google Workspace]"
            chunks.append(
                {
                    "source_type": "google_meet",
                    "platform": "Google Meet",
                    "channel_name": f"Google Meet Call: {title} ({meet_code})",
                    "channel_id": meet_code,
                    "account_type": "Corporate Google Workspace (Google Meet)",
                    "thread_url": f"https://meet.google.com/{meet_code}",
                    "start_msg_id": m_id,
                    "end_msg_id": m_id,
                    "start_timestamp": m_date,
                    "end_timestamp": m_date,
                    "participants": attendees,
                    "chunk_text": f"{header}\n{group}",
                }
            )

    # 3. Add Master Dossier sections
    c.execute("SELECT section_id, title, content FROM dossier WHERE section_id != 'full_dossier'")
    for sec_id, title, content in c.fetchall():
        header = f"[Platform: Grounding Dossier | Section: {title} ({sec_id})]"
        chunks.append(
            {
                "source_type": "dossier",
                "platform": "Grounding Dossier",
                "channel_name": f"Master Grounding Dossier — {title}",
                "channel_id": sec_id,
                "account_type": "Synthesized Ground Truth Dossier",
                "thread_url": "",
                "start_msg_id": 0,
                "end_msg_id": 0,
                "start_timestamp": "2024-04-23",
                "end_timestamp": "2026-09-22",
                "participants": "Jesus Chavez, Selene Song",
                "chunk_text": f"{header}\n{content}",
            }
        )

    print(f"Prepared {len(chunks)} semantic chunks across Instagram, Google Chat, Google Meet, and Dossier.")
    return chunks


def embed_and_store(conn: sqlite3.Connection, chunks: list):
    client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)
    c = conn.cursor()

    batch_size = 50
    total = len(chunks)
    for start in range(0, total, batch_size):
        batch = chunks[start : start + batch_size]
        texts = [item["chunk_text"] for item in batch]
        res = client.models.embed_content(model=EMBEDDING_MODEL, contents=texts)
        for item, emb_obj in zip(batch, res.embeddings):
            vec = np.array(emb_obj.values, dtype=np.float32)
            # L2-normalize vector for fast dot-product cosine similarity
            norm = np.linalg.norm(vec)
            if norm > 0:
                vec = vec / norm
            c.execute(
                """
                INSERT INTO conversation_vectors (
                    source_type, platform, channel_name, channel_id, account_type,
                    thread_url, start_msg_id, end_msg_id, start_timestamp, end_timestamp,
                    participants, chunk_text, embedding_blob
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    item["source_type"],
                    item["platform"],
                    item["channel_name"],
                    item["channel_id"],
                    item["account_type"],
                    item["thread_url"],
                    item["start_msg_id"],
                    item["end_msg_id"],
                    item["start_timestamp"],
                    item["end_timestamp"],
                    item["participants"],
                    item["chunk_text"],
                    vec.tobytes(),
                ),
            )
        conn.commit()
        print(f"Embedded and indexed {min(start + batch_size, total)}/{total} chunks...")
        time.sleep(0.2)


if __name__ == "__main__":
    conn = sqlite3.connect(DB_PATH)
    enrich_raw_messages_metadata(conn)
    chunks = build_chunks(conn)
    embed_and_store(conn, chunks)
    conn.close()
    print("Vector index build complete!")
