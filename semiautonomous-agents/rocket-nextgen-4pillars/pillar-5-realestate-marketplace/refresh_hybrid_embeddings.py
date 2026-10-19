#!/usr/bin/env python3
"""Refreshes 128-dim L2-normalized Hybrid Vector Search embeddings (text_vec & visual_vec)
for all 108 distinct architectural homes in Pillar 5 Real Estate Marketplace.
"""

import ast
import base64
from concurrent.futures import ThreadPoolExecutor
import json
import math
import os
from pathlib import Path
import subprocess
import time
from typing import Any, Dict, List
import urllib.request

# Ensure no mTLS OpenSSL requirement issues in standard python environments
os.environ.setdefault("GOOGLE_API_USE_CLIENT_CERTIFICATE", "false")

from google import genai
from google.genai import types

PROJECT_ID = "vtxdemos"
GCS_BUCKET = "vtxdemos-abnb-images"
GCS_DEST = f"gs://{GCS_BUCKET}/rocket_re_cdn/v1/catalog_108_index.json"

BASE_DIR = Path(__file__).resolve().parent
CATALOG_PATH = BASE_DIR / "catalog_108_index.json"
REGEN_SCRIPT_PATH = BASE_DIR / "regenerate_108_distinct_houses.py"


def load_distinct_subtypes() -> Dict[str, str]:
    """Parses DISTINCT_SUBTYPES mapping from regenerate_108_distinct_houses.py via AST."""
    with open(REGEN_SCRIPT_PATH, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read())
    
    subtypes = {}
    for node in tree.body:
        if isinstance(node, ast.AnnAssign) and getattr(node.target, "id", None) == "DISTINCT_SUBTYPES":
            val = ast.literal_eval(node.value)
            for fam, pairs in val.items():
                for name, desc in pairs:
                    subtypes[name] = desc
    return subtypes


def build_text_input(item: Dict[str, Any]) -> str:
    """Builds comprehensive text semantic payload for text_vec."""
    palette = ", ".join(item.get("palette_tags", []))
    room_captions = " | ".join(
        f"{r.get('title', '')}: {r.get('caption', '')}"
        for r in item.get("rooms", [])
    )
    return (
        f"Listing ID: {item.get('id')} | Title: {item.get('title')} | "
        f"Location: {item.get('city')}, {item.get('submarket')} | "
        f"Architectural Family: {item.get('family_name')} | "
        f"Subtype: {item.get('distinct_subtype', '')} | "
        f"Materials & Palette: {palette} | "
        f"Specs: {item.get('beds')} beds, {item.get('baths')} baths, {item.get('sqft')} sqft | "
        f"Price: ${item.get('price', 0):,} | "
        f"Description: {item.get('description', '')} | "
        f"Rooms & Layout: {room_captions}"
    )


def build_visual_input(item: Dict[str, Any], subtype_blueprints: Dict[str, str]) -> str:
    """Builds visual facade & architectural DNA payload for visual_vec."""
    subtype = item.get("distinct_subtype", "")
    facade_blueprint = subtype_blueprints.get(subtype, "")
    palette = ", ".join(item.get("palette_tags", []))
    
    exterior_rooms = [
        r for r in item.get("rooms", [])
        if r.get("category") == "exterior" or "ext_" in r.get("room_id", "")
    ]
    ext_desc = " | ".join(f"{r.get('title', '')}: {r.get('caption', '')}" for r in exterior_rooms)
    
    interior_rooms = [
        r for r in item.get("rooms", [])
        if r.get("category") != "exterior" and "ext_" not in r.get("room_id", "")
    ]
    int_desc = " | ".join(f"{r.get('title', '')}: {r.get('caption', '')}" for r in interior_rooms[:6])
    
    return (
        f"Architectural visual facade, exterior elevation and interior material DNA: {item.get('title')} | "
        f"Distinct Subtype: {subtype} | "
        f"Facade & Roof Silhouette: {facade_blueprint} | "
        f"Architectural Family: {item.get('family_name')} | "
        f"Material Palette: {palette} | "
        f"Exterior Elevations: {ext_desc} | "
        f"Interior Materials & Finishes: {int_desc}"
    )


def l2_normalize(vec: List[float]) -> List[float]:
    """Computes unit-length L2-normalized vector."""
    norm = math.sqrt(sum(x * x for x in vec))
    if norm < 1e-9:
        return [0.0] * len(vec)
    return [round(x / norm, 6) for x in vec]


def embed_batch_with_retry(client: genai.Client, texts: List[str], retries: int = 3) -> List[List[float]]:
    """Embeds a batch of texts using gemini-embedding-001 (dim=128) with retry logic."""
    for attempt in range(retries):
        try:
            resp = client.models.embed_content(
                model="gemini-embedding-001",
                contents=texts,
                config=types.EmbedContentConfig(output_dimensionality=128),
            )
            return [l2_normalize(list(emb.values)) for emb in resp.embeddings]
        except Exception as e:
            if attempt == retries - 1:
                raise
            time.sleep(1.0 + attempt * 2.0)
    return []


def refresh_catalog_embeddings():
    print("=" * 72)
    print("Refreshing Hybrid Vector Search Embeddings for 108 Distinct Houses")
    print("=" * 72)
    
    t0 = time.perf_counter()
    subtype_blueprints = load_distinct_subtypes()
    print(f"Loaded {len(subtype_blueprints)} distinct subtype blueprints.")
    
    with open(CATALOG_PATH, "r", encoding="utf-8") as f:
        catalog = json.load(f)
        
    items = catalog.get("announcements", [])
    print(f"Loaded catalog with {len(items)} announcements.")
    
    text_inputs = [build_text_input(item) for item in items]
    visual_inputs = [build_visual_input(item, subtype_blueprints) for item in items]
    
    client = genai.Client(vertexai=True, project=PROJECT_ID, location="us-central1")
    
    batch_size = 27  # 108 / 27 = 4 batches
    print(f"\nComputing text_vec embeddings ({len(text_inputs)} items, batch size {batch_size})...")
    text_vecs: List[List[float]] = []
    for i in range(0, len(text_inputs), batch_size):
        chunk = text_inputs[i : i + batch_size]
        print(f"  Embedding text batch {i // batch_size + 1} ({len(chunk)} items)...")
        vecs = embed_batch_with_retry(client, chunk)
        text_vecs.extend(vecs)
        
    print(f"\nComputing visual_vec embeddings ({len(visual_inputs)} items, batch size {batch_size})...")
    visual_vecs: List[List[float]] = []
    for i in range(0, len(visual_inputs), batch_size):
        chunk = visual_inputs[i : i + batch_size]
        print(f"  Embedding visual batch {i // batch_size + 1} ({len(chunk)} items)...")
        vecs = embed_batch_with_retry(client, chunk)
        visual_vecs.extend(vecs)
        
    # Verification of dimensions and normalization
    print("\nVerifying embedding vectors...")
    for idx, (t_vec, v_vec) in enumerate(zip(text_vecs, visual_vecs)):
        assert len(t_vec) == 128, f"Item {idx} text_vec len {len(t_vec)} != 128"
        assert len(v_vec) == 128, f"Item {idx} visual_vec len {len(v_vec)} != 128"
        t_norm = math.sqrt(sum(x * x for x in t_vec))
        v_norm = math.sqrt(sum(x * x for x in v_vec))
        assert abs(t_norm - 1.0) < 1e-3, f"Item {idx} text_vec norm {t_norm} != 1.0"
        assert abs(v_norm - 1.0) < 1e-3, f"Item {idx} visual_vec norm {v_norm} != 1.0"
        items[idx]["text_vec"] = t_vec
        items[idx]["visual_vec"] = v_vec
        
    print("All 108 listings successfully updated with verified 128-dim L2-normalized vectors!")
    
    # Save locally
    catalog["announcements"] = items
    with open(CATALOG_PATH, "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=2)
    file_size_mb = CATALOG_PATH.stat().st_size / (1024 * 1024)
    print(f"Saved local catalog: {CATALOG_PATH} ({file_size_mb:.2f} MB)")
    
    # Upload to GCS
    print(f"\nUploading updated catalog to {GCS_DEST} ...")
    upload_cmd = [
        "gcloud", "storage", "cp",
        "--cache-control=public, max-age=60, no-cache",
        str(CATALOG_PATH),
        GCS_DEST,
    ]
    res = subprocess.run(upload_cmd, capture_output=True, text=True, check=True)
    print(f"Upload complete:\n{res.stdout.strip() or res.stderr.strip()}")
    
    elapsed = time.perf_counter() - t0
    print(f"\nRefresh pipeline finished in {elapsed:.2f}s!")


if __name__ == "__main__":
    refresh_catalog_embeddings()
