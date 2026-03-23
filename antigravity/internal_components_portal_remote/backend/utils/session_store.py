import json
import os
import time
from typing import List, Dict, Optional

SESSION_INDEX_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "local_only", "saved_sessions.json")

def load_sessions() -> List[Dict]:
    """Loads the sessions list from disk."""
    if not os.path.exists(SESSION_INDEX_FILE):
        os.makedirs(os.path.dirname(SESSION_INDEX_FILE), exist_ok=True)
        return []
    try:
        with open(SESSION_INDEX_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return []

def save_sessions(sessions: List[Dict]):
    """Saves the sessions list to disk."""
    os.makedirs(os.path.dirname(SESSION_INDEX_FILE), exist_ok=True)
    with open(SESSION_INDEX_FILE, "w") as f:
        json.dump(sessions, f, indent=2)

def upsert_session(session_id: str, title: str):
    """Adds or updates a session with a title and timestamp."""
    sessions = load_sessions()
    now = time.time()
    for s in sessions:
        if s["id"] == session_id:
            s["title"] = title
            s["updated_at"] = now
            save_sessions(sessions)
            return
            
    sessions.append({
        "id": session_id,
        "title": title,
        "created_at": now,
        "updated_at": now
    })
    # Sort by descending order of updated at
    sessions.sort(key=lambda x: x["updated_at"], reverse=True)
    save_sessions(sessions)

def get_session_title(session_id: str) -> Optional[str]:
    """Gets the title if it exists on disk."""
    sessions = load_sessions()
    for s in sessions:
        if s["id"] == session_id:
            return s["title"]
    return None
