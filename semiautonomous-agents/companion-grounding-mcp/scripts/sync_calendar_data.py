import os
import json
import sqlite3
import sys

DATA_DIR = os.path.expanduser("~/IdeaProjects/vertex-ai-samples/semiautonomous-agents/companion-grounding-mcp/data")
DB_PATH = os.path.join(DATA_DIR, "ground_truth.db")

def init_calendar_tables(conn):
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS calendar_events (
        event_id TEXT PRIMARY KEY,
        owner_calendar TEXT,
        summary TEXT,
        start_time TEXT,
        end_time TEXT,
        location TEXT,
        description TEXT,
        status TEXT,
        raw_json TEXT
    )
    """)

    c.execute("""
    CREATE VIRTUAL TABLE IF NOT EXISTS calendar_fts USING fts5(
        event_id,
        owner_calendar,
        summary,
        location,
        description
    )
    """)
    conn.commit()

def ingest_events(conn, events_list, owner_calendar):
    c = conn.cursor()
    inserted = 0
    updated = 0
    for e in events_list:
        event_id = e.get("id")
        if not event_id:
            continue
        summary = e.get("summary", "") or ""
        start = e.get("start", {}).get("dateTime") or e.get("start", {}).get("date") or ""
        end = e.get("end", {}).get("dateTime") or e.get("end", {}).get("date") or ""
        location = e.get("location", "") or ""
        description = e.get("description", "") or ""
        status = e.get("status", "confirmed") or ""
        raw_json = json.dumps(e, ensure_ascii=False)

        c.execute("SELECT event_id FROM calendar_events WHERE event_id = ?", (event_id,))
        row = c.fetchone()
        if row:
            c.execute("""
            UPDATE calendar_events
            SET owner_calendar = ?, summary = ?, start_time = ?, end_time = ?, location = ?, description = ?, status = ?, raw_json = ?
            WHERE event_id = ?
            """, (owner_calendar, summary, start, end, location, description, status, raw_json, event_id))
            updated += 1
        else:
            c.execute("""
            INSERT INTO calendar_events (event_id, owner_calendar, summary, start_time, end_time, location, description, status, raw_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (event_id, owner_calendar, summary, start, end, location, description, status, raw_json))
            inserted += 1

    # Rebuild FTS
    c.execute("DELETE FROM calendar_fts WHERE owner_calendar = ?", (owner_calendar,))
    c.execute("""
    INSERT INTO calendar_fts (event_id, owner_calendar, summary, location, description)
    SELECT event_id, owner_calendar, summary, location, description FROM calendar_events WHERE owner_calendar = ?
    """, (owner_calendar,))
    conn.commit()
    return inserted, updated

def sync_from_files(jesus_file, selene_file):
    conn = sqlite3.connect(DB_PATH)
    init_calendar_tables(conn)

    if os.path.exists(jesus_file):
        with open(jesus_file, "r", encoding="utf-8") as f:
            j_events = json.load(f)
        ins, upd = ingest_events(conn, j_events, "jesusarguelles@google.com")
        print(f"Jesus Calendar synced: {ins} new, {upd} updated ({len(j_events)} total)")
    else:
        print(f"File not found: {jesus_file}")

    if os.path.exists(selene_file):
        with open(selene_file, "r", encoding="utf-8") as f:
            s_events = json.load(f)
        ins, upd = ingest_events(conn, s_events, "selenesong@google.com")
        print(f"Selene Calendar synced: {ins} new, {upd} updated ({len(s_events)} total)")
    else:
        print(f"File not found: {selene_file}")

    conn.close()

if __name__ == "__main__":
    if len(sys.argv) >= 3:
        j_file = sys.argv[1]
        s_file = sys.argv[2]
    else:
        j_file = "/Users/jesusarguelles/.gemini/jetski/brain/5a619144-bf76-4065-9230-a82577c02dd6/.system_generated/steps/914/output.txt"
        s_file = "/Users/jesusarguelles/.gemini/jetski/brain/5a619144-bf76-4065-9230-a82577c02dd6/.system_generated/steps/912/output.txt"

    sync_from_files(j_file, s_file)
