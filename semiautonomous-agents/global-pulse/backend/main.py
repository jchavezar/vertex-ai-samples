"""
Global Pulse — FastAPI backend.

Endpoints:
  POST /api/investigate   – Main news investigation
  POST /api/deep-analysis – Deep dive on a topic
  GET  /api/health        – Health check
"""

from __future__ import annotations

import json
import logging
import os
import sys
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Add project root to path so imports work
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.veracity_engine import (
    COUNTRY_FLAGS,
    compute_diversity_radar,
    compute_veracity_score,
    detect_signals,
    enrich_source,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Global Pulse API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------

class InvestigateRequest(BaseModel):
    query: str
    max_iterations: int = 3


class DeepAnalysisRequest(BaseModel):
    query: str
    source_url: str = ""


# ---------------------------------------------------------------------------
# Mock data for development
# ---------------------------------------------------------------------------

MOCK_SOURCES = [
    {"source_name": "Reuters", "country": "United Kingdom", "country_code": "GB", "language_original": "English",
     "headline": "EU reaches landmark agreement on comprehensive AI regulation framework",
     "summary": "The European Union has finalized its AI Act, establishing the world's first comprehensive legal framework for artificial intelligence. The regulation introduces a risk-based approach that categorizes AI systems and imposes obligations accordingly.",
     "url": "https://www.reuters.com/technology/eu-ai-act-2025", "image_url": None, "published_date": "2025-06-15", "signal_type": "CONFIRMED"},
    {"source_name": "Le Monde", "country": "France", "country_code": "FR", "language_original": "French",
     "headline": "L'UE adopte le règlement sur l'intelligence artificielle — A historic step for digital sovereignty",
     "summary": "Le Monde reports that France played a key mediating role in the final negotiations, balancing innovation interests with citizen protection. French tech companies express cautious optimism about the framework.",
     "url": "https://www.lemonde.fr/tech/ai-regulation", "image_url": None, "published_date": "2025-06-15", "signal_type": "CONFIRMED"},
    {"source_name": "NHK", "country": "Japan", "country_code": "JP", "language_original": "Japanese",
     "headline": "EU AI regulation draws attention from Japanese tech sector — implications for global standards",
     "summary": "NHK World reports Japanese technology firms are closely monitoring the EU's AI Act, as it may set a precedent for similar regulations in Asia. Japan's METI is studying the framework for potential adoption.",
     "url": "https://www3.nhk.or.jp/news/ai-eu", "image_url": None, "published_date": "2025-06-16", "signal_type": "ANALYSIS"},
    {"source_name": "Al Jazeera", "country": "Qatar", "country_code": "QA", "language_original": "English",
     "headline": "EU AI Act: What developing nations need to know about the global ripple effects",
     "summary": "Al Jazeera examines how the EU's regulatory approach could impact developing economies that rely on AI tools for growth. Experts warn of a potential 'regulatory divide' between the Global North and South.",
     "url": "https://www.aljazeera.com/tech/eu-ai-developing", "image_url": None, "published_date": "2025-06-16", "signal_type": "ANALYSIS"},
    {"source_name": "Der Spiegel", "country": "Germany", "country_code": "DE", "language_original": "German",
     "headline": "KI-Gesetz der EU: Deutschland setzt auf Innovation trotz strenger Regeln",
     "summary": "Der Spiegel reports that German industry leaders have mixed reactions. While supporting safety guardrails, they worry the regulation could slow down European competitiveness against US and Chinese AI firms.",
     "url": "https://www.spiegel.de/tech/ki-gesetz-eu", "image_url": None, "published_date": "2025-06-15", "signal_type": "DEVELOPING"},
    {"source_name": "The Hindu", "country": "India", "country_code": "IN", "language_original": "English",
     "headline": "India studies EU AI Act as template for own regulatory framework",
     "summary": "India's IT ministry is examining the EU's risk-based approach to AI regulation as it drafts its own Digital India AI framework. Officials note the need to balance innovation with protection in a developing economy context.",
     "url": "https://www.thehindu.com/tech/india-ai-regulation", "image_url": None, "published_date": "2025-06-17", "signal_type": "DEVELOPING"},
    {"source_name": "BBC", "country": "United Kingdom", "country_code": "GB", "language_original": "English",
     "headline": "EU AI Act explained: What it means for tech companies worldwide",
     "summary": "The BBC provides a comprehensive overview of the EU AI Act's key provisions, including the ban on social scoring, restrictions on biometric surveillance, and transparency requirements for generative AI systems.",
     "url": "https://www.bbc.com/news/technology/eu-ai-act", "image_url": None, "published_date": "2025-06-15", "signal_type": "CONFIRMED"},
    {"source_name": "South China Morning Post", "country": "Hong Kong", "country_code": "HK", "language_original": "English",
     "headline": "China's tech giants brace for EU AI rules as market access hangs in balance",
     "summary": "SCMP reports that Chinese AI companies including Baidu and Alibaba are scrambling to comply with the new EU regulations to maintain access to the European market, one of their largest overseas revenue sources.",
     "url": "https://www.scmp.com/tech/china-eu-ai", "image_url": None, "published_date": "2025-06-16", "signal_type": "DEVELOPING"},
    {"source_name": "El País", "country": "Spain", "country_code": "ES", "language_original": "Spanish",
     "headline": "La ley de IA de la UE marca un antes y un después en la regulación tecnológica",
     "summary": "El País reports Spain's technology sector views the regulation positively, noting it could attract AI safety companies to establish European headquarters in Barcelona and Madrid.",
     "url": "https://elpais.com/tecnologia/ley-ia-ue", "image_url": None, "published_date": "2025-06-15", "signal_type": "CONFIRMED"},
    {"source_name": "Nikkei Asia", "country": "Japan", "country_code": "JP", "language_original": "English",
     "headline": "EU AI regulation creates opportunities for Asian compliance tech firms",
     "summary": "Nikkei Asia reports that AI governance and compliance startups across Asia are seeing increased interest from European clients seeking help to meet the new regulatory requirements.",
     "url": "https://asia.nikkei.com/Business/eu-ai-asia-compliance", "image_url": None, "published_date": "2025-06-17", "signal_type": "ANALYSIS"},
    {"source_name": "Deutsche Welle", "country": "Germany", "country_code": "DE", "language_original": "English",
     "headline": "EU AI Act: Balancing innovation and regulation in the age of artificial intelligence",
     "summary": "DW reports on the political compromise that made the AI Act possible, highlighting the tensions between tech-friendly Nordic countries and more regulation-minded Southern European states.",
     "url": "https://www.dw.com/en/eu-ai-act-balance", "image_url": None, "published_date": "2025-06-16", "signal_type": "ANALYSIS"},
    {"source_name": "The Globe and Mail", "country": "Canada", "country_code": "CA", "language_original": "English",
     "headline": "Canada looks to EU AI Act as blueprint for its own artificial intelligence legislation",
     "summary": "The Globe and Mail reports that Canadian lawmakers are using the EU framework as a reference point, particularly its risk categorization system, as they develop the Artificial Intelligence and Data Act.",
     "url": "https://www.theglobeandmail.com/tech/canada-ai-legislation", "image_url": None, "published_date": "2025-06-17", "signal_type": "DEVELOPING"},
    {"source_name": "O Globo", "country": "Brazil", "country_code": "BR", "language_original": "Portuguese",
     "headline": "Regulação europeia de IA pode impactar startups brasileiras que exportam tecnologia",
     "summary": "O Globo examines how Brazilian AI startups that export services to Europe will need to adapt to the new regulatory requirements, with some viewing compliance as a competitive advantage.",
     "url": "https://oglobo.globo.com/tecnologia/ia-regulacao-eu-brasil", "image_url": None, "published_date": "2025-06-16", "signal_type": "DEVELOPING"},
    {"source_name": "Haaretz", "country": "Israel", "country_code": "IL", "language_original": "Hebrew",
     "headline": "Israeli AI companies prepare for EU regulation — cybersecurity sector sees opportunity",
     "summary": "Haaretz reports that Israel's robust AI cybersecurity sector sees the EU AI Act as a business opportunity, with several firms already offering compliance-as-a-service solutions to European clients.",
     "url": "https://www.haaretz.com/israel-news/tech/ai-eu-regulation", "image_url": None, "published_date": "2025-06-17", "signal_type": "ANALYSIS"},
    {"source_name": "The Straits Times", "country": "Singapore", "country_code": "SG", "language_original": "English",
     "headline": "Singapore's AI governance framework compared favorably to new EU regulation",
     "summary": "The Straits Times notes that Singapore's existing Model AI Governance Framework shares principles with the EU AI Act, positioning the city-state well for regulatory alignment and cross-border AI trade.",
     "url": "https://www.straitstimes.com/tech/singapore-eu-ai-governance", "image_url": None, "published_date": "2025-06-16", "signal_type": "CONFIRMED"},
    {"source_name": "Daily Nation", "country": "Kenya", "country_code": "KE", "language_original": "English",
     "headline": "African Union calls for inclusive AI regulation following EU's landmark act",
     "summary": "Daily Nation reports on the African Union's response to the EU AI Act, with AU officials calling for a framework that considers the unique challenges and opportunities of AI deployment in African contexts.",
     "url": "https://nation.africa/kenya/news/au-ai-regulation-eu", "image_url": None, "published_date": "2025-06-17", "signal_type": "DEVELOPING"},
    {"source_name": "Associated Press", "country": "United States", "country_code": "US", "language_original": "English",
     "headline": "EU finalizes world's first comprehensive AI law, setting global benchmark",
     "summary": "The AP reports on the final vote and key provisions of the EU AI Act, noting bipartisan interest in the US Congress to study the European approach as a model for potential American AI legislation.",
     "url": "https://apnews.com/article/eu-ai-act-regulation", "image_url": None, "published_date": "2025-06-15", "signal_type": "CONFIRMED"},
]

MOCK_RESULT = {
    "query": "EU AI regulation impact",
    "concise_answer": (
        "The European Union has finalized the AI Act, the world's first comprehensive legal framework for artificial intelligence, "
        "adopting a risk-based classification system. The regulation is drawing global attention, with countries from Japan to Canada "
        "studying it as a potential model. While welcomed for its safety provisions, industry groups across Europe and Asia express "
        "concerns about potential impacts on competitiveness and innovation speed."
    ),
    "report": """## Key Findings

The EU AI Act represents a watershed moment in technology regulation, establishing the first legally binding framework for artificial intelligence globally. The regulation adopts a **risk-based approach**, categorizing AI systems into four tiers: unacceptable risk (banned), high risk (strict obligations), limited risk (transparency requirements), and minimal risk (no restrictions).

## Regional Perspectives

### Europe
European reactions are mixed. While France and Germany supported the framework, industry leaders in both countries worry about competitiveness against US and Chinese firms. Southern European nations, particularly Spain, view the regulation as an opportunity to attract AI safety companies.

### Asia-Pacific
Japan, Singapore, and India are actively studying the EU framework. Japanese tech firms are monitoring implications for global standards, while Singapore's existing governance framework positions it well for alignment. India is using the EU model as a template for its own Digital India AI framework.

### Middle East & Africa
Al Jazeera highlights concerns about a 'regulatory divide' between developed and developing nations. The African Union has called for inclusive frameworks that consider African contexts. Israel's cybersecurity sector sees compliance-as-a-service as a business opportunity.

### Americas
The US Congress is studying the European approach with bipartisan interest. Canada is using the EU framework as a blueprint for its Artificial Intelligence and Data Act. Brazilian tech startups that export to Europe are preparing for compliance requirements.

## Points of Consensus

- The AI Act sets a **global benchmark** that other jurisdictions will follow or adapt
- A risk-based approach is the most pragmatic regulatory framework
- Transparency requirements for generative AI are widely supported
- The ban on social scoring and certain biometric surveillance is appropriate

## Points of Disagreement

- Whether the regulation is too restrictive for European innovation
- Impact on developing economies that depend on AI tools for growth
- Speed of implementation timelines
- Whether similar regulations should be adopted in Asia

## Analysis

The EU AI Act marks a decisive shift from voluntary AI ethics guidelines to enforceable law. Its extraterritorial reach — applying to any AI system used in the EU market — means global companies must comply regardless of where they are headquartered. This "Brussels Effect" is likely to shape AI governance worldwide, similar to how GDPR influenced global data protection standards.

The regulation's impact will depend heavily on implementation and enforcement. The EU AI Office, tasked with oversight, will need to balance strict compliance with practical flexibility. The coming 24-month implementation period will be crucial in determining whether the Act achieves its dual goals of promoting innovation while protecting fundamental rights.""",
    "sources": MOCK_SOURCES,
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _use_mock() -> bool:
    return os.getenv("USE_MOCK_DATA", "false").lower() in ("true", "1", "yes")


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "global-pulse", "mock_mode": _use_mock()}


@app.post("/api/investigate")
async def investigate(req: InvestigateRequest):
    if _use_mock():
        logger.info("Returning mock data for query: %s", req.query)
        result = {**MOCK_RESULT, "query": req.query}
        sources = [enrich_source(dict(s)) for s in result["sources"]]
        veracity = compute_veracity_score(sources)
        radar = compute_diversity_radar(sources)
        signals = detect_signals(sources)
        return {
            **result,
            "sources": sources,
            "veracity": veracity,
            "radar": radar,
            "signals": signals,
            "metadata": {
                "total_sources": len(sources),
                "countries_covered": len({s["country_code"] for s in sources}),
                "languages": list({s.get("language_original", "English") for s in sources}),
                "search_iterations": 3,
            },
        }

    # --- Live mode ---
    try:
        from agent.agent import investigate_topic

        raw = await investigate_topic(req.query, num_iterations=req.max_iterations)
        sources = [enrich_source(dict(s)) for s in raw.get("sources", [])]
        veracity = compute_veracity_score(sources)
        radar = compute_diversity_radar(sources)
        signals = detect_signals(sources)

        return {
            "query": req.query,
            "concise_answer": raw.get("concise_answer", ""),
            "report": raw.get("report", ""),
            "sources": sources,
            "veracity": veracity,
            "radar": radar,
            "signals": signals,
            "metadata": {
                "total_sources": len(sources),
                "countries_covered": len({s.get("country_code", "XX") for s in sources}),
                "languages": list({s.get("language_original", "English") for s in sources}),
                "search_iterations": raw.get("search_iterations", req.max_iterations),
            },
        }
    except Exception as e:
        logger.exception("Investigation failed")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/deep-analysis")
async def deep_analysis(req: DeepAnalysisRequest):
    """Deep dive on a specific aspect of a topic."""
    if _use_mock():
        return {
            "query": req.query,
            "analysis": "Deep analysis is available in live mode. Set USE_MOCK_DATA=false and configure your GCP project.",
        }

    try:
        from agent.agent import investigate_topic

        raw = await investigate_topic(
            f"Deep analysis: {req.query}. Focus on expert opinions, historical context, and implications.",
            num_iterations=2,
        )
        sources = [enrich_source(dict(s)) for s in raw.get("sources", [])]
        return {
            "query": req.query,
            "analysis": raw.get("report", ""),
            "sources": sources,
        }
    except Exception as e:
        logger.exception("Deep analysis failed")
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------------------
# Startup
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8888"))
    uvicorn.run("backend.main:app", host="0.0.0.0", port=port, reload=True)
