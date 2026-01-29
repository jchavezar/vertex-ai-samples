import asyncio
import re
import json
import os
import sys

# Add backend/src to path for imports
sys.path.append(os.path.join(os.getcwd(), "backend"))

from src.adk_comps_workflow import run_adk_comps_workflow

async def test_workflow():
    ticker = "NVDA"
    session_id = f"test_{ticker}_{int(asyncio.get_event_loop().time())}"
    context = "AI accelerators and data center dominance"
    
    print(f"🚀 Starting Battlecards Workflow Test for {ticker}...")
    print(f"Context: {context}")
    print("-" * 50)
    
    intel_received = False
    reasoning_steps = 0
    
    try:
        async for event in run_adk_comps_workflow(ticker, session_id, context):
            event_type = event.get("type")
            if event_type == "reasoning":
                reasoning_steps += 1
                msg = event.get("message", "")
                prog = event.get("progress", 0)
                print(f"🧠 [{prog}%] {msg}")
            
            elif event_type == "intel":
                intel_received = True
                data = event.get("data", {})
                print("\n💎 INTELLIGENCE RECEIVED:")
                print(json.dumps(data, indent=2))
                
                # Basic validation
                primary = data.get("primary")
                peers = data.get("peers", [])
                
                if not primary:
                    print("❌ Error: Primary ticker data is missing!")
                elif primary.get("ticker") != ticker:
                    print(f"⚠️ Warning: Primary ticker mismatch. Expected {ticker}, got {primary.get('ticker')}")
                else:
                    print(f"✅ Primary {ticker} data verified.")
                
                if not peers:
                    print("❌ Error: No peer tickers found!")
                else:
                    print(f"✅ {len(peers)} peers found: {', '.join([p.get('ticker') for p in peers])}")
            
            else:
                print(f"❓ Unknown event: {event}")

        print("-" * 50)
        if intel_received:
            print("✨ Workflow Test COMPLETED SUCCESSFULLY!")
        else:
            print("❌ Workflow Test FAILED: No intel event received.")
            
    except Exception as e:
        print(f"💥 Workflow Test CRASHED: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_workflow())
