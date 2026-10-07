import os
import re
import json
import time
import sqlite3
import numpy as np
from google import genai

DATA_DIR = os.path.expanduser(
    "~/IdeaProjects/vertex-ai-samples/semiautonomous-agents/companion-grounding-mcp/data"
)
DB_PATH = os.path.join(DATA_DIR, "ground_truth.db")
IG_VERIFIED_PATH = os.path.join(DATA_DIR, "instagram_from_msg1_verified.json")

PROJECT_ID = "vtxdemos"
LOCATION = "us-central1"
EMBED_MODEL = "gemini-embedding-001"

DATE_HEADER_RE = re.compile(
    r"^(\d{1,2}/\d{1,2}/\d{2,4},?\s+\d{1,2}:\d{2}\s*[AP]M|"
    r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},\s+\d{4},?\s+\d{1,2}:\d{2}\s*[AP]M|"
    r"(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)\s+\d{1,2}:\d{2}\s*[AP]M)$",
    re.IGNORECASE,
)


def analyze_sentiment_and_models(sender: str, text: str, prev_sender: str, consecutive_by_sender: int):
    """Compute sentiment score/label and Mark Manson 'Models' positives/flaws for Jesus's messages."""
    t_low = text.lower().strip()
    words = t_low.split()
    word_count = len(words)

    # 1. Sentiment Analysis (for both Selene and Jesus)
    pos_markers = [
        "love", "happy", "amazing", "great", "thank", "nice", "good", "haha", "lol",
        "yay", "awesome", "beautiful", "sweet", "excited", "glad", "❤️", "😍", "🙌", "💪", "✨"
    ]
    vuln_markers = [
        "passed away", "sick", "hard time", "split", "relationship", "healed", "scared",
        "nervous", "tired", "sleepy", "sedation", "alone", "miss", "freedom", "ex"
    ]
    playful_markers = [
        ":p", "😜", "😆", "😹", "cane", "mustache", "matrushka", "lonely flower", "villamelon",
        "challenge accepted", "black belt", "careful with my words", "plan worked", "boss level"
    ]
    apologetic_markers = [
        "sorry", "apologize", "hope you don't mind", "don't want to entertain", "asking a bunch of questions",
        "tell me when there is a lot", "my bad", "mixed up"
    ]

    pos_hits = sum(1 for m in pos_markers if m in t_low)
    vuln_hits = sum(1 for m in vuln_markers if m in t_low)
    play_hits = sum(1 for m in playful_markers if m in t_low)
    apol_hits = sum(1 for m in apologetic_markers if m in t_low)

    score = min(1.0, max(-1.0, 0.25 * pos_hits + 0.3 * play_hits + 0.15 * vuln_hits - 0.3 * apol_hits))
    if play_hits > 0:
        sentiment_label = "Playful / Teasing & Warm"
    elif vuln_hits > 0:
        sentiment_label = "Vulnerable / Emotionally Open"
    elif apol_hits > 0:
        sentiment_label = "Apologetic / Self-Conscious"
    elif pos_hits >= 2:
        sentiment_label = "High-Warmth / Enthusiastic"
    elif pos_hits == 1:
        sentiment_label = "Positive / Friendly"
    else:
        sentiment_label = "Neutral / Conversational"

    # If Selene is the sender, we record her receptivity / investment signal
    if sender != "Jesus":
        selene_signals = []
        if any(k in t_low for k in ["gift for you", "bring one", "see you soon", "sep 2nd", "office on 2nd", "catch up"]):
            selene_signals.append("Proactive Future / In-Person Investment")
        if any(k in t_low for k in ["special flower", "look so young", "makes me feel so much better", "glad you like it"]):
            selene_signals.append("High Warmth / Direct Validation")
        if any(k in t_low for k in ["freedom", "my ex", "graduate thesis", "black belt", "childlike", "teared up"]):
            selene_signals.append("Deep Personal Self-Disclosure")
        if any(k in t_low for k in ["hahaha", "lol", "phahaha", "😹"]):
            selene_signals.append("High Banter / Laughter Receptivity")
        return {
            "sentiment_label": sentiment_label,
            "sentiment_score": round(score, 2),
            "models_positives": json.dumps(selene_signals),
            "models_flaws": json.dumps([]),
            "models_net_rating": "Selene High Receptivity" if selene_signals else "Selene Normal Engagement",
            "models_coaching_note": "Selene is reciprocating warmly and investing details." if selene_signals else ""
        }

    # 2. Mark Manson 'Models' Analysis for Jesus's messages
    positives = []
    flaws = []
    notes = []

    # Check Positive Applications of Models
    if any(k in t_low for k in ["cane is coming", "grey", "lonely flower", "matrushka", "careful with my words", "plan worked", "tulane", "villamelon", ":p", "😆"]):
        positives.append("Playful Teasing & Push-Pull Banter")
        notes.append("Good use of playful teasing/push-pull instead of dry corporate small talk.")

    if any(k in t_low for k in ["left my family when i was 17", "mom got sick", "passed away", "nearly two years since my split", "sedation", "endoscopy"]):
        positives.append("Authentic Vulnerability (Emotional Courage)")
        notes.append("Strong Models Chapter 4 vulnerability: sharing real personal history openly without begging for sympathy.")

    if any(k in t_low for k in ["dang! you look good", "discover that", "when are you leaving me", "get my gifts", "passed from one type of red"]):
        positives.append("Polarizing / Unapologetic Attraction Signal")
        notes.append("Good polarization: signaling romantic/personal appreciation rather than hiding strictly in the colleague zone.")

    if any(k in t_low for k in ["colonized", "mayan", "astrology", "saju", "discipline, dedication, courage", "ultimately matters is what you enjoy"]):
        positives.append("Intellectual & Cultural Depth")
        notes.append("Projects grounded identity, values, and intellectual depth.")

    # Check Models Flaws / Neediness Leaks
    if any(k in t_low for k in [
        "ended up asking a bunch of questions",
        "tell me when there is a lot",
        "hope you don't mind",
        "don't want youyo entrain",
        "don't want to entertain",
        "always ended up talking a lot with you",
        "good bye to my recovery"
    ]):
        flaws.append("Apologetic Self-Qualification (Permission-Seeking)")
        notes.append("Models Flaw: Never apologize for taking up her time or enjoying the conversation; it frames yourself as a burden and asks her to validate you.")

    if any(k in t_low for k in [
        "you def have more experience than i have",
        "you don't need help because you're amazing",
        "you are special. people with such skills",
        "can't believe what you have done, you should be very proud",
        "way more that i could possibly do"
    ]):
        flaws.append("Pedestalizing / Over-Validation")
        notes.append("Models Flaw: Avoid placing her on a pedestal above you ('way more than I could do'); validate her as an equal peer, not a fan.")

    if any(k in t_low for k in ["mixed up sorry", "damn so sorry"]):
        flaws.append("Supplication / Over-Apologizing for Minor Slip")
        notes.append("Models Flaw: Apologizing multiple times for a tiny geography mix-up lowers frame; laugh it off once and move on.")

    if consecutive_by_sender >= 4 or word_count > 55:
        flaws.append("Over-Investment / Multi-Bubble Chasing Asymmetry")
        notes.append("Models Calibration: Sending 4+ consecutive bubbles or long paragraphs increases investment asymmetry; match her concise pacing.")

    if positives and not flaws:
        net_rating = "Strong Models Execution (Non-Needy & Polarizing)"
    elif positives and flaws:
        net_rating = "Mixed Execution (Good Warmth/Banter but Contains Qualification/Pedestalizing)"
    elif flaws:
        net_rating = "Models Flaw Detected (Neediness / Over-Qualification Leak)"
    else:
        net_rating = "Neutral / Grounded Rapport"

    return {
        "sentiment_label": sentiment_label,
        "sentiment_score": round(score, 2),
        "models_positives": json.dumps(positives),
        "models_flaws": json.dumps(flaws),
        "models_net_rating": net_rating,
        "models_coaching_note": " ".join(notes)
    }


TOPIC_DEFINITIONS = [
    ("malaysia_and_grad_school", "Malaysia Trip, Intel Conference & Grad School Friend/Thesis",
     ["malaysia", "penang", "kuala lumpur", "nasi lemak", "best friend from graduate", "malaysian economic", "surrounded by 5000"]),
    ("education_and_martial_arts", "Education: Economics Master's, Taekwondo Black Belt & Career Pivot",
     ["what's your major", "econ!!!", "econ for grad", "taekwondo", "international studies", "black belt", "cognizant", "principal eng", "oracle"]),
    ("cats_constantine_and_beanie", "Constantine & Beanie (Pets, Vet, Cat Sitters, Food & Cane in 3 Years)",
     ["constantine", "beanie", "cat", "kitten", "cane", "tiki", "weruva", "korean air", "sitter", "vet", "litter"]),
    ("saju_and_mayan_astrology", "Korean Saju Readings, Birth Charts & Mayan Calendar Alignment",
     ["saju", "mayan", "astrology", "birth", "pillar", "wood horse", "reading", "screenshot of your saju"]),
    ("nyc_in_person_dates_and_office", "NYC Office Visits (Sep 2 & Oct 2), Manhattan & In-Person Plans",
     ["sep 2nd", "office on 2nd", "8510", "pier", "white plains", "sfo", "come to the office", "see you soon", "masquerade"]),
    ("past_relationships_and_healing", "Past Relationships, Ex-Breakups, Healing & Emotional Recovery",
     ["long term relationship", "my split", "getting healed", "freedom", "subordinate", "ex ", "breakup", "fall in love with something"]),
    ("mexico_and_tulum_travel", "Mexico Culture, Tulum Mayan Ruins, Puerto Vallarta & World Cup",
     ["tulum", "tulim", "puerto vallarta", "ritmo de la noche", "rhythms of the night", "colonized", "mexican", "world cup"]),
    ("korea_roots_and_family", "South Korea Roots, Parents' Home, Matrushka Doll & Year-End Work from Korea",
     ["korea", "seoul", "matrushka", "doll", "thanksgiving", "parents home", "working from anywhere"]),
    ("sports_nba_and_athletics", "NBA (Miami Heat vs Celtics 2024, Knicks in Five), Ballet & Boxing",
     ["knicks", "miami heat", "celtics", "spoelstra", "jalen", "playoff", "villamelon", "ballet", "boxing"]),
    ("fashion_eyewear_and_aesthetics", "Cartier Santos Eyewear, Style Compliments & Photos",
     ["cartier", "santos", "eyewear", "glasses", "look so young", "look good", "grey mustached"]),
    ("personality_and_inner_child", "Louise Belcher (Bob's Burgers), Sarcasm vs Childlike Nature & Meditation",
     ["sarcastic", "childlike", "meditate", "louise", "special flower", "shiny garden", "lonely flower"]),
    ("health_and_medical_care", "Health, Endoscopy/Sedation, Dinorah & Sleep/Red-Eye Recovery",
     ["sedation", "dinorah", "red eyes", "recovery", "sleepy", "go to bed", "1 am", "endoscopy"]),
    ("gifts_and_souvenirs", "Gifts & Souvenirs Exchange (Mexico, Malaysia & Korea)",
     ["souvenir", "bringing gift", "bring one", "get my gifts", "gesture", "something from korea"]),
    ("plants_and_home_life", "Poisonous Plant Assessment, Plant Whisperer & Home Routine",
     ["plant", "poisonous", "pot", "dr. selene", "prime suspect", "almond or soy"]),
]


def rebuild_verified_messages_and_graph():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # 1. Load the 100% verified Instagram stream from Message #1 (10/11/24, 11:00 PM)
    ig_raw = json.load(open(IG_VERIFIED_PATH, "r", encoding="utf-8"))

    # Separate inline date headers from actual chat messages
    ig_clean = []
    cur_date_str = "2024-10-11 23:00"
    for item in ig_raw:
        txt = (item.get("text") or "").strip()
        if not txt:
            continue
        # Skip pure UI labels like "You replied to selenesng", "selenesng replied to you", "Edited"
        if txt in ("You replied to selenesng", "selenesng replied to you", "Edited", "Instagram"):
            continue
        if DATE_HEADER_RE.match(txt):
            cur_date_str = txt
            continue
        ig_clean.append({
            "platform": "Instagram",
            "sender": item["sender"],
            "timestamp": cur_date_str,
            "text": txt,
            "raw_json": json.dumps(item)
        })

    # Also ensure the final Sept 13, 2026 evening messages are included at the end of Instagram
    c.execute(
        "SELECT sender, timestamp, text, raw_json FROM raw_messages WHERE platform = 'Instagram' AND timestamp LIKE '2026-09-13%' ORDER BY id ASC"
    )
    sep13_rows = c.fetchall()
    existing_tail_texts = {m["text"] for m in ig_clean[-30:]}
    for s, ts, txt, rj in sep13_rows:
        if txt not in existing_tail_texts:
            ig_clean.append({
                "platform": "Instagram",
                "sender": "Selene" if "selene" in s.lower() else "Jesus",
                "timestamp": ts,
                "text": txt,
                "raw_json": rj or "{}"
            })

    # 2. Fetch all 764 verified Google Chat messages
    c.execute(
        "SELECT sender, timestamp, text, reactions, media_desc, raw_json, native_msg_id FROM raw_messages WHERE platform = 'Google Chat' ORDER BY id ASC"
    )
    gchat_rows = c.fetchall()

    # Recreate raw_messages with full analytical, sentiment, Models, and channel columns
    c.execute("DROP TABLE IF EXISTS raw_messages_fts")
    c.execute("DROP TABLE IF EXISTS raw_messages")
    c.execute(
        """
        CREATE TABLE raw_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            platform TEXT,
            platform_msg_index INTEGER,
            channel_name TEXT,
            channel_id TEXT,
            account_type TEXT,
            thread_url TEXT,
            native_msg_id TEXT,
            sender TEXT,
            timestamp TEXT,
            text TEXT,
            reactions TEXT,
            media_desc TEXT,
            sentiment_label TEXT,
            sentiment_score REAL,
            models_positives TEXT,
            models_flaws TEXT,
            models_net_rating TEXT,
            models_coaching_note TEXT,
            linked_topics TEXT,
            raw_json TEXT
        )
        """
    )

    all_to_insert = []
    # Add Instagram messages (from Message #1 on Oct 11, 2024 to Sep 13, 2026)
    for idx, m in enumerate(ig_clean, start=1):
        all_to_insert.append({
            "platform": "Instagram",
            "platform_msg_index": idx,
            "channel_name": "Instagram Direct Message (@selenesng <-> @jchavezarg)",
            "channel_id": "ig_dm_119805939405917",
            "account_type": "Personal Social Account (Instagram @selenesng / @jchavezarg)",
            "thread_url": "https://www.instagram.com/direct/t/119805939405917/",
            "native_msg_id": f"ig_msg_{idx}",
            "sender": m["sender"],
            "timestamp": m["timestamp"],
            "text": m["text"],
            "reactions": "",
            "media_desc": "",
            "raw_json": m["raw_json"]
        })

    # Add Google Chat messages (1..764)
    for idx, r in enumerate(gchat_rows, start=1):
        s, ts, txt, react, media, rj, nat_id = r
        norm_s = "Selene" if "selene" in (s or "").lower() else "Jesus"
        all_to_insert.append({
            "platform": "Google Chat",
            "platform_msg_index": idx,
            "channel_name": "Google Chat 1:1 DM (selenesong@google.com <-> jesusarguelles@google.com | spaces/jeWaL0AAAAE)",
            "channel_id": "spaces/jeWaL0AAAAE",
            "account_type": "Corporate Google Workspace (selenesong@google.com / jesusarguelles@google.com)",
            "thread_url": "https://chat.google.com/dm/jeWaL0AAAAE",
            "native_msg_id": nat_id or f"gchat_msg_{idx}",
            "sender": norm_s,
            "timestamp": ts or "",
            "text": txt or "",
            "reactions": react or "",
            "media_desc": media or "",
            "raw_json": rj or "{}"
        })

    prev_sender = ""
    consec_count = 0
    for item in all_to_insert:
        if item["sender"] == prev_sender:
            consec_count += 1
        else:
            consec_count = 1
            prev_sender = item["sender"]

        analysis = analyze_sentiment_and_models(
            item["sender"], item["text"], prev_sender, consec_count
        )

        # Match topics for the Temporal Knowledge Graph
        t_low = item["text"].lower()
        matched_topics = [
            t_id for t_id, t_title, kw_list in TOPIC_DEFINITIONS
            if any(kw in t_low for kw in kw_list)
        ]

        c.execute(
            """
            INSERT INTO raw_messages (
                platform, platform_msg_index, channel_name, channel_id, account_type,
                thread_url, native_msg_id, sender, timestamp, text, reactions, media_desc,
                sentiment_label, sentiment_score, models_positives, models_flaws,
                models_net_rating, models_coaching_note, linked_topics, raw_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                item["platform"],
                item["platform_msg_index"],
                item["channel_name"],
                item["channel_id"],
                item["account_type"],
                item["thread_url"],
                item["native_msg_id"],
                item["sender"],
                item["timestamp"],
                item["text"],
                item["reactions"],
                item["media_desc"],
                analysis["sentiment_label"],
                analysis["sentiment_score"],
                analysis["models_positives"],
                analysis["models_flaws"],
                analysis["models_net_rating"],
                analysis["models_coaching_note"],
                json.dumps(matched_topics),
                item["raw_json"]
            )
        )

    # Rebuild FTS5 table
    c.execute(
        """
        CREATE VIRTUAL TABLE raw_messages_fts USING fts5(
            platform, sender, text, reactions, media_desc, models_net_rating, linked_topics,
            content='raw_messages', content_rowid='id'
        )
        """
    )
    c.execute("INSERT INTO raw_messages_fts(raw_messages_fts) VALUES('rebuild')")

    # 3. Build Cross-Date Temporal Knowledge Graph tables
    c.execute("DROP TABLE IF EXISTS topic_graph_nodes")
    c.execute("DROP TABLE IF EXISTS topic_graph_edges")
    c.execute(
        """
        CREATE TABLE topic_graph_nodes (
            topic_id TEXT PRIMARY KEY,
            topic_title TEXT,
            total_mentions INTEGER,
            platforms_spanned TEXT,
            first_seen_timestamp TEXT,
            last_seen_timestamp TEXT,
            summary_json TEXT
        )
        """
    )
    c.execute(
        """
        CREATE TABLE topic_graph_edges (
            edge_id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic_id TEXT,
            topic_title TEXT,
            from_msg_id INTEGER,
            to_msg_id INTEGER,
            from_platform TEXT,
            to_platform TEXT,
            from_timestamp TEXT,
            to_timestamp TEXT,
            cross_platform_hop INTEGER,
            relationship_type TEXT
        )
        """
    )

    for t_id, t_title, _ in TOPIC_DEFINITIONS:
        c.execute(
            "SELECT id, platform, channel_name, timestamp, sender, text FROM raw_messages WHERE linked_topics LIKE ? ORDER BY id ASC",
            (f'%"{t_id}"%',)
        )
        mentions = c.fetchall()
        if not mentions:
            continue
        platforms = sorted(list({m[1] for m in mentions}))
        first_ts = mentions[0][3]
        last_ts = mentions[-1][3]
        key_milestones = [
            {"msg_id": m[0], "platform": m[1], "timestamp": m[3], "sender": m[4], "text": m[5][:140]}
            for m in mentions
        ]
        c.execute(
            "INSERT INTO topic_graph_nodes VALUES (?, ?, ?, ?, ?, ?, ?)",
            (t_id, t_title, len(mentions), ", ".join(platforms), first_ts, last_ts, json.dumps(key_milestones))
        )
        for i in range(len(mentions) - 1):
            m1 = mentions[i]
            m2 = mentions[i + 1]
            cross = 1 if m1[1] != m2[1] else 0
            rel = "CROSS_PLATFORM_CONTINUATION" if cross else "TEMPORAL_CALLBACK"
            c.execute(
                """
                INSERT INTO topic_graph_edges (
                    topic_id, topic_title, from_msg_id, to_msg_id,
                    from_platform, to_platform, from_timestamp, to_timestamp,
                    cross_platform_hop, relationship_type
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (t_id, t_title, m1[0], m2[0], m1[1], m2[1], m1[3], m2[3], cross, rel)
            )

    # Also add Selene's Cat Food Google Doc to dossier
    cat_doc_text = (
        "Google Doc created and shared by Selene Song on Aug 26, 2026 ('Choosing Cat Food', Doc ID: 1OjgTb1dy3FRmSg7SWkPp7wTjQqnf4fQSeAxyRtumfd4):\n"
        "- Wet food recommendations: Tiki Cat, Weruva, Instinct, plus subscription human-grade brands (Small, Nom Nom, Cat Person, Darwin).\n"
        "- Frozen dry raw recommendations: Dr. Marty, Stella & Chewy, Primal Nuggets.\n"
        "- Dental care: Use an angled brush with flavored toothpaste slowly over days; solid dental treats help plaque, liquid supplements do not.\n"
        "- Toys: Food puzzle toys & Flippy addictive fish toy."
    )
    c.execute(
        "INSERT OR REPLACE INTO dossier (section_id, title, content) VALUES (?, ?, ?)",
        ("selene_cat_food_google_doc", "Selene's 'Choosing Cat Food' Google Doc (Aug 26, 2026)", cat_doc_text)
    )

    conn.commit()
    ig_total = c.execute("SELECT COUNT(*) FROM raw_messages WHERE platform='Instagram'").fetchone()[0]
    gc_total = c.execute("SELECT COUNT(*) FROM raw_messages WHERE platform='Google Chat'").fetchone()[0]
    edge_total = c.execute("SELECT COUNT(*) FROM topic_graph_edges").fetchone()[0]
    print(f"Rebuilt raw_messages: {ig_total} verified Instagram msgs (from Msg #1 on 10/11/24) + {gc_total} Google Chat msgs = {ig_total + gc_total} total.")
    print(f"Constructed Temporal Knowledge Graph with {len(TOPIC_DEFINITIONS)} topic nodes and {edge_total} cross-date edges.")
    conn.close()


if __name__ == "__main__":
    rebuild_verified_messages_and_graph()
