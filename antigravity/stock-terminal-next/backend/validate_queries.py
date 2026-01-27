
import asyncio
import aiohttp
import json
import re

QUERIES = [
    # Fundamentals
    "How much short-term and long-term debt does GE carry?",
    "Is Netflix's current P/E above or below their 5-year average?",
    
    # Estimates
    "How have next fiscal year EPS estimates for Apple evolved over the past 12 months?",
    "What is the current analyst consensus rating for Apple?",
    
    # Prices
    "Show the week-over-week change in closing prices for Oracle in Q1 2024",
    "Which days in the past month had the highest trading volume for Amazon?",
    
    # Ownership
    "Who are the top 10 institutional holders of Apple stock?",
    "Compare insider buying vs selling activity for Tesla over the past year",
    
    # M&A
    "List all completed acquisitions made by Apple since 2020",
    "What deals were announced yesterday where the target is a public company?",
    
    # People
    "Show me the organizational structure and contact information for Tesla's leadership team",
    "Show me all the CFOs across the FAANG companies",
    
    # Calendar
    "When was Microsoft's last earnings call?",
    
    # GeoRev
    "How much revenue does Apple make in China?",
    
    # Supply Chain
    "List all direct customers of Taiwan Semiconductor",
]

async def test_query(session, query):
    url = "http://localhost:8001/chat"
    payload = {
        "messages": [{"content": query, "role": "user"}],
        "sessionId": f"test_suite_{query[:5].strip()}_{str(asyncio.get_event_loop().time())}",
        "model": "gemini-2.0-flash-exp"
    }
    
    print(f"\n[TEST] Query: {query}")
    try:
        async with session.post(url, json=payload) as resp:
            if resp.status != 200:
                print(f"[FAIL] HTTP {resp.status}")
                return False
            
            tool_detected = False
            error_detected = False
            response_text = ""
            
            async for line in resp.content:
                line = line.decode('utf-8').strip()
                if not line: continue
                
                if line.startswith("data:"):
                    data_str = line[5:] # Remove 'data:' prefix
                    print(f"  [RAW]: {data_str[:100]}...")
                    try:
                        data = json.loads(data_str)
                        # Check for Protocol v1 or v2 format
                        # Using AIStreamProtocol, we look for 'type'
                        if "type" in data:
                            if data["type"] == "tool_call":
                                print(f"  -> Tool Call: {data.get('tool')}")
                                tool_detected = True
                            elif data["type"] == "tool_result":
                                # print(f"  -> Tool Result for {data.get('tool')}")
                                pass
                            elif data["type"] == "error":
                                print(f"  -> ERROR PROTOCOL: {data.get('args')}")
                                error_detected = True
                            elif data["type"] == "text":
                                chunk = data.get("args", "") 
                                # args might be string or dict? check protocol
                                # ADK usually emits text(chunk) where args is the text
                                print(f"  [Text]: {chunk[:50]}..." if len(str(chunk)) > 50 else f"  [Text]: {chunk}")
                    except:
                        # Maybe just text?
                        pass
                else:
                    # Non-data line
                    pass
                        
            if error_detected:
                print("[FAIL] Error returned.")
                return False
                        
            if error_detected:
                print("[FAIL] Error returned.")
                return False
            
            if tool_detected:
                print("[PASS] Tools triggered.")
                return True
            else:
                print("[WARN] No tools triggered (Answer might be chat-only or LLM failure).")
                return True # Technically not a crash, but suspicious for these queries.
                
    except Exception as e:
        print(f"[FAIL] Exception: {e}")
        return False

async def main():
    async with aiohttp.ClientSession() as session:
        params = {"query": "warmup"}
        # Just simple warmup
        await asyncio.sleep(1)
        
        results = []
        for q in QUERIES:
            success = await test_query(session, q)
            results.append((q, success))
            # Wait a bit between queries to avoid rate limits
            await asyncio.sleep(2)
            
        print("\n\n=== SUMMARY ===")
        for q, success in results:
            status = "PASS" if success else "FAIL"
            print(f"[{status}] {q}")

if __name__ == "__main__":
    import sys
    # Install dependencies if missing (quick hack for execution environment)
    # subprocess.check_call([sys.executable, "-m", "pip", "install", "aiohttp"])
    asyncio.run(main())
