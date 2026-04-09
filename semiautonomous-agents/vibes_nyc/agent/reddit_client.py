"""
Reddit signals via Gemini + Google Search grounding.
Searches for real Reddit posts about venues using the google-genai SDK.
"""
import os
import json
import re
import asyncio
from typing import Optional


async def search_venue_mentions(
    venue_name: str,
    max_results: int = 3,
) -> list[dict]:
    """
    Find real Reddit mentions of a venue using Gemini with Google Search grounding.

    Args:
        venue_name: Name of the venue to search for
        max_results: Max signals to return

    Returns:
        List of dicts with source, quote, score, url, real=True
        Empty list if no real results found.
    """
    try:
        from google import genai
        from google.genai.types import Tool, GoogleSearch, GenerateContentConfig

        client = genai.Client(
            vertexai=True,
            project=os.environ.get("GOOGLE_CLOUD_PROJECT", "vtxdemos"),
            location="us-central1",  # Search grounding requires non-global region
        )

        prompt = f"""Search Reddit for real posts mentioning "{venue_name}" in NYC.

Find up to 3 actual Reddit posts from r/nyc, r/FoodNYC, r/AskNYC, or similar NYC subreddits.

Return ONLY a valid JSON array (no markdown, no explanation):
[
  {{
    "source": "r/subredditname",
    "quote": "verbatim or close paraphrase from the real post/comment, max 200 chars",
    "score": "upvote count as string, or '?' if not found",
    "url": "full reddit.com URL if found, else null",
    "real": true
  }}
]

IMPORTANT:
- Only include posts where "{venue_name}" is explicitly mentioned
- Do NOT fabricate or invent posts — if you find fewer than 3, return fewer
- If no real posts exist for this venue, return []
- Quotes should be casual and authentic, not marketing language"""

        response = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=GenerateContentConfig(
                    tools=[Tool(google_search=GoogleSearch())],
                    temperature=0.1,
                ),
            ),
        )

        text = response.text.strip() if response.text else ""
        # Extract JSON array from response
        match = re.search(r'\[.*?\]', text, re.DOTALL)
        if not match:
            print(f"[Reddit/Search] No JSON array for '{venue_name}' — no results found")
            return []

        results = json.loads(match.group())
        valid = [r for r in results if isinstance(r, dict) and r.get("quote") and r.get("source")]
        print(f"[Reddit/Search] {len(valid)} real signals for '{venue_name}'")
        return valid[:max_results]

    except Exception as e:
        print(f"[Reddit/Search] Error: {e}")
        return []
