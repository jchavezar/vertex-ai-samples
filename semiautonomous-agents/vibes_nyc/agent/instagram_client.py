"""
Instagram signals via Gemini + Google Search grounding.
Searches for real Instagram posts about venues.
Same pattern as reddit_client.py.
"""
import os
import json
import re
import asyncio


async def search_venue_instagram(
    venue_name: str,
    max_results: int = 3,
) -> list[dict]:
    """
    Find real Instagram mentions of a venue using Gemini with Google Search grounding.

    Args:
        venue_name: Name of the venue to search for
        max_results: Max signals to return

    Returns:
        List of dicts with source, username, quote, url
        Empty list if no real results found.
    """
    try:
        from google import genai
        from google.genai.types import Tool, GoogleSearch, GenerateContentConfig

        client = genai.Client(
            vertexai=True,
            project=os.environ.get("GOOGLE_CLOUD_PROJECT", "vtxdemos"),
            location="us-central1",
        )

        prompt = f"""Search Instagram for real posts mentioning "{venue_name}" in New York City.

Find up to {max_results} actual Instagram posts, captions, or comments about this venue.

Return ONLY a valid JSON array (no markdown, no explanation):
[
  {{
    "source": "instagram",
    "username": "@username_who_posted",
    "quote": "caption or comment text mentioning the venue, max 200 chars",
    "score": "likes count as string, or '?' if not found",
    "url": "full instagram.com URL if found, else null"
  }}
]

IMPORTANT:
- Only include posts where "{venue_name}" is explicitly mentioned or clearly about this venue
- Do NOT fabricate or invent posts — if you find fewer than {max_results}, return fewer
- If no real posts exist for this venue, return []
- Quotes should be authentic captions/comments, not marketing language"""

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
        match = re.search(r'\[.*?\]', text, re.DOTALL)
        if not match:
            print(f"[Instagram/Search] No JSON array for '{venue_name}' — no results found")
            return []

        results = json.loads(match.group())
        valid = [r for r in results if isinstance(r, dict) and r.get("quote")]
        for r in valid:
            r["source"] = r.get("source", "instagram")
        print(f"[Instagram/Search] {len(valid)} signals for '{venue_name}'")
        return valid[:max_results]

    except Exception as e:
        print(f"[Instagram/Search] Error: {e}")
        return []
