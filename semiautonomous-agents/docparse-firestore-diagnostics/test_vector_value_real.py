from google.cloud import firestore
from google.cloud.firestore_v1.vector import Vector
from google.cloud.firestore_v1.base_vector_query import DistanceMeasure

PROJECT = "vtxdemos"
COLLECTION = "docparse_chunks"

def main():
    db = firestore.Client(project=PROJECT)
    
    # 1. Fetch document p001's list embedding
    doc_ref = db.collection(COLLECTION).document("Accenture_Metaverse_Evolution_Before_Revolution_p001")
    doc = doc_ref.get()
    data = doc.to_dict()
    emb_list = data.get("embedding")
    
    print("Plain list embedding type:", type(emb_list))
    
    # Let's see if we can update the document's embedding to a Vector
    print("Updating p001 embedding field to Vector...")
    try:
        vector_val = Vector(emb_list)
        doc_ref.update({"embedding": vector_val})
        print("Update successful!")
    except Exception as e:
        print("Update failed:", e)
        return
        
    # Now let's try the nearest neighbor query again!
    print("Running vector query with Vector field...")
    try:
        vector_query = db.collection(COLLECTION).find_nearest(
            vector_field="embedding",
            query_vector=vector_val,
            distance_measure=DistanceMeasure.COSINE,
            limit=2,
        )
        results = list(vector_query.get())
        print(f"Query returned {len(results)} results.")
        for r in results:
            print(f"  Result doc ID: {r.id}, pdf_name: {r.to_dict().get('pdf_name')}")
    except Exception as e:
        print("Vector query failed:", e)

if __name__ == "__main__":
    main()
