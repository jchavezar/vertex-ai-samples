
import asyncio
import os
import sys
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

# Load env
load_dotenv(dotenv_path="backend/.env")

try:
    from src.neural_link_agent import neural_service
    
    async def test():
        print("Testing Neural Link for 'NVDA'...")
        try:
            result = await neural_service.get_trends("NVDA")
            print("\n--- RESULTS ---")
            print(f"Ticker: {result.get('ticker')}")
            print(f"Summary: {result.get('summary')}")
            print(f"Market Vibe: {result.get('market_vibe')}")
            
            print(f"\nNews Cards: {len(result.get('cards', []))}")
            for card in result.get('cards', [])[:2]:
                print(f" - {card.get('title')} ({card.get('sentiment')})")
                
            print(f"\nRumor Cards: {len(result.get('rumors', []))}")
            for rumor in result.get('rumors', []):
                print(f" - [{rumor.get('source')}] {rumor.get('content')} (Impact: {rumor.get('impact')})")
                
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()

    asyncio.run(test())

except ImportError as e:
    print(f"Import Error: {e}")
    print("Make sure you are in the root directory.")
