"""Demo 9 — Multimodal embeddings (preview).

Uses gemini-embedding-2-preview to embed:
  * a text query, and
  * a synthetic image (programmatically generated so the demo runs offline).

We show that text and image live in the same vector space and can be searched
against one another (the cross-modal "match my brand" capability).
"""
from __future__ import annotations

import io

import numpy as np
from PIL import Image, ImageDraw

from _client import CLIENT, MM_MODEL, banner
from google.genai import types


def make_image(label: str, color: tuple[int, int, int]) -> bytes:
    img = Image.new("RGB", (256, 256), color=color)
    d = ImageDraw.Draw(img)
    d.text((20, 110), label, fill=(255, 255, 255))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def embed(part_or_parts) -> np.ndarray:
    parts = part_or_parts if isinstance(part_or_parts, list) else [part_or_parts]
    resp = CLIENT.models.embed_content(model=MM_MODEL, contents=parts)
    v = np.asarray(resp.embeddings[0].values, dtype=np.float32)
    return v / np.linalg.norm(v)


def main() -> None:
    banner(f"Demo 09 — multimodal cross-modal search with {MM_MODEL}")

    palette = {
        "warm sunset orange":  (235, 130, 50),
        "cool ocean blue":     (40, 110, 180),
        "fresh forest green":  (60, 140, 80),
        "deep midnight black": (20, 20, 30),
    }

    print("Embedding 4 generated swatches as 'images' …")
    image_parts: list[tuple[str, bytes]] = []
    for label, color in palette.items():
        png = make_image(label, color)
        image_parts.append((label, png))

    img_vecs = []
    for label, png in image_parts:
        try:
            v = embed(types.Part.from_bytes(data=png, mime_type="image/png"))
            img_vecs.append(v)
            print(f"  ✓ {label:<22} dim={v.shape[0]}")
        except Exception as exc:
            print(f"  ! {label}: {exc}")
            img_vecs.append(None)

    text_queries = [
        "warmth, golden-hour, summer mood",
        "calm aquatic, marine palette",
        "lush nature and vegetation",
        "dark cinematic night scene",
    ]

    print("\nText → image similarity matrix (rows = text, cols = images):")
    print(f"{'query':<40} " + " ".join(f"{lbl[:8]:>9}" for lbl, _ in image_parts))
    for q in text_queries:
        try:
            qv = embed(q)
            row = []
            for v in img_vecs:
                row.append(float(qv @ v) if v is not None else float("nan"))
            best = int(np.nanargmax(row)) if any(np.isfinite(row)) else -1
            row_str = " ".join(
                f"{(s if not np.isnan(s) else 0):>9.3f}{'*' if i == best else ' '}"
                for i, s in enumerate(row)
            )
            print(f"{q[:40]:<40} {row_str}")
        except Exception as exc:
            print(f"{q[:40]:<40}  ! {exc}")

    banner("Why this lands")
    print(
        "One embedding space across text + image (and audio, video, PDF).\n"
        "Drop a brand logo or hero shot; retrieve stylistically aligned\n"
        "stock content across photos, video, music tracks and 3D models."
    )


if __name__ == "__main__":
    main()
