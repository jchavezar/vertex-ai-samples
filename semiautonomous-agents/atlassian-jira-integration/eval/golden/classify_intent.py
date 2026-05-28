"""Phase 1a: Classify each question into one of 6 intent buckets.

Intents:
  - field_value_lookup   : asks for a specific field value of a specific issue
  - count_or_groupby     : asks how many or wants a grouped breakdown
  - time_relative_count  : count over a relative time window ("last 7 days")
  - key_recall           : "list/show/find all matching X" — set of keys
  - analytical           : everything analytical that doesn't fit above
  - safety               : refusal-test, prompt-injection, pii-sensitive, ambiguous

Writes golden/intents.json keyed by qid.
"""
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

EVAL_DIR = Path(__file__).resolve().parent.parent

SAFETY_CATS = {"refusal-test", "prompt-injection", "pii-sensitive", "ambiguous"}

# Regex patterns (case-insensitive) — priority order matters
FIELD_VALUE_PATS = [
    re.compile(r"\b(who|whom)\b.{0,20}\b(assigned|owns?|reporter|reported|assignee|owner|created|reviewer)\b", re.I),
    re.compile(r"\b(assigned to|reporter of|assignee for|owner of)\b", re.I),
    re.compile(r"\b(what|what's|which|whats)\b.{0,30}\b(priority|status|due ?date|resolution|assignee|reporter|summary|type|component|label|fix ?version|description|parent|epic)\b.{0,30}\b(of|for|is|are|on)\b", re.I),
    re.compile(r"\b(priority|status|assignee|reporter|due ?date|resolution date|summary|description|type|fix version|parent|epic)\s+(of|for|is)\b", re.I),
    re.compile(r"\b(show|tell|give|fetch)\s+(me|us)?\s*(the\s+)?(assignee|priority|status|reporter|summary|description|due date|resolution|parent|epic|owner)\b", re.I),
    re.compile(r"\bwhen (was|is)\b.{0,20}\b(created|resolved|updated|closed|opened)\b", re.I),
    re.compile(r"\bcan you tell me\b.{0,30}\b(summary|assignee|priority|status|reporter|description|parent|owner)\b", re.I),
]

TIME_RELATIVE_PATS = [
    re.compile(r"\b(last|past)\s+\d+\s*(day|week|month|hour|min)s?\b", re.I),
    re.compile(r"\bin the (last|past)\s+(\d+\s+)?(day|week|month|year|hour)s?\b", re.I),
    re.compile(r"\b(this|next|previous)\s+(week|month|sprint|quarter|year)\b", re.I),
    re.compile(r"\b(yesterday|today|tomorrow)\b", re.I),
    re.compile(r"\brecently\b", re.I),
]

COUNT_PATS = [
    re.compile(r"\b(how many|count(?:\s+of)?|total (?:number|count)|number of)\b", re.I),
    re.compile(r"\b(group(ed)? by|breakdown|distribution)\b", re.I),
    re.compile(r"\b(per project|per priority|per status|per component|per type|per assignee|per reporter)\b", re.I),
]

KEY_RECALL_PATS = [
    re.compile(r"\b(list|show me|find|give me|fetch)\s+(all|every|each)\b", re.I),
    re.compile(r"\b(all|every)\s+(open|closed|active|resolved|unresolved|in progress)\s+(issue|bug|task|story)s?\b", re.I),
    re.compile(r"\bwhich\s+(issues?|bugs?|tasks?|stories|tickets?)\b.{0,30}\b(are|match|exist|have)\b", re.I),
]

JIRA_KEY_RE = re.compile(r"\b[A-Z]{2,8}-\d+\b")


def classify_one(q: dict) -> dict:
    qid = q["id"]
    cat = q.get("category", "")
    qtext = q["q"]

    # Safety categories first
    if cat in SAFETY_CATS:
        return {"id": qid, "intent": "safety", "subcategory": cat, "reason": f"safety category={cat}"}

    # field_value_lookup — must reference a specific key OR have expected_keys length 1
    has_key = bool(JIRA_KEY_RE.search(qtext)) or len(q.get("expected_keys", [])) == 1
    if has_key:
        for pat in FIELD_VALUE_PATS:
            if pat.search(qtext):
                return {"id": qid, "intent": "field_value_lookup", "reason": f"matches '{pat.pattern[:60]}' + has key"}

    # time_relative_count
    has_time_rel = any(p.search(qtext) for p in TIME_RELATIVE_PATS)
    has_count = any(p.search(qtext) for p in COUNT_PATS)
    if has_time_rel and (has_count or "trend" in qtext.lower()):
        return {"id": qid, "intent": "time_relative_count", "reason": "time-relative + count/trend"}

    # count_or_groupby
    if has_count:
        return {"id": qid, "intent": "count_or_groupby", "reason": "count/groupby pattern"}

    # key_recall
    for pat in KEY_RECALL_PATS:
        if pat.search(qtext):
            return {"id": qid, "intent": "key_recall", "reason": f"key_recall pattern"}

    # Lookup category with JQL oracle, no key in text → small set retrieval
    if q.get("oracle") == "jql" and q.get("expected_keys"):
        if len(q["expected_keys"]) == 1:
            return {"id": qid, "intent": "field_value_lookup", "reason": "jql oracle, single expected key"}
        return {"id": qid, "intent": "key_recall", "reason": "jql oracle, multi expected key"}

    # Default: analytical
    return {"id": qid, "intent": "analytical", "reason": "no specific intent pattern matched"}


def main():
    qs = json.load(open(EVAL_DIR / "questions/main.json"))
    out = {}
    for q in qs:
        c = classify_one(q)
        out[q["id"]] = c

    by_intent = Counter(v["intent"] for v in out.values())
    print(f"Total: {len(out)}")
    for intent, n in by_intent.most_common():
        print(f"  {intent}: {n} ({n/len(out)*100:.1f}%)")

    out_path = EVAL_DIR / "golden/intents.json"
    out_path.write_text(json.dumps(out, indent=2))
    print(f"\nWrote {out_path}")


if __name__ == "__main__":
    main()
