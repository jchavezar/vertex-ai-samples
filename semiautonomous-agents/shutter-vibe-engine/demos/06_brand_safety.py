"""Demo 6 — Per-customer brand-safety filter via concept anchors.

Each customer defines their forbidden-content policy in plain English.
We embed those concept anchors and rank every asset by max similarity.
Anything over a configurable threshold is flagged — no retraining needed.
"""
from __future__ import annotations

import numpy as np

from _client import banner, embed_text
from data.stock_corpus import CORPUS


POLICIES = {
    "Children's app":  ["alcohol or drinking", "gambling or casinos", "weapons or violence"],
    "Beer brand":      ["weapons or violence", "illegal drug use"],
    "Bank":            ["alcohol or drinking", "gambling or casinos", "violent crime"],
}
THRESHOLD = 0.55


def main() -> None:
    banner("Demo 06 — Zero-shot brand-safety filtering")
    captions = [a.caption for a in CORPUS]
    asset_vecs = embed_text(captions, task_type="CLASSIFICATION", output_dim=768)

    for brand, policy in POLICIES.items():
        anchor_vecs = embed_text(policy, task_type="CLASSIFICATION", output_dim=768)
        sims = asset_vecs @ anchor_vecs.T  # (n_assets, n_anchors)
        worst_score = sims.max(axis=1)
        worst_anchor = sims.argmax(axis=1)

        print(f"\n🚫 Policy for {brand} (threshold={THRESHOLD})")
        flagged = [(i, worst_score[i], policy[worst_anchor[i]])
                   for i in range(len(CORPUS)) if worst_score[i] >= THRESHOLD]
        flagged.sort(key=lambda r: -r[1])
        for idx, score, anchor in flagged[:6]:
            a = CORPUS[idx]
            print(f"  {a.asset_id} cos={score:.3f}  matches '{anchor}'  → {a.caption[:70]}…")
        if not flagged:
            print("  (no flags)")

    banner("Why this lands")
    print(
        "No fine-tuning. Each customer ships their own policy in English (or\n"
        "any of 100+ languages) and the same embedding model enforces it."
    )


if __name__ == "__main__":
    main()
