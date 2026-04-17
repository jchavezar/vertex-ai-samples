"""Demo 4 — Vibe Search (the headline demo).

Natural-language queries that contain *zero* keyword overlap with the
contributor captions, returning the right asset by meaning alone.
"""
from __future__ import annotations

import numpy as np

from _client import banner, embed_text
from data.stock_corpus import CORPUS


VIBE_QUERIES = [
    "a feeling of nostalgia in a coffee shop",
    "the calm before a storm",
    "wholesome family time outdoors",
    "youth saving the planet",
    "old-world craftsmanship and ritual",
    "an emerging Gen-Z urban sport scene",
]


def main() -> None:
    banner("Demo 04 — Vibe Search: meaning beats keywords")
    captions = [a.caption for a in CORPUS]
    docs = embed_text(captions, task_type="RETRIEVAL_DOCUMENT", output_dim=768)

    for q in VIBE_QUERIES:
        qv = embed_text(q, task_type="RETRIEVAL_QUERY", output_dim=768)
        sims = docs @ qv[0]
        top = np.argsort(-sims)[:3]
        print(f"\n🔍 {q}")
        for rank, idx in enumerate(top, 1):
            a = CORPUS[idx]
            score = float(sims[idx])
            print(f"  {rank}. [{a.catalog:<11} {a.kind:<9}] cos={score:.3f}  {a.caption[:90]}…")

    banner("Why this lands")
    print(
        "None of the queries share keywords with the winning caption. The\n"
        "model retrieves by intent. This is the side-by-side that immediately\n"
        "shows up shutterstock.com's current keyword-and-tag search."
    )


if __name__ == "__main__":
    main()
