"""Demo 8 — Bonus: CODE_RETRIEVAL_QUERY task type.

Shutterstock's API & developer-tools team will love this. Natural-language
question → matching code snippet. Same model, different task type.
"""
from __future__ import annotations

import numpy as np

from _client import banner, embed_text


SNIPPETS = [
    ("python_search", """\
def search_assets(query: str, top_k: int = 10):
    qv = embed(query, task_type='RETRIEVAL_QUERY')
    sims = corpus_vecs @ qv
    return [corpus[i] for i in sims.argsort()[::-1][:top_k]]
"""),
    ("python_retry", """\
import time, random
def with_retry(fn, *, attempts=5, base=0.5):
    for i in range(attempts):
        try: return fn()
        except Exception:
            if i == attempts - 1: raise
            time.sleep(base * 2**i + random.random() * base)
"""),
    ("python_resize", """\
from PIL import Image
def thumbnail(path, max_side=512):
    im = Image.open(path); im.thumbnail((max_side, max_side)); return im
"""),
    ("python_oauth", """\
import requests
def token(client_id, client_secret):
    r = requests.post('https://api.shutterstock.com/v2/oauth/access_token',
        data={'grant_type': 'client_credentials',
              'client_id': client_id, 'client_secret': client_secret})
    r.raise_for_status(); return r.json()['access_token']
"""),
]

QUERIES = [
    "How do I implement vector search over an embedding corpus?",
    "Resize an image to a smaller thumbnail",
    "Get an OAuth access token from the Shutterstock API",
    "Retry an API call with exponential backoff",
]


def main() -> None:
    banner("Demo 08 — code retrieval with CODE_RETRIEVAL_QUERY")
    snippet_vecs = embed_text([s for _, s in SNIPPETS],
                              task_type="RETRIEVAL_DOCUMENT", output_dim=768)
    for q in QUERIES:
        qv = embed_text(q, task_type="CODE_RETRIEVAL_QUERY", output_dim=768)
        sims = snippet_vecs @ qv[0]
        order = np.argsort(-sims)
        print(f"\n💡 {q}")
        for rank, idx in enumerate(order[:2], 1):
            name, code = SNIPPETS[idx]
            print(f"  {rank}. {name} (cos={sims[idx]:.3f})")
            for line in code.strip().splitlines()[:2]:
                print(f"      {line}")

    banner("Why this lands")
    print(
        "Same embedding model, new task type. Powers Shutterstock developer\n"
        "docs search, internal IDE assistants, and code-aware contributor APIs."
    )


if __name__ == "__main__":
    main()
