import asyncio
import os
from src.vais import vais_client
from dotenv import load_dotenv

load_dotenv()

async def find_pdfs():
    queries = ["annual report 2024", "earnings release 2024", "investor presentation", "sustainability report", "10-K"]
    found_pdfs = []
    
    print("--- Searching for PDFs ---")
    for q in queries:
        try:
            print(f"Searching: {q}...")
            results = await vais_client.search(q, page_size=10)
            if results and "results" in results:
                for res in results["results"]:
                    doc = res.get("document", {}).get("derivedStructData", {})
                    link = doc.get("link", "") or doc.get("displayLink", "")
                    title = doc.get("title", "Untitled")
                    
                    if link.lower().endswith(".pdf"):
                        found_pdfs.append({"query": q, "title": title, "link": link})
        except Exception as e:
            print(f"Error searching {q}: {e}")
            
    # Deduplicate
    unique_pdfs = {p["link"]: p for p in found_pdfs}.values()
    
    print(f"\nFound {len(unique_pdfs)} Unique PDFs:")
    for i, pdf in enumerate(unique_pdfs):
        print(f"{i+1}. [{pdf['query']}] {pdf['title']} -> {pdf['link']}")

if __name__ == "__main__":
    asyncio.run(find_pdfs())
