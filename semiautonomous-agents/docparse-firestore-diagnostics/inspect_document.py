from google.cloud import firestore

PROJECT = "vtxdemos"
COLLECTION = "docparse_chunks"

def main():
    db = firestore.Client(project=PROJECT)
    doc_ref = db.collection(COLLECTION).document("Accenture_Metaverse_Evolution_Before_Revolution_p001")
    doc = doc_ref.get()
    if not doc.exists:
        print("Document p001 does not exist!")
        return
    
    data = doc.to_dict()
    print("Keys:", list(data.keys()))
    print("pdf_name:", data.get("pdf_name"))
    print("page:", data.get("page"))
    print("gcs_pdf_uri:", data.get("gcs_pdf_uri"))
    print("https_pdf_url:", data.get("https_pdf_url"))
    
    embedding = data.get("embedding")
    if embedding is None:
        print("embedding is None!")
    else:
        print("embedding type:", type(embedding))
        if hasattr(embedding, "values"):
            print("embedding has values:", len(embedding.values))
        elif isinstance(embedding, list):
            print("embedding is list of length:", len(embedding))
            print("first 5 values:", embedding[:5])
        else:
            print("embedding is other type:", repr(embedding))

if __name__ == "__main__":
    main()
