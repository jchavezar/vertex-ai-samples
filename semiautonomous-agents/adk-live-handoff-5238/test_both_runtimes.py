import asyncio
import os
import certifi

os.environ.setdefault("SSL_CERT_FILE", certifi.where())
os.environ.setdefault("REQUESTS_CA_BUNDLE", certifi.where())

import vertexai

PROJECT_ID = "vtxdemos"
LOCATION = "us-central1"

RUNTIME_1_ADK_271 = "projects/254356041555/locations/us-central1/reasoningEngines/434137218425028608"
RUNTIME_2_FIXED = "projects/254356041555/locations/us-central1/reasoningEngines/6983496976528572416"


def test_text_mode(resource_name: str, label: str):
    """Test standard text mode (stream_query) routed to gemini-2.5-flash."""
    print(f"\n{'='*70}")
    print(f"[TEXT MODE - stream_query] {label}")
    print(f"Resource: {resource_name}")
    print(f"{'='*70}")
    client = vertexai.Client(project=PROJECT_ID, location=LOCATION)
    engine = client.agent_engines.get(name=resource_name)

    for query in ["What is the weather in Miami?", "What time is it right now?"]:
        print(f"\nUser (Text): {query}")
        for ev in engine.stream_query(user_id="text-user-1", message=query):
            out = ev.get("output", ev) if isinstance(ev, dict) else {}
            author = out.get("author", "")
            parts = out.get("content", {}).get("parts", [])
            for p in parts:
                if "function_call" in p:
                    print(f"  [{author}] Tool Call -> {p['function_call']['name']}({p['function_call'].get('args', {})})")
                if "text" in p and p["text"]:
                    print(f"  [{author}] Answer    -> {p['text']}")


async def drain_live_turn(session, idle_timeout=2.5):
    """Reads all events from a Live Bidi turn.
    IMPORTANT: When tools or transfers are called in Live mode, Gemini Live emits
    an intermediate `turn_complete=True` after the tool call BEFORE streaming the
    spoken audio & output_transcription. Draining until idle ensures we don't break early!
    """
    full_transcript = []
    audio_chunks = 0
    tool_calls = []
    last_author = ""

    while True:
        try:
            ev_raw = await asyncio.wait_for(session.receive(), timeout=idle_timeout)
            out = ev_raw.get("bidiStreamOutput", ev_raw)
            author = out.get("author", "")
            if author:
                last_author = author

            # Check tool calls
            parts = out.get("content", {}).get("parts", [])
            for p in parts:
                if "function_call" in p:
                    tool_calls.append(f"{author}:{p['function_call']['name']}")
                if "inline_data" in p:
                    audio_chunks += 1

            # Check native audio transcription
            tx = out.get("output_transcription", {})
            if tx and tx.get("text") and tx.get("finished"):
                full_transcript.append(f"[{author}]: {tx['text']}")
        except asyncio.TimeoutError:
            break

    return {
        "author": last_author,
        "tool_calls": tool_calls,
        "audio_chunks": audio_chunks,
        "transcripts": full_transcript,
    }


async def test_live_bidi_mode(resource_name: str, label: str):
    """Test Live Bidi WebSocket mode (bidi_stream_query) with round-trip agent handoff."""
    print(f"\n{'='*70}")
    print(f"[LIVE BIDI MODE - bidi_stream_query] {label}")
    print(f"Resource: {resource_name}")
    print(f"{'='*70}")
    client = vertexai.Client(project=PROJECT_ID, location=LOCATION)

    async with client.aio.live.agent_engines.connect(
        agent_engine=resource_name,
        config={"class_method": "bidi_stream_query"},
    ) as session:
        await session.send({"user_id": "live-user-1"})

        # Turn 1: Root -> Helper transfer
        q1 = "What is the weather in Miami?"
        print(f"\nTurn 1 User (Live): {q1}")
        await session.send({"content": {"role": "user", "parts": [{"text": q1}]}})
        res1 = await drain_live_turn(session)
        print(f"  Tool Calls : {res1['tool_calls']}")
        print(f"  Audio PCM  : {res1['audio_chunks']} chunks received")
        print(f"  Spoken Text: {' '.join(res1['transcripts'])}")

        # Turn 2: Helper -> Root round-trip transfer
        q2 = "What time is it right now?"
        print(f"\nTurn 2 User (Live Round-Trip): {q2}")
        await session.send({"content": {"role": "user", "parts": [{"text": q2}]}})
        res2 = await drain_live_turn(session)
        print(f"  Tool Calls : {res2['tool_calls']}")
        print(f"  Audio PCM  : {res2['audio_chunks']} chunks received")
        print(f"  Spoken Text: {' '.join(res2['transcripts'])}")


if __name__ == "__main__":
    test_text_mode(RUNTIME_1_ADK_271, "Runtime 1: ADK 2.7.1 (Standard)")
    test_text_mode(RUNTIME_2_FIXED, "Runtime 2: ADK 2.7.1 + Wakeup Trigger Patch")

    asyncio.run(test_live_bidi_mode(RUNTIME_1_ADK_271, "Runtime 1: ADK 2.7.1 (Standard)"))
    asyncio.run(test_live_bidi_mode(RUNTIME_2_FIXED, "Runtime 2: ADK 2.7.1 + Wakeup Trigger Patch"))
