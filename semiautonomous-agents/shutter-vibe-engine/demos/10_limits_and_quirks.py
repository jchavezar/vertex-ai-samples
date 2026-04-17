"""Demo 10 — Limits & quirks probe.

We deliberately poke the API:
  * how does it react to over-length input (autoTruncate behaviour)?
  * confirm Gemini Embedding 1 ↔ 2 vector spaces are *not* comparable
  * fused multi-input embedding on the multimodal model (text + image in one call)
  * raw HTTP response shape for production observability (token count)
"""
from __future__ import annotations

import io
import time

import numpy as np
from PIL import Image

from _client import CLIENT, MM_MODEL, TEXT_MODEL, banner
from google.genai import types


def main() -> None:
    banner("Demo 10 — limits & quirks")

    # --- 1. Over-length input ------------------------------------------------
    long_text = "An espresso is a small concentrated coffee. " * 700  # ~7000 tokens
    print(f"Submitting {len(long_text):,} chars to {TEXT_MODEL} (~7k tokens)…")
    try:
        t0 = time.perf_counter()
        resp = CLIENT.models.embed_content(model=TEXT_MODEL, contents=long_text)
        dur = time.perf_counter() - t0
        meta = resp.embeddings[0].statistics if hasattr(resp.embeddings[0], "statistics") else None
        print(f"  ✓ accepted, {dur:.2f}s, dim={len(resp.embeddings[0].values)}, statistics={meta}")
    except Exception as exc:
        print(f"  ! rejected: {exc}")

    # --- 2. Cross-model space incompatibility --------------------------------
    sample = "A serene Japanese tea ceremony"
    v1 = CLIENT.models.embed_content(model=TEXT_MODEL, contents=sample,
                                     config=types.EmbedContentConfig(output_dimensionality=768))
    v2 = CLIENT.models.embed_content(model=MM_MODEL, contents=sample,
                                     config=types.EmbedContentConfig(output_dimensionality=768))
    a = np.array(v1.embeddings[0].values, dtype=np.float32)
    b = np.array(v2.embeddings[0].values, dtype=np.float32)
    a /= np.linalg.norm(a); b /= np.linalg.norm(b)
    print(f"\ncos(gemini-embedding-001 vec, gemini-embedding-2-preview vec) on the SAME text = {a @ b:.4f}")
    print("  Expected: low — the spaces are documented as incompatible. Re-embed when migrating.")

    # --- 3. Fused multimodal: text + image → single vector ------------------
    img = Image.new("RGB", (128, 128), color=(20, 110, 180))  # blue swatch
    buf = io.BytesIO(); img.save(buf, format="PNG")
    fused = CLIENT.models.embed_content(
        model=MM_MODEL,
        contents=["A cool ocean blue palette",
                  types.Part.from_bytes(data=buf.getvalue(), mime_type="image/png")],
    )
    print(f"\nFused multimodal call returned {len(fused.embeddings)} embedding(s) "
          f"of dim {len(fused.embeddings[0].values)}")
    print("  Note: text + image in one `contents` list collapse to ONE fused vector.")

    # --- 4. Production observability -----------------------------------------
    r = CLIENT.models.embed_content(
        model=TEXT_MODEL,
        contents="usage metadata probe",
        config=types.EmbedContentConfig(output_dimensionality=768),
    )
    print("\nFull response metadata for production telemetry:")
    print(f"  metadata = {r.metadata}")
    print(f"  embedding stats = {getattr(r.embeddings[0], 'statistics', None)}")

    banner("Why this matters")
    print(
        "Knowing autoTruncate behaviour, cross-model incompatibility, fused\n"
        "multimodal collapse, and the response.metadata.token_count field is\n"
        "what separates a demo from a production design."
    )


if __name__ == "__main__":
    main()
