from __future__ import annotations

import asyncio
from pathlib import Path

import typer
from rich.console import Console

from .pipeline import parse_pdf_async, write_outputs

app = typer.Typer(help="PDF -> high-fidelity markdown via Gemini multimodal")
console = Console()


@app.command()
def parse(
    pdf: Path = typer.Argument(..., exists=True, dir_okay=False, readable=True),
    out: Path = typer.Option(Path("./out"), "--out", "-o", help="Output directory"),
    detect_concurrency: int = typer.Option(8, help="Parallel page-detect calls"),
    text_concurrency: int = typer.Option(8, help="Parallel page-OCR calls"),
    struct_concurrency: int = typer.Option(8, help="Parallel chart/table/diagram/photo extracts"),
) -> None:
    """Parse PDF into a single markdown file."""
    console.rule(f"[bold]docparse[/bold] {pdf.name}")
    result = asyncio.run(
        parse_pdf_async(
            pdf,
            detect_concurrency=detect_concurrency,
            text_concurrency=text_concurrency,
            struct_concurrency=struct_concurrency,
        )
    )
    md_path = write_outputs(result, pdf, out)
    t = result.timings
    console.rule(
        f"[green]done[/green] {md_path}  ({t['total']:.1f}s total: "
        f"warm+render {t['render_and_warmup']:.1f}s | "
        f"detect {t['detect']:.1f}s | "
        f"extract {t['extract']:.1f}s)"
    )


if __name__ == "__main__":
    app()
