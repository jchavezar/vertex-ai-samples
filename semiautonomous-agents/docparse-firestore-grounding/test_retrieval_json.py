"""Test retrieval tool JSON output."""
import os
import sys
sys.path.insert(0, "/workspace")

os.environ["FIRESTORE_PROJECT"] = "sharepoint-wif"
os.environ["FIRESTORE_COLLECTION"] = "docparse_chunks"

from firestore_agent.firestore_retrieval import retrieve_with_pdf_grounding
import json

print("=== Testing retrieval tool ===\n")

query = "bring me all the statistics for milenial gen?"
result = retrieve_with_pdf_grounding(query)

print("Raw result:")
print(result[:500])
print("\n" + "="*80 + "\n")

try:
    data = json.loads(result)
    print(f"Status: {data.get('status')}")
    print(f"Total found: {data.get('total_found')}")
    print(f"Chunks: {len(data.get('chunks', []))}")
    print(f"Grounding: {len(data.get('grounding', []))}")

    if data.get('grounding'):
        print("\nFirst grounding entry:")
        print(json.dumps(data['grounding'][0], indent=2))

    if data.get('chunks'):
        print("\nFirst chunk (first 300 chars):")
        print(data['chunks'][0][:300])
except Exception as e:
    print(f"Parse error: {e}")
