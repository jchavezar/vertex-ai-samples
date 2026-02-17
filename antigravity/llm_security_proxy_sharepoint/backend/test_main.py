import asyncio
from main import _chat_stream

async def run():
    async for res in _chat_stream([{"content":"hello"}], "gemini-2.5-flash"):
        print(res)

asyncio.run(run())
