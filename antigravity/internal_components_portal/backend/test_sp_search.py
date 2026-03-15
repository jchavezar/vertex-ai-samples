import asyncio
from mcp_service.mcp_sharepoint import SharePointMCP

async def main():
    sp = SharePointMCP()
    print("Searching...")
    try:
        results = sp.search_documents("salary of a cfo", 5)
        print("Results:", results)
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    asyncio.run(main())
