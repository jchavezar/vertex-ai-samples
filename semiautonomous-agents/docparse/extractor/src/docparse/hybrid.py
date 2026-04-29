"""Helpers for the text-layer + LLM hybrid pipeline.

The dedup machinery lives in pipeline._unique_sentences. This module exposes
the small predicates that classify whether a region's text-layer content is
trustworthy enough to keep, plus the canonical set of region types treated
as "text" (vs. visual structures like charts/photos).
"""
from __future__ import annotations

from .schemas import RegionType

TEXT_TYPES = {
    RegionType.HEADING,
    RegionType.BODY,
    RegionType.QUOTE,
    RegionType.CAPTION,
    RegionType.FOOTNOTE,
}


def text_layer_usable(text: str, region_area_frac: float = 0.05) -> bool:
    """True if the text layer's content for a region is trustworthy.

    Cascading checks:
    1. empty / whitespace
    2. CID-fallback garble — pypdfium2 returns "(cid:NNN)" when fonts have
       no Unicode mapping
    3. low printable-character ratio (binary contamination)
    4. for long passages, sparse stopwords → likely OCR artefact
    5. text length implausibly small for the bbox area
    """
    stripped = text.strip()
    if len(stripped) < 10:
        return False
    if "(cid:" in stripped or stripped.count("�") > 2:
        return False
    printable = sum(1 for c in stripped if c.isprintable() or c in " \n\t")
    if printable / len(stripped) < 0.90:
        return False
    if len(stripped) > 200:
        STOPWORDS = {
            "the", "and", "of", "to", "in", "for", "is", "are", "a", "an", "on", "as",
            "el", "la", "los", "que", "de", "en", "con", "por", "las", "y", "o",
        }
        words = [w.lower().strip(".,;:()[]\"'") for w in stripped.split()]
        if words:
            hits = sum(1 for w in words if w in STOPWORDS)
            if hits / len(words) < 0.05:
                return False
    expected_min_chars = max(20, int(region_area_frac * 2000))
    if len(stripped) < expected_min_chars * 0.10:
        return False
    return True
