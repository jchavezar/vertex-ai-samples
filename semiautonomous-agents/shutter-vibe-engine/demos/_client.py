"""Shared Vertex AI client + small helpers used by every demo."""
from __future__ import annotations

import os
import sys
import time
from contextlib import contextmanager
from pathlib import Path

import numpy as np
from google import genai
from google.genai import types

# Make `data` importable when running scripts from the repo root or demos/
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

PROJECT = os.environ.get("GOOGLE_CLOUD_PROJECT", "vtxdemos")
LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")

# Force Vertex AI mode (env var read by the client constructor)
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"
os.environ["GOOGLE_CLOUD_PROJECT"] = PROJECT
os.environ["GOOGLE_CLOUD_LOCATION"] = LOCATION

# Models we lean on
TEXT_MODEL = "gemini-embedding-001"          # GA, text only, all task types
MM_MODEL = "gemini-embedding-2-preview"       # multimodal, no task_type field

CLIENT = genai.Client()


def banner(title: str) -> None:
    print("\n" + "=" * 78)
    print(f" {title}")
    print("=" * 78)


@contextmanager
def timed(label: str):
    start = time.perf_counter()
    yield
    print(f"  ⏱  {label}: {time.perf_counter() - start:.2f}s")


def embed_text(
    text: str | list[str],
    *,
    task_type: str | None = "RETRIEVAL_DOCUMENT",
    output_dim: int | None = 768,
    model: str = TEXT_MODEL,
    title: str | None = None,
) -> np.ndarray:
    """Returns an (n, d) array. Always L2-normalized."""
    if isinstance(text, str):
        contents: list = [text]
    else:
        contents = list(text)

    cfg_kwargs: dict = {}
    if task_type:
        cfg_kwargs["task_type"] = task_type
    if output_dim:
        cfg_kwargs["output_dimensionality"] = output_dim
    if title:
        cfg_kwargs["title"] = title

    config = types.EmbedContentConfig(**cfg_kwargs) if cfg_kwargs else None

    out = []
    # gemini-embedding-001 on Vertex accepts only ONE input per call. Loop.
    for item in contents:
        resp = CLIENT.models.embed_content(
            model=model,
            contents=item,
            config=config,
        )
        out.append(resp.embeddings[0].values)
    arr = np.asarray(out, dtype=np.float32)
    return arr / np.linalg.norm(arr, axis=1, keepdims=True)


def embed_multimodal(parts: list, *, output_dim: int | None = 768,
                     model: str = MM_MODEL) -> np.ndarray:
    """Embed a single mixed-modality input (returns shape (1, d), L2-normed)."""
    cfg = types.EmbedContentConfig(output_dimensionality=output_dim) if output_dim else None
    resp = CLIENT.models.embed_content(model=model, contents=parts, config=cfg)
    arr = np.asarray([resp.embeddings[0].values], dtype=np.float32)
    return arr / np.linalg.norm(arr, axis=1, keepdims=True)


def cosine(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Cosine similarity for L2-normed inputs reduces to a dot product."""
    return a @ b.T


def topk(scores: np.ndarray, k: int = 5) -> list[int]:
    return np.argsort(-scores)[:k].tolist()
