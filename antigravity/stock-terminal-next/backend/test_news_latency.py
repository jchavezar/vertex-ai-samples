import asyncio
import logging
import sys
import os

# Ensure backend root is in path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from src.news_agent import get_parallel_news
from src.latency_logger import logger as llog

async def test_news_latency():
    ticker = "NVDA"
    print(f"Testing NEWS PIPELINE latency for {ticker}...")
    
    llog.start("news_test")
    
    # Run the pipeline
    items = await get_parallel_news(ticker)
    
    llog.mark("news_test", f"Pipeline completed. Found {len(items)} items.")
    llog.dump_latency_summary("news_test")
    
    for i in items:
        print(f" - {i.headline} ({i.sentiment})")

if __name__ == "__main__":
    # Ensure logs are visible
    logging.basicConfig(level=logging.INFO)
    asyncio.run(test_news_latency())
