import os
import json
import sqlite3
import re

DATA_DIR = os.path.expanduser("~/IdeaProjects/vertex-ai-samples/semiautonomous-agents/companion-grounding-mcp/data")
DB_PATH = os.path.join(DATA_DIR, "ground_truth.db")
DESKTOP_DIR = os.path.expanduser("~/Desktop")

def init_db(conn, drop_existing=True):
    c = conn.cursor()
    
    if drop_existing:
        c.execute("DROP TABLE IF EXISTS raw_messages_fts")
        c.execute("DROP TABLE IF EXISTS advisories_fts")
        c.execute("DROP TABLE IF EXISTS meet_fts")
        c.execute("DROP TABLE IF EXISTS raw_messages")
        c.execute("DROP TABLE IF EXISTS gemini_advisories")
        c.execute("DROP TABLE IF EXISTS meet_transcripts")
        c.execute("DROP TABLE IF EXISTS dossier")

    # 1. Raw Messages (Instagram, Google Chat)
    c.execute("""
    CREATE TABLE IF NOT EXISTS raw_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        platform TEXT,
        sender TEXT,
        timestamp TEXT,
        text TEXT,
        reactions TEXT,
        media_desc TEXT,
        raw_json TEXT
    )
    """)
    
    # 2. Gemini Strategic Advisories (Turns from Chrome & Saju Notebook)
    c.execute("""
    CREATE TABLE IF NOT EXISTS gemini_advisories (
        turn_id INTEGER PRIMARY KEY,
        chat_source TEXT,
        user_query TEXT,
        gemini_response TEXT,
        user_char_count INTEGER,
        response_char_count INTEGER
    )
    """)
    
    # 3. Google Meet Transcripts & Notes
    c.execute("""
    CREATE TABLE IF NOT EXISTS meet_transcripts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        meeting_id TEXT,
        date TEXT,
        title TEXT,
        attendees TEXT,
        content TEXT
    )
    """)
    
    # 4. Master Grounding Dossier
    c.execute("""
    CREATE TABLE IF NOT EXISTS dossier (
        section_id TEXT PRIMARY KEY,
        title TEXT,
        content TEXT
    )
    """)
    
    # FTS5 Full Text Search Indexes
    c.execute("CREATE VIRTUAL TABLE IF NOT EXISTS raw_messages_fts USING fts5(platform, sender, text, reactions, media_desc, content='raw_messages', content_rowid='id')")
    c.execute("CREATE VIRTUAL TABLE IF NOT EXISTS advisories_fts USING fts5(user_query, gemini_response, content='gemini_advisories', content_rowid='turn_id')")
    c.execute("CREATE VIRTUAL TABLE IF NOT EXISTS meet_fts USING fts5(title, attendees, content, content='meet_transcripts', content_rowid='id')")
    
    conn.commit()

def ingest_instagram(conn):
    ig_paths = [
        os.path.join(DATA_DIR, "instagram_live_complete.json"),
        os.path.join(DESKTOP_DIR, "Selene_Instagram_Complete_Chat_History.json"),
        os.path.join(DESKTOP_DIR, "selene_chat_history.json")
    ]
    
    target_path = None
    for p in ig_paths:
        if os.path.exists(p):
            target_path = p
            break
            
    if not target_path:
        print("Instagram JSON file not found.")
        return 0
        
    with open(target_path, "r", encoding="utf-8") as f:
        items = json.load(f)
        
    c = conn.cursor()
    count = 0
    for item in items:
        sender = item.get("sender", "Unknown")
        text = item.get("text", "") or ""
        date = item.get("date", "") or ""
        reactions = json.dumps(item.get("reactions", [])) if "reactions" in item else ""
        media = item.get("media", "") or item.get("img", "") or ""
        media_str = json.dumps(media) if isinstance(media, (dict, list)) else str(media)
        
        c.execute("""
        INSERT INTO raw_messages (platform, sender, timestamp, text, reactions, media_desc, raw_json)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, ("Instagram", sender, date, text, reactions, media_str, json.dumps(item)))
        
        row_id = c.lastrowid
        c.execute("""
        INSERT INTO raw_messages_fts (rowid, platform, sender, text, reactions, media_desc)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (row_id, "Instagram", sender, text, reactions, media_str))
        count += 1
        
    conn.commit()
    print(f"Ingested {count} Instagram messages from {os.path.basename(target_path)}")
    return count

def ingest_google_chat(conn):
    chat_path = os.path.join(DESKTOP_DIR, "Selene_Complete_Master_Grounding_Archive.json")
    if not os.path.exists(chat_path):
        print(f"Master Archive not found at {chat_path}")
        return 0
        
    with open(chat_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    c = conn.cursor()
    count = 0
    
    messages = data.get("google_chat_messages", [])
    for m in messages:
        sender = m.get("sender", "Unknown")
        text = m.get("text", "") or ""
        date = m.get("date", "") or m.get("timestamp", "") or ""
        reactions = json.dumps(m.get("reactions", [])) if "reactions" in m else ""
        
        c.execute("""
        INSERT INTO raw_messages (platform, sender, timestamp, text, reactions, media_desc, raw_json)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, ("Google Chat", sender, date, text, reactions, "", json.dumps(m)))
        
        row_id = c.lastrowid
        c.execute("""
        INSERT INTO raw_messages_fts (rowid, platform, sender, text, reactions, media_desc)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (row_id, "Google Chat", sender, text, reactions, ""))
        count += 1
        
    conn.commit()
    print(f"Ingested {count} Google Chat messages from Master Archive.")
    return count

def ingest_meet_transcripts(conn):
    c = conn.cursor()
    count = 0
    
    # 1. August 26, 2026 Meet Transcript
    aug26_path = "/Users/jesusarguelles/.gemini/jetski/brain/5a619144-bf76-4065-9230-a82577c02dd6/.system_generated/steps/263/output.txt"
    if os.path.exists(aug26_path):
        with open(aug26_path, "r", encoding="utf-8") as f:
            t_aug26 = f.read()
        c.execute("""
        INSERT INTO meet_transcripts (meeting_id, date, title, attendees, content)
        VALUES (?, ?, ?, ?, ?)
        """, ("oue-drmk-nox", "2026-08-26", "oue-drmk-nox (Gemini Enterprise Canvas EAP)", "Jesus Chavez, Selene Song", t_aug26))
        row_id = c.lastrowid
        c.execute("INSERT INTO meet_fts (rowid, title, attendees, content) VALUES (?, ?, ?, ?)",
                  (row_id, "oue-drmk-nox (Gemini Enterprise Canvas EAP)", "Jesus Chavez, Selene Song", t_aug26))
        count += 1
        print("Ingested Google Meet Transcript: oue-drmk-nox (2026-08-26)")

    # 2. April 23, 2024 Meet Notes / Onboarding
    apr24_path = "/Users/jesusarguelles/.gemini/jetski/brain/5a619144-bf76-4065-9230-a82577c02dd6/.system_generated/steps/259/output.txt"
    if os.path.exists(apr24_path):
        with open(apr24_path, "r", encoding="utf-8") as f:
            t_apr24 = f.read()
        c.execute("""
        INSERT INTO meet_transcripts (meeting_id, date, title, attendees, content)
        VALUES (?, ?, ?, ?, ?)
        """, ("notes-jesus-selene", "2024-04-23", "Notes - Jesus / Selene (Vertex AI Pipelines & Onboarding)", "Jesus Chavez, Selene Song", t_apr24))
        row_id = c.lastrowid
        c.execute("INSERT INTO meet_fts (rowid, title, attendees, content) VALUES (?, ?, ?, ?)",
                  (row_id, "Notes - Jesus / Selene (Vertex AI Pipelines & Onboarding)", "Jesus Chavez, Selene Song", t_apr24))
        count += 1
        print("Ingested Google Meet Notes: Notes - Jesus / Selene (2024-04-23)")
        
    conn.commit()
    return count

def ingest_gemini_advisories(conn):
    gemini_path = os.path.join(DATA_DIR, "gemini_advisory_archive.json")
    if not os.path.exists(gemini_path):
        print(f"Gemini archive not found at {gemini_path}")
        return 0
        
    with open(gemini_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    c = conn.cursor()
    count = 0
    turns = data.get("turns", [])
    for t in turns:
        t_id = t["turn_id"]
        source = t.get("chat_source", "Chatting About Saju and Careers")
        q = t["user_query"]
        r = t["gemini_response"]
        u_len = t.get("user_char_count", len(q))
        r_len = t.get("response_char_count", len(r))
        
        c.execute("""
        INSERT OR REPLACE INTO gemini_advisories (turn_id, chat_source, user_query, gemini_response, user_char_count, response_char_count)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (t_id, source, q, r, u_len, r_len))
        
        c.execute("""
        INSERT INTO advisories_fts (rowid, user_query, gemini_response)
        VALUES (?, ?, ?)
        """, (t_id, q, r))
        count += 1
        
    conn.commit()
    print(f"Ingested {count} Gemini strategic advisory turns across all Saju chats.")
    return count

def ingest_dossier(conn):
    dossier_path = os.path.join(DESKTOP_DIR, "Selene_Song_Full_Grounding_Dossier.md")
    if not os.path.exists(dossier_path):
        print(f"Dossier not found at {dossier_path}")
        return 0
        
    with open(dossier_path, "r", encoding="utf-8") as f:
        text = f.read()
        
    c = conn.cursor()
    c.execute("""
    INSERT OR REPLACE INTO dossier (section_id, title, content)
    VALUES (?, ?, ?)
    """, ("full_dossier", "Selene Song Full Grounding Dossier", text))
    
    sections = re.split(r'\n(?=##\s+)', text)
    for s in sections:
        match = re.match(r'##\s+(.*)', s)
        if match:
            title = match.group(1).strip()
            sec_id = re.sub(r'[^a-zA-Z0-9_]+', '_', title.lower())
            c.execute("INSERT OR REPLACE INTO dossier (section_id, title, content) VALUES (?, ?, ?)",
                      (sec_id, title, s.strip()))
                      
    conn.commit()
    print(f"Ingested master dossier and {len(sections)} indexed sections.")
    return len(sections)

def main():
    print("=== Initializing Ground Truth Local SQLite Database ===")
    conn = sqlite3.connect(DB_PATH)
    init_db(conn, drop_existing=True)
    
    print("\n--- Ingesting Complete Instagram Messages (including Sept 9 Live) ---")
    ingest_instagram(conn)
    
    print("\n--- Ingesting Google Chat Messages ---")
    ingest_google_chat(conn)
    
    print("\n--- Ingesting Google Meet Transcripts ---")
    ingest_meet_transcripts(conn)
    
    print("\n--- Ingesting Master Grounding Dossier ---")
    ingest_dossier(conn)
    
    print("\n--- Ingesting All Gemini Strategic Advisories (Master + Secondary Saju) ---")
    ingest_gemini_advisories(conn)
    
    # Final database metrics
    c = conn.cursor()
    raw_count = c.execute("SELECT COUNT(*) FROM raw_messages").fetchone()[0]
    adv_count = c.execute("SELECT COUNT(*) FROM gemini_advisories").fetchone()[0]
    meet_count = c.execute("SELECT COUNT(*) FROM meet_transcripts").fetchone()[0]
    dossier_count = c.execute("SELECT COUNT(*) FROM dossier").fetchone()[0]
    conn.close()

    print("\n=== Final Master Ground Truth Verification ===")
    print(f"  • Total Raw Messages (IG + Chat): {raw_count}")
    print(f"  • Total Gemini Strategic Advisories: {adv_count}")
    print(f"  • Total Google Meet Records: {meet_count}")
    print(f"  • Total Dossier Sections: {dossier_count}")
    print(f"  • Local Database Location: {DB_PATH}")

if __name__ == "__main__":
    main()
