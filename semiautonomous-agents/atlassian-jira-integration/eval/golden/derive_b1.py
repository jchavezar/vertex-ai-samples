"""Phase 2A: Derive ground-truth answers for Bucket 1 (Jira-derivable) questions.

For each B1 question, query Jira REST + build:
  - golden_facts: dict of verifiable facts (counts, key lists, parent keys, time values)
  - golden_answer: prose reference answer the judge can compare against

Writes eval/golden/golden_b1.json — keyed by question id.

No LLM calls. Pure Python + Jira REST.
"""
from __future__ import annotations

import base64
import json
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path

import requests

EVAL_DIR = Path(__file__).resolve().parent.parent

# Load .env
for line in (EVAL_DIR / ".env").read_text().splitlines():
    line = line.strip()
    if not line or line.startswith("#") or "=" not in line:
        continue
    k, v = line.split("=", 1)
    os.environ[k.strip()] = v.strip()

SITE = os.environ["ATLASSIAN_SITE_URL"].rstrip("/")
EMAIL = os.environ["ATLASSIAN_EMAIL"]
TOKEN = os.environ["ATLASSIAN_API_TOKEN"]
_AUTH = base64.b64encode(f"{EMAIL}:{TOKEN}".encode()).decode()
HDR = {"Authorization": f"Basic {_AUTH}", "Accept": "application/json"}


# --- Helpers ----------------------------------------------------------------

def jql_search(jql: str, fields=("summary", "status", "priority", "issuetype",
                                  "created", "parent", "components",
                                  "customfield_10014", "subtasks"),
               max_pages: int = 20) -> list[dict]:
    """Run a JQL search, paginate, return all issues."""
    out = []
    nxt = ""
    for _ in range(max_pages):
        params = {"jql": jql, "fields": ",".join(fields), "maxResults": 100}
        if nxt:
            params["nextPageToken"] = nxt
        r = requests.get(f"{SITE}/rest/api/3/search/jql", headers=HDR, params=params, timeout=30)
        if r.status_code != 200:
            return out  # silent fail, return what we have
        body = r.json()
        out.extend(body.get("issues", []))
        nxt = body.get("nextPageToken")
        if not nxt:
            break
    return out


def get_issue(key: str, fields=("summary", "status", "priority", "issuetype",
                                "parent", "subtasks", "customfield_10014",
                                "components", "labels", "issuelinks", "created")) -> dict | None:
    r = requests.get(f"{SITE}/rest/api/3/issue/{key}", headers=HDR,
                     params={"fields": ",".join(fields)}, timeout=30)
    if r.status_code == 200:
        return r.json()
    return None


def get_comments(key: str) -> list[dict]:
    r = requests.get(f"{SITE}/rest/api/3/issue/{key}/comment", headers=HDR, timeout=30)
    if r.status_code == 200:
        return r.json().get("comments", [])
    return []


def get_worklogs(key: str) -> list[dict]:
    r = requests.get(f"{SITE}/rest/api/3/issue/{key}/worklog", headers=HDR, timeout=30)
    if r.status_code == 200:
        return r.json().get("worklogs", [])
    return []


def adf_to_text(adf) -> str:
    """Best-effort ADF → text for comment bodies."""
    if isinstance(adf, str):
        return adf
    if not isinstance(adf, dict):
        return ""
    out_parts = []
    for content in adf.get("content", []) or []:
        if isinstance(content, dict):
            if content.get("type") == "text":
                out_parts.append(content.get("text", ""))
            else:
                out_parts.append(adf_to_text(content))
    return " ".join(out_parts).strip()


def extract_issue_key(qtext: str) -> str | None:
    """Find a single Jira key (e.g. BUGS-100, CRM-85) in the question text."""
    m = re.search(r"\b([A-Z]{2,8}-\d+)\b", qtext)
    return m.group(1) if m else None


# --- Derivers per "kind" ----------------------------------------------------

def derive_parent_lookup(q: dict) -> dict:
    """Question asks about parent/epic of a specific issue."""
    key = extract_issue_key(q["q"]) or (q.get("expected_keys") or [None])[0]
    if not key:
        return {"_skipped": "could not extract issue key"}
    iss = get_issue(key)
    if not iss:
        return {"_skipped": f"issue {key} not found"}
    f = iss["fields"]
    parent = f.get("parent")
    epic_link = f.get("customfield_10014")
    subtasks = f.get("subtasks") or []
    facts = {
        "subject_key": key,
        "subject_type": f.get("issuetype", {}).get("name"),
        "subject_summary": f.get("summary"),
        "parent_key": parent.get("key") if parent else None,
        "parent_summary": (parent.get("fields") or {}).get("summary") if parent else None,
        "epic_link": epic_link,
        "subtask_keys": [s.get("key") for s in subtasks],
    }
    # Build prose answer
    if parent:
        ans = (f"{key} ({facts['subject_type']}) — \"{facts['subject_summary']}\" — "
               f"belongs to parent {parent.get('key')} (\"{facts['parent_summary']}\").")
    elif epic_link:
        ans = f"{key} is linked to epic {epic_link}."
    elif subtasks:
        ans = (f"{key} is a parent issue with {len(subtasks)} subtask(s): "
               f"{', '.join(facts['subtask_keys'])}.")
    else:
        ans = f"{key} ({facts['subject_type']}) has no parent issue, epic link, or subtasks."
    facts["golden_answer"] = ans
    return facts


def derive_comments_fetch(q: dict) -> dict:
    key = extract_issue_key(q["q"]) or (q.get("expected_keys") or [None])[0]
    if not key:
        return {"_skipped": "no issue key"}
    cs = get_comments(key)
    facts = {
        "subject_key": key,
        "comment_count": len(cs),
        "comments": [
            {"author": c.get("author", {}).get("displayName", "?"),
             "created": (c.get("created") or "")[:10],
             "body_snippet": adf_to_text(c.get("body"))[:300]}
            for c in cs
        ],
    }
    if not cs:
        facts["golden_answer"] = f"{key} has no comments."
    else:
        snippets = "\n".join(f"- {c['author']} ({c['created']}): {c['body_snippet']}"
                              for c in facts["comments"][:5])
        facts["golden_answer"] = (f"{key} has {len(cs)} comment(s). "
                                    f"Recent activity:\n{snippets}")
    return facts


def derive_worklog_fetch(q: dict) -> dict:
    key = extract_issue_key(q["q"]) or (q.get("expected_keys") or [None])[0]
    if not key:
        return {"_skipped": "no issue key"}
    ws = get_worklogs(key)
    total_seconds = sum(w.get("timeSpentSeconds", 0) or 0 for w in ws)
    facts = {
        "subject_key": key,
        "worklog_count": len(ws),
        "total_time_seconds": total_seconds,
        "total_time_human": f"{total_seconds // 3600}h {(total_seconds % 3600) // 60}m",
        "entries": [
            {"author": w.get("author", {}).get("displayName", "?"),
             "time_spent": w.get("timeSpent", ""),
             "comment": adf_to_text(w.get("comment"))[:200]}
            for w in ws
        ],
    }
    if not ws:
        facts["golden_answer"] = f"No time has been logged on {key}."
    else:
        facts["golden_answer"] = (f"{key} has {len(ws)} worklog entries totaling "
                                    f"{facts['total_time_human']}.")
    return facts


def derive_issue_links_fetch(q: dict) -> dict:
    key = extract_issue_key(q["q"]) or (q.get("expected_keys") or [None])[0]
    if not key:
        return {"_skipped": "no issue key"}
    iss = get_issue(key, fields=("issuelinks", "summary"))
    if not iss:
        return {"_skipped": "issue not found"}
    links = iss["fields"].get("issuelinks", []) or []
    facts = {
        "subject_key": key,
        "link_count": len(links),
        "links": [],
    }
    for l in links:
        if l.get("inwardIssue"):
            facts["links"].append({
                "direction": "inward",
                "type": l.get("type", {}).get("inward"),
                "key": l["inwardIssue"].get("key"),
            })
        if l.get("outwardIssue"):
            facts["links"].append({
                "direction": "outward",
                "type": l.get("type", {}).get("outward"),
                "key": l["outwardIssue"].get("key"),
            })
    if not links:
        facts["golden_answer"] = f"{key} has no issue links (no dependencies, duplicates, or related issues)."
    else:
        items = "; ".join(f"{l['type']} {l['key']}" for l in facts["links"])
        facts["golden_answer"] = f"{key} has {len(facts['links'])} link(s): {items}."
    return facts


def derive_count_or_groupby(q: dict) -> dict:
    """Generic count + group-by from the question's JQL."""
    jql = q.get("jql")
    if not jql:
        return {"_skipped": "no JQL on the question"}
    issues = jql_search(jql, fields=("summary", "status", "priority", "issuetype", "components"))
    facts = {
        "jql": jql,
        "issue_count": len(issues),
        "expected_count_from_question": q.get("expected_count"),
        "by_project": dict(Counter(i["key"].split("-")[0] for i in issues)),
        "by_priority": dict(Counter((i["fields"].get("priority") or {}).get("name", "Unknown") for i in issues)),
        "by_status": dict(Counter((i["fields"].get("status") or {}).get("name", "Unknown") for i in issues)),
        "by_type": dict(Counter((i["fields"].get("issuetype") or {}).get("name", "Unknown") for i in issues)),
        "sample_keys": [i["key"] for i in issues[:10]],
    }
    # Prose
    parts = [f"There are {len(issues)} issue(s) matching the query."]
    if len(facts["by_project"]) > 1:
        parts.append("By project: " + ", ".join(f"{k}={v}" for k, v in sorted(facts["by_project"].items(), key=lambda x: -x[1])))
    if "Priority" in q["q"] or "priority" in q["q"]:
        parts.append("By priority: " + ", ".join(f"{k}={v}" for k, v in sorted(facts["by_priority"].items(), key=lambda x: -x[1])))
    if "status" in q["q"].lower() or "to do" in q["q"].lower():
        parts.append("By status: " + ", ".join(f"{k}={v}" for k, v in sorted(facts["by_status"].items(), key=lambda x: -x[1])))
    facts["golden_answer"] = " ".join(parts)
    return facts


def derive_comparison_groupby(q: dict) -> dict:
    return derive_count_or_groupby(q)


def derive_schema_filter(q: dict) -> dict:
    """Component/version filter — count + per-component breakdown."""
    jql = q.get("jql")
    if not jql:
        return {"_skipped": "no JQL"}
    issues = jql_search(jql, fields=("summary", "components"))
    comp_counter = Counter()
    for i in issues:
        cs = (i["fields"].get("components") or []) or []
        if not cs:
            comp_counter["(none)"] += 1
        for c in cs:
            comp_counter[c.get("name", "?")] += 1
    facts = {
        "jql": jql,
        "issue_count": len(issues),
        "by_component": dict(comp_counter),
        "sample_keys": [i["key"] for i in issues[:10]],
    }
    facts["golden_answer"] = (f"{len(issues)} issue(s) match the filter. "
                                f"Components: " + ", ".join(f"{k}={v}" for k, v in comp_counter.most_common()))
    return facts


def derive_time_bucket(q: dict) -> dict:
    """Trend questions — bucket the JQL result by created date."""
    jql = q.get("jql")
    if not jql:
        return {"_skipped": "no JQL"}
    issues = jql_search(jql, fields=("created",))
    by_day = Counter()
    for i in issues:
        day = (i["fields"].get("created") or "")[:10]
        if day:
            by_day[day] += 1
    facts = {
        "jql": jql,
        "issue_count": len(issues),
        "by_day": dict(sorted(by_day.items())),
        "distinct_days": len(by_day),
    }
    if len(by_day) <= 1:
        d = list(by_day.keys())[0] if by_day else "(none)"
        facts["golden_answer"] = (f"All {len(issues)} matching issues were created on {d}. "
                                    f"There is no meaningful day-over-day trend because the corpus "
                                    f"was bulk-created in a single session.")
    else:
        days_str = ", ".join(f"{d}={n}" for d, n in sorted(by_day.items()))
        facts["golden_answer"] = (f"{len(issues)} issues across {len(by_day)} distinct day(s). "
                                    f"Distribution by day: {days_str}")
    return facts


DERIVERS = {
    "parent_lookup": derive_parent_lookup,
    "comments_fetch": derive_comments_fetch,
    "worklog_fetch": derive_worklog_fetch,
    "issue_links_fetch": derive_issue_links_fetch,
    "count_or_groupby": derive_count_or_groupby,
    "comparison_groupby": derive_comparison_groupby,
    "schema_filter": derive_schema_filter,
    "time_bucket": derive_time_bucket,
}


def main():
    triage = json.load(open(EVAL_DIR / "golden/triage.json"))
    questions = {q["id"]: q for q in json.load(open(EVAL_DIR / "questions/main.json"))}
    b1 = [t for t in triage if t["bucket"] == "B1"]
    print(f"Deriving golden facts for {len(b1)} Bucket-1 questions...")

    out_path = EVAL_DIR / "golden/golden_b1.json"
    out = {}
    if out_path.exists():
        out = json.loads(out_path.read_text())
        print(f"  resuming from existing {len(out)} entries")

    for i, t in enumerate(b1, 1):
        qid = t["id"]
        if qid in out and "_skipped" not in out[qid]:
            continue
        kind = t["kind"]
        derive_fn = DERIVERS.get(kind)
        if not derive_fn:
            out[qid] = {"_skipped": f"no deriver for kind={kind}"}
            continue
        q = questions[qid]
        try:
            facts = derive_fn(q)
        except Exception as exc:
            facts = {"_skipped": f"derive error: {type(exc).__name__}: {str(exc)[:200]}"}
        facts["kind"] = kind
        facts["question_id"] = qid
        out[qid] = facts
        if i % 10 == 0:
            print(f"  [{i}/{len(b1)}] done so far")
            out_path.write_text(json.dumps(out, indent=2))

    out_path.write_text(json.dumps(out, indent=2))
    success = sum(1 for v in out.values() if "_skipped" not in v)
    print(f"\nDone. {success}/{len(b1)} golden facts derived. Written to {out_path}.")


if __name__ == "__main__":
    main()
