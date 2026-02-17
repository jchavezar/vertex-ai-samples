import os
import base64
from typing import List, Dict, Any
from pypdf import PdfReader, PdfWriter
import tempfile

def split_pdf_logically(pdf_path: str, max_pages_per_chunk: int = 1) -> List[Dict[str, Any]]:
    """
    Splits a PDF locally into separate single-page chunks to be parsed independently.
    Returns a list of dicts containing the base64 encoded chunks and metadata.
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"File {pdf_path} not found.")

    chunks = []
    reader = PdfReader(pdf_path)
    num_pages = len(reader.pages)

    for i in range(0, num_pages, max_pages_per_chunk):
        writer = PdfWriter()
        end_idx = min(i + max_pages_per_chunk, num_pages)
        for j in range(i, end_idx):
             writer.add_page(reader.pages[j])
        
        # Write to temp file to read back as base64 bytes
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
             writer.write(tmp)
             tmp_path = tmp.name
             
        with open(tmp_path, "rb") as f:
             pdf_bytes = f.read()
             
        os.remove(tmp_path)
        
        chunks.append({
             "start_page": i + 1,
             "end_page": end_idx,
             "pdf_bytes": pdf_bytes,
             "mime_type": "application/pdf"
        })

    return chunks
