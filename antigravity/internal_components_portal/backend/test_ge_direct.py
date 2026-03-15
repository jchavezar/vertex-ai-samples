from agents.ge_search_branch import stream_ge_search
import asyncio
import json
import os

from utils.protocol import AIStreamProtocol

async def main():
    messages = [{"role": "user", "content": "whats the salary of a cfo?"}]
    # To see the actual json parsing logs we can capture stdout or write to a file inside stream_ge_search locally
    async for chunk in stream_ge_search(messages, []):
        if "telemetry" in str(chunk):
            print("TELEMETRY CHUNK:", chunk)

if __name__ == "__main__":
    from auth_context_mock import setup_mock
    setup_mock()
    asyncio.run(main())
