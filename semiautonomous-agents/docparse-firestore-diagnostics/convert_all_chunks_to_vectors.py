from google.cloud import firestore
from google.cloud.firestore_v1.vector import Vector

PROJECT = "vtxdemos"
COLLECTION = "docparse_chunks"

def main():
    db = firestore.Client(project=PROJECT)
    print(f"Connecting to Firestore collection '{COLLECTION}' in project '{PROJECT}'...")
    
    docs = list(db.collection(COLLECTION).stream())
    print(f"Found {len(docs)} documents to check.")
    
    updated_count = 0
    for doc in docs:
        data = doc.to_dict()
        embedding = data.get("embedding")
        if embedding is None:
            print(f"Doc {doc.id} has no embedding!")
            continue
            
        # Check if it's already a Vector type or can be converted
        # In python, list is converted to Vector
        if isinstance(embedding, list):
            print(f"Converting plain list embedding for document '{doc.id}' (length {len(embedding)}) to Vector...")
            vector_val = Vector(embedding)
            doc.reference.update({"embedding": vector_val})
            updated_count += 1
        else:
            print(f"Document '{doc.id}' already has embedding of type: {type(embedding)}")
            
    print(f"Done! Successfully updated {updated_count} documents to Vector format.")

if __name__ == "__main__":
    main()
