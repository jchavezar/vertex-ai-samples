"""Index docparse markdown files to Firestore with rich grounding metadata and embeddings.

Parses docparse-extracted page-level markdown, computes embeddings via text-embedding-005,
and uploads them to Firestore with rich citations, GCS URI, page indices, and direct HTTPS 
PDF grounding links for Gemini Enterprise.

Usage:
    python index_to_firestore.py \\
        --project your-gcp-project \\
        --collection docparse_chunks \\
        --markdown-bucket gs://your-markdown-out-bucket \\
        --pdf-bucket gs://your-source-pdf-in-bucket
"""
from __future__ import annotations

import argparse
import os
import re
import tempfile
from pathlib import Path

from google import genai
from google.cloud import firestore, storage


def embed_text(client: genai.Client, text: str, project: str) -> list[float]:
    """Embed text using text-embedding-005 (768-d)."""
    # Force vertexai=True inside our client calls
    resp = client.models.embed_content(
        model="text-embedding-005",
        contents=[text],
    )
    return resp.embeddings[0].values


def extract_page_chunks(markdown_text: str, pdf_name: str, pdf_bucket: str) -> list[dict]:
    """Split markdown by <!-- page: N --> markers, returning rich chunk metadata.

    Ensures we construct full HTTPS URLs and GCS URIs for high-fidelity PDF grounding 
    inside Gemini Enterprise.
    """
    parts = re.split(r"<!-- page: (\d+) -->", markdown_text)
    chunks = []
    pdf_stem = pdf_name.replace(" ", "_").replace("-", "_")

    # Clean bucket names
    clean_bucket = pdf_bucket.replace("gs://", "").split("/")[0]
    gcs_pdf_uri = f"gs://{clean_bucket}/{pdf_name}.pdf"
    https_pdf_url = f"https://storage.googleapis.com/{clean_bucket}/{pdf_name}.pdf"

    # Counter for position tracking
    total_parts = len(parts)

    for i in range(1, total_parts, 2):
        page_num = int(parts[i])
        content = parts[i+1] if i+1 < total_parts else ""
        if not content.strip():
            continue

        # Add page position metadata relative to document length
        total_pages_approx = total_parts // 2
        page_pct = page_num / max(1, total_pages_approx)
        if page_pct <= 0.33:
            pos_label = "beginning"
        elif page_pct <= 0.66:
            pos_label = "middle"
        else:
            pos_label = "end"

        chunk_text = f"# {pdf_name} — Page {page_num}\n\n{content.strip()}"

        chunks.append({
            "id": f"{pdf_stem}_p{page_num:03d}",
            "text": chunk_text,
            "page": page_num,
            "pdf_name": pdf_name,
            "gcs_pdf_uri": gcs_pdf_uri,
            "https_pdf_url": f"{https_pdf_url}#page={page_num}",
            "page_position": {
                "number": page_num,
                "label": pos_label,
                "percentage": round(page_pct, 2)
            }
        })

    return chunks


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True, help="GCP Project ID")
    parser.add_argument("--collection", default="docparse_chunks", help="Firestore collection name")
    parser.add_argument("--markdown-bucket", required=True, help="GCS bucket containing markdown files (gs://bucket)")
    parser.add_argument("--pdf-bucket", required=True, help="GCS bucket containing original PDFs (gs://bucket)")
    args = parser.parse_args()

    # Create temporary directory to hold downloaded markdown
    temp_dir = Path(tempfile.mkdtemp())
    print(f"[*] Downloading markdown from GCS: {args.markdown_bucket}...")

    bucket_name = args.markdown_bucket.replace("gs://", "").split("/")[0]
    storage_client = storage.Client(project=args.project)
    bucket = storage_client.bucket(bucket_name)

    blobs = bucket.list_blobs()
    markdown_files = []
    for blob in blobs:
        if blob.name.endswith(".txt") and not blob.name.startswith("_"):
            local_path = temp_dir / Path(blob.name).name
            blob.download_to_filename(local_path)
            markdown_files.append(local_path)

    print(f"[+] Downloaded {len(markdown_files)} files to local cache")

    # Initialize Clients
    db = firestore.Client(project=args.project)
    genai_client = genai.Client(vertexai=True, project=args.project, location="global")
    collection = db.collection(args.collection)

    print(f"[*] Indexing to Firestore collection '{args.collection}' inside project '{args.project}'...")

    total_chunks = 0
    for md_file in markdown_files:
        pdf_name = md_file.stem
        print(f"\nProcessing document: {pdf_name}")

        markdown = md_file.read_text(encoding="utf-8")
        chunks = extract_page_chunks(markdown, pdf_name, args.pdf_bucket)
        print(f"  -> Extracted {len(chunks)} page-level chunks")

        for chunk in chunks:
            # Generate Embeddings (768 dimensions)
            embedding = embed_text(genai_client, chunk["text"], args.project)

            # Store in Firestore with State-of-the-Art Metadata
            doc_data = {
                "text": chunk["text"],
                "embedding": embedding,
                "page": chunk["page"],
                "pdf_name": chunk["pdf_name"],
                "gcs_pdf_uri": chunk["gcs_pdf_uri"],
                "https_pdf_url": chunk["https_pdf_url"],
                "page_position": chunk["page_position"]
            }

            collection.document(chunk["id"]).set(doc_data)
            total_chunks += 1

    print(f"\n[+] Indexing Complete! {total_chunks} chunks successfully synchronized with Firestore.")


if __name__ == "__main__":
    main()
