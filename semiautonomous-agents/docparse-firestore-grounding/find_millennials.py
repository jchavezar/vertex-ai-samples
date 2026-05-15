"""Find millennials data in Firestore."""
from google.cloud import firestore

db = firestore.Client(project="sharepoint-wif")
collection = db.collection("docparse_chunks")

print("=== Searching for millennials data ===\n")

# Get all docs and search for millennials
all_docs = list(collection.stream())
print(f"Total docs: {len(all_docs)}\n")

matches = []
for doc in all_docs:
    data = doc.to_dict()
    text = data.get("text", "")
    if "millennial" in text.lower() or "milenial" in text.lower():
        matches.append((doc.id, text))

print(f"Found {len(matches)} docs with millennials data:\n")
for doc_id, text in matches[:5]:
    print(f"Doc ID: {doc_id}")
    print(text[:500])
    print("\n" + "="*80 + "\n")
