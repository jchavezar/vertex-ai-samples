"""Test if Gemini with function-call style RAG produces grounding."""
import json
import os

from google import genai
from google.genai import types

os.environ["GOOGLE_CLOUD_LOCATION"] = "global"
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "true"

RAG_CORPUS = "projects/254356041555/locations/us-central1/ragCorpora/6206766569943089152"
MODEL = "gemini-2.5-flash"  # Use a Gemini 2.x model
TEST_QUESTION = "What was the total mentions of metaverse-related keywords in 2020 Q1?"

print("=" * 80)
print("Testing Gemini with FUNCTION-CALL style RAG for grounding")
print("=" * 80)

client = genai.Client(
    vertexai=True,
    project="vtxdemos",
    location="global",
)

# Define a RAG retrieval function (manual function-call style)
rag_function = types.FunctionDeclaration(
    name="retrieve_docparse_context",
    description="Retrieves relevant chunks from the docparse corpus",
    parameters={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The query to match against the corpus"
            }
        },
        "required": ["query"]
    }
)

rag_tool = types.Tool(function_declarations=[rag_function])

print(f"\nModel: {MODEL}")
print(f"Question: {TEST_QUESTION}\n")

# First call - Gemini should ask to use the function
print("Step 1: Initial call (expect function call request):\n")
response1 = client.models.generate_content(
    model=MODEL,
    contents=TEST_QUESTION,
    config=types.GenerateContentConfig(
        tools=[rag_tool],
    ),
)

print(json.dumps(response1.model_dump(), indent=2, default=str)[:2000])

# Check if we got a function call
if response1.candidates and response1.candidates[0].content.parts:
    for part in response1.candidates[0].content.parts:
        if part.function_call:
            print(f"\n✓ Got function call: {part.function_call.name}")
            print(f"  Args: {part.function_call.args}")

            # Simulate function execution - retrieve from RAG
            from vertexai.preview import rag

            rag_response = rag.retrieval_query(
                text=part.function_call.args.get("query", TEST_QUESTION),
                rag_corpora=[RAG_CORPUS],
                similarity_top_k=20,
                vector_distance_threshold=0.5,
            )

            contexts = [ctx.text for ctx in rag_response.contexts.contexts] if rag_response.contexts.contexts else []

            print(f"  Retrieved {len(contexts)} chunks")

            # Step 2: Send function response back
            print("\nStep 2: Sending function response and getting final answer:\n")

            function_response_part = types.Part(
                function_response=types.FunctionResponse(
                    name=part.function_call.name,
                    id=part.function_call.id,
                    response={"contexts": contexts}
                )
            )

            response2 = client.models.generate_content(
                model=MODEL,
                contents=[
                    types.Content(role="user", parts=[types.Part(text=TEST_QUESTION)]),
                    response1.candidates[0].content,  # The function call from model
                    types.Content(role="user", parts=[function_response_part]),  # Our function response
                ],
                config=types.GenerateContentConfig(
                    tools=[rag_tool],
                ),
            )

            print(json.dumps(response2.model_dump(), indent=2, default=str)[:3000])

            # Check for grounding in response2
            if response2.candidates and response2.candidates[0].grounding_metadata:
                print("\n✓✓✓ GROUNDING METADATA FOUND IN FINAL RESPONSE! ✓✓✓")
                print(json.dumps(response2.candidates[0].grounding_metadata.model_dump(), indent=2, default=str)[:1000])
            else:
                print("\n✗ No grounding_metadata in final response")

print("\n" + "=" * 80)
