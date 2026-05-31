from google.cloud import firestore

def main():
    db = firestore.Client(project="vtxdemos")
    col = db.collection("docparse_chunks")
    docs = col.get()
    
    print(f"Total chunks indexed: {len(docs)}")
    multiverse_count = 0
    metaverse_count = 0
    
    for doc in docs:
        d = doc.to_dict()
        text = d.get("text", "")
        pdf_name = d.get("pdf_name", "")
        page = d.get("page", "")
        
        if "multiverse" in text.lower():
            multiverse_count += 1
            print(f"Match found in '{pdf_name}' on Page {page} (Doc ID: {doc.id}):")
            print(f"--- TEXT SNIPPET ---")
            print(text[:500])
            print("--------------------\n")
        
        if "metaverse" in text.lower():
            metaverse_count += 1

    print(f"Summary: Found {multiverse_count} chunks containing 'multiverse' and {metaverse_count} containing 'metaverse'.")

if __name__ == "__main__":
    main()
