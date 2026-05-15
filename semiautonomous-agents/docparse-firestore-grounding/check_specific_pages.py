"""Check specific pages for millennials data."""
from google.cloud import firestore

db = firestore.Client(project="sharepoint-wif")
collection = db.collection("docparse_chunks")

pages_to_check = [
    "Accenture_Metaverse_Evolution_Before_Revolution_p015",
    "Accenture_Metaverse_Evolution_Before_Revolution_p024"
]

for page_id in pages_to_check:
    doc = collection.document(page_id).get()
    if doc.exists:
        data = doc.to_dict()
        text = data.get("text", "")
        print(f"\n{'='*80}")
        print(f"Page: {page_id}")
        print(f"{'='*80}")
        print(text)
        print("\n")
    else:
        print(f"Page {page_id} not found")
