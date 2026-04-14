"""
Fast ADK: Pre-warmed client for Google ADK

Problem: ADK's default Gemini model creates a new genai.Client() per agent,
which triggers auth discovery (~18 seconds of metadata server retries).

Solution: Create a shared, pre-warmed client and inject it into ADK.

Usage:
    from fast_adk import FastGemini, warm_up_client

    # Warm up once at startup
    await warm_up_client()

    # Use FastGemini instead of model string
    agent = LlmAgent(
        name="my_agent",
        model=FastGemini(model="gemini-2.5-flash"),  # Uses pre-warmed client
        ...
    )

Performance:
    - Default ADK: ~18-20 seconds (auth discovery)
    - FastGemini: ~0.6-1.2 seconds (same as direct API)
"""

import os
import time
from functools import cached_property
from typing import Optional

from google import genai
from google.genai import types
from google.adk.models.google_llm import Gemini

# Get config from environment
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("PROJECT_ID")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION") or os.getenv("LOCATION", "us-central1")

# Shared client instance
_shared_client: Optional[genai.Client] = None
_credentials = None
_warmup_done: bool = False


def _get_fast_credentials():
    """
    Get credentials using direct method instead of slow discovery.

    google.auth.default() does a long discovery chain with retries (~18s).
    Using compute_engine.Credentials() directly is instant (~150ms).
    """
    global _credentials

    if _credentials is not None:
        return _credentials

    # Check if we're on GCP (Compute Engine, Cloud Run, GKE, etc.)
    try:
        from google.auth import compute_engine
        import google.auth.transport.requests

        credentials = compute_engine.Credentials()
        request = google.auth.transport.requests.Request()
        credentials.refresh(request)
        _credentials = credentials
        return credentials
    except Exception:
        # Fall back to default discovery (slow but works everywhere)
        import google.auth
        credentials, _ = google.auth.default()
        _credentials = credentials
        return credentials


def get_shared_client() -> genai.Client:
    """Get or create the shared genai client with fast credentials."""
    global _shared_client

    if _shared_client is None:
        credentials = _get_fast_credentials()
        _shared_client = genai.Client(
            vertexai=True,
            project=PROJECT_ID,
            location=LOCATION,
            credentials=credentials,
        )

    return _shared_client


async def warm_up_client(model: str = "gemini-2.5-flash") -> float:
    """
    Warm up the shared client with a simple request.
    Call this once at application startup.

    Returns:
        Time taken to warm up in seconds
    """
    global _warmup_done

    if _warmup_done:
        return 0.0

    start = time.perf_counter()
    client = get_shared_client()

    # Make a simple request to warm up the connection
    await client.aio.models.generate_content(
        model=model,
        contents="Hi",
        config=types.GenerateContentConfig(max_output_tokens=5),
    )

    _warmup_done = True
    warmup_time = time.perf_counter() - start
    print(f"[FastADK] Client warmed up in {warmup_time:.2f}s")

    return warmup_time


def warm_up_client_sync(model: str = "gemini-2.5-flash") -> float:
    """
    Synchronous version of warm_up_client.
    Use this in non-async contexts (e.g., module initialization).
    """
    global _warmup_done

    if _warmup_done:
        return 0.0

    start = time.perf_counter()
    client = get_shared_client()

    # Make a simple request to warm up the connection
    client.models.generate_content(
        model=model,
        contents="Hi",
        config=types.GenerateContentConfig(max_output_tokens=5),
    )

    _warmup_done = True
    warmup_time = time.perf_counter() - start
    print(f"[FastADK] Client warmed up in {warmup_time:.2f}s")

    return warmup_time


class FastGemini(Gemini):
    """
    Gemini model that uses a pre-warmed, shared client.

    This avoids the ~18 second auth discovery overhead that occurs
    when ADK creates a new client for each agent.

    Usage:
        # Instead of:
        agent = LlmAgent(model="gemini-2.5-flash", ...)

        # Use:
        agent = LlmAgent(model=FastGemini(model="gemini-2.5-flash"), ...)
    """

    @property
    def api_client(self) -> genai.Client:
        """Return the shared, pre-warmed client instead of creating a new one."""
        return get_shared_client()

    @cached_property
    def _live_api_client(self) -> genai.Client:
        """Return the shared client for live API as well."""
        return get_shared_client()


# Convenience function to create a FastGemini model
def fast_gemini(model: str = "gemini-2.5-flash", **kwargs) -> FastGemini:
    """
    Create a FastGemini model instance.

    Args:
        model: The Gemini model name
        **kwargs: Additional Gemini parameters

    Returns:
        FastGemini instance
    """
    return FastGemini(model=model, **kwargs)
