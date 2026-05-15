"""Debug metaverse retrieval."""
import sys
sys.path.insert(0, "/workspace")
import os
os.environ["FIRESTORE_PROJECT"] = "sharepoint-wif"
os.environ["FIRESTORE_COLLECTION"] = "docparse_chunks"

from firestore_agent.firestore_retrieval import retrieve_with_pdf_grounding
import json

print("Testing metaverse query...")
try:
    result = retrieve_with_pdf_grounding("what is the metaverse?")
    print(f"Raw result length: {len(result)}")

    data = json.loads(result)
    print(f"\nStatus: {data.get('status')}")
    print(f"Total found: {data.get('total_found')}")
    print(f"Chunks: {len(data.get('chunks', []))}")

    if data.get('chunks'):
        print(f"\nFirst chunk (300 chars):")
        print(data['chunks'][0][:300])
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
