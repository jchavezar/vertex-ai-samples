import requests
import json

def search(query):
    print(f"--- Searching: {query} ---")
    try:
        url = "http://localhost:8085/search"
        resp = requests.post(url, json={"query": query, "pageSize": 10})
        if resp.status_code == 200:
            data = resp.json()
            results = data.get("results", [])
            for res in results:
                doc = res.get("document", {}).get("derivedStructData", {})
                link = doc.get("link", "") or doc.get("displayLink", "")
                title = doc.get("title", "Untitled")
                
                if link.lower().endswith(".pdf"):
                    print(f"[PDF FOUND] Title: {title}\nLink: {link}\n")
        else:
            print(f"Error: {resp.status_code} - {resp.text}")
    except Exception as e:
        print(f"Exception: {e}")

queries = [
    "quantitative analysis pdf",
    "risk model white paper",
    "fixed income outlook pdf",
    "ESG investing report",
    "private markets trends pdf",
    "wealth management brochure",
    "asset allocation strategy pdf",
    "factor investing white paper",
    "market commentary pdf",
    "ETF landscape report",
    "regulatory compliance guide pdf",
    "smart beta white paper"
]

found_pdfs = set()

for q in queries:
    try:
        url = "http://localhost:8085/search"
        resp = requests.post(url, json={"query": q, "pageSize": 10})
        if resp.status_code == 200:
            data = resp.json()
            results = data.get("results", [])
            for res in results:
                doc = res.get("document", {}).get("derivedStructData", {})
                link = doc.get("link", "") or doc.get("displayLink", "")
                title = doc.get("title", "Untitled")
                
                if link.lower().endswith(".pdf"):
                    if link not in found_pdfs:
                        print(f"[PDF FOUND] Query: '{q}'\nTitle: {title}\nLink: {link}\n")
                        found_pdfs.add(link)
        else:
             print(f"Error: {resp.status_code}")
    except Exception as e:
        print(f"Ex: {e}")

print(f"Total Unique PDFs: {len(found_pdfs)}")

