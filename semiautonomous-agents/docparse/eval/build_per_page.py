"""Split each docparse-extracted markdown file into per-page mini-files,
with the page number embedded in the chunk text AND the filename.

This lets RAG Engine treat each page as its own document, and gives the
embedding direct access to the page-number signal so questions like
"on page 11" retrieve the right chunk without separate metadata indexing.

Usage:
    uv run python build_per_page.py <input_dir> <output_dir>

    input_dir   directory of .txt files produced by docparse (one per PDF)
    output_dir  where to write the per-page split (one .txt per page)

The deploy.sh orchestrator uploads <output_dir> to GCS and points the
RAG Engine corpus at it.
"""
import re
import sys
from pathlib import Path

if len(sys.argv) < 3:
    sys.exit("usage: build_per_page.py <input_dir> <output_dir>")

INP = Path(sys.argv[1])
OUT = Path(sys.argv[2])
OUT.mkdir(parents=True, exist_ok=True)

for src in sorted(INP.glob("*.txt")):
    text = src.read_text()
    # Split on docparse's page markers
    parts = re.split(r"<!-- page: (\d+) -->", text)
    # parts = [pre_first_marker, page_num_1, content_1, page_num_2, content_2, ...]

    title = src.stem.replace(" ", "_").replace("(", "").replace(")", "")[:60]

    pages = {}
    for i in range(1, len(parts), 2):
        page_num = int(parts[i])
        content = parts[i + 1] if i + 1 < len(parts) else ""
        pages.setdefault(page_num, []).append(content.strip())

    print(f"{src.name}: {len(pages)} pages")
    for page_num in sorted(pages):
        body = "\n\n".join(pages[page_num]).strip()
        if not body:
            continue
        # Page header is what makes "on page N" questions retrievable.
        chunk_text = f"# {title.replace('_', ' ')} — Page {page_num}\n\n{body}"
        fname = f"{title}_p{page_num:03d}.txt"
        (OUT / fname).write_text(chunk_text)

print(f"\n{len(list(OUT.glob('*.txt')))} per-page files written to {OUT}")
