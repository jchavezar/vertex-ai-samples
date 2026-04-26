"""Undeploy and delete the canvas indexes + endpoint.

Deployed Vector Search replicas cost money even when idle. Run this
when you're done playing with the canvas demo to bring spend to zero.

    python teardown.py            # dry run, prints what would be deleted
    CONFIRM=yes python teardown.py # actually delete
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from google.cloud import aiplatform

PROJECT  = "vtxdemos"
LOCATION = "us-central1"


def main():
    cfg_path = Path(__file__).parent / "indexes.json"
    if not cfg_path.exists():
        sys.exit("indexes.json missing — nothing to tear down (or already deleted)")
    cfg = json.loads(cfg_path.read_text())
    confirm = os.environ.get("CONFIRM", "").lower() == "yes"

    aiplatform.init(project=PROJECT, location=LOCATION)
    ep = aiplatform.MatchingEngineIndexEndpoint(cfg["endpoint"])

    print(f"endpoint:   {ep.resource_name}")
    print(f"deployed:   {[d.id for d in (ep.deployed_indexes or [])]}")
    print(f"tree_ah:    {cfg['tree_ah_index']}")
    print(f"brute:      {cfg['brute_index']}")
    print()

    if not confirm:
        print("DRY RUN — re-run with CONFIRM=yes to actually delete")
        return

    for d in list(ep.deployed_indexes or []):
        print(f"[undeploy] {d.id}…")
        ep.undeploy_index(deployed_index_id=d.id, sync=True)

    print(f"[delete] endpoint…")
    ep.delete(sync=True)

    for key in ("tree_ah_index", "brute_index"):
        try:
            idx = aiplatform.MatchingEngineIndex(cfg[key])
            print(f"[delete] {key}…")
            idx.delete(sync=True)
        except Exception as exc:
            print(f"  ! {key} delete failed: {exc}")

    cfg_path.unlink()
    print("done.")


if __name__ == "__main__":
    main()
