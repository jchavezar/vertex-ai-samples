import os
from google import genai
from google.cloud import firestore
from google.cloud.firestore_v1.base_vector_query import DistanceMeasure

PROJECT = "vtxdemos"
COLLECTION = "docparse_chunks"
EMBED_MODEL = "text-embedding-005"

def main():
    print(f"Connecting to genai client and firestore client on project {PROJECT}...")
    client = genai.Client(vertexai=True, project=PROJECT, location="global")
    db = firestore.Client(project=PROJECT)
    
    query = "what is the metaverse?"
    print(f"Embedding query: '{query}' using model {EMBED_MODEL}...")
    resp = client.models.embed_content(model=EMBED_MODEL, contents=query)
    embedding = resp.embeddings[0].values
    print(f"Embedding length: {len(embedding)}")
    print(f"First 5 values: {embedding[:5]}")
    
    print(f"Running find_nearest vector query in collection {COLLECTION}...")
    vector_query = db.collection(COLLECTION).find_nearest(
        vector_field="embedding",
        query_vector=embedding,
        distance_measure=DistanceMeasure.COSINE,
        limit=5,
    )
    
    print("Fetching results...")
    results = []
    for doc in vector_query.get():
        data = doc.to_dict()
        print(f"Document {doc.id} found!")
        print(f"  pdf_name: {data.get('pdf_name')}")
        print(f"  page: {data.get('page')}")
        print(f"  text snippet: {data.get('text', '')[:200]}...")
        results.append(data)
        
    print(f"Total results returned: {len(results)}")

if __name__ == "__main__":
    main()
