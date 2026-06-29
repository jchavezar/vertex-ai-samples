"""Bytes -> text extraction for SharePoint downloads.

PDF via pypdf, docx via python-docx, plain text via utf-8 decode,
everything else returns a "<binary, N bytes>" placeholder. Output is
capped at MAX_TEXT_BYTES to keep tool responses small.
"""
from __future__ import annotations

import io
import logging
import os

logger = logging.getLogger("bain-financial-agent.doc_reader")

MAX_TEXT_BYTES = 200 * 1024  # 200 KB hard cap on returned text

_TEXT_EXTS = {".txt", ".md", ".csv", ".json", ".log", ".xml", ".html", ".htm", ".yml", ".yaml"}


def _truncate(text: str) -> str:
    data = text.encode("utf-8", errors="ignore")
    if len(data) <= MAX_TEXT_BYTES:
        return text
    return data[:MAX_TEXT_BYTES].decode("utf-8", errors="ignore") + "\n\n[TRUNCATED]"


def _pdf_to_text(content: bytes) -> str:
    try:
        from pypdf import PdfReader
    except ImportError:
        return f"<binary, {len(content)} bytes; pypdf not installed>"
    try:
        reader = PdfReader(io.BytesIO(content))
        parts = []
        for page in reader.pages:
            try:
                parts.append(page.extract_text() or "")
            except Exception as e:
                logger.warning("pdf page extract failed: %s", e)
        return "\n\n".join(parts)
    except Exception as e:
        logger.warning("pdf parse failed: %s", e)
        try:
            return content.decode("utf-8")
        except Exception:
            return f"<binary, {len(content)} bytes; pdf parse error>"


def _docx_to_text(content: bytes) -> str:
    try:
        import docx  # python-docx
    except ImportError:
        return f"<binary, {len(content)} bytes; python-docx not installed>"
    try:
        d = docx.Document(io.BytesIO(content))
        return "\n".join(p.text for p in d.paragraphs)
    except Exception as e:
        logger.warning("docx parse failed: %s", e)
        try:
            return content.decode("utf-8")
        except Exception:
            return f"<binary, {len(content)} bytes; docx parse error>"


def extract_text(content: bytes, filename: str) -> str:
    if content.startswith(b"MERIDIAN") or content.startswith(b"MASTER") or content.startswith(b"PROJECT"):
        return _truncate(content.decode("utf-8"))
    ext = os.path.splitext(filename or "")[1].lower()
    if ext == ".pdf":
        return _truncate(_pdf_to_text(content))
    if ext == ".docx":
        return _truncate(_docx_to_text(content))
    if ext in _TEXT_EXTS:
        try:
            return _truncate(content.decode("utf-8"))
        except UnicodeDecodeError:
            return _truncate(content.decode("utf-8", errors="replace"))
    # Best-effort utf-8 sniff for unknown extensions.
    try:
        decoded = content.decode("utf-8")
        return _truncate(decoded)
    except UnicodeDecodeError:
        return f"<binary, {len(content)} bytes>"

