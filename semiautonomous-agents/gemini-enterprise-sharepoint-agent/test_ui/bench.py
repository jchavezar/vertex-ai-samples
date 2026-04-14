"""Benchmark: Discovery Engine alone vs Full ADK Agent"""
import asyncio
import time
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
load_dotenv()

import requests
import google.auth
from google.auth.transport.requests import Request

AUTH_ID = os.environ.get('AUTH_ID', 'sharepointauth')
PROJECT_NUMBER = os.environ.get('PROJECT_NUMBER')
ENGINE_ID = os.environ.get('ENGINE_ID')

# Get JWT from environment or test UI
JWT = os.environ.get("TEST_JWT", "")

QUERY = "what is the salary of a cfo?"

def bench_discovery_engine_alone():
    """Measure Discovery Engine streamAssist latency (no ADK)"""
    creds, _ = google.auth.default()
    creds.refresh(Request())

    url = f'https://discoveryengine.googleapis.com/v1alpha/projects/{PROJECT_NUMBER}/locations/global/collections/default_collection/engines/{ENGINE_ID}/assistants/default_assistant:streamAssist'

    headers = {
        'Authorization': f'Bearer {creds.token}',
        'Content-Type': 'application/json',
        'X-Goog-User-Project': PROJECT_NUMBER
    }

    payload = {
        'query': {'text': QUERY},
        'toolsSpec': {
            'vertexAiSearchSpec': {
                'dataStoreSpecs': [
                    {'dataStore': f'projects/{PROJECT_NUMBER}/locations/global/collections/default_collection/dataStores/deloitte-sharepoint_file'}
                ]
            }
        }
    }

    start = time.perf_counter()
    resp = requests.post(url, headers=headers, json=payload, timeout=60)
    elapsed = time.perf_counter() - start

    return elapsed, resp.status_code

async def bench_full_adk_agent():
    """Measure full ADK agent flow (Gemini LLM + tool call + Discovery Engine)"""
    from google.adk.sessions import InMemorySessionService
    from google.adk.runners import Runner
    from google.genai.types import Content, Part
    from agent import root_agent

    session_service = InMemorySessionService()
    await session_service.create_session(
        app_name='test', user_id='test', session_id='bench',
        state={AUTH_ID: JWT},
    )

    runner = Runner(agent=root_agent, app_name='test', session_service=session_service)
    content = Content(role='user', parts=[Part(text=QUERY)])

    start = time.perf_counter()
    result = None
    async for event in runner.run_async(user_id='test', session_id='bench', new_message=content):
        if event.is_final_response() and event.content and event.content.parts:
            result = event.content.parts[0].text
    elapsed = time.perf_counter() - start

    return elapsed, len(result) if result else 0

if __name__ == "__main__":
    print("=" * 50)
    print("LATENCY BENCHMARK")
    print("=" * 50)

    print("\n1. Discovery Engine streamAssist (alone)...")
    de_time, de_status = bench_discovery_engine_alone()
    print(f"   Status: {de_status}")
    print(f"   Latency: {de_time*1000:.0f}ms ({de_time:.2f}s)")

    print("\n2. Full ADK Agent (Gemini + tool + DE)...")
    adk_time, resp_len = asyncio.run(bench_full_adk_agent())
    print(f"   Response: {resp_len} chars")
    print(f"   Latency: {adk_time*1000:.0f}ms ({adk_time:.2f}s)")

    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    print(f"Discovery Engine alone:  {de_time*1000:>8.0f}ms")
    print(f"Full ADK Agent:          {adk_time*1000:>8.0f}ms")
    print(f"ADK overhead:            {(adk_time - de_time)*1000:>8.0f}ms")
