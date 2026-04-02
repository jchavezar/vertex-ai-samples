"""
Test: Fix ADK slowness by sharing the warmed client
"""

import asyncio
import os
import time
from dotenv import load_dotenv

load_dotenv(dotenv_path="../.env")

PROJECT_ID = os.getenv("PROJECT_ID")
LOCATION = os.getenv("LOCATION", "us-central1")

os.environ["GOOGLE_CLOUD_PROJECT"] = PROJECT_ID
os.environ["GOOGLE_CLOUD_LOCATION"] = LOCATION
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "true"

from google import genai
from google.genai import types
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.models.google_llm import Gemini

import logging
logging.basicConfig(level=logging.WARNING)

MODEL = "gemini-2.5-flash"
TEST_PROMPT = "What is 2+2? Answer briefly."


# Create a warmed client ONCE at module level
print("Warming up client...")
t0 = time.perf_counter()
warmed_client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)

# Make a request to fully warm up
warmup_response = warmed_client.models.generate_content(
    model=MODEL,
    contents="Hi",
    config=types.GenerateContentConfig(max_output_tokens=5),
)
print(f"Client warmed in {(time.perf_counter() - t0)*1000:.0f}ms")


# Custom Gemini that uses our pre-warmed client
class FastGemini(Gemini):
    """Gemini model that uses a pre-warmed client."""

    _shared_client = None

    @classmethod
    def set_client(cls, client):
        cls._shared_client = client

    @property
    def api_client(self):
        if FastGemini._shared_client is not None:
            return FastGemini._shared_client
        # Fall back to default
        return super().api_client


# Set the warmed client
FastGemini.set_client(warmed_client)


async def benchmark_adk_with_fast_gemini():
    """ADK with pre-warmed client."""
    start = time.perf_counter()

    agent = LlmAgent(
        name="test_agent",
        model=FastGemini(model=MODEL),  # Use our custom Gemini
        instruction="Answer briefly.",
        generate_content_config=types.GenerateContentConfig(
            temperature=0.1,
            max_output_tokens=50,
        ),
    )

    session_service = InMemorySessionService()
    runner = Runner(
        agent=agent,
        session_service=session_service,
        app_name="benchmark",
        auto_create_session=True,
    )

    result_text = ""
    async for event in runner.run_async(
        user_id="test",
        session_id="fast_session",
        new_message=types.Content(
            role="user",
            parts=[types.Part.from_text(text=TEST_PROMPT)],
        ),
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    result_text += part.text

    elapsed = time.perf_counter() - start
    return elapsed, result_text.strip()


async def benchmark_direct_api():
    """Direct API for comparison."""
    start = time.perf_counter()

    response = await warmed_client.aio.models.generate_content(
        model=MODEL,
        contents=TEST_PROMPT,
        config=types.GenerateContentConfig(
            temperature=0.1,
            max_output_tokens=50,
        ),
    )

    elapsed = time.perf_counter() - start
    return elapsed, response.text.strip() if response.text else "empty"


async def benchmark_adk_default():
    """ADK with default Gemini (slow)."""
    start = time.perf_counter()

    agent = LlmAgent(
        name="test_agent",
        model=MODEL,  # String model name -> creates new client
        instruction="Answer briefly.",
        generate_content_config=types.GenerateContentConfig(
            temperature=0.1,
            max_output_tokens=50,
        ),
    )

    session_service = InMemorySessionService()
    runner = Runner(
        agent=agent,
        session_service=session_service,
        app_name="benchmark",
        auto_create_session=True,
    )

    result_text = ""
    async for event in runner.run_async(
        user_id="test",
        session_id="default_session",
        new_message=types.Content(
            role="user",
            parts=[types.Part.from_text(text=TEST_PROMPT)],
        ),
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    result_text += part.text

    elapsed = time.perf_counter() - start
    return elapsed, result_text.strip()


async def main():
    print("\n" + "=" * 60)
    print("ADK FIX TEST: Pre-warmed Client")
    print("=" * 60)

    print("\n1. Direct API (baseline)...")
    t, r = await benchmark_direct_api()
    print(f"   Time: {t*1000:.0f}ms, Result: {r[:50]}")

    print("\n2. ADK with FastGemini (pre-warmed client)...")
    t, r = await benchmark_adk_with_fast_gemini()
    print(f"   Time: {t*1000:.0f}ms, Result: {r[:50]}")

    print("\n3. ADK with FastGemini (second call)...")
    t, r = await benchmark_adk_with_fast_gemini()
    print(f"   Time: {t*1000:.0f}ms, Result: {r[:50]}")

    print("\n4. ADK default (for comparison)...")
    t, r = await benchmark_adk_default()
    print(f"   Time: {t*1000:.0f}ms, Result: {r[:50]}")

    print("\n5. Direct API (final)...")
    t, r = await benchmark_direct_api()
    print(f"   Time: {t*1000:.0f}ms, Result: {r[:50]}")


if __name__ == "__main__":
    asyncio.run(main())
