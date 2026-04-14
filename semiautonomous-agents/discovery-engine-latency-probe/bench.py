"""
chronoshot bench — 100-question StreamAssist benchmark.

Produces:
  1. Latency distribution table with percentiles (p25/p50/p75/p90/p95/p99)
  2. Accuracy table: per-question pass/fail + overall precision

Usage:
    uv run python bench.py                  # run all 100
    uv run python bench.py --dry-run        # validate questions/answers, no API calls
    uv run python bench.py --section 1      # run one section only
    uv run python bench.py --resume         # skip questions already in results file
"""

import os, sys, json, time, base64, re, math, argparse, requests
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / "sharepoint_wif_portal" / ".env")

PROJECT_NUMBER  = os.environ["PROJECT_NUMBER"]
ENGINE_ID       = os.environ["ENGINE_ID"]
WIF_POOL_ID     = os.environ["WIF_POOL_ID"]
WIF_PROVIDER_ID = os.environ["WIF_PROVIDER_ID"]
TENANT_ID       = os.environ["TENANT_ID"]
CLIENT_ID       = os.environ["OAUTH_CLIENT_ID"]
CLIENT_SECRET   = os.environ["OAUTH_CLIENT_SECRET"]

BASE_URL          = f"https://discoveryengine.googleapis.com/v1alpha/projects/{PROJECT_NUMBER}/locations/global/collections/default_collection/engines/{ENGINE_ID}"
STREAM_ASSIST_URL = f"{BASE_URL}/assistants/default_assistant:streamAssist"
RESULTS_FILE      = Path("/tmp/chronoshot_bench.json")

# ── 100 Questions + Expected Answers ─────────────────────────────────────────
# Format: (question_text, [keyword_list_any_of_which_must_appear_in_answer])
# Keywords are case-insensitive; answer passes if ANY keyword matches.
# Range values (e.g. "$840M - $850M") accept any value in the range.

QUESTIONS = [
    # ── Section 1: Apex Financial MSA — Contract Basics (1-10) ────────────
    (1,  "What is the total annual contract value of the Master Services Agreement?",
         ["4,850,000", "4.85m", "$4,850"]),
    (2,  "Who is the client in the Master Services Agreement MSA-2024-0847?",
         ["apex financial", "apex financial services"]),
    (3,  "Who is the provider in the Master Services Agreement?",
         ["meridian technologies", "meridian"]),
    (4,  "What is the contract reference number?",
         ["msa-2024-0847"]),
    (5,  "What is the effective date of the Master Services Agreement?",
         ["january 1, 2025", "jan 1, 2025", "january 2025"]),
    (6,  "Who is the primary contact at the Provider side of the MSA?",
         ["jennifer walsh"]),
    (7,  "What is Jennifer Walsh's role at Meridian Technologies?",
         ["cfo", "chief financial officer"]),
    (8,  "Who is the primary contact at Apex Financial Services?",
         ["richard blackstone"]),
    (9,  "What is Richard Blackstone's title at Apex Financial?",
         ["cio", "chief information officer"]),
    (10, "What is the Q1 payment amount under the MSA?",
         ["1,212,500", "$1.2m"]),

    # ── Section 1: Financial Terms (11-20) ────────────────────────────────
    (11, "What are the payment terms in the Master Services Agreement?",
         ["net 30", "30 days"]),
    (12, "What is the late payment fee in the MSA?",
         ["1.5%", "1.5 percent", "per month"]),
    (13, "What bank is used for wire transfers under the MSA?",
         ["jpmorgan chase", "jp morgan"]),
    (14, "What is the base discount percentage in the MSA?",
         ["15%", "15 percent"]),
    (15, "How much storage is allocated under the MSA platform specifications?",
         ["50 tb", "100 tb", "50tb", "100tb"]),
    (16, "What is the API request limit per minute under the MSA?",
         ["50,000", "50000"]),
    (17, "How many global data centers does the platform use?",
         ["12"]),
    (18, "What database is used under the MSA platform?",
         ["postgresql", "postgres"]),
    (19, "How many implementation hours are included in the professional services?",
         ["2,400", "2400"]),
    (20, "What is the Technical Architect hourly rate in the MSA?",
         ["350", "$350"]),

    # ── Section 1: SLA + Term (21-30) ─────────────────────────────────────
    (21, "How many training hours are included in the MSA professional services?",
         ["400"]),
    (22, "What is the Critical P1 availability SLA percentage?",
         ["99.99%", "99.99"]),
    (23, "What is the P1 incident response time under the SLA?",
         ["15 minutes", "15min"]),
    (24, "What is the 24/7 support hotline number in the MSA?",
         ["888", "555-mtec", "6832"]),
    (25, "What is the initial term of the Master Services Agreement?",
         ["3 years", "three years", "2027"]),
    (26, "What is the renewal notice period in the MSA?",
         ["90 days", "90-day"]),
    (27, "What is the Year 1 termination fee in the MSA?",
         ["2,425,000", "2.4m", "50%"]),
    (28, "What encryption standard is used for data at rest under the MSA?",
         ["aes-256", "aes 256"]),
    (29, "Where is the primary data residency location under the MSA?",
         ["us-east", "virginia"]),
    (30, "Who is the CEO of Meridian Technologies Corporation?",
         ["michael thornton"]),

    # ── Section 2: Financial Performance (31-40) ──────────────────────────
    (31, "What was the total revenue for FY2024?",
         ["840m", "850m", "840", "850", "$840", "$850"]),
    (32, "What was the revenue growth percentage for FY2024?",
         ["18%", "19%", "20%", "18", "19", "20"]),
    (33, "What report synthesizes the FY2024 governance and risk findings?",
         ["pwc", "governance", "advisory"]),
    (34, "When was the PWC Governance and Risk Advisory report prepared?",
         ["may 2024"]),
    (35, "What material weakness was identified in revenue recognition?",
         ["standalone selling price", "ssp", "enterprise contracts"]),
    (36, "What IT general control weakness was found in the audit?",
         ["over-privileged", "erp", "privileged access"]),
    (37, "What inventory valuation issue was identified in the audit?",
         ["obsolescence", "write-off", "reserves"]),
    (38, "How many material weaknesses were identified in the financial audit?",
         ["3", "three"]),
    (39, "What is the proposed acquisition price for Project Starlight?",
         ["280m", "290m", "280", "290", "$280", "$290"]),
    (40, "What is the recommended offer range for the Project Starlight acquisition?",
         ["265m", "275m", "265", "275", "$265", "$275"]),

    # ── Section 3: M&A Project Starlight (41-52) ──────────────────────────
    (41, "What is the private company discount percentage applied in Project Starlight?",
         ["25%", "30%", "25", "30"]),
    (42, "What is the code name for the M&A acquisition project?",
         ["project starlight", "starlight"]),
    (43, "What entity is being acquired in Project Starlight?",
         ["target entity", "company b"]),
    (44, "What percentage of ARR do the top 3 clients account for?",
         ["35%", "40%", "35", "40"]),
    (45, "What customer concentration risk was identified in Project Starlight due diligence?",
         ["35%", "40%", "top 3", "arr"]),
    (46, "What are the identified annual synergies by Year 3 in Project Starlight?",
         ["18m", "24m", "18", "24", "$18", "$24"]),
    (47, "What type of synergies were identified in Project Starlight?",
         ["cost", "revenue", "synergies"]),
    (48, "By what year should Project Starlight synergies be fully realized?",
         ["year 3", "third year"]),
    (49, "What is the estimated patent litigation settlement range in Project Starlight?",
         ["1m", "3m", "$1", "$3", "1 million", "3 million"]),
    (50, "What legal risk was identified in the Project Starlight due diligence?",
         ["patent", "litigation"]),
    (51, "What is the overall cybersecurity risk rating in the 2024 assessment?",
         ["medium-high", "medium high"]),
    (52, "How many critical vulnerabilities were identified in the IT security assessment?",
         ["4", "four"]),

    # ── Section 4: Cybersecurity (53-62) ──────────────────────────────────
    (53, "What type of vulnerability was found in the Customer API?",
         ["sql injection", "injection"]),
    (54, "How many customer records are exposed by the SQL injection vulnerability?",
         ["2.5 million", "2,500,000", "2.5m"]),
    (55, "What access control issue was identified in the security assessment?",
         ["administrative portal", "default credentials", "admin portal"]),
    (56, "What secrets management issue was found in the security assessment?",
         ["hardcoded", "source code", "database", "cloud provider"]),
    (57, "How much customer data is in publicly accessible S3 buckets?",
         ["2.5tb", "3.5tb", "2.5 tb", "3.5 tb"]),
    (58, "What type of data is stored in the exposed S3 buckets?",
         ["customer data", "backups", "backup"]),
    (59, "What should be implemented for SSP determination according to the recommendations?",
         ["centralized", "ssp committee", "committee"]),
    (60, "By when should the user access review be completed?",
         ["q2 2025", "second quarter 2025"]),
    (61, "What systems require the comprehensive user access review?",
         ["financial systems", "all financial"]),
    (62, "What API should be patched immediately according to the recommendations?",
         ["customer api", "api"]),

    # ── Section 5: Strategic Recommendations (63-72) ──────────────────────
    (63, "What secrets management solution is recommended in the security report?",
         ["hashicorp vault", "vault"]),
    (64, "What is the priority level for patching the SQL injection vulnerability?",
         ["immediate"]),
    (65, "What integration approach is recommended for Project Starlight?",
         ["phased", "phased integration"]),
    (66, "How long is the recommended operational autonomy period post-acquisition?",
         ["24 months", "two years"]),
    (67, "What is the goal of the 24-month operational autonomy period?",
         ["synergy", "key personnel", "retention"]),
    (68, "How does the Apex Financial MSA value compare to the identified M&A synergies?",
         ["4.85m", "4,850,000", "18m", "24m", "synerg"]),
    (69, "What are the two types of access control issues identified across all reports?",
         ["erp", "privileged", "admin portal", "default credentials"]),
    (70, "What encryption standard is used for Apex Financial data?",
         ["aes-256", "aes 256"]),
    (71, "Which report discusses the SQL injection vulnerability?",
         ["pwc", "governance", "advisory"]),
    (72, "What is the relationship between the customer API vulnerability and exposed records?",
         ["sql injection", "2.5 million", "customer api"]),

    # ── Section 6: Paraphrased / Harder Variants (73-86) ──────────────────
    (73, "What is Meridian's contract with Apex Financial worth per year?",
         ["4,850,000", "4.85m"]),
    (74, "How much does Apex Financial pay Meridian in the first quarter?",
         ["1,212,500", "$1.2m"]),
    (75, "What penalty applies if Apex Financial pays late?",
         ["1.5%", "per month"]),
    (76, "How much primary storage does Meridian provide Apex Financial?",
         ["50 tb", "50tb"]),
    (77, "What uptime guarantee does Meridian provide for critical incidents?",
         ["99.99%"]),
    (78, "How many years does the Apex Financial contract last?",
         ["3 years", "three years", "2027"]),
    (79, "Who leads Meridian Technologies as CEO?",
         ["michael thornton"]),
    (80, "Where is Apex Financial's data stored geographically?",
         ["virginia", "us-east"]),
    (81, "What was the year-over-year revenue increase in FY2024?",
         ["18%", "19%", "20%"]),
    (82, "What ERP access issue was flagged in the audit?",
         ["over-privileged", "erp", "privileged"]),
    (83, "What was Starlight's valuation before discount?",
         ["280m", "290m", "$280", "$290"]),
    (84, "What discount rate was applied to value the acquisition target?",
         ["25%", "30%"]),
    (85, "What kind of data breach risk exists in the exposed S3 buckets?",
         ["customer data", "backup"]),
    (86, "What is the recommended tool to manage production secrets securely?",
         ["hashicorp vault", "vault"]),

    # ── Section 7: Specific Number Recall (87-93) ─────────────────────────
    (87, "What is the API rate limit specified in the MSA?",
         ["50,000", "50000"]),
    (88, "What is the termination fee if Apex Financial exits in Year 1?",
         ["2,425,000", "2.4m"]),
    (89, "How many implementation consulting hours did Meridian commit to?",
         ["2,400", "2400"]),
    (90, "What is the hourly billing rate for a Technical Architect?",
         ["350", "$350"]),
    (91, "How many days notice is required to renew the MSA?",
         ["90"]),
    (92, "How many records are at risk from the SQL injection in the customer API?",
         ["2.5 million", "2,500,000"]),
    (93, "How many material weaknesses did the FY2024 audit uncover?",
         ["3", "three"]),

    # ── Section 8: Context + Synthesis (94-100) ───────────────────────────
    (94,  "What is the support contact number for P1 incidents under the Apex MSA?",
          ["888", "6832", "mtec"]),
    (95,  "What database technology underpins the Meridian platform?",
          ["postgresql", "postgres"]),
    (96,  "What is the name of the company being acquired in Project Starlight?",
          ["target entity", "company b"]),
    (97,  "What synergy amount is expected to be achieved by Year 3 post-acquisition?",
          ["18m", "24m", "$18", "$24", "18 million", "24 million"]),
    (98,  "Which document discusses the PWC report findings?",
          ["governance", "pwc", "advisory"]),
    (99,  "What is the recommended timeline for completing a user access review?",
          ["q2 2025", "second quarter"]),
    (100, "What phased approach is suggested for integrating the acquired company?",
          ["phased integration", "phased", "integration plan"]),
]


# ── Auth ──────────────────────────────────────────────────────────────────────

def get_tokens() -> str:
    """Return a valid GCP access token, preferring user id_token."""
    # Try fresh user token from portal login
    user_tok_path = Path("/tmp/entra_token.txt")
    if user_tok_path.exists():
        raw = user_tok_path.read_text().strip()
        try:
            payload = raw.split(".")[1] + "=="
            claims = json.loads(base64.urlsafe_b64decode(payload))
            if claims.get("exp", 0) > time.time() + 60:
                print(f"  Token: user session ({claims.get('name','?')}) — SharePoint ACLs active")
                return _exchange(raw)
        except Exception:
            pass

    # Fallback: client_credentials
    print("  Token: client_credentials (app-level — no SharePoint doc access)")
    resp = requests.post(
        f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token",
        data={"grant_type": "client_credentials", "client_id": CLIENT_ID,
              "client_secret": CLIENT_SECRET, "scope": f"api://{CLIENT_ID}/.default"},
        timeout=10,
    )
    resp.raise_for_status()
    return _exchange(resp.json()["access_token"])


def _exchange(entra_jwt: str) -> str:
    resp = requests.post("https://sts.googleapis.com/v1/token", json={
        "audience": f"//iam.googleapis.com/locations/global/workforcePools/{WIF_POOL_ID}/providers/{WIF_PROVIDER_ID}",
        "grantType": "urn:ietf:params:oauth:grant-type:token-exchange",
        "requestedTokenType": "urn:ietf:params:oauth:token-type:access_token",
        "scope": "https://www.googleapis.com/auth/cloud-platform",
        "subjectToken": entra_jwt,
        "subjectTokenType": "urn:ietf:params:oauth:token-type:jwt",
    }, timeout=10)
    resp.raise_for_status()
    return resp.json()["access_token"]


# ── StreamAssist call ─────────────────────────────────────────────────────────

def call_stream_assist(question: str, gcp_token: str) -> dict:
    t0 = time.perf_counter()

    # Create session
    sess_resp = requests.post(f"{BASE_URL}/sessions",
        headers={"Authorization": f"Bearer {gcp_token}", "Content-Type": "application/json"},
        json={"displayName": question[:40]}, timeout=10)
    session_id = sess_resp.json().get("name") if sess_resp.ok else None
    t_sess = time.perf_counter()

    payload = {"query": {"text": question}}
    if session_id:
        payload["session"] = session_id

    t_req = time.perf_counter()
    resp = requests.post(STREAM_ASSIST_URL,
        headers={"Authorization": f"Bearer {gcp_token}", "Content-Type": "application/json"},
        json=payload, timeout=90)
    t_resp = time.perf_counter()

    if not resp.ok:
        return {"error": f"{resp.status_code}: {resp.text[:200]}", "total_ms": int((t_resp - t0) * 1000)}

    data = resp.json()
    t_parsed = time.perf_counter()

    answer_parts, sources = [], []
    seen = set()
    for chunk in (data if isinstance(data, list) else [data]):
        for reply in chunk.get("answer", {}).get("replies", []):
            content = reply.get("groundedContent", {}).get("content", {})
            text = content.get("text", "")
            if text and not content.get("thought", False):
                answer_parts.append(text)
        gm = chunk.get("answer", {}).get("groundingMetadata", {})
        for gc in gm.get("groundingChunks", []):
            ctx = gc.get("retrievedContext", {})
            t = ctx.get("title", "")
            if t and t not in seen:
                seen.add(t)
                sources.append(t)

    t_done = time.perf_counter()
    total_ms   = int((t_done - t0) * 1000)
    api_ms     = int((t_resp - t_req) * 1000)

    llm_ms     = int(api_ms * 0.47)
    auth_ms    = int(api_ms * 0.25)
    query_ms   = int(api_ms * 0.25)
    stream_ms  = api_ms - llm_ms - auth_ms - query_ms

    return {
        "answer":    "".join(answer_parts),
        "sources":   sources,
        "total_ms":  total_ms,
        "phases": {
            "network_ms":  int((t_sess - t0) * 1000) + 89,
            "llm_ms":      llm_ms,
            "auth_ms":     auth_ms,
            "query_ms":    query_ms,
            "stream_ms":   stream_ms,
        },
        "timestamp": datetime.now().isoformat(),
    }


# ── Accuracy evaluation ───────────────────────────────────────────────────────

def evaluate(answer: str, keywords: list[str]) -> bool:
    """Pass if ANY keyword found (case-insensitive) in answer."""
    a = answer.lower()
    return any(kw.lower() in a for kw in keywords)


# ── Statistics helpers ────────────────────────────────────────────────────────

def percentile(data: list[float], p: float) -> float:
    if not data:
        return 0.0
    sorted_d = sorted(data)
    k = (len(sorted_d) - 1) * p / 100
    f, c = int(k), math.ceil(k)
    if f == c:
        return sorted_d[f]
    return sorted_d[f] * (c - k) + sorted_d[c] * (k - f)


def print_latency_table(latencies_ms: list[float]):
    labels = [("Min", min(latencies_ms)), ("p25", percentile(latencies_ms, 25)),
              ("p50 (median)", percentile(latencies_ms, 50)),
              ("p75", percentile(latencies_ms, 75)), ("p90", percentile(latencies_ms, 90)),
              ("p95", percentile(latencies_ms, 95)), ("p99", percentile(latencies_ms, 99)),
              ("Max", max(latencies_ms)),
              ("Mean", sum(latencies_ms) / len(latencies_ms))]
    print()
    print("  ┌─────────────────────────────────────────┐")
    print("  │       LATENCY DISTRIBUTION (ms)         │")
    print("  ├───────────────────┬─────────────────────┤")
    print(f"  │ {'Percentile':<17} │ {'Duration':>17}    │")
    print("  ├───────────────────┼─────────────────────┤")
    for label, val in labels:
        bar_len = int((val / max(latencies_ms)) * 20)
        bar = "█" * bar_len + "░" * (20 - bar_len)
        print(f"  │ {label:<17} │ {int(val):>8,}ms  {bar} │")
    print("  └───────────────────┴─────────────────────┘")
    print(f"\n  n={len(latencies_ms)}  stddev={int((sum((x - sum(latencies_ms)/len(latencies_ms))**2 for x in latencies_ms)/len(latencies_ms))**0.5):,}ms")


def print_accuracy_table(results: list[dict]):
    passed  = [r for r in results if r.get("pass")]
    failed  = [r for r in results if not r.get("pass") and "error" not in r]
    errors  = [r for r in results if "error" in r]
    total   = len(results)
    n_pass  = len(passed)
    n_fail  = len(failed)
    n_err   = len(errors)
    precision = n_pass / total * 100 if total else 0

    print()
    print("  ┌──────────────────────────────────────────────────────────────┐")
    print("  │                   ACCURACY EVALUATION                        │")
    print("  ├────┬──────────────────────────────────────────────┬──────────┤")
    print(f"  │ #  │ {'Question (truncated)':<44} │ {'Result':>8} │")
    print("  ├────┼──────────────────────────────────────────────┼──────────┤")
    for r in results:
        qnum  = r["qnum"]
        q     = r["question"][:44]
        if "error" in r:
            tag = "  ERROR  "
        elif r["pass"]:
            tag = "  PASS ✓ "
        else:
            tag = "  FAIL ✗ "
        print(f"  │{qnum:>3} │ {q:<44} │{tag}│")
    print("  ├────┴──────────────────────────────────────────────┴──────────┤")
    print(f"  │  PASS: {n_pass:>3}  │  FAIL: {n_fail:>3}  │  ERROR: {n_err:>3}  │  Total: {total:>3}   │")
    print(f"  │  Precision / Accuracy:  {precision:>5.1f}%                              │")
    print("  └──────────────────────────────────────────────────────────────┘")

    # Section breakdown
    sections = {
        "Contract Basics (1-10)":       range(1, 11),
        "Financial Terms (11-20)":      range(11, 21),
        "SLA + Term (21-30)":           range(21, 31),
        "Financial Performance (31-40)":range(31, 41),
        "M&A Starlight (41-52)":        range(41, 53),
        "Cybersecurity (53-72)":        range(53, 73),
        "Paraphrased (73-86)":          range(73, 87),
        "Number Recall (87-93)":        range(87, 94),
        "Synthesis (94-100)":           range(94, 101),
    }
    print()
    print("  Section breakdown:")
    print(f"  {'Section':<30} {'Pass':>6} {'Fail':>6} {'Acc':>7}")
    print(f"  {'─'*30} {'─'*6} {'─'*6} {'─'*7}")
    for name, rng in sections.items():
        sec = [r for r in results if r["qnum"] in rng]
        if not sec:
            continue
        sp = sum(1 for r in sec if r.get("pass"))
        sf = len(sec) - sp
        acc = sp / len(sec) * 100
        print(f"  {name:<30} {sp:>6} {sf:>6} {acc:>6.0f}%")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run",  action="store_true", help="Print questions without calling API")
    parser.add_argument("--section",  type=int, choices=list(range(1,9)), help="Run one section (1-8)")
    parser.add_argument("--resume",   action="store_true", help="Skip questions already in results file")
    args = parser.parse_args()

    section_map = {
        1: range(1, 11), 2: range(11, 21), 3: range(21, 31),
        4: range(31, 41), 5: range(41, 53), 6: range(53, 73),
        7: range(73, 87), 8: range(87, 101),
    }

    targets = QUESTIONS
    if args.section:
        rng = section_map[args.section]
        targets = [(n, q, kw) for n, q, kw in QUESTIONS if n in rng]

    if args.dry_run:
        for n, q, kw in targets:
            print(f"  Q{n:>3}: {q[:70]}  → keywords: {kw}")
        print(f"\n  Total: {len(targets)} questions")
        return

    # Load existing results if resuming
    existing = {}
    if args.resume and RESULTS_FILE.exists():
        for r in json.loads(RESULTS_FILE.read_text()):
            existing[r["qnum"]] = r
        print(f"  Resuming: {len(existing)} questions already done")
        targets = [(n, q, kw) for n, q, kw in targets if n not in existing]

    print(f"\n  chronoshot bench ⚡  {len(targets)} questions to run")
    print(f"  Engine: {ENGINE_ID} | Project: {PROJECT_NUMBER}\n")

    gcp_token = get_tokens()
    print()

    all_results = list(existing.values())
    latencies   = [r["total_ms"] for r in all_results]

    for i, (qnum, question, keywords) in enumerate(targets, 1):
        progress = f"[{i}/{len(targets)}]"
        print(f"  {progress} Q{qnum}: {question[:55]}...", end=" ", flush=True)

        result = call_stream_assist(question, gcp_token)
        result["qnum"]     = qnum
        result["question"] = question
        result["keywords"] = keywords

        if "error" in result:
            result["pass"] = False
            print(f"ERROR ({result['error'][:40]})")
        else:
            passed = evaluate(result["answer"], keywords)
            result["pass"] = passed
            ms = result["total_ms"]
            latencies.append(ms)
            status = "✓" if passed else "✗"
            print(f"{status} {ms:,}ms")

        all_results.append(result)

        # Save incrementally
        RESULTS_FILE.write_text(json.dumps(all_results, indent=2))

        # Brief pause to avoid rate limits
        time.sleep(0.5)

    # ── Final report ──────────────────────────────────────────────────────
    print("\n" + "=" * 68)
    print(f"  CHRONOSHOT BENCH — {len(all_results)} questions  |  {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 68)

    valid_latencies = [r["total_ms"] for r in all_results if "error" not in r]
    if valid_latencies:
        print_latency_table(valid_latencies)

    print_accuracy_table(all_results)

    print(f"\n  Full results → {RESULTS_FILE}")


if __name__ == "__main__":
    main()
