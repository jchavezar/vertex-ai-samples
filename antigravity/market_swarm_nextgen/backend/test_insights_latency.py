import asyncio
import logging
import sys
import os

# Ensure backend root is in path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from src.insights_agent import fetch_insights_dashboard
from src.latency_logger import logger as llog

async def test_insights_latency():
    ticker = "NVDA"
    print(f"Testing INSIGHTS latency for {ticker}...")
    
    llog.start("insights_test")
    
    # Run the agent
    result = await fetch_insights_dashboard(ticker)
    
    llog.mark("insights_test", "Insights completed.")
    llog.dump_latency_summary("insights_test")
    
    print(f"Result Preview: {result[:200]}...")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(test_insights_latency())
