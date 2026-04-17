"""Vertex AI Gemini client wrapper with retry and rate limiting."""

import asyncio
import json
import logging
import os
import time

from google import genai
from google.genai import types

logger = logging.getLogger("amex-mcp.gemini")

MODEL = os.environ.get("ENRICHMENT_MODEL", "gemini-3.1-flash-lite-preview")
PROJECT = os.environ.get("GCP_PROJECT_ID", "vtxdemos")
LOCATION = "global"

_client = None
_semaphore = asyncio.Semaphore(5)


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client(vertexai=True, project=PROJECT, location=LOCATION)
    return _client


async def generate_json(
    prompt: str,
    system_instruction: str | None = None,
    max_retries: int = 3,
) -> dict:
    """Call Gemini and return parsed JSON response.

    Uses structured output (response_mime_type=application/json),
    retries with exponential backoff, and a semaphore for rate limiting.
    """
    config = types.GenerateContentConfig(
        response_mime_type="application/json",
    )
    if system_instruction:
        config.system_instruction = system_instruction

    async with _semaphore:
        for attempt in range(max_retries):
            try:
                client = _get_client()
                response = await asyncio.to_thread(
                    client.models.generate_content,
                    model=MODEL,
                    contents=prompt,
                    config=config,
                )
                text = response.text.strip()
                return json.loads(text)
            except Exception as e:
                if attempt < max_retries - 1:
                    wait = 2 ** (attempt + 1)
                    logger.warning(json.dumps({
                        "event": "gemini_retry",
                        "attempt": attempt + 1,
                        "wait_secs": wait,
                        "error": str(e),
                    }))
                    await asyncio.sleep(wait)
                else:
                    logger.error(json.dumps({
                        "event": "gemini_failed",
                        "error": str(e),
                    }))
                    raise
