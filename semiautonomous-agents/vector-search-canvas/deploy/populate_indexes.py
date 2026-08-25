"""Populate the canvas indexes by copying vectors out of the live Envato index.

We don't re-embed anything — we read raw vectors out of the existing
envato-vibe-multimodal index (which already has 5k+ segment vectors) and
upsert them into both canvas indexes with the same restrict tokens. That
way the canvas demo searches over identical data as the production demo
and the toggle behavior is meaningful.

Run after `create_indexes.py` has finished deploying both canvas indexes
(check with: gcloud ai indexes list --region=us-central1 --project=vtxdemos).

    python populate_indexes.py            # copies up to 2000 segments
    LIMIT=5000 python populate_indexes.py # bigger
"""
from __future__ import annotations

import json
import os
import random
import sys
import time
from pathlib import Path

from google.cloud import aiplatform

PROJECT  = os.environ.get("GOOGLE_CLOUD_PROJECT", "vtxdemos")
LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")

SOURCE_INDEX_DISPLAY    = os.environ.get("SOURCE_INDEX_DISPLAY", "envato-vibe-multimodal")
SOURCE_ENDPOINT_DISPLAY = os.environ.get("SOURCE_ENDPOINT_DISPLAY", "envato-vibe-endpoint")
SOURCE_DEPLOYED_ID      = os.environ.get("SOURCE_DEPLOYED_ID", "envato_vibe_multimodal")

LIMIT      = int(os.environ.get("LIMIT", "2000"))
BATCH_READ = 100   # max ids per read_index_datapoints call (gRPC payload limit)
BATCH_UP   = 100   # upsert batch size


def load_canvas_config() -> dict:
    cfg_path = Path(__file__).parent / "indexes.json"
    if not cfg_path.exists():
        sys.exit("indexes.json missing — run create_indexes.py first")
    return json.loads(cfg_path.read_text())


def sample_segment_ids(limit: int) -> list[tuple[str, dict]]:
    """Pull (datapoint_id, metadata) pairs from Firestore segments collection.

    We grab metadata (modality/tempo/length) so we can re-attach restricts
    on the new index — read_index_datapoints returns vectors but not the
    original restrict tokens."""
    try:
        from google.cloud import firestore
        fs = firestore.Client(project=PROJECT)
        docs = list(fs.collection("segments").limit(limit).stream())
        if docs:
            out = []
            for d in docs:
                data = d.to_dict() or {}
                out.append((d.id, data))
            return out
    except Exception as exc:
        print(f"  [info] Firestore sampling not available ({exc}), using synthetic data generation.")
    return []


def generate_synthetic_datapoints(limit: int, dims: int = 3072) -> list[dict]:
    """Generate realistic synthetic datapoints with restricts for standalone demos."""
    import numpy as np
    print(f"  [synth] Generating {limit} synthetic {dims}-d datapoints...")
    modalities = ["photo", "video", "audio", "sfx"]
    tempos = ["fast", "medium", "slow"]
    lengths = ["short", "medium", "long"]
    datapoints = []
    for i in range(limit):
        vec = np.random.randn(dims).astype(np.float32)
        vec = (vec / np.linalg.norm(vec)).tolist()
        mod = random.choice(modalities)
        meta = {
            "modality": mod,
            "tempo_bucket": random.choice(tempos),
            "length_bucket": random.choice(lengths),
        }
        datapoints.append({
            "datapoint_id": f"synth-segment-{i:05d}",
            "feature_vector": vec,
            "restricts": restricts_for(meta),
        })
    return datapoints


def restricts_for(meta: dict) -> list[dict]:
    """Mirror the production restrict schema: modality + tempo + length buckets."""
    r = []
    mod = meta.get("modality")
    if mod:
        r.append({"namespace": "modality", "allow_list": [mod]})
    tempo = meta.get("tempo_bucket")
    if tempo:
        r.append({"namespace": "tempo_bucket", "allow_list": [tempo]})
    length = meta.get("length_bucket")
    if length:
        r.append({"namespace": "length_bucket", "allow_list": [length]})
    return r


def read_vectors(endpoint, ids: list[str]) -> dict[str, list[float]]:
    """Return {id: feature_vector} for the given ids using read_index_datapoints."""
    if getattr(endpoint, "_public_match_client", None) is None:
        endpoint._public_match_client = endpoint._instantiate_public_match_client()
    out = {}
    for i in range(0, len(ids), BATCH_READ):
        chunk = ids[i:i + BATCH_READ]
        try:
            dps = endpoint.read_index_datapoints(
                deployed_index_id=SOURCE_DEPLOYED_ID,
                ids=chunk,
            )
        except Exception as exc:
            print(f"  ! read failed at offset {i}: {exc}")
            continue
        for dp in dps:
            out[dp.datapoint_id] = list(dp.feature_vector)
    return out


def upsert_to(index, datapoints: list[dict]) -> None:
    """Stream upsert in batches. `datapoints` is a list of dicts shaped as
    {datapoint_id, feature_vector, restricts}."""
    from google.cloud.aiplatform.compat.types import index as gca_index
    payload = []
    for d in datapoints:
        restricts = [
            gca_index.IndexDatapoint.Restriction(
                namespace=r["namespace"], allow_list=r["allow_list"])
            for r in d["restricts"]
        ]
        payload.append(gca_index.IndexDatapoint(
            datapoint_id=d["datapoint_id"],
            feature_vector=d["feature_vector"],
            restricts=restricts,
        ))
    for i in range(0, len(payload), BATCH_UP):
        chunk = payload[i:i + BATCH_UP]
        index.upsert_datapoints(datapoints=chunk)
        print(f"  upserted {min(i + BATCH_UP, len(payload))}/{len(payload)}")


def main():
    cfg = load_canvas_config()
    aiplatform.init(project=PROJECT, location=LOCATION)

    datapoints = []
    mode = os.environ.get("SOURCE_MODE", "auto").lower()

    if mode != "synthetic":
        print(f"[step 1/4] sampling up to {LIMIT} segment ids from Firestore…")
        samples = sample_segment_ids(LIMIT)
        if samples:
            print(f"          got {len(samples)} segments from Firestore")
            print(f"[step 2/4] reading raw vectors from {SOURCE_INDEX_DISPLAY}…")
            src_eps = aiplatform.MatchingEngineIndexEndpoint.list(
                filter=f'display_name="{SOURCE_ENDPOINT_DISPLAY}"')
            if src_eps:
                src_ep = src_eps[0]
                ids = [sid for sid, _ in samples]
                vectors = read_vectors(src_ep, ids)
                print(f"          got {len(vectors)} vectors (asked {len(ids)})")
                metas = {sid: meta for sid, meta in samples}
                for sid, vec in vectors.items():
                    datapoints.append({
                        "datapoint_id": sid,
                        "feature_vector": vec,
                        "restricts": restricts_for(metas.get(sid, {})),
                    })

    if not datapoints:
        print("[step 1/4] Generating synthetic vector dataset for canvas demo…")
        datapoints = generate_synthetic_datapoints(LIMIT)

    print(f"[step 3/4] upserting {len(datapoints)} into canvas TREE_AH…")
    tree = aiplatform.MatchingEngineIndex(cfg["tree_ah_index"])
    upsert_to(tree, datapoints)

    print(f"[step 4/4] upserting {len(datapoints)} into canvas BRUTE_FORCE…")
    brute = aiplatform.MatchingEngineIndex(cfg["brute_index"])
    upsert_to(brute, datapoints)

    print(f"\nDone. Streaming upserts are eventually consistent; allow ~30-60s")
    print("before queries see the new datapoints.")


if __name__ == "__main__":
    main()
