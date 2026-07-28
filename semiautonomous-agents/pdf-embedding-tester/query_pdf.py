#!/usr/bin/env python3
import os
import sys
import json
import numpy as np
from google import genai

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
if not PROJECT_ID or PROJECT_ID == "jesusarguelles-sandbox":
    PROJECT_ID = "vtxdemos"
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
DEFAULT_MODEL = "text-embedding-005"

def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

def query_embedded_doc(json_path, query_text, top_k=3):
    if not os.path.exists(json_path):
        print(f"Error: JSON file not found at {json_path}")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    summary = data["summary"]
    chunks = data["embedded_chunks"]
    model_name = summary.get("embedding_model_used", DEFAULT_MODEL)

    print(f"\nDocument: {summary['pdf_name']}")
    print(f"Searching for query: '{query_text}' using model: {model_name}...")

    client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)
    res = client.models.embed_content(
        model=model_name,
        contents=query_text
    )
    query_emb = res.embeddings[0].values

    scored_chunks = []
    for chunk in chunks:
        sim = cosine_similarity(query_emb, chunk["embedding"])
        scored_chunks.append((sim, chunk))

    scored_chunks.sort(key=lambda x: x[0], reverse=True)

    print(f"\n--- TOP {top_k} RESULTS ---")
    for idx, (sim, chunk) in enumerate(scored_chunks[:top_k], 1):
        print(f"\n[Result {idx}] Score: {sim:.4f} | Page {chunk['page_num']} | Chunk ID {chunk['chunk_id']}")
        print(f"Snippet: {chunk['text'][:300]}...")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 query_pdf.py <path_to_embedded_json> <query_text>")
        sys.exit(1)

    json_path = sys.argv[1]
    query_text = " ".join(sys.argv[2:])
    query_embedded_doc(json_path, query_text)
