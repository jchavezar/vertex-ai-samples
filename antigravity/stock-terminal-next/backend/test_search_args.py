import asyncio
from google.adk.tools import google_search

async def test_call():
    try:
        # Try 'query'
        print("Trying args={'query': 'NVDA news'}...")
        res = await google_search.run_async(args={"query": "NVDA news"})
        print(f"Success! Result: {str(res)[:100]}...")
    except Exception as e:
        print(f"Failed with 'query': {e}")
        
    try:
        # Try 'q'
        print("\nTrying args={'q': 'NVDA news'}...")
        res = await google_search.run_async(args={"q": "NVDA news"})
        print(f"Success! Result: {str(res)[:100]}...")
    except Exception as e:
        print(f"Failed with 'q': {e}")

if __name__ == "__main__":
    asyncio.run(test_call())
