import asyncio
import json
import re
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from src.comps_agent import run_comps_intelligence

async def test_comps_extraction():
    print("=== STARTING COMPS EXTRACTION TEST ===")
    ticker = "NVDA"
    session_id = "test_verification_session"
    
    found_intel = False
    reasoning_count = 0
    
    print(f"Running intelligence for {ticker}...")
    try:
        async for event in run_comps_intelligence(ticker, session_id):
            if event["type"] == "reasoning":
                reasoning_count += 1
                print(f" [Reasoning {reasoning_count}] {event['message'][:50]}...")
            elif event["type"] == "intel":
                print(" [SUCCESS] Intelligence block isolated and parsed.")
                intel = event["data"]
                print(f" - Summary: {intel.get('summary', 'MISSING')[:100]}...")
                print(f" - Primary: {intel.get('primary', {}).get('ticker')} ({intel.get('primary', {}).get('name')})")
                print(f" - Peers identified: {len(intel.get('peers', []))}")
                for peer in intel.get('peers', []):
                    print(f"   -> {peer.get('ticker')}: {peer.get('momentum')}")
                found_intel = True
            elif event["type"] == "error":
                print(f" [ERROR] {event['message']}")
    except Exception as e:
        print(f" [CRITICAL] Pipeline crashed: {e}")
    
    print("\n=== VERIFICATION RESULTS ===")
    print(f"Reasoning steps captured: {reasoning_count}")
    print(f"Intelligence parsed: {'PASSED' if found_intel else 'FAILED'}")
    
    if reasoning_count < 3:
        print(" [WARNING] Low reasoning count. UI might feel too fast.")
    
    if found_intel:
        print(" [RESULT] TEST PASSED")
    else:
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(test_comps_extraction())
