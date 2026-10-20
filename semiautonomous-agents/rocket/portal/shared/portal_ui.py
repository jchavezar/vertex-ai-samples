# -*- coding: utf-8 -*-
"""Unified Rocket × Google Cloud Single Source of Truth Hub (`rocket-hackathon-portal`).
Features:
1. 4 Interactive Apple iOS 26 / visionOS Liquid Glass + Black Mirror Spatial Editions (V1–V4)
2. Real Photorealistic `gemini-3.8-live` Video Avatar Concierge (`/ws/live-avatar`) + Omniscient Portal Screen Co-Pilot
3. Ryan Holiday "Stillness & Essentialism" 4-Tab Information Architecture:
   - Tab 1: Flagship Live Studios (5-Pillar Studio, GECX Launchpad, Monday Super-Wow Lab, 8 Rocket's Bay Ideas)
   - Tab 2: Build & GitHub (<3 Min Setup, 3x Retina Diagrams, Source Code, PAM/Incognito & Office Hours)
   - Tab 3: Customer AI Glossary, 2026 Model Matrix & Competitor Tool Translator (Synced 1:1 with Google Doc)
   - Tab 4: Reference Library (33 Departmental Consultancy Blueprints Archive)
"""

import html as _html
import json
import re
from typing import Any, Dict, List
from shared.auth_and_vertex import get_recommended_model_for_square
from shared.bespoke_apps import get_bespoke_config
from shared.catalog_data import (
    ALL_DOMAINS,
    PROJECTS_BY_CODE,
    TRANSLATOR_SERVICES,
)
from shared.glossary_launchpad_ui import render_dynamic_glossary_tab_html


def _fmt_text(val: str) -> str:
    """Escapes HTML and converts `backtick` spans into crisp <code class='lg-inline-code'> pills."""
    escaped = _html.escape(str(val or ""))
    return re.sub(
        r"`([^`]+)`",
        r'<code class="lg-inline-code">\1</code>',
        escaped,
    )


# 2026 Futuristic Precision Vector SVG Icon Registry (Apple visionOS / Linear Multi-Layer Geometry)
SVG_ICONS: Dict[str, str] = {
    "rocket": (
        '<svg class="lg-svg-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="1.85" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
        '<path d="M12 2.5L19.5 19.5L12 16L4.5 19.5L12 2.5Z"/>'
        '<path d="M12 2.5V16" opacity="0.45"/>'
        '<path d="M9.5 21.5H14.5" opacity="0.65"/>'
        '</svg>'
    ),
    "studios": (
        '<svg class="lg-svg-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="1.85" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
        '<path d="M12 2.75L20.5 7.5V16.5L12 21.25L3.5 16.5V7.5L12 2.75Z"/>'
        '<path d="M3.5 7.5L12 12.25L20.5 7.5" opacity="0.5"/>'
        '<path d="M12 12.25V21.25" opacity="0.5"/>'
        '</svg>'
    ),
    "terminal": (
        '<svg class="lg-svg-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="1.85" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
        '<rect x="2.75" y="4" width="18.5" height="16" rx="3"/>'
        '<path d="M7 9.5L10.5 12.5L7 15.5"/>'
        '<path d="M12.5 15.5H17" opacity="0.65"/>'
        '</svg>'
    ),
    "compass": (
        '<svg class="lg-svg-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="1.85" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
        '<circle cx="12" cy="12" r="9.25" opacity="0.45"/>'
        '<polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76"/>'
        '<circle cx="12" cy="12" r="1.25" fill="currentColor"/>'
        '</svg>'
    ),
    "library": (
        '<svg class="lg-svg-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="1.85" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
        '<rect x="3" y="3" width="7.5" height="7.5" rx="1.75"/>'
        '<rect x="13.5" y="3" width="7.5" height="7.5" rx="1.75" opacity="0.65"/>'
        '<rect x="3" y="13.5" width="7.5" height="7.5" rx="1.75" opacity="0.65"/>'
        '<rect x="13.5" y="13.5" width="7.5" height="7.5" rx="1.75"/>'
        '</svg>'
    ),
    "layers_theme": (
        '<svg class="lg-svg-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="1.85" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
        '<polygon points="12 2.5 21.5 8.5 12 14.5 2.5 8.5 12 2.5"/>'
        '<polyline points="2.5 13 12 19 21.5 13" opacity="0.65"/>'
        '<polyline points="2.5 17 12 22 21.5 17" opacity="0.4"/>'
        '</svg>'
    ),
    "bolt": (
        '<svg class="lg-svg-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="1.85" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
        '<path d="M13.25 2.5L4.5 13.5H11.5L10.75 21.5L19.5 10.5H12.5L13.25 2.5Z"/>'
        '</svg>'
    ),
    "play": (
        '<svg class="lg-svg-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="1.85" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
        '<polygon points="6.5 4.75 19.25 12 6.5 19.25 6.5 4.75"/>'
        '<path d="M9.5 8.5L15.5 12L9.5 15.5" opacity="0.4"/>'
        '</svg>'
    ),
    "video_reel": (
        '<svg class="lg-svg-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="1.85" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
        '<rect x="2.75" y="4" width="18.5" height="16" rx="3"/>'
        '<path d="M2.75 8.5H21.25" opacity="0.45"/>'
        '<path d="M8 4L10.5 8.5M14 4L16.5 8.5" opacity="0.45"/>'
        '<polygon points="10.25 11.25 15.25 14 10.25 16.75 10.25 11.25"/>'
        '</svg>'
    ),
    "map_pin": (
        '<svg class="lg-svg-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="1.85" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
        '<path d="M12 21C16 16.8 18.5 13.4 18.5 9.75A6.5 6.5 0 1 0 5.5 9.75C5.5 13.4 8 16.8 12 21Z"/>'
        '<circle cx="12" cy="9.75" r="2.25"/>'
        '<ellipse cx="12" cy="21" rx="5.5" ry="1.5" opacity="0.4"/>'
        '</svg>'
    ),
    "home_vector": (
        '<svg class="lg-svg-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="1.85" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
        '<path d="M3 10.5L12 3L21 10.5"/>'
        '<path d="M5.25 9.25V19.5A1.5 1.5 0 0 0 6.75 21H17.25A1.5 1.5 0 0 0 18.75 19.5V9.25"/>'
        '<path d="M9.5 21V14.25H14.5V21" opacity="0.55"/>'
        '<circle cx="12" cy="7.5" r="1" fill="currentColor"/>'
        '</svg>'
    ),
    "waveform": (
        '<svg class="lg-svg-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="1.95" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
        '<path d="M4 10V14" opacity="0.55"/>'
        '<path d="M8 7V17"/>'
        '<path d="M12 3.5V20.5"/>'
        '<path d="M16 7V17"/>'
        '<path d="M20 10V14" opacity="0.55"/>'
        '</svg>'
    ),
    "stop_square": (
        '<svg class="lg-svg-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="1.85" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
        '<circle cx="12" cy="12" r="9.25" opacity="0.45"/>'
        '<rect x="8.75" y="8.75" width="6.5" height="6.5" rx="1.25"/>'
        '</svg>'
    ),
    "doc_blueprint": (
        '<svg class="lg-svg-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="1.85" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
        '<path d="M14.5 2.75H6.5A2 2 0 0 0 4.5 4.75V19.25A2 2 0 0 0 6.5 21.25H17.5A2 2 0 0 0 19.5 19.25V7.75L14.5 2.75Z"/>'
        '<polyline points="14 2.75 14 8 19.5 8" opacity="0.55"/>'
        '<line x1="8" y1="12.5" x2="16" y2="12.5" opacity="0.65"/>'
        '<line x1="8" y1="16.5" x2="13.5" y2="16.5" opacity="0.65"/>'
        '</svg>'
    ),
    "github_code": (
        '<svg class="lg-svg-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="1.85" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
        '<circle cx="6" cy="6" r="2.25"/>'
        '<circle cx="18" cy="8" r="2.25"/>'
        '<circle cx="6" cy="18" r="2.25"/>'
        '<path d="M6 8.25V15.75"/>'
        '<path d="M18 10.25C18 14 14.5 14.5 6 14.5" opacity="0.65"/>'
        '</svg>'
    ),
    "shield_lock": (
        '<svg class="lg-svg-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="1.85" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
        '<path d="M12 2.75L19.5 5.75V11.5C19.5 16.5 16.25 19.85 12 21.25C7.75 19.85 4.5 16.5 4.5 11.5V5.75L12 2.75Z"/>'
        '<circle cx="12" cy="11" r="1.5"/>'
        '<path d="M12 12.5V15.5" opacity="0.65"/>'
        '</svg>'
    ),
    "external_link": (
        '<svg class="lg-svg-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="1.85" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
        '<path d="M7 17L17 7"/>'
        '<polyline points="8.5 7 17 7 17 15.5"/>'
        '<path d="M19 13.5V18.5A1.5 1.5 0 0 1 17.5 20H5.5A1.5 1.5 0 0 1 4 18.5V6.5A1.5 1.5 0 0 1 5.5 5H10.5" opacity="0.42"/>'
        '</svg>'
    ),
    "search": (
        '<svg class="lg-svg-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="1.85" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
        '<circle cx="11" cy="11" r="7.25"/>'
        '<path d="M16.5 16.5L21 21"/>'
        '<path d="M8.5 9A3 3 0 0 1 13 7.75" opacity="0.45"/>'
        '</svg>'
    ),
    "close": (
        '<svg class="lg-svg-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="1.95" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
        '<line x1="18" y1="6" x2="6" y2="18"/>'
        '<line x1="6" y1="6" x2="18" y2="18"/>'
        '</svg>'
    ),
    "sparkle_ai": (
        '<svg class="lg-svg-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="1.85" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
        '<path d="M12 2.5L14.4 9.6L21.5 12L14.4 14.4L12 21.5L9.6 14.4L2.5 12L9.6 9.6L12 2.5Z"/>'
        '<circle cx="19" cy="5" r="1" fill="currentColor" opacity="0.6"/>'
        '<circle cx="5" cy="19" r="1" fill="currentColor" opacity="0.6"/>'
        '</svg>'
    ),
    "chevron_down": (
        '<svg class="lg-svg-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="1.95" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
        '<polyline points="6 9 12 15 18 9"/>'
        '</svg>'
    ),
    "arrow_left": (
        '<svg class="lg-svg-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="1.85" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
        '<line x1="19" y1="12" x2="5" y2="12"/>'
        '<polyline points="12 19 5 12 12 5"/>'
        '</svg>'
    ),
}


def _svg(name: str, size: int = 18) -> str:
    """Returns a sized inline geometric vector SVG by key."""
    raw = SVG_ICONS.get(name, SVG_ICONS["sparkle_ai"])
    return raw.replace(
        'class="lg-svg-icon"',
        f'class="lg-svg-icon" width="{size}" height="{size}" style="width:{size}px;height:{size}px;"',
        1,
    )

NEXTGEN_TOKEN = "rocket:e3a48aa96ebeb0731e4c751d"
FIVE_PILLAR_PROD_URL = f"https://rocket-polymorphic-search-254356041555.us-central1.run.app/?auth_token={NEXTGEN_TOKEN}"
FIVE_PILLAR_STABLE_URL = f"https://demo-stable---rocket-polymorphic-search-oyntfgdwsq-uc.a.run.app/?auth_token={NEXTGEN_TOKEN}"
SUPERWOW_URL = f"https://rocket-monday-superwow-254356041555.us-central1.run.app/?auth_token={NEXTGEN_TOKEN}"
GECX_LAUNCHPAD_URL = "https://rocket-cxas-launchpad-721536271629.us-central1.run.app/"
GECX_CONSOLE_URL = "https://ces.cloud.google.com/"
GITHUB_ROOT_URL = "https://github.com/jchavezar/vertex-ai-samples/tree/main/semiautonomous-agents/rocket"
GLOSSARY_DOC_URL = "https://docs.google.com/document/d/1UwZpS8gmEwY07329NjUakSmNZSHL-WEwhI2ivG8a7dk/edit?tab=t.0"
USECASES_DOC_URL = "https://docs.google.com/document/d/1wAPDWLX0U10x1HbN8Sir8baFkzP-Bxw81UaXUDLQwto/edit?resourcekey=0-1iV8FyWU2l-EmKEAOs7Prw"
EXEC_GUIDE_DOC_URL = "https://docs.google.com/document/d/1oEZ1Pncs1wFHw9S-KoENYSr6Gqh0245sx5BfR3JX4is/edit?resourcekey=0-wEfX0W36FKtdnA_0YJTKqg"


FLAGSHIP_PILLARS: List[Dict[str, Any]] = [
    {
        "num": 1,
        "id": "pillar-1",
        "badge": "DEMO #1 · PILLAR 1 · TREASURY & SERVICING",
        "title": "BigQuery ML TimesFM 2.0 Zero-Shot Forecasting",
        "subtitle": "Forecast Mr. Cooper $2.1T servicing refi waves, Redfin tour demand & warehouse liquidity under Fed rate shocks in one SQL query.",
        "icon": "bolt",
        "tint": "cobalt",
        "gif": "/static/nextgen/p1_bqml_timesfm_demo.gif",
        "arch_svg": "/static/nextgen/p1_architecture_blueprint.svg",
        "walk_svg": "/static/nextgen/p1_component_walkthrough.svg",
        "live_url": f"{FIVE_PILLAR_PROD_URL}&pillar=1",
        "github_url": f"{GITHUB_ROOT_URL}/pillar-1-bqml-timesfm",
        "models": ["BigQuery AI.FORECAST (TimesFM 2.0)", "gemini-3.8-flash", "gemini-3.8-live (24kHz TTS)"],
        "metrics": "-150 to +100 bps Rate Shock Simulator · Confidence Fan Chart · Live BigQuery SQL",
    },
    {
        "num": 2,
        "id": "pillar-2",
        "badge": "DEMO #2 · PILLAR 2 · GENERATIVE VIDEO STUDIO",
        "title": "Vertex AI Veo 3.1 + Nano Banana 2 Reels Studio",
        "subtitle": "Turn any custom architectural prompt or Redfin listing into a 9:16 social Reel with live PITI overlays and 24kHz HD voiceover.",
        "icon": "video_reel",
        "tint": "purple",
        "gif": "/static/nextgen/p2_veo_reels_demo.gif",
        "arch_svg": "/static/nextgen/p2_architecture_blueprint.svg",
        "walk_svg": "/static/nextgen/p2_component_walkthrough.svg",
        "live_url": f"{FIVE_PILLAR_PROD_URL}&pillar=2",
        "github_url": f"{GITHUB_ROOT_URL}/pillar-2-veo-reels-studio",
        "models": ["veo-3.1-fast-generate-001", "gemini-3.1-flash-image", "gemini-3.8-flash", "gemini-3.8-live"],
        "metrics": "~10s Custom Keyframe Reel · ~55s Full Veo 3.1 MP4 · 8 Instant Vault Reels",
    },
    {
        "num": 3,
        "id": "pillar-3",
        "badge": "DEMO #3 · PILLAR 3 · ASK REDFIN 2.0 CHAT",
        "title": "Tri-Modal Grounded Chat (Maps + YouTube + Search)",
        "subtitle": "Streaming multi-turn chat grounded simultaneously in Google Maps Places, YouTube video walkthroughs, and live Google Search.",
        "icon": "map_pin",
        "tint": "emerald",
        "gif": "/static/nextgen/p3_trimodal_grounding_demo.gif",
        "arch_svg": "/static/nextgen/p3_architecture_blueprint.svg",
        "walk_svg": "/static/nextgen/p3_component_walkthrough.svg",
        "live_url": f"{FIVE_PILLAR_PROD_URL}&pillar=3",
        "github_url": f"{GITHUB_ROOT_URL}/pillar-3-trimodal-grounding",
        "models": ["gemini-3.8-flash", "Google Maps Grounding", "YouTube Part.from_uri", "Google Search Grounding"],
        "metrics": "<3.5s First Token NDJSON Stream · Live Leaflet Place Pins · MSHDA Grant Verification",
    },
    {
        "num": 4,
        "id": "pillar-4",
        "badge": "DEMO #4 · PILLAR 4 · LIVE VIDEO CONCIERGE",
        "title": "Gemini 3.8 Live Official Video Avatar Stage",
        "subtitle": "Face-to-face 24fps H.264 video avatar conversation (`AvatarConfig`) with server VAD, <200ms native barge-in, and zero screen clutter.",
        "icon": "waveform",
        "tint": "amber",
        "gif": "/static/nextgen/p4_live_avatar_demo.gif",
        "arch_svg": "/static/nextgen/p4_architecture_blueprint.svg",
        "walk_svg": "/static/nextgen/p4_component_walkthrough.svg",
        "live_url": f"{FIVE_PILLAR_PROD_URL}&pillar=4",
        "github_url": f"{GITHUB_ROOT_URL}/pillar-4-live-api-avatar",
        "models": ["gemini-3.8-live (BidiGenerateContent)", "AvatarConfig (704×1280 H.264)", "Server VAD Barge-In"],
        "metrics": "5 Official 24fps Video Avatars (Kira, Sam, Ben, Vera, Leo) · 24kHz Native Audio & Barge-In",
    },
    {
        "num": 5,
        "id": "pillar-5",
        "badge": "DEMO #5 · PILLAR 5 · HYBRID VECTOR MARKETPLACE",
        "title": "Redfin × Rocket Homes Hybrid Vector Marketplace",
        "subtitle": "BigQuery `VECTOR_SEARCH` (`COSINE` + RRF) across 108 homes, 3D floorplans, Veo 3.1 tours & honest multimodal Gemini Judge.",
        "icon": "home_vector",
        "tint": "crimson",
        "gif": "/static/nextgen/p5_realestate_marketplace_demo.gif",
        "arch_svg": "/static/nextgen/p5_architecture_blueprint.svg",
        "walk_svg": "/static/nextgen/p5_component_walkthrough.svg",
        "live_url": f"{FIVE_PILLAR_PROD_URL}&pillar=5",
        "github_url": f"{GITHUB_ROOT_URL}/pillar-5-realestate-marketplace",
        "models": ["gemini-embedding-001 (3072-D)", "multimodalembedding@001 (1408-D)", "gemini-3.8-flash", "veo-3.1-fast-generate-001"],
        "metrics": "108 Curated Homes · 0.6s Veo/Cinematic MP4 Stream · Interactive Vector Topology Canvas",
    },
]

BAY_8_USE_CASES: List[Dict[str, str]] = [
    {
        "num": "01",
        "title": "Summon the Borrower (User Research Persona Agent)",
        "icon": "waveform",
        "stack": "Gemini 3.8 Live + Condens UX RAG",
        "desc": "Interview synthetic first-time, VA, and jumbo borrowers grounded in Condens UX transcripts in English, Spanish, Tamil, and Hindi.",
        "url": f"{SUPERWOW_URL}&opt=2",
        "cta": "Launch in Super-Wow Opt #2 ↗",
    },
    {
        "num": "02",
        "title": "Physical Security Visitor Pass & Escort Orchestrator",
        "icon": "shield_lock",
        "stack": "Gemini Enterprise + ADK + Cloud Run",
        "desc": "Conversational physical security check-in, host validation, and digital badge provisioning for Detroit & Phoenix campuses.",
        "url": "/square/1.5",
        "cta": "Open Sandbox Blueprint ↗",
    },
    {
        "num": "03",
        "title": "Rocket Pro Broker Command Deck & Rate-Lock Copilot",
        "icon": "bolt",
        "stack": "Gemini 4 Argon + Parallel Function Calling",
        "desc": "Sub-second wholesale broker pricing comparison across Par, Permanent Buydown, and Seller 2-1 Temporary Buydown scenarios.",
        "url": "/square/1.2",
        "cta": "Open Broker Deck [1.2] ↗",
    },
    {
        "num": "04",
        "title": "Rocket Agent Passport (Cryptographic Identity & Guardrails)",
        "icon": "shield_lock",
        "stack": "Cloud KMS JWT + Spanner Policy Wall + Model Armor",
        "desc": "Every autonomous agent carries a KMS-signed passport; rogue wires are blocked in 0ms by Spanner Policy Wall with Titan M3 biometric approval.",
        "url": f"{SUPERWOW_URL}&opt=3",
        "cta": "Launch in Super-Wow Opt #3 ↗",
    },
    {
        "num": "05",
        "title": "Meaning of Home Creative Arena (Multimodal Reels & Staging)",
        "icon": "video_reel",
        "stack": "Veo 3.1 + Gemini 3.1 Flash Image + SynthID",
        "desc": "Generate emotionally resonant 9:16 homeownership stories and virtually staged rooms with compliant TILA Reg Z overlays.",
        "url": f"{FIVE_PILLAR_PROD_URL}&pillar=2",
        "cta": "Launch Pillar 2 Studio ↗",
    },
    {
        "num": "06",
        "title": "Chart a Course (BigQuery TimesFM 2.0 Treasury & Refi Forecast)",
        "icon": "compass",
        "stack": "BigQuery ML AI.FORECAST (TimesFM 2.0)",
        "desc": "Zero-shot forecasting of Mr. Cooper recapture waves, escrow disbursements, and staffing capacity across interest-rate scenarios.",
        "url": f"{FIVE_PILLAR_PROD_URL}&pillar=1",
        "cta": "Launch Pillar 1 Studio ↗",
    },
    {
        "num": "07",
        "title": "Team Brain Constellation (Cross-Funnel Swarm Race)",
        "icon": "studios",
        "stack": "Antigravity Parallel Subagents + MCP",
        "desc": "5 concurrent subagents fan out across Redfin, Rocket Money, Fannie Mae, TRID, and Treasury in 1.58s (4.0x faster than serial chains).",
        "url": f"{SUPERWOW_URL}&opt=4",
        "cta": "Launch in Super-Wow Opt #4 ↗",
    },
    {
        "num": "08",
        "title": "Not Hotdog Property Vision & Honest Appraisal Judge",
        "icon": "home_vector",
        "stack": "Gemini 3.8 Flash Multimodal + 1408-D Image Vectors",
        "desc": "Upload any home photo to match architectural twins across 108 listings and run an 8-photo multimodal appraisal coherence audit.",
        "url": f"{FIVE_PILLAR_PROD_URL}&pillar=5",
        "cta": "Launch Pillar 5 Vision ↗",
    },
]

MODEL_PORTFOLIO_2026: List[Dict[str, str]] = [
    {
        "family": "Gemini 4.0 Argon & 3.1 Pro",
        "id": "gemini-4-argon / gemini-3.1-pro-preview",
        "tier": "Frontier Deep Reasoning & Coding",
        "best_for": "Complex Fannie Mae Form 1084 tax analysis, AST legal redlining, multi-step architecture, and C#/.NET modernization.",
        "pillar": "Super-Wow #1 & Underwriting [2.1]",
    },
    {
        "family": "Gemini 3.8 Flash (Default Workhorse)",
        "id": "gemini-3.8-flash (location='global')",
        "tier": "High-Speed Multimodal & Grounding",
        "best_for": "Sub-second agentic routing, Tri-Modal Maps/YouTube/Search chat, 8-photo appraisal judge, and parallel subagent swarms.",
        "pillar": "Pillars 1, 2, 3, 5 & Portal Co-Pilot",
    },
    {
        "family": "Gemini 3.1 Flash-Lite",
        "id": "gemini-3.1-flash-lite",
        "tier": "Ultra-Fast / Low-Cost Classification",
        "best_for": "High-throughput intent routing, guardrails triage, and lightweight schema extraction at minimal cost.",
        "pillar": "Subagent Fan-Out Router",
    },
    {
        "family": "Gemini 3.8 Live API + Video Avatar",
        "id": "gemini-3.8-live (location='us-central1')",
        "tier": "Bidirectional 24kHz Voice & 24fps Video Avatar",
        "best_for": "Real-time voice & video concierge (`AvatarConfig`), server VAD <200ms barge-in, and live screen function calling.",
        "pillar": "Pillar 4 & Portal Live Concierge",
    },
    {
        "family": "Veo 3.1 & Veo 3.1 Fast",
        "id": "veo-3.1-generate-001 / veo-3.1-fast-generate-001",
        "tier": "Cinematic 9:16 & 16:9 Video + Audio",
        "best_for": "Text-to-video social Reels and image-to-video room-by-room steadicam property walkthroughs.",
        "pillar": "Pillar 2 Reels & Pillar 5 Tours",
    },
    {
        "family": "Nano Banana 2 & Imagen 4 Ultra",
        "id": "gemini-3.1-flash-image / imagen-4.0-ultra-generate-001",
        "tier": "Photorealistic Image Generation & Editing",
        "best_for": "10-second custom architectural keyframes, virtual room staging, and compliant mortgage ad typography.",
        "pillar": "Pillar 2 Keyframes & Marketing [4.2]",
    },
    {
        "family": "Text & Multimodal Vector Embeddings",
        "id": "gemini-embedding-001 (3072-D) / multimodalembedding@001 (1408-D)",
        "tier": "Hybrid Semantic + Visual Vector Search",
        "best_for": "BigQuery `VECTOR_SEARCH` (`COSINE` + Reciprocal Rank Fusion) matching natural language and photos across listings.",
        "pillar": "Pillar 5 Hybrid Marketplace",
    },
    {
        "family": "BigQuery ML TimesFM 2.0 / 2.5",
        "id": "AI.FORECAST (TimesFM 2.0)",
        "tier": "Zero-Shot Time-Series Foundation Model",
        "best_for": "Forecasting Mr. Cooper refi lock volume, Redfin tour demand, and escrow outflows directly in SQL without training.",
        "pillar": "Pillar 1 Treasury Forecast",
    },
]

LIFECYCLE_TERMS: List[Dict[str, str]] = [
    {
        "term": "Configurable AI (No-Code Assistants)",
        "tag": "L100 · Everyday Productivity",
        "def": "Pre-built Google AI workspaces configured with instructions and uploaded files in minutes—no code or infrastructure required.",
        "tools": "Gemini Gems, NotebookLM Enterprise, Gemini Enterprise (Sobi / Spark `/work`)",
    },
    {
        "term": "Task-Based Agentic AI (Custom Systems)",
        "tag": "L200–L300 · Production Engineering",
        "def": "Goal-driven AI systems built with SDKs, APIs, state machines, and tool calling that execute multi-step workflows across Rocket APIs.",
        "tools": "Vertex AI, Agent Development Kit (ADK), GECX / CX Agent Studio, Google Antigravity, Cloud Run",
    },
    {
        "term": "Tri-Modal Grounding & Enterprise RAG",
        "tag": "Zero Hallucination",
        "def": "Anchoring model outputs in verifiable truth across Google Maps (places/pins), YouTube video streams, Google Search, and SharePoint/BigQuery.",
        "tools": "Vertex AI Grounding, BigQuery `VECTOR_SEARCH`, Discovery Engine `streamAssist`",
    },
    {
        "term": "Function Calling, MCP & A2A",
        "tag": "Interoperability",
        "def": "Structured protocols allowing Gemini to invoke external APIs (`Function Calling`), connect to standardized data servers (`MCP`), and delegate across agents (`A2A`).",
        "tools": "Model Context Protocol (MCP), Agent-to-Agent (A2A), Cloud KMS Agent Passports",
    },
    {
        "term": "Skills (`SKILL.md`) & Parallel Subagents",
        "tag": "Agentic Velocity",
        "def": "Reusable instruction/code packages (`SKILL.md`) and concurrent worker fan-out (`asyncio.gather` / `run_workflow`) that cut latency by 4.0x.",
        "tools": "Google Antigravity 2.0, Vertex AI `gemini-3.8-flash` Subagent Router",
    },
    {
        "term": "GECX & Autonomous Hill-Climbing (`cxas-scrappy`)",
        "tag": "Contact Center AI",
        "def": "Omnichannel customer experience studio where `cxas-scrappy` compiles a PRD into a live voice/chat agent and hill-climbs against simulated callers.",
        "tools": "Gemini Enterprise for CX (`ces.cloud.google.com`), Dialogflow CX, CCAI Agent Assist",
    },
]


def render_portal_html(auth_token: str) -> str:
    """Renders the Apple Liquid Glass + Black Mirror Spatial Unified Portal (4 Live Versions + Real Video Avatar)."""

    # Build Flagship 5-Pillar Cards HTML (Streamlined 2-Action Layout + Unified Architecture & 5-Block Flow Lightbox)
    pillar_cards_html = []
    for p in FLAGSHIP_PILLARS:
        models_chips = "".join(
            f'<span class="lg-chip lg-chip-mono">{_html.escape(m)}</span>' for m in p["models"]
        )
        pillar_cards_html.append(f"""
        <article id="{p['id']}" class="liquid-card liquid-3d-tilt pillar-showcase-card">
          <div class="pillar-card-top-bar">
            <span class="lg-badge lg-badge-{p['tint']}">{_html.escape(p['badge'])}</span>
            <button type="button" class="lg-diagram-btn" onclick="openDiagramLightbox('{p['arch_svg']}', '{_html.escape(p['title'])}', '{p['walk_svg']}', '{p['github_url']}', 'arch')" title="Inspect 3x GCP Architecture & 5-Block Flow">
              {_svg("studios", 15)}
              <span>Architecture &amp; Flow</span>
            </button>
          </div>
          <div class="pillar-media-wrap">
            <img src="{p['gif']}" alt="{_html.escape(p['title'])}" loading="lazy" class="pillar-gif-preview"
                 onclick="openDiagramLightbox('{p['arch_svg']}', '{_html.escape(p['title'])}', '{p['walk_svg']}', '{p['github_url']}', 'arch')">
          </div>
          <div class="pillar-body">
            <div class="pillar-title-row">
              <div class="squircle-3d-icon tint-{p['tint']}">
                {_svg(p['icon'], 22)}
              </div>
              <div>
                <h3 class="pillar-title">{_fmt_text(p['title'])}</h3>
                <div class="pillar-metrics-line mono">{_html.escape(p['metrics'])}</div>
              </div>
            </div>
            <p class="pillar-desc">{_fmt_text(p['subtitle'])}</p>
            <div class="pillar-models-row">{models_chips}</div>
            <div class="pillar-actions-row">
              <a href="{p['live_url']}" target="_blank" class="lg-btn lg-btn-primary">
                {_svg("play", 16)}
                Launch Live Studio
              </a>
              <a href="{p['github_url']}" target="_blank" class="lg-btn lg-btn-glass">
                {_svg("github_code", 16)}
                GitHub &amp; SKILL.md
              </a>
            </div>
          </div>
        </article>
        """)

    # Build Compact 8 Rocket's Bay Hackathon Track Mapper Strip HTML
    bay_cards_html = []
    for idea in BAY_8_USE_CASES:
        href = idea["url"]
        if href.startswith("/"):
            href = f"{href}?auth_token={auth_token}"
        bay_cards_html.append(f"""
        <a href="{href}" target="_blank" class="liquid-card bay-track-pill" title="{_html.escape(idea['desc'])}">
          <div class="squircle-3d-icon tint-cobalt sm" style="width:34px;height:34px;border-radius:10px;">
            {_svg(idea['icon'], 17)}
          </div>
          <div style="flex:1;min-width:0;">
            <div class="bay-track-hdr">
              <span class="mono bay-num-pill">TRACK #{idea['num']}</span>
              <span class="mono bay-stack" style="font-size:10px;">{_html.escape(idea['stack'])}</span>
            </div>
            <div class="bay-track-title">{_fmt_text(idea['title'])}</div>
          </div>
          <span style="color:var(--accent-primary);flex-shrink:0;display:inline-flex;">{_svg("external_link", 16)}</span>
        </a>
        """)

    # Build 2026 Model Portfolio Rows HTML
    model_rows_html = []
    for m in MODEL_PORTFOLIO_2026:
        model_rows_html.append(f"""
        <tr class="glossary-filter-item" data-tags="all model">
          <td>
            <div class="tbl-strong">{_fmt_text(m['family'])}</div>
            <div class="mono tbl-code">{_html.escape(m['id'])}</div>
          </td>
          <td><span class="lg-chip">{_html.escape(m['tier'])}</span></td>
          <td class="tbl-desc">{_fmt_text(m['best_for'])}</td>
          <td class="mono tbl-meta">{_html.escape(m['pillar'])}</td>
        </tr>
        """)

    # Build Lifecycle Terms Cards HTML
    lifecycle_cards_html = []
    for t in LIFECYCLE_TERMS:
        lifecycle_cards_html.append(f"""
        <div class="liquid-card glossary-term-card glossary-filter-item" data-tags="all lifecycle">
          <div class="term-hdr">
            <span class="lg-badge lg-badge-cobalt">{_html.escape(t['tag'])}</span>
          </div>
          <h4 class="term-title">{_fmt_text(t['term'])}</h4>
          <p class="term-desc">{_fmt_text(t['def'])}</p>
          <div class="term-tools mono"><strong>Google Stack:</strong> {_fmt_text(t['tools'])}</div>
        </div>
        """)

    # Build Competitor Tool Translator Rows HTML
    translator_rows_html = []
    for tr in TRANSLATOR_SERVICES:
        tags_str = "all " + " ".join(tr.get("tags", []))
        translator_rows_html.append(f"""
        <tr class="glossary-filter-item" data-tags="{_html.escape(tags_str)}">
          <td>
            <a href="{tr['url']}" target="_blank" class="tbl-link">{_fmt_text(tr['service'])} ↗</a>
            <div class="tbl-sub">{_fmt_text(tr['oneLiner'])}</div>
          </td>
          <td class="tbl-desc">{_fmt_text(tr['claude'])}</td>
          <td class="tbl-desc">{_fmt_text(tr['sierra'])}</td>
          <td class="tbl-desc">{_fmt_text(tr['chatgpt'])}</td>
        </tr>
        """)

    # Build 33 Consultancy Archive Cards HTML (each with its own separated GitHub repo!)
    archive_cards_html = []
    for d in ALL_DOMAINS:
        for p in d["projects"]:
            code = p["code"]
            ded_repo_url = p.get("github_repo_url", GITHUB_ROOT_URL)
            ded_repo_rel = p.get("github_repo_rel", "")
            archive_cards_html.append(f"""
            <div class="liquid-card archive-blueprint-card" data-dept="{_html.escape(d['id'])}">
              <div class="archive-card-hdr">
                <span class="lg-badge lg-badge-crimson mono">SQUARE {code}</span>
                <span class="lg-chip mono">{_html.escape(p['level'])}</span>
                <span class="archive-dept-lbl mono">{_html.escape(d['shortTitle'])}</span>
              </div>
              <h4 class="archive-title">{_fmt_text(p['project'])}</h4>
              <p class="archive-desc">{_fmt_text(p['desc'])}</p>
              <div class="archive-stack mono">{_html.escape(p['tool'])}</div>
              <div class="mono" style="font-size:10.5px;color:var(--text-muted);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;display:flex;align-items:center;gap:5px;" title="rocket-ai-hackathon-argon-suite/{_html.escape(ded_repo_rel)}">
                {_svg("github_code", 13)} <span>Repo:</span> <a href="{_html.escape(ded_repo_url)}" target="_blank" style="color:var(--accent-secondary);text-decoration:none;font-weight:700;">rocket-ai-hackathon-argon-suite/{_html.escape(ded_repo_rel.split('/')[-1] if ded_repo_rel else code)} ↗</a>
              </div>
              <div class="archive-actions">
                <a href="/square/{code}?auth_token={auth_token}" class="lg-btn lg-btn-primary sm">
                  {_svg("play", 14)}
                  Interactive Sandbox
                </a>
                <a href="/docs/{code}?auth_token={auth_token}" class="lg-btn lg-btn-glass sm">
                  {_svg("doc_blueprint", 14)}
                  Blueprint &amp; Guide
                </a>
                <a href="{_html.escape(ded_repo_url)}" target="_blank" class="lg-btn lg-btn-glass sm" title="Open Dedicated Standalone GitHub Repo for Square {code}">
                  {_svg("github_code", 14)}
                  Repo [{code}]
                </a>
              </div>
            </div>
            """)

    return f"""<!DOCTYPE html>
<html lang="en" data-liquid-version="v1">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
  <title>Rocket × Google Cloud | Single Source of Truth Spatial AI Hub</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=JetBrains+Mono:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/static/glossary_launchpad.css">
  <style>
    /* ==========================================================================
       4-VERSION APPLE iOS 26 / visionOS LIQUID GLASS + BLACK MIRROR ENGINE
       ========================================================================== */
    :root,
    html[data-liquid-version="v1"] {{
      /* V1: Apple iOS 26 / visionOS Cupertino Daylight Prism (Default) */
      --bg-canvas: #EEF2F9;
      --bg-mesh:
        radial-gradient(at 12% 8%, rgba(216, 30, 40, 0.11) 0px, transparent 48%),
        radial-gradient(at 88% 12%, rgba(0, 102, 204, 0.13) 0px, transparent 52%),
        radial-gradient(at 50% 90%, rgba(16, 185, 129, 0.08) 0px, transparent 55%),
        linear-gradient(180deg, #F6F8FC 0%, #E9EEF8 100%);
      --glass-surface: rgba(255, 255, 255, 0.68);
      --glass-surface-strong: rgba(255, 255, 255, 0.86);
      --glass-surface-subtle: rgba(255, 255, 255, 0.48);
      --glass-border: rgba(255, 255, 255, 0.85);
      --glass-outer-stroke: rgba(15, 23, 42, 0.08);
      --glass-specular-top: inset 0 1.5px 0 rgba(255, 255, 255, 0.98), inset 0 -1px 0 rgba(255, 255, 255, 0.45);
      --glass-shadow: 0 22px 48px -14px rgba(15, 23, 42, 0.09), 0 4px 14px rgba(15, 23, 42, 0.04);
      --glass-blur: blur(28px) saturate(190%);
      --text-primary: #0B1120;
      --text-secondary: #334155;
      --text-muted: #64748B;
      --accent-primary: #D81E28;
      --accent-secondary: #0066CC;
      --accent-glow: rgba(216, 30, 40, 0.22);
      --card-radius: 26px;
      --pill-radius: 999px;
      --heading-font: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }}

    html[data-liquid-version="v2"] {{
      /* V2: Black Mirror Holographic Obsidian Neural Glass */
      --bg-canvas: #04060E;
      --bg-mesh:
        radial-gradient(at 15% 10%, rgba(225, 29, 72, 0.24) 0px, transparent 48%),
        radial-gradient(at 85% 16%, rgba(6, 182, 212, 0.22) 0px, transparent 50%),
        radial-gradient(at 50% 85%, rgba(99, 102, 241, 0.18) 0px, transparent 55%),
        linear-gradient(180deg, #03050B 0%, #090D1A 100%);
      --glass-surface: rgba(13, 19, 34, 0.62);
      --glass-surface-strong: rgba(17, 24, 42, 0.88);
      --glass-surface-subtle: rgba(255, 255, 255, 0.05);
      --glass-border: rgba(255, 255, 255, 0.18);
      --glass-outer-stroke: rgba(6, 182, 212, 0.22);
      --glass-specular-top: inset 0 1.5px 0 rgba(255, 255, 255, 0.28), inset 0 -1px 0 rgba(6, 182, 212, 0.18);
      --glass-shadow: 0 28px 60px -12px rgba(0, 0, 0, 0.72), 0 0 28px rgba(6, 182, 212, 0.08);
      --glass-blur: blur(28px) saturate(200%);
      --text-primary: #F8FAFC;
      --text-secondary: #CBD5E1;
      --text-muted: #94A3B8;
      --accent-primary: #FF2E4C;
      --accent-secondary: #00F0FF;
      --accent-glow: rgba(0, 240, 255, 0.28);
      --card-radius: 24px;
      --pill-radius: 999px;
      --heading-font: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }}

    html[data-liquid-version="v3"] {{
      /* V3: Apple Vision Pro Grade-5 Spatial Titanium 3D Studio */
      --bg-canvas: #12141C;
      --bg-mesh:
        radial-gradient(at 20% 5%, rgba(251, 191, 36, 0.14) 0px, transparent 45%),
        radial-gradient(at 82% 18%, rgba(216, 30, 40, 0.18) 0px, transparent 50%),
        radial-gradient(at 50% 95%, rgba(56, 189, 248, 0.12) 0px, transparent 55%),
        linear-gradient(160deg, #161923 0%, #0D0F16 100%);
      --glass-surface: rgba(34, 38, 50, 0.56);
      --glass-surface-strong: rgba(42, 47, 62, 0.86);
      --glass-surface-subtle: rgba(255, 248, 235, 0.07);
      --glass-border: rgba(255, 244, 228, 0.26);
      --glass-outer-stroke: rgba(255, 255, 255, 0.12);
      --glass-specular-top: inset 0 2px 1px rgba(255, 248, 238, 0.38), inset 0 -1px 0 rgba(255, 255, 255, 0.12);
      --glass-shadow: 0 32px 64px -12px rgba(0, 0, 0, 0.65), 0 8px 24px rgba(0, 0, 0, 0.35);
      --glass-blur: blur(30px) saturate(190%) brightness(1.06);
      --text-primary: #FAF8F5;
      --text-secondary: #E2E8F0;
      --text-muted: #A1A1AA;
      --accent-primary: #E11D48;
      --accent-secondary: #F59E0B;
      --accent-glow: rgba(245, 158, 11, 0.25);
      --card-radius: 30px;
      --pill-radius: 999px;
      --heading-font: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }}

    html[data-liquid-version="v4"] {{
      /* V4: Ryan Holiday "Stillness Is The Key" Architectural Frosted Monolith */
      --bg-canvas: #FAF8F5;
      --bg-mesh: linear-gradient(180deg, #FAF8F5 0%, #F3EFEA 100%);
      --glass-surface: rgba(255, 255, 255, 0.88);
      --glass-surface-strong: rgba(255, 255, 255, 0.96);
      --glass-surface-subtle: rgba(245, 242, 235, 0.75);
      --glass-border: rgba(226, 220, 210, 0.9);
      --glass-outer-stroke: rgba(28, 25, 23, 0.08);
      --glass-specular-top: inset 0 1px 0 rgba(255, 255, 255, 1);
      --glass-shadow: 0 12px 32px -10px rgba(28, 25, 23, 0.06);
      --glass-blur: blur(20px) saturate(140%);
      --text-primary: #1C1917;
      --text-secondary: #44403C;
      --text-muted: #78716C;
      --accent-primary: #B91C1C;
      --accent-secondary: #1D4ED8;
      --accent-glow: rgba(185, 28, 28, 0.14);
      --card-radius: 18px;
      --pill-radius: 999px;
      --heading-font: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }}

    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    html {{ scroll-behavior: smooth; }}
    body {{
      font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
      background-color: var(--bg-canvas);
      background-image: var(--bg-mesh);
      background-attachment: fixed;
      color: var(--text-primary);
      min-height: 100vh;
      line-height: 1.55;
      -webkit-font-smoothing: antialiased;
      transition: background 0.35s ease, color 0.25s ease;
      overflow-x: hidden;
    }}
    .mono {{ font-family: 'JetBrains Mono', monospace; }}
    .lg-svg-icon {{
      width: 18px;
      height: 18px;
      display: inline-block;
      vertical-align: -0.18em;
      flex-shrink: 0;
      stroke: currentColor;
      fill: none;
      transition: transform 0.18s ease, stroke 0.18s ease;
      user-select: none;
    }}

    /* ==========================================================================
       LIQUID GLASS SURFACES, 3D PERSPECTIVE TILT & ANODIZED VECTOR BADGES
       ========================================================================== */
    .liquid-card {{
      position: relative;
      background: var(--glass-surface);
      backdrop-filter: var(--glass-blur);
      -webkit-backdrop-filter: var(--glass-blur);
      border-radius: var(--card-radius);
      border: 1px solid var(--glass-border);
      outline: 1px solid var(--glass-outer-stroke);
      box-shadow: var(--glass-specular-top), var(--glass-shadow);
      transition: transform 0.22s cubic-bezier(0.22, 1, 0.36, 1), box-shadow 0.25s ease, border-color 0.25s ease;
      overflow: hidden;
    }}
    /* 120fps Compositor Optimization: Avoid stacking 35+ heavy backdrop-filter blurs on Archive & Track cards */
    .archive-blueprint-card,
    .bay-track-pill,
    .glossary-term-card {{
      backdrop-filter: none;
      -webkit-backdrop-filter: none;
      background: var(--glass-surface-strong);
      content-visibility: auto;
      contain-intrinsic-size: 210px;
    }}
    .liquid-card::before {{
      content: "";
      position: absolute;
      inset: 0;
      pointer-events: none;
      background: radial-gradient(
        480px circle at var(--glare-x, 25%) var(--glare-y, 15%),
        rgba(255, 255, 255, 0.18),
        transparent 60%
      );
      opacity: 0.75;
      z-index: 0;
    }}
    .liquid-card > * {{ position: relative; z-index: 1; }}

    html[data-liquid-version="v3"] .liquid-3d-tilt {{
      transform: perspective(1100px) rotateX(var(--rx, 0deg)) rotateY(var(--ry, 0deg));
    }}
    .liquid-card:hover {{
      transform: translateY(-2px);
    }}
    html[data-liquid-version="v3"] .liquid-3d-tilt:hover {{
      transform: perspective(1100px) rotateX(var(--rx, 0deg)) rotateY(var(--ry, 0deg)) translateY(-3px);
    }}

    .liquid-pulse-highlight {{
      box-shadow: 0 0 0 3px var(--accent-primary), 0 0 36px var(--accent-glow), var(--glass-shadow) !important;
    }}

    /* 2026 Linear / Apple visionOS Anodized Glass-Metal Vector Badges */
    .squircle-3d-icon {{
      width: 44px;
      height: 44px;
      flex-shrink: 0;
      border-radius: 13px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      background: linear-gradient(145deg, rgba(15, 23, 42, 0.90) 0%, rgba(9, 13, 24, 0.98) 100%);
      border: 1px solid rgba(255, 255, 255, 0.18);
      box-shadow:
        inset 0 1px 0 rgba(255, 255, 255, 0.26),
        inset 0 -1px 0 rgba(0, 0, 0, 0.45),
        0 8px 20px -6px rgba(15, 23, 42, 0.28);
      position: relative;
      color: #F8FAFC;
      transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
    }}
    .squircle-3d-icon .lg-svg-icon {{
      vertical-align: middle;
      filter: drop-shadow(0 0 8px currentColor);
    }}
    .squircle-3d-icon.sm {{ width: 36px; height: 36px; border-radius: 10px; }}
    .squircle-3d-icon.tint-crimson {{
      color: #FF4D5E;
      background: linear-gradient(145deg, rgba(36, 12, 20, 0.94) 0%, rgba(15, 10, 18, 0.98) 100%);
      border-color: rgba(255, 77, 94, 0.42);
      box-shadow: inset 0 1px 0 rgba(255, 120, 133, 0.32), 0 8px 20px -6px rgba(216, 30, 40, 0.28);
    }}
    .squircle-3d-icon.tint-cobalt {{
      color: #38BDF8;
      background: linear-gradient(145deg, rgba(12, 26, 46, 0.94) 0%, rgba(10, 16, 29, 0.98) 100%);
      border-color: rgba(56, 189, 248, 0.42);
      box-shadow: inset 0 1px 0 rgba(125, 211, 252, 0.32), 0 8px 20px -6px rgba(0, 102, 204, 0.28);
    }}
    .squircle-3d-icon.tint-emerald {{
      color: #34D399;
      background: linear-gradient(145deg, rgba(10, 33, 28, 0.94) 0%, rgba(9, 19, 18, 0.98) 100%);
      border-color: rgba(52, 211, 153, 0.42);
      box-shadow: inset 0 1px 0 rgba(110, 231, 183, 0.32), 0 8px 20px -6px rgba(5, 150, 105, 0.28);
    }}
    .squircle-3d-icon.tint-purple {{
      color: #C084FC;
      background: linear-gradient(145deg, rgba(28, 16, 46, 0.94) 0%, rgba(15, 11, 28, 0.98) 100%);
      border-color: rgba(192, 132, 252, 0.42);
      box-shadow: inset 0 1px 0 rgba(216, 180, 254, 0.32), 0 8px 20px -6px rgba(124, 58, 237, 0.28);
    }}
    .squircle-3d-icon.tint-amber {{
      color: #FBBF24;
      background: linear-gradient(145deg, rgba(38, 24, 12, 0.94) 0%, rgba(20, 14, 10, 0.98) 100%);
      border-color: rgba(251, 191, 36, 0.42);
      box-shadow: inset 0 1px 0 rgba(253, 224, 71, 0.32), 0 8px 20px -6px rgba(217, 119, 6, 0.28);
    }}

    /* ==========================================================================
       TOP SPATIAL ORNAMENT DOCK & 4-VERSION SWITCHER
       ========================================================================== */
    .spatial-header-wrap {{
      position: sticky;
      top: 12px;
      z-index: 90;
      max-width: 1380px;
      margin: 12px auto 0;
      padding: 0 20px;
    }}
    .spatial-ornament-bar {{
      background: var(--glass-surface-strong);
      backdrop-filter: var(--glass-blur);
      -webkit-backdrop-filter: var(--glass-blur);
      border: 1px solid var(--glass-border);
      outline: 1px solid var(--glass-outer-stroke);
      box-shadow: var(--glass-specular-top), var(--glass-shadow);
      border-radius: 22px;
      padding: 10px 16px;
      display: flex;
      flex-wrap: nowrap;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
    }}
    .brand-cluster {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}
    .brand-title {{
      font-size: 16px;
      font-weight: 800;
      letter-spacing: -0.02em;
      color: var(--text-primary);
    }}
    .brand-subtitle {{
      font-size: 11px;
      color: var(--text-muted);
      font-family: 'JetBrains Mono', monospace;
    }}

    /* 4 Primary Navigation Tabs */
    .spatial-nav-tabs {{
      display: flex;
      align-items: center;
      gap: 6px;
      background: var(--glass-surface-subtle);
      padding: 5px;
      border-radius: 999px;
      border: 1px solid var(--glass-outer-stroke);
      overflow-x: auto;
    }}
    .spatial-tab-btn {{
      border: none;
      background: transparent;
      color: var(--text-secondary);
      font-family: inherit;
      font-size: 13px;
      font-weight: 700;
      padding: 8px 15px;
      border-radius: 999px;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      white-space: nowrap;
      transition: all 0.18s ease;
    }}
    .spatial-tab-btn:hover {{
      color: var(--text-primary);
      background: rgba(128, 128, 128, 0.09);
    }}
    .spatial-tab-btn.active {{
      background: var(--accent-primary);
      color: #FFFFFF;
      box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.4), 0 4px 12px var(--accent-glow);
    }}

    /* 4-Version Liquid Glass Switcher Button + Popover Menu */
    .version-switcher-wrap {{
      position: relative;
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }}
    .version-swap-trigger {{
      border: 1px solid var(--glass-outer-stroke);
      background: var(--glass-surface-subtle);
      color: var(--text-primary);
      font-family: inherit;
      font-size: 12.5px;
      font-weight: 800;
      padding: 8px 13px;
      border-radius: 999px;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 7px;
      white-space: nowrap;
      transition: all 0.18s ease;
      box-shadow: var(--glass-specular-top);
    }}
    .version-swap-trigger:hover {{
      border-color: var(--accent-primary);
      transform: translateY(-1px);
    }}
    .version-cycle-btn {{
      border: 1px solid var(--accent-primary);
      background: var(--accent-primary);
      color: #FFFFFF;
      font-family: 'JetBrains Mono', monospace;
      font-size: 11.5px;
      font-weight: 800;
      padding: 8px 12px;
      border-radius: 999px;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 5px;
      white-space: nowrap;
      box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.35), 0 4px 12px var(--accent-glow);
      transition: all 0.18s ease;
    }}
    .version-cycle-btn:hover {{
      opacity: 0.94;
      transform: translateY(-1px);
    }}
    .version-popover-menu {{
      position: absolute;
      top: calc(100% + 10px);
      right: 0;
      width: 340px;
      background: var(--glass-surface-strong);
      backdrop-filter: blur(48px) saturate(210%);
      -webkit-backdrop-filter: blur(48px) saturate(210%);
      border: 1px solid var(--glass-border);
      outline: 1px solid var(--glass-outer-stroke);
      box-shadow: 0 24px 56px rgba(0, 0, 0, 0.28);
      border-radius: 20px;
      padding: 10px;
      display: none;
      flex-direction: column;
      gap: 6px;
      z-index: 150;
    }}
    .version-popover-menu.open {{
      display: flex;
      animation: paneFade 0.18s ease-out;
    }}
    .version-menu-item {{
      border: 1px solid transparent;
      background: transparent;
      color: var(--text-primary);
      text-align: left;
      padding: 10px 12px;
      border-radius: 14px;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 10px;
      transition: all 0.15s ease;
      font-family: inherit;
    }}
    .version-menu-item:hover {{
      background: var(--glass-surface-subtle);
      border-color: var(--glass-outer-stroke);
    }}
    .version-menu-item.active {{
      background: var(--glass-surface-subtle);
      border-color: var(--accent-primary);
      box-shadow: 0 0 0 1px var(--accent-primary);
    }}
    .ver-swatch {{
      width: 28px;
      height: 28px;
      border-radius: 9px;
      flex-shrink: 0;
      border: 1px solid rgba(255, 255, 255, 0.45);
      box-shadow: 0 2px 6px rgba(0, 0, 0, 0.18);
    }}
    .ver-swatch-v1 {{ background: linear-gradient(135deg, #F6F8FC 0%, #D81E28 50%, #0066CC 100%); }}
    .ver-swatch-v2 {{ background: linear-gradient(135deg, #04060E 0%, #FF2E4C 55%, #00F0FF 100%); }}
    .ver-swatch-v3 {{ background: linear-gradient(135deg, #161923 0%, #F59E0B 55%, #E11D48 100%); }}
    .ver-swatch-v4 {{ background: linear-gradient(135deg, #FAF8F5 0%, #E2DCD2 55%, #B91C1C 100%); }}
    .ver-item-title {{ font-size: 12.5px; font-weight: 800; color: var(--text-primary); }}
    .ver-item-sub {{ font-size: 11px; color: var(--text-muted); margin-top: 1px; }}

    /* Inline 4-Version Pill Strip inside Hero Card */
    .version-switcher-pill {{
      display: inline-flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 4px;
      background: var(--glass-surface-subtle);
      padding: 3px;
      border-radius: 999px;
      border: 1px solid var(--glass-outer-stroke);
    }}
    .ver-btn {{
      border: none;
      background: transparent;
      color: var(--text-secondary);
      font-family: 'JetBrains Mono', monospace;
      font-size: 10.5px;
      font-weight: 700;
      padding: 5px 10px;
      border-radius: 999px;
      cursor: pointer;
      transition: all 0.18s ease;
      white-space: nowrap;
    }}
    .ver-btn.active {{
      background: var(--text-primary);
      color: var(--bg-canvas);
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.18);
    }}

    /* ==========================================================================
       MAIN CONTAINER & HERO LIVE VIDEO AVATAR CONCIERGE DECK
       ========================================================================== */
    .portal-main {{
      max-width: 1380px;
      margin: 22px auto 64px;
      padding: 0 20px;
      display: flex;
      flex-direction: column;
      gap: 28px;
    }}

    .hero-spatial-grid {{
      display: grid;
      grid-template-columns: 360px 1fr;
      gap: 22px;
      align-items: stretch;
    }}

    /* Left: Real Photorealistic Gemini 3.8 Live Video Avatar Stage */
    .avatar-stage-card {{
      padding: 18px;
      display: flex;
      flex-direction: column;
      gap: 12px;
    }}
    .avatar-stage-viewport {{
      position: relative;
      width: 100%;
      aspect-ratio: 4 / 4.4;
      border-radius: 20px;
      overflow: hidden;
      background: #0B0F19;
      border: 1px solid rgba(255, 255, 255, 0.22);
      box-shadow: inset 0 0 24px rgba(0, 0, 0, 0.45);
    }}
    .avatar-stage-viewport[data-live-state="speaking"] {{
      box-shadow: 0 0 0 2px #10B981, 0 0 28px rgba(16, 185, 129, 0.45);
    }}
    .avatar-stage-viewport[data-live-state="listening"],
    .avatar-stage-viewport[data-live-state="user_speaking"] {{
      box-shadow: 0 0 0 2px #0066CC, 0 0 28px rgba(0, 102, 204, 0.45);
    }}
    .portal-avatar-poster {{
      width: 100%;
      height: 100%;
      object-fit: cover;
      object-position: center 18%;
      display: block;
    }}
    .portal-avatar-video {{
      position: absolute;
      inset: 0;
      width: 100%;
      height: 100%;
      object-fit: cover;
      object-position: center 18%;
      opacity: 0 !important;
      transition: opacity 0.22s ease !important;
      pointer-events: none;
    }}
    .portal-avatar-video.is-streaming {{
      opacity: 1 !important;
    }}
    .avatar-stage-hud-top {{
      position: absolute;
      top: 10px;
      left: 10px;
      right: 10px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 6px;
      z-index: 3;
    }}
    .avatar-live-pill {{
      background: rgba(11, 15, 25, 0.76);
      backdrop-filter: blur(16px);
      color: #F8FAFC;
      border: 1px solid rgba(255, 255, 255, 0.2);
      padding: 4px 10px;
      border-radius: 999px;
      font-size: 10.5px;
      font-weight: 700;
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }}
    .status-dot {{
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: #10B981;
    }}
    .status-dot.state-speaking {{ background: #10B981; box-shadow: 0 0 10px #10B981; }}
    .status-dot.state-listening, .status-dot.state-user_speaking {{ background: #38BDF8; box-shadow: 0 0 10px #38BDF8; }}
    .status-dot.state-connecting, .status-dot.state-thinking {{ background: #F59E0B; box-shadow: 0 0 10px #F59E0B; }}

    .avatar-external-status-bar {{
      background: var(--glass-surface-subtle);
      border: 1px solid var(--glass-outer-stroke);
      border-radius: 12px;
      padding: 7px 11px;
      display: flex;
      flex-direction: column;
      gap: 2px;
    }}
    .avatar-name-role-row {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 6px;
    }}
    .avatar-name-line {{ font-size: 13px; font-weight: 800; color: var(--text-primary); }}
    .avatar-role-line {{ font-size: 10.5px; font-weight: 600; color: var(--text-secondary); }}
    .avatar-status-subline {{ font-size: 10.5px; color: var(--accent-secondary); font-weight: 700; }}

    .avatar-roster-strip {{
      display: grid;
      grid-template-columns: repeat(5, 1fr);
      gap: 5px;
    }}
    .avatar-chip-btn {{
      border: 1px solid var(--glass-outer-stroke);
      background: var(--glass-surface-subtle);
      color: var(--text-secondary);
      border-radius: 10px;
      padding: 4px 2px;
      font-size: 10px;
      font-weight: 700;
      cursor: pointer;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 2px;
      transition: all 0.15s ease;
      white-space: nowrap;
      overflow: hidden;
    }}
    .avatar-chip-btn img {{
      width: 22px;
      height: 22px;
      border-radius: 50%;
      object-fit: cover;
      flex-shrink: 0;
    }}
    .avatar-chip-btn.active {{
      border-color: var(--accent-primary);
      background: var(--accent-primary);
      color: #FFFFFF;
    }}

    .avatar-controls-row {{
      display: flex;
      gap: 8px;
    }}
    .btn-live-call {{
      flex: 1;
      border: none;
      border-radius: 12px;
      padding: 11px 14px;
      font-family: inherit;
      font-size: 13px;
      font-weight: 800;
      color: #FFFFFF;
      background: linear-gradient(135deg, #D81E28 0%, #B91C1C 100%);
      box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.35), 0 8px 18px rgba(216, 30, 40, 0.25);
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 7px;
    }}
    .btn-live-call.is-live {{
      background: linear-gradient(135deg, #059669 0%, #047857 100%);
      box-shadow: 0 0 20px rgba(16, 185, 129, 0.35);
    }}
    .btn-live-stop {{
      border: 1px solid var(--glass-outer-stroke);
      background: var(--glass-surface-subtle);
      color: var(--text-primary);
      border-radius: 12px;
      padding: 11px 12px;
      font-size: 12px;
      font-weight: 700;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 4px;
    }}

    /* Right: Omniscient Portal Guide & Ryan Holiday Executive Clarity Deck */
    .hero-copilot-card {{
      padding: 24px 26px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      gap: 16px;
    }}
    .edition-kicker-row {{
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
    }}
    .hero-headline {{
      font-family: var(--heading-font);
      font-size: clamp(23px, 2.5vw, 31px);
      font-weight: 800;
      letter-spacing: -0.025em;
      line-height: 1.2;
      color: var(--text-primary);
    }}
    html[data-liquid-version="v4"] .hero-headline {{
      font-family: 'Instrument Serif', Georgia, serif;
      font-size: clamp(28px, 3vw, 38px);
      font-weight: 400;
      letter-spacing: -0.01em;
    }}
    .hero-lead {{
      font-size: 14px;
      color: var(--text-secondary);
      max-width: 820px;
    }}

    /* Interactive Copilot Feed & Input */
    .copilot-feed {{
      background: var(--glass-surface-subtle);
      border: 1px solid var(--glass-outer-stroke);
      border-radius: 16px;
      padding: 12px 14px;
      max-height: 175px;
      overflow-y: auto;
      display: flex;
      flex-direction: column;
      gap: 10px;
    }}
    .copilot-msg {{
      padding: 9px 12px;
      border-radius: 12px;
      font-size: 13px;
      line-height: 1.48;
    }}
    .copilot-msg-user {{
      align-self: flex-end;
      background: var(--accent-primary);
      color: #FFFFFF;
      max-width: 85%;
    }}
    .copilot-msg-assistant {{
      align-self: flex-start;
      background: var(--glass-surface-strong);
      border: 1px solid var(--glass-outer-stroke);
      color: var(--text-primary);
      max-width: 94%;
    }}
    .copilot-msg-hdr {{
      font-size: 10.5px;
      font-weight: 700;
      font-family: 'JetBrains Mono', monospace;
      opacity: 0.78;
      margin-bottom: 3px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 8px;
    }}
    .copilot-meta-pill {{
      padding: 2px 8px;
      border-radius: 999px;
      background: rgba(0, 102, 204, 0.14);
      color: var(--accent-secondary);
      font-size: 10px;
      font-weight: 800;
    }}
    .copilot-msg-user .copilot-msg-hdr {{
      opacity: 0.95;
      color: #FFFFFF;
    }}
    .copilot-msg-user .copilot-meta-pill {{
      background: rgba(255, 255, 255, 0.24);
      color: #FFFFFF;
      border: 1px solid rgba(255, 255, 255, 0.45);
    }}
    .lg-inline-code {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.9em;
      font-weight: 700;
      padding: 2px 6px;
      border-radius: 6px;
      background: var(--glass-surface-subtle);
      border: 1px solid var(--glass-outer-stroke);
      color: var(--accent-secondary);
    }}
    .copilot-msg-actions {{
      margin-top: 6px;
      display: flex;
      gap: 8px;
    }}
    .copilot-action-btn {{
      border: none;
      background: transparent;
      color: var(--accent-secondary);
      font-size: 11.5px;
      font-weight: 700;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 4px;
    }}

    .copilot-input-bar {{
      display: flex;
      align-items: center;
      gap: 8px;
      background: var(--glass-surface-strong);
      border: 1px solid var(--glass-border);
      outline: 1px solid var(--glass-outer-stroke);
      border-radius: 14px;
      padding: 6px 8px 6px 14px;
    }}
    .copilot-input-bar input {{
      flex: 1;
      border: none;
      background: transparent;
      color: var(--text-primary);
      font-family: inherit;
      font-size: 14px;
      outline: none;
    }}
    .copilot-quick-chips {{
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
    }}
    .quick-ask-chip {{
      border: 1px solid var(--glass-outer-stroke);
      background: var(--glass-surface-subtle);
      color: var(--text-secondary);
      border-radius: 999px;
      padding: 5px 11px;
      font-size: 11.5px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.15s ease;
    }}
    .quick-ask-chip:hover {{
      border-color: var(--accent-primary);
      color: var(--text-primary);
    }}

    /* ==========================================================================
       SHARED BUTTONS, BADGES, SECTION HEADERS & GRIDS
       ========================================================================== */
    .lg-badge {{
      display: inline-flex;
      align-items: center;
      gap: 5px;
      padding: 4px 10px;
      border-radius: 999px;
      font-size: 10.5px;
      font-weight: 800;
      font-family: 'JetBrains Mono', monospace;
      letter-spacing: 0.03em;
    }}
    .lg-badge-crimson {{ background: rgba(216, 30, 40, 0.14); color: #E11D48; border: 1px solid rgba(216, 30, 40, 0.28); }}
    .lg-badge-cobalt  {{ background: rgba(0, 102, 204, 0.14); color: #2563EB; border: 1px solid rgba(0, 102, 204, 0.28); }}
    .lg-badge-emerald {{ background: rgba(5, 150, 105, 0.14); color: #059669; border: 1px solid rgba(5, 150, 105, 0.28); }}
    .lg-badge-purple  {{ background: rgba(124, 58, 237, 0.14); color: #7C3AED; border: 1px solid rgba(124, 58, 237, 0.28); }}
    .lg-badge-amber   {{ background: rgba(217, 119, 6, 0.15); color: #D97706; border: 1px solid rgba(217, 119, 6, 0.3); }}
    html[data-liquid-version="v2"] .lg-badge-cobalt,
    html[data-liquid-version="v3"] .lg-badge-cobalt {{ color: #60A5FA; }}
    html[data-liquid-version="v2"] .lg-badge-crimson,
    html[data-liquid-version="v3"] .lg-badge-crimson {{ color: #FB7185; }}
    html[data-liquid-version="v2"] .lg-badge-emerald,
    html[data-liquid-version="v3"] .lg-badge-emerald {{ color: #34D399; }}
    html[data-liquid-version="v2"] .lg-badge-purple,
    html[data-liquid-version="v3"] .lg-badge-purple {{ color: #C084FC; }}

    .lg-chip {{
      display: inline-flex;
      align-items: center;
      padding: 3px 9px;
      border-radius: 8px;
      font-size: 11px;
      font-weight: 600;
      background: var(--glass-surface-subtle);
      border: 1px solid var(--glass-outer-stroke);
      color: var(--text-secondary);
    }}
    .lg-chip-mono {{ font-family: 'JetBrains Mono', monospace; font-size: 10.5px; }}

    .lg-btn {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
      padding: 9px 15px;
      border-radius: 12px;
      font-size: 12.5px;
      font-weight: 700;
      text-decoration: none;
      cursor: pointer;
      transition: all 0.16s ease;
      border: 1px solid transparent;
    }}
    .lg-btn.sm {{ padding: 7px 12px; font-size: 11.5px; border-radius: 10px; }}
    .lg-btn.sm-full {{ width: 100%; padding: 8px 12px; font-size: 12px; margin-top: auto; }}
    .lg-btn-primary {{
      background: var(--accent-primary);
      color: #FFFFFF;
      box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.35), 0 6px 16px var(--accent-glow);
    }}
    .lg-btn-primary:hover {{ opacity: 0.94; transform: translateY(-1px); }}
    .lg-btn-glass {{
      background: var(--glass-surface-strong);
      color: var(--text-primary);
      border-color: var(--glass-outer-stroke);
      box-shadow: var(--glass-specular-top);
    }}
    .lg-btn-glass:hover {{ border-color: var(--accent-secondary); }}

    .portal-tab-pane {{ display: none; flex-direction: column; gap: 28px; }}
    .portal-tab-pane.active {{ display: flex; animation: paneFade 0.24s ease-out; }}
    @keyframes paneFade {{
      from {{ opacity: 0; transform: translateY(6px); }}
      to {{ opacity: 1; transform: translateY(0); }}
    }}

    .section-hdr {{
      display: flex;
      flex-wrap: wrap;
      align-items: flex-end;
      justify-content: space-between;
      gap: 12px;
      margin-bottom: 14px;
    }}
    .section-title {{
      font-size: 21px;
      font-weight: 800;
      letter-spacing: -0.02em;
      color: var(--text-primary);
    }}
    .section-sub {{
      font-size: 13.5px;
      color: var(--text-muted);
    }}

    /* ==========================================================================
       TAB 1: FLAGSHIP 5-PILLAR CARDS, GECX, SUPER-WOW & 8 BAY IDEAS
       ========================================================================== */
    .pillars-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(390px, 1fr));
      gap: 20px;
    }}
    .pillar-showcase-card {{
      display: flex;
      flex-direction: column;
    }}
    .pillar-card-top-bar {{
      padding: 12px 16px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 8px;
      background: var(--glass-surface-strong);
      border-bottom: 1px solid var(--glass-outer-stroke);
    }}
    .lg-diagram-btn {{
      border: 1px solid var(--glass-outer-stroke);
      background: var(--glass-surface-subtle);
      color: var(--text-primary);
      border-radius: 999px;
      padding: 5px 11px;
      font-size: 11px;
      font-weight: 700;
      font-family: inherit;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 5px;
      transition: all 0.15s ease;
    }}
    .lg-diagram-btn:hover {{
      border-color: var(--accent-secondary);
      color: var(--accent-secondary);
    }}
    .pillar-media-wrap {{
      position: relative;
      height: 205px;
      background: #0B0F19;
      overflow: hidden;
      border-bottom: 1px solid var(--glass-outer-stroke);
    }}
    .pillar-gif-preview {{
      width: 100%;
      height: 100%;
      object-fit: cover;
      object-position: top center;
      cursor: zoom-in;
      transition: transform 0.35s ease;
    }}
    .pillar-showcase-card:hover .pillar-gif-preview {{
      transform: scale(1.025);
    }}
    .pillar-body {{
      padding: 20px;
      display: flex;
      flex-direction: column;
      gap: 12px;
      flex: 1;
    }}
    .pillar-title-row {{
      display: flex;
      align-items: flex-start;
      gap: 12px;
    }}
    .pillar-title {{
      font-size: 17px;
      font-weight: 800;
      letter-spacing: -0.015em;
      color: var(--text-primary);
    }}
    .pillar-metrics-line {{
      font-size: 11px;
      color: var(--accent-secondary);
      margin-top: 2px;
    }}
    .pillar-desc {{
      font-size: 13px;
      color: var(--text-secondary);
      line-height: 1.52;
    }}
    .pillar-models-row {{
      display: flex;
      flex-wrap: wrap;
      gap: 5px;
    }}
    .pillar-actions-row {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-top: auto;
      padding-top: 6px;
    }}

    .special-studios-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(460px, 1fr));
      gap: 20px;
    }}
    .special-studio-card {{
      padding: 24px;
      display: flex;
      flex-direction: column;
      gap: 14px;
    }}

    .bay-ideas-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(295px, 1fr));
      gap: 10px;
    }}
    .bay-track-pill {{
      padding: 12px 14px;
      display: flex;
      align-items: center;
      gap: 12px;
      text-decoration: none;
      color: var(--text-primary);
    }}
    .bay-track-hdr {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 6px;
      margin-bottom: 2px;
    }}
    .bay-num-pill {{
      font-size: 10px;
      font-weight: 800;
      color: var(--accent-primary);
    }}
    .bay-track-title {{
      font-size: 13px;
      font-weight: 800;
      color: var(--text-primary);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }}
    .bay-stack {{
      font-size: 10.5px;
      color: var(--accent-secondary);
    }}

    /* ==========================================================================
       TAB 2: BUILD & GITHUB (<3 MIN SETUP) + DIAGRAMS
       ========================================================================== */
    .diagram-showcase-card {{
      padding: 22px;
      display: flex;
      flex-direction: column;
      gap: 14px;
    }}
    .diagram-img-frame {{
      width: 100%;
      border-radius: 16px;
      border: 1px solid var(--glass-outer-stroke);
      background: #FFFFFF;
      padding: 10px;
      cursor: zoom-in;
    }}
    .code-snippet-box {{
      background: #0B0F19;
      color: #E2E8F0;
      border-radius: 14px;
      padding: 16px;
      font-family: 'JetBrains Mono', monospace;
      font-size: 12px;
      line-height: 1.6;
      overflow-x: auto;
      border: 1px solid rgba(255, 255, 255, 0.14);
    }}

    /* ==========================================================================
       TAB 3 & TAB 4: TABLES, GLOSSARY & ARCHIVE CARDS
       ========================================================================== */
    .filter-toolbar {{
      padding: 16px 20px;
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
    }}
    .search-input-wrap {{
      flex: 1;
      min-width: 260px;
      display: flex;
      align-items: center;
      gap: 8px;
      background: var(--glass-surface-strong);
      border: 1px solid var(--glass-outer-stroke);
      border-radius: 12px;
      padding: 8px 14px;
    }}
    .search-input-wrap input {{
      width: 100%;
      border: none;
      background: transparent;
      color: var(--text-primary);
      font-size: 13.5px;
      outline: none;
    }}
    .filter-pills-row {{
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
    }}
    .filter-pill-btn {{
      border: 1px solid var(--glass-outer-stroke);
      background: var(--glass-surface-subtle);
      color: var(--text-secondary);
      border-radius: 999px;
      padding: 6px 12px;
      font-size: 12px;
      font-weight: 700;
      cursor: pointer;
    }}
    .filter-pill-btn.active {{
      background: var(--accent-primary);
      color: #FFFFFF;
      border-color: var(--accent-primary);
    }}

    .liquid-table-wrap {{
      overflow-x: auto;
      border-radius: 20px;
    }}
    table.liquid-table {{
      width: 100%;
      border-collapse: collapse;
      text-align: left;
      font-size: 13px;
    }}
    table.liquid-table th {{
      padding: 14px 16px;
      font-size: 11px;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      font-family: 'JetBrains Mono', monospace;
      color: var(--text-muted);
      border-bottom: 1px solid var(--glass-outer-stroke);
      background: var(--glass-surface-subtle);
    }}
    table.liquid-table td {{
      padding: 14px 16px;
      border-bottom: 1px solid var(--glass-outer-stroke);
      vertical-align: top;
    }}
    .tbl-strong {{ font-weight: 800; color: var(--text-primary); margin-bottom: 2px; }}
    .tbl-code {{ font-size: 11px; color: var(--accent-secondary); }}
    .tbl-desc {{ color: var(--text-secondary); line-height: 1.5; }}
    .tbl-meta {{ font-size: 11.5px; color: var(--text-muted); }}
    .tbl-link {{ font-weight: 800; color: var(--accent-secondary); text-decoration: none; }}
    .tbl-sub {{ font-size: 12px; color: var(--text-muted); margin-top: 3px; }}

    .glossary-terms-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
      gap: 16px;
    }}
    .glossary-term-card {{
      padding: 20px;
      display: flex;
      flex-direction: column;
      gap: 8px;
    }}
    .term-title {{ font-size: 16px; font-weight: 800; color: var(--text-primary); }}
    .term-desc {{ font-size: 13px; color: var(--text-secondary); flex: 1; }}
    .term-tools {{ font-size: 11.5px; color: var(--accent-secondary); padding-top: 6px; border-top: 1px solid var(--glass-outer-stroke); }}

    .archive-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(330px, 1fr));
      gap: 16px;
    }}
    .archive-blueprint-card {{
      padding: 20px;
      display: flex;
      flex-direction: column;
      gap: 10px;
    }}
    .archive-card-hdr {{
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 6px;
    }}
    .archive-dept-lbl {{ font-size: 11px; color: var(--text-muted); margin-left: auto; }}
    .archive-title {{ font-size: 15.5px; font-weight: 800; color: var(--text-primary); }}
    .archive-desc {{ font-size: 12.5px; color: var(--text-secondary); line-height: 1.5; flex: 1; }}
    .archive-stack {{ font-size: 11px; color: var(--accent-secondary); }}
    .archive-actions {{ display: flex; gap: 8px; padding-top: 6px; }}

    /* Lightbox Modal */
    .diagram-lightbox {{
      position: fixed;
      inset: 0;
      z-index: 200;
      background: rgba(5, 8, 17, 0.86);
      backdrop-filter: blur(20px);
      display: none;
      align-items: center;
      justify-content: center;
      padding: 24px;
    }}
    .diagram-lightbox.open {{ display: flex; }}
    .lightbox-inner {{
      max-width: 1280px;
      width: 100%;
      max-height: 92vh;
      background: #FFFFFF;
      border-radius: 20px;
      padding: 18px;
      display: flex;
      flex-direction: column;
      gap: 12px;
      overflow: auto;
    }}
    .lightbox-hdr {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      color: #0F172A;
      font-weight: 800;
    }}
    .lightbox-inner img {{ width: 100%; height: auto; border-radius: 12px; }}

    /* Interactive Live Autonomous Studio Workbench & Glowing Agent Cursor */
    .autonomous-workbench {{
      margin-bottom: 24px;
      scroll-margin-top: 96px;
      padding: 20px 22px;
      border: 2px solid var(--accent-primary);
      display: none;
      flex-direction: column;
      gap: 16px;
      position: relative;
      overflow: hidden;
    }}
    .autonomous-workbench.open {{
      display: flex;
      animation: wbSlideDown 0.28s cubic-bezier(0.22, 1, 0.36, 1);
    }}
    @keyframes wbSlideDown {{
      from {{ opacity: 0; transform: translateY(-10px); }}
      to {{ opacity: 1; transform: translateY(0); }}
    }}
    .wb-header-bar {{
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      padding-bottom: 12px;
      border-bottom: 1px solid var(--glass-outer-stroke);
    }}
    .wb-steps-strip {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 10px;
    }}
    .wb-step-card {{
      background: var(--glass-surface-subtle);
      border: 1px solid var(--glass-outer-stroke);
      border-radius: 12px;
      padding: 10px 12px;
      font-size: 11.5px;
      color: var(--text-secondary);
      transition: all 0.22s ease;
      display: flex;
      flex-direction: column;
      gap: 4px;
    }}
    .wb-step-card.active {{
      border-color: var(--accent-primary);
      background: var(--glass-surface-strong);
      box-shadow: 0 0 0 2px rgba(216, 30, 40, 0.16);
      color: var(--text-primary);
    }}
    .wb-step-card.done {{
      border-color: var(--accent-tertiary);
      background: var(--glass-surface-strong);
    }}
    .wb-kpi-grid {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 12px;
    }}
    .wb-kpi-box {{
      background: var(--glass-surface-strong);
      border: 1px solid var(--glass-outer-stroke);
      border-radius: 14px;
      padding: 12px 14px;
    }}
    .wb-kpi-lbl {{
      font-size: 10.5px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.04em;
      color: var(--text-muted);
    }}
    .wb-kpi-val {{
      font-size: 20px;
      font-weight: 800;
      color: var(--text-primary);
      margin-top: 3px;
    }}
    .wb-controls-bar {{
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 10px;
      padding: 10px 14px;
      border-radius: 14px;
      background: var(--glass-surface-subtle);
      border: 1px solid var(--glass-outer-stroke);
    }}
    .portal-agent-cursor {{
      position: fixed;
      top: 50%;
      left: 50%;
      z-index: 350;
      pointer-events: none;
      display: none;
      align-items: center;
      gap: 8px;
      transition: top 0.48s cubic-bezier(0.22, 1, 0.36, 1), left 0.48s cubic-bezier(0.22, 1, 0.36, 1), transform 0.2s ease;
    }}
    .portal-agent-cursor.visible {{
      display: inline-flex;
    }}
    .agent-cursor-dot {{
      width: 22px;
      height: 22px;
      border-radius: 50%;
      background: #D81E28;
      border: 2.5px solid #FFFFFF;
      box-shadow: 0 0 18px rgba(216, 30, 40, 0.85), 0 4px 12px rgba(0,0,0,0.35);
      display: flex;
      align-items: center;
      justify-content: center;
      color: #FFFFFF;
    }}
    .agent-cursor-pill {{
      background: rgba(11, 15, 25, 0.92);
      color: #F8FAFC;
      border: 1px solid rgba(255, 255, 255, 0.22);
      border-radius: 999px;
      padding: 6px 12px;
      font-size: 11.5px;
      font-weight: 700;
      white-space: nowrap;
      box-shadow: 0 10px 25px rgba(0, 0, 0, 0.35);
    }}

    /* Responsive Mobile (412px Pixel 11 Pro) */
    @media (max-width: 960px) {{
      .hero-spatial-grid {{ grid-template-columns: 1fr; }}
      .pillars-grid, .special-studios-grid, .wb-steps-strip, .wb-kpi-grid {{ grid-template-columns: 1fr; }}
      .spatial-header-wrap {{ padding: 0 12px; }}
      .portal-main {{ padding: 0 12px; }}
    }}
  </style>
</head>
<body>
  <!-- SVG Optical Liquid Glass Refraction Filter -->
  <svg width="0" height="0" style="position:absolute;pointer-events:none;" aria-hidden="true">
    <defs>
      <filter id="apple-liquid-refraction" x="-10%" y="-10%" width="120%" height="120%">
        <feTurbulence type="fractalNoise" baseFrequency="0.012" numOctaves="2" result="noise" />
        <feDisplacementMap in="SourceGraphic" in2="noise" scale="4" xChannelSelector="R" yChannelSelector="G" />
      </filter>
    </defs>
  </svg>

  <!-- TOP SPATIAL ORNAMENT BAR (4 TABS + 4 LIQUID GLASS VERSIONS) -->
  <header class="spatial-header-wrap">
    <div class="spatial-ornament-bar">
      <div class="brand-cluster">
        <div class="squircle-3d-icon tint-crimson sm">
          {_svg("rocket", 19)}
        </div>
        <div>
          <div class="brand-title">Rocket × Google Cloud</div>
          <div class="brand-subtitle">SINGLE SOURCE OF TRUTH · 2026 AI HUB</div>
        </div>
      </div>

      <!-- 4 Effortless Primary Tabs -->
      <nav class="spatial-nav-tabs" role="tablist" aria-label="Primary Portal Sections">
        <button type="button" class="spatial-tab-btn active" data-tab-btn="studios" onclick="switchPortalTab('studios')">
          {_svg("studios", 16)}
          1. Live Studios
        </button>
        <button type="button" class="spatial-tab-btn" data-tab-btn="build" onclick="switchPortalTab('build')">
          {_svg("terminal", 16)}
          2. Build &amp; GitHub (&lt;3m)
        </button>
        <button type="button" class="spatial-tab-btn" data-tab-btn="glossary" onclick="switchPortalTab('glossary')">
          {_svg("compass", 16)}
          3. AI &amp; Agent Platform Glossary
        </button>
        <button type="button" class="spatial-tab-btn" data-tab-btn="archive" onclick="switchPortalTab('archive')">
          {_svg("library", 16)}
          4. Reference Library (33)
        </button>
      </nav>

      <!-- 4-Version Apple Liquid Glass & Black Mirror Customer Popover Selector -->
      <div id="ui-version-switcher-wrap" class="version-switcher-wrap" aria-label="Swap UI Version (4 Spatial Styles)">
        <button type="button" id="ui-version-menu-btn" class="version-swap-trigger" onclick="toggleVersionPopover(event)" title="Choose between all 4 Spatial UI Versions">
          <span style="color:var(--accent-primary);display:inline-flex;">{_svg("layers_theme", 16)}</span>
          <span id="ui-version-active-label">UI: V1 · Prism</span>
          <span style="opacity:0.75;display:inline-flex;">{_svg("chevron_down", 15)}</span>
        </button>

        <div id="ui-version-popover" class="version-popover-menu" role="menu" style="right:0;left:auto;">
          <div class="mono" style="font-size:10px;font-weight:800;color:var(--text-muted);padding:4px 8px;letter-spacing:0.04em;">
            SELECT SPATIAL UI EDITION (4 VERSIONS)
          </div>
          <button type="button" class="version-menu-item active" data-ver-btn="v1" onclick="setLiquidVersion('v1');closeVersionPopover();">
            <span class="ver-swatch ver-swatch-v1"></span>
            <div>
              <div class="ver-item-title">V1 · Cupertino Daylight Prism (Default)</div>
              <div class="ver-item-sub">Apple iOS 26 / visionOS translucent quartz &amp; specular glass</div>
            </div>
          </button>
          <button type="button" class="version-menu-item" data-ver-btn="v2" onclick="setLiquidVersion('v2');closeVersionPopover();">
            <span class="ver-swatch ver-swatch-v2"></span>
            <div>
              <div class="ver-item-title">V2 · Black Mirror Obsidian</div>
              <div class="ver-item-sub">Deep-space holographic dark glass &amp; crimson/cyan telemetry</div>
            </div>
          </button>
          <button type="button" class="version-menu-item" data-ver-btn="v3" onclick="setLiquidVersion('v3');closeVersionPopover();">
            <span class="ver-swatch ver-swatch-v3"></span>
            <div>
              <div class="ver-item-title">V3 · Vision Pro Titanium 3D</div>
              <div class="ver-item-sub">Interactive 3D perspective tilt slabs &amp; warm titanium rims</div>
            </div>
          </button>
          <button type="button" class="version-menu-item" data-ver-btn="v4" onclick="setLiquidVersion('v4');closeVersionPopover();">
            <span class="ver-swatch ver-swatch-v4"></span>
            <div>
              <div class="ver-item-title">V4 · Ryan Holiday Stillness</div>
              <div class="ver-item-sub">Warm architectural stone &amp; editorial serif monolith</div>
            </div>
          </button>
        </div>
      </div>
    </div>
  </header>

  <main class="portal-main">
    <!-- ========================================================================
         HERO DECK: REAL GEMINI 3.8 LIVE VIDEO AVATAR + OMNISCIENT PORTAL CO-PILOT
         ======================================================================== -->
    <section class="hero-spatial-grid">
      <!-- Real Photorealistic Video Avatar Card (100% Unobstructed Portrait + 5 Working Official Video Avatars) -->
      <div class="liquid-card liquid-3d-tilt avatar-stage-card">
        <div id="portal-avatar-stage-box" class="avatar-stage-viewport" data-live-state="idle">
          <img id="portal-avatar-poster" src="/static/official_kira_38_full.jpg" alt="Kira Official Live Video Avatar" class="portal-avatar-poster">
          <video id="portal-avatar-live-video" class="portal-avatar-video" playsinline autoplay></video>

          <div class="avatar-stage-hud-top">
            <span class="avatar-live-pill">
              <span id="portal-avatar-status-dot" class="status-dot"></span>
              <span id="portal-avatar-voice-badge" class="mono">gemini-3.8-live · 24fps Video · Aoede</span>
            </span>
          </div>
        </div>

        <!-- External Unobstructed Status Strip (Never covers the avatar's face or mouth!) -->
        <div class="avatar-external-status-bar">
          <div class="avatar-name-role-row">
            <span class="avatar-name-line" id="portal-avatar-name">Kira</span>
            <span class="avatar-role-line" id="portal-avatar-role">Principal AI Portal Concierge</span>
          </div>
          <div id="portal-avatar-status-text" class="mono avatar-status-subline">
            Ready · Click "Start Live Video Avatar" or ask me to run any demo
          </div>
        </div>

        <!-- 5 Official Vertex AI 24fps Video Avatars (Zero Custom / Broken Avatars) -->
        <div class="avatar-roster-strip">
          <button type="button" class="avatar-chip-btn active" data-avatar-chip="Kira" onclick="selectPortalAvatar('Kira')">
            <img src="/static/official_kira_38.jpg" alt="Kira"> Kira
          </button>
          <button type="button" class="avatar-chip-btn" data-avatar-chip="Sam" onclick="selectPortalAvatar('Sam')">
            <img src="/static/official_sam_38.jpg" alt="Sam"> Sam
          </button>
          <button type="button" class="avatar-chip-btn" data-avatar-chip="Ben" onclick="selectPortalAvatar('Ben')">
            <img src="/static/official_ben_38.jpg" alt="Ben"> Ben
          </button>
          <button type="button" class="avatar-chip-btn" data-avatar-chip="Vera" onclick="selectPortalAvatar('Vera')">
            <img src="/static/official_vera_38.jpg" alt="Vera"> Vera
          </button>
          <button type="button" class="avatar-chip-btn" data-avatar-chip="Leo" onclick="selectPortalAvatar('Leo')">
            <img src="/static/official_leo_38.jpg" alt="Leo"> Leo
          </button>
        </div>

        <div class="avatar-controls-row">
          <button type="button" id="portal-btn-live-toggle" class="btn-live-call" onclick="togglePortalLiveAvatar()">
            {_svg("waveform", 17)}
            <span id="portal-btn-live-label">Start Live Video Avatar</span>
          </button>
          <button type="button" id="portal-btn-live-stop" class="btn-live-stop" onclick="stopAllPortalAudio()" title="Stop Live Video Call &amp; All Audio Immediately (0ms)">
            {_svg("stop_square", 16)}
            Stop
          </button>
        </div>
      </div>

      <!-- Right: Omniscient Portal Co-Pilot & Executive Summary -->
      <div class="liquid-card liquid-3d-tilt hero-copilot-card">
        <div>
          <div class="edition-kicker-row">
            <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
              <span class="lg-badge lg-badge-crimson">ROCKET × GOOGLE CLOUD · SINGLE SOURCE OF TRUTH</span>
            </div>
            <div style="display:flex;gap:8px;flex-wrap:wrap;">
              <a href="{FIVE_PILLAR_PROD_URL}&amp;pillar=1" target="_blank" class="lg-btn lg-btn-primary sm">
                {_svg("play", 14)}
                Open 5-Pillar Live Studio
              </a>
              <a href="/glossary?auth_token={auth_token}" target="_blank" class="lg-btn lg-btn-glass sm" title="Open Standalone Google Cloud Agent Platform &amp; AI Glossary">
                {_svg("compass", 14)}
                AI Glossary (/glossary)
              </a>
              <a href="{GITHUB_ROOT_URL}" target="_blank" class="lg-btn lg-btn-glass sm">
                {_svg("github_code", 14)}
                GitHub Repo
              </a>
            </div>
          </div>
          <h1 class="hero-headline" style="margin-top:10px;">
            Everything Rocket Needs to Build on Google Cloud—In One Calm Place.
          </h1>
          <p class="hero-lead" style="margin-top:6px;">
            Explore the 5 Flagship Production Studios (ordered #1 to #5), Ricky Merrefield’s GECX Launchpad, the &lt;3 Minute GitHub Kit, the Agent Platform Glossary, and 33 Standalone Departmental Microservice Repos.
          </p>
        </div>

        <!-- Omniscient Portal Chat Feed -->
        <div id="portal-copilot-feed" class="copilot-feed">
          <div class="copilot-msg copilot-msg-assistant">
            <div class="copilot-msg-hdr">
              <span>Kira · Principal AI Concierge</span>
              <span class="copilot-meta-pill">Vertex AI · ADK · BigQuery · GECX</span>
            </div>
            <div class="copilot-msg-body">
              Welcome! Ask me any question about our 5 Flagship Studios, how to build agents with Google ADK &amp; Vertex AI Agent Engine, or which of the 33 standalone repositories fits your hackathon track.
            </div>
          </div>
        </div>

        <!-- Ask Anything Input Bar -->
        <div>
          <div class="copilot-input-bar">
            <span style="color:var(--accent-primary);display:inline-flex;">{_svg("sparkle_ai", 18)}</span>
            <input id="portal-copilot-input" type="text"
                   placeholder="Ask Kira about any Google Cloud Agent Platform feature, model, or Rocket studio…"
                   onkeydown="if(event.key==='Enter'){{event.preventDefault();askPortalCopilot();}}">
            <span id="portal-copilot-loader" class="mono" style="display:none;font-size:11px;color:var(--accent-secondary);">Running…</span>
            <button type="button" class="lg-btn lg-btn-primary sm" onclick="askPortalCopilot()">
              {_svg("play", 14)}
              Ask
            </button>
          </div>
          <div class="copilot-quick-chips" style="margin-top:8px;">
            <button type="button" class="quick-ask-chip" onclick="switchPortalTab('studios', 'pillar-1')">
              {_svg("bolt", 13)} Demo #1: BigQuery TimesFM 2.0
            </button>
            <button type="button" class="quick-ask-chip" onclick="switchPortalTab('studios', 'pillar-2')">
              {_svg("video_reel", 13)} Demo #2: Veo 3.1 Reels Studio
            </button>
            <button type="button" class="quick-ask-chip" onclick="switchPortalTab('studios', 'pillar-3')">
              {_svg("map_pin", 13)} Demo #3: Grounded Maps+YT+Search
            </button>
            <button type="button" class="quick-ask-chip" onclick="switchPortalTab('studios', 'pillar-5')">
              {_svg("home_vector", 13)} Demo #5: Hybrid Vector Homes
            </button>
            <button type="button" class="quick-ask-chip" onclick="switchPortalTab('glossary')">
              {_svg("compass", 13)} Agent Platform Glossary
            </button>
          </div>
        </div>
      </div>
    </section>

    <!-- ========================================================================
         TAB 1: FLAGSHIP LIVE STUDIOS (ORDERED DEMO #1 TO DEMO #5)
         ======================================================================== -->
    <div id="tab-pane-studios" class="portal-tab-pane active">
      <!-- 1A. The 5 Flagship Production Pillars -->
      <section>
        <div class="section-hdr">
          <div>
            <span class="lg-badge lg-badge-crimson">TIER 1 · PRODUCTION SHOWCASE (ORDERED DEMO #1 TO #5)</span>
            <h2 class="section-title" style="margin-top:6px;">The 5 Flagship Google Cloud × Rocket AI Studios</h2>
            <p class="section-sub">Click <strong>Launch Live Studio</strong> on any card to open the production application, or click <strong>Architecture &amp; Flow</strong> to inspect the 3x Retina Google Cloud diagrams.</p>
          </div>
          <div style="display:flex;gap:8px;flex-wrap:wrap;">
            <a href="{FIVE_PILLAR_PROD_URL}&amp;pillar=1" target="_blank" class="lg-btn lg-btn-primary">
              {_svg("external_link", 16)}
              Open Full 5-Pillar Studio
            </a>
          </div>
        </div>
        <div class="pillars-grid">
          {"".join(pillar_cards_html)}
        </div>
      </section>

      <!-- 1B. Executive Special Studios: GECX Launchpad & Monday Super-Wow Lab -->
      <section>
        <div class="section-hdr">
          <div>
            <span class="lg-badge lg-badge-cobalt">EXECUTIVE LAUNCHPADS</span>
            <h2 class="section-title" style="margin-top:6px;">GECX Contact Center Studio &amp; Monday Super-Wow Lab</h2>
          </div>
        </div>
        <div class="special-studios-grid">
          <!-- GECX Card -->
          <div id="gecx-card" class="liquid-card liquid-3d-tilt special-studio-card">
            <div style="display:flex;align-items:center;justify-content:space-between;gap:12px;">
              <div class="squircle-3d-icon tint-emerald">
                {_svg("waveform", 22)}
              </div>
              <span class="lg-badge lg-badge-emerald">RICKY MERREFIELD · GECX &amp; CX AGENT STUDIO</span>
            </div>
            <h3 class="pillar-title">Gemini Enterprise for CX (GECX) &amp; <code class="lg-inline-code">cxas-scrappy</code> Launchpad</h3>
            <p class="pillar-desc">
              Build, test, and hill-climb production voice &amp; chat contact center agents for Mr. Cooper Servicing and Rocket Mortgage. Includes the live GECX Launchpad and the <code class="lg-inline-code">cxas-scrappy</code> CLI that compiles a PRD into an evaluated agent automatically.
            </p>
            <div class="pillar-models-row">
              <span class="lg-chip lg-chip-mono">ces.cloud.google.com</span>
              <span class="lg-chip lg-chip-mono">cxas-scrappy Hill-Climbing</span>
              <span class="lg-chip lg-chip-mono">CCAI Agent Assist</span>
            </div>
            <div class="pillar-actions-row">
              <a href="{GECX_LAUNCHPAD_URL}" target="_blank" class="lg-btn lg-btn-primary">
                {_svg("rocket", 16)}
                Launch GECX Launchpad
              </a>
              <a href="{GECX_CONSOLE_URL}" target="_blank" class="lg-btn lg-btn-glass">
                {_svg("external_link", 16)}
                Open CES Console
              </a>
            </div>
          </div>

          <!-- Monday Super-Wow Lab Card -->
          <div id="superwow-card" class="liquid-card liquid-3d-tilt special-studio-card">
            <div style="display:flex;align-items:center;justify-content:space-between;gap:12px;">
              <div class="squircle-3d-icon tint-purple">
                {_svg("bolt", 22)}
              </div>
              <span class="lg-badge lg-badge-purple">5 EXECUTIVE WOW DEMOS · DESKTOP + PIXEL 11 PRO</span>
            </div>
            <h3 class="pillar-title">Monday Super-Wow 5-Option Showcase Lab</h3>
            <p class="pillar-desc">
              Interactive executive lab featuring: <strong>#1</strong> Format-Locked <code class="lg-inline-code">.docx</code> AST Legal Redliner, <strong>#2</strong> Multilingual Borrower Séance, <strong>#3</strong> Cloud KMS &amp; Spanner Agent Passport, <strong>#4</strong> 4.0x Parallel Subagent Swarm Race, and <strong>#5</strong> Sovereign Personal CFO.
            </p>
            <div class="pillar-models-row">
              <a href="{SUPERWOW_URL}&opt=1" target="_blank" class="lg-chip lg-chip-mono" style="text-decoration:none;">#1 .docx Redline ↗</a>
              <a href="{SUPERWOW_URL}&opt=2" target="_blank" class="lg-chip lg-chip-mono" style="text-decoration:none;">#2 Borrower Séance ↗</a>
              <a href="{SUPERWOW_URL}&opt=3" target="_blank" class="lg-chip lg-chip-mono" style="text-decoration:none;">#3 KMS Passport ↗</a>
              <a href="{SUPERWOW_URL}&opt=4" target="_blank" class="lg-chip lg-chip-mono" style="text-decoration:none;">#4 Swarm Race ↗</a>
              <a href="{SUPERWOW_URL}&opt=5" target="_blank" class="lg-chip lg-chip-mono" style="text-decoration:none;">#5 Personal CFO ↗</a>
            </div>
            <div class="pillar-actions-row">
              <a href="{SUPERWOW_URL}" target="_blank" class="lg-btn lg-btn-primary">
                {_svg("sparkle_ai", 16)}
                Launch Super-Wow Lab
              </a>
              <a href="{SUPERWOW_URL}&mobile=1" target="_blank" class="lg-btn lg-btn-glass">
                {_svg("external_link", 16)}
                Mobile Layout Preview
              </a>
            </div>
          </div>
        </div>
      </section>

      <!-- 1C. Compact 8 Rocket's Bay Hackathon Track -> Studio Quick-Jump Strip -->
      <section id="bay-8-ideas">
        <div class="section-hdr" style="margin-bottom:10px;">
          <div>
            <span class="lg-badge lg-badge-amber">8 HACKATHON TRACKS → STUDIO QUICK-JUMP</span>
            <h2 class="section-title" style="margin-top:4px;font-size:19px;">Map Any Rocket’s Bay Track Straight to Its Working Reference Studio</h2>
          </div>
          <a href="{USECASES_DOC_URL}" target="_blank" class="lg-btn lg-btn-glass sm">
            {_svg("doc_blueprint", 15)}
            8 Use Cases Google Doc
          </a>
        </div>
        <div class="bay-ideas-grid">
          {"".join(bay_cards_html)}
        </div>
      </section>
    </div>

    <!-- ========================================================================
         TAB 2: BUILD & GITHUB (<3 MIN SETUP, DIAGRAMS & ACCESS)
         ======================================================================== -->
    <div id="tab-pane-build" class="portal-tab-pane">
      <section class="liquid-card diagram-showcase-card" id="arch-diagram">
        <div class="section-hdr" style="margin-bottom:4px;">
          <div>
            <span class="lg-badge lg-badge-cobalt">3X RETINA ARCHITECTURE &amp; COMPONENT FLOW</span>
            <h2 class="section-title" style="margin-top:6px;">Master Google Cloud Reference Architecture &amp; 5-Block Walkthrough</h2>
            <p class="section-sub">Click any diagram to inspect at full 4800px 3x Retina resolution.</p>
          </div>
          <div style="display:flex;gap:8px;flex-wrap:wrap;">
            <a href="{GITHUB_ROOT_URL}" target="_blank" class="lg-btn lg-btn-primary">
              {_svg("github_code", 16)}
              Open GitHub Repository
            </a>
            <a href="{EXEC_GUIDE_DOC_URL}" target="_blank" class="lg-btn lg-btn-glass">
              {_svg("doc_blueprint", 16)}
              Executive Replication Doc
            </a>
          </div>
        </div>

        <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(420px,1fr));gap:16px;">
          <div>
            <div class="mono" style="font-size:11.5px;font-weight:700;margin-bottom:6px;color:var(--text-secondary);">
              1. Master 5-Pillar Google Cloud Reference Architecture (<code class="lg-inline-code">00_rocket_gcp_reference_architecture.svg</code>)
            </div>
            <img src="/static/nextgen/00_rocket_gcp_reference_architecture.svg" alt="Master GCP Reference Architecture"
                 class="diagram-img-frame"
                 onclick="openDiagramLightbox('/static/nextgen/00_rocket_gcp_reference_architecture.svg', 'Master 5-Pillar Google Cloud Reference Architecture')">
          </div>
          <div>
            <div class="mono" style="font-size:11.5px;font-weight:700;margin-bottom:6px;color:var(--text-secondary);">
              2. End-to-End 5-Block Component Walkthrough (<code class="lg-inline-code">05_rocket_component_walkthrough_banner.svg</code>)
            </div>
            <img src="/static/nextgen/05_rocket_component_walkthrough_banner.svg" alt="5-Block Component Walkthrough"
                 class="diagram-img-frame"
                 onclick="openDiagramLightbox('/static/nextgen/05_rocket_component_walkthrough_banner.svg', '5-Block Component Walkthrough Banner')">
          </div>
        </div>
      </section>

      <!-- <3 Minute Clone & Run Commands + Rocket GCP PAM / Incognito Tips -->
      <section style="display:grid;grid-template-columns:repeat(auto-fit,minmax(440px,1fr));gap:20px;">
        <div class="liquid-card diagram-showcase-card">
          <div style="display:flex;align-items:center;justify-content:space-between;">
            <span class="lg-badge lg-badge-emerald">QUICKSTART · UNDER 3 MINUTES</span>
            <button type="button" class="lg-btn lg-btn-glass sm"
                    onclick="copyTextSnippet(document.getElementById('quickstart-cmd-block').innerText, this)">
              {_svg("doc_blueprint", 14)} Copy Commands
            </button>
          </div>
          <h3 class="pillar-title">1. Clone, Enable 7 GCP APIs &amp; Run Any Pillar Standalone</h3>
          <pre id="quickstart-cmd-block" class="code-snippet-box"># 1. Clone the public Rocket 5-Pillar repository
git clone https://github.com/jchavezar/vertex-ai-samples.git
cd vertex-ai-samples/semiautonomous-agents/rocket

# 2. Enable the 7 required Google Cloud APIs
gcloud services enable \\
  aiplatform.googleapis.com \\
  bigquery.googleapis.com \\
  bigquerystorage.googleapis.com \\
  run.googleapis.com \\
  storage.googleapis.com \\
  cloudbuild.googleapis.com \\
  artifactregistry.googleapis.com

# 3. Copy .env.example and launch the unified studio or any single pillar
cp .env.example .env
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 8080</pre>
        </div>

        <div class="liquid-card diagram-showcase-card">
          <span class="lg-badge lg-badge-amber">HACKATHON FIELD GUIDE · ACCESS &amp; PAM</span>
          <h3 class="pillar-title">2. Rocket GCP Login (`dev-233554-hllwn26-hack-f1f8`), PAM Grant &amp; Codelabs</h3>
          <ul style="list-style:none;display:flex;flex-direction:column;gap:10px;font-size:13px;color:var(--text-secondary);">
            <li>
              <strong>• Step 1 — Open an Incognito Browser Window:</strong> Always use an Incognito window (connected to Rocket VPN for CAA auth) when logging into <code class="lg-inline-code">console.cloud.google.com</code> or Antigravity IDE with your <code class="lg-inline-code">@rocket.com</code> credentials so personal Gmail profiles do not conflict.
            </li>
            <li>
              <strong>• Step 2 — Request PAM Grant (Max 6 Hours):</strong> Open <strong>IAM &amp; Admin → Privileged Access Manager (PAM) → Request Grant</strong> on project <code class="lg-inline-code">dev-233554-hllwn26-hack-f1f8</code> (or request access via Rocket MyAccess Confluence guide).
            </li>
            <li>
              <strong>• Step 3 — Install Antigravity IDE / CLI &amp; Agents CLI:</strong> Download <a href="https://antigravity.google/download" target="_blank" class="tbl-link">Antigravity Desktop/Extension ↗</a>, <a href="https://github.com/google-antigravity/antigravity-cli" target="_blank" class="tbl-link">antigravity-cli ↗</a>, and <a href="https://github.com/google/agents-cli" target="_blank" class="tbl-link">google/agents-cli ↗</a>.
            </li>
            <li>
              <strong>• Step 4 — Hands-On Codelabs:</strong> Practice with <a href="https://codelabs.developers.google.com/Deploy-simple-agent-using-adk" target="_blank" class="tbl-link">Deploy a Simple Agent Using ADK ↗</a> and <a href="https://codelabs.developers.google.com/getting-started-with-antigravity" target="_blank" class="tbl-link">Getting Started with Google Antigravity ↗</a>.
            </li>
          </ul>
        </div>
      </section>

      <!-- What We Promised on the Oct 16 (Detroit) & Oct 19 (India) Demo Sessions -->
      <section class="liquid-card diagram-showcase-card" id="promised-deliverables-card">
        <div class="section-hdr" style="margin-bottom:4px;">
          <div>
            <span class="lg-badge lg-badge-crimson">OCT 16 &amp; OCT 19 DEMO SESSIONS · PROMISED FOLLOW-UPS &amp; CONTACTS</span>
            <h2 class="section-title" style="margin-top:6px;">What We Promised Rocket &amp; Who to Contact</h2>
            <p class="section-sub">Direct access to every license, dataset, code repository, and technical lead promised during the Detroit and India overview sessions.</p>
          </div>
          <a href="{GLOSSARY_DOC_URL}" target="_blank" class="lg-btn lg-btn-primary sm">
            {_svg("doc_blueprint", 15)}
            Open 3-Tab Google Doc Playbook
          </a>
        </div>
        <div class="liquid-table-wrap">
          <table class="liquid-table">
            <thead>
              <tr>
                <th>Promised Deliverable</th>
                <th>Google / Rocket Lead</th>
                <th>How to Access / Action Required</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>
                  <div class="tbl-strong">500 Gemini Enterprise Licenses (1-Month Trial)</div>
                  <div class="mono tbl-code">Gemini Enterprise App + Deep Research + Agent Workbench</div>
                </td>
                <td class="tbl-desc"><strong>Angela Kavanaugh</strong> (<code class="lg-inline-code">akavanaugh@google.com</code>)<br><strong>Luis Lopez</strong> (<code class="lg-inline-code">luislopez@google.com</code>)</td>
                <td class="tbl-desc">500 licenses approved for 1 month. Join <strong>Luis Lopez’s Office Hours</strong> to see how to register custom agents in the Gemini Enterprise App.</td>
              </tr>
              <tr>
                <td>
                  <div class="tbl-strong">5-Pillar Demo Code &amp; BigQuery TimesFM 2.0 Dataset</div>
                  <div class="mono tbl-code">vtxdemos.rocket_nextgen_timesfm + 108-Home Vector Index</div>
                </td>
                <td class="tbl-desc"><strong>Jesus Chavez</strong> (<code class="lg-inline-code">jesusarguelles@google.com</code>)</td>
                <td class="tbl-desc">Clone <a href="{GITHUB_ROOT_URL}" target="_blank" class="tbl-link">vertex-ai-samples/semiautonomous-agents/rocket ↗</a> (includes standalone <code class="lg-inline-code">SKILL.md</code> &amp; <code class="lg-inline-code">.env.example</code> per pillar). Ping Jesus for BigQuery dataset reader access.</td>
              </tr>
              <tr>
                <td>
                  <div class="tbl-strong">GECX Contact Center Studio &amp; <code class="lg-inline-code">cxas-scrappy</code> CLI</div>
                  <div class="mono tbl-code">Customer Experience Agent Studio + PRD-to-Agent Hill-Climbing</div>
                </td>
                <td class="tbl-desc"><strong>Ricky Merrefield</strong> (<code class="lg-inline-code">rmerrefield@google.com</code>)<br><strong>Steven Roberts</strong></td>
                <td class="tbl-desc">Launch <a href="{GECX_LAUNCHPAD_URL}" target="_blank" class="tbl-link">GECX Launchpad ↗</a> and <a href="{GECX_CONSOLE_URL}" target="_blank" class="tbl-link">ces.cloud.google.com ↗</a> to build voice/chat concierge agents with warm banker transfers.</td>
              </tr>
              <tr>
                <td>
                  <div class="tbl-strong">Rocket Internal MCP, MyAccess &amp; GCP PAM Entitlements</div>
                  <div class="mono tbl-code">Project: dev-233554-hllwn26-hack-f1f8</div>
                </td>
                <td class="tbl-desc"><strong>Jeremy Drager</strong> (<code class="lg-inline-code">jeremydrager@rocket.com</code>)<br><strong>Jordan Peterson</strong> (<code class="lg-inline-code">jordanpeterson@rocket.com</code>)<br><strong>Nitesh Bhusal &amp; Sundar Chellappa</strong></td>
                <td class="tbl-desc">Antigravity VS Code extension is approved. For GCP quota/auth or internal Rocket MCP access during Oct 28–29, request PAM grant or contact Rocket GCP admins.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </div>

    <!-- ========================================================================
         TAB 3: DYNAMIC AI GLOSSARY & BEGINNER LAUNCHPAD (INTERACTIVE + /glossary APP)
         ======================================================================== -->
    <div id="tab-pane-glossary" class="portal-tab-pane">
      <div class="liquid-card" style="padding:14px 18px;margin-bottom:14px;display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:12px;">
        <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;">
          <span class="lg-badge lg-badge-crimson">NEW · INTERACTIVE BEGINNER-TO-ARCHITECT LAUNCHPAD</span>
          <span style="font-size:13px;font-weight:700;color:var(--text-primary);">
            Available right here in Tab 3 OR as a dedicated full-screen Web App tab (`GET /glossary`)
          </span>
        </div>
        <div style="display:flex;gap:8px;flex-wrap:wrap;">
          <a href="/glossary?auth_token={auth_token}" target="_blank" class="lg-btn lg-btn-primary sm">
            {_svg("external_link", 14)}
            Open Standalone Glossary Web App (/glossary)
          </a>
          <a href="{GLOSSARY_DOC_URL}" target="_blank" class="lg-btn lg-btn-glass sm">
            {_svg("doc_blueprint", 14)}
            3-Tab Printable Google Doc
          </a>
        </div>
      </div>
      {render_dynamic_glossary_tab_html(auth_token)}
    </div>

    <!-- ========================================================================
         TAB 4: REFERENCE LIBRARY (33 DEPARTMENTAL CONSULTANCY BLUEPRINTS)
         ======================================================================== -->
    <div id="tab-pane-archive" class="portal-tab-pane">
      <div class="liquid-card filter-toolbar">
        <div class="search-input-wrap">
          <span style="color:var(--text-muted);display:inline-flex;">{_svg("search", 16)}</span>
          <input id="archive-search-input" type="text"
                 placeholder="Filter 33 domain blueprints by code, title, or keyword (e.g. '2.1', 'Form 1084', 'TRID', 'escrow', 'CodeMender')…"
                 oninput="filterArchiveBlueprints()">
        </div>
        <div class="filter-pills-row">
          <button type="button" class="filter-pill-btn active" data-archive-dept="all" onclick="filterArchiveBlueprints('all')">All (33)</button>
          <button type="button" class="filter-pill-btn" data-archive-dept="sales" onclick="filterArchiveBlueprints('sales')">Origination</button>
          <button type="button" class="filter-pill-btn" data-archive-dept="ops" onclick="filterArchiveBlueprints('ops')">Underwriting</button>
          <button type="button" class="filter-pill-btn" data-archive-dept="servicing" onclick="filterArchiveBlueprints('servicing')">Servicing</button>
          <button type="button" class="filter-pill-btn" data-archive-dept="marketing" onclick="filterArchiveBlueprints('marketing')">Marketing</button>
          <button type="button" class="filter-pill-btn" data-archive-dept="risk" onclick="filterArchiveBlueprints('risk')">Risk &amp; TRID</button>
          <button type="button" class="filter-pill-btn" data-archive-dept="sdlc" onclick="filterArchiveBlueprints('sdlc')">SDLC</button>
          <button type="button" class="filter-pill-btn" data-archive-dept="moonshots" onclick="filterArchiveBlueprints('moonshots')">Moonshots</button>
        </div>
      </div>

      <section>
        <div class="section-hdr">
          <div>
            <span class="lg-badge lg-badge-purple">TIER 4 · SECONDARY CONSULTANCY ARCHIVE</span>
            <h2 class="section-title" style="margin-top:6px;">33 Departmental Domain Blueprints &amp; Deterministic Sandboxes</h2>
            <p class="section-sub">Conceptual L100–L300 domain patterns preserved for reference without cluttering the primary hackathon studios.</p>
          </div>
          <span id="archive-visible-count" class="lg-chip mono">33 Blueprints Shown</span>
        </div>
        <div class="archive-grid">
          {"".join(archive_cards_html)}
        </div>
      </section>
    </div>
  </main>

  <!-- UNIFIED 3X RETINA ARCHITECTURE & 5-BLOCK FLOW LIGHTBOX MODAL -->
  <div id="portal-diagram-lightbox" class="diagram-lightbox" onclick="if(event.target===this)closeDiagramLightbox()">
    <div class="lightbox-inner">
      <div class="lightbox-hdr" style="flex-wrap:wrap;gap:10px;">
        <span id="portal-lightbox-title" style="font-size:15px;font-weight:800;">3x Retina Architecture Blueprint</span>
        <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
          <div id="portal-lightbox-mode-pills" style="display:none;gap:6px;align-items:center;">
            <button type="button" id="lightbox-btn-arch" class="filter-pill-btn active" onclick="switchLightboxView('arch')">1. 3x GCP Architecture</button>
            <button type="button" id="lightbox-btn-walk" class="filter-pill-btn" onclick="switchLightboxView('walk')">2. 5-Block Component Flow</button>
            <a id="lightbox-github-link" href="#" target="_blank" class="lg-btn lg-btn-glass sm" style="text-decoration:none;color:#0F172A;border-color:rgba(15,23,42,0.16);">
              {_svg("github_code", 14)}
              GitHub &amp; SKILL.md
            </a>
          </div>
          <button type="button" class="lg-btn lg-btn-primary sm" onclick="closeDiagramLightbox()">{_svg("close", 14)} Close</button>
        </div>
      </div>
      <img id="portal-lightbox-img" src="" alt="Full Resolution Architecture Diagram">
    </div>
  </div>

  <script>
    window.PORTAL_AUTH_TOKEN = {json.dumps(auth_token)};
    window.PORTAL_SVG = {json.dumps(SVG_ICONS)};
  </script>
  <link rel="stylesheet" href="/static/support_overlay.css">
  <script src="/static/live_session.js"></script>
  <script src="/static/portal_liquid_glass.js"></script>
  <script src="/static/glossary_launchpad.js"></script>
  <script src="/static/support_overlay.js"></script>
  <script src="/static/portal_telemetry.js"></script>
</body>
</html>"""


def render_docs_page_html(code: str, auth_token: str) -> str:
    """Renders the step-by-step reproduction blueprint for any square in matching Apple Liquid Glass style,
    with direct links to that demo's dedicated standalone GitHub repository (separated from the 5-Pillar repo)."""
    p = PROJECTS_BY_CODE.get(code) or PROJECTS_BY_CODE["1.4"]
    cfg = get_bespoke_config(p["code"])
    route_info = get_recommended_model_for_square(p["code"])

    ded_repo_url = p.get("github_repo_url", GITHUB_ROOT_URL)
    ded_blob_base = p.get("github_blob_base", GITHUB_ROOT_URL)
    ded_skill_url = p.get("github_skill_url", GITHUB_ROOT_URL)
    ded_repo_rel = p.get("github_repo_rel", "")
    code_slug = p["code"].lower().replace(".", "_")

    steps_html = "".join(
        f'<li style="padding:12px 14px;border-radius:12px;background:rgba(255,255,255,0.65);border:1px solid rgba(15,23,42,0.08);font-size:13.5px;">'
        f'<strong style="color:#D81E28;font-family:monospace;margin-right:8px;">STEP {idx + 1}:</strong> {_html.escape(step)}</li>'
        for idx, step in enumerate(p.get("reproSteps", []))
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Blueprint [{_html.escape(p['code'])}] {_html.escape(p['project'])} | Rocket × Google Cloud</title>
  <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: 'Plus Jakarta Sans', sans-serif;
      background: linear-gradient(180deg, #F6F8FC 0%, #E9EEF8 100%);
      color: #0F172A;
      min-height: 100vh;
      padding: 24px;
    }}
    .mono {{ font-family: 'JetBrains Mono', monospace; }}
    .lg-svg-icon {{
      width: 16px;
      height: 16px;
      display: inline-block;
      vertical-align: -0.18em;
      flex-shrink: 0;
      stroke: currentColor;
      fill: none;
    }}
    .wrap {{ max-width: 1120px; margin: 0 auto; display: flex; flex-direction: column; gap: 20px; }}
    .glass-card {{
      background: rgba(255, 255, 255, 0.86);
      backdrop-filter: blur(24px);
      border: 1px solid rgba(255, 255, 255, 0.9);
      outline: 1px solid rgba(15, 23, 42, 0.08);
      border-radius: 22px;
      padding: 24px;
      box-shadow: 0 20px 44px -14px rgba(15, 23, 42, 0.08);
    }}
    .btn {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 9px 15px;
      border-radius: 12px;
      font-size: 12.5px;
      font-weight: 700;
      text-decoration: none;
      border: 1px solid rgba(15, 23, 42, 0.12);
      background: #FFFFFF;
      color: #0F172A;
    }}
    .btn-primary {{ background: #D81E28; color: #FFFFFF; border-color: #D81E28; }}
    .btn-blue {{ background: #0066CC; color: #FFFFFF; border-color: #0066CC; }}
    pre {{
      background: #0B0F19;
      color: #E2E8F0;
      padding: 16px;
      border-radius: 14px;
      font-family: 'JetBrains Mono', monospace;
      font-size: 12px;
      line-height: 1.55;
      overflow-x: auto;
    }}
    .repo-table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 13px;
      margin-top: 10px;
    }}
    .repo-table th {{
      text-align: left;
      padding: 10px 12px;
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: #64748B;
      border-bottom: 1px solid rgba(15, 23, 42, 0.1);
    }}
    .repo-table td {{
      padding: 10px 12px;
      border-bottom: 1px solid rgba(15, 23, 42, 0.06);
      color: #334155;
    }}
    .repo-table a {{
      color: #0066CC;
      font-weight: 700;
      text-decoration: none;
      font-family: 'JetBrains Mono', monospace;
    }}
    .repo-table a:hover {{ text-decoration: underline; }}
  </style>
</head>
<body>
  <div class="wrap">
    <div class="glass-card" style="display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:12px;padding:16px 22px;">
      <a href="/?auth_token={auth_token}&tab=archive" class="btn">{_svg("arrow_left", 15)} Back to Reference Library (33)</a>
      <div style="display:flex;gap:8px;flex-wrap:wrap;">
        <a href="{_html.escape(ded_repo_url)}" target="_blank" class="btn btn-blue">{_svg("github_code", 15)} Dedicated GitHub Repo [{_html.escape(p['code'])}]</a>
        <a href="{_html.escape(ded_skill_url)}" target="_blank" class="btn">{_svg("doc_blueprint", 15)} SKILL.md [{_html.escape(p['code'])}]</a>
        <a href="/square/{p['code']}?auth_token={auth_token}" class="btn btn-primary">{_svg("play", 15)} Launch Interactive Sandbox [{_html.escape(p['code'])}]</a>
      </div>
    </div>

    <div class="glass-card">
      <div class="mono" style="font-size:11px;font-weight:700;color:#D81E28;margin-bottom:6px;">
        SQUARE {_html.escape(p['code'])} · {_html.escape(p['level'])} · {_html.escape(p['dept_full'])}
      </div>
      <h1 style="font-size:28px;font-weight:800;letter-spacing:-0.02em;margin-bottom:8px;">{_html.escape(p['project'])}</h1>
      <p style="font-size:14.5px;color:#334155;line-height:1.6;margin-bottom:14px;">{_html.escape(p['desc'])}</p>
      <div class="mono" style="font-size:12px;color:#0066CC;display:flex;flex-wrap:wrap;gap:14px;align-items:center;">
        <span>Recommended 2026 Model Routing: <strong>{_html.escape(route_info['runtime_badge'])}</strong></span>
        <span>·</span>
        <span>UI Archetype: <strong>{_html.escape(cfg['ui_archetype'])}</strong></span>
        <span>·</span>
        <span>Dedicated Repo: <a href="{_html.escape(ded_repo_url)}" target="_blank" style="color:#D81E28;font-weight:700;">rocket-ai-hackathon-argon-suite/{_html.escape(ded_repo_rel)} ↗</a></span>
      </div>
    </div>

    <div class="glass-card">
      <div style="display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:10px;margin-bottom:8px;">
        <div>
          <div class="mono" style="font-size:11px;font-weight:700;color:#059669;">ISOLATED STANDALONE MICROSERVICE REPOSITORY (SEPARATED FROM 5-PILLAR STUDIO)</div>
          <h2 style="font-size:16px;font-weight:800;margin-top:2px;">1. Dedicated GitHub Repository &amp; Source Files (`Square {_html.escape(p['code'])}`)</h2>
        </div>
        <a href="{_html.escape(ded_repo_url)}" target="_blank" class="btn btn-blue">{_svg("github_code", 15)} Open Square [{_html.escape(p['code'])}] Folder on GitHub</a>
      </div>
      <table class="repo-table">
        <thead>
          <tr>
            <th>Source File in Dedicated Repo</th>
            <th>Architectural Role</th>
            <th>Runtime / Stack</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><a href="{_html.escape(ded_blob_base)}/app.py" target="_blank">app.py ↗</a></td>
            <td>Standalone FastAPI server (`PORT=8080`) serving the bespoke UI + `/api/sandbox` + `/api/run`</td>
            <td class="mono">FastAPI · Uvicorn</td>
          </tr>
          <tr>
            <td><a href="{_html.escape(ded_blob_base)}/code/agent.py" target="_blank">code/agent.py ↗</a></td>
            <td>Structured Vertex AI GenAI runner combining deterministic sandbox metrics with LLM synthesis</td>
            <td class="mono">{_html.escape(route_info.get('default_model', 'gemini-4-argon'))}</td>
          </tr>
          <tr>
            <td><a href="{_html.escape(ded_blob_base)}/code/sandbox_tool.py" target="_blank">code/sandbox_tool.py ↗</a></td>
            <td>Deterministic Python gVisor calculation verifier &amp; bespoke visual artifact builder</td>
            <td class="mono">Python 3.12</td>
          </tr>
          <tr>
            <td><a href="{_html.escape(ded_blob_base)}/ui/sq_{_html.escape(code_slug)}.py" target="_blank">ui/sq_{_html.escape(code_slug)}.py ↗</a> &amp; <a href="{_html.escape(ded_blob_base)}/ui/standalone_app.html" target="_blank">ui/standalone_app.html ↗</a></td>
            <td>Custom UI renderer &amp; pre-rendered standalone HTML app for `{_html.escape(cfg['ui_archetype'])}`</td>
            <td class="mono">HTML5 / CSS3 / JS</td>
          </tr>
          <tr>
            <td><a href="{_html.escape(ded_blob_base)}/SKILL.md" target="_blank">SKILL.md ↗</a> &amp; <a href="{_html.escape(ded_blob_base)}/README.md" target="_blank">README.md ↗</a></td>
            <td>Reusable Antigravity / Gemini CLI skill contract &amp; standalone documentation</td>
            <td class="mono">Antigravity Skill</td>
          </tr>
          <tr>
            <td><a href="{_html.escape(ded_blob_base)}/Dockerfile" target="_blank">Dockerfile ↗</a>, <a href="{_html.escape(ded_blob_base)}/requirements.txt" target="_blank">requirements.txt ↗</a> &amp; <a href="{_html.escape(ded_blob_base)}/mock_data/sample_payload.json" target="_blank">sample_payload.json ↗</a></td>
            <td>1-command Cloud Run container definition &amp; verified mortgage/servicing test dataset</td>
            <td class="mono">Cloud Run</td>
          </tr>
        </tbody>
      </table>
      <pre style="margin-top:14px;"># Clone &amp; run ONLY Square [{_html.escape(p['code'])}] ({_html.escape(p['project'])}) standalone:
git clone https://github.com/jchavezar/vertex-ai-samples.git
cd vertex-ai-samples/semiautonomous-agents/rocket-ai-hackathon-argon-suite/{_html.escape(ded_repo_rel)}
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 8080</pre>
    </div>

    <div class="glass-card">
      <h2 style="font-size:16px;font-weight:800;margin-bottom:12px;">2. Step-by-Step GCP Reproduction Guide</h2>
      <ol style="list-style:none;display:flex;flex-direction:column;gap:8px;">{steps_html}</ol>
    </div>

    <div class="glass-card">
      <h2 style="font-size:16px;font-weight:800;margin-bottom:12px;">3. Reference Architecture &amp; Implementation Snippet</h2>
      <pre style="margin-bottom:14px;">{_html.escape(p['architectureDiagram'])}</pre>
      <pre>{_html.escape(p['codeSnippet'])}</pre>
    </div>
  </div>
</body>
</html>"""
