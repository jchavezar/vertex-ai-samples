import asyncio
from google.adk.tools import google_search

async def check_schema():
    print(f"Tool Name: {google_search.name}")
    print(f"Input Schema: {google_search.input_schema}")

if __name__ == "__main__":
    asyncio.run(check_schema())
