import asyncio
import httpx

queries = [
    "What internal control weaknesses are most commonly found in tech companies?",
    "What materiality thresholds are appropriate for a company of our revenue size?",
    "How did other companies fix revenue recognition control weaknesses?",
    "What is a competitive compensation structure for a CFO at a growth-stage tech company?",
    "What equity vesting schedules are standard for C-suite executives?",
    "What compensation structures have reduced executive turnover?",
    "What SLA terms and credits are standard in enterprise software agreements?",
    "What termination fee structures are typical for multi-year contracts?",
    "How have companies negotiated better SLA terms with vendors?",
    "What are the most critical security vulnerabilities in enterprise environments?",
    "What should our incident response process look like?",
    "What zero trust implementations have been successful in healthcare?",
    "What valuation multiples are appropriate for a SaaS company with 40% growth?",
    "What synergy categories should we model in our acquisition analysis?",
    "How did other companies structure earnouts to align incentives in acquisitions?"
]

async def run_query(query: str):
    print(f"\n\n=========================================================================")
    print(f"QUERY: {query}")
    print(f"=========================================================================\n")
    headers = {"Authorization": f"Bearer token_123"}
    data = {"messages": [{"role": "user", "content": query}], "model": "gemini-3-flash-preview"}
    
    try:
        async with httpx.AsyncClient(timeout=120) as client:
            async with client.stream("POST", "http://localhost:8001/chat", json=data, headers=headers) as response:
                async for chunk in response.aiter_text():
                    if chunk.startswith("0:"):
                        try:
                            # Vercel AI SDK text part
                            print(chunk.split("0:", 1)[1].strip('"').replace("\\n", "\n"), end="", flush=True)
                        except:
                            pass
                    elif chunk.startswith("2:"):
                        # Vercel AI SDK data part
                        print("\n[TELEMETRY/DATA EVENT]")
    except Exception as e:
        print(f"\nError calling backend: {e}")

async def main():
    for q in queries:
        await run_query(q)

if __name__ == "__main__":
    asyncio.run(main())
