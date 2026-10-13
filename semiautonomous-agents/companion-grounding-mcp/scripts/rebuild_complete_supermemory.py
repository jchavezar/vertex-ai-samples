#!/usr/bin/env python3
"""
Master Zero-Loss Consolidation, Chronological Rebuilder, Knowledge Graph & Vector Indexer
for Companion Grounding Supermemory (ground_truth.db).
"""

import os
import re
import json
import time
import shutil
import sqlite3
import numpy as np
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime
from google import genai

DB_PATH = "/usr/local/google/home/jesusarguelles/companion-grounding-mcp/data/ground_truth.db"
BACKUP_PATH = "/usr/local/google/home/jesusarguelles/companion-grounding-mcp/data/ground_truth.db.bak_20261013"
SNAPS_PATH = "/usr/local/google/home/jesusarguelles/.gemini/jetski/brain/d8addc88-8268-4c00-abf7-07eeeed7bc21/selene_snapshots.json"
ALL_LINES_PATH = "/usr/local/google/home/jesusarguelles/.gemini/jetski/brain/d8addc88-8268-4c00-abf7-07eeeed7bc21/selene_all_lines.txt"

PROJECT_ID = "vtxdemos"
LOCATION = "us-central1"
EMBED_MODEL = "gemini-embedding-001"

DATE_RE = re.compile(
    r"^(?:(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},?\s*\d{0,4},?\s*\d{1,2}:\d{2}\s*(?:AM|PM)|"
    r"(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)\s+\d{1,2}:\d{2}\s*(?:AM|PM)|"
    r"\d{1,2}/\d{1,2}/\d{2,4},?\s+\d{1,2}:\d{2}\s*(?:AM|PM))$",
    re.I,
)


def norm_text(s: str) -> str:
    return " ".join((s or "").replace("\u202f", " ").replace("\xa0", " ").split())


def parse_to_utc_iso(ts_str: str, fallback_iso: str = "2026-07-15T12:00:00") -> str:
    s = (ts_str or "").replace("\u202f", " ").strip()
    if not s or "Archive" in s or s == "Instagram":
        return fallback_iso
    s_clean = re.sub(r"\s*\([^)]*\)\s*$", "", s).strip()

    try:
        iso_cand = s_clean.replace("Z", "+00:00")
        dt = datetime.fromisoformat(iso_cand)
        if dt.tzinfo is not None:
            edt_tz = timezone(timedelta(hours=-4))
            dt_edt = dt.astimezone(edt_tz).replace(tzinfo=None)
            return dt_edt.strftime("%Y-%m-%dT%H:%M:%S")
        return dt.strftime("%Y-%m-%dT%H:%M:%S")
    except Exception:
        pass

    fmts = [
        "%m/%d/%y, %I:%M %p",
        "%m/%d/%Y, %I:%M %p",
        "%b %d, %Y, %I:%M %p",
        "%b %d, %Y %I:%M %p",
        "%B %d, %Y, %I:%M %p",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d",
        "%b %d, %Y",
    ]
    for fmt in fmts:
        try:
            dt = datetime.strptime(s_clean, fmt)
            return dt.strftime("%Y-%m-%dT%H:%M:%S")
        except Exception:
            continue

    return fallback_iso


def infer_sender_for_missing_ig_line(line: str, prev_sender: str) -> str:
    l_low = line.lower().strip()
    jesus_clues = [
        "thank you for bringing me to this place",
        "the cane is coming in 3 years",
        "wait... truly knicks fan",
        "that's what i wanted talk about",
        "yes i’m literally looking for the meaning",
        "historically speaking that’s a fact",
        "misogynist, and a bunch of negative values",
        "it’s a beautiful country, played of amazing people",
        "yes, lot of things happening down there",
        "have you ever gone?",
        "i still have a bunch of talk to you later",
        "i hope you don't mind",
        "oh thank you, it was luck",
        "your country played better",
        "i talk to people like they'd watched soccer",
        "ye i don't have a thing for the little roaches",
        "it's just how he's always with his legs shrinked",
        "i'm so happy for you! best decision taken ever",
        "oh ye good luck with that",
        "thank you, for taking the time again",
        "hey selene",
        "oh beautiful! that reminds me my hometown a lot",
        "(la virgen de guadalupe)",
        "yes yes please do play for me",
        "yes, you too",
        "i love when you show up",
        "ohh ok so it depends on the provider",
        "which one are you planning to use?",
        "i knew you said that",
        "that's why you're my fav engineer",
        "after that integrate the same agent with 3p connector",
        "a lot of security trash that now i have nightmares with",
        "nope",
        "right but sales will need to sell something",
        "get measured by sales acumen too",
        "it's like the hot tub is to hot",
        "ye that's true, i have some demons in my head",
        "do you think so?",
        "have you thought about it? like going as fde",
        "true, i never worry about the money",
        "omg selene",
        "i feel you are in a great place",
        "you are not",
        "hummm makes me think a lot",
        "tams usually have 2 faces",
        "10000000000000%!",
        "seriously?!",
        "i deal most of my time with many ces",
        "yes true! you know one of the cem2 gave a speech",
        "ahh! i was about to say \"aguachile\"",
        "ah aha! i haven't gone to this one, it reminds me \"los mariscos\"",
        "hahahaha tripa taco! oh girl you're something haha",
        "you have a folclorical taste",
        "i'm gonna be candid with this",
        "ok, i respect other people",
        "yes that's what i hate the most",
        "but i didn't want to ruin the conversation",
        "let's say like a lot of variety",
        "like a person with many tastes",
        "ahh k town very close from home, i gotta explore",
        "this how i go to the office",
        "the day you go far i will go to anthropic",
        "see he doesn't know a thing",
        "they are for now because that was the only way to have spark enterprise",
        "no impossible one is the workspace license",
        "oh i know what he's referring to!",
        "lm confirm something but i have to go",
        "but he's basically saying what i tried to explain earlier",
        "versetheprincess",
        "blackcathub",
        "inocat_t",
        "ulises.bernalm",
    ]
    selene_clues = [
        "yeah i didn’t think i would see knicks",
        "me in playoff game heat vs celtics",
        "i should study more of it so that i can explain",
        "wtf",
        "i see… i don’t have too much cultural context about mexico",
        "yeah but briefly. ive been to tulum",
        "i need to test connecting to mcp server",
        "yes i think i picked the right time to get out!",
        "keep me posted!",
        "how do you find a mcp server that you can test connection?",
        "i want corp ones not the ones in github",
        "it was nice seeing you in a while",
        "anything",
        "haha that sounds convenient",
        "do you put auth tokens inside of the adk?",
        "i feel like you can get very well compensated",
        "if you are in sales yes",
        "i think this oce path will become more and more different",
        "i don’t know. i guess we will find out early next year",
        "i think there will be some changes for account ces",
        "yes to me, it’s better than sales ladder",
        "i guess i will see after the intel work",
        "am i?",
        "ai ce is a good place to be",
        "i think that’s why brendan",
        "whoa internet service just got really patchy",
        "we really should stop selling more though",
        "ge pm specifically said that there is no plan",
        "i was told that some huge deals are selling gecx",
        "oh so some huge deals as in other customers",
        "they are pretty young and in early career",
        "i mean they are not 20 but",
        "it was a big deal for strato",
        "and now i realized",
        "there are many ces",
        "outside of my fellow ce org",
        "just doing basic stuff",
        "i have no idea",
        "right???",
        "i also considered to try becoming a pa hm",
        "that happend two years afo",
        "i want to hear more",
        "i thought it’s tomato",
        "poinsettias are technically poisonous to cats",
        "it doesn’t sound serious, but if beanie nibbles",
        "selenesng sent 5 photos",
        "haha i can see that",
        "there were only 2 at whole foods",
        "right back there",
        "i had aguachille in san antonio",
        "probably my favorite mexican food",
        "there is also really food aguachile place in brooklyn",
        "mariscos el submarino",
        "maps.app.goo.gl/koef4ta1v17aanwa7",
        "everything is spicy",
        "this is way better",
        "their housemade corn tortillas is so good",
        "this place i like tripa taco",
        "that’s perfectly fine. plus octopus is highly intelligent",
        "what is folclorical?",
        "i like menudo as well",
        "similar to korean soup",
        "that’s perfectly fine",
        "there is k town but the food quality is ok",
        "how long does it take?",
        "i thought you are super near to the office",
        "does it makes a two minute ride?",
        "lolllll noooooooo",
        "eric peter just confirmed",
        "gemini enterprise desktop app",
        "wait, he just said something diff",
        "oh my god, i’m so confused",
        "are you on fish food?",
        "wow, so these are two essentially different product",
        "let me cc you",
        "they’re both tied to same license",
        "according to eric",
        "????",
    ]
    for c in jesus_clues:
        if c in l_low:
            return "Jesus"
    for c in selene_clues:
        if c in l_low:
            return "Selene"
    return prev_sender or "Selene"


def analyze_sentiment_and_models(sender: str, text: str, prev_sender: str, consecutive_by_sender: int):
    """Contextual sentiment & Mark Manson 'Models' calibration across all platforms."""
    t_low = text.lower().strip()
    words = t_low.split()
    word_count = len(words)

    pos_markers = [
        "love", "happy", "amazing", "great", "thank", "nice", "good", "haha", "lol",
        "yay", "awesome", "beautiful", "sweet", "excited", "glad", "❤️", "😍", "🙌", "💪", "✨", "🎉"
    ]
    vuln_markers = [
        "passed away", "sick", "hard time", "split", "relationship", "healed", "scared",
        "nervous", "tired", "sleepy", "sedation", "alone", "miss", "freedom", "ex", "splash of cold water", "demons in my head"
    ]
    playful_markers = [
        ":p", "😜", "😆", "😹", "cane", "mustache", "matrushka", "lonely flower", "villamelon",
        "challenge accepted", "black belt", "careful with my words", "plan worked", "boss level",
        "go to anthropic", "connect me jetski to my veins", "killed me with that one", "tripa taco", "folclorical", "mariachi"
    ]
    apologetic_markers = [
        "sorry", "apologize", "hope you don't mind", "don't want to entertain", "asking a bunch of questions",
        "tell me when there is a lot", "my bad", "mixed up", "didn't want to ruin the conversation"
    ]

    pos_hits = sum(1 for m in pos_markers if m in t_low)
    vuln_hits = sum(1 for m in vuln_markers if m in t_low)
    play_hits = sum(1 for m in playful_markers if m in t_low)
    apol_hits = sum(1 for m in apologetic_markers if m in t_low)

    score = min(1.0, max(-1.0, 0.25 * pos_hits + 0.35 * play_hits + 0.15 * vuln_hits - 0.3 * apol_hits))
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

    if sender != "Jesus":
        selene_signals = []
        if any(k in t_low for k in [
            "gift for you", "bring one", "see you soon", "sep 2nd", "office on 2nd", "catch up",
            "lunch", "share your calendar", "moving next year", "sauna", "let me cc you", "nice seeing you"
        ]):
            selene_signals.append("Proactive Future / In-Person Investment")
        if any(k in t_low for k in [
            "special flower", "look so young", "makes me feel so much better", "glad you like it",
            "thank you jesus!!", "glad it helped", "lolllll noooooooo"
        ]):
            selene_signals.append("High Warmth / Direct Validation")
        if any(k in t_low for k in [
            "freedom", "my ex", "graduate thesis", "black belt", "childlike", "teared up",
            "tripa taco", "menudo", "sauna in the building", "michael burry"
        ]):
            selene_signals.append("Deep Personal Self-Disclosure")
        if any(k in t_low for k in ["hahaha", "lol", "phahaha", "😹", "😂", "😆"]):
            selene_signals.append("High Banter / Laughter Receptivity")
        return {
            "sentiment_label": sentiment_label,
            "sentiment_score": round(score, 2),
            "models_positives": json.dumps(selene_signals),
            "models_flaws": json.dumps([]),
            "models_net_rating": "Selene High Receptivity" if selene_signals else "Selene Normal Engagement",
            "models_coaching_note": "Selene is reciprocating warmly and investing personal/future details." if selene_signals else "",
        }

    positives = []
    flaws = []
    notes = []

    if any(k in t_low for k in [
        "cane is coming", "grey", "lonely flower", "matrushka", "careful with my words", "plan worked",
        "tulane", "villamelon", ":p", "😆", "go to anthropic", "tripa taco", "folclorical", "killed me with that one",
        "connect me jetski to my veins", "mariachi"
    ]):
        positives.append("Playful Teasing & Push-Pull Banter")
        notes.append("Strong playful teasing/push-pull that sparks emotional momentum.")

    if any(k in t_low for k in [
        "left my family when i was 17", "mom got sick", "passed away", "nearly two years since my split",
        "sedation", "endoscopy", "splash of cold water", "demons in my head", "never worry about the money"
    ]):
        positives.append("Authentic Vulnerability (Emotional Courage)")
        notes.append("Models Chapter 4 vulnerability: sharing honest internal truth and history without seeking pity.")

    if any(k in t_low for k in [
        "dang! you look good", "discover that", "when are you leaving me", "get my gifts",
        "passed from one type of red", "i love when you show up", "fav engineer", "go to anthropic"
    ]):
        positives.append("Polarizing / Unapologetic Appreciation Signal")
        notes.append("Clear warm/personal appreciation that avoids dry corporate neutrality.")

    if any(k in t_low for k in [
        "colonized", "mayan", "astrology", "saju", "discipline, dedication, courage",
        "ultimately matters is what you enjoy", "huge impact @selene song", "gemini 4"
    ]):
        positives.append("Intellectual, Cultural & Technical Leadership")
        notes.append("Demonstrates grounded competence, cultural depth, and high-status technical leadership.")

    if any(k in t_low for k in [
        "ended up asking a bunch of questions", "tell me when there is a lot", "hope you don't mind",
        "don't want youyo entrain", "don't want to entertain", "always ended up talking a lot with you",
        "good bye to my recovery", "didn't want to ruin the conversation", "bugging you with too many questions"
    ]):
        flaws.append("Apologetic Self-Qualification (Permission-Seeking)")
        notes.append("Models Flaw: Avoid apologizing for taking up space or asking if you are bothering her; assume your presence is welcome.")

    if any(k in t_low for k in [
        "you def have more experience than i have", "you don't need help because you're amazing",
        "you are special. people with such skills", "can't believe what you have done, you should be very proud",
        "way more that i could possibly do"
    ]):
        flaws.append("Pedestalizing / Over-Validation")
        notes.append("Models Flaw: Validate her as an equal high-performing peer rather than placing her above yourself.")

    if any(k in t_low for k in ["mixed up sorry", "damn so sorry"]):
        flaws.append("Supplication / Over-Apologizing for Minor Slip")
        notes.append("Models Flaw: Don't over-apologize for minor slips; pivot with humor.")

    if consecutive_by_sender >= 5 or (word_count > 65 and "[shared google doc:" not in t_low and "[gmail:" not in t_low):
        flaws.append("Over-Investment / Multi-Bubble Chasing Asymmetry")
        notes.append("Models Calibration: Keep bubble count and length balanced with her concise rhythm.")

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
        "models_coaching_note": " ".join(notes),
    }


TOPIC_DEFINITIONS = [
    ("malaysia_and_intel_roadshow", "Malaysia Trip, Intel AI Roadshow (5,000 Employees / CIO Demo) & Grad School Friend",
     ["malaysia", "penang", "kuala lumpur", "nasi lemak", "best friend from graduate", "surrounded by 5000", "intel malaysia", "cindy stoddard", "composite yield"]),
    ("nyc_office_lunch_and_in_person", "NYC Office Visits (Sep 2 & Oct 2 Lunch at Pier 57 / 9th Floor Cafe) & Co-Location",
     ["sep 2nd", "office on 2nd", "lunch at office", "pier 57", "9th floor", "4th floor", "8510", "white plains", "come to the office", "see you soon"]),
    ("calendar_sharing_and_hola_mariachi", "Shared Google Calendar (Oct 5), Hola Celebrations, Mariachi Band & Moving Next Year (Sauna)",
     ["shared calendar", "share your calendar", "hola", "mariachi", "moving next year", "sauna", "amenities", "building"]),
    ("gemini_4_argon_and_agy_3p_models", "Gemini 4 Argon (Oct 13 b/565407631), Fairwind, Jetski & AGY 3P Models (Opus/Sonnet)",
     ["argon", "gemini 4", "565407631", "fairwind", "opus", "sonnet", "agy", "antigravity", "jetski", "rebranding"]),
    ("spark_eap_and_gogo_fishfood", "Spark EAP, Gemini Enterprise Desktop App & 'gogo fishfood support' (@Jesus Chavez CC)",
     ["fish food", "fishfood", "eric peter", "spark", "desktop app", "let me cc you", "adding @jesus chavez"]),
    ("mcp_servers_jira_and_entra_wif", "MCP Servers, Jira Atlassian Remote MCP Doc, Entra IdP & WIF Security",
     ["mcp server", "jira", "atlassian", "entra", "wif", "auth token", "adk", "3p connector"]),
    ("career_ladder_oce_ce_and_fde", "Career Ladder: OCE vs Account CE vs FDE, Comp Plan Rumors & Stock/ETFs (Michael Burry)",
     ["fde", "oce", "sales ladder", "comp plan", "michael burry", "etf", "index fund", "strato", "brendan", "gecx"]),
    ("mexican_food_aguachile_and_tripa", "Mexican Food: Aguachile (Mariscos El Submarino), Taqueria Ramirez (Tripa Taco), Menudo & Octopus",
     ["aguachile", "aguachille", "submarino", "taqueria ramirez", "tripa", "vampiro", "menudo", "octopus", "folclorical", "hot pot"]),
    ("commute_scooter_and_anthropic_banter", "NYC Commute to Office, Scooter Ride & 'The Day You Go Far I Will Go to Anthropic' Banter",
     ["go to anthropic", "ten minute walk", "two minute ride", "how i go to the office", "k town"]),
    ("cats_constantine_and_beanie", "Constantine & Beanie (Meowing on Calls, Churu, Poinsettia Toxicity & Choosing Cat Food Doc)",
     ["constantine", "beanie", "cat", "kitten", "cane", "tiki", "weruva", "churu", "poinsettia", "sitter", "vet", "meow"]),
    ("education_and_martial_arts", "Education: Economics Master's, Taekwondo Black Belt & Career Pivot",
     ["what's your major", "econ!!!", "econ for grad", "taekwondo", "international studies", "black belt", "cognizant", "principal eng", "oracle"]),
    ("saju_and_mayan_astrology", "Korean Saju Readings, Birth Charts & Mayan Calendar Alignment",
     ["saju", "mayan", "astrology", "birth", "pillar", "wood horse", "reading", "screenshot of your saju"]),
    ("past_relationships_and_healing", "Past Relationships, Ex-Breakups, Healing & Emotional Recovery",
     ["long term relationship", "my split", "getting healed", "freedom", "subordinate", "ex ", "breakup", "fall in love with something"]),
    ("mexico_roots_tulum_and_coco", "Mexico Culture, Coatzacoalcos, Tulum Mayan Ruins, Puerto Vallarta, Coco & Virgen de Guadalupe",
     ["tulum", "tulim", "puerto vallarta", "ritmo de la noche", "rhythms of the night", "colonized", "coatzacoalcos", "guadalupe", "coco", "alebrije"]),
    ("korea_roots_and_family", "South Korea Roots, Parents' Home, Matrushka Doll & Year-End Work from Korea",
     ["korea", "seoul", "matrushka", "doll", "thanksgiving", "parents home", "working from anywhere"]),
    ("sports_nba_and_world_cup", "NBA (Miami Heat vs Celtics 2024, Knicks in Five), World Cup, Ballet & Boxing",
     ["knicks", "miami heat", "celtics", "spoelstra", "jalen", "playoff", "villamelon", "ballet", "boxing", "world cup"]),
    ("fashion_eyewear_and_aesthetics", "Cartier Santos Eyewear, Style Compliments & Photos",
     ["cartier", "santos", "eyewear", "glasses", "look so young", "look good", "grey mustached"]),
    ("personality_and_inner_child", "Louise Belcher (Bob's Burgers), Sarcasm vs Childlike Nature, Special Flower & Meditation",
     ["sarcastic", "childlike", "meditate", "louise", "special flower", "shiny garden", "lonely flower"]),
    ("health_and_medical_care", "Health, Endoscopy/Sedation, Dinorah & Sleep/Red-Eye Recovery",
     ["sedation", "dinorah", "red eyes", "recovery", "sleepy", "go to bed", "1 am", "endoscopy"]),
    ("gifts_and_souvenirs", "Gifts & Souvenirs Exchange (Mexico, Malaysia & Korea)",
     ["souvenir", "bringing gift", "bring one", "get my gifts", "gesture", "something from korea"]),
]


def build_complete_instagram(conn: sqlite3.Connection) -> list:
    c = conn.cursor()
    c.execute("SELECT id, timestamp, sender, text, reactions, media_desc, raw_json FROM raw_messages WHERE id BETWEEN 1 AND 746 ORDER BY id")
    b1_raw = c.fetchall()
    b1 = []
    for rid, ts, sender, txt, react, media, rj in b1_raw:
        ts_clean = ts.replace("\u202f", " ").strip()
        if 59 <= rid <= 72 and "8/22/25" in ts_clean:
            ts_clean = "Jun 5, 2026, 1:16 AM"
        b1.append({
            "platform": "Instagram",
            "channel_name": "Instagram Direct Message (@selenesng <-> @jchavezarg)",
            "channel_id": "ig_dm_119805939405917",
            "account_type": "Personal Social Account (Instagram @selenesng / @jchavezarg)",
            "thread_url": "https://www.instagram.com/direct/t/119805939405917/",
            "native_msg_id": f"ig_b1_{rid}",
            "timestamp": ts_clean,
            "sender": "Selene" if "selene" in sender.lower() else "Jesus",
            "text": txt.strip(),
            "reactions": react or "",
            "media_desc": media or "",
            "raw_json": rj or "{}",
        })

    c.execute("SELECT id, timestamp, sender, text, reactions, media_desc, raw_json FROM raw_messages WHERE id BETWEEN 1511 AND 1969 ORDER BY id")
    b2_raw = c.fetchall()
    b2 = []
    cur_ts = "Jun 15, 2026, 1:16 AM"
    for rid, ts, sender, txt, react, media, rj in b2_raw:
        t_norm = txt.replace("\u202f", " ").strip()
        if DATE_RE.match(t_norm):
            if t_norm.startswith("Tue 7:") or t_norm.startswith("Tue 8:"):
                cur_ts = "Jul 14, 2026, " + t_norm.split(" ", 1)[1]
            else:
                cur_ts = t_norm
            continue
        ts_clean = ts.replace("\u202f", " ").strip()
        if ts_clean and "Archive" not in ts_clean and ts_clean != "Instagram":
            if ts_clean.startswith("Tue 10:"):
                cur_ts = "Jul 28, 2026, " + ts_clean.split(" ", 1)[1]
            elif ts_clean.startswith("Wed "):
                cur_ts = "Jul 29, 2026, " + ts_clean.split(" ", 1)[1]
            elif "(Instagram)" in ts_clean:
                cur_ts = ts_clean.replace("(Instagram)", "").strip() + ", 8:00 PM"
            else:
                cur_ts = ts_clean
        if rid == 1684:
            cur_ts = "Jul 16, 2026, 11:31 PM"
        elif rid == 1687:
            cur_ts = "Jul 17, 2026, 12:38 AM"
        elif rid == 1705:
            cur_ts = "Jul 21, 2026, 7:15 PM"

        if b2 and norm_text(b2[-1]["text"]) == norm_text(txt) and b2[-1]["sender"] == sender:
            continue
        b2.append({
            "platform": "Instagram",
            "channel_name": "Instagram Direct Message (@selenesng <-> @jchavezarg)",
            "channel_id": "ig_dm_119805939405917",
            "account_type": "Personal Social Account (Instagram @selenesng / @jchavezarg)",
            "thread_url": "https://www.instagram.com/direct/t/119805939405917/",
            "native_msg_id": f"ig_b2_{rid}",
            "timestamp": cur_ts,
            "sender": "Selene" if "selene" in sender.lower() else "Jesus",
            "text": txt.strip(),
            "reactions": react or "",
            "media_desc": media or "",
            "raw_json": rj or "{}",
        })

    with open(ALL_LINES_PATH, "r", encoding="utf-8") as f:
        s_lines = [l.strip() for l in f.read().splitlines() if l.strip()]

    existing_norms = set()
    for m in b1 + b2:
        existing_norms.add(norm_text(m["text"]))
        for sub in m["text"].splitlines():
            if sub.strip():
                existing_norms.add(norm_text(sub))

    s_missing = []
    cur_s_ts = "May 12, 2026, 3:59 AM"
    prev_sender = "Jesus"
    for idx, line in enumerate(s_lines):
        nl = norm_text(line)
        if nl in ("Edited", "You replied to selenesng", "selenesng replied to you", "Instagram"):
            continue
        if DATE_RE.match(nl):
            if nl.startswith("Thu 12:28"):
                cur_s_ts = "Aug 27, 2026, 12:28 AM"
            else:
                cur_s_ts = nl
            continue
        if 35 <= idx <= 68:
            cur_s_ts = "Jun 15, 2026, 12:16 AM"
        elif 69 <= idx <= 105:
            cur_s_ts = "Jun 21, 2026, 11:10 PM"
        elif 106 <= idx <= 208:
            cur_s_ts = "Jul 16, 2026, 9:30 PM"
        elif 215 <= idx <= 340:
            cur_s_ts = "Jul 17, 2026, 1:00 AM"
        elif 341 <= idx <= 530:
            cur_s_ts = "Jul 21, 2026, 7:20 PM"
        elif 531 <= idx <= 695:
            cur_s_ts = "Aug 20, 2026, 8:30 PM"
        elif 696 <= idx <= 753:
            cur_s_ts = "Aug 25, 2026, 9:35 PM"
        elif 754 <= idx <= 774:
            cur_s_ts = "Aug 26, 2026, 5:45 PM"

        if nl not in existing_norms:
            sender = infer_sender_for_missing_ig_line(line, prev_sender)
            prev_sender = sender
            media_desc = ""
            if "maps.app.goo.gl" in line:
                media_desc = "Google Maps Restaurant Share (https://maps.app.goo.gl/koEF4Ta1V17aanWA7?g_st=ic)"
            elif line in ("versetheprincess", "blackcathub", "inocat_t", "ulises.bernalm"):
                media_desc = f"Instagram Reel Share (https://www.instagram.com/{line}/)"
            s_missing.append({
                "platform": "Instagram",
                "channel_name": "Instagram Direct Message (@selenesng <-> @jchavezarg)",
                "channel_id": "ig_dm_119805939405917",
                "account_type": "Personal Social Account (Instagram @selenesng / @jchavezarg)",
                "thread_url": "https://www.instagram.com/direct/t/119805939405917/",
                "native_msg_id": f"ig_sline_{idx}",
                "timestamp": cur_s_ts,
                "sender": sender,
                "text": line,
                "reactions": "",
                "media_desc": media_desc,
                "raw_json": json.dumps({"source": "selene_snapshots.json", "line_index": idx}),
            })
            existing_norms.add(nl)

    combined = b1 + b2 + s_missing
    for seq_idx, m in enumerate(combined):
        m["timestamp_utc"] = parse_to_utc_iso(m["timestamp"])
        m["_seq"] = seq_idx
    combined.sort(key=lambda x: (x["timestamp_utc"], x["_seq"]))
    return combined


def build_complete_google_chat_and_spaces(conn: sqlite3.Connection) -> list:
    c = conn.cursor()
    c.execute(
        "SELECT id, channel_name, channel_id, account_type, thread_url, native_msg_id, sender, timestamp, text, reactions, media_desc, raw_json "
        "FROM raw_messages WHERE platform = 'Google Chat' ORDER BY id ASC"
    )
    db_gchat = c.fetchall()

    gchat_items = []
    seen_dm_keys = set()
    for r in db_gchat:
        rid, ch_name, ch_id, acc_type, t_url, nat_id, sender, ts, txt, react, media, rj = r
        iso = parse_to_utc_iso(ts, fallback_iso="2026-08-21T12:00:00")
        norm_s = "Selene" if "selene" in (sender or "").lower() else "Jesus"
        dedup_key = (iso[:10], norm_s, norm_text(txt)[:100])
        if dedup_key in seen_dm_keys and rid >= 1970:
            continue
        seen_dm_keys.add(dedup_key)
        gchat_items.append({
            "platform": "Google Chat",
            "channel_name": "Google Chat 1:1 DM (selenesong@google.com <-> jesusarguelles@google.com | spaces/jeWaL0AAAAE)",
            "channel_id": "spaces/jeWaL0AAAAE",
            "account_type": "Corporate Google Workspace (selenesong@google.com / jesusarguelles@google.com)",
            "thread_url": t_url or "https://chat.google.com/dm/jeWaL0AAAAE",
            "native_msg_id": nat_id or f"gchat_db_{rid}",
            "timestamp": ts,
            "timestamp_utc": iso,
            "sender": norm_s,
            "text": (txt or "").strip(),
            "reactions": react or "",
            "media_desc": media or "",
            "raw_json": rj or "{}",
        })

    csa_files = [
        "/tmp/csa_selene_all.txt",
        "/tmp/csa_selene_chat_gaps.txt",
        "/tmp/csa_selene_spaces.txt",
        "/tmp/csa_dm_gaps2.txt",
    ]
    csa_unique = {}
    for path in csa_files:
        if not os.path.exists(path):
            continue
        with open(path, "r", encoding="utf-8") as f:
            txt = f.read()
        for s in txt.split("\n---\n"):
            if "CORPUS_CHAT" not in s:
                continue
            m_title = re.search(r"title:\s*([^,]+),\s*url:\s*([^,\s]+)", s)
            title = m_title.group(1).strip() if m_title else "Google Chat"
            url = m_title.group(2).strip() if m_title else ""
            url_parts = url.split("/")
            space_id = f"spaces/{url_parts[4]}" if len(url_parts) > 4 else "spaces/unknown"
            thread_id = url_parts[5] if len(url_parts) > 5 else ""

            msgs = re.findall(
                r"Sender:\s*([^\n]+)\nTime:\s*([^\n]+)\nText:\s*(.*?)(?=\n\[(?:Read|Unread) Message\]|\Z)",
                s,
                re.S,
            )
            for sender_raw, ts_raw, text_raw in msgs:
                text_clean = re.sub(
                    r"\n=== CSA Response ===.*|\nSending request to CSA.*",
                    "",
                    text_raw,
                    flags=re.S,
                ).strip()
                # Strip CSA trailing URL footers
                text_clean = re.sub(r"\s*(?:\]\s*)?URL from (?:Chat|Email):\s*https?://\S+.*$", "", text_clean, flags=re.S).strip()
                if not text_clean:
                    continue
                ts_clean = ts_raw.strip()
                iso = parse_to_utc_iso(ts_clean)
                s_low = sender_raw.lower()
                if "selene" in s_low:
                    norm_s = "Selene"
                elif "jesus" in s_low:
                    norm_s = "Jesus"
                else:
                    norm_s = sender_raw.split("<")[0].strip() or sender_raw.strip()

                key = (space_id, iso, norm_s, norm_text(text_clean)[:120])
                csa_unique[key] = {
                    "space_title": title,
                    "space_id": space_id,
                    "thread_id": thread_id,
                    "url": url,
                    "sender": norm_s,
                    "sender_raw": sender_raw.strip(),
                    "timestamp": ts_clean,
                    "timestamp_utc": iso,
                    "text": text_clean,
                }

    added_dm = 0
    added_spaces = 0
    for key, m in sorted(csa_unique.items(), key=lambda x: x[1]["timestamp_utc"]):
        dedup_key = (m["timestamp_utc"][:10], m["sender"], norm_text(m["text"])[:100])
        if m["space_id"] == "spaces/jeWaL0AAAAE":
            if dedup_key in seen_dm_keys:
                continue
            seen_dm_keys.add(dedup_key)
            gchat_items.append({
                "platform": "Google Chat",
                "channel_name": f"Google Chat 1:1 DM (selenesong@google.com <-> jesusarguelles@google.com | {m['space_id']} / thread {m['thread_id']})",
                "channel_id": m["space_id"],
                "account_type": "Corporate Google Workspace (selenesong@google.com / jesusarguelles@google.com)",
                "thread_url": m["url"],
                "native_msg_id": f"{m['space_id']}/threads/{m['thread_id']}_{m['timestamp_utc']}",
                "timestamp": m["timestamp"],
                "timestamp_utc": m["timestamp_utc"],
                "sender": m["sender"],
                "text": m["text"],
                "reactions": "",
                "media_desc": "",
                "raw_json": json.dumps(m),
            })
            added_dm += 1
        else:
            gchat_items.append({
                "platform": "Google Chat Space",
                "channel_name": f"Google Chat Space: {m['space_title']} ({m['space_id']} / thread {m['thread_id']})",
                "channel_id": m["space_id"],
                "account_type": "Corporate Google Workspace Shared Space / Thread",
                "thread_url": m["url"],
                "native_msg_id": f"{m['space_id']}/threads/{m['thread_id']}_{m['timestamp_utc']}",
                "timestamp": m["timestamp"],
                "timestamp_utc": m["timestamp_utc"],
                "sender": m["sender"],
                "text": m["text"],
                "reactions": "",
                "media_desc": f"Space: {m['space_title']} | Sender: {m['sender_raw']}",
                "raw_json": json.dumps(m),
            })
            added_spaces += 1

    print(f"Google Chat 1:1 DM new CSA msgs added: {added_dm} | Shared Space msgs added: {added_spaces}")
    return gchat_items


def build_workspace_docs_and_gmail() -> list:
    items = []
    if os.path.exists("/tmp/gmail_selene_full.json"):
        with open("/tmp/gmail_selene_full.json", "r", encoding="utf-8") as f:
            gmails = json.load(f)
        for g in gmails:
            mid = g["id"]
            raw = g["raw"]
            subj_m = re.search(r"^Subject:\s*(.+)$", raw, re.M)
            from_m = re.search(r"^From:\s*(.+)$", raw, re.M)
            date_m = re.search(r"^Date:\s*(.+)$", raw, re.M)
            subj = subj_m.group(1).strip() if subj_m else "Gmail Message"
            frm = from_m.group(1).strip() if from_m else "Unknown"
            dt_str = date_m.group(1).strip() if date_m else "2026-08-26"
            if "415051610" in subj:
                continue
            body = raw.split("\n---\n", 1)[1].strip() if "\n---\n" in raw else raw.strip()
            try:
                dt_obj = parsedate_to_datetime(dt_str)
                edt_tz = timezone(timedelta(hours=-4))
                iso = dt_obj.astimezone(edt_tz).replace(tzinfo=None).strftime("%Y-%m-%dT%H:%M:%S")
            except Exception:
                iso = parse_to_utc_iso(dt_str)

            sender = "Selene" if "selene" in frm.lower() else ("Jesus" if "jesus" in frm.lower() else frm.split("<")[0].strip())
            items.append({
                "platform": "Google Workspace",
                "channel_name": f"Gmail / Workspace Notification: {subj[:80]}",
                "channel_id": f"gmail_{mid}",
                "account_type": "Corporate Google Workspace (Gmail / Calendar / Docs)",
                "thread_url": f"https://mail.google.com/mail/u/0/#all/{mid}",
                "native_msg_id": f"gmail_{mid}",
                "timestamp": iso.replace("T", " "),
                "timestamp_utc": iso,
                "sender": sender,
                "text": f"[Gmail: {subj}]\n{body[:1200]}",
                "reactions": "",
                "media_desc": f"From: {frm}",
                "raw_json": json.dumps({"gmail_id": mid, "subject": subj, "from": frm, "date": dt_str}),
            })

    if os.path.exists("/tmp/gdocs_selene_all.json"):
        with open("/tmp/gdocs_selene_all.json", "r", encoding="utf-8") as f:
            gdocs = json.load(f)
        doc_meta = {
            "1DPMkvCrwSwDOvAFMYAPL6W3kR9i256nKwJ2Q3M1yGJ0": ("2024-04-23T12:17:57", "Selene", "Notes - Jesus / Selene (Vertex AI Pipelines & Onboarding Doc)"),
            "1IRS3Ay__H3LYwrs7p7O-9_Rmg6unVdhqEHxRwj-Ro7U": ("2025-06-13T11:25:09", "Jesus", "from gem2.0 > gem2.5 (Gemini 2.0 to 2.5 Customer Migration Guide shared with Selene)"),
            "1AWXkI1VQZL38uiIfhv70E27TYdRc7EdA9QMpxBAulF8": ("2026-07-23T09:53:20", "Jesus", "Jira as MCP Datastore for GE (Atlassian Remote MCP DCR & OAuth 2.1 Setup Guide shared with Selene)"),
            "1A2zRaZcMQw4gI3nTGZgYzhzOBtByS1hP9qhqbzF7Pj0": ("2026-08-26T13:10:34", "Jesus", "Google Meet Transcript: oue-drmk-nox (Jesus Chavez & Selene Song — Gemini Enterprise Canvas EAP)"),
            "1OjgTb1dy3FRmSg7SWkPp7wTjQqnf4fQSeAxyRtumfd4": ("2026-08-26T16:26:45", "Selene", "Cat food recommendation ('Choosing Cat Food' Google Doc shared by Selene Song)"),
        }
        for did, dinfo in gdocs.items():
            iso, sender, desc = doc_meta.get(did, ("2026-08-26T12:00:00", "Selene", dinfo["title"]))
            body = dinfo.get("body", "").strip()
            items.append({
                "platform": "Google Docs",
                "channel_name": f"Google Docs Shared Document: {desc}",
                "channel_id": f"gdoc_{did}",
                "account_type": "Corporate Google Workspace (Google Drive / Docs)",
                "thread_url": f"https://docs.google.com/document/d/{did}/edit",
                "native_msg_id": f"gdoc_{did}",
                "timestamp": iso.replace("T", " "),
                "timestamp_utc": iso,
                "sender": sender,
                "text": f"[Shared Google Doc: {desc}]\n{body}",
                "reactions": "",
                "media_desc": f"Google Doc ID: {did}",
                "raw_json": json.dumps({"doc_id": did, "title": desc}),
            })
    return items


def sync_calendars_to_db(conn: sqlite3.Connection):
    c = conn.cursor()
    cal_files = [
        ("/tmp/cal_jesus.json", "jesusarguelles@google.com"),
        ("/tmp/cal_jesus_2.json", "jesusarguelles@google.com"),
        ("/tmp/cal_selene.json", "selenesong@google.com"),
        ("/tmp/cal_selene_2.json", "selenesong@google.com"),
    ]
    ins_total = 0
    upd_total = 0
    for fpath, owner in cal_files:
        if not os.path.exists(fpath):
            continue
        with open(fpath, "r", encoding="utf-8") as f:
            data = json.load(f)
        events = data if isinstance(data, list) else data.get("items", data.get("events", []))
        for e in events:
            eid = e.get("id")
            if not eid:
                continue
            summary = e.get("summary", "") or ""
            start = e.get("start", {}).get("dateTime") or e.get("start", {}).get("date") or ""
            end = e.get("end", {}).get("dateTime") or e.get("end", {}).get("date") or ""
            loc = e.get("location", "") or ""
            desc = e.get("description", "") or ""
            status = e.get("status", "confirmed") or ""
            rj = json.dumps(e, ensure_ascii=False)
            c.execute("SELECT event_id FROM calendar_events WHERE event_id = ?", (eid,))
            if c.fetchone():
                c.execute(
                    "UPDATE calendar_events SET owner_calendar=?, summary=?, start_time=?, end_time=?, location=?, description=?, status=?, raw_json=? WHERE event_id=?",
                    (owner, summary, start, end, loc, desc, status, rj, eid),
                )
                upd_total += 1
            else:
                c.execute(
                    "INSERT INTO calendar_events VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (eid, owner, summary, start, end, loc, desc, status, rj),
                )
                ins_total += 1
    c.execute("DELETE FROM calendar_fts")
    c.execute(
        "INSERT INTO calendar_fts (event_id, owner_calendar, summary, location, description) "
        "SELECT event_id, owner_calendar, summary, location, description FROM calendar_events"
    )
    conn.commit()
    total_cal = c.execute("SELECT COUNT(*) FROM calendar_events").fetchone()[0]
    print(f"Calendar synced: +{ins_total} new, {upd_total} updated -> {total_cal} total events through Jan 2027.")


def main():
    if not os.path.exists(BACKUP_PATH):
        shutil.copy2(DB_PATH, BACKUP_PATH)
        print(f"Backed up original DB to {BACKUP_PATH}")

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    ig = build_complete_instagram(conn)
    gchat = build_complete_google_chat_and_spaces(conn)
    ws = build_workspace_docs_and_gmail()

    all_items = ig + gchat + ws
    for i, it in enumerate(all_items):
        it["_seq"] = i
    all_items.sort(key=lambda x: (x["timestamp_utc"], x["_seq"]))

    # Recreate raw_messages with timestamp_utc and strict chronological ordering
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
            timestamp_utc TEXT,
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

    plat_counters = {}
    prev_sender = ""
    consec_count = 0

    for item in all_items:
        plat = item["platform"]
        plat_counters[plat] = plat_counters.get(plat, 0) + 1
        p_idx = plat_counters[plat]

        if item["sender"] == prev_sender:
            consec_count += 1
        else:
            consec_count = 1
            prev_sender = item["sender"]

        analysis = analyze_sentiment_and_models(item["sender"], item["text"], prev_sender, consec_count)
        t_low = item["text"].lower()
        matched_topics = [
            t_id for t_id, t_title, kw_list in TOPIC_DEFINITIONS
            if any(kw in t_low for kw in kw_list)
        ]

        c.execute(
            """
            INSERT INTO raw_messages (
                platform, platform_msg_index, channel_name, channel_id, account_type,
                thread_url, native_msg_id, sender, timestamp, timestamp_utc, text, reactions, media_desc,
                sentiment_label, sentiment_score, models_positives, models_flaws,
                models_net_rating, models_coaching_note, linked_topics, raw_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                plat,
                p_idx,
                item["channel_name"],
                item["channel_id"],
                item["account_type"],
                item["thread_url"],
                item["native_msg_id"],
                item["sender"],
                item["timestamp"],
                item["timestamp_utc"],
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
                item["raw_json"],
            ),
        )

    c.execute(
        """
        CREATE VIRTUAL TABLE raw_messages_fts USING fts5(
            platform, sender, text, reactions, media_desc, models_net_rating, linked_topics,
            content='raw_messages', content_rowid='id'
        )
        """
    )
    c.execute("INSERT INTO raw_messages_fts(raw_messages_fts) VALUES('rebuild')")

    # Update dossier with all 5 full Google Docs + October 2026 timeline section
    if os.path.exists("/tmp/gdocs_selene_all.json"):
        with open("/tmp/gdocs_selene_all.json", "r", encoding="utf-8") as f:
            gdocs = json.load(f)
        for did, dinfo in gdocs.items():
            c.execute(
                "INSERT OR REPLACE INTO dossier (section_id, title, content) VALUES (?, ?, ?)",
                (f"gdoc_{did[:12]}", f"Shared Google Doc: {dinfo['title']}", dinfo.get("body", "")),
            )

    oct_summary = (
        "## 📅 8. SEPTEMBER – OCTOBER 2026 UPDATE (MALAYSIA RETURN, OCT 2 NYC OFFICE LUNCH, SHARED CALENDAR & GEMINI 4 ARGON)\n"
        "- **Sep 25–27, 2026 (`AI GTM Tech - All Team` Space `spaces/AAQAlvoeMDA`)**: Srini Ranganna announced `[🎉Intel Malaysia AI Roadshow🎉]`, highlighting Selene Song's Composite Yield Optimization Agent demo for Intel CIO Cindy Stoddard in front of 5,000 employees across 15 sessions. Jesus Chavez publicly praised Selene (`\"Huge impact @Selene Song...\"`), and Selene replied directly (`\"Thank you Jesus!!\"`).\n"
        "- **Oct 1, 2026 (`spaces/jeWaL0AAAAE`)**: Selene returned from Malaysia (`\"Back to reality!\"`) and immediately coordinated an in-person NYC office lunch with Jesus for Friday, Oct 2 (`\"Lunch at office\"` calendar invite).\n"
        "- **Oct 2, 2026 (`spaces/AAQAkK_HhYs` `'Lunch at office - Oct 2'`)**: Jesus and Selene met in person at the NYC Google office (coordinating between the 4th floor, 9th floor cafe, and Pier 57).\n"
        "- **Oct 5–6, 2026 (`spaces/jeWaL0AAAAE` & `Gmail`)**: Jesus shared his Google Calendar (`jesusarguelles@google.com`) with Selene. They discussed the `Hola` Hispanic heritage celebration (mariachi band), and Selene shared that she is considering **moving apartments next year** and wants a building with a **sauna**.\n"
        "- **Oct 7–9, 2026 (`spaces/AAAALJmrcaY` `[Helpdesk] AGY for Enterprise` & `spaces/jeWaL0AAAAE`)**: Selene investigated 3P model licensing (Claude Opus/Sonnet in Antigravity/GE) in the Helpdesk space and DM'd Jesus (`\"Hi Jesus\"`) to discuss Gemini rebranding, Jetski (`\"connect me jetski to my veins\"`), and the **Gemini 4 (Argon)** launch date (`Oct 13th ! Gemini 4`, `b/565407631`)."
    )
    c.execute(
        "INSERT OR REPLACE INTO dossier (section_id, title, content) VALUES (?, ?, ?)",
        ("october_2026_master_update", "📅 8. SEPTEMBER – OCTOBER 2026 MASTER UPDATE", oct_summary),
    )

    # Rebuild 20-Topic Temporal & Cross-Space Knowledge Graph
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
            "SELECT id, platform, channel_name, timestamp_utc, sender, text FROM raw_messages WHERE linked_topics LIKE ? ORDER BY id ASC",
            (f'%"{t_id}"%',),
        )
        mentions = c.fetchall()
        if not mentions:
            continue
        platforms = sorted(list({m[1] for m in mentions}))
        first_ts = mentions[0][3]
        last_ts = mentions[-1][3]
        key_milestones = [
            {"msg_id": m[0], "platform": m[1], "channel": m[2], "timestamp": m[3], "sender": m[4], "text": m[5][:140]}
            for m in mentions
        ]
        c.execute(
            "INSERT INTO topic_graph_nodes VALUES (?, ?, ?, ?, ?, ?, ?)",
            (t_id, t_title, len(mentions), ", ".join(platforms), first_ts, last_ts, json.dumps(key_milestones)),
        )
        for i in range(len(mentions) - 1):
            m1, m2 = mentions[i], mentions[i + 1]
            cross = 1 if (m1[1] != m2[1] or m1[2] != m2[2]) else 0
            rel = "CROSS_PLATFORM_OR_SPACE_HOP" if cross else "TEMPORAL_CALLBACK"
            c.execute(
                """
                INSERT INTO topic_graph_edges (
                    topic_id, topic_title, from_msg_id, to_msg_id,
                    from_platform, to_platform, from_timestamp, to_timestamp,
                    cross_platform_hop, relationship_type
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (t_id, t_title, m1[0], m2[0], m1[1], m2[1], m1[3], m2[3], cross, rel),
            )

    conn.commit()
    sync_calendars_to_db(conn)

    # Rebuild 3072-dim gemini-embedding-001 vector index across all platforms
    from build_vector_index import build_chunks, embed_and_store
    # Also include 'Google Chat Space', 'Google Workspace', 'Google Docs' in chunking!
    c.execute("DELETE FROM conversation_vectors")
    conn.commit()

    chunks = []
    for platform in ["Instagram", "Google Chat", "Google Chat Space", "Google Workspace", "Google Docs"]:
        c.execute(
            """
            SELECT id, platform, channel_name, channel_id, account_type, thread_url, sender, timestamp_utc, text, reactions, media_desc
            FROM raw_messages
            WHERE platform = ?
            ORDER BY id ASC
            """,
            (platform,),
        )
        rows = c.fetchall()
        window_size = 8 if platform in ("Instagram", "Google Chat") else 4
        stride = 4 if platform in ("Instagram", "Google Chat") else 2
        for i in range(0, len(rows), stride):
            window = rows[i : i + window_size]
            if not window:
                break
            first, last = window[0], window[-1]
            lines = [f"[Platform: {first[1]} | Channel: {first[2]} | Space/Thread ID: {first[3]}]"]
            for r in window:
                msg_id, plat_n, ch_name, ch_id, acc_type, url, sender, ts, txt, react, media = r
                lines.append(f"[{msg_id}] ({ts}) {sender}: {txt[:600]}")
            chunks.append({
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
                "chunk_text": "\n".join(lines),
            })

    # Add Meet transcripts & Dossier sections
    c.execute("SELECT section_id, title, content FROM dossier WHERE section_id != 'full_dossier'")
    for sec_id, title, content in c.fetchall():
        chunks.append({
            "source_type": "dossier",
            "platform": "Grounding Dossier",
            "channel_name": f"Master Grounding Dossier — {title}",
            "channel_id": sec_id,
            "account_type": "Synthesized Ground Truth Dossier",
            "thread_url": "",
            "start_msg_id": 0,
            "end_msg_id": 0,
            "start_timestamp": "2024-04-23",
            "end_timestamp": "2026-10-09",
            "participants": "Jesus Chavez, Selene Song",
            "chunk_text": f"[Platform: Grounding Dossier | Section: {title}]\n{content[:3000]}",
        })

    print(f"Embedding {len(chunks)} semantic windows with {EMBED_MODEL}...")
    embed_and_store(conn, chunks)

    total_msgs = c.execute("SELECT COUNT(*) FROM raw_messages").fetchone()[0]
    total_nodes = c.execute("SELECT COUNT(*) FROM topic_graph_nodes").fetchone()[0]
    total_edges = c.execute("SELECT COUNT(*) FROM topic_graph_edges").fetchone()[0]
    total_vecs = c.execute("SELECT COUNT(*) FROM conversation_vectors").fetchone()[0]
    conn.close()
    print(f"=== SUPERMEMORY REBUILD COMPLETE ===")
    print(f"  raw_messages         : {total_msgs}")
    print(f"  topic_graph_nodes    : {total_nodes}")
    print(f"  topic_graph_edges    : {total_edges}")
    print(f"  conversation_vectors : {total_vecs}")


if __name__ == "__main__":
    main()
