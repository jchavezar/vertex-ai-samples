#!/usr/bin/env python3
"""One-time backfill: Vector Search index → BigQuery.

Reads every datapoint (id + 3072-d vector + restricts) out of the deployed
Vector Search index using `read_index_datapoints`, then bulk-loads into the
`envato_vibe.segments` BigQuery table.

Re-runnable. Wipes + reloads the table each time so we never get duplicates.

Usage:
    python backends/bigquery/backfill.py
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
import time
from pathlib import Path
from typing import Iterable

from google.cloud import aiplatform, bigquery, firestore

PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", "vtxdemos")
REGION  = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
ENDPOINT_ID  = os.getenv("BACKFILL_VS_ENDPOINT_ID", "546600215516282880")
DEPLOYED_ID  = os.getenv("BACKFILL_VS_DEPLOYED_ID", "envato_vibe_multimodal")
FS_COLLECTION = os.getenv("FIRESTORE_SEGMENTS", "segments")
BQ_TABLE     = os.getenv("BQ_TABLE", "vtxdemos.envato_vibe.segments")
BATCH = 200  # read_index_datapoints batch size


def chunked(seq: list, n: int) -> Iterable[list]:
    for i in range(0, len(seq), n):
        yield seq[i:i + n]


def list_all_ids() -> list[str]:
    """Source of truth: every Firestore segment document id."""
    db = firestore.Client(project=PROJECT, database="(default)")
    ids = [d.id for d in db.collection(FS_COLLECTION).select([]).stream()]
    return sorted(ids)


def read_vectors(ids: list[str]) -> list[dict]:
    aiplatform.init(project=PROJECT, location=REGION)
    ep = aiplatform.MatchingEngineIndexEndpoint(ENDPOINT_ID)
    rows: list[dict] = []
    missing = 0
    for batch in chunked(ids, BATCH):
        try:
            dps = ep.read_index_datapoints(deployed_index_id=DEPLOYED_ID, ids=batch)
        except Exception as e:
            print(f"[!] read failed for batch starting {batch[0]}: {e}", file=sys.stderr)
            continue
        got = {dp.datapoint_id for dp in dps}
        missing += len(batch) - len(got)
        for dp in dps:
            r = {n.namespace: list(n.allow_list) for n in dp.restricts}
            rows.append({
                "datapoint_id": dp.datapoint_id,
                "modality":      (r.get("modality")     or [None])[0],
                "kind":          (r.get("kind")         or [None])[0],
                "tempo_bucket":  (r.get("tempo_bucket") or [None])[0],
                "length_bucket": (r.get("length_bucket") or [None])[0],
                "embedding": list(dp.feature_vector),
            })
        print(f"  read {len(rows):>5} / {len(ids)}  (missing so far: {missing})")
    return rows


def load_into_bq(rows: list[dict]) -> None:
    client = bigquery.Client(project=PROJECT)
    # Stage as newline-delimited JSON. ARRAY<FLOAT64> loads natively.
    with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False) as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
        path = Path(f.name)
    try:
        job_config = bigquery.LoadJobConfig(
            source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
            write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
            schema=[
                bigquery.SchemaField("datapoint_id",  "STRING", mode="REQUIRED"),
                bigquery.SchemaField("modality",      "STRING"),
                bigquery.SchemaField("kind",          "STRING"),
                bigquery.SchemaField("tempo_bucket",  "STRING"),
                bigquery.SchemaField("length_bucket", "STRING"),
                bigquery.SchemaField("embedding",     "FLOAT64", mode="REPEATED"),
            ],
        )
        with path.open("rb") as fh:
            job = client.load_table_from_file(fh, BQ_TABLE, job_config=job_config)
        job.result()
        print(f"[ok] loaded {job.output_rows} rows into {BQ_TABLE}")
    finally:
        path.unlink(missing_ok=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="read only, skip BQ load")
    args = ap.parse_args()

    t0 = time.time()
    print(f"[1/3] listing ids from Firestore '{FS_COLLECTION}'...")
    ids = list_all_ids()
    print(f"      → {len(ids)} ids")

    print(f"[2/3] reading vectors from VS endpoint {ENDPOINT_ID} / {DEPLOYED_ID}...")
    rows = read_vectors(ids)
    print(f"      → {len(rows)} datapoints with vectors")

    if args.dry_run:
        print("[dry-run] skipping BQ load.")
        return

    print(f"[3/3] loading into BigQuery {BQ_TABLE}...")
    load_into_bq(rows)
    print(f"done in {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()
