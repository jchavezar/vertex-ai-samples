"""Phase 1c: Build golden/golden_super.json — one entry per question.

Schema:
  {qid: {
    "id": str,
    "intent": str,
    "category": str,
    "expected_keys": [...],
    "facts": {key: {...}},
    "required_facts": [paths into facts[key]],
    "forbidden_substrings": [...],
    "absolute_jql": str | null,
    "extracted_at": ISO timestamp
  }}
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path

EVAL_DIR = Path(__file__).resolve().parent.parent
TODAY = datetime(2026, 5, 21, tzinfo=timezone.utc)

JIRA_KEY_RE = re.compile(r"\b[A-Z]{2,8}-\d+\b")

# Field name → fact path (in cached struct)
FIELD_PATHS = {
    "assignee": "assignee.displayName",
    "assigned": "assignee.displayName",
    "owner": "assignee.displayName",
    "owns": "assignee.displayName",
    "assigne": "assignee.displayName",
    "working on": "assignee.displayName",
    "responsible for": "assignee.displayName",
    "reporter": "reporter.displayName",
    "reported": "reporter.displayName",
    "status": "status",
    "priority": "priority",
    "summary": "summary",
    "type": "issuetype",
    "issuetype": "issuetype",
    "issue type": "issuetype",
    "parent": "parent",
    "belong": "parent",
    "epic": "epic_link",
    "components": "components",
    "component": "components",
    "labels": "labels",
    "label": "labels",
    "fix version": "fixVersions",
    "fixversion": "fixVersions",
    "created": "created",
    "updated": "updated",
    "resolved": "resolution_date",
    "resolution": "resolution_date",
    "due date": "duedate",
    "duedate": "duedate",
    "blocks": "linked_issues",
    "blocked": "linked_issues",
    "relate": "linked_issues",
    "linked": "linked_issues",
    "dependency": "linked_issues",
    "depends": "linked_issues",
}

# For time_relative — map common phrases to JQL date arithmetic
# Today = 2026-05-21
def expand_time_jql(jql: str) -> str:
    """Expand JQL relative date arithmetic ('-7d', '-1w') against TODAY for
    a snapshot semantics. Leaves absolute dates alone."""
    if not jql:
        return jql
    # Pattern: -<n><unit> — replace with absolute date
    def _sub(m):
        n = int(m.group(1))
        unit = m.group(2).lower()
        delta = {
            "d": timedelta(days=n),
            "w": timedelta(weeks=n),
            "m": timedelta(days=30 * n),
            "y": timedelta(days=365 * n),
        }.get(unit, timedelta(days=n))
        dt = TODAY - delta
        return f'"{dt.strftime("%Y-%m-%d")}"'
    return re.sub(r"-(\d+)([dwmy])", _sub, jql)


def infer_required_facts(qtext: str, intent: str) -> list[str]:
    """Pick fact-paths from the question text. Returns list like ['assignee.displayName']."""
    if intent != "field_value_lookup":
        return []
    qlow = qtext.lower()
    found = []
    # Greedy keyword match
    for kw, path in FIELD_PATHS.items():
        if re.search(rf"\b{re.escape(kw)}\b", qlow):
            if path not in found:
                found.append(path)
    # Special: generic lookup verbs → summary fallback if nothing else matched
    if not found and re.search(r"\b(show|give|get|fetch|tell me about|describe|find|look up|lookup|pull up|pull|details|details on|what is|what's happening with|happening with)\b", qlow):
        found.append("summary")
    return found


def main():
    qs = json.load(open(EVAL_DIR / "questions/main.json"))
    intents = json.load(open(EVAL_DIR / "golden/intents.json"))
    facts_cache = json.load(open(EVAL_DIR / "golden/facts_cache.json"))
    per_qid_keys = json.load(open(EVAL_DIR / "golden/per_qid_keys.json"))

    extracted_at = datetime.now(timezone.utc).isoformat()
    out: dict[str, dict] = {}

    # Stats
    stat_intent_counts = {}
    stat_with_required = 0
    stat_with_facts = 0

    for q in qs:
        qid = q["id"]
        intent = (intents.get(qid) or {}).get("intent", "analytical")
        cat = q.get("category", "")
        keys = per_qid_keys.get(qid, [])

        facts = {}
        for k in keys:
            if k in facts_cache:
                facts[k] = facts_cache[k]

        required = infer_required_facts(q["q"], intent)

        # Build absolute_jql for time_relative
        absolute_jql = None
        if intent == "time_relative_count":
            jql = q.get("jql") or ""
            absolute_jql = expand_time_jql(jql) if jql else None

        entry = {
            "id": qid,
            "intent": intent,
            "category": cat,
            "question": q["q"],
            "expected_keys": q.get("expected_keys", []),
            "expected_count": q.get("expected_count"),
            "jql": q.get("jql"),
            "absolute_jql": absolute_jql,
            "facts": facts,
            "required_facts": required,
            "forbidden_substrings": [],
            "themes": q.get("expected_themes", []),
            "extracted_at": extracted_at,
        }
        out[qid] = entry

        stat_intent_counts[intent] = stat_intent_counts.get(intent, 0) + 1
        if required:
            stat_with_required += 1
        if facts:
            stat_with_facts += 1

    out_path = EVAL_DIR / "golden/golden_super.json"
    out_path.write_text(json.dumps(out, indent=2))
    print(f"Wrote {out_path} ({len(out)} questions)")
    print(f"Intent distribution: {stat_intent_counts}")
    print(f"Questions with required_facts: {stat_with_required}")
    print(f"Questions with at least 1 fact loaded: {stat_with_facts}")


if __name__ == "__main__":
    main()
