"""
Global News Research Agent — Gemini + Google Search grounding.

Persona: PhD in Communications, impartial international news expert.
Searches 15+ countries, translates non-English sources, returns structured JSON.
"""

from __future__ import annotations

import json
import logging
import os

from google import genai
from google.genai.types import (
    GenerateContentConfig,
    GoogleSearch,
    Tool,
)

logger = logging.getLogger(__name__)

PROJECT_ID = os.getenv("PROJECT_ID", "")
LOCATION = os.getenv("LOCATION", "us-central1")

SYSTEM_INSTRUCTION = """\
You are a Global News Intelligence Analyst with a PhD in Communications.

CORE IDENTITY:
- You are impartial and NEVER lean toward any political party, ideology, or nation.
- You are a researcher by nature — every claim must be grounded in verifiable reporting.
- You seek the TRUTH by cross-referencing multiple international sources.

REQUIREMENTS:
1. Search for the topic across the MOST RELEVANT international news sources.
2. You MUST include sources from at least 5 different countries and 3 different languages.
3. Prioritize sources with high journalistic standards: wire services (Reuters, AP, AFP), \
public broadcasters (BBC, NHK, DW, France 24, Al Jazeera), and respected newspapers \
(The Guardian, Le Monde, Der Spiegel, El País, The Hindu, Nikkei, Haaretz, etc.).
4. If sources are in non-English languages, translate the key information into English.
5. For EACH source, determine the signal type: BREAKING, DEVELOPING, CONFIRMED, DISPUTED, ANALYSIS.
6. Take your time — iterate your research until you have at least 15 distinct sources.

CONSTRAINTS:
- Under NO circumstance rely on only one country's or one language's news coverage.
- Do NOT include social media posts as primary sources.
- Do NOT fabricate or hallucinate URLs — only include URLs from your search results.
- Be transparent about what different sources agree and disagree on.

OUTPUT FORMAT — Return ONLY valid JSON (no markdown fencing):
{
  "concise_answer": "2-3 sentence factual summary answering the user's question",
  "report": "Detailed markdown report with sections: ## Key Findings, ## Regional Perspectives, ## Points of Consensus, ## Points of Disagreement, ## Timeline (if relevant), ## Analysis",
  "sources": [
    {
      "source_name": "Reuters",
      "country": "United Kingdom",
      "country_code": "GB",
      "language_original": "English",
      "headline": "Exact or close headline",
      "summary": "2-3 sentence summary of what this source reports",
      "url": "https://...",
      "image_url": null,
      "published_date": "2025-01-15",
      "signal_type": "CONFIRMED"
    }
  ]
}
"""

REGION_PROMPTS = [
    "Search for news about '{query}' from European sources (BBC, Guardian, Le Monde, Der Spiegel, El País, Corriere della Sera, NOS, SVT). Translate non-English headlines.",
    "Search for news about '{query}' from Asian sources (NHK, Nikkei, The Hindu, Times of India, South China Morning Post, Straits Times, Taipei Times, Dawn). Translate non-English headlines.",
    "Search for news about '{query}' from Middle Eastern and African sources (Al Jazeera, Haaretz, Daily Nation, Nation Africa). Translate non-English headlines.",
    "Search for news about '{query}' from Latin American and other sources (O Globo, El País Argentina, The Globe and Mail Canada, ABC Australia). Translate non-English headlines.",
]


def _get_client() -> genai.Client:
    return genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)


def _parse_json(text: str) -> dict | None:
    """Best-effort JSON extraction from model output."""
    text = text.strip()
    # Strip markdown code fences if present
    if text.startswith("```"):
        first_nl = text.index("\n") if "\n" in text else 3
        text = text[first_nl + 1 :]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Try to find JSON object in text
        start = text.find("{")
        end = text.rfind("}") + 1
        if start != -1 and end > start:
            try:
                return json.loads(text[start:end])
            except json.JSONDecodeError:
                pass
    return None


async def investigate_topic(query: str, num_iterations: int = 3) -> dict:
    """
    Main research function. Searches international news across multiple
    iterations and regions, then synthesizes findings.
    """
    client = _get_client()
    search_tool = Tool(google_search=GoogleSearch())
    config = GenerateContentConfig(
        tools=[search_tool],
        temperature=0.1,
        system_instruction=SYSTEM_INSTRUCTION,
    )

    all_sources: list[dict] = []
    concise_answer = ""
    report = ""

    # --- Phase 1: Broad international search ---
    logger.info("Phase 1: Broad international search for '%s'", query)
    try:
        broad_prompt = (
            f"Investigate this topic using international news sources: {query}\n\n"
            "Search across Reuters, AP, AFP, BBC, Al Jazeera, NHK, Deutsche Welle, "
            "France 24, The Guardian, Le Monde, and other major international outlets. "
            "Return at least 8 sources from at least 5 different countries."
        )
        response = await client.aio.models.generate_content(
            model="gemini-2.5-flash",
            contents=broad_prompt,
            config=config,
        )
        parsed = _parse_json(response.text)
        if parsed:
            concise_answer = parsed.get("concise_answer", "")
            report = parsed.get("report", "")
            all_sources.extend(parsed.get("sources", []))
            logger.info("Phase 1 found %d sources", len(parsed.get("sources", [])))
    except Exception as e:
        logger.error("Phase 1 search failed: %s", e)

    # --- Phase 2: Regional deep-dives ---
    iterations = min(num_iterations - 1, len(REGION_PROMPTS))
    for i in range(iterations):
        logger.info("Phase 2, iteration %d: Regional search", i + 1)
        try:
            region_prompt = (
                REGION_PROMPTS[i].format(query=query)
                + "\n\nReturn ONLY a JSON array of source objects (same schema as before). "
                "Do NOT repeat sources already found."
            )
            response = await client.aio.models.generate_content(
                model="gemini-2.5-flash",
                contents=region_prompt,
                config=config,
            )
            parsed = _parse_json(response.text)
            if parsed:
                new_sources = parsed.get("sources", [])
                if not new_sources and isinstance(parsed, list):
                    new_sources = parsed
                all_sources.extend(new_sources)
                logger.info("Region %d found %d sources", i + 1, len(new_sources))
        except Exception as e:
            logger.error("Regional search %d failed: %s", i + 1, e)

    # --- Phase 3: Synthesize final report ---
    if all_sources and (not concise_answer or not report):
        logger.info("Phase 3: Synthesizing final report")
        try:
            synth_prompt = (
                f"Based on these {len(all_sources)} sources about '{query}', write:\n"
                "1. A 'concise_answer': 2-3 sentence factual summary\n"
                "2. A 'report': detailed markdown report with sections for Key Findings, "
                "Regional Perspectives, Points of Consensus, Points of Disagreement, "
                "and Analysis.\n\n"
                f"Sources: {json.dumps(all_sources[:20], default=str)}\n\n"
                "Return JSON with 'concise_answer' and 'report' keys only."
            )
            response = await client.aio.models.generate_content(
                model="gemini-2.5-flash",
                contents=synth_prompt,
                config=GenerateContentConfig(temperature=0.2),
            )
            parsed = _parse_json(response.text)
            if parsed:
                concise_answer = parsed.get("concise_answer", concise_answer)
                report = parsed.get("report", report)
        except Exception as e:
            logger.error("Synthesis failed: %s", e)

    # Deduplicate sources by URL
    seen_urls: set[str] = set()
    unique_sources: list[dict] = []
    for s in all_sources:
        url = s.get("url", "")
        if url and url in seen_urls:
            continue
        if url:
            seen_urls.add(url)
        unique_sources.append(s)

    return {
        "concise_answer": concise_answer or "Unable to generate summary. Please try again.",
        "report": report or "Report generation failed.",
        "sources": unique_sources,
        "search_iterations": num_iterations,
    }
