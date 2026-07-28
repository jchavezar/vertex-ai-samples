#!/usr/bin/env python3
import os
import sys
import time
import json
import argparse
import fitz  # PyMuPDF
from google import genai

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
if not PROJECT_ID or PROJECT_ID == "jesusarguelles-sandbox":
    PROJECT_ID = "vtxdemos"
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
DEFAULT_MODEL = "text-embedding-005"
FALLBACK_MODEL = "text-embedding-004"

def get_genai_client():
    return genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)

def extract_pdf_info(pdf_path, chunk_size=1000, chunk_overlap=200):
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found at {pdf_path}")
    
    file_size_bytes = os.path.getsize(pdf_path)
    file_size_kb = file_size_bytes / 1024
    file_size_mb = file_size_kb / 1024

    doc = fitz.open(pdf_path)
    num_pages = len(doc)

    pages_data = []
    total_words = 0
    total_chars = 0

    chunks = []

    for page_idx in range(num_pages):
        page = doc[page_idx]
        text = page.get_text()
        words_count = len(text.split())
        chars_count = len(text)
        total_words += words_count
        total_chars += chars_count

        pages_data.append({
            "page_num": page_idx + 1,
            "words": words_count,
            "chars": chars_count,
            "text": text
        })

        # Create overlapping text chunks for RAG reusability
        clean_text = text.strip()
        if not clean_text:
            continue
        
        # Simple character sliding window chunker
        start = 0
        while start < len(clean_text):
            end = min(start + chunk_size, len(clean_text))
            chunk_str = clean_text[start:end]
            chunks.append({
                "chunk_id": len(chunks) + 1,
                "page_num": page_idx + 1,
                "text": chunk_str
            })
            if end == len(clean_text):
                break
            start += (chunk_size - chunk_overlap)

    return {
        "file_name": os.path.basename(pdf_path),
        "file_path": os.path.abspath(pdf_path),
        "size_bytes": file_size_bytes,
        "size_kb": file_size_kb,
        "size_mb": file_size_mb,
        "pages_count": num_pages,
        "total_words": total_words,
        "total_chars": total_chars,
        "pages_data": pages_data,
        "chunks": chunks
    }

def generate_embeddings(chunks, model_name=DEFAULT_MODEL):
    client = get_genai_client()
    texts = [c["text"] for c in chunks]
    
    start_time = time.time()
    
    # Try embedding batch or sequentially if batch size limit applies
    batch_size = 50
    embedded_chunks = []
    used_model = model_name

    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i:i + batch_size]
        try:
            res = client.models.embed_content(
                model=used_model,
                contents=batch_texts
            )
            embeddings_list = res.embeddings
        except Exception as e:
            if used_model != FALLBACK_MODEL:
                print(f"Model {used_model} failed ({e}). Falling back to {FALLBACK_MODEL}...")
                used_model = FALLBACK_MODEL
                res = client.models.embed_content(
                    model=used_model,
                    contents=batch_texts
                )
                embeddings_list = res.embeddings
            else:
                raise e

        for sub_idx, emb_obj in enumerate(embeddings_list):
            chunk_info = chunks[i + sub_idx].copy()
            chunk_info["embedding"] = emb_obj.values
            chunk_info["embedding_dim"] = len(emb_obj.values)
            embedded_chunks.append(chunk_info)

    end_time = time.time()
    latency = end_time - start_time

    return embedded_chunks, latency, used_model

def process_pdf(pdf_path, output_json=None):
    print(f"\n--- Processing PDF: {os.path.basename(pdf_path)} ---")
    
    start_total_time = time.time()
    
    pdf_info = extract_pdf_info(pdf_path)
    chunks = pdf_info["chunks"]

    print(f"File Size: {pdf_info['size_bytes']:,} bytes ({pdf_info['size_kb']:.2f} KB / {pdf_info['size_mb']:.2f} MB)")
    print(f"Number of Pages: {pdf_info['pages_count']}")
    print(f"Total Words: {pdf_info['total_words']:,}")
    print(f"Total Chunks Created: {len(chunks)}")

    print("\nGenerating embeddings via Vertex AI...")
    embedded_chunks, embed_latency, model_used = generate_embeddings(chunks)
    
    total_latency = time.time() - start_total_time

    dimension = embedded_chunks[0]["embedding_dim"] if embedded_chunks else 0

    result_summary = {
        "pdf_name": pdf_info["file_name"],
        "pdf_path": pdf_info["file_path"],
        "file_size_bytes": pdf_info["size_bytes"],
        "file_size_kb": round(pdf_info["size_kb"], 2),
        "file_size_mb": round(pdf_info["size_mb"], 4),
        "number_of_pages": pdf_info["pages_count"],
        "number_of_words": pdf_info["total_words"],
        "number_of_chunks": len(chunks),
        "number_of_embeddings": len(embedded_chunks),
        "embedding_model_used": model_used,
        "embedding_dimension": dimension,
        "embedding_api_latency_seconds": round(embed_latency, 3),
        "total_processing_latency_seconds": round(total_latency, 3)
    }

    print("\n=== SUMMARY RESULTS ===")
    print(json.dumps(result_summary, indent=2))

    if not output_json:
        output_json = os.path.join(os.path.dirname(__file__), f"embedded_{pdf_info['file_name'].replace(' ', '_')}.json")

    save_data = {
        "summary": result_summary,
        "embedded_chunks": embedded_chunks
    }

    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(save_data, f, indent=2)

    print(f"\nSaved full embeddings and metadata to: {output_json}")

    return result_summary

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Embed a PDF document using Google Gemini Embeddings")
    parser.add_argument("pdf_path", nargs="?", default="/Users/jesusarguelles/Downloads/2026q1-alphabet-earnings-release.pdf", help="Path to PDF file")
    parser.add_argument("--output", help="Output JSON path to save embeddings")
    args = parser.parse_args()

    process_pdf(args.pdf_path, args.output)
