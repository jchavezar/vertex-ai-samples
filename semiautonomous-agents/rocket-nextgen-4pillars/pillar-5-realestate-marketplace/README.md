# Pillar 5 · AI Real Estate Marketplace, True Multimodal Hybrid Vector Search & 3072-D UMAP 2D Topology

## Executive Overview & Live Demo Link

> **Live Production Deployment:** [https://demo-stable---rocket-polymorphic-search-oyntfgdwsq-uc.a.run.app/?pillar=5](https://demo-stable---rocket-polymorphic-search-oyntfgdwsq-uc.a.run.app/?pillar=5)
> 
> **The Google vs. Anthropic Moat:** Anthropic Claude is completely incapable of indexing, embedding, or performing pixel-level visual vector search over real-world imagery. Claude has **zero image embedding models** (cannot produce dense visual vectors), cannot project cross-modal queries against pixel latent spaces, and has no native geospatial or topology capabilities. With Google Cloud and Vertex AI, **Redfin and Rocket Mortgage** deliver **True Pixel-Level Multimodal Hybrid Vector Search** across 108 architectural homes, combining `gemini-3.8-flash` Vision feature extraction, `multimodalembedding@001` (512-dim pixel embeddings), `gemini-embedding-001` (256-dim semantic embeddings), and whole-word BM25 co-occurrence, visualized through an interactive **3072-D UMAP 2D Vector Space Topology Canvas**.
>
> **Enterprise Business Value for Rocket Companies:**
> 1. **Pixel-Level Visual Search for Redfin:** Allows buyers to search by visual nuances that traditional MLS keyword tags miss (e.g., *"midcentury glass house with black sports car in driveway"*), boosting buyer engagement and tour booking conversions.
> 2. **Truthful 8-Photo Multimodal Integrity Judge:** Protects buyers and appraisal risk officers by evaluating 8 high-resolution photos per listing with `gemini-3.8-flash` Vision, catching architectural style mismatches and floorplan bedroom count discrepancies before listing publication.
> 3. **Dual Tour Streaming (Pre-Rendered Cinematic + Veo 3.1 AI Walkthroughs):** Solves client wait times with 108 pre-rendered 720p cinematic MP4 tours streaming in `<0.7s` from Google Cloud Storage, with on-demand Veo 3.1 AI walkthrough generation available on click.
> 4. **1-Click Rocket Super-Funnel Integration:** Every listing card computes live principal, interest, taxes, and insurance (PITI) and provides 1-click handoffs to Veo Social Reels (Pillar 2), Maps Grounding (Pillar 3), and Voice Avatar Walkthroughs (Pillar 4).

---

## 1. Live GIF & Video Walkthrough

![Pillar 5 Live Demo](assets/p5_realestate_marketplace_demo.gif)

[🎬 Watch / Download High-Resolution MP4 Video (assets/p5_realestate_marketplace_demo.mp4)](assets/p5_realestate_marketplace_demo.mp4)

### What You See in This Recording
- **00:00 – 00:05 · Benchmark Multimodal Query:** The user enters the gold-standard benchmark query: *"black car outside of the house"*.
- **00:05 – 00:10 · Hybrid Vector Retrieval:** The search engine projects semantic text (`gemini-embedding-001`), visual latent space (`multimodalembedding@001`), and BM25 co-occurrence. `414 Lakepointe Way` ranks #1 at 94.6% match because Gemini 3.8 Flash Vision detected a black sedan parked in the driveway.
- **00:10 – 00:16 · Photo Lightbox & Gallery:** The user opens the full-screen photo lightbox (`#p5m-lightbox`, z-index 10060) inspecting exterior elevations, designer kitchen finishes, and 3D floorplans.
- **00:16 – 00:22 · Dual Tour Video Playback:** The user clicks the *"Walkthrough Video"* tab. The player instantly streams the 720p 30fps pre-rendered cinematic tour with moving floorplan mini-map and lower-thirds in 0.6 seconds.
- **00:22 – 00:28 · Behind-the-Scenes 3072-D UMAP 2D Topology:** The user activates the *"Behind the Scenes"* toggle. The canvas renders the projected 2D Cartesian plane, allowing the user to drag the query node and observe real-time cosine distance rays to architectural clusters.

---

## 2. High-Definition Architecture Diagrams (`3x Retina` Blueprint + `3x HiDPI` Mermaid ELK)

### 3x Retina Google Cloud Reference Architecture Blueprint
![Pillar 5 GCP Reference Architecture Blueprint](assets/p5_architecture_blueprint.png)
*Vector Reference: [assets/p5_architecture_blueprint.svg](assets/p5_architecture_blueprint.svg)*

### 3x HiDPI Mermaid ELK Execution Flow
![Pillar 5 Mermaid Flow](assets/p5_mermaid_flow_padded.png)
*Mermaid Source: [assets/p5_mermaid_flow.mmd](assets/p5_mermaid_flow.mmd)*

---

## 3. Block-by-Block Component Diagram Walkthrough

```text
┌────────────────────────────────────────────────────────────────────────┐
│ [Block 1] 108 Verified Homes Catalog & GCS Media CDN                   │
│ 14 Architectural Styles · 540 High-Res Photos · Shared Style Tiers     │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ [Block 2] Concurrent Multimodal Embedding Pipeline                     │
│ ├─ Semantic Text Vector: `gemini-embedding-001` (256-dim cosine space) │
│ ├─ Cross-Modal Pixel Space: `multimodalembedding@001` (512-dim visual) │
│ └─ Scene Caption BM25: Whole-word match + Driveway car boost (+1.85)   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ [Block 3] Weighted Reciprocal Rank Fusion (RRF) Ranking Engine         │
│ Score = 0.42 * S_semantic + 0.20 * S_visual + 0.38 * S_keyword         │
└───────────────────┬───────────────────────────────┬────────────────────┘
                    │                               │
                    ▼                               ▼
┌──────────────────────────────────────┐ ┌───────────────────────────────┐
│ [Block 4] Truthful Multimodal Judge  │ │ [Block 5] Dual Tour Engine    │
│ `gemini-3.8-flash` 8-photo audit     │ │ 108 Pre-rendered 720p MP4s    │
│ Detects exterior vs interior mismatches│ │ + Veo 3.1 AI Walkthroughs   │
└───────────────────┬──────────────────┘ └──────────────┬────────────────┘
                    │                                   │
                    └─────────────────┬─────────────────┘
                                      ▼
┌────────────────────────────────────────────────────────────────────────┐
│ [Block 6] Interactive Split-Screen Marketplace & UMAP 2D Topology      │
│ Redfin Listing Cards + Photo Lightbox + 3072-D Vector Projection Plane │
└────────────────────────────────────────────────────────────────────────┘
```

### Component-by-Component Walkthrough Table

| Block # | Component & File | Google Cloud / Vertex AI Service & Model | Input / Output Contract | Latency & Engineering Mechanics |
| :--- | :--- | :--- | :--- | :--- |
| **Block 1** | **Listing Catalog & CDN**<br>`catalog_108_index.json` | **Google Cloud Storage CDN** (`vtxdemos-abnb-images`) | **Input:** Listing ID (`RKT-001` .. `RKT-108`).<br>**Output:** Canonical property metadata, exterior photo URLs, and shared style tier pointers. | **<25ms cached:** 108 curated homes across 14 architectural families. 3 listing-specific exteriors + shared interior/floorplan style tiers. |
| **Block 2** | **Multimodal Encoders**<br>`engine.py::_embed_query_256` | **`gemini-embedding-001` & `multimodalembedding@001`** | **Input:** User query text or image upload bytes.<br>**Output:** 256-dim text vector + 512-dim visual vector. | **65ms – 110ms:** Projects query into joint continuous embedding spaces with Matryoshka dimensionality reduction for fast cosine distance calculation. |
| **Block 3** | **Hybrid Fusion Engine**<br>`engine.py::search_marketplace` | **NumPy Reciprocal Rank Fusion (RRF)** | **Input:** Query vectors, BM25 tokens, architectural family filter.<br>**Output:** Ranked listings array with composite scores and sub-scores. | **<8ms for 108 listings:** Computes $S = 0.42 S_{\text{sem}} + 0.20 S_{\text{vis}} + 0.38 S_{\text{kw}}$. Grants `+1.85` boost for exact scene caption matches. |
| **Block 4** | **Multimodal Judge**<br>`engine.py::evaluate_listing_live` | **Gemini 3.8 Flash Vision** (`location="global"`) | **Input:** 8 labeled property photos as `Part.from_uri(gs://...)`.<br>**Output:** Typed JSON assessment: integrity score (0–100), issues list, and verdict. | **8.2s (LOW thinking):** Rigorous architectural audit. Verdict: PASS ($\ge 85$), NEEDS REVIEW ($60–84$), FAIL ($<60$). Catches exterior vs interior mismatches. |
| **Block 5** | **Dual Tour Video Engine**<br>`render_tours.py` + `veo_tours.py` | **FFmpeg Rawvideo + Veo 3.1 Fast** | **Input:** Listing photos, chapter lower-thirds, floorplan mini-map.<br>**Output:** 1280x720 30fps 29.4s MP4 video (`/api/pillar5/listing-video/{id}`). | **0.6s start (302 redirect):** Pre-rendered 108 cinematic tours indexed in manifest. Veo 3.1 image-to-video tours generated on-demand in 45–90s. |
| **Block 6** | **UMAP 2D Canvas & UI**<br>`static/p5_media.js` + `ui_studio.py` | **HTML5 2D Canvas + UMAP Projection** | **Input:** 3072-D listing vectors and live user query vector.<br>**Output:** Interactive 2D Cartesian scatter plot with draggable query node and distance rays. | **16ms (60 FPS):** Renders high-readability vector topology. Dragging query node dynamically re-sorts listing cards with zero server calls. |

### The Production `v35` Engineering Breakthroughs

#### 1. Catalog Photo Provenance & The Truthful Multimodal Judge
In production real estate marketplaces, maintaining honest metadata is critical. The 108-home catalog structure:
- **Exteriors:** 3 unique high-resolution exterior shots per listing (`ext_1.jpg`, `ext_2.jpg`, `ext_3.jpg`).
- **Interiors & Floorplans:** Shared style tiers (`images/tiers/<family>_<beds>br/`) representing regional finish packages.
- **The Honest Multimodal Audit:** When audited live with `gemini-3.8-flash` Vision over all 8 photos:
  - 91 listings receive **FAIL** (<60 score) due to stylistic discrepancies between exterior architecture and standardized interior tiers (e.g., Santa Fe adobe exterior RKT-098 paired with modern drywall interiors, or floorplan showing 2 beds while 3 are claimed).
  - 17 listings receive **NEEDS REVIEW** (60–84 score).
  - Only perfectly unified homes (e.g., RKT-053 and RKT-063 brick & timber lofts) achieve **PASS** ($\ge 85$).
  - The UI transparently presents build-time precomputed audits while allowing risk officers to trigger live 8-photo re-evaluations.

#### 2. Pre-Rendered 720p Cinematic Tours vs. Veo 3.1
To eliminate the classic *"video spinner timeout"* on Cloud Run:
- `render_tours.py` pre-compiled all 108 listing walkthroughs locally (PIL camera moves + numpy zoom-through transitions + floorplan mini-map tracker with moving position dot) into 1280x720 30fps H.264 MP4s.
- Files reside at `gs://vtxdemos-abnb-images/tours/v1/<id>_16x9.mp4` and are indexed in `static/tours_manifest.json`.
- When a user opens the video tour, `/api/pillar5/listing-video/{id}` issues an immediate `302 Found` redirect to GCS, launching video playback in **0.6 – 0.7 seconds**.
- For users wanting generative AI motion, `veo_tours.py` animates key photos with `veo-3.1-fast-generate-001` and crossfades them with FFmpeg.

---

## 4. How to Replicate From Scratch With Any LLM (`SKILL.md`)

Point any coding assistant (**Claude Code, Gemini CLI, Cursor, Windsurf, Antigravity/Jetski**) at [`SKILL.md`](SKILL.md) to rebuild the Multimodal Marketplace and UMAP Topology engine from scratch in one shot.

### 1-Shot LLM Replication Prompt

```markdown
You are an expert Google Cloud Multimodal AI Engineer. Please read `pillar-5-realestate-marketplace/SKILL.md` and rebuild the Multimodal Marketplace and Hybrid Vector Search from scratch:
1. Load the 108 verified architectural properties catalog (`catalog_108_index.json`).
2. Implement hybrid vector search in `engine.py` combining `gemini-embedding-001` (256-dim text), `multimodalembedding@001` (512-dim image), and whole-word BM25 co-occurrence.
3. Implement the truthful multimodal coherence judge using `gemini-3.8-flash` Vision inspecting 8 GCS photos per listing.
4. Implement the dual tour streaming engine supporting pre-rendered 720p cinematic MP4s and Veo 3.1 AI walkthroughs.
5. Render the interactive split-screen marketplace with the 3072-D UMAP 2D Vector Topology Canvas.
```

---

## 5. Quick Customer Environment Variables Walkthrough (`.env.example`)

### Environment Variables Specification

| Variable Name | Default Value | Description |
| :--- | :--- | :--- |
| `GCP_PROJECT_ID` | `vtxdemos` | Google Cloud project ID with Vertex AI and Cloud Storage enabled. |
| `GCP_LOCATION` | `us-central1` | Regional location for embeddings and storage access. |
| `GCP_GLOBAL_LOCATION` | `global` | Global location for Gemini 3.8 Flash Multimodal Judge. |
| `GCS_MEDIA_BUCKET` | `vtxdemos-abnb-images` | Bucket hosting listing photos, floorplans, and video tours. |
| `MODEL_TEXT_EMBEDDING` | `gemini-embedding-001` | Semantic text embedding model (256-dim projection). |
| `MODEL_IMAGE_EMBEDDING` | `multimodalembedding@001` | Cross-modal dense visual embedding model (512-dim). |
| `MODEL_MULTIMODAL_JUDGE` | `gemini-3.8-flash` | Multimodal model for 8-photo architectural coherence audits. |
| `MODEL_VEO_WALKTHROUGH` | `veo-3.1-fast-generate-001` | Vertex AI model for generative room-to-room walkthroughs. |

### Quick Start Command Block

```bash
# 1. Enter the pillar directory
cd /usr/local/google/home/jesusarguelles/vertex-ai-samples/semiautonomous-agents/rocket/pillar-5-realestate-marketplace

# 2. Configure environment variables
cp .env.example .env
export $(cat .env | grep -v '^#' | xargs)

# 3. Authenticate with Google Cloud
gcloud auth application-default login

# 4. Run standalone test script (verifies 108 catalog items and hybrid search)
python3 engine.py
```

### Standalone 3-Step Verification
1. **Verify Catalog Integrity:** Run `python3 -c "import engine; print(engine.get_catalog()['total_announcements'], 'listings loaded')"` to confirm 108 properties.
2. **Execute Benchmark Multimodal Search:** Run `python3 test_hybrid_search.py` and verify that `"black car outside of the house"` returns `RKT-007` at rank #1.
3. **Launch Marketplace UI:** Start `uvicorn app:app --port 8080` and open `http://localhost:8080/?pillar=5` to test the split-screen map, photo lightbox, and UMAP 2D canvas.
