#!/usr/bin/env python3
import json

with open('golden_100_suite.json', 'r') as f:
    suite = json.load(f)

print(f"Total test suite questions: {len(suite)}")
for q in suite:
    print(f"[{q['id']}] Category: {q['category']} | Complexity: {q['complexity']}")
    print(f"    Q: {q['query']}")
    print(f"    Ans: {q['ground_truth_answer']}")
    print("-" * 80)
