"""Phase 1d: Re-synthesize B3 entries that came up empty (n_real_issues=0)
in golden_b3.json. Fallback strategy:

1. If question has expected_keys, fetch those
2. Else, extract Jira keys from question text
3. Else, infer JQL from category + content keywords (e.g. "BUGS" project, "API" labels)
4. Else, mark intent=unanswerable and add to excluded list

Writes:
  - golden/golden_b3_super.json — extended b3 with all 116 entries grounded
  - golden/excluded_qids.json — list of qids to drop from accuracy denominator
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

# Map question keywords → JQL fragments
PROJECT_HINTS = {
    "BUGS": "project = BUGS",
    "CRM": "project = CRM",
    "OPS": "project = OPS",
    "PLAT": "project = PLAT",
    "SMP": "project = SMP",
}

# Keyword → text-search fragment
TEXT_HINTS = [
    (re.compile(r"\bapi\b", re.I), 'text ~ "API"'),
    (re.compile(r"\bdatabase|storage\b", re.I), 'text ~ "database" OR text ~ "storage"'),
    (re.compile(r"\bauth(?:entication)?\b", re.I), 'text ~ "authentication" OR text ~ "auth"'),
    (re.compile(r"\bmobile\b", re.I), 'text ~ "mobile"'),
    (re.compile(r"\bperformance|latency|slow\b", re.I), 'text ~ "performance" OR text ~ "latency"'),
    (re.compile(r"\bsecurity\b", re.I), 'text ~ "security"'),
    (re.compile(r"\bemail\b", re.I), 'text ~ "email"'),
    (re.compile(r"\bpagerduty\b", re.I), 'text ~ "pagerduty"'),
    (re.compile(r"\bintegration\b", re.I), 'text ~ "integration"'),
    (re.compile(r"\brender(?:ing)?|ui\b", re.I), 'text ~ "render" OR text ~ "UI"'),
    (re.compile(r"\bnotification\b", re.I), 'text ~ "notification"'),
    (re.compile(r"\bdashboard\b", re.I), 'text ~ "dashboard"'),
]


def adf_to_text(adf, max_len=400):
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
                parts.append(adf_to_text(content, max_len))
    return " ".join(p for p in parts if p).strip()[:max_len]


def infer_jql(q: dict) -> str | None:
    qtext = q["q"]
    parts = []
    proj_parts = [v for k, v in PROJECT_HINTS.items() if re.search(rf"\b{k}\b", qtext)]
    text_parts = [pat[1] for pat in TEXT_HINTS if pat[0].search(qtext)]
    if proj_parts:
        parts.append("(" + " OR ".join(proj_parts) + ")")
    if text_parts:
        parts.append("(" + " OR ".join(text_parts) + ")")
    if not parts:
        return None
    return " AND ".join(parts)


async def jql_fetch(client, jql, sem, max_issues=15):
    async with sem:
        params = {"jql": jql, "fields": "summary,description,status,priority,issuetype,components,labels", "maxResults": max_issues}
        try:
            r = await client.get(f"{SITE}/rest/api/3/search/jql", headers=HDR, params=params, timeout=30.0)
            if r.status_code != 200:
                return []
            return r.json().get("issues", [])
        except Exception:
            return []


async def synthesize_one(q: dict, issues: list[dict], gemini_client) -> str:
    if not issues:
        return "[no data]"
    from google.genai import types as _t
    render = []
    for i in issues[:15]:
        f = i["fields"]
        render.append(
            f"{i['key']} [{(f.get('issuetype') or {}).get('name')}, "
            f"{(f.get('priority') or {}).get('name')}, {(f.get('status') or {}).get('name')}]\n"
            f"  Summary: {f.get('summary','')[:200]}\n"
            f"  Description: {adf_to_text(f.get('description'), 300)}\n"
        )
    prompt = f"""Question: {q['q']}

EXPECTED THEMES (hints): {', '.join(q.get('expected_themes', []) or ['(none)'])}

ACTUAL JIRA ISSUES (use ONLY these as ground truth):
{chr(10).join(render)}

Write a concise reference answer (under 250 words) grounded ONLY in the data above."""

    def _do():
        resp = gemini_client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=prompt,
            config=_t.GenerateContentConfig(
                system_instruction="You are writing ground-truth reference answers for an AI eval. Be concise, grounded, prose.",
                temperature=0.2,
                max_output_tokens=500,
                thinking_config=_t.ThinkingConfig(include_thoughts=False, thinking_level=_t.ThinkingLevel.MINIMAL),
            ),
        )
        return (resp.text or "").strip()

    for attempt in range(3):
        try:
            return await asyncio.to_thread(_do)
        except Exception as exc:
            if attempt < 2:
                await asyncio.sleep(2 ** attempt)
                continue
            return f"[synthesis-error: {type(exc).__name__}: {str(exc)[:200]}]"
    return "[synthesis-error]"


async def main():
    qs = {q["id"]: q for q in json.load(open(EVAL_DIR / "questions/main.json"))}
    b3 = json.load(open(EVAL_DIR / "golden/golden_b3.json"))
    out_b3 = dict(b3)

    empty = [qid for qid, v in b3.items() if v.get("n_real_issues", 0) == 0]
    print(f"Re-synthesizing {len(empty)} empty B3 entries...")

    # Setup Gemini
    sys.path.insert(0, str(EVAL_DIR))
    import judge as _j
    from google import genai
    gemini = genai.Client(vertexai=True, project="vtxdemos", location="global", credentials=_j._user_credentials())

    excluded = []
    timeout = httpx.Timeout(connect=10.0, read=30.0, write=30.0, pool=30.0)
    sem = asyncio.Semaphore(10)
    sem_syn = asyncio.Semaphore(4)

    async with httpx.AsyncClient(timeout=timeout) as client:
        async def one(qid):
            q = qs[qid]
            keys = q.get("expected_keys") or re.findall(r"\b[A-Z]{2,8}-\d+\b", q["q"])
            issues = []
            if keys:
                jql = "key in (" + ",".join(keys[:20]) + ")"
                issues = await jql_fetch(client, jql, sem, max_issues=20)
            if not issues:
                inferred = infer_jql(q)
                if inferred:
                    issues = await jql_fetch(client, inferred, sem, max_issues=15)
            if not issues:
                # Mark unanswerable
                excluded.append(qid)
                out_b3[qid] = {
                    "question_id": qid,
                    "category": q["category"],
                    "n_real_issues": 0,
                    "issue_keys_used": [],
                    "golden_answer": "[unanswerable: no relevant Jira data found]",
                    "intent": "unanswerable",
                    "synthesis_error": False,
                }
                return None
            async with sem_syn:
                ans = await synthesize_one(q, issues, gemini)
            out_b3[qid] = {
                "question_id": qid,
                "category": q["category"],
                "n_real_issues": len(issues),
                "issue_keys_used": [i["key"] for i in issues],
                "golden_answer": ans,
                "synthesizer_model": "gemini-3-flash-preview",
                "resynth": True,
            }
            return qid

        results = await asyncio.gather(*[one(qid) for qid in empty])
        done = sum(1 for r in results if r)
        print(f"Synthesized {done}/{len(empty)} (excluded as unanswerable: {len(excluded)})")

    out_path = EVAL_DIR / "golden/golden_b3_super.json"
    out_path.write_text(json.dumps(out_b3, indent=2))
    print(f"Wrote {out_path}")

    excl_path = EVAL_DIR / "golden/excluded_qids.json"
    excl_path.write_text(json.dumps(excluded, indent=2))
    print(f"Wrote {len(excluded)} excluded qids → {excl_path}")


if __name__ == "__main__":
    asyncio.run(main())
