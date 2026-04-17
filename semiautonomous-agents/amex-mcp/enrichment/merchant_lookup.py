"""Stage 0: Merchant identification via Gemini + Google Search grounding.

Deduplicates raw merchant descriptions, searches the web for each unique
merchant, and builds a lookup dict so the categorizer has accurate context.
"""

import asyncio
import json
import logging
import os
import re

from google import genai
from google.genai import types

logger = logging.getLogger("amex-mcp.merchant-lookup")

PROJECT = os.environ.get("GCP_PROJECT_ID", "vtxdemos")
LOCATION = "global"
MODEL = os.environ.get("ENRICHMENT_MODEL", "gemini-3.1-flash-lite-preview")

_search_client = None
_semaphore = asyncio.Semaphore(5)


def _get_search_client() -> genai.Client:
    """Client with Google Search grounding support."""
    global _search_client
    if _search_client is None:
        _search_client = genai.Client(
            vertexai=True, project=PROJECT, location=LOCATION
        )
    return _search_client


def _extract_unique_merchants(transactions: list[dict]) -> dict[str, dict]:
    """Deduplicate raw descriptions into unique merchant keys.

    Returns a dict mapping a normalized key to a representative transaction.
    """
    seen = {}
    for txn in transactions:
        desc = txn.get("description", "").strip()
        if not desc:
            continue
        # Normalize: strip payment prefixes, collapse whitespace
        key = re.sub(r"^(AplPay|GglPay|SQ \*)\s*", "", desc)
        key = re.sub(r"\s+", " ", key).strip()[:40]  # first 40 chars
        if key not in seen:
            seen[key] = {
                "raw_description": desc,
                "amount": txn.get("amount", 0),
                "date": txn.get("date", ""),
            }
    return seen


LOOKUP_PROMPT = """\
Identify this business from a credit card statement. The description is \
abbreviated and truncated — credit card processors shorten merchant names \
heavily (e.g., "WHOLEFDS MHW#" = Whole Foods Market, "LHR UNION SQU" = \
Lenox Hill Radiology at Union Square).

Raw credit card description: "{raw_description}"
Amount: ${amount}
Date: {date}

IMPORTANT:
- The description is often truncated to ~20 chars. "LHR" could be an acronym, \
abbreviation, or first letters of a business name.
- Look for embedded phone numbers (e.g., "212-9968000") and search those too.
- Look for location hints (city, state abbreviations like NY, CA).
- Consider the amount — $928 at "LHR UNION SQU" is more likely a medical \
facility or professional service than a restaurant.
- Search Google for the abbreviation + location + phone number to find the \
real business.

Return JSON:
{{"merchant_name": "the real full business name", \
"business_description": "one-line description of what they do", \
"category_hint": "one of: Dining, Groceries, Transportation, Travel, Shopping, \
Entertainment, Health, Utilities, Subscriptions, Insurance, Education, \
Personal Care, Home, Gifts, Fees, Other", \
"subcategory_hint": "more specific label", \
"merchant_type_hint": "one of: chain, local, online, service, government, unknown"}}
"""


async def _lookup_merchant(key: str, info: dict) -> tuple[str, dict]:
    """Look up a single merchant using Gemini + Google Search grounding."""
    prompt = LOOKUP_PROMPT.format(
        raw_description=info["raw_description"],
        amount=info["amount"],
        date=info["date"],
    )

    config = types.GenerateContentConfig(
        response_mime_type="application/json",
        tools=[types.Tool(google_search=types.GoogleSearch())],
    )

    async with _semaphore:
        try:
            client = _get_search_client()
            response = await asyncio.to_thread(
                client.models.generate_content,
                model=MODEL,
                contents=prompt,
                config=config,
            )
            text = response.text.strip()
            result = json.loads(text)
            logger.info(json.dumps({
                "event": "merchant_identified",
                "key": key,
                "merchant": result.get("merchant_name", ""),
                "category": result.get("category_hint", ""),
            }))
            return key, result
        except Exception as e:
            logger.warning(json.dumps({
                "event": "merchant_lookup_failed",
                "key": key,
                "error": str(e),
            }))
            return key, {}


async def lookup_merchants(transactions: list[dict]) -> dict[str, dict]:
    """Identify all unique merchants via web search.

    Returns a dict mapping normalized merchant keys to lookup results:
    {
        "LHR UNION SQU212-9968000": {
            "merchant_name": "LHR - Brain Health",
            "business_description": "Neurofeedback and brain scanning clinic",
            "category_hint": "Health",
            "subcategory_hint": "Brain Health/Neurofeedback",
            "merchant_type_hint": "service"
        },
        ...
    }
    """
    unique = _extract_unique_merchants(transactions)
    logger.info(json.dumps({
        "event": "merchant_lookup_started",
        "total_transactions": len(transactions),
        "unique_merchants": len(unique),
    }))

    tasks = [_lookup_merchant(key, info) for key, info in unique.items()]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    lookup = {}
    for result in results:
        if isinstance(result, Exception):
            continue
        key, data = result
        if data:
            lookup[key] = data

    logger.info(json.dumps({
        "event": "merchant_lookup_completed",
        "identified": len(lookup),
        "total": len(unique),
    }))
    return lookup


def match_lookup(description: str, lookup: dict[str, dict]) -> dict | None:
    """Find the best matching lookup result for a transaction description."""
    desc = re.sub(r"^(AplPay|GglPay|SQ \*)\s*", "", description.strip())
    desc = re.sub(r"\s+", " ", desc).strip()[:40]
    return lookup.get(desc)
