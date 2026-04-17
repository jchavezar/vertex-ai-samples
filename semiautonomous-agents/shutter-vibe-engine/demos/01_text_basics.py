"""Demo 1 — First contact.

Goals:
* Confirm Vertex client works end-to-end.
* Show response shape, default vs requested dimensions, L2 normalization.
* Time a single call so the customer sees latency live.
"""
from __future__ import annotations

import numpy as np

from _client import CLIENT, TEXT_MODEL, banner, embed_text, timed
from google.genai import types


def main() -> None:
    banner(f"Demo 01 — first contact with {TEXT_MODEL}")

    sample = "Steam rising from a coffee cup on a rainy morning."
    print(f"Input: {sample!r}")

    with timed("single embed_content call (default 3072 dim)"):
        resp = CLIENT.models.embed_content(model=TEXT_MODEL, contents=sample)
    vec = np.array(resp.embeddings[0].values, dtype=np.float32)
    print(f"  default vector len = {vec.shape[0]}, L2 norm = {np.linalg.norm(vec):.4f}")
    print(f"  first 8 values     = {vec[:8].round(4).tolist()}")
    print(f"  raw response keys  = {list(resp.model_dump().keys())}")

    print()
    for dim in (3072, 1536, 768, 256, 128):
        with timed(f"output_dimensionality={dim}"):
            v = embed_text(sample, output_dim=dim)
        print(f"  → shape {v.shape}, post-norm L2 = {np.linalg.norm(v):.4f}")

    banner("Why this matters")
    print(
        "Same call, four order-of-magnitude storage choices. The 768-dim prefix\n"
        "of the 3072 vector is what we use as the production sweet spot."
    )


if __name__ == "__main__":
    main()
