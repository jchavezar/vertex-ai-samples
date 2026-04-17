"""Demo 3 — Matryoshka dimension trade-off.

We embed the synthetic Shutterstock corpus once at every supported dimension
and measure how recall@5 against a fixed query set changes. Also reports
storage footprint and per-call latency so the customer can see the cost lever.
"""
from __future__ import annotations

import time

import numpy as np

from _client import banner, embed_text
from data.stock_corpus import CORPUS


# A handful of intent-rich queries with a known "gold" asset id we expect.
PROBES = [
    ("Cozy nostalgic morning vibes in a small european cafe", "SS-00001"),
    ("Sustainable Gen-Z beach activism at sunrise", "SS-00020"),
    ("Tense atmospheric weather before a thunderstorm", "SS-00010"),
    ("Vintage cinematic road-trip mood", "SS-00031"),
    ("Traditional Japanese minimalism", "SS-00081"),
]
DIMS = (3072, 1536, 768, 256, 128)


def main() -> None:
    banner("Demo 03 — Matryoshka: dimension vs recall vs cost")
    captions = [a.caption for a in CORPUS]
    ids = [a.asset_id for a in CORPUS]

    print(f"Corpus size: {len(CORPUS)} assets, {len(PROBES)} probe queries\n")
    print(f"{'dim':>5} {'embed_corpus_s':>15} {'recall@5':>10} {'avg_query_ms':>14} {'storage_KB':>11}")

    for dim in DIMS:
        # corpus embed
        t0 = time.perf_counter()
        corpus_vecs = embed_text(captions, task_type="RETRIEVAL_DOCUMENT", output_dim=dim)
        corpus_secs = time.perf_counter() - t0

        # query embed + recall
        hits = 0
        t0 = time.perf_counter()
        for query, gold in PROBES:
            qv = embed_text(query, task_type="RETRIEVAL_QUERY", output_dim=dim)
            sims = corpus_vecs @ qv[0]
            top5 = np.argsort(-sims)[:5]
            if gold in [ids[i] for i in top5]:
                hits += 1
        query_ms = (time.perf_counter() - t0) / len(PROBES) * 1000

        recall = hits / len(PROBES)
        storage_kb = corpus_vecs.nbytes / 1024
        print(f"{dim:>5} {corpus_secs:>15.2f} {recall:>10.2f} {query_ms:>14.0f} {storage_kb:>11.1f}")

    banner("Takeaway")
    print(
        "For ~30 captions you'll see flat recall across dims. At Shutterstock\n"
        "scale (200M+ photos) the same curve maps to 4× storage savings going\n"
        "from 3072 → 768 with negligible MTEB drop (68.16 → 67.99)."
    )


if __name__ == "__main__":
    main()
