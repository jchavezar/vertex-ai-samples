async def run_query(query: str):
    print(f"\n\n=========================================================================")
    print(f"QUERY: {query}")
    print(f"=========================================================================\n")
    headers = {"Authorization": f"Bearer token_123"}
    data = {"messages": [{"role": "user", "content": query}], "model": "gemini-3-flash-preview"}
    
    try:
        async with httpx.AsyncClient(timeout=120) as client:
            async with client.stream("POST", "http://localhost:8001/chat", json=data, headers=headers) as response:
                async for chunk in response.aiter_text():
                    if chunk.startswith("0:"):
                        try:
                            # Vercel AI SDK text part
                            print(chunk.split("0:", 1)[1].strip('"').replace("\\n", "\n"), end="", flush=True)
                        except:
                            pass
                    elif chunk.startswith("2:"):
                        # Vercel AI SDK data part
                        print("\n[TELEMETRY/DATA EVENT]")
    except Exception as e:
        print(f"\nError calling backend: {e}")

async def main():
    for q in queries:
        await run_query(q)

import asyncio
import httpx
from test_one import run_query
asyncio.run(run_query('finance info'))
