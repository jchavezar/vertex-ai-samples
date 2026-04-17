"""Demo 5 — Multilingual brief, English-only catalog.

The Shutterstock catalog metadata is English-biased. We embed an English
corpus and shoot the same intent at it from five languages — same hit.
"""
from __future__ import annotations

import numpy as np

from _client import banner, embed_text
from data.stock_corpus import CORPUS


# All five paraphrase the same intent: a tea ceremony in Japan.
QUERIES = {
    "English":   "A traditional Japanese tea ceremony moment",
    "Spanish":   "Un momento de la ceremonia tradicional japonesa del té",
    "Japanese":  "伝統的な日本の茶道の一場面",
    "German":    "Ein Moment einer traditionellen japanischen Teezeremonie",
    "Arabic":    "لحظة من حفل الشاي الياباني التقليدي",
}


def main() -> None:
    banner("Demo 05 — Multilingual queries hit the same English asset")
    captions = [a.caption for a in CORPUS]
    docs = embed_text(captions, task_type="RETRIEVAL_DOCUMENT", output_dim=768)

    print(f"{'language':<10} {'top hit id':<10} {'cos':>6}  caption")
    for lang, q in QUERIES.items():
        qv = embed_text(q, task_type="RETRIEVAL_QUERY", output_dim=768)
        sims = docs @ qv[0]
        top = int(np.argmax(sims))
        a = CORPUS[top]
        print(f"{lang:<10} {a.asset_id:<10} {sims[top]:>6.3f}  {a.caption[:80]}…")

    banner("Why this lands")
    print(
        "Same vector space across 100+ languages. No translation pipeline,\n"
        "no per-locale index, no quality cliff. Direct revenue lift on\n"
        "international enterprise contracts."
    )


if __name__ == "__main__":
    main()
