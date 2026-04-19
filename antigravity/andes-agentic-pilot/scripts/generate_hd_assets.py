"""
Generate HD hero/section assets for the Caja Los Andes (CCLA) demo.

This script calls Vertex AI Imagen 4 (us-central1) to render high-resolution
imagery for the static parts of the frontend, then stamps each PNG with a
discrete watermark identifying the generator (Gemini / Nano Banana).

Output: frontend/public/images/generated/*.png

Run from anywhere - paths are absolute. Requires:
  - gcloud ADC (gcloud auth application-default login)
  - Pillow >= 10
  - requests
"""

from __future__ import annotations

import base64
import io
import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

import requests
from PIL import Image, ImageDraw, ImageFilter, ImageFont

PROJECT = os.getenv("VERTEX_PROJECT", "vtxdemos")
LOCATION = "us-central1"
MODEL = "imagen-4.0-generate-001"
ENDPOINT = (
    f"https://{LOCATION}-aiplatform.googleapis.com/v1/projects/{PROJECT}"
    f"/locations/{LOCATION}/publishers/google/models/{MODEL}:predict"
)

OUT_DIR = str(
    (Path(__file__).resolve().parent.parent / "frontend/public/images/generated")
)
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

WATERMARK_TEXT = "Generado con Gemini  |  Nano Banana"


@dataclass
class Spec:
    """One image to render."""

    slug: str
    aspect: str  # "16:9" | "4:3" | "1:1" | "3:4" | "9:16"
    target_w: int  # final upscaled width (px)
    target_h: int  # final upscaled height (px)
    prompt: str


SPECS: list[Spec] = [
    Spec(
        slug="hero-familia",
        aspect="16:9",
        target_w=2400,
        target_h=1350,
        prompt=(
            "Premium editorial photograph, ultra detailed, soft natural window light. "
            "A diverse multi-generational Chilean family at home in Santiago: parents "
            "in their late 30s, two children (a 7-year-old girl and a 12-year-old boy) "
            "and an abuela in her late 60s, gathered together on a warm linen sofa "
            "in a bright modern living room. They are smiling, relaxed, sharing a "
            "moment together. Behind them, large windows reveal a soft hint of the "
            "Andes mountains at golden hour. Warm earth tones with subtle sky-blue "
            "accents, shallow depth of field, 50mm lens, photographed by an award "
            "winning lifestyle photographer. Optimistic, dignified, contemporary. "
            "No text, no logos, no watermark."
        ),
    ),
    Spec(
        slug="credito-hipotecario",
        aspect="16:9",
        target_w=2400,
        target_h=1350,
        prompt=(
            "Premium real-estate lifestyle photograph. A young Chilean couple in "
            "their early 30s standing in front of the door of their new modest, "
            "well-built suburban house in central Chile. The husband is holding a "
            "set of keys up to the camera, both are smiling with genuine relief and "
            "joy. Daylight, soft shadows, neighborhood of warm beige and white "
            "houses, small front garden, real Chilean residential architecture. "
            "Aspirational but realistic, middle-class, dignified. Slight cinematic "
            "color grade, shallow depth of field, 35mm lens. No text, no logos, "
            "no watermark."
        ),
    ),
    Spec(
        slug="bodas-de-oro",
        aspect="16:9",
        target_w=2400,
        target_h=1350,
        prompt=(
            "Documentary-style portrait, golden warm light. A Chilean elderly "
            "couple in their early 70s celebrating their 50th wedding anniversary "
            "(Bodas de Oro). They are embracing tenderly in a softly lit dining "
            "room, looking at each other with affection. The wife wears a simple "
            "elegant dress, the husband a button-up shirt. Soft bokeh in the "
            "background suggests family around a dinner table with flowers and "
            "candlelight. Warm, emotional, full of dignity. Cinematic photo-real, "
            "85mm lens, shallow depth of field, color grade in soft amber and rose. "
            "No text, no logos, no watermark."
        ),
    ),
    Spec(
        slug="becas-educacion",
        aspect="16:9",
        target_w=2400,
        target_h=1350,
        prompt=(
            "Modern educational lifestyle photograph. A Chilean university student "
            "in their early 20s, casual sweater, sitting at a sunlit shared study "
            "table with an open laptop and notebook. They are smiling slightly, "
            "focused, taking notes. In the soft-focus background, a bright modern "
            "Chilean university library or campus space with other students out of "
            "focus. Natural daylight from large windows, optimistic atmosphere. "
            "35mm lens, shallow depth of field, contemporary color grade. "
            "No text, no logos, no watermark."
        ),
    ),
    Spec(
        slug="turismo-cordillera",
        aspect="16:9",
        target_w=2400,
        target_h=1350,
        prompt=(
            "Wide cinematic landscape photograph of the Chilean Andes at golden "
            "hour: snow-capped peaks, a calm alpine lake in the foreground, a "
            "small Chilean family of four (parents + two kids) silhouetted on a "
            "wooden lookout deck, standing close together and admiring the view. "
            "Style of National Geographic travel photography, shot on full-frame "
            "with a 24mm lens, deep clarity, rich blues and warm orange "
            "highlights, no people in front of the camera. No text, no logos, "
            "no watermark."
        ),
    ),
    Spec(
        slug="andesia-orb",
        aspect="1:1",
        target_w=1600,
        target_h=1600,
        prompt=(
            "Minimalist abstract 3D render of a glowing translucent sphere made "
            "of soft cyan and deep blue plasma energy, with subtle interior "
            "swirls suggesting a mountain range silhouette. The sphere floats "
            "centered on a clean dark navy background with a gentle radial glow "
            "and soft drifting particles. Premium calm fintech aesthetic, "
            "friendly assistant brand mark, octane render, soft volumetric "
            "lighting, deep navy and electric cyan palette."
        ),
    ),
]


def _access_token() -> str:
    """Pull an OAuth token using application default credentials."""
    out = subprocess.check_output(
        ["gcloud", "auth", "application-default", "print-access-token"],
        text=True,
    ).strip()
    if not out:
        raise RuntimeError("empty access token from gcloud")
    return out


def _imagen_call(prompt: str, aspect: str, token: str) -> bytes:
    """Call Imagen 4, return raw PNG bytes for the first sample."""
    body = {
        "instances": [{"prompt": prompt}],
        "parameters": {
            "sampleCount": 1,
            "aspectRatio": aspect,
            # safetySetting: keep defaults (block_some) so we don't tank quality
            "personGeneration": "allow_adult",
            "addWatermark": False,  # we add our own visible "Nano Banana" mark
        },
    }
    resp = requests.post(
        ENDPOINT,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        data=json.dumps(body),
        timeout=180,
    )
    if resp.status_code != 200:
        raise RuntimeError(
            f"Imagen HTTP {resp.status_code}: {resp.text[:400]}"
        )
    payload = resp.json()
    preds = payload.get("predictions") or []
    if not preds:
        raise RuntimeError(f"Imagen returned no predictions: {payload}")
    b64 = preds[0].get("bytesBase64Encoded")
    if not b64:
        raise RuntimeError(f"Imagen prediction missing image: {preds[0]}")
    return base64.b64decode(b64)


def _add_watermark(img: Image.Image, text: str) -> Image.Image:
    """Stamp a discrete pill-shaped watermark in the bottom-right corner."""
    img = img.convert("RGBA")
    w, h = img.size

    # Font size: ~2.2% of height, capped to a sensible range.
    font_size = max(16, min(int(h * 0.022), 42))
    try:
        font = ImageFont.truetype(FONT_BOLD, font_size)
    except OSError:
        font = ImageFont.load_default()

    # Measure
    tmp = Image.new("RGBA", (10, 10))
    bbox = ImageDraw.Draw(tmp).textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]

    pad_x = int(font_size * 0.95)
    pad_y = int(font_size * 0.55)
    pill_w = tw + pad_x * 2
    pill_h = th + pad_y * 2
    margin = int(h * 0.025)

    pill = Image.new("RGBA", (pill_w, pill_h), (0, 0, 0, 0))
    pdraw = ImageDraw.Draw(pill)
    radius = pill_h // 2
    pdraw.rounded_rectangle(
        (0, 0, pill_w - 1, pill_h - 1),
        radius=radius,
        fill=(10, 18, 38, 170),  # deep navy, semi-transparent
        outline=(255, 255, 255, 90),
        width=1,
    )

    # Tiny gemini-style sparkle dot before text
    dot_d = max(6, font_size // 3)
    dot_x = pad_x - dot_d - max(4, font_size // 6)
    dot_y = (pill_h - dot_d) // 2
    if dot_x > 4:
        pdraw.ellipse(
            (dot_x, dot_y, dot_x + dot_d, dot_y + dot_d),
            fill=(0, 184, 217, 255),
        )

    pdraw.text(
        (pad_x, pad_y - bbox[1]),
        text,
        font=font,
        fill=(255, 255, 255, 235),
    )

    # Soft drop shadow behind the pill so it pops on busy images.
    shadow = Image.new("RGBA", (pill_w + 20, pill_h + 20), (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(shadow)
    sdraw.rounded_rectangle(
        (10, 10, pill_w + 9, pill_h + 9),
        radius=radius,
        fill=(0, 0, 0, 110),
    )
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=6))

    px = w - pill_w - margin
    py = h - pill_h - margin
    img.alpha_composite(shadow, (px - 10, py - 10))
    img.alpha_composite(pill, (px, py))
    return img.convert("RGB")


def _resize_cover(img: Image.Image, target_w: int, target_h: int) -> Image.Image:
    """Upscale to >= target then center-crop to exact target_w x target_h."""
    src_w, src_h = img.size
    scale = max(target_w / src_w, target_h / src_h)
    if scale > 1.0:
        new_w = int(round(src_w * scale))
        new_h = int(round(src_h * scale))
        img = img.resize((new_w, new_h), Image.LANCZOS)
    # center-crop
    cw, ch = img.size
    left = (cw - target_w) // 2
    top = (ch - target_h) // 2
    return img.crop((left, top, left + target_w, top + target_h))


def render_one(spec: Spec, token: str) -> str:
    raw = _imagen_call(spec.prompt, spec.aspect, token)
    img = Image.open(io.BytesIO(raw))
    img = _resize_cover(img, spec.target_w, spec.target_h)
    img = _add_watermark(img, WATERMARK_TEXT)
    out_path = os.path.join(OUT_DIR, f"{spec.slug}.png")
    img.save(out_path, format="PNG", optimize=True)
    return out_path


def main() -> int:
    os.makedirs(OUT_DIR, exist_ok=True)
    token = _access_token()
    print(f"[ok] auth OK, writing to {OUT_DIR}", flush=True)
    print(f"[ok] model: {MODEL}", flush=True)

    only = set(sys.argv[1:])  # optional slug filter
    failed: list[tuple[str, str]] = []
    for spec in SPECS:
        if only and spec.slug not in only:
            continue
        t0 = time.time()
        try:
            path = render_one(spec, token)
            dt = time.time() - t0
            sz = os.path.getsize(path) / 1024
            print(
                f"[ok] {spec.slug:<22} {spec.aspect}  "
                f"{spec.target_w}x{spec.target_h}  "
                f"{dt:5.1f}s  {sz:6.1f} KB  -> {path}",
                flush=True,
            )
        except Exception as exc:  # noqa: BLE001 - we want any failure logged
            print(f"[FAIL] {spec.slug}: {exc}", flush=True)
            failed.append((spec.slug, str(exc)))

    if failed:
        print(f"\n{len(failed)} failed:", flush=True)
        for slug, err in failed:
            print(f"  - {slug}: {err[:200]}", flush=True)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
