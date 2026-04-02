"""
Detailed ADK Timing Analysis
Find exactly where the 18 seconds goes.
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

# Enable ADK debug logging
import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(name)s %(message)s')
adk_logger = logging.getLogger('google_adk')
adk_logger.setLevel(logging.DEBUG)

client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)
MODEL = "gemini-2.5-flash"
TEST_PROMPT = "What is 2+2?"


async def run_adk_with_timing():
    """Run ADK with detailed timing."""
    times = {}

    t0 = time.perf_counter()

    # Create agent
    agent = LlmAgent(
        name="test_agent",
        model=MODEL,
        instruction="Answer briefly.",
        generate_content_config=types.GenerateContentConfig(
            temperature=0.1,
            max_output_tokens=50,
        ),
    )
    times["agent_create"] = time.perf_counter() - t0

    t1 = time.perf_counter()

    # Create session service
    session_service = InMemorySessionService()
    times["session_service_create"] = time.perf_counter() - t1

    t2 = time.perf_counter()

    # Create runner
    runner = Runner(
        agent=agent,
        session_service=session_service,
        app_name="benchmark",
        auto_create_session=True,
    )
    times["runner_create"] = time.perf_counter() - t2

    t3 = time.perf_counter()

    # Create message
    new_message = types.Content(
        role="user",
        parts=[types.Part.from_text(text=TEST_PROMPT)],
    )
    times["message_create"] = time.perf_counter() - t3

    print("\n=== Starting run_async ===")
    t4 = time.perf_counter()
    times["before_run"] = t4 - t0

    # Run and track each event
    event_times = []
    event_count = 0
    result_text = ""

    async for event in runner.run_async(
        user_id="test",
        session_id="test_session",
        new_message=new_message,
    ):
        event_time = time.perf_counter()
        event_count += 1

        event_type = type(event).__name__
        has_content = bool(event.content)
        has_text = False

        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    result_text += part.text
                    has_text = True

        event_times.append({
            "num": event_count,
            "time_since_start": event_time - t4,
            "type": event_type,
            "has_content": has_content,
            "has_text": has_text,
            "author": getattr(event, 'author', 'unknown'),
        })

        print(f"  Event {event_count}: +{(event_time - t4)*1000:.0f}ms, "
              f"author={getattr(event, 'author', '?')}, "
              f"text={has_text}")

    t5 = time.perf_counter()
    times["run_async_total"] = t5 - t4
    times["total"] = t5 - t0

    return times, event_times, result_text


async def main():
    print("=" * 60)
    print("Detailed ADK Timing Analysis")
    print("=" * 60)

    # Warm up
    print("\nWarming up model...")
    await client.aio.models.generate_content(
        model=MODEL,
        contents="Hi",
        config=types.GenerateContentConfig(max_output_tokens=5),
    )

    print("\nRunning ADK benchmark...")
    times, event_times, result = await run_adk_with_timing()

    print("\n" + "=" * 60)
    print("TIMING BREAKDOWN")
    print("=" * 60)

    print("\nSetup times:")
    print(f"  Agent create:          {times['agent_create']*1000:8.1f}ms")
    print(f"  SessionService create: {times['session_service_create']*1000:8.1f}ms")
    print(f"  Runner create:         {times['runner_create']*1000:8.1f}ms")
    print(f"  Message create:        {times['message_create']*1000:8.1f}ms")
    print(f"  Total setup:           {times['before_run']*1000:8.1f}ms")

    print(f"\nrun_async() total:       {times['run_async_total']*1000:8.1f}ms")
    print(f"\nGrand total:             {times['total']*1000:8.1f}ms")

    print(f"\nResult: {result}")

    print("\n" + "=" * 60)
    print("EVENT TIMELINE")
    print("=" * 60)
    for e in event_times:
        print(f"  Event {e['num']:2d}: +{e['time_since_start']*1000:8.1f}ms "
              f"| author={e['author']:8s} | text={e['has_text']}")

    # Now run direct API for comparison
    print("\n" + "=" * 60)
    print("DIRECT API COMPARISON")
    print("=" * 60)

    t0 = time.perf_counter()
    response = await client.aio.models.generate_content(
        model=MODEL,
        contents=TEST_PROMPT,
        config=types.GenerateContentConfig(
            temperature=0.1,
            max_output_tokens=50,
        ),
    )
    t1 = time.perf_counter()

    print(f"Direct API: {(t1-t0)*1000:.0f}ms")
    print(f"Result: {response.text}")


if __name__ == "__main__":
    asyncio.run(main())
