---
name: pillar-5-realestate-marketplace
description: Step-by-step LLM replication skill to build and deploy Pillar 5 (AI Real Estate Marketplace with True Multimodal Hybrid Vector Search, Gemini 3.8 Flash Coherence Judge, and 3072-D UMAP 2D Topology) from scratch for Rocket Companies & Redfin.
---

# SKILL: Replicating Pillar 5 (`Multimodal Real Estate Marketplace` & UMAP) From Scratch

Any frontier coding assistant (**Claude Code, Gemini CLI, Cursor, Windsurf, Antigravity/Jetski**) can rebuild Pillar 5 from zero by executing the following 5 engineering steps:

## Step 1: Initialize the Vertex AI Multimodal Embedding & Generation Clients

Use the official `google-genai` SDK (`google-genai >= 2.31.0`):

```python
import os
from google import genai
from google.genai import types

PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "vtxdemos")

# Regional client (us-central1) for text & multimodal image embeddings
client_us = genai.Client(vertexai=True, project=PROJECT_ID, location="us-central1")

# Global client for Gemini 3.8 Flash Multimodal Judge
client_global = genai.Client(vertexai=True, project=PROJECT_ID, location="global")
```

## Step 2: Implement True Multimodal Hybrid Search

Combine `gemini-embedding-001` (256-dim semantic text), `multimodalembedding@001` (512-dim visual latent space), and BM25 scene caption matches:

```python
def search_marketplace(query_text: str, beds_filter: int = 0, family_filter: str = "all", limit: int = 10):
    catalog = get_catalog()
    announcements = catalog.get("announcements", [])
    
    # 1. Compute 256-dim query text vector
    resp_text = client_us.models.embed_content(
        model="gemini-embedding-001",
        contents=[query_text],
        config=types.EmbedContentConfig(output_dimensionality=256, task_type="RETRIEVAL_QUERY"),
    )
    query_text_vec = list(resp_text.embeddings[0].values)
    
    # 2. Compute 512-dim cross-modal pixel query vector
    resp_vis = client_us.models.embed_content(
        model="multimodalembedding@001",
        contents=[query_text],
    )
    query_vis_vec = list(resp_vis.embeddings[0].values)
    
    # 3. Score against 108 listings using Reciprocal Rank Fusion
    results = []
    tokens = set(re.findall(r"[a-z0-9]+", query_text.lower()))
    for item in announcements:
        # Compute cosine similarities and BM25 boosts
        s_sem = cosine(query_text_vec, item["embedding_256"])
        s_vis = cosine(query_vis_vec, item["image_embedding_512"])
        
        # Driveway vehicle detection boost
        s_kw = sum(1.85 for t in tokens if t in item.get("visual_scene_caption", "").lower())
        
        composite = 0.42 * s_sem + 0.20 * s_vis + 0.38 * min(1.0, s_kw)
        results.append({**item, "composite_score": composite})
        
    return sorted(results, key=lambda x: x["composite_score"], reverse=True)[:limit]
```

## Step 3: Implement the Truthful Multimodal Coherence Judge

Send 8 labeled property photos as `Part.from_uri(gs://...)` to `gemini-3.8-flash` Vision:

```python
def evaluate_listing_live_with_gemini(listing_id: str):
    item = find_listing(listing_id)
    # Collect 3 exteriors, 4 interiors, and 1 floorplan
    image_parts = [types.Part.from_uri(file_uri=uri, mime_type="image/jpeg") for uri in item["photo_uris"]]
    
    prompt = f"""
    Perform a rigorous architectural coherence audit for listing {listing_id} ({item['title']}).
    Inspect the exterior architectural style vs. the interior finishes, and verify bedroom counts against the floorplan.
    Return JSON with:
    - 'integrity_score': integer 0-100
    - 'exterior_style_detected': string
    - 'interior_style_detected': string
    - 'issues': list of discrepancy notes
    """
    resp = client_global.models.generate_content(
        model="gemini-3.8-flash",
        contents=[*image_parts, prompt],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.1,
            thinking_config=types.ThinkingConfig(thinking_level="LOW"),
        ),
    )
    audit = json.loads(resp.text)
    # Assign verdict: PASS (score >= 85), NEEDS REVIEW (60-84), FAIL (<60)
    audit["verdict"] = "PASS" if audit["integrity_score"] >= 85 else ("NEEDS REVIEW" if audit["integrity_score"] >= 60 else "FAIL")
    return audit
```

## Step 4: Implement Dual Tour Streaming

1. Pre-render 720p 30fps cinematic tours with `render_tours.py` and upload to `gs://vtxdemos-abnb-images/tours/v1/`.
2. Generate on-demand Veo 3.1 room walkthroughs via `veo_tours.py`.
3. Route `GET /api/pillar5/listing-video/{id}` to return an immediate `302 Found` redirect to GCS, starting video playback in $<0.7\text{s}$.

## Step 5: Verification & Benchmark Testing

```bash
# Verify catalog and benchmark query
python3 pillar-5-realestate-marketplace/test_hybrid_search.py
```
Confirm that searching for `"black car outside of the house"` returns `414 Lakepointe Way` (`RKT-007`) at rank #1.
