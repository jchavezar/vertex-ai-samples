#!/usr/bin/env python3
"""
Generate sanitized questions.json that preserves structure but redacts customer data.
"""
import json

def sanitize_question(q):
    """Sanitize a single question, preserving metadata but redacting content."""
    category = q.get("category", "")
    difficulty = q.get("difficulty", "")
    element = q.get("element", "")
    page = q.get("page", "")

    # Create a generic redacted question based on metadata
    redacted_q = f"[REDACTED — sample {category} question about {element} on page {page}]"
    redacted_a = "[REDACTED]"

    return {
        "id": q["id"],
        "pdf": q["pdf"],
        "page": q["page"],
        "element": q["element"],
        "category": q["category"],
        "difficulty": q["difficulty"],
        "q": redacted_q,
        "a": redacted_a
    }

def main():
    # Read original questions
    with open("/home/admin_jesusarguelles_altostrat_c/docparse-eval-private/questions.json", "r") as f:
        questions = json.load(f)

    # Sanitize all questions
    sanitized = [sanitize_question(q) for q in questions]

    # Write sanitized version
    with open("/home/admin_jesusarguelles_altostrat_c/vertex-ai-samples/semiautonomous-agents/docparse/eval/questions.json", "w") as f:
        json.dump(sanitized, f, indent=2)

    print(f"Sanitized {len(sanitized)} questions")
    print(f"Sample sanitized question: {sanitized[0]}")

if __name__ == "__main__":
    main()
