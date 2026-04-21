"""BigQuery search backend — drop-in replacement for vs_find_neighbors.

Same signature, same return shape:
    [(datapoint_id, cosine_similarity), ...] sorted best-first.

Uses BigQuery `VECTOR_SEARCH` with brute-force over a 2k-row table; with
modality clustering the planner skips non-matching blocks, so per-modality
queries scan ~400 rows max. Effective monthly cost at demo volume: ~$0.

Lazy-initialized client + a one-shot warmup() to keep first-search latency
under 600 ms after cold start.
"""
from __future__ import annotations

import os
import time
from typing import Iterable

import numpy as np
from google.cloud import bigquery

PROJECT  = os.getenv("GOOGLE_CLOUD_PROJECT", "vtxdemos")
BQ_TABLE = os.getenv("BQ_TABLE", "vtxdemos.envato_vibe.segments")

_CLIENT: bigquery.Client | None = None


def client() -> bigquery.Client:
    global _CLIENT
    if _CLIENT is None:
        _CLIENT = bigquery.Client(project=PROJECT)
    return _CLIENT


def warmup() -> dict:
    """Prime the BQ slot by running a tiny query. Call from /api/warmup
    on startup to avoid 1-2s cold-start on the first real search."""
    t0 = time.time()
    job = client().query(f"SELECT COUNT(*) AS n FROM `{BQ_TABLE}`")
    n = next(iter(job.result())).n
    return {"backend": "bigquery", "rows": int(n),
            "warmup_ms": round((time.time() - t0) * 1000, 1)}


def _build_where(modality: str | None, tempo: str | None,
                 length: str | None) -> tuple[str, list]:
    """Push-down WHERE clauses on the pre-filter subquery."""
    where: list[str] = []
    params: list = []
    if modality and modality != "all":
        if modality == "audio":
            where.append("modality IN UNNEST(@modalities)")
            params.append(bigquery.ArrayQueryParameter(
                "modalities", "STRING", ["audio", "sfx"]))
        else:
            where.append("modality = @modality")
            params.append(bigquery.ScalarQueryParameter(
                "modality", "STRING", modality))
    if tempo:
        where.append("tempo_bucket = @tempo")
        params.append(bigquery.ScalarQueryParameter("tempo", "STRING", tempo))
    if length:
        where.append("length_bucket = @length")
        params.append(bigquery.ScalarQueryParameter("length", "STRING", length))
    where_sql = ("WHERE " + " AND ".join(where)) if where else ""
    return where_sql, params


def find_neighbors(q_vec: np.ndarray, *, k: int = 20,
                   modality: str | None = None,
                   tempo: str | None = None,
                   length: str | None = None) -> list[tuple[str, float]]:
    """BigQuery VECTOR_SEARCH with brute force + push-down filters.

    Returns [(datapoint_id, cosine_similarity), ...] sorted best-first.
    Cosine similarity = 1 - distance (BigQuery returns COSINE distance).
    """
    where_sql, where_params = _build_where(modality, tempo, length)
    sql = f"""
    SELECT base.datapoint_id AS id, distance
    FROM VECTOR_SEARCH(
      (SELECT datapoint_id, embedding FROM `{BQ_TABLE}` {where_sql}),
      'embedding',
      (SELECT @q AS embedding),
      top_k => @k,
      distance_type => 'COSINE',
      options => '{{"use_brute_force":true}}'
    )
    ORDER BY distance ASC
    """
    params = [
        bigquery.ArrayQueryParameter("q", "FLOAT64", q_vec.astype(float).tolist()),
        bigquery.ScalarQueryParameter("k", "INT64", int(k)),
        *where_params,
    ]
    job = client().query(sql, job_config=bigquery.QueryJobConfig(query_parameters=params))
    rows = list(job.result())
    return [(r.id, 1.0 - float(r.distance)) for r in rows]


def fanout_all(q_vec: np.ndarray, *, k: int,
               tempo: str | None, length: str | None,
               modalities: Iterable[str],
               apply_floor) -> list[tuple[str, float]]:
    """Per-modality fan-out — same shape as vs_fanout_all in main.py.

    Run one find_neighbors per modality in parallel, apply the per-modality
    cosine floor, then merge by best score per datapoint.
    """
    from concurrent.futures import ThreadPoolExecutor
    mods = list(modalities)
    with ThreadPoolExecutor(max_workers=len(mods)) as ex:
        futures = {m: ex.submit(find_neighbors, q_vec, k=k,
                                modality=m, tempo=tempo, length=length)
                   for m in mods}
        per_mod = {m: f.result() for m, f in futures.items()}
    merged: dict[str, float] = {}
    for mod, hits in per_mod.items():
        for dp_id, score in apply_floor(hits, mod):
            if dp_id not in merged or score > merged[dp_id]:
                merged[dp_id] = score
    return sorted(merged.items(), key=lambda x: -x[1])
