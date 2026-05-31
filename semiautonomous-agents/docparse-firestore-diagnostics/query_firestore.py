import os
from google.cloud import firestore

def main():
    db = firestore.Client(project="vtxdemos")
    print("Listing collections in (default) database:")
    collections = db.collections()
    for col in collections:
        print(f"Collection ID: {col.id}")
        # Let's get a few documents to see what's inside
        docs = col.limit(5).get()
        for doc in docs:
            print(f"  Document ID: {doc.id}")
            print(f"    Data: {list(doc.to_dict().keys())}")

if __name__ == "__main__":
    main()
