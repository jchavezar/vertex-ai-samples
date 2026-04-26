"""Create the two Vector Search indexes for the canvas demo + an endpoint.

Two indexes so the UI can show APPROXIMATE (TREE_AH) vs EXACT (BRUTE_FORCE)
side by side and the user can see real recall@k drop in real time.

Both are STREAM_UPDATE so we can demo live upserts later. Both are public
endpoints (no PSC/VPC) — simplest path for a learning sandbox.

Run once:
    python create_indexes.py
Outputs the resource names to stdout. Capture them for the app config.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

from google.cloud import aiplatform

PROJECT  = "vtxdemos"
LOCATION = "us-central1"
DIMS     = 3072  # gemini-embedding-2-preview output dim

TREE_AH_NAME    = "vs-canvas-tree-ah"
BRUTE_NAME      = "vs-canvas-bruteforce"
ENDPOINT_NAME   = "vs-canvas-endpoint"
DEPLOYED_TREE   = "vs_canvas_tree_ah"
DEPLOYED_BRUTE  = "vs_canvas_brute"


def get_or_create_indexes():
    """Idempotent: returns existing index if display name already taken."""
    aiplatform.init(project=PROJECT, location=LOCATION)

    existing = {i.display_name: i for i in aiplatform.MatchingEngineIndex.list()}

    if TREE_AH_NAME in existing:
        print(f"[skip] tree-ah index exists: {existing[TREE_AH_NAME].resource_name}")
        tree_ah = existing[TREE_AH_NAME]
    else:
        print(f"[create] tree-ah index ({DIMS}-d, COSINE)…")
        tree_ah = aiplatform.MatchingEngineIndex.create_tree_ah_index(
            display_name=TREE_AH_NAME,
            dimensions=DIMS,
            approximate_neighbors_count=150,
            distance_measure_type="COSINE_DISTANCE",
            leaf_node_embedding_count=500,
            leaf_nodes_to_search_percent=10,
            description="Vector Search Canvas — TREE_AH cosine, streaming",
            index_update_method="STREAM_UPDATE",
            sync=True,
        )
        print(f"[ok]   tree-ah: {tree_ah.resource_name}")

    if BRUTE_NAME in existing:
        print(f"[skip] brute-force index exists: {existing[BRUTE_NAME].resource_name}")
        brute = existing[BRUTE_NAME]
    else:
        print(f"[create] brute-force index ({DIMS}-d, COSINE)…")
        brute = aiplatform.MatchingEngineIndex.create_brute_force_index(
            display_name=BRUTE_NAME,
            dimensions=DIMS,
            distance_measure_type="COSINE_DISTANCE",
            description="Vector Search Canvas — BRUTE_FORCE cosine baseline",
            index_update_method="STREAM_UPDATE",
            sync=True,
        )
        print(f"[ok]   brute: {brute.resource_name}")

    return tree_ah, brute


def get_or_create_endpoint():
    aiplatform.init(project=PROJECT, location=LOCATION)
    existing = {e.display_name: e for e in aiplatform.MatchingEngineIndexEndpoint.list()}
    if ENDPOINT_NAME in existing:
        ep = existing[ENDPOINT_NAME]
        print(f"[skip] endpoint exists: {ep.resource_name}")
        return ep
    print(f"[create] endpoint…")
    ep = aiplatform.MatchingEngineIndexEndpoint.create(
        display_name=ENDPOINT_NAME,
        public_endpoint_enabled=True,
        description="Vector Search Canvas — public endpoint",
        sync=True,
    )
    print(f"[ok]   endpoint: {ep.resource_name}")
    return ep


def deploy(endpoint, tree_ah, brute):
    deployed_ids = {d.id for d in (endpoint.deployed_indexes or [])}

    if DEPLOYED_TREE not in deployed_ids:
        print(f"[deploy] tree-ah → {DEPLOYED_TREE} (this can take ~30 min)…")
        endpoint.deploy_index(
            index=tree_ah,
            deployed_index_id=DEPLOYED_TREE,
            display_name=DEPLOYED_TREE,
            min_replica_count=1,
            max_replica_count=1,
            sync=False,
        )
        print(f"[ok]   tree-ah deploy started")
    else:
        print(f"[skip] tree-ah already deployed as {DEPLOYED_TREE}")

    if DEPLOYED_BRUTE not in deployed_ids:
        print(f"[deploy] brute-force → {DEPLOYED_BRUTE}…")
        endpoint.deploy_index(
            index=brute,
            deployed_index_id=DEPLOYED_BRUTE,
            display_name=DEPLOYED_BRUTE,
            min_replica_count=1,
            max_replica_count=1,
            sync=False,
        )
        print(f"[ok]   brute deploy started")
    else:
        print(f"[skip] brute already deployed as {DEPLOYED_BRUTE}")


def write_config(tree_ah, brute, endpoint):
    cfg = {
        "project": PROJECT,
        "location": LOCATION,
        "tree_ah_index": tree_ah.resource_name,
        "brute_index": brute.resource_name,
        "endpoint": endpoint.resource_name,
        "deployed_tree": DEPLOYED_TREE,
        "deployed_brute": DEPLOYED_BRUTE,
    }
    out = Path(__file__).parent / "indexes.json"
    out.write_text(json.dumps(cfg, indent=2))
    print(f"[ok]   wrote {out}")


def main():
    tree_ah, brute = get_or_create_indexes()
    endpoint = get_or_create_endpoint()
    deploy(endpoint, tree_ah, brute)
    write_config(tree_ah, brute, endpoint)
    print()
    print("Index/endpoint creation kicked off. Deploy completion takes 20-45 min.")
    print("Poll with: gcloud ai index-endpoints describe", endpoint.name,
          f"--region={LOCATION} --project={PROJECT}")


if __name__ == "__main__":
    main()
