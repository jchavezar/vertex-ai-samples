import asyncio
import os
import json
from src.news_agent import get_parallel_news

async def verify():
    print("--- VERIFYING OPTIMIZED NEWS PIPELINE ---")
    ticker = "NVDA"
    print(f"Ticker: {ticker}")
    
    try:
        items = await get_parallel_news(ticker)
        print(f"\nFetched {type(items)} results.")
        print(items)
        
        if not items:
            print("No items found.")
            return
            
        for i, item in enumerate(items):
            print(f"\n[{i+1}] {item.headline}")
            print(f"    Source: {item.source} | Time: {item.time}")
            print(f"    Sentiment: {item.sentiment} | Impact: {item.impact_score}")
            print(f"    Summary: {item.summary[:100]}...")
            
        print("\n--- FINAL JSON ---")
        print(json.dumps([item.model_dump() for item in items], indent=2))
        
    except Exception as e:
        print(f"Verification failed: {e}")

if __name__ == "__main__":
    asyncio.run(verify())
