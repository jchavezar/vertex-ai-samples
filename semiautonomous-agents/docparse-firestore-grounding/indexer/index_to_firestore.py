"""Index docparse markdown to Firestore with gemini-embeddings-002.

Reads GA-extracted markdown, embeds each per-page chunk with gemini-embeddings-002,
stores in Firestore with PDF metadata for grounding construction.

Usage:
    python index_to_firestore.py \\
        /tmp/docparse-ga-extraction/*.txt \\
        --project sharepoint-wif \\
        --collection docparse_chunks
"""
import argparse
from pathlib import Path
from google.cloud import firestore
from google.cloud.firestore_v1.vector import Vector
from google import genai
from google.genai import types
import re

def embed_text(client, text: str) -> list[float]:
    """Embed with text-embedding-005 (768-d, GA-compatible)."""
    resp = client.models.embed_content(
        model="text-embedding-005",
        contents=[text])
    return resp.embeddings[0].values


def extract_page_chunks(markdown_text: str, pdf_name: str) -> list[dict]:
    """Split markdown by <!-- page: N [printed: M] --> markers, return chunks with metadata."""
    pattern = re.compile(r"<!-- page: (\d+)(?:\s+printed:\s*(\w*))? -->")
    matches = list(pattern.finditer(markdown_text))
    chunks = []

    for i, match in enumerate(matches):
        page_num = int(match.group(1))
        printed_page = match.group(2)
        if printed_page is not None:
            printed_page = printed_page.strip()
            if not printed_page:
                printed_page = None

        start_idx = match.end()
        end_idx = matches[i+1].start() if i + 1 < len(matches) else len(markdown_text)
        content = markdown_text[start_idx:end_idx]
        if not content.strip():
            continue

        # Prepend page header
        chunk_text = f"# {pdf_name} — Page {page_num}\n\n{content.strip()}"

        chunks.append({
            "id": f"{pdf_name.replace(' ', '_')}_p{page_num:03d}",
            "text": chunk_text,
            "page": page_num,
            "printed_page": printed_page,
            "pdf_name": pdf_name,
        })

    return chunks


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--markdown-bucket", required=True, help="GCS bucket with markdown files (gs://bucket/*.txt)")
    parser.add_argument("--project", required=True, help="GCP project for Firestore")
    parser.add_argument("--collection", default="docparse_chunks", help="Firestore collection name")
    parser.add_argument("--pdf-bucket", default="gs://sharepoint-wif-docparse-in", help="GCS bucket with source PDFs")
    args = parser.parse_args()

    # Download markdown from GCS using Python client
    from google.cloud import storage
    import tempfile

    temp_dir = Path(tempfile.mkdtemp())
    print(f"Downloading markdown from {args.markdown_bucket}...")

    # Parse bucket name from gs:// URI
    bucket_name = args.markdown_bucket.replace("gs://", "").split("/")[0]
    storage_client = storage.Client(project=args.project)
    bucket = storage_client.bucket(bucket_name)

    # List and download all .txt files
    blobs = bucket.list_blobs(prefix="", delimiter="/")
    markdown_files = []
    for blob in blobs:
        if blob.name.endswith(".txt") and not blob.name.startswith("_"):
            local_path = temp_dir / Path(blob.name).name
            blob.download_to_filename(local_path)
            markdown_files.append(local_path)

    print(f"Downloaded {len(markdown_files)} files")

    # Credentials auto-work in Cloud Run
    db = firestore.Client(project=args.project)
    genai_client = genai.Client(vertexai=True, project=args.project, location="global")

    collection = db.collection(args.collection)

    print(f"Indexing {len(markdown_files)} files to Firestore...")
    print(f"  Project: {args.project}")
    print(f"  Collection: {args.collection}")
    print(f"  Embedding model: text-embedding-005 (768-d)")

    total_chunks = 0
    for md_file in markdown_files:
        md_path = Path(md_file)
        pdf_name = md_path.stem.replace("-", " ")
        print(f"\n{md_path.name}:")

        markdown = md_path.read_text()
        chunks = extract_page_chunks(markdown, pdf_name)
        print(f"  {len(chunks)} page-level chunks")

        total_pages = len(chunks)
        for chunk in chunks:
            # Embed
            embedding = embed_text(genai_client, chunk["text"])

            # Reconstruct GCS and HTTPS PDF URIs
            clean_bucket = args.pdf_bucket.replace("gs://", "").split("/")[0]
            gcs_pdf_uri = f"gs://{clean_bucket}/{md_path.stem}.pdf"
            https_pdf_url = f"https://storage.googleapis.com/{clean_bucket}/{md_path.stem}.pdf#page={chunk['page']}"
            
            # Reconstruct page position
            page_pct = chunk["page"] / max(1, total_pages)
            if page_pct <= 0.33:
                pos_label = "beginning"
            elif page_pct <= 0.66:
                pos_label = "middle"
            else:
                pos_label = "end"
                
            page_position = {
                "number": chunk["page"],
                "label": pos_label,
                "percentage": round(page_pct, 2)
            }

            # Store in Firestore
            doc_data = {
                "text": chunk["text"],
                "embedding": Vector(embedding),
                "page": chunk["page"],
                "printed_page": chunk.get("printed_page"),
                "pdf_name": chunk["pdf_name"],
                "pdf_uri": f"{args.pdf_bucket}/{md_path.stem}.pdf",  # Reconstruct PDF URI
                "gcs_pdf_uri": gcs_pdf_uri,
                "https_pdf_url": https_pdf_url,
                "page_position": page_position,
            }

            collection.document(chunk["id"]).set(doc_data)
            total_chunks += 1

        print(f"  Indexed {len(chunks)} chunks")

    print(f"\n✅ Total: {total_chunks} chunks indexed to Firestore")
    print(f"   Collection: {args.project}/{args.collection}")


if __name__ == "__main__":
    main()
