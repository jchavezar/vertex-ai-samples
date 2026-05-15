"""Test vector search step by step."""
import sys
sys.path.insert(0, "/workspace")

print("Step 1: Import libraries...")
try:
    from google import genai
    from google.cloud import firestore
    from google.cloud.firestore_v1.base_vector_query import DistanceMeasure
    print("  ✓ Imports successful")
except Exception as e:
    print(f"  ✗ Import error: {e}")
    sys.exit(1)

print("\nStep 2: Create embedding client...")
try:
    client = genai.Client(vertexai=True, project="sharepoint-wif", location="global")
    print("  ✓ Client created")
except Exception as e:
    print(f"  ✗ Client error: {e}")
    sys.exit(1)

print("\nStep 3: Embed query...")
try:
    query = "what is the metaverse?"
    response = client.models.embed_content(model="text-embedding-005", contents=query)
    query_embedding = response.embeddings[0].values
    print(f"  ✓ Embedding created: {len(query_embedding)} dimensions")
except Exception as e:
    print(f"  ✗ Embedding error: {e}")
    sys.exit(1)

print("\nStep 4: Connect to Firestore...")
try:
    db = firestore.Client(project="sharepoint-wif")
    collection = db.collection("docparse_chunks")
    print("  ✓ Firestore connected")
except Exception as e:
    print(f"  ✗ Firestore error: {e}")
    sys.exit(1)

print("\nStep 5: Run vector search...")
try:
    vector_query = collection.find_nearest(
        vector_field="embedding",
        query_vector=query_embedding,
        distance_measure=DistanceMeasure.COSINE,
        limit=5
    )
    results = vector_query.get()
    print(f"  ✓ Vector search returned {len(results)} results")

    if results:
        print(f"\nFirst result:")
        doc = results[0]
        print(f"  Doc ID: {doc.id}")
        data = doc.to_dict()
        print(f"  Text preview: {data.get('text', '')[:200]}")
except Exception as e:
    print(f"  ✗ Vector search error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
