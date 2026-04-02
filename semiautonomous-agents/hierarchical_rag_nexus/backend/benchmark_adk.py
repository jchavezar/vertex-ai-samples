"""
Benchmark: ADK Runner vs Direct API
Tests different configurations to find what makes ADK slow.
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
from google.adk.agents.run_config import RunConfig, StreamingMode

# Disable ADK logging to reduce noise
import logging
logging.getLogger('google_adk').setLevel(logging.ERROR)

client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)
MODEL = "gemini-2.5-flash"
TEST_PROMPT = "What is 2+2? Answer in one word."


async def benchmark_direct_api():
    """Direct API call - baseline."""
    start = time.perf_counter()

    response = await client.aio.models.generate_content(
        model=MODEL,
        contents=TEST_PROMPT,
        config=types.GenerateContentConfig(
            temperature=0.1,
            max_output_tokens=50,
        ),
    )

    elapsed = time.perf_counter() - start
    return elapsed, response.text.strip() if response.text else "empty"


async def benchmark_adk_basic():
    """ADK with minimal config."""
    start = time.perf_counter()

    agent = LlmAgent(
        name="test_agent",
        model=MODEL,
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
        auto_create_session=True,  # Auto-create session
    )

    result_text = ""
    async for event in runner.run_async(
        user_id="test",
        session_id="test_session",
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


async def benchmark_adk_no_streaming():
    """ADK with explicit non-streaming mode."""
    start = time.perf_counter()

    agent = LlmAgent(
        name="test_agent",
        model=MODEL,
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

    run_config = RunConfig(streaming_mode=StreamingMode.NONE)

    result_text = ""
    async for event in runner.run_async(
        user_id="test",
        session_id="test_session_2",
        new_message=types.Content(
            role="user",
            parts=[types.Part.from_text(text=TEST_PROMPT)],
        ),
        run_config=run_config,
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    result_text += part.text

    elapsed = time.perf_counter() - start
    return elapsed, result_text.strip()


async def benchmark_adk_reuse_runner():
    """ADK with runner reuse across calls."""
    # Setup once
    agent = LlmAgent(
        name="test_agent",
        model=MODEL,
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

    # First call (cold)
    start = time.perf_counter()
    result_text = ""
    async for event in runner.run_async(
        user_id="test",
        session_id="reuse_session",
        new_message=types.Content(
            role="user",
            parts=[types.Part.from_text(text=TEST_PROMPT)],
        ),
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    result_text += part.text
    cold_time = time.perf_counter() - start

    # Second call (warm - same session)
    start = time.perf_counter()
    result_text = ""
    async for event in runner.run_async(
        user_id="test",
        session_id="reuse_session",
        new_message=types.Content(
            role="user",
            parts=[types.Part.from_text(text="What is 3+3?")],
        ),
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    result_text += part.text
    warm_time = time.perf_counter() - start

    return cold_time, warm_time, result_text.strip()


async def benchmark_adk_no_thinking():
    """ADK with thinking disabled."""
    start = time.perf_counter()

    agent = LlmAgent(
        name="test_agent",
        model=MODEL,
        instruction="Answer briefly.",
        generate_content_config=types.GenerateContentConfig(
            temperature=0.1,
            max_output_tokens=50,
            thinking_config=types.ThinkingConfig(thinking_budget=0),  # Disable thinking
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
        session_id="no_thinking_session",
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


async def benchmark_direct_no_thinking():
    """Direct API with thinking disabled."""
    start = time.perf_counter()

    response = await client.aio.models.generate_content(
        model=MODEL,
        contents=TEST_PROMPT,
        config=types.GenerateContentConfig(
            temperature=0.1,
            max_output_tokens=50,
            thinking_config=types.ThinkingConfig(thinking_budget=0),
        ),
    )

    elapsed = time.perf_counter() - start
    return elapsed, response.text.strip() if response.text else "empty"


async def main():
    print("=" * 60)
    print("ADK vs Direct API Benchmark")
    print("=" * 60)
    print(f"Model: {MODEL}")
    print(f"Prompt: {TEST_PROMPT}")
    print()

    # Warm up the model first
    print("Warming up model...")
    await client.aio.models.generate_content(
        model=MODEL,
        contents="Hi",
        config=types.GenerateContentConfig(max_output_tokens=5),
    )
    print()

    # Run benchmarks
    results = []

    print("1. Direct API (baseline)...")
    t, r = await benchmark_direct_api()
    results.append(("Direct API", t, r))
    print(f"   Time: {t*1000:.0f}ms, Response: {r[:30]}")

    print("\n2. ADK Basic...")
    t, r = await benchmark_adk_basic()
    results.append(("ADK Basic", t, r))
    print(f"   Time: {t*1000:.0f}ms, Response: {r[:30]}")

    print("\n3. ADK No Streaming...")
    t, r = await benchmark_adk_no_streaming()
    results.append(("ADK No Stream", t, r))
    print(f"   Time: {t*1000:.0f}ms, Response: {r[:30]}")

    print("\n4. Direct API (no thinking)...")
    t, r = await benchmark_direct_no_thinking()
    results.append(("Direct (no think)", t, r))
    print(f"   Time: {t*1000:.0f}ms, Response: {r[:30]}")

    print("\n5. ADK (no thinking)...")
    t, r = await benchmark_adk_no_thinking()
    results.append(("ADK (no think)", t, r))
    print(f"   Time: {t*1000:.0f}ms, Response: {r[:30]}")

    # Run direct API again for comparison
    print("\n6. Direct API (second call)...")
    t, r = await benchmark_direct_api()
    results.append(("Direct API v2", t, r))
    print(f"   Time: {t*1000:.0f}ms, Response: {r[:30]}")

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    baseline = results[0][1]
    for name, time_s, _ in results:
        overhead = ((time_s / baseline) - 1) * 100 if baseline > 0 else 0
        print(f"{name:20s}: {time_s*1000:6.0f}ms  ({overhead:+.0f}% vs baseline)")


if __name__ == "__main__":
    asyncio.run(main())
