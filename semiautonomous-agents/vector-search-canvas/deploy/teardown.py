"""Undeploy and delete the canvas indexes + endpoint.

Deployed Vector Search replicas cost money even when idle (~$0.40/hr per replica).
Run this when you're done playing with the canvas demo to bring spend to zero.

Usage:
    python teardown.py                           # dry run, prints what would be deleted
    CONFIRM=yes python teardown.py               # undeploy & delete endpoint AND indexes
    CONFIRM=yes KEEP_INDEXES=yes python teardown.py # undeploy & delete endpoint only (keeps indexes saved in Vertex AI)
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from google.cloud import aiplatform

PROJECT  = os.environ.get("GOOGLE_CLOUD_PROJECT", "vtxdemos")
LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")


def main():
    cfg_path = Path(__file__).parent / "indexes.json"
    if not cfg_path.exists():
        sys.exit("indexes.json missing — nothing to tear down (or already deleted)")
    cfg = json.loads(cfg_path.read_text())
    confirm = os.environ.get("CONFIRM", "").lower() == "yes"
    keep_indexes = os.environ.get("KEEP_INDEXES", "").lower() in ("yes", "true", "1")

    aiplatform.init(project=PROJECT, location=LOCATION)

    try:
        ep = aiplatform.MatchingEngineIndexEndpoint(cfg["endpoint"])
        deployed = [d.id for d in (ep.deployed_indexes or [])]
        print(f"endpoint:   {ep.resource_name}")
        print(f"deployed:   {deployed}")
    except Exception as exc:
        print(f"endpoint:   {cfg.get('endpoint')} (could not load: {exc})")
        ep = None
        deployed = []

    print(f"tree_ah:    {cfg.get('tree_ah_index')}")
    print(f"brute:      {cfg.get('brute_index')}")
    print(f"keep_idx:   {keep_indexes}")
    print()

    if not confirm:
        print("DRY RUN — re-run with CONFIRM=yes to execute.")
        if keep_indexes:
            print("(Mode: undeploy and delete endpoint ONLY, keeping indexes in Vertex AI)")
        else:
            print("(Mode: undeploy, delete endpoint, AND delete underlying indexes)")
        return

    if ep:
        for d in list(ep.deployed_indexes or []):
            print(f"[undeploy] {d.id} from endpoint…")
            try:
                ep.undeploy_index(deployed_index_id=d.id, sync=True)
                print(f"[ok]       undeployed {d.id}")
            except Exception as exc:
                print(f"  ! undeploy {d.id} failed: {exc}")

        print(f"[delete] endpoint {ep.resource_name}…")
        try:
            ep.delete(sync=True)
            print("[ok]     endpoint deleted")
        except Exception as exc:
            print(f"  ! endpoint delete failed: {exc}")

    if not keep_indexes:
        for key in ("tree_ah_index", "brute_index"):
            if key in cfg and cfg[key]:
                try:
                    idx = aiplatform.MatchingEngineIndex(cfg[key])
                    print(f"[delete] {key} ({cfg[key]})…")
                    idx.delete(sync=True)
                    print(f"[ok]     {key} deleted")
                except Exception as exc:
                    print(f"  ! {key} delete failed: {exc}")
        cfg_path.unlink(missing_ok=True)
    else:
        print("[info] Keeping underlying indexes saved in Vertex AI as requested.")

    print("\nTeardown complete.")


if __name__ == "__main__":
    main()
