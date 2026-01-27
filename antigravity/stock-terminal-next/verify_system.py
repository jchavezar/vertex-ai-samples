import asyncio
import httpx
import sys
import os

# Add backend to path for imports
sys.path.append(os.path.abspath("backend"))

# Mocking environment for loose imports if needed, but we prefer external testing
# Actually, let's test specific internal functions directly to ensure they work,
# AND test the endpoints.

from backend.src.market_data import get_real_price, get_real_history

async def verify_market_data():
    print("\n--- Verifying Market Data (yfinance) ---")
    try:
        # Test NVDA
        print("Fetching NVDA Price...")
        price = get_real_price("NVDA")
        if price:
            print(f"✅ Success: {price['ticker']} = ${price['price']} ({price['time'].strip().splitlines()[0]})")
        else:
            print("❌ Failed: NVDA Price returned None")

        print("Fetching NVDA History...")
        hist = get_real_history("NVDA")
        if hist and hist.get("history"):
            print(f"✅ Success: Got {len(hist['history'])} days of history")
        else:
            print("❌ Failed: NVDA History returned None/Empty")

    except Exception as e:
        print(f"❌ Exception in Market Data: {e}")

async def verify_backend_health():
    print("\n--- Verifying Backend API ---")
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get("http://localhost:8001/health")
            if resp.status_code == 200:
                print(f"✅ Backend Health: OK ({resp.json()})")
            else:
                print(f"❌ Backend Health Failed: {resp.status_code}")
        except Exception as e:
             print(f"❌ Backend Connection Failed: {e}")

async def verify_report_stream():
    print("\n--- Verifying Report Generator (Stream) ---")
    async with httpx.AsyncClient() as client:
        try:
            # We use a short timeout because we just want to see if it starts
            print("Initiating Stream for AAPL...")
            async with client.stream("GET", "http://localhost:8001/report/stream?ticker=AAPL&type=primer") as resp:
                if resp.status_code == 200:
                    print("✅ Stream Connection Established (200 OK)")
                    # Read first few chunks
                    count = 0
                    async for chunk in resp.aiter_lines():
                        if chunk.strip():
                            print(f"   Received chunk: {chunk[:60]}...")
                            count += 1
                            if count >= 3: break
                    print("✅ Stream Data Flow Confirmed")
                else:
                    print(f"❌ Stream Failed: {resp.status_code}")
        except Exception as e:
            print(f"❌ Stream Exception: {e}")

async def main():
    await verify_market_data()
    await asyncio.sleep(2) # Give backend time to start
    await verify_backend_health()
    await verify_report_stream()

if __name__ == "__main__":
    asyncio.run(main())
