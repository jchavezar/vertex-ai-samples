import asyncio
from main import _chat_stream

async def test():
    messages = [{"role": "user", "content": "hello"}]
    try:
        async for chunk in _chat_stream(messages, "gemini-3-pro-preview"):
            print("CHUNK:", chunk)
    except Exception as e:
        print("EXCEPTION:", e)

if __name__ == "__main__":
    asyncio.run(test())
