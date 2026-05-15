"""Test if Gemini API with RAG tool returns grounding_metadata."""
import json
import os

from google import genai
from google.genai import types

# Hardcoded config
os.environ["GOOGLE_CLOUD_LOCATION"] = "global"
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "true"

RAG_CORPUS = "projects/254356041555/locations/us-central1/ragCorpora/6206766569943089152"
MODEL = "gemini-3-flash-preview"
TEST_QUESTION = "What was the total mentions of metaverse-related keywords in 2020 Q1?"

print("=" * 80)
print("Testing Gemini API with RAG tool for grounding_metadata")
print("=" * 80)

# Create client
client = genai.Client(
    vertexai=True,
    project="vtxdemos",
    location="global",
)

# Configure RAG tool
rag_tool = types.Tool(
    retrieval=types.Retrieval(
        vertex_rag_store=types.VertexRagStore(
            rag_corpora=[RAG_CORPUS],
            similarity_top_k=20,
            vector_distance_threshold=0.5,
        )
    )
)

print(f"\nModel: {MODEL}")
print(f"RAG corpus: {RAG_CORPUS}")
print(f"Question: {TEST_QUESTION}\n")

# Call Gemini with RAG
response = client.models.generate_content(
    model=MODEL,
    contents=TEST_QUESTION,
    config=types.GenerateContentConfig(
        tools=[rag_tool],
    ),
)

print("Response type:", type(response))
print("\nFull response:")
print(json.dumps(response.model_dump(), indent=2, default=str))

# Check for grounding
if hasattr(response, 'candidates') and response.candidates:
    for i, cand in enumerate(response.candidates):
        print(f"\nCandidate {i}:")
        if hasattr(cand, 'grounding_metadata'):
            print(f"  grounding_metadata: {cand.grounding_metadata}")
            if cand.grounding_metadata:
                print("  ✓ FOUND GROUNDING METADATA")
            else:
                print("  ✗ grounding_metadata is None/empty")
        else:
            print("  ✗ No grounding_metadata attribute")

print("\n" + "=" * 80)
