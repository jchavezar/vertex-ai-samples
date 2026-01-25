import requests
import json

url = "http://localhost:8085/search"
query = "pdf"

print(f"--- Query: {query} ---")
try:
    resp = requests.post(url, json={"query": query, "pageSize": 5})
    if resp.status_code == 200:
        data = resp.json()
        results = data.get("results", [])
        for i, res in enumerate(results):
            doc = res.get("document", {}).get("derivedStructData", {})
            link = doc.get("link", "")
            title = doc.get("title", "Untitled")
            mime = doc.get("mime", "N/A")
            fileFormat = doc.get("fileFormat", "N/A")
            
            print(f"\nResult {i+1}:")
            print(f"  Title: {title}")
            print(f"  Link: {link}")
            print(f"  Mime: {mime}")
            print(f"  FileFormat: {fileFormat}")
            print(f"  EndsWith.pdf: {link.lower().endswith('.pdf')}")
    else:
        print(f"Error: {resp.status_code}")
except Exception as e:
    print(f"Ex: {e}")
