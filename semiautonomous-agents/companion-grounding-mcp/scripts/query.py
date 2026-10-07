import sys
import json
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from server import (
    semantic_search_conversations,
    search_interactions,
    analyze_models_performance,
    trace_topic_graph,
    search_past_advice,
    get_meet_transcripts,
    get_grounding_dossier,
    get_recent_context,
    verify_draft_tone,
    get_calendar_schedule,
    get_upcoming_trips,
    find_co_location_days,
)

def print_help():
    print("""
Usage:
  python3 scripts/query.py semantic <query> [platform]
  python3 scripts/query.py raw <query> [platform]
  python3 scripts/query.py models [flaws|positives|all] [platform]
  python3 scripts/query.py graph [topic]
  python3 scripts/query.py advice <query>
  python3 scripts/query.py meet [query]
  python3 scripts/query.py dossier [section]
  python3 scripts/query.py recent [count]
  python3 scripts/query.py check <draft_message>
  python3 scripts/query.py calendar [jesus|selene|both] [YYYY-MM-DD]
  python3 scripts/query.py trips
  python3 scripts/query.py colocate
""")

def main():
    if len(sys.argv) < 2:
        print_help()
        return

    cmd = sys.argv[1].lower()
    
    if cmd == "semantic":
        q = sys.argv[2] if len(sys.argv) > 2 else ""
        platform = sys.argv[3] if len(sys.argv) > 3 else ""
        print(semantic_search_conversations(q, platform=platform))
    elif cmd == "raw":
        q = sys.argv[2] if len(sys.argv) > 2 else ""
        platform = sys.argv[3] if len(sys.argv) > 3 else ""
        print(search_interactions(q, platform=platform))
    elif cmd == "models":
        flt = sys.argv[2] if len(sys.argv) > 2 else "all"
        platform = sys.argv[3] if len(sys.argv) > 3 else ""
        print(analyze_models_performance(filter_type=flt, platform=platform))
    elif cmd == "graph":
        topic = sys.argv[2] if len(sys.argv) > 2 else ""
        print(trace_topic_graph(topic=topic))
    elif cmd == "advice":
        q = sys.argv[2] if len(sys.argv) > 2 else ""
        print(search_past_advice(q))
    elif cmd == "meet":
        q = sys.argv[2] if len(sys.argv) > 2 else ""
        print(get_meet_transcripts(q))
    elif cmd == "dossier":
        sec = sys.argv[2] if len(sys.argv) > 2 else "full_dossier"
        print(get_grounding_dossier(sec))
    elif cmd == "recent":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 15
        print(get_recent_context(limit))
    elif cmd == "check":
        draft = " ".join(sys.argv[2:])
        print(verify_draft_tone(draft))
    elif cmd == "calendar":
        person = sys.argv[2] if len(sys.argv) > 2 else "both"
        date = sys.argv[3] if len(sys.argv) > 3 else ""
        print(get_calendar_schedule(person=person, date=date))
    elif cmd == "trips":
        print(get_upcoming_trips())
    elif cmd == "colocate":
        print(find_co_location_days())
    else:
        print_help()

if __name__ == "__main__":
    main()
