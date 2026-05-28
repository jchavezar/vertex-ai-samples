"""Phase 2C: LLM-synthesized golden answers for Bucket 3 (genuine analytical).

For each B3 question:
  1. Pull the relevant Jira issues' full text (summary + description + components)
  2. Pass to gemini-3-flash-preview (different family than judges; was available
     in the project — pro-preview returned 404)
  3. Ask it to write a defensible reference answer GROUNDED in the issue text

Writes eval/golden/golden_b3.json — keyed by question id.

Cross-vendor independence note: the JUDGES are
  - Gemini 3.5 Flash (Google, Flash family)
  - Claude Sonnet 4.6 (Anthropic)
The GOLDEN synthesizer here is gemini-3-flash-preview — different family than
3.5-flash so the per-judge bias is partially neutralized. The QUESTION
generator was Claude Opus, so Sonnet still has a slight understanding edge,
but at least the golden answer text doesn't come from Claude.
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
import requests

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

sys.path.insert(0, str(EVAL_DIR))
import judge as _judge  # for the gcloud-user creds path

SYNTH_MODEL = os.environ.get("GOLDEN_MODEL", "gemini-3-flash-preview")
SYNTH_REGION = "global"
SYNTH_PROJECT = "vtxdemos"


# --- Issue fetcher ----------------------------------------------------------

def jql_search(jql: str, fields=("summary", "description", "status", "priority",
                                 "issuetype", "components", "labels", "created"),
               max_pages: int = 10) -> list[dict]:
    out = []
    nxt = ""
    for _ in range(max_pages):
        params = {"jql": jql, "fields": ",".join(fields), "maxResults": 100}
        if nxt:
            params["nextPageToken"] = nxt
        r = requests.get(f"{SITE}/rest/api/3/search/jql", headers=HDR, params=params, timeout=30)
        if r.status_code != 200:
            return out
        body = r.json()
        out.extend(body.get("issues", []))
        nxt = body.get("nextPageToken")
        if not nxt:
            break
    return out


def adf_to_text(adf, max_len: int = 600) -> str:
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


def fetch_issues_for_question(q: dict, max_issues: int = 20) -> list[dict]:
    """Get the actual Jira issues most relevant to the question."""
    jql = q.get("jql")
    if jql:
        issues = jql_search(jql)[:max_issues]
    elif q.get("expected_keys"):
        keys = q["expected_keys"][:max_issues]
        if keys:
            kq = "key in (" + ",".join(keys) + ")"
            issues = jql_search(kq)
        else:
            issues = []
    else:
        # Fall back — extract issue keys from question text
        keys = re.findall(r"\b[A-Z]{2,8}-\d+\b", q["q"])
        if keys:
            kq = "key in (" + ",".join(keys) + ")"
            issues = jql_search(kq)
        else:
            issues = []
    # Compact summary per issue
    out = []
    for i in issues:
        f = i["fields"]
        out.append({
            "key": i["key"],
            "type": (f.get("issuetype") or {}).get("name"),
            "priority": (f.get("priority") or {}).get("name"),
            "status": (f.get("status") or {}).get("name"),
            "summary": f.get("summary", "")[:200],
            "description": adf_to_text(f.get("description") or "", max_len=500),
            "components": [c.get("name") for c in (f.get("components") or [])],
            "labels": f.get("labels", []) or [],
        })
    return out


# --- Synthesizer ------------------------------------------------------------

SYSTEM = (
    "You are writing GROUND-TRUTH REFERENCE ANSWERS for an AI eval. "
    "Your answer MUST be grounded EXCLUSIVELY in the actual Jira issue text "
    "provided below. DO NOT invent issue keys or facts not in the data. "
    "Keep it concise — under 250 words. No headers, no markdown lists; just "
    "plain prose that a human grader can quickly compare against."
)

PROMPT_TPL = """Question: {q}

EXPECTED THEMES (hints — but defer to actual data if they conflict):
{themes}

ACTUAL JIRA ISSUES (use ONLY these as your ground truth):
{issues}

Write the reference answer."""


def render_issues(issues: list[dict]) -> str:
    if not issues:
        return "(no issues retrieved)"
    lines = []
    for i in issues:
        head = f"{i['key']} [{i.get('type','?')}, {i.get('priority','?')}, {i.get('status','?')}]"
        if i.get("components"):
            head += f", components: {', '.join(i['components'][:3])}"
        lines.append(head)
        lines.append(f"  Summary: {i['summary']}")
        if i.get("description"):
            lines.append(f"  Description: {i['description'][:400]}")
        lines.append("")
    return "\n".join(lines)


def _gemini_client():
    from google import genai
    return genai.Client(
        vertexai=True,
        project=SYNTH_PROJECT,
        location=SYNTH_REGION,
        credentials=_judge._user_credentials(),
    )


_CLIENT = None


async def synthesize(q: dict, issues: list[dict]) -> str:
    global _CLIENT
    if _CLIENT is None:
        _CLIENT = _gemini_client()
    from google.genai import types as _t
    themes = q.get("expected_themes", []) or []
    prompt = PROMPT_TPL.format(
        q=q["q"],
        themes="\n".join(f"- {t}" for t in themes) or "(no themes specified)",
        issues=render_issues(issues),
    )

    def _do() -> str:
        resp = _CLIENT.models.generate_content(
            model=SYNTH_MODEL,
            contents=prompt,
            config=_t.GenerateContentConfig(
                system_instruction=SYSTEM,
                temperature=0.2,
                max_output_tokens=500,
                thinking_config=_t.ThinkingConfig(
                    include_thoughts=False,
                    thinking_level=_t.ThinkingLevel.MINIMAL,
                ),
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
    return "[synthesis-error: exhausted retries]"


async def main():
    triage = json.load(open(EVAL_DIR / "golden/triage.json"))
    questions = {q["id"]: q for q in json.load(open(EVAL_DIR / "questions/main.json"))}
    b3 = [t for t in triage if t["bucket"] == "B3"]
    print(f"Synthesizing golden answers for {len(b3)} Bucket-3 questions...")
    print(f"Synthesizer: {SYNTH_MODEL} in {SYNTH_REGION}")

    out_path = EVAL_DIR / "golden/golden_b3.json"
    out = {}
    if out_path.exists():
        out = json.loads(out_path.read_text())
        print(f"  resuming from existing {len(out)} entries")

    sem = asyncio.Semaphore(8)

    async def one(t):
        qid = t["id"]
        if qid in out and "synthesis_error" not in out[qid]:
            return None
        async with sem:
            q = questions[qid]
            issues = fetch_issues_for_question(q)
            ans = await synthesize(q, issues)
            entry = {
                "question_id": qid,
                "category": q["category"],
                "n_real_issues": len(issues),
                "issue_keys_used": [i["key"] for i in issues],
                "golden_answer": ans,
                "synthesizer_model": SYNTH_MODEL,
            }
            if "[synthesis-error:" in ans:
                entry["synthesis_error"] = True
            out[qid] = entry
            return qid

    todo = [t for t in b3 if t["id"] not in out or "synthesis_error" in out[t["id"]]]
    print(f"  {len(todo)} need synthesis (others already cached)")
    done = 0
    for fut in asyncio.as_completed([one(t) for t in todo]):
        r = await fut
        if r:
            done += 1
            if done % 10 == 0:
                print(f"  [{done}/{len(todo)}] done so far")
                out_path.write_text(json.dumps(out, indent=2))

    out_path.write_text(json.dumps(out, indent=2))
    ok = sum(1 for v in out.values() if not v.get("synthesis_error"))
    print(f"\nDone. {ok}/{len(b3)} golden answers synthesized. Written to {out_path}")


if __name__ == "__main__":
    asyncio.run(main())
