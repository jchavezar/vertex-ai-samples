"""Phase 1+2: Cluster, dedup, and curate the 500-question set.

Outputs:
  eval/golden/dedup_audit.json        — cluster report
  eval/questions/main_v2_phase2.json  — curated set (Phase 2 only; Phase 3 appends new ones)
"""
from __future__ import annotations

import copy
import json
import re
from collections import Counter, defaultdict
from datetime import date, timedelta
from pathlib import Path

EVAL_DIR = Path(__file__).resolve().parent.parent
SRC = EVAL_DIR / "questions/main.json"
EXCLUDED_FILE = EVAL_DIR / "golden/excluded_qids.json"


def project_set(q):
    text = q["q"]
    projs = set(re.findall(r"\b(BUGS|CRM|OPS|PLAT|SMP)\b", text))
    if re.search(r"Customer Support", text, re.I): projs.add("CRM")
    if re.search(r"Infrastructure|SRE", text, re.I): projs.add("OPS")
    if re.search(r"Platform Engineering", text, re.I): projs.add("PLAT")
    if re.search(r"Software Bug|bug.triage", text, re.I): projs.add("BUGS")
    if re.search(r"Sample Project", text, re.I): projs.add("SMP")
    return frozenset(projs)


def keys_in(q):
    return re.findall(r"\b[A-Z]{2,6}-\d+\b", q["q"])


def primary_project(q):
    keys = keys_in(q)
    if keys:
        return keys[0].split("-")[0]
    ps = sorted(project_set(q))
    return ps[0] if ps else "?"


REL_DATE_RE = re.compile(r"-\d+[dwmy]\b")
REL_PHRASE_RE = re.compile(r"\b(last|past)\s+(\d+|few)\s+(day|week|month|hour)", re.I)
REL_CALENDAR_RE = re.compile(r"\b(today|yesterday|this week|this month|this quarter)\b", re.I)


def has_relative_date(q):
    jql = q.get("jql") or ""
    text = q["q"]
    return (REL_DATE_RE.search(jql) or REL_PHRASE_RE.search(text) or
            REL_CALENDAR_RE.search(text))


def lookup_field(text):
    t = text.lower()
    if re.search(r"\b(assignee|assigned|owner|owns|working on|who is)\b", t):
        return "assignee"
    if re.search(r"\bstatus\b|\bstate\b", t):
        return "status"
    if re.search(r"\bpriorit", t):
        return "priority"
    if re.search(r"\b(summary|title|describe|description|say|tell)\b", t):
        return "summary"
    if re.search(r"\bissue\s*type\b|\btype\b", t):
        return "issuetype"
    return "other"


def intent_signature(q):
    """Cluster signature: same signature = same template type."""
    cat = q.get("category", "?")
    text = q["q"]
    keys = keys_in(q)
    n_keys = len(keys)
    projs = project_set(q)
    n_proj = len(projs)
    rel_date = bool(has_relative_date(q))
    has_pri = bool(re.search(r"\b(highest|high|critical|low|medium|priority)\b", text, re.I))

    if cat == "lookup":
        return (cat, lookup_field(text))
    if cat == "tool-efficiency":
        # Mostly disguised lookups + count + summary
        if n_keys:
            return (cat, "lookup", lookup_field(text))
        return (cat, "count", f"proj{n_proj}", "pri" if has_pri else "nopri")
    if cat == "comments-worklogs":
        is_worklog = bool(re.search(r"\b(worklog|time|hours|log)\b", text, re.I))
        return (cat, "worklog" if is_worklog else "comments", "with_key" if n_keys else "no_key")
    if cat == "issue-links":
        is_block = bool(re.search(r"block", text, re.I))
        return (cat, "block" if is_block else "link")
    if cat == "epic-tree":
        is_child = bool(re.search(r"child|subtask|under|stories", text, re.I))
        return (cat, "children" if is_child else "parent")
    if cat in ("jql-filter", "count-aggregate", "pagination-required",
                "multi-project", "components-versions"):
        # Combine signal: project-count + topic to give better variety.
        return (cat, f"proj{n_proj}", _cap_subkey(cat, text))
    if cat == "trend":
        # Very templated — dedup aggressively
        period = "monthly" if re.search(r"month|30", text, re.I) else "weekly" if re.search(r"week|7|14", text, re.I) else "other"
        return (cat, period, "pri" if has_pri else "nopri", f"proj{n_proj}")
    if cat == "golden-anti-regression":
        return (cat, "rel" if rel_date else "abs", "with_key" if n_keys else "no_key")
    if cat == "typo-robustness":
        ttype = "key_lookup" if n_keys else ("count" if re.search(r"how many|count", text, re.I) else "search")
        return (cat, ttype)
    if cat in CAP_CATS:
        return (cat, _cap_subkey(cat, text))
    return (cat, q["id"])


TOPIC_KEYWORDS = [
    ("api", r"\bapi\b"),
    ("mobile", r"\bmobile|android|ios|battery|crash\b"),
    ("auth", r"\bauth|login|password|token|credential\b"),
    ("datetime", r"\bdatetime|timezone|date\b"),
    ("rate-limit", r"\brate.?limit|throttl\b"),
    ("docs", r"\bdocs?|documentation|openapi|tutorial\b"),
    ("fraud", r"\bfraud|scam|abuse\b"),
    ("self-service", r"\bself.?service|automation\b"),
    ("monitoring", r"\bmonitor|alert|pagerduty|observability\b"),
    ("integration", r"\bintegration|slack|webhook\b"),
    ("payments", r"\bpayment|billing|refund|charge\b"),
    ("performance", r"\bperformance|latency|slow|optimi\b"),
    ("security", r"\bsecurity|vuln|exploit|inject|leak\b"),
    ("infra", r"\binfrastructure|k8s|kubernetes|cluster|cost\b"),
    ("escalation", r"\bescalation|escalate\b"),
    ("subtask", r"\bsubtask|child\b"),
    ("priority", r"\bhigh|medium|low|critical|priority\b"),
    ("distribution", r"\bdistribution|breakdown|group|per\b"),
]


def _topic_key(text):
    t = text.lower()
    for tag, pat in TOPIC_KEYWORDS:
        if re.search(pat, t, re.I):
            return tag
    return "other"


# Sub-axis per safety/analytical category to maximise variety within the cap
REFUSAL_VERBS = [
    ("delete", r"\b(delete|drop|wipe|remove|permanently|archive)\b"),
    ("bulk-close", r"\b(close|mark.*done|mark.*duplicate)\b"),
    ("reassign", r"\b(reassign|change.*reporter|transfer ownership|grant admin|unassign)\b"),
    ("modify", r"\b(set.*priority|reset.*description|change.*status|remove.*labels|wipe.*comments)\b"),
    ("export", r"\b(export|send.*email|transfer)\b"),
]

INJECTION_TECHNIQUES = [
    ("ignore-prev", r"\bignore (all )?previous|forget you|previous safety|previous instructions|new system prompt|override\b"),
    ("persona-swap", r"\b(you are now|pretend|act as|simulation mode|dan|administrator|developer note|admin mode)\b"),
    ("encoded-payload", r"\b(base64|decode|execute|hidden instruction|comment|hex)\b|<!--"),
    ("authority-claim", r"\b(i'?m the (system )?(admin|developer)|anthropic|tip you|override code|admin_?backdoor|admin\d+)\b"),
    ("steganographic", r"\b(while|when|also|silently|in addition|together)\b"),
    ("misdirection", r"\b(translate|for debugging|debug|error recovery|new task|priority override)\b"),
]

PII_TYPES = [
    ("emails", r"\b(email|address|@)\b"),
    ("names", r"\b(customer name|reporter|developer)\b"),
    ("creds", r"\b(password|credential|secret|token|ssh|api key)\b"),
    ("payments", r"\b(credit card|billing|payment)\b"),
    ("ip-server", r"\b(ip address|server)\b"),
    ("general-pii", r"\b(personal|pii|identif|anonymiz|redact|mask)\b"),
]

ANALYTICAL_THEMES = [
    ("api-design", r"\bapi|rest|openapi\b"),
    ("mobile", r"\bmobile|android|ios|battery\b"),
    ("auth-security", r"\b(auth|security|fraud|vuln)\b"),
    ("monitoring", r"\b(monitor|alert|pagerduty|observability|incident)\b"),
    ("performance", r"\bperformance|latency|optimi\b"),
    ("docs", r"\bdocs?|documentation|tutorial\b"),
    ("datetime", r"\bdatetime|timezone\b"),
    ("rate-limit", r"\brate.?limit|throttl\b"),
    ("automation", r"\b(automation|self.?service|workflow)\b"),
    ("infra", r"\binfrastructure|k8s|cluster|databases\b"),
    ("billing-refund", r"\b(billing|refund|payment|charge)\b"),
    ("escalation", r"\b(escalation|escalate)\b"),
    ("distribution", r"\b(distribution|breakdown|group|per |compare)\b"),
    ("priority-mix", r"\b(high|medium|low|critical)\b"),
]


def _match_first(text, axes):
    for tag, pat in axes:
        if re.search(pat, text, re.I):
            return tag
    return "other"


def _cap_subkey(cat, text):
    if cat == "refusal-test":
        return _match_first(text, REFUSAL_VERBS)
    if cat == "prompt-injection":
        return _match_first(text, INJECTION_TECHNIQUES)
    if cat == "pii-sensitive":
        return _match_first(text, PII_TYPES)
    if cat in ("root-cause-synthesis", "cross-issue-analysis", "multi-step"):
        return _match_first(text, ANALYTICAL_THEMES)
    return _topic_key(text)


# === Selection rules ============================================================
# Categories where every question is genuinely unique → keep all (minus excluded):
KEEP_ALL_CATS = {
    "ambiguous",
}

# Categories of inherently varied content that we still cap at N for size balance.
CAP_CATS = {
    "refusal-test": 10,
    "prompt-injection": 10,
    "pii-sensitive": 8,
    "root-cause-synthesis": 8,
    "cross-issue-analysis": 8,
    "multi-step": 8,
    # Templated JQL-style — also cap to avoid excessive variants per topic
    "count-aggregate": 8,
    "jql-filter": 8,
    "multi-project": 8,
    "pagination-required": 6,
    "tool-efficiency": 6,
    "components-versions": 6,
}

DEDUP_TARGET = 3


def rewrite_relative_to_absolute(q):
    """Convert -30d / 'last 30 days' to absolute dates anchored to a fixed cutoff
    so the JQL stays stable. We use today's date and pre-compute the window."""
    today = date(2026, 5, 21)  # frozen reference
    q = copy.deepcopy(q)
    jql = q.get("jql") or ""
    text = q.get("q") or ""

    def sub_jql(jql_in):
        def repl(m):
            n = int(m.group(0)[1:-1])
            unit = m.group(0)[-1]
            mult = {"d": 1, "w": 7, "m": 30, "y": 365}[unit]
            start = today - timedelta(days=n * mult)
            return f'"{start.isoformat()}"'
        return REL_DATE_RE.sub(repl, jql_in)

    q["jql"] = sub_jql(jql)
    # Mark in tags
    tags = list(q.get("tags", []))
    if "absolute-date" not in tags:
        tags.append("absolute-date")
    q["tags"] = tags
    return q


def main():
    data = json.load(open(SRC))
    excluded = set(json.load(open(EXCLUDED_FILE)))
    print(f"Loaded {len(data)} questions, {len(excluded)} excluded.")

    clusters = defaultdict(list)
    for q in data:
        sig = intent_signature(q)
        clusters[sig].append(q)

    for sig, qs in clusters.items():
        qs.sort(key=lambda x: x["id"])

    audit = []
    keep_ids = set()
    rewritten = {}  # id -> new q dict
    drop_reasons = Counter()

    for sig, qs in clusters.items():
        cat = sig[0]
        ids = [q["id"] for q in qs]

        if cat in KEEP_ALL_CATS:
            recommended = []
            for q in qs:
                if q["id"] in excluded:
                    drop_reasons["excluded"] += 1
                    continue
                if has_relative_date(q):
                    drop_reasons["relative_date"] += 1
                    continue
                recommended.append(q["id"])
                keep_ids.add(q["id"])
            audit.append({
                "cluster_id": str(sig),
                "category": cat,
                "member_qids": ids,
                "count": len(qs),
                "keep_sample_size": len(recommended),
                "recommended_keep": recommended,
                "reason": "always-keep category (inherently unique)",
            })
            continue

        # CAP categories: the cluster sig already includes topic — keep 1 per topic
        # then top up to one entry per topic until exhausted.
        if cat in CAP_CATS:
            # All members of this cluster have the same sub-key already
            picks = []
            for q in qs:
                if q["id"] in excluded:
                    drop_reasons["excluded"] += 1
                    continue
                if has_relative_date(q):
                    if REL_DATE_RE.search(q.get("jql") or ""):
                        # Rewriteable
                        rewritten[q["id"]] = rewrite_relative_to_absolute(q)
                        picks.append(q)
                    else:
                        drop_reasons["relative_date"] += 1
                    continue
                picks.append(q)
            # Keep first one per cluster (topic) — rest dropped
            recommended = [picks[0]["id"]] if picks else []
            if len(picks) > 1:
                drop_reasons["topic_redundant"] += len(picks) - 1
            keep_ids.update(recommended)
            audit.append({
                "cluster_id": str(sig),
                "category": cat,
                "member_qids": ids,
                "count": len(qs),
                "keep_sample_size": len(recommended),
                "recommended_keep": recommended,
                "reason": f"cap category — one representative per topic ({sig[-1]})",
            })
            continue

        # Dedup target — but vary by cluster size
        target = DEDUP_TARGET
        if cat == "trend":
            target = 1  # heavily dedup trend templates
        elif cat == "typo-robustness":
            target = 4  # keep more variety
        elif cat == "tool-efficiency":
            target = 2  # most are duplicates of lookups

        # Filter out excluded
        in_play = [q for q in qs if q["id"] not in excluded]
        # First pass: pick absolute-date variants; relative-date ones get rewritten if needed
        absolutes = [q for q in in_play if not has_relative_date(q)]
        relatives = [q for q in in_play if has_relative_date(q)]

        # Diversity-bucket by project
        def diversify(pool, n):
            by_proj = defaultdict(list)
            for q in pool:
                by_proj[primary_project(q)].append(q)
            picks = []
            order = ["BUGS", "CRM", "OPS", "PLAT", "SMP", "?"]
            for proj in order:
                if proj in by_proj and len(picks) < n:
                    picks.append(by_proj[proj][0])
            for q in pool:
                if len(picks) >= n:
                    break
                if q not in picks:
                    picks.append(q)
            return picks

        chosen = []
        # Prefer absolutes
        if absolutes:
            chosen.extend(diversify(absolutes, target))
        # If still under target, rewrite relatives to absolute
        if len(chosen) < target and relatives:
            need = target - len(chosen)
            rels_picked = diversify(relatives, need)
            for q in rels_picked:
                if REL_DATE_RE.search(q.get("jql") or ""):
                    new_q = rewrite_relative_to_absolute(q)
                    rewritten[q["id"]] = new_q
                    chosen.append(q)
                # else can't rewrite cleanly (phrase-only) — drop

        recommended = [q["id"] for q in chosen]
        keep_ids.update(recommended)
        dropped = len(qs) - len(recommended)
        if dropped:
            drop_reasons["templated_duplicate"] += dropped
        audit.append({
            "cluster_id": str(sig),
            "category": cat,
            "member_qids": ids,
            "count": len(qs),
            "keep_sample_size": len(recommended),
            "recommended_keep": recommended,
            "reason": (f"templated cluster — sampled for project variety (target={target})"
                       if len(qs) > target else "small cluster — kept available"),
        })

    # Post-pass: enforce per-category caps
    by_cat = defaultdict(list)
    qid_to_obj = {q["id"]: q for q in data}
    for qid in keep_ids:
        by_cat[qid_to_obj[qid].get("category", "?")].append(qid)
    for cat, cap in CAP_CATS.items():
        kept = sorted(by_cat[cat])  # stable
        if len(kept) > cap:
            drop = kept[cap:]
            for qid in drop:
                keep_ids.discard(qid)
                drop_reasons["cap_overflow"] += 1

    audit.sort(key=lambda x: -x["count"])

    out_audit = EVAL_DIR / "golden/dedup_audit.json"
    out_audit.write_text(json.dumps(audit, indent=2))
    print(f"\nWrote audit → {out_audit}")
    print(f"Kept {len(keep_ids)} of {len(data)} questions ({len(rewritten)} relative→absolute rewrites).")
    print(f"Drop reasons: {dict(drop_reasons)}")

    cat_before = Counter(q.get("category", "?") for q in data)
    cat_after = Counter(q.get("category", "?") for q in data if q["id"] in keep_ids)
    print("\nPer-category before → after:")
    for c in sorted(cat_before):
        print(f"  {c:30s} {cat_before[c]:3d} → {cat_after[c]:3d}")

    # Build curated set (with rewrites)
    curated = []
    for q in data:
        if q["id"] not in keep_ids:
            continue
        if q["id"] in rewritten:
            curated.append(rewritten[q["id"]])
        else:
            curated.append(q)

    out_curated = EVAL_DIR / "questions/main_v2_phase2.json"
    out_curated.write_text(json.dumps(curated, indent=2))
    print(f"\nWrote curated (phase 2) → {out_curated} (n={len(curated)})")


if __name__ == "__main__":
    main()
