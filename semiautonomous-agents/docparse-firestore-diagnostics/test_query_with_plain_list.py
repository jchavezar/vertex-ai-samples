from google.cloud import firestore
from google.cloud.firestore_v1.base_vector_query import DistanceMeasure

PROJECT = "vtxdemos"
COLLECTION = "docparse_chunks"

def main():
    db = firestore.Client(project=PROJECT)
    
    # Let's get p001's embedding list to use as a query vector
    doc_ref = db.collection(COLLECTION).document("Accenture_Metaverse_Evolution_Before_Revolution_p001")
    doc = doc_ref.get()
    data = doc.to_dict()
    emb_list = list(data.get("embedding")) # This is now a Vector, let's get its values list
    
    # Print type
    print("embedding type in doc p001:", type(data.get("embedding")))
    
    # Try find_nearest with plain list
    print("Running vector query using a PLAIN list of floats as query_vector...")
    try:
        vector_query = db.collection(COLLECTION).find_nearest(
            vector_field="embedding",
            query_vector=emb_list,
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
