"""Document parsing via markitdown — converts PDF/DOCX to plain text."""

import tempfile
from pathlib import Path
from markitdown import MarkItDown


def parse_document(content: bytes, filename: str) -> str:
    """Convert a single document (PDF/DOCX) to markdown text."""
    # If content is already text (pre-cached .md), return as-is
    try:
        text = content.decode("utf-8")
        if not text.startswith("%PDF"):
            return text
    except UnicodeDecodeError:
        pass

    # Binary file — use markitdown
    suffix = Path(filename).suffix
    md = MarkItDown()
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as f:
        f.write(content)
        f.flush()
        result = md.convert(f.name)
        return result.text_content


def parse_all(files: dict[str, bytes]) -> dict[str, str]:
    """Parse all downloaded files. Returns {filename: text_content}."""
    documents = {}
    for filename, content in files.items():
        text = parse_document(content, filename)
        if text and text.strip():
            documents[filename] = text
    return documents
