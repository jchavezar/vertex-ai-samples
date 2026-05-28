"""Phase 3: Hand-craft 30 realistic power-user questions and verify them live.

Each question is paired with the JQL needed to derive its answer. We then run the
JQL against the live Jira tenant (async, semaphore 15) and capture golden_facts
(counts, key lists, summary samples) into the question record.

Output: eval/golden/phase3_handcrafted.json
"""
from __future__ import annotations

import asyncio
import base64
import json
import os
import re
from collections import Counter
from datetime import date, datetime
from pathlib import Path

import aiohttp

EVAL_DIR = Path(__file__).resolve().parent.parent

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
HDR = {"Authorization": f"Basic {_AUTH}", "Accept": "application/json",
       "Content-Type": "application/json"}

# Today (frozen for stable JQL)
TODAY = date(2026, 5, 21)


# === 30 Hand-crafted power-user questions ===================================
HANDCRAFTED = [
    # Multi-dimensional filter (4)
    {
        "id": "q5000",
        "q": "Show me all High priority OPS issues currently unresolved that involve either CI/CD or observability work.",
        "category": "multi-step",
        "tags": ["multi-dimensional", "filter", "real-power-user"],
        "intent": "key_recall",
        "jql": 'project = OPS AND priority = High AND resolution = Unresolved AND labels in ("ci-cd","observability")',
    },
    {
        "id": "q5001",
        "q": "Which BUGS stories are tagged 'api-v2' and were created in May 2026?",
        "category": "multi-step",
        "tags": ["multi-dimensional", "filter", "real-power-user"],
        "intent": "key_recall",
        "jql": 'project = BUGS AND issuetype = Story AND labels = "api-v2" AND created >= "2026-05-01" AND created < "2026-06-01"',
    },
    {
        "id": "q5002",
        "q": "List CRM tickets in the 'refunds' or 'billing-support' components that are tagged as either an initiative or 'automation'.",
        "category": "multi-step",
        "tags": ["multi-dimensional", "filter", "real-power-user"],
        "intent": "key_recall",
        "jql": 'project = CRM AND component in ("refunds","billing-support") AND labels in ("initiative","automation")',
    },
    {
        "id": "q5003",
        "q": "Find every PLAT story (not subtask) at High or Highest priority that mentions service mesh or RBAC.",
        "category": "multi-step",
        "tags": ["multi-dimensional", "filter", "real-power-user"],
        "intent": "key_recall",
        "jql": 'project = PLAT AND issuetype = Story AND priority in (High, Highest) AND (text ~ "service mesh" OR text ~ "RBAC")',
    },
    # Comparative analysis (3)
    {
        "id": "q5004",
        "q": "Compare the number of High and Highest priority issues between BUGS and CRM — which project has more and by how much?",
        "category": "cross-issue-analysis",
        "tags": ["comparative", "cross-project", "real-power-user"],
        "intent": "comparative",
        "jql": 'project in (BUGS, CRM) AND priority in (High, Highest)',
    },
    {
        "id": "q5005",
        "q": "Across all four engineering projects (BUGS/CRM/OPS/PLAT), which one has the most subtasks and which has the fewest?",
        "category": "cross-issue-analysis",
        "tags": ["comparative", "cross-project", "real-power-user"],
        "intent": "comparative",
        "jql": 'project in (BUGS, CRM, OPS, PLAT) AND issuetype = Subtask',
    },
    {
        "id": "q5006",
        "q": "How does the priority mix of the OPS project compare to the PLAT project — give me percentages by priority level.",
        "category": "cross-issue-analysis",
        "tags": ["comparative", "cross-project", "real-power-user"],
        "intent": "comparative",
        "jql": 'project in (OPS, PLAT)',
    },
    # Root cause synthesis / summarisation (3)
    {
        "id": "q5007",
        "q": "Summarize the work captured under the 'API v2 Modernization' initiative (BUGS-76) — what are the major workstreams in its subtasks?",
        "category": "root-cause-synthesis",
        "tags": ["synthesis", "epic", "real-power-user"],
        "intent": "synthesis",
        "jql": '"Epic Link" = BUGS-76 OR parent = BUGS-76',
    },
    {
        "id": "q5008",
        "q": "Looking at all High-priority OPS issues, what are the recurring themes — is it more about reliability, performance, or cost?",
        "category": "root-cause-synthesis",
        "tags": ["synthesis", "themes", "real-power-user"],
        "intent": "synthesis",
        "jql": 'project = OPS AND priority = High',
    },
    {
        "id": "q5009",
        "q": "Across CRM's 'account-recovery' component, what self-service capabilities are being built and what's still manual?",
        "category": "root-cause-synthesis",
        "tags": ["synthesis", "component", "real-power-user"],
        "intent": "synthesis",
        "jql": 'project = CRM AND component = "account-recovery"',
    },
    # Cross-project dependency (3)
    {
        "id": "q5010",
        "q": "Which PLAT issues are currently blocking other PLAT issues, and what's the dependency chain?",
        "category": "issue-links",
        "tags": ["dependency", "cross-issue", "real-power-user"],
        "intent": "key_recall",
        "jql": 'project = PLAT AND issueLinkType = "blocks"',
    },
    {
        "id": "q5011",
        "q": "Are any OPS issues blocking work in other projects, or vice versa?",
        "category": "issue-links",
        "tags": ["dependency", "cross-project", "real-power-user"],
        "intent": "analytical",
        "jql": 'project = OPS AND issueLinkType in ("blocks","is blocked by")',
    },
    {
        "id": "q5012",
        "q": "Show me the full blockers tree for PLAT-43 — who blocks it, and who do those blockers block in turn?",
        "category": "issue-links",
        "tags": ["dependency", "single-issue-tree", "real-power-user"],
        "intent": "analytical",
        "jql": 'key = PLAT-43',
    },
    # Workload analysis (2)
    {
        "id": "q5013",
        "q": "Who currently has the most High and Highest priority unresolved tickets across all engineering projects?",
        "category": "cross-issue-analysis",
        "tags": ["workload", "ownership", "real-power-user"],
        "intent": "analytical",
        "jql": 'project in (BUGS, CRM, OPS, PLAT) AND priority in (High, Highest) AND resolution = Unresolved',
    },
    {
        "id": "q5014",
        "q": "Among unresolved BUGS issues, list the 5 with the oldest creation date — they're at risk of stalling.",
        "category": "multi-step",
        "tags": ["workload", "aging", "real-power-user"],
        "intent": "analytical",
        "jql": 'project = BUGS AND resolution = Unresolved ORDER BY created ASC',
    },
    # Process compliance (2)
    {
        "id": "q5015",
        "q": "How many Story-type issues across the engineering projects are at High or Highest priority right now, broken down by project?",
        "category": "cross-issue-analysis",
        "tags": ["planning", "groupby", "real-power-user"],
        "intent": "count_or_groupby",
        "jql": 'project in (BUGS, CRM, OPS, PLAT) AND issuetype = Story AND priority in (High, Highest)',
    },
    {
        "id": "q5016",
        "q": "Find every Epic across our engineering projects that has fewer than 3 subtasks — these epics may be under-broken-down.",
        "category": "cross-issue-analysis",
        "tags": ["compliance", "planning", "real-power-user"],
        "intent": "analytical",
        "jql": 'project in (BUGS, CRM, OPS, PLAT) AND issuetype = Epic',
    },
    # Sprint planning (2)
    {
        "id": "q5017",
        "q": "Show me all CRM Story-type issues at High or Highest priority — these are the candidates for the next sprint.",
        "category": "jql-filter",
        "tags": ["planning", "sprint", "real-power-user"],
        "intent": "key_recall",
        "jql": 'project = CRM AND issuetype = Story AND priority in (High, Highest)',
    },
    {
        "id": "q5018",
        "q": "Of the issues under the 'Service Mesh Migration' epic (PLAT-1), which are the high-priority ones to tackle first?",
        "category": "epic-tree",
        "tags": ["planning", "epic", "real-power-user"],
        "intent": "key_recall",
        "jql": 'parent = PLAT-1 AND priority in (High, Highest) ORDER BY priority DESC',
    },
    # Risk surfacing (2)
    {
        "id": "q5019",
        "q": "Give me every Highest-priority issue across the four engineering projects, grouped by project — these are our top-of-mind risks right now.",
        "category": "cross-issue-analysis",
        "tags": ["risk", "highest-priority", "real-power-user"],
        "intent": "key_recall",
        "jql": 'project in (BUGS, CRM, OPS, PLAT) AND priority = Highest ORDER BY project, key',
    },
    {
        "id": "q5020",
        "q": "List all OPS Highest-priority issues created in May 2026 — these are the top-of-mind production-risk items.",
        "category": "jql-filter",
        "tags": ["risk", "highest-priority", "real-power-user"],
        "intent": "key_recall",
        "jql": 'project = OPS AND priority = Highest AND created >= "2026-05-01" AND created < "2026-06-01"',
    },
    # Knowledge transfer / synthesis (3)
    {
        "id": "q5021",
        "q": "Walk me through the four 'initiative'-tagged epics across BUGS/CRM/OPS/PLAT — what's the high-level theme of each program?",
        "category": "root-cause-synthesis",
        "tags": ["synthesis", "initiative", "real-power-user"],
        "intent": "synthesis",
        "jql": 'project in (BUGS, CRM, OPS, PLAT) AND issuetype = Epic AND labels = "initiative"',
    },
    {
        "id": "q5022",
        "q": "Give me the 5 most important takeaways from the 'Cloud Cost Optimization' initiative (PLAT-76) and its subtasks.",
        "category": "root-cause-synthesis",
        "tags": ["synthesis", "epic", "real-power-user"],
        "intent": "synthesis",
        "jql": 'key = PLAT-76 OR parent = PLAT-76',
    },
    {
        "id": "q5023",
        "q": "What's the architectural direction of the OPS Kubernetes Cluster Upgrade initiative (OPS-1) based on its subtasks?",
        "category": "root-cause-synthesis",
        "tags": ["synthesis", "epic", "real-power-user"],
        "intent": "synthesis",
        "jql": 'key = OPS-1 OR parent = OPS-1',
    },
    # Audit / history (2)
    {
        "id": "q5024",
        "q": "Has PLAT-43 ever been blocked, and if so, by which issues is it blocked right now?",
        "category": "issue-links",
        "tags": ["history", "audit", "real-power-user"],
        "intent": "analytical",
        "jql": 'key = PLAT-43',
    },
    {
        "id": "q5025",
        "q": "When was BUGS-76 (the API v2 Modernization epic) created, and how many child issues does it have today?",
        "category": "epic-tree",
        "tags": ["history", "audit", "real-power-user"],
        "intent": "analytical",
        "jql": 'key = BUGS-76 OR parent = BUGS-76',
    },
    # Tag / label exploration (2)
    {
        "id": "q5026",
        "q": "Across BUGS, which mobile-related tickets (mobile-android or mobile-ios labels) are at High priority or above?",
        "category": "jql-filter",
        "tags": ["filter", "label", "real-power-user"],
        "intent": "key_recall",
        "jql": 'project = BUGS AND labels in ("mobile-android","mobile-ios") AND priority in (High, Highest)',
    },
    {
        "id": "q5027",
        "q": "What 'developer-experience'-tagged work is in flight across PLAT and OPS, grouped by project?",
        "category": "multi-project",
        "tags": ["filter", "label", "real-power-user"],
        "intent": "count_or_groupby",
        "jql": 'project in (PLAT, OPS) AND labels = "developer-experience"',
    },
    # Comparative date / planning (2)
    {
        "id": "q5028",
        "q": "How many issues were created across all engineering projects in the second week of May 2026 (May 8-14)?",
        "category": "trend",
        "tags": ["volume", "trend", "real-power-user"],
        "intent": "count_or_groupby",
        "jql": 'project in (BUGS, CRM, OPS, PLAT) AND created >= "2026-05-08" AND created <= "2026-05-14"',
    },
    {
        "id": "q5029",
        "q": "For the BUGS project, give me a priority breakdown of the issues created on May 9, 2026 — that was a high-volume day.",
        "category": "trend",
        "tags": ["volume", "groupby", "real-power-user"],
        "intent": "count_or_groupby",
        "jql": 'project = BUGS AND created >= "2026-05-09" AND created < "2026-05-10"',
    },
]


# === Live verification ======================================================
async def jql_search(session, sem, jql, fields="summary,status,priority,issuetype,parent,labels,components,assignee,created,issuelinks,description",
                      limit=200):
    """Return list of issues for a JQL query (paginated, capped at limit)."""
    out = []
    nxt = None
    async with sem:
        while len(out) < limit:
            params = {"jql": jql, "fields": fields, "maxResults": min(100, limit - len(out))}
            if nxt:
                params["nextPageToken"] = nxt
            async with session.get(f"{SITE}/rest/api/3/search/jql", headers=HDR, params=params) as r:
                if r.status != 200:
                    return out, r.status
                body = await r.json()
                out.extend(body.get("issues", []))
                nxt = body.get("nextPageToken")
                if not nxt:
                    break
        return out, 200


async def approximate_count(session, sem, jql):
    async with sem:
        async with session.post(f"{SITE}/rest/api/3/search/approximate-count",
                                 headers=HDR, json={"jql": jql}) as r:
            if r.status == 200:
                return (await r.json()).get("count", 0)
            return None


def adf_to_text(adf):
    if isinstance(adf, str):
        return adf
    if not isinstance(adf, dict):
        return ""
    parts = []
    for content in adf.get("content", []) or []:
        if isinstance(content, dict):
            if content.get("type") == "text":
                parts.append(content.get("text", ""))
            else:
                parts.append(adf_to_text(content))
    return " ".join(p for p in parts if p)


async def verify_one(session, sem, q):
    """Run the question's JQL and capture golden_facts."""
    jql = q.get("jql") or ""
    issues, status = await jql_search(session, sem, jql, limit=200)
    if status != 200:
        return {**q, "golden_facts": {"error": f"JQL HTTP {status}"}, "expected_keys": []}

    keys = [i["key"] for i in issues]
    n = len(issues)

    # Build per-priority and per-project breakdowns when relevant
    by_pri = Counter()
    by_proj = Counter()
    by_type = Counter()
    by_component = Counter()
    by_label = Counter()
    samples = []
    for i in issues[:10]:
        f = i["fields"]
        by_pri[(f.get("priority") or {}).get("name", "-")] += 1
        by_proj[i["key"].split("-")[0]] += 1
        by_type[(f.get("issuetype") or {}).get("name", "-")] += 1
        for c in f.get("components", []) or []:
            by_component[c.get("name", "-")] += 1
        for l in f.get("labels", []) or []:
            if l != "eval-corpus":
                by_label[l] += 1
        samples.append({
            "key": i["key"],
            "summary": f.get("summary", "")[:120],
            "priority": (f.get("priority") or {}).get("name"),
            "status": (f.get("status") or {}).get("name"),
        })
    for i in issues[10:]:
        f = i["fields"]
        by_pri[(f.get("priority") or {}).get("name", "-")] += 1
        by_proj[i["key"].split("-")[0]] += 1
        by_type[(f.get("issuetype") or {}).get("name", "-")] += 1

    facts = {
        "count": n,
        "keys": keys,
        "by_priority": dict(by_pri),
        "by_project": dict(by_proj),
        "by_issuetype": dict(by_type),
        "samples": samples,
    }
    if by_component:
        facts["by_component"] = dict(by_component.most_common(20))
    if by_label:
        facts["by_label"] = dict(by_label.most_common(20))

    # For "blocks"-type questions, capture link facts
    is_link_q = ("issueLinkType" in jql or "block" in (q.get("q") or "").lower()
                  or any("dependency" in t for t in q.get("tags", []) or []))
    if is_link_q:
        link_facts = []
        for i in issues[:50]:
            for l in i["fields"].get("issuelinks", []) or []:
                lt = (l.get("type") or {}).get("name", "")
                if "outwardIssue" in l:
                    link_facts.append({"from": i["key"], "type": l["type"].get("outward", lt),
                                       "to": l["outwardIssue"]["key"]})
                if "inwardIssue" in l:
                    link_facts.append({"from": i["key"], "type": l["type"].get("inward", lt),
                                       "to": l["inwardIssue"]["key"]})
        facts["links"] = link_facts

    return {**q, "expected_keys": keys[:50], "expected_count": n, "golden_facts": facts}


async def main():
    sem = asyncio.Semaphore(15)
    timeout = aiohttp.ClientTimeout(total=60)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        verified = await asyncio.gather(*(verify_one(session, sem, q) for q in HANDCRAFTED))

    out = EVAL_DIR / "golden/phase3_handcrafted.json"
    out.write_text(json.dumps(verified, indent=2, default=str))
    print(f"Wrote {len(verified)} handcrafted (verified) → {out}")

    # Print summary
    for q in verified:
        facts = q.get("golden_facts", {})
        n = facts.get("count", "?")
        print(f"  {q['id']} [{q['category']:24s}] n={n:>4} | {q['q'][:90]}")


if __name__ == "__main__":
    asyncio.run(main())
