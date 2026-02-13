import os
from mcp_sharepoint import SharePointMCP

mcp = SharePointMCP()
print("Searching for ALL files...")
results = mcp.search_documents(query="*", limit=20)
print(f"Found {len(results)} files.")
for r in results:
    print(f"- {r['name']} (ID: {r['id']})")
    try:
        content = mcp.get_document_content(r['id'])
        print(f"  Content length: {len(content)} characters")
        if content:
           print(f"  Preview: {content[:100]}...")
    except Exception as e:
        print(f"  Error reading: {e}")
