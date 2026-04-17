"""Demo 7 — Mood-board generator.

Embed the corpus with CLUSTERING task type, run K-means, name each cluster by
the closest caption to its centroid. This is what an agency creative director
would project on the wall during a pitch.
"""
from __future__ import annotations

import numpy as np
from sklearn.cluster import KMeans

from _client import banner, embed_text
from data.stock_corpus import CORPUS


N_CLUSTERS = 5


def main() -> None:
    banner(f"Demo 07 — auto mood-board ({N_CLUSTERS} clusters)")
    captions = [a.caption for a in CORPUS]
    vecs = embed_text(captions, task_type="CLUSTERING", output_dim=768)

    km = KMeans(n_clusters=N_CLUSTERS, random_state=42, n_init="auto").fit(vecs)
    labels = km.labels_

    for cid in range(N_CLUSTERS):
        members = [i for i, l in enumerate(labels) if l == cid]
        if not members:
            continue
        center = km.cluster_centers_[cid]
        # caption closest to the centroid is our cluster headline
        sims = vecs[members] @ (center / np.linalg.norm(center))
        head = members[int(np.argmax(sims))]
        print(f"\n🎨 Mood-board {cid + 1} — anchor: {CORPUS[head].caption[:80]}…")
        for i in members:
            a = CORPUS[i]
            print(f"   - [{a.catalog:<11} {a.kind:<9}] {a.asset_id}  {a.caption[:75]}…")

    banner("Why this lands")
    print(
        "One brief, five themed boards, zero hand-curation. Pair with Gemini\n"
        "to auto-name each cluster ('Hero shots', 'Lifestyle B-roll', …)."
    )


if __name__ == "__main__":
    main()
