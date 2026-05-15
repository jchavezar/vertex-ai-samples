"""Test Firestore retrieval locally."""
import os
from google.cloud import firestore

os.environ["FIRESTORE_PROJECT"] = "sharepoint-wif"
os.environ["FIRESTORE_COLLECTION"] = "docparse_chunks"

db = firestore.Client(project="sharepoint-wif")
collection = db.collection("docparse_chunks")

print("=== Testing Firestore retrieval ===\n")

# Get all docs
docs = list(collection.limit(10).stream())
print(f"Total docs in first 10: {len(docs)}\n")

# Test keyword search for millennials
query = "bring me all the statistics for milenial gen?"
query_lower = query.lower()
keywords = query_lower.split()[:5]

print(f"Keywords: {keywords}\n")

matches = []
for doc in docs:
    data = doc.to_dict()
    text = data.get("text", "")
    if any(word in text.lower() for word in keywords):
        matches.append(text[:300])

print(f"Found {len(matches)} matches")
for i, match in enumerate(matches[:3]):
    print(f"\n--- Match {i+1} ---")
    print(match)
