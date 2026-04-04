#!/usr/bin/env python3
"""Test grounding accuracy with 30 questions about the Master Services Agreement."""

import requests
import json
import time

# Get token from saved file
try:
    with open("/tmp/entra_token.txt", "r") as f:
        TOKEN = f.read().strip()
except:
    TOKEN = None
    print("WARNING: No token found - responses will be unauthenticated")

API_URL = "http://localhost:8000/api/chat"

# Expected answers from the ACTUAL document (MSA-2024-0847)
QUESTIONS = [
    # Contract basics
    ("What is the total annual contract value of the Master Services Agreement?", "$4,850,000", "Contract Value"),
    ("Who is the client in the Master Services Agreement MSA-2024-0847?", "Apex Financial Services", "Client name"),
    ("Who is the provider in the Master Services Agreement?", "Meridian Technologies Corporation", "Provider name"),
    ("What is the contract reference number?", "MSA-2024-0847", "Contract ref"),
    ("What is the effective date of the Master Services Agreement?", "January 1, 2025", "Effective date"),

    # Contacts
    ("Who is the primary contact at the Provider?", "Jennifer Walsh", "Provider contact"),
    ("What is Jennifer Walsh's role?", "CFO", "Jennifer's role"),
    ("Who is the primary contact at Apex Financial Services?", "Richard Blackstone", "Client contact"),
    ("What is Richard Blackstone's title?", "CIO", "Richard's title"),

    # Financial terms
    ("What is the Q1 payment amount?", "$1,212,500", "Q1 payment"),
    ("What are the payment terms?", "Net 30 days", "Payment terms"),
    ("What is the late payment fee?", "1.5% per month", "Late fee"),
    ("What bank is used for wire transfers?", "JPMorgan Chase", "Bank name"),
    ("What is the base discount percentage?", "15%", "Base discount"),

    # Platform specs
    ("How much storage is allocated?", "50 TB primary, 100 TB backup", "Storage"),
    ("What is the API request limit?", "50,000 requests per minute", "API limit"),
    ("How many global data centers?", "12", "Data centers"),
    ("What database is used?", "PostgreSQL", "Database"),

    # Professional services
    ("How many implementation hours are included?", "2,400 hours", "Implementation hours"),
    ("What is the Technical Architect rate?", "$350/hour", "Architect rate"),
    ("How many training hours are included?", "400 hours", "Training hours"),

    # SLA
    ("What is the Critical (P1) availability SLA?", "99.99%", "P1 SLA"),
    ("What is the P1 response time?", "15 minutes", "P1 response"),
    ("What is the 24/7 support hotline number?", "(888) 555-MTEC", "Support number"),

    # Term and termination
    ("What is the initial term of the agreement?", "3 years", "Initial term"),
    ("What is the renewal notice period?", "90 days", "Renewal notice"),
    ("What is the Year 1 termination fee?", "$2,425,000", "Y1 termination"),

    # Data protection
    ("What encryption is used for data at rest?", "AES-256", "Encryption"),
    ("Where is the primary data residency?", "US-East (Virginia)", "Data residency"),

    # CEO info
    ("Who is the CEO of Meridian Technologies?", "Michael Thornton", "CEO name"),
]

def test_query(question, expected, label):
    """Send query and check if response contains expected answer."""
    headers = {"Content-Type": "application/json"}
    if TOKEN:
        headers["X-Entra-Id-Token"] = TOKEN

    payload = {
        "query": question,
        "sharepoint_only": True,
        "session_id": None  # Fresh query each time for grounding
    }

    try:
        start = time.time()
        resp = requests.post(API_URL, headers=headers, json=payload, timeout=120)
        elapsed = time.time() - start

        if not resp.ok:
            return {"label": label, "question": question, "expected": expected,
                    "answer": f"ERROR: {resp.status_code}", "sources": [],
                    "grounded": False, "correct": False, "latency": elapsed}

        data = resp.json()
        answer = data.get("answer", "")
        sources = data.get("sources", [])

        # Check if expected value is in answer
        correct = expected.lower() in answer.lower()
        grounded = len(sources) > 0

        return {
            "label": label,
            "question": question[:60] + "..." if len(question) > 60 else question,
            "expected": expected,
            "answer": answer[:200] + "..." if len(answer) > 200 else answer,
            "sources": [s.get("title", "?")[:30] for s in sources],
            "grounded": grounded,
            "correct": correct,
            "latency": round(elapsed, 1)
        }
    except Exception as e:
        return {"label": label, "question": question, "expected": expected,
                "answer": f"EXCEPTION: {e}", "sources": [],
                "grounded": False, "correct": False, "latency": 0}

def main():
    print("=" * 80)
    print("GROUNDING TEST - 30 Questions about Master Services Agreement")
    print("=" * 80)
    print()

    results = []
    correct_count = 0
    grounded_count = 0

    for i, (question, expected, label) in enumerate(QUESTIONS, 1):
        print(f"[{i:02d}/30] Testing: {label}...")
        result = test_query(question, expected, label)
        results.append(result)

        if result["correct"]:
            correct_count += 1
            status = "✓ CORRECT"
        else:
            status = "✗ WRONG"

        if result["grounded"]:
            grounded_count += 1
            grounding = f"📎 {len(result['sources'])} sources"
        else:
            grounding = "⚠️ NO SOURCES"

        print(f"       {status} | {grounding} | {result['latency']}s")
        print(f"       Expected: {expected}")
        print(f"       Got: {result['answer'][:100]}...")
        print()

        # Small delay between requests
        time.sleep(1)

    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total Questions: 30")
    print(f"Correct Answers: {correct_count}/30 ({correct_count/30*100:.1f}%)")
    print(f"Grounded (has sources): {grounded_count}/30 ({grounded_count/30*100:.1f}%)")
    print()

    print("DETAILED RESULTS:")
    print("-" * 80)
    for r in results:
        status = "✓" if r["correct"] else "✗"
        sources = "📎" if r["grounded"] else "⚠️"
        print(f"{status} {sources} [{r['label']}] Expected: {r['expected']}")
        if not r["correct"]:
            print(f"      Got: {r['answer'][:80]}...")

    # Save full results
    with open("/tmp/grounding_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print()
    print("Full results saved to /tmp/grounding_results.json")

if __name__ == "__main__":
    main()
