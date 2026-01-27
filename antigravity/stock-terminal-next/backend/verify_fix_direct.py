
import asyncio
import os
import sys
from dotenv import load_dotenv

# Ensure we can import from src
sys.path.append(os.getcwd())

from src.smart_agent import create_smart_agent

async def main():
    print("--- Starting Verification ---")
    load_dotenv()
    
    # Check if we have a token or need to use mock
    token = os.getenv("FACTSET_API_KEY", "mock_token")
    print(f"Token: {token[:5]}...")
    
    agent = await create_smart_agent(token)
    
    tool_names = [getattr(t, 'name', t.__name__) for t in agent.tools]
    print(f"\nRegistered Tools ({len(tool_names)}):")
    for name in tool_names:
        print(f"  - {name}")
        
    required = "FactSet_Prices"
    required_lower = "factset_prices"
    
    if required in tool_names or required_lower in tool_names:
        print(f"\n[PASS] '{required}' (or lowercase) found.")
    else:
        print(f"\n[FAIL] '{required}' NOT found in tools.")
        
    # Also verify if prompt encourages CamelCase
    print("\nChecking Instructions for Tool References...")
    if required in agent.instruction:
        print(f"  - Instructions mention '{required}' (CamelCase)")
    else:
        print(f"  - Instructions DO NOT mention '{required}' (CamelCase)")

if __name__ == "__main__":
    asyncio.run(main())
