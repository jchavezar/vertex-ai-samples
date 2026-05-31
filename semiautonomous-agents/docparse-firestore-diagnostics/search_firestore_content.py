from google.cloud import firestore

def search_db(db_name):
    print(f"\n--- Searching database: {db_name} ---")
    db = firestore.Client(project="vtxdemos", database=db_name)
    collections = db.collections()
    for col in collections:
        # Check collection id
        if "metaverse" in col.id.lower() or "multiverse" in col.id.lower() or "doc" in col.id.lower():
            print(f"Match Collection ID: {col.id}")
        
        # Check a few docs
        try:
            docs = col.limit(20).get()
            for doc in docs:
                data_str = str(doc.to_dict()).lower()
                if "multiverse" in data_str or "metaverse" in data_str:
                    print(f"FOUND MATCH in Collection: {col.id}, Doc ID: {doc.id}")
                    print(f"Data snippet: {str(doc.to_dict())[:300]}...")
        except Exception as e:
            pass

def main():
    search_db("(default)")
    search_db("abnb")

if __name__ == "__main__":
    main()
