#!/usr/bin/env python3
"""
Generate sanitized judged/*.json files with only composite scores.
"""
import json
import os
from pathlib import Path

def compute_summary(judged_data):
    """Compute summary statistics from judged data."""
    strategy = judged_data[0]["parser"] if judged_data else "unknown"

    # Compute aggregate metrics
    correctness_sum = sum(q.get("correctness", 0) for q in judged_data)
    completeness_sum = sum(q.get("completeness", 0) for q in judged_data)
    total = len(judged_data)

    correctness_pct = (correctness_sum / total * 100) if total > 0 else 0
    completeness_pct = (completeness_sum / total * 100) if total > 0 else 0
    composite = (correctness_pct + completeness_pct) / 2

    # Count verdicts
    verdict_counts = {}
    for q in judged_data:
        verdict = q.get("verdict", "unknown")
        verdict_counts[verdict] = verdict_counts.get(verdict, 0) + 1

    return {
        "strategy": strategy,
        "total_questions": total,
        "composite_score": round(composite, 1),
        "correctness_score": round(correctness_pct, 1),
        "completeness_score": round(completeness_pct, 1),
        "verdicts": verdict_counts,
        "note": "Per-question data redacted for customer privacy. Full evaluation dataset available internally."
    }

def main():
    judged_dir = Path("/home/admin_jesusarguelles_altostrat_c/docparse-eval-private/judged")
    output_dir = Path("/home/admin_jesusarguelles_altostrat_c/vertex-ai-samples/semiautonomous-agents/docparse/eval/judged")

    for judged_file in judged_dir.glob("*.json"):
        # Read original judged data
        with open(judged_file, "r") as f:
            judged_data = json.load(f)

        # Compute summary
        summary = compute_summary(judged_data)

        # Write sanitized version
        output_path = output_dir / judged_file.name
        with open(output_path, "w") as f:
            json.dump(summary, f, indent=2)

        print(f"Sanitized {judged_file.name}: {summary['strategy']} -> {summary['composite_score']}%")

if __name__ == "__main__":
    main()
