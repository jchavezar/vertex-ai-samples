import asyncio
from app.api.endpoints.ge_search_branch import stream_ge_search

async def main():
    async for chunk in stream_ge_search('Who is the current CFO of Deloitte?', 'deloitte-demo'):
        print(chunk)

if __name__ == "__main__":
    asyncio.run(main())
