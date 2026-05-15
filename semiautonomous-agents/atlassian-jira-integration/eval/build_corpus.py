"""Build a multi-project Jira corpus for production-grade eval.

Creates 4 projects (BUGS, CRM, OPS, PLAT) with:
- Realistic epics + stories + subtasks (research-grounded content via Claude)
- Issue links (blocks, duplicates, relates)
- Components, fix versions
- Comments + worklogs on a subset
- Labels including "eval-corpus" so the user can bulk-delete later

All issues get an "eval-corpus" label for easy cleanup:
  cd eval && .venv/bin/python -c "import asyncio,jira_oracle; asyncio.run(jira_oracle.run_jql('labels = eval-corpus'))"

Usage:
    python build_corpus.py            # build everything
    python build_corpus.py --dry-run  # preview without writing
"""
from __future__ import annotations

import argparse
import asyncio
import base64
import json
import os
import random
import re
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import httpx
from anthropic import AsyncAnthropicVertex

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
import jira_oracle as jo  # noqa: E402

SITE = jo.SITE_URL
EMAIL = jo.ATLASSIAN_EMAIL
TOKEN = jo.ATLASSIAN_API_TOKEN
HDR = {
    "Authorization": "Basic " + base64.b64encode(f"{EMAIL}:{TOKEN}".encode()).decode(),
    "Accept": "application/json",
    "Content-Type": "application/json",
}
LEAD = os.environ.get("ATLASSIAN_LEAD_ACCOUNT_ID", "712020:83307bf3-9871-4fc6-bba8-a660f79810c2")
EVAL_LABEL = "eval-corpus"

REGION = os.environ.get("JUDGE_REGION", "us-east5")
PROJECT = os.environ.get("JUDGE_PROJECT", "vtxdemos")
MODEL = os.environ.get("GEN_MODEL", "claude-opus-4-5@20251101")


# --- Project specs --------------------------------------------------------

@dataclass
class ProjectSpec:
    key: str
    name: str
    domain: str  # used to seed Claude with what kind of tickets to generate
    template: str = "com.pyxis.greenhopper.jira:gh-simplified-agility-scrum"
    project_type: str = "software"
    epics: int = 4   # 4 epics × ~6 stories × ~3 subtasks ≈ 90 issues per project
    stories_per_epic: int = 6
    subtasks_per_story: int = 3
    components: list[str] = field(default_factory=list)
    fix_versions: list[str] = field(default_factory=list)


PROJECTS = [
    ProjectSpec(
        key="BUGS",
        name="Software Bug Triage",
        domain=("A SaaS web application bug tracker. Issues are real-feeling software bugs "
                "(crashes, regressions, perf issues, race conditions, memory leaks, UI glitches, "
                "API errors, mobile-only bugs). Affects different components: auth, billing, "
                "search, dashboard, mobile-ios, mobile-android, api-v2."),
        components=["auth", "billing", "search", "dashboard", "mobile-ios", "mobile-android", "api-v2"],
        fix_versions=["v2.4.0", "v2.4.1", "v2.5.0", "v3.0.0-beta"],
    ),
    ProjectSpec(
        key="CRM",
        name="Customer Support",
        domain=("Customer support tickets from end users of a B2C marketplace app. Mix of "
                "billing disputes, account access issues, refund requests, app crashes "
                "reported by users, feature requests, payment failures. Each ticket has a "
                "real-feeling user description with steps to reproduce or context."),
        components=["billing-support", "account-recovery", "payments", "refunds", "feature-requests"],
        fix_versions=["Q2-2026", "Q3-2026"],
    ),
    ProjectSpec(
        key="OPS",
        name="Infrastructure & SRE",
        domain=("SRE / infrastructure tickets — incidents, postmortems, capacity issues, "
                "deployment failures, certificate expiries, monitoring alerts, network "
                "outages, db migrations, kubernetes/helm chart issues, CI/CD failures."),
        components=["k8s-prod", "k8s-staging", "ci-cd", "observability", "networking", "databases"],
        fix_versions=["sprint-22", "sprint-23", "sprint-24"],
    ),
    ProjectSpec(
        key="PLAT",
        name="Platform Engineering",
        domain=("Platform engineering work — internal developer platform improvements, "
                "service-mesh upgrades, golden-path templates, paved-road tooling, library "
                "upgrades, internal API design, RBAC enhancements, cost-optimization work."),
        components=["service-mesh", "platform-libs", "rbac", "cost-optimization", "developer-experience"],
        fix_versions=["v1.0.0", "v1.1.0", "v2.0.0"],
    ),
]


# --- HTTP helpers ----------------------------------------------------------

class Stats:
    def __init__(self):
        self.created_projects = []
        self.created_issues = []
        self.created_links = 0
        self.created_comments = 0
        self.created_worklogs = 0
        self.created_versions = 0
        self.created_components = 0


async def jget(client: httpx.AsyncClient, path: str, **kw) -> dict[str, Any]:
    r = await client.get(f"{SITE}{path}", headers=HDR, timeout=30, **kw)
    r.raise_for_status()
    return r.json()


async def jpost(client: httpx.AsyncClient, path: str, json_body: dict[str, Any] | None = None,
                expect_codes: tuple = (200, 201, 204)) -> dict[str, Any] | None:
    r = await client.post(f"{SITE}{path}", headers=HDR, json=json_body or {}, timeout=60)
    if r.status_code not in expect_codes:
        raise RuntimeError(f"POST {path} → {r.status_code}: {r.text[:300]}")
    if not r.text:
        return None
    try:
        return r.json()
    except Exception:
        return None


async def jdelete(client: httpx.AsyncClient, path: str, expect: tuple = (200, 204)) -> bool:
    r = await client.delete(f"{SITE}{path}", headers=HDR, timeout=30)
    return r.status_code in expect


# --- Project creation ------------------------------------------------------

async def create_project(client: httpx.AsyncClient, spec: ProjectSpec, dry: bool = False) -> dict[str, Any] | None:
    payload = {
        "key": spec.key,
        "name": spec.name,
        "leadAccountId": LEAD,
        "projectTypeKey": spec.project_type,
        "projectTemplateKey": spec.template,
        "description": f"[{EVAL_LABEL}] Eval corpus — {spec.domain[:200]}",
    }
    if dry:
        print(f"  [DRY] would POST /rest/api/3/project key={spec.key}")
        return {"key": spec.key, "id": "DRY"}
    # Idempotent: if project exists, return its info
    existing = await client.get(f"{SITE}/rest/api/3/project/{spec.key}", headers=HDR, timeout=30)
    if existing.status_code == 200:
        print(f"  [{spec.key}] already exists, skipping create")
        return existing.json()
    out = await jpost(client, "/rest/api/3/project", payload)
    print(f"  [{spec.key}] created: id={out.get('id')}")
    return out


# --- Description-builder using Claude --------------------------------------

GEN_SYSTEM = (
    "You generate realistic Jira issue content for an evaluation corpus. "
    "Issues should feel like real bugs/tickets/postmortems written by real engineers, "
    "not generic placeholders. Return ONLY valid JSON, no prose."
)

EPIC_TPL = """Generate {n} epic-level initiatives for a Jira project.

Project: {name} ({key})
Domain: {domain}

Each epic represents a 1-3 month initiative. Output JSON array:
[
  {{
    "summary": "<Epic title, 6-12 words>",
    "description": "<3-5 sentences explaining the goal and scope>",
    "labels": ["initiative", "<theme>"],
    "stories": [
      {{
        "summary": "<Story title, 6-12 words>",
        "description": "<5-15 sentences with acceptance criteria, technical notes, or repro steps. Realistic and specific.>",
        "priority": "Highest|High|Medium|Low|Lowest",
        "labels": ["<label1>", "<label2>"],
        "subtasks": [
          {{"summary": "<Subtask, 5-10 words>", "description": "<2-4 sentences>"}}
        ]
      }}
    ]
  }}
]

Generate exactly {n} epics, with exactly {s} stories each, and exactly {st} subtasks per story.
Each story needs realistic, varied content — never repeat the same description. Vary priority distribution naturally.
Use real component names from this project: {components}.
"""


def _strip(t: str) -> str:
    t = t.strip()
    if t.startswith("```"):
        t = re.sub(r"^```(?:json)?\n", "", t)
        t = re.sub(r"\n```$", "", t)
    return t


async def gen_content(spec: ProjectSpec, sem: asyncio.Semaphore, llm: AsyncAnthropicVertex) -> list[dict[str, Any]]:
    prompt = EPIC_TPL.format(
        n=spec.epics, name=spec.name, key=spec.key, domain=spec.domain,
        s=spec.stories_per_epic, st=spec.subtasks_per_story,
        components=", ".join(spec.components),
    )
    async with sem:
        for attempt in range(4):
            try:
                resp = await llm.messages.create(
                    model=MODEL, max_tokens=16000, system=GEN_SYSTEM,
                    messages=[{"role": "user", "content": prompt}],
                )
                return json.loads(_strip(resp.content[0].text))
            except Exception as e:
                if attempt < 3:
                    await asyncio.sleep(min(60, 2 ** attempt))
                    continue
                print(f"  [{spec.key}] generation failed: {e}", file=sys.stderr)
                return []


# --- Issue create ----------------------------------------------------------

def adf(text: str) -> dict[str, Any]:
    """Convert plain text to Atlassian Document Format (paragraph blocks)."""
    paragraphs = []
    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue
        paragraphs.append({
            "type": "paragraph",
            "content": [{"type": "text", "text": line}],
        })
    if not paragraphs:
        paragraphs = [{"type": "paragraph", "content": [{"type": "text", "text": " "}]}]
    return {"version": 1, "type": "doc", "content": paragraphs}


async def create_issue(client: httpx.AsyncClient, project_key: str, summary: str,
                       description: str, issuetype: str = "Story",
                       parent_key: str | None = None, priority: str | None = None,
                       labels: list[str] | None = None, components: list[str] | None = None,
                       dry: bool = False) -> dict[str, Any] | None:
    fields: dict[str, Any] = {
        "project": {"key": project_key},
        "summary": summary[:240],
        "description": adf(description),
        "issuetype": {"name": issuetype},
        "labels": (labels or []) + [EVAL_LABEL],
    }
    if parent_key:
        fields["parent"] = {"key": parent_key}
    if priority:
        fields["priority"] = {"name": priority}
    if components:
        fields["components"] = [{"name": c} for c in components]
    if dry:
        return {"key": f"{project_key}-DRY"}
    try:
        out = await jpost(client, "/rest/api/3/issue", {"fields": fields})
        return out
    except Exception as e:
        # Many Jira instances reject Sub-task without correct issuetype name; retry
        if issuetype == "Subtask":
            fields["issuetype"] = {"name": "Sub-task"}
            try:
                return await jpost(client, "/rest/api/3/issue", {"fields": fields})
            except Exception as e2:
                print(f"   subtask retry failed: {str(e2)[:200]}", file=sys.stderr)
        print(f"   create failed: {str(e)[:200]}", file=sys.stderr)
        return None


# --- Comments + worklogs + links + components + versions -----------------

async def add_comment(client: httpx.AsyncClient, key: str, body: str) -> bool:
    try:
        await jpost(client, f"/rest/api/3/issue/{key}/comment", {"body": adf(body)})
        return True
    except Exception:
        return False


async def add_worklog(client: httpx.AsyncClient, key: str, time_spent: str = "1h",
                      comment: str = "Initial scoping") -> bool:
    try:
        await jpost(client, f"/rest/api/3/issue/{key}/worklog",
                    {"comment": adf(comment), "timeSpent": time_spent})
        return True
    except Exception:
        return False


async def link_issues(client: httpx.AsyncClient, inward_key: str, outward_key: str,
                      link_type: str = "Blocks") -> bool:
    try:
        await jpost(client, "/rest/api/3/issueLink",
                    {"type": {"name": link_type},
                     "inwardIssue": {"key": inward_key},
                     "outwardIssue": {"key": outward_key}})
        return True
    except Exception:
        return False


async def create_component(client: httpx.AsyncClient, project_key: str, name: str) -> bool:
    try:
        await jpost(client, "/rest/api/3/component",
                    {"name": name, "project": project_key, "leadAccountId": LEAD})
        return True
    except Exception:
        return False


async def create_version(client: httpx.AsyncClient, project_id: str, name: str) -> bool:
    try:
        await jpost(client, "/rest/api/3/version",
                    {"name": name, "projectId": int(project_id)})
        return True
    except Exception:
        return False


# --- Main orchestration ----------------------------------------------------

async def build_one(spec: ProjectSpec, sem: asyncio.Semaphore, llm: AsyncAnthropicVertex,
                    client: httpx.AsyncClient, stats: Stats, dry: bool):
    print(f"\n=== Building project {spec.key} ({spec.name}) ===")

    # 1. Create project (idempotent)
    proj = await create_project(client, spec, dry=dry)
    if not proj:
        print(f"  [{spec.key}] skipped — could not create")
        return
    project_id = str(proj.get("id"))
    stats.created_projects.append(spec.key)

    # 2. Components
    if not dry:
        for c in spec.components:
            ok = await create_component(client, spec.key, c)
            if ok:
                stats.created_components += 1
        for v in spec.fix_versions:
            ok = await create_version(client, project_id, v)
            if ok:
                stats.created_versions += 1

    # 3. Generate content via Claude
    print(f"  [{spec.key}] generating content...")
    epics = await gen_content(spec, sem, llm)
    if not epics:
        print(f"  [{spec.key}] no content generated; abort")
        return
    print(f"  [{spec.key}] got {len(epics)} epics")

    # 4. Create issues — Epic → Story → Subtask
    issues_in_proj: list[dict[str, Any]] = []
    for ep in epics[:spec.epics]:
        ep_issue = await create_issue(
            client, spec.key, ep["summary"], ep.get("description", ""),
            issuetype="Epic", labels=ep.get("labels", []), dry=dry,
        )
        if not ep_issue:
            continue
        epic_key = ep_issue["key"]
        stats.created_issues.append(epic_key)
        issues_in_proj.append({"key": epic_key, "type": "Epic", "summary": ep["summary"]})
        print(f"    Epic {epic_key}")

        for story in ep.get("stories", [])[:spec.stories_per_epic]:
            story_components = random.sample(spec.components, min(2, len(spec.components)))
            st_issue = await create_issue(
                client, spec.key, story["summary"], story.get("description", ""),
                issuetype="Story", parent_key=epic_key,
                priority=story.get("priority", "Medium"),
                labels=story.get("labels", []),
                components=story_components, dry=dry,
            )
            if not st_issue:
                continue
            story_key = st_issue["key"]
            stats.created_issues.append(story_key)
            issues_in_proj.append({"key": story_key, "type": "Story",
                                   "summary": story["summary"], "epic": epic_key})

            # Subtasks
            for sub in story.get("subtasks", [])[:spec.subtasks_per_story]:
                sub_issue = await create_issue(
                    client, spec.key, sub["summary"], sub.get("description", ""),
                    issuetype="Subtask", parent_key=story_key, dry=dry,
                )
                if sub_issue:
                    stats.created_issues.append(sub_issue["key"])
                    issues_in_proj.append({"key": sub_issue["key"], "type": "Subtask",
                                           "summary": sub["summary"], "parent": story_key})

    # 5. Cross-link some issues (Blocks, Duplicates, Relates)
    stories_only = [i for i in issues_in_proj if i["type"] == "Story"]
    if len(stories_only) >= 4 and not dry:
        for _ in range(min(15, len(stories_only) // 2)):
            a, b = random.sample(stories_only, 2)
            ok = await link_issues(client, a["key"], b["key"],
                                   random.choice(["Blocks", "Relates", "Duplicate"]))
            if ok:
                stats.created_links += 1

    # 6. Add comments + worklogs to a subset (~30%) of stories
    if not dry:
        comment_seeds = [
            "Reproduced on staging. The error happens on the auth callback when the cookie is missing.",
            "Looks like this regressed in v2.4.0 — bisecting now.",
            "Customer escalated; promised a fix by EOW.",
            "Workaround: clear local storage and retry. Permanent fix in next sprint.",
            "Postmortem doc: https://example.com/pm/2026-q2/incident-2331 — root cause was missing connection-pool tuning.",
            "Patched and deployed. Confirming with affected users.",
            "PR open. Reviewers: @platform-team. Tests added.",
            "Spike to investigate. ETA: 3 days.",
        ]
        for s in random.sample(stories_only, min(len(stories_only) // 3, len(stories_only))):
            await add_comment(client, s["key"], random.choice(comment_seeds))
            stats.created_comments += 1
            if random.random() < 0.5:
                await add_worklog(client, s["key"], random.choice(["1h", "2h", "30m", "4h"]),
                                  random.choice(["Initial scoping", "Reproduced + root-caused",
                                                 "Patch + tests + PR opened", "Postmortem write-up"]))
                stats.created_worklogs += 1


async def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--projects", nargs="*", default=[s.key for s in PROJECTS],
                    help="subset of project keys to build")
    args = ap.parse_args()

    stats = Stats()
    llm = AsyncAnthropicVertex(region=REGION, project_id=PROJECT)
    gen_sem = asyncio.Semaphore(2)

    async with httpx.AsyncClient() as client:
        for spec in PROJECTS:
            if spec.key not in args.projects:
                continue
            await build_one(spec, gen_sem, llm, client, stats, dry=args.dry_run)

    print("\n=== STATS ===")
    print(f"  Projects:    {stats.created_projects}")
    print(f"  Issues:      {len(stats.created_issues)}")
    print(f"  Links:       {stats.created_links}")
    print(f"  Comments:    {stats.created_comments}")
    print(f"  Worklogs:    {stats.created_worklogs}")
    print(f"  Components:  {stats.created_components}")
    print(f"  Versions:    {stats.created_versions}")
    print(f"\nAll issues tagged with label `{EVAL_LABEL}` for cleanup.")


if __name__ == "__main__":
    asyncio.run(main())
