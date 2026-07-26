#!/usr/bin/env python3
import json

with open('/Users/jesusarguelles/IdeaProjects/vertex-ai-samples/semiautonomous-agents/custom_ui_mcp_outlook/golden_100_suite.json', 'r') as f:
    suite = json.load(f)

print(f"Total test suite questions: {len(suite)}")
for q in suite:
    print(f"[{q['id']}] Category: {q['category']} | Complexity: {q['complexity']}")
    print(f"    Q: {q['query']}")
    print(f"    Ans: {q['ground_truth_answer']}")
    print("-" * 80)
