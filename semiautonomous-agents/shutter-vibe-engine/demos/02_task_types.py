"""Demo 2 — Task types side by side.

Embeds the same query and document with different task types and shows how the
cosine similarity changes. Highlights the asymmetric retrieval pair
(RETRIEVAL_QUERY ↔ RETRIEVAL_DOCUMENT) vs the symmetric SEMANTIC_SIMILARITY.
"""
from __future__ import annotations

import numpy as np

from _client import banner, embed_text


QUERY = "How do I prepare a perfect pour-over coffee?"
DOC = (
    "Heat 350 ml of water to 96 °C, place a V60 dripper with rinsed paper "
    "filter on a server, add 22 g of medium-fine ground coffee, bloom for "
    "30 s with 50 ml of water, then pour the rest in slow concentric circles."
)
NEG = "Tropical hurricane approaching the Florida coastline at sunset."

TASK_TYPES = [
    "SEMANTIC_SIMILARITY",
    "RETRIEVAL_QUERY",
    "RETRIEVAL_DOCUMENT",
    "QUESTION_ANSWERING",
    "FACT_VERIFICATION",
    "CLASSIFICATION",
    "CLUSTERING",
    "CODE_RETRIEVAL_QUERY",
]


def cos(a: np.ndarray, b: np.ndarray) -> float:
    return float((a @ b.T).ravel()[0])


def main() -> None:
    banner("Demo 02 — task types affect similarity")

    print(f"QUERY: {QUERY}")
    print(f"DOC:   {DOC}")
    print(f"NEG:   {NEG}\n")

    rows = []
    for tt in TASK_TYPES:
        try:
            q = embed_text(QUERY, task_type=tt, output_dim=768)
            # For asymmetric pairs we'd embed the doc with RETRIEVAL_DOCUMENT.
            d_tt = "RETRIEVAL_DOCUMENT" if tt in {
                "RETRIEVAL_QUERY", "QUESTION_ANSWERING",
                "FACT_VERIFICATION", "CODE_RETRIEVAL_QUERY",
            } else tt
            d = embed_text(DOC, task_type=d_tt, output_dim=768)
            n = embed_text(NEG, task_type=d_tt, output_dim=768)
            rows.append((tt, d_tt, cos(q, d), cos(q, n)))
        except Exception as exc:  # pragma: no cover - we want to keep going
            rows.append((tt, "?", float("nan"), float("nan")))
            print(f"  ! task_type={tt} failed: {exc}")

    print(f"{'query task':<22} {'doc task':<22} {'cos(q,doc)':>11} {'cos(q,neg)':>11}  {'gap':>6}")
    for tt, d_tt, sim_pos, sim_neg in rows:
        gap = sim_pos - sim_neg
        print(f"{tt:<22} {d_tt:<22} {sim_pos:>11.4f} {sim_neg:>11.4f}  {gap:>+6.3f}")

    banner("Takeaway")
    print(
        "RETRIEVAL_QUERY paired with RETRIEVAL_DOCUMENT typically opens the\n"
        "largest gap between the on-topic doc and the off-topic distractor.\n"
        "SEMANTIC_SIMILARITY is symmetric and great for dedup / 'more like this'.\n"
        "QUESTION_ANSWERING + RETRIEVAL_DOCUMENT lifts QA recall when the query\n"
        "is phrased as a real question."
    )


if __name__ == "__main__":
    main()
