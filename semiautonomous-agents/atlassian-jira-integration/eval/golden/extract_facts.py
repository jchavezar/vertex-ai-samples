"""Phase 1b: For each question that has a definite issue key (or JQL with small
result set), fetch the full Jira issue facts and cache.

Outputs golden/facts_cache.json keyed by Jira issue key (e.g. "BUGS-100").
"""
from __future__ import annotations

import asyncio
import base64
import json
import os
import re
import sys
from pathlib import Path

import httpx

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
HDR = {"Authorization": f"Basic {_AUTH}", "Accept": "application/json"}

JIRA_KEY_RE = re.compile(r"\b[A-Z]{2,8}-\d+\b")

FIELDS = ",".join([
    "summary", "status", "priority", "issuetype", "assignee", "reporter",
    "components", "labels", "fixVersions", "created", "updated",
    "resolutiondate", "parent", "issuelinks", "duedate",
    "customfield_10014",
])


def _adf_text(adf, max_len=400):
    if isinstance(adf, str):
        return adf[:max_len]
    if not isinstance(adf, dict):
        return ""
    parts = []
    for content in adf.get("content", []) or []:
        if isinstance(content, dict):
            if content.get("type") == "text":
                parts.append(content.get("text", ""))
            else:
                parts.append(_adf_text(content, max_len))
    return " ".join(p for p in parts if p).strip()[:max_len]


def _person(p):
    if not p or not isinstance(p, dict):
        return None
    return {
        "displayName": p.get("displayName"),
        "email": p.get("emailAddress"),
        "accountId": p.get("accountId"),
    }


def _struct_issue(iss: dict) -> dict:
    f = iss.get("fields", {}) or {}
    parent = f.get("parent") or {}
    links = []
    for l in (f.get("issuelinks") or []):
        if l.get("inwardIssue"):
            links.append({"dir": "inward", "type": (l.get("type") or {}).get("inward"), "key": l["inwardIssue"].get("key")})
        if l.get("outwardIssue"):
            links.append({"dir": "outward", "type": (l.get("type") or {}).get("outward"), "key": l["outwardIssue"].get("key")})
    return {
        "key": iss.get("key"),
        "summary": f.get("summary"),
        "status": (f.get("status") or {}).get("name"),
        "priority": (f.get("priority") or {}).get("name"),
        "issuetype": (f.get("issuetype") or {}).get("name"),
        "assignee": _person(f.get("assignee")),
        "reporter": _person(f.get("reporter")),
        "components": [c.get("name") for c in (f.get("components") or [])],
        "labels": f.get("labels") or [],
        "fixVersions": [v.get("name") for v in (f.get("fixVersions") or [])],
        "created": f.get("created"),
        "updated": f.get("updated"),
        "resolution_date": f.get("resolutiondate"),
        "parent": parent.get("key") if parent else None,
        "epic_link": f.get("customfield_10014"),
        "duedate": f.get("duedate"),
        "linked_issues": links,
    }


async def fetch_issue(client: httpx.AsyncClient, key: str, sem: asyncio.Semaphore) -> tuple[str, dict | None]:
    async with sem:
        try:
            url = f"{SITE}/rest/api/3/issue/{key}"
            r = await client.get(url, headers=HDR, params={"fields": FIELDS}, timeout=30.0)
            if r.status_code != 200:
                return key, None
            return key, _struct_issue(r.json())
        except Exception:
            return key, None


async def fetch_comments_count(client: httpx.AsyncClient, key: str, sem: asyncio.Semaphore) -> tuple[str, int]:
    async with sem:
        try:
            r = await client.get(f"{SITE}/rest/api/3/issue/{key}/comment", headers=HDR, timeout=20.0)
            if r.status_code == 200:
                return key, len(r.json().get("comments", []))
            return key, 0
        except Exception:
            return key, 0


async def fetch_worklog_total(client: httpx.AsyncClient, key: str, sem: asyncio.Semaphore) -> tuple[str, int]:
    async with sem:
        try:
            r = await client.get(f"{SITE}/rest/api/3/issue/{key}/worklog", headers=HDR, timeout=20.0)
            if r.status_code == 200:
                return key, sum((w.get("timeSpentSeconds") or 0) for w in r.json().get("worklogs", []))
            return key, 0
        except Exception:
            return key, 0


async def jql_keys(client: httpx.AsyncClient, jql: str, sem: asyncio.Semaphore, max_pages: int = 5) -> list[str]:
    async with sem:
        out = []
        nxt = ""
        for _ in range(max_pages):
            params = {"jql": jql, "fields": "summary", "maxResults": 100}
            if nxt:
                params["nextPageToken"] = nxt
            try:
                r = await client.get(f"{SITE}/rest/api/3/search/jql", headers=HDR, params=params, timeout=30.0)
                if r.status_code != 200:
                    return out
                body = r.json()
                out.extend(i["key"] for i in body.get("issues", []))
                nxt = body.get("nextPageToken")
                if not nxt:
                    break
            except Exception:
                return out
        return out


def gather_keys(qs: list[dict], intents: dict) -> tuple[set[str], dict[str, list[str]]]:
    """Return (all_keys_to_fetch, per_qid_keys)."""
    all_keys: set[str] = set()
    per_qid: dict[str, list[str]] = {}
    for q in qs:
        qid = q["id"]
        intent = (intents.get(qid) or {}).get("intent", "analytical")
        keys: list[str] = []

        # From explicit field
        for k in (q.get("expected_keys") or []):
            keys.append(k)
        # From question text
        for k in JIRA_KEY_RE.findall(q["q"]):
            keys.append(k)

        # Dedup
        keys = sorted(set(keys))

        # Cap per question — analytical questions can have huge sets; keep first 30
        if intent in {"key_recall", "analytical"}:
            keys = keys[:30]
        elif intent == "count_or_groupby":
            # We don't need to fetch all; the count comes from JQL
            keys = keys[:10]

        per_qid[qid] = keys
        all_keys.update(keys)

    return all_keys, per_qid


async def main():
    qs = json.load(open(EVAL_DIR / "questions/main.json"))
    intents = json.load(open(EVAL_DIR / "golden/intents.json"))

    all_keys, per_qid = gather_keys(qs, intents)
    print(f"Total unique keys to fetch: {len(all_keys)}")

    # Resume if cache exists
    cache_path = EVAL_DIR / "golden/facts_cache.json"
    cache: dict[str, dict] = {}
    if cache_path.exists():
        cache = json.loads(cache_path.read_text())
        print(f"Resuming from cache with {len(cache)} entries")

    todo = [k for k in all_keys if k not in cache]
    print(f"Need to fetch {len(todo)} new keys")

    sem = asyncio.Semaphore(20)
    timeout = httpx.Timeout(connect=10.0, read=30.0, write=30.0, pool=30.0)

    async with httpx.AsyncClient(timeout=timeout) as client:
        # Fetch issue base in parallel
        results = await asyncio.gather(*[fetch_issue(client, k, sem) for k in todo])
        for key, struct in results:
            if struct:
                cache[key] = struct

        cache_path.write_text(json.dumps(cache, indent=2))
        print(f"Phase 1: base issues fetched. Cache size now {len(cache)}")

        # Now fetch comments/worklog counts for all keys
        all_keys_for_extra = [k for k in cache if "comments_count" not in cache[k] or "worklog_total_seconds" not in cache[k]]
        print(f"Phase 2: comments_count + worklog for {len(all_keys_for_extra)} keys")

        if all_keys_for_extra:
            cs = await asyncio.gather(*[fetch_comments_count(client, k, sem) for k in all_keys_for_extra])
            for k, n in cs:
                if k in cache:
                    cache[k]["comments_count"] = n
            ws = await asyncio.gather(*[fetch_worklog_total(client, k, sem) for k in all_keys_for_extra])
            for k, n in ws:
                if k in cache:
                    cache[k]["worklog_total_seconds"] = n

        cache_path.write_text(json.dumps(cache, indent=2))
        print(f"Done. Cache size: {len(cache)} → {cache_path}")

    # Also write per_qid
    out_path = EVAL_DIR / "golden/per_qid_keys.json"
    out_path.write_text(json.dumps(per_qid, indent=2))
    print(f"Wrote per-qid key map → {out_path}")


if __name__ == "__main__":
    asyncio.run(main())
