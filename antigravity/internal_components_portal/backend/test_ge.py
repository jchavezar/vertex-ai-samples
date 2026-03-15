import asyncio
from agents.ge_search_branch import stream_ge_search

async def main():
    async for chunk in stream_ge_search('What is the Deloitte approach to AI?'):
        print(chunk)

if __name__ == "__main__":
    asyncio.run(main())
