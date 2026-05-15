"""Index docparse markdown to Firestore with text-embedding-005.

Reads page-chunked markdown from a GCS bucket, embeds each chunk, writes to
Firestore with PDF metadata so the MCP server can return PDF-page citations.

Usage (local):
    python index_to_firestore.py \
        --markdown-bucket gs://sharepoint-wif-docparse-out \
        --pdf-bucket gs://sharepoint-wif-docparse-in \
        --project sharepoint-wif \
        --collection mcp_docs

Cloud Run job: see deploy_indexer_job.sh
"""
import argparse
import re
import tempfile
from pathlib import Path

from google import genai
from google.cloud import firestore, storage


def embed_text(client: genai.Client, text: str) -> list[float]:
    resp = client.models.embed_content(
        model="text-embedding-005",
        contents=[text],
    )
    return resp.embeddings[0].values


def extract_page_chunks(markdown_text: str, pdf_name: str) -> list[dict]:
    """Split docparse markdown by `<!-- page: N -->` markers."""
    parts = re.split(r"<!-- page: (\d+) -->", markdown_text)
    chunks = []
    for i in range(1, len(parts), 2):
        page_num = int(parts[i])
        content = parts[i + 1] if i + 1 < len(parts) else ""
        if not content.strip():
            continue
        chunks.append({
            "id": f"{pdf_name.replace(' ', '_')}_p{page_num:03d}",
            "text": f"# {pdf_name} — Page {page_num}\n\n{content.strip()}",
            "page": page_num,
            "pdf_name": pdf_name,
        })
    return chunks


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--markdown-bucket", required=True)
    parser.add_argument("--pdf-bucket", required=True)
    parser.add_argument("--project", required=True)
    parser.add_argument("--collection", default="mcp_docs")
    args = parser.parse_args()

    bucket_name = args.markdown_bucket.replace("gs://", "").split("/")[0]
    storage_client = storage.Client(project=args.project)
    bucket = storage_client.bucket(bucket_name)

    temp_dir = Path(tempfile.mkdtemp())
    md_files = []
    for blob in bucket.list_blobs(prefix="", delimiter="/"):
        if blob.name.endswith(".txt") and not blob.name.startswith("_"):
            local = temp_dir / Path(blob.name).name
            blob.download_to_filename(local)
            md_files.append(local)
    print(f"Downloaded {len(md_files)} markdown files from {args.markdown_bucket}")

    db = firestore.Client(project=args.project)
    genai_client = genai.Client(vertexai=True, project=args.project, location="global")
    collection = db.collection(args.collection)

    total = 0
    for md_file in md_files:
        pdf_name = md_file.stem.replace("-", " ")
        chunks = extract_page_chunks(md_file.read_text(), pdf_name)
        print(f"{md_file.name}: {len(chunks)} chunks")
        for chunk in chunks:
            embedding = embed_text(genai_client, chunk["text"])
            collection.document(chunk["id"]).set({
                "text": chunk["text"],
                "embedding": embedding,
                "page": chunk["page"],
                "pdf_name": chunk["pdf_name"],
                "pdf_uri": f"{args.pdf_bucket}/{md_file.stem}.pdf",
            })
            total += 1

    print(f"\nIndexed {total} chunks to {args.project}/{args.collection}")


if __name__ == "__main__":
    main()
