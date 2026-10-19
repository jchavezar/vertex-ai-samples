"""Pillar 5: AI Real Estate & Hybrid Vector Marketplace Engine (108 Verified Homes · GCS CDN · Hybrid Image+Text+BM25 Search · Gemini 3.8 Multimodal Coherence Judge)."""

import base64
import json
import math
import os
from pathlib import Path
import re
import threading
import time
from typing import Any, Dict, List, Optional

os.environ.setdefault("GOOGLE_API_USE_CLIENT_CERTIFICATE", "false")

from google import genai
from google.genai import types

PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "vtxdemos")
GCS_MEDIA_BUCKET = os.environ.get("GCS_MEDIA_BUCKET", "vtxdemos-abnb-images")
import urllib.request

BASE_DIR = Path(__file__).resolve().parent
CATALOG_PATH = BASE_DIR / "catalog_108_index.json"
GCS_LIVE_CATALOG_URL = os.environ.get(
    "GCS_LIVE_CATALOG_URL",
    f"https://storage.googleapis.com/{GCS_MEDIA_BUCKET}/rocket_re_cdn/v1/catalog_108_index.json",
)

_CATALOG_CACHE: Optional[Dict[str, Any]] = None
_CATALOG_TS: float = 0.0
_EMBED_CACHE: Dict[str, List[float]] = {}
_CLIENT_US: Optional[genai.Client] = None
_CLIENT_GL: Optional[genai.Client] = None


def _get_us_client() -> genai.Client:
    global _CLIENT_US
    if _CLIENT_US is None:
        _CLIENT_US = genai.Client(vertexai=True, project=PROJECT_ID, location="us-central1")
    return _CLIENT_US


def _get_gl_client() -> genai.Client:
    global _CLIENT_GL
    if _CLIENT_GL is None:
        _CLIENT_GL = genai.Client(vertexai=True, project=PROJECT_ID, location="global")
    return _CLIENT_GL


def get_catalog() -> Dict[str, Any]:
    global _CATALOG_CACHE, _CATALOG_TS
    now = time.time()
    if _CATALOG_CACHE is None and CATALOG_PATH.exists():
        try:
            _CATALOG_CACHE = json.loads(CATALOG_PATH.read_text())
            _CATALOG_TS = now
        except Exception:
            pass
    if _CATALOG_CACHE is None and now - _CATALOG_TS > 35.0:
        _CATALOG_TS = now
        try:
            req = urllib.request.Request(
                f"{GCS_LIVE_CATALOG_URL}?t={int(now)}",
                headers={"Cache-Control": "no-cache"},
            )
            with urllib.request.urlopen(req, timeout=2.5) as resp:
                remote_cat = json.loads(resp.read().decode("utf-8"))
                if isinstance(remote_cat, dict) and remote_cat.get("announcements"):
                    _CATALOG_CACHE = remote_cat
        except Exception:
            pass
    return _CATALOG_CACHE or {
        "total_announcements": 0,
        "grouping_summary": {"by_bedrooms": {}, "by_architecture": []},
        "announcements": [],
    }


def _cosine(v1: List[float], v2: List[float]) -> float:
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0
    return sum(a * b for a, b in zip(v1, v2))


def _embed_query_256(text: str) -> List[float]:
    key = f"g256:{text.strip().lower()}"
    if key in _EMBED_CACHE:
        return _EMBED_CACHE[key]
    try:
        client = _get_us_client()
        resp = client.models.embed_content(
            model="gemini-embedding-001",
            contents=[text],
            config=types.EmbedContentConfig(
                output_dimensionality=256,
                task_type="RETRIEVAL_QUERY",
            ),
        )
        vec = list(resp.embeddings[0].values)
        norm = math.sqrt(sum(x * x for x in vec)) or 1.0
        vec = [x / norm for x in vec]
        _EMBED_CACHE[key] = vec
        return vec
    except Exception:
        return []


def _embed_mm_text_512(text: str) -> List[float]:
    """Projects a text query directly into the 512-d Vertex AI multimodalembedding@001 image-pixel space."""
    key = f"mm512:{text.strip().lower()}"
    if key in _EMBED_CACHE:
        return _EMBED_CACHE[key]
    try:
        import google.auth
        import google.auth.transport.requests

        creds, _ = google.auth.default()
        if not creds.valid:
            creds.refresh(google.auth.transport.requests.Request())
        url = f"https://us-central1-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/us-central1/publishers/google/models/multimodalembedding@001:predict"
        payload = {
            "instances": [{"text": text[:500]}],
            "parameters": {"dimension": 512},
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {creds.token}",
                "Content-Type": "application/json",
            },
        )
        with urllib.request.urlopen(req, timeout=4.0) as resp:
            pred = json.loads(resp.read().decode("utf-8"))["predictions"][0]
            vec = list(pred["textEmbedding"])
            norm = math.sqrt(sum(x * x for x in vec)) or 1.0
            vec = [x / norm for x in vec]
            _EMBED_CACHE[key] = vec
            return vec
    except Exception:
        return []


_STOPWORDS = {
    "the", "of", "in", "on", "at", "to", "for", "with", "and", "or", "a", "an",
    "by", "from", "is", "are", "show", "me", "find", "house", "home", "homes",
    "houses", "outside", "inside", "near", "that", "has", "have",
}

_VISUAL_SYNONYMS = {
    "car": {"car", "cars", "suv", "sedan", "vehicle", "vehicles", "sports", "coupe", "parked"},
    "cars": {"car", "cars", "suv", "sedan", "vehicle", "vehicles", "parked"},
    "black": {"black", "dark", "charcoal", "ebony", "obsidian", "slate", "blackened"},
    "pool": {"pool", "swimming", "infinity", "lap"},
    "tree": {"tree", "trees", "foliage", "oak", "pine", "palm", "autumn", "forest"},
    "trees": {"tree", "trees", "foliage", "oak", "pine", "palm", "autumn", "forest"},
}


def _bm25_keyword_score(query: str, item: Dict[str, Any]) -> float:
    if not query.strip():
        return 1.0
    raw_tokens = [t for t in re.findall(r"[a-z0-9]+", query.lower()) if len(t) >= 2]
    tokens = [t for t in raw_tokens if t not in _STOPWORDS] or raw_tokens
    if not tokens:
        return 1.0

    vis_scene = (item.get("visual_scene_caption") or "").lower()
    vis_words = set(re.findall(r"[a-z0-9]+", vis_scene))

    meta_text = (
        f"{item['id']} {item['title']} {item['address']} {item['city']} {item['submarket']} "
        f"{item['family_name']} {' '.join(item.get('palette_tags', []))} {item['beds']}br {item['beds']} bedroom "
        f"{item['description']} " + " ".join(r["title"] + " " + r["caption"] for r in item.get("rooms", []))
    ).lower()
    meta_words = set(re.findall(r"[a-z0-9]+", meta_text))
    title_city_words = set(re.findall(r"[a-z0-9]+", f"{item['title']} {item['city']} {item['family_name']}".lower()))

    hits = 0.0
    vis_hits = 0
    exact_vis_hits = 0
    for tok in tokens:
        syn_set = _VISUAL_SYNONYMS.get(tok, {tok})
        if tok in vis_words:
            # Exact literal word match inside the actual exterior photo's Gemini Vision inspection!
            hits += 1.85
            vis_hits += 1
            exact_vis_hits += 1
        elif syn_set & vis_words:
            # Visual synonym match inside the exterior photo's Gemini Vision inspection
            hits += 1.35
            vis_hits += 1
        elif tok in title_city_words:
            hits += 1.20
        elif syn_set & meta_words:
            hits += 0.75

    # Multi-term visual co-occurrence bonus (e.g. BOTH "black" AND "car" in the photo scene!)
    if len(tokens) >= 2 and exact_vis_hits == len(tokens):
        hits += 1.50
    elif len(tokens) >= 2 and vis_hits == len(tokens):
        hits += 0.90

    return min(1.0, hits / max(1.0, len(tokens) * 2.6))


def hybrid_search_marketplace(
    query_text: str = "",
    beds_filter: int = 0,
    family_filter: str = "all",
    max_price: int = 3500000,
    reference_listing_id: str = "",
    reference_image_b64: str = "",
    semantic_weight: float = 0.45,
    visual_weight: float = 0.35,
    keyword_weight: float = 0.20,
    limit: int = 108,
) -> Dict[str, Any]:
    """Executes True Multimodal Hybrid Vector Search combining:
    1. Dense Text + Vision Scene Embedding (`gemini-embedding-001` 256-dim cosine similarity)
    2. True Image-Pixel CLIP Embedding (`multimodalembedding@001` 512-dim + `visual_vec` over Gemini Vision photo scene)
    3. Whole-Word BM25 & Visual Scene Co-Occurrence Scoring
    """
    t0 = time.perf_counter()
    cat = get_catalog()
    items = cat.get("announcements", [])

    visual_query_caption = ""
    if reference_image_b64:
        try:
            raw_b64 = reference_image_b64.split(",")[-1]
            img_bytes = base64.b64decode(raw_b64)
            resp = _get_gl_client().models.generate_content(
                model="gemini-3.8-flash",
                contents=[
                    types.Part.from_bytes(data=img_bytes, mime_type="image/jpeg"),
                    "Describe this home or room's architectural style, visible vehicles/driveway, trees/landscaping, facade/interior materials, wood/stone palette, and layout in 30 concise keywords.",
                ],
                config=types.GenerateContentConfig(
                    temperature=0.1,
                    thinking_config=types.ThinkingConfig(thinking_level="LOW"),
                ),
            )
            visual_query_caption = (resp.text or "").strip()
        except Exception:
            visual_query_caption = ""

    ref_visual_vec: List[float] = []
    ref_mm_vec: List[float] = []
    if reference_listing_id:
        for it in items:
            if it["id"] == reference_listing_id:
                ref_visual_vec = it.get("visual_vec", [])
                ref_mm_vec = it.get("mm_image_vec", [])
                break

    combined_query = f"{query_text} {visual_query_caption}".strip()
    query_vec: List[float] = _embed_query_256(combined_query) if combined_query else []
    query_mm_vec: List[float] = _embed_mm_text_512(combined_query) if combined_query else []

    # Normalize weights
    w_sum = max(0.01, semantic_weight + visual_weight + keyword_weight)
    w_sem = semantic_weight / w_sum
    w_vis = visual_weight / w_sum
    w_kw = keyword_weight / w_sum

    scored_results = []
    filtered_bed_counts: Dict[int, int] = {2: 0, 3: 0, 4: 0, 5: 0, 6: 0}
    filtered_fam_counts: Dict[str, int] = {}

    # Pre-check if strict filters yield 0 homes; if so, auto-relax max_price (and beds_filter if needed) so categories never show 0 homes
    candidate_items = [
        it for it in items
        if (not beds_filter or int(it["beds"]) == int(beds_filter))
        and (not family_filter or family_filter == "all" or it["family_id"] == family_filter)
        and (not max_price or int(it["price"]) <= int(max_price))
    ]
    if not candidate_items:
        candidate_items = [
            it for it in items
            if (not beds_filter or int(it["beds"]) == int(beds_filter))
            and (not family_filter or family_filter == "all" or it["family_id"] == family_filter)
        ]
    if not candidate_items:
        candidate_items = [
            it for it in items
            if (not family_filter or family_filter == "all" or it["family_id"] == family_filter)
        ]
    if not candidate_items:
        candidate_items = list(items)

    for it in candidate_items:

        # 1. Semantic score (gemini-embedding-001 256-d over text + photo scene)
        if query_vec and it.get("text_vec"):
            sem_score = max(0.0, _cosine(query_vec, it["text_vec"]))
        else:
            sem_score = 0.94

        # 2. Visual score (combines gemini-embedding-001 256-d over Gemini Vision photo scene + multimodalembedding@001 512-d raw image pixels)
        if ref_visual_vec and it.get("visual_vec"):
            v_cos = max(0.0, _cosine(ref_visual_vec, it["visual_vec"]))
            mm_cos = max(0.0, _cosine(ref_mm_vec, it.get("mm_image_vec", []))) if ref_mm_vec and it.get("mm_image_vec") else v_cos
            vis_score = 0.65 * v_cos + 0.35 * mm_cos
        elif query_vec and it.get("visual_vec"):
            v_cos = max(0.0, _cosine(query_vec, it["visual_vec"]))
            mm_cos = max(0.0, _cosine(query_mm_vec, it.get("mm_image_vec", []))) if query_mm_vec and it.get("mm_image_vec") else 0.0
            # Scale raw CLIP cosine (~0.10 to 0.28) to [0, 1] range alongside dense visual scene cosine
            mm_scaled = min(1.0, max(0.0, mm_cos * 3.8)) if mm_cos > 0 else v_cos
            vis_score = 0.70 * v_cos + 0.30 * mm_scaled
        else:
            vis_score = float(it.get("evaluation", {}).get("overall_judge_score", 98.5)) / 100.0

        # 3. Whole-word BM25 + Photo Scene keyword score
        kw_score = _bm25_keyword_score(combined_query, it) if combined_query else 0.95

        if not combined_query and not ref_visual_vec:
            hybrid = (vis_score * 0.6 + sem_score * 0.4)
        else:
            hybrid = (w_sem * sem_score) + (w_vis * vis_score) + (w_kw * kw_score)

        # Strip raw float arrays from response payload for ultra-fast JSON serialization
        slim = {k: v for k, v in it.items() if k not in ("text_vec", "visual_vec", "mm_image_vec")}
        slim["_raw_hybrid"] = hybrid
        slim["search_scores"] = {
            "hybrid_pct": round(min(99.8, hybrid * 100.0), 1),
            "semantic_pct": round(min(99.8, sem_score * 100.0), 1),
            "visual_pct": round(min(99.8, vis_score * 100.0), 1),
            "keyword_pct": round(min(99.8, kw_score * 100.0), 1),
        }
        scored_results.append(slim)
        filtered_bed_counts[it["beds"]] = filtered_bed_counts.get(it["beds"], 0) + 1
        filtered_fam_counts[it["family_id"]] = filtered_fam_counts.get(it["family_id"], 0) + 1

    if combined_query or ref_visual_vec:
        scored_results.sort(key=lambda x: x["_raw_hybrid"], reverse=True)
    else:
        # Default curated order interleaving all architectural families & bedroom counts
        scored_results.sort(key=lambda x: (x["seq"] % 6, x["seq"]))

    for s in scored_results:
        s.pop("_raw_hybrid", None)

    total_matched = len(scored_results)
    latency_ms = round((time.perf_counter() - t0) * 1000.0, 1)

    return {
        "ok": True,
        "latency_ms": latency_ms,
        "query_text": query_text,
        "visual_query_caption": visual_query_caption,
        "total_catalog": cat.get("total_announcements", 108),
        "total_matched": total_matched,
        "grouping_summary": cat.get("grouping_summary", {}),
        "filtered_distribution": {
            "by_bedrooms": {
                str(b): {
                    "count": c,
                    "pct": round(c * 100.0 / max(1, total_matched), 1),
                }
                for b, c in sorted(filtered_bed_counts.items())
            },
            "by_family": {
                fid: {
                    "count": c,
                    "pct": round(c * 100.0 / max(1, total_matched), 1),
                }
                for fid, c in filtered_fam_counts.items()
            },
        },
        "results": scored_results[:limit],
    }


_JUDGE_MODEL = "gemini-3.8-flash"
_JUDGE_MEDIA_RESOLUTION = os.environ.get("P5_JUDGE_MEDIA_RESOLUTION", "MEDIA_RESOLUTION_LOW")
_GCS_PUBLIC_PREFIX = "https://storage.googleapis.com/"
JUDGE_CACHE_PATH = Path(os.environ.get("P5_JUDGE_CACHE_PATH", str(BASE_DIR.parent / "static" / "judge_live_results.json")))
_JUDGE_CACHE: Optional[Dict[str, Any]] = None
_JUDGE_CACHE_LOCK = threading.Lock()

# Photos shown to the judge, in order (max 8): 3 exteriors + 4 key interiors + the floorplan.
_JUDGE_IMAGE_PLAN = [
    ("ext_front", "Front exterior"),
    ("ext_rear", "Rear exterior / patio"),
    ("ext_aerial", "Aerial exterior"),
    ("living_room", "Great room / living room"),
    ("chef_kitchen", "Kitchen"),
    ("dining_room", "Dining room"),
    ("primary_bedroom", "Primary bedroom"),
    ("floorplan_3d", "3D floorplan"),
]

_JUDGE_STATUS_VALUES = ["CONSISTENT", "MINOR ISSUE", "MISMATCH", "NOT VERIFIABLE"]
_JUDGE_VERDICTS = ["PASS", "NEEDS REVIEW", "FAIL"]
_JUDGE_SEVERITIES = ["low", "medium", "high"]


def _https_to_gs(url: str) -> str:
    """https://storage.googleapis.com/<bucket>/<obj>?v=2 -> gs://<bucket>/<obj> ('' if not a GCS URL)."""
    u = (url or "").split("?", 1)[0]
    if u.startswith(_GCS_PUBLIC_PREFIX):
        return "gs://" + u[len(_GCS_PUBLIC_PREFIX):]
    return ""


def _fetch_image_bytes(url: str, timeout: float = 6.0) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "rocket-p5-judge/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def _judge_select_images(target: Dict[str, Any]) -> List[Dict[str, str]]:
    rooms_by_id = {r.get("room_id"): r for r in target.get("rooms", [])}
    ext_urls = list(target.get("exterior_urls") or [])
    picked: List[Dict[str, str]] = []
    for idx, (room_id, label) in enumerate(_JUDGE_IMAGE_PLAN):
        url = (rooms_by_id.get(room_id) or {}).get("image_url", "")
        if not url and room_id.startswith("ext_") and idx < len(ext_urls):
            url = ext_urls[idx]
        if not url and room_id == "floorplan_3d":
            url = target.get("floorplan_url", "")
        if url:
            picked.append({"room_id": room_id, "label": label, "url": url})
    return picked[:8]


def _photo_provenance(images: List[Dict[str, str]]) -> Dict[str, Any]:
    """Where each photo comes from: listing-specific (/listings/<id>/) or a shared style-tier set (/tiers/<tier>/)."""
    listing_specific, shared, tiers = [], [], set()
    for i, im in enumerate(images):
        m = re.search(r"/tiers/([^/]+)/", im["url"])
        if m:
            shared.append(f"IMG{i + 1}")
            tiers.add(m.group(1))
        else:
            listing_specific.append(f"IMG{i + 1}")
    return {"listing_specific": listing_specific, "shared_style_tier": shared, "tiers": sorted(tiers)}


def _judge_response_schema() -> types.Schema:
    S, T = types.Schema, types.Type
    score = lambda d: S(type=T.NUMBER, minimum=0, maximum=100, description=d)  # noqa: E731
    return S(
        type=T.OBJECT,
        properties={
            "exterior_coherence_score": score(
                "0-100, one decimal. How convincingly the exterior photos show ONE and the same building."),
            "interior_harmony_score": score(
                "0-100, one decimal. How consistent the interiors are with each other AND with the exterior architecture."),
            "room_completeness_score": score(
                "0-100, one decimal. How well the room manifest and the floorplan support the claimed bed/bath count."),
            "overall_judge_score": score(
                "0-100, one decimal. Holistic score (~40% exterior, 35% interior, 25% completeness), lowered for high-severity issues."),
            "verdict": S(type=T.STRING, enum=list(_JUDGE_VERDICTS)),
            "verdict_reason": S(type=T.STRING, description="At most 8 words explaining the verdict."),
            "executive_summary": S(type=T.STRING, description=(
                "Two sentences: what the photos actually show and the main point a buyer should verify.")),
            "exterior_angles_verified": S(type=T.STRING, description=(
                "Short phrase, e.g. how many of the exterior angles depict the same building.")),
            "bedroom_math_verified": S(type=T.STRING, description=(
                "Short phrase comparing the claimed beds/baths with what the floorplan and manifest show.")),
            "exterior_audit_note": S(type=T.STRING, description=(
                "1-2 sentences citing concrete visible features (roof form, facade materials, windows, site) with IMG numbers.")),
            "interior_audit_note": S(type=T.STRING, description=(
                "1-2 sentences citing concrete visible features (floors, ceilings, millwork, palette) with IMG numbers.")),
            "room_by_room_checks": S(
                type=T.ARRAY,
                description="One check per audited space, in the order requested.",
                items=S(
                    type=T.OBJECT,
                    properties={
                        "space": S(type=T.STRING, description="Space name with its IMG references."),
                        "status": S(type=T.STRING, enum=list(_JUDGE_STATUS_VALUES)),
                        "detail": S(type=T.STRING, description=(
                            "One or two sentences of concrete visual evidence (what you see) supporting the status.")),
                    },
                    required=["space", "status", "detail"],
                    property_ordering=["space", "status", "detail"],
                ),
            ),
            "issues": S(
                type=T.ARRAY,
                description="Every inconsistency or unverifiable claim found. Empty array only if nothing is wrong.",
                items=S(
                    type=T.OBJECT,
                    properties={
                        "severity": S(type=T.STRING, enum=list(_JUDGE_SEVERITIES)),
                        "title": S(type=T.STRING, description="At most 10 words, neutral QA language."),
                        "detail": S(type=T.STRING, description="At most 30 words of visual evidence with IMG refs."),
                    },
                    required=["severity", "title", "detail"],
                    property_ordering=["severity", "title", "detail"],
                ),
            ),
        },
        required=[
            "exterior_coherence_score", "interior_harmony_score", "room_completeness_score",
            "overall_judge_score", "verdict", "verdict_reason", "executive_summary", "exterior_angles_verified",
            "bedroom_math_verified", "exterior_audit_note", "interior_audit_note",
            "room_by_room_checks", "issues",
        ],
        property_ordering=[
            "exterior_audit_note", "interior_audit_note", "room_by_room_checks", "issues",
            "exterior_angles_verified", "bedroom_math_verified",
            "exterior_coherence_score", "interior_harmony_score", "room_completeness_score",
            "overall_judge_score", "verdict", "verdict_reason", "executive_summary",
        ],
    )


def _judge_prompt(target: Dict[str, Any], images: List[Dict[str, str]]) -> str:
    img_lines = "\n".join(f"- IMG{i + 1} = {im['label']} ({im['room_id']})" for i, im in enumerate(images))
    ext_refs = ", ".join(f"IMG{i + 1}" for i, im in enumerate(images) if im["room_id"].startswith("ext_")) or "none"
    checks = []
    for i, im in enumerate(images):
        if not im["room_id"].startswith("ext_"):
            checks.append(f"{im['label']} (IMG{i + 1})")
    checks_txt = "; ".join([f"Exterior elevations ({ext_refs})"] + checks)
    manifest = "; ".join(
        f"{r.get('title', '')} [{r.get('dimensions', '')}]" for r in target.get("rooms", [])
    )
    prov = _photo_provenance(images)
    prov_txt = (
        f"Photo provenance (context only, NOT evidence either way): {', '.join(prov['listing_specific']) or 'none'} "
        f"are unique to this listing; {', '.join(prov['shared_style_tier']) or 'none'} come from a shared style-tier "
        f"photo set ({', '.join(prov['tiers']) or 'n/a'}) that is reused by other listings of the same style and size. "
        "Judge only what is visible; if shared photos do not match this home, say so and mention the shared style-tier set."
    )
    return f"""You are an independent, skeptical architectural photo QA auditor for a real-estate marketplace.
The listing below claims that ALL attached photos show ONE single property. Audit that claim using ONLY what
is visible in the photos. The listing text is the claim under test, not evidence.

LISTING CLAIM
- ID: {target.get('id')} | {target.get('title')}
- Address: {target.get('address')}
- Price ${int(target.get('price', 0)):,} | {target.get('beds')} bedrooms | {target.get('baths')} bathrooms | {int(target.get('sqft', 0)):,} sq ft
- Style: {target.get('family_name')} | Palette tags: {', '.join(target.get('palette_tags', []))}
- Room manifest ({target.get('total_rooms_mapped', len(target.get('rooms', [])))} spaces): {manifest}

ATTACHED PHOTOS ({len(images)}), each preceded by its label:
{img_lines}
{prov_txt}

WHAT TO CHECK
A. Exterior coherence ({ext_refs}): same building in every angle? Compare roof form, massing, facade materials,
   window/door pattern, colors, landscaping and site. Name specific matching AND conflicting features.
B. Interior harmony: do the interior photos share one design language (floors, ceilings, millwork, window frames,
   palette), and is that language plausible for the exterior architecture and the claimed style?
C. Room completeness: compare the manifest and the floorplan with the claimed beds/baths. Count only bedrooms and
   bathrooms you can actually make out on the floorplan; if it is not legible, say so. Only one bedroom photo is
   attached: never claim to have seen the other bedrooms.
D. Claim accuracy: do the photos match the stated style and palette tags?

RULES
- Every score must be justified by evidence you cite. Do not default to high scores.
  Rubric: 90-100 = no visible inconsistency and concrete matching evidence; 75-89 = minor inconsistencies or limited
  evidence; 50-74 = clear mismatches; below 50 = photos look like different properties or contradict the claim.
- verdict: PASS only if overall >= 85 and there is no high-severity issue; FAIL if overall < 60; otherwise NEEDS REVIEW.
- room_by_room_checks: exactly one entry per space, in this order: {checks_txt}.
- Refer to photos as IMG1..IMG{len(images)}. Be concise, concrete and factual. Never invent features you cannot see.
- If two photos show the same viewpoint, call them "near-duplicate views" (you cannot know whether files are identical);
  a listing that labels the same view as rear or aerial has not shown that angle.
- Length limits: each check detail <= 25 words; each audit note <= 35 words; executive_summary <= 45 words;
  at most 4 issues.
- Tone: neutral QA language, like an appraiser's report ("inconsistent", "appears to show a different
  property"). Never speculate about intent and never use words such as fraud, fraudulent, scam, deceptive or
  misrepresentation."""


def _load_judge_cache() -> Dict[str, Any]:
    global _JUDGE_CACHE
    if _JUDGE_CACHE is None:
        try:
            _JUDGE_CACHE = json.loads(JUDGE_CACHE_PATH.read_text()) if JUDGE_CACHE_PATH.exists() else {}
        except Exception:
            _JUDGE_CACHE = {}
    return _JUDGE_CACHE


def _store_judge_cache(listing_id: str, audit: Dict[str, Any]) -> None:
    """Flat map {listing_id: audit} persisted to static/judge_live_results.json (best effort, atomic write)."""
    with _JUDGE_CACHE_LOCK:
        cache = _load_judge_cache()
        cache[listing_id] = audit
        try:
            tmp = JUDGE_CACHE_PATH.with_name(f".{JUDGE_CACHE_PATH.name}.{os.getpid()}.{threading.get_ident()}.tmp")
            tmp.write_text(json.dumps(dict(sorted(cache.items())), indent=1, ensure_ascii=False) + "\n")
            os.replace(tmp, JUDGE_CACHE_PATH)
        except Exception:
            pass


def _normalize_live_audit(audit: Dict[str, Any], images: List[Dict[str, str]]) -> Dict[str, Any]:
    for k in ("overall_judge_score", "exterior_coherence_score", "interior_harmony_score", "room_completeness_score"):
        try:
            audit[k] = round(max(0.0, min(100.0, float(audit.get(k, 0.0)))), 1)
        except Exception:
            audit[k] = 0.0
    issues = []
    for x in audit.get("issues") or []:
        if isinstance(x, dict):
            sev = str(x.get("severity", "medium")).lower()
            issues.append({
                "severity": sev if sev in _JUDGE_SEVERITIES else "medium",
                "title": str(x.get("title", "")).strip(),
                "detail": str(x.get("detail", "")).strip(),
            })
        elif str(x).strip():
            issues.append({"severity": "medium", "title": str(x).strip()[:80], "detail": str(x).strip()})
    audit["issues"] = issues
    audit["room_by_room_checks"] = [
        {"space": str(c.get("space", "")), "status": str(c.get("status", "")), "detail": str(c.get("detail", ""))}
        for c in (audit.get("room_by_room_checks") or []) if isinstance(c, dict)
    ]
    # Deterministic verdict from the judge's own scores/issues so all 108 listings are graded on the same rule.
    overall = audit["overall_judge_score"]
    has_high = any(i["severity"] == "high" for i in issues)
    audit["model_verdict"] = str(audit.get("verdict", ""))
    if overall >= 85.0 and not has_high:
        audit["verdict"] = "PASS"
    elif overall < 60.0:
        audit["verdict"] = "FAIL"
    else:
        audit["verdict"] = "NEEDS REVIEW"
    audit["source"] = "live"
    audit["model"] = _JUDGE_MODEL
    audit["images_reviewed"] = len(images)
    audit["reviewed_images"] = [
        {"img": f"IMG{i + 1}", "room_id": im["room_id"], "label": im["label"], "url": im["url"]}
        for i, im in enumerate(images)
    ]
    audit["photo_provenance"] = _photo_provenance(images)
    return audit


def evaluate_listing_live_with_gemini(listing_id: str, fresh: bool = False, max_attempts: int = 2) -> Dict[str, Any]:
    """Live multimodal Gemini 3.8 Flash judge: shows the model the listing's exterior, interior and floorplan photos
    and asks for an evidence-based coherence audit (no anchored example scores).

    fresh=False returns the cached live result from static/judge_live_results.json instantly when available;
    fresh=True (or a cache miss) runs the model and updates the cache. Falls back to the precomputed catalog
    evaluation (marked source='precomputed') on failure."""
    t0 = time.perf_counter()
    cat = get_catalog()
    target = None
    for it in cat.get("announcements", []):
        if it["id"] == listing_id:
            target = it
            break
    if not target:
        return {"ok": False, "error": f"Listing {listing_id} not found"}

    if not fresh:
        cached = _load_judge_cache().get(listing_id)
        if isinstance(cached, dict) and cached.get("source") == "live":
            out = dict(cached)
            out["cached"] = True
            out["cache_latency_ms"] = int((time.perf_counter() - t0) * 1000)
            return {"ok": True, "audit": out, "cached": True}

    images = _judge_select_images(target)
    prompt = _judge_prompt(target, images)
    config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=_judge_response_schema(),
        media_resolution=getattr(types.MediaResolution, _JUDGE_MEDIA_RESOLUTION),
        thinking_config=types.ThinkingConfig(thinking_level="LOW"),
        max_output_tokens=4096,
    )

    def _contents(use_bytes: bool) -> List[Any]:
        parts: List[Any] = [prompt]
        blobs: Dict[int, bytes] = {}
        if use_bytes:
            from concurrent.futures import ThreadPoolExecutor
            with ThreadPoolExecutor(max_workers=8) as pool:
                futs = {i: pool.submit(_fetch_image_bytes, im["url"]) for i, im in enumerate(images)}
                for i, f in futs.items():
                    try:
                        blobs[i] = f.result(timeout=8.0)
                    except Exception:
                        pass
        for i, im in enumerate(images):
            parts.append(f"IMG{i + 1} = {im['label']} ({im['room_id']}):")
            gs_uri = _https_to_gs(im["url"])
            if not use_bytes and gs_uri:
                parts.append(types.Part.from_uri(file_uri=gs_uri, mime_type="image/jpeg"))
            elif i in blobs:
                parts.append(types.Part.from_bytes(data=blobs[i], mime_type="image/jpeg"))
            else:
                parts.append("(photo unavailable)")
        return parts

    audit: Dict[str, Any] = {}
    errors: List[str] = []
    attempt = 0
    use_bytes = False
    while attempt < max(1, max_attempts) and not audit:
        attempt += 1
        try:
            resp = _get_gl_client().models.generate_content(
                model=_JUDGE_MODEL, contents=_contents(use_bytes), config=config,
            )
            parsed = getattr(resp, "parsed", None)
            audit = dict(parsed) if isinstance(parsed, dict) else json.loads(resp.text)
            if not isinstance(audit, dict) or "overall_judge_score" not in audit:
                raise ValueError("judge returned no scores")
            audit["image_transport"] = "bytes" if use_bytes else "gcs_uri"
        except Exception as e:  # noqa: BLE001
            msg = f"{type(e).__name__}: {str(e)[:180]}"
            errors.append(f"{'bytes' if use_bytes else 'gcs_uri'}#{attempt}: {msg}")
            audit = {}
            low = msg.lower()
            if any(k in low for k in ("429", "resource_exhausted", "quota", "503", "unavailable", "overloaded")):
                time.sleep(min(30.0, 2.0 * (2 ** (attempt - 1))) + (attempt % 3) * 0.7)
            elif not use_bytes:
                use_bytes = True  # e.g. gs:// access problem -> retry with fetched bytes

    if audit:
        audit = _normalize_live_audit(audit, images)
        audit["evaluated_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        audit["latency_ms"] = int((time.perf_counter() - t0) * 1000)
        audit["listing_id"] = listing_id
        _store_judge_cache(listing_id, audit)
        out = dict(audit)
        out["cached"] = False
        return {"ok": True, "audit": out, "cached": False}

    audit = dict(target.get("evaluation", {}) or {})
    audit.setdefault("issues", [])
    audit["source"] = "precomputed"
    audit["model"] = None
    audit["images_reviewed"] = 0
    audit["reviewed_images"] = []
    audit["evaluated_at"] = None
    audit["cached"] = False
    audit["error"] = " | ".join(errors)[:400]
    audit["latency_ms"] = int((time.perf_counter() - t0) * 1000)
    audit["listing_id"] = listing_id
    return {"ok": True, "audit": audit, "cached": False}
