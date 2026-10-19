#!/usr/bin/env python3
"""Pre-render cinematic 16:9 guided walkthrough tours for the 108 Pillar 5 listings.

Why: rendering a tour live on Cloud Run (ffmpeg zoompan at 2x upscale, 25 s
timeout) left the "Render / Stream MP4" button spinning. These tours are built
offline once, uploaded to GCS, and served by a 302 redirect from
`/api/pillar5/listing-video/{id}` (see app.py) via `static/tours_manifest.json`.

What a tour looks like (1280x720, 30 fps, H.264, ~29 s):
  Front exterior -> Great room -> Kitchen -> Dining -> Primary suite ->
  Primary bath -> Rear patio / pool -> Aerial.
  * Every shot carries camera momentum into the next room: the camera decelerates
    out of the incoming move and accelerates into the outgoing one (push-in
    through a doorway, lateral dolly, crane up for the aerial).
  * Shots are joined by directional transitions in the walking direction:
    whip pans (motion-blurred slides) and zoom-through dissolves.
  * Lower-third room labels with dimensions, a floorplan mini-map with a moving
    "you are here" dot following the route, a progress rail, an opening title
    card and a closing Rocket card.

Usage:
  python3 render_tours.py                    # render every listing
  python3 render_tours.py RKT-098 RKT-001    # render a subset
  python3 render_tours.py --upload           # render all, upload, write manifest
  python3 render_tours.py --upload-only      # upload what is already rendered
"""

from __future__ import annotations

import argparse
import json
import math
import os
import subprocess
import sys
import time
import urllib.request
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
CATALOG = HERE / "catalog_108_index.json"
OUT_DIR = Path(os.environ.get("TOUR_OUT_DIR", "/tmp/rocket_tours_v1"))
IMG_CACHE = OUT_DIR / "_img"
GCS_PREFIX = "gs://vtxdemos-abnb-images/tours/v1"
PUBLIC_PREFIX = "https://storage.googleapis.com/vtxdemos-abnb-images/tours/v1"
MANIFEST = REPO / "static" / "tours_manifest.json"
TOUR_VERSION = "v1"

W, H, FPS = 1280, 720, 30
SHOT_S, XF_S = 4.2, 0.6
SHOT_F, XF_F = round(SHOT_S * FPS), round(XF_S * FPS)
STEP_F = SHOT_F - XF_F

RED = (216, 30, 40)
BLUE = (26, 115, 232)
INK = (9, 13, 22)

# (room_id, chapter label, transition into the NEXT room)
ROUTE = [
    ("ext_front", "Front Exterior", "push"),
    ("living_room", "Great Room", "right"),
    ("chef_kitchen", "Kitchen", "push"),
    ("dining_room", "Dining", "right"),
    ("primary_bedroom", "Primary Suite", "push"),
    ("primary_bathroom", "Primary Bath", "left"),
    ("ext_rear", "Rear Patio & Pool", "up"),
    ("ext_aerial", "Aerial", None),
]
N_SHOTS = len(ROUTE)
TOTAL_F = N_SHOTS * SHOT_F - (N_SHOTS - 1) * XF_F
DIRS = {"right": (1, 0, 0), "left": (-1, 0, 0), "up": (0, -1, 0), "push": (0, 0, 1), None: (0, 0, 0)}

# Same blueprint coordinates as the modal's "Interactive 2D/3D Floorplan" SVG (800x355 viewBox).
FP_BOXES = {
    "ext_rear": (20, 18, 413, 94, "PATIO & POOL"),
    "living_room": (20, 120, 220, 142, "GREAT ROOM"),
    "ext_front": (20, 270, 220, 65, "ENTRY"),
    "chef_kitchen": (248, 120, 185, 105, "KITCHEN"),
    "dining_room": (248, 233, 185, 102, "DINING"),
    "primary_bathroom": (441, 18, 145, 94, "BATH"),
    "primary_bedroom": (441, 120, 145, 117, "PRIMARY"),
    "home_office": (441, 245, 145, 90, "STUDY"),
    "guest_bathroom": (594, 265, 186, 70, "GUEST BATH"),
}
WAYPOINTS = [
    (130, 302), (130, 191), (340, 172), (340, 284),
    (513, 178), (513, 65), (226, 65), (400, 177),
]

FONT_DIRS = [
    Path(os.environ.get("TOUR_FONT_DIR", "")),
    HERE / "assets" / "fonts",
    Path("/usr/local/google/home/jesusarguelles/.gemini/jetski/brain/ff24b663-abf5-4da3-9f9c-732a11e04a65/scratch/worker_e/fonts"),
]


def _font(kind: str, size: int, weight: int = 700) -> ImageFont.FreeTypeFont:
    names = {"sans": "PJS.ttf", "mono": "JBM.ttf"}
    for d in FONT_DIRS:
        p = d / names[kind]
        if str(d) and p.exists():
            try:
                f = ImageFont.truetype(str(p), size)
                try:
                    f.set_variation_by_axes([weight])
                except Exception:
                    pass
                return f
            except Exception:
                pass
    fallback = {
        "sans": "/usr/share/fonts/truetype/roboto/unhinted/RobotoTTF/Roboto-Black.ttf" if weight >= 750
        else "/usr/share/fonts/truetype/roboto/unhinted/RobotoTTF/Roboto-Bold.ttf",
        "mono": "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
    }[kind]
    return ImageFont.truetype(fallback, size)


# ----------------------------------------------------------------------------
# Small helpers
# ----------------------------------------------------------------------------
def clamp01(x: float) -> float:
    return 0.0 if x < 0 else 1.0 if x > 1 else x


def smooth(x: float) -> float:
    x = clamp01(x)
    return x * x * (3 - 2 * x)


def ease_io(x: float) -> float:
    x = clamp01(x)
    return 4 * x * x * x if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2


def ease_out(x: float) -> float:
    x = clamp01(x)
    return 1 - (1 - x) ** 3


class Sprite:
    """Premultiplied RGBA overlay that can be blended into a float32 frame."""

    def __init__(self, im: Image.Image):
        a = np.asarray(im.convert("RGBA"), dtype=np.float32)
        self.a = a[..., 3:4] / 255.0
        self.rgb = a[..., :3] * self.a
        self.h, self.w = a.shape[:2]

    def blend(self, frame: np.ndarray, x: float, y: float, k: float = 1.0) -> None:
        if k <= 0.003:
            return
        x, y = int(round(x)), int(round(y))
        x0, y0 = max(x, 0), max(y, 0)
        x1, y1 = min(x + self.w, W), min(y + self.h, H)
        if x1 <= x0 or y1 <= y0:
            return
        sx, sy = x0 - x, y0 - y
        a = self.a[sy:sy + (y1 - y0), sx:sx + (x1 - x0)]
        rgb = self.rgb[sy:sy + (y1 - y0), sx:sx + (x1 - x0)]
        reg = frame[y0:y1, x0:x1]
        if k >= 0.997:
            reg *= 1.0 - a
            reg += rgb
        else:
            reg *= 1.0 - a * k
            reg += rgb * k


def rounded_panel(w: int, h: int, r: int, fill, outline=None, ss: int = 3) -> Image.Image:
    im = Image.new("RGBA", (w * ss, h * ss), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w * ss - 1, h * ss - 1), radius=r * ss, fill=fill,
                        outline=outline, width=ss if outline else 0)
    return im.resize((w, h), Image.Resampling.LANCZOS)


def hblur(arr: np.ndarray, r: int) -> np.ndarray:
    if r < 1:
        return arr
    k = 2 * r + 1
    pad = np.pad(arr, ((0, 0), (r + 1, r), (0, 0)), mode="edge")
    cs = np.cumsum(pad, axis=1, dtype=np.float32)
    return (cs[:, k:, :] - cs[:, :-k, :]) / k


def vblur(arr: np.ndarray, r: int) -> np.ndarray:
    if r < 1:
        return arr
    k = 2 * r + 1
    pad = np.pad(arr, ((r + 1, r), (0, 0), (0, 0)), mode="edge")
    cs = np.cumsum(pad, axis=0, dtype=np.float32)
    return (cs[k:, :, :] - cs[:-k, :, :]) / k


def truncate(text: str, font, max_w: int) -> str:
    if font.getlength(text) <= max_w:
        return text
    while text and font.getlength(text + "…") > max_w:
        text = text[:-1]
    return text.rstrip(" ·,&") + "…"


# ----------------------------------------------------------------------------
# Camera
# ----------------------------------------------------------------------------
def camera(i: int, u: float):
    """Camera (cx, cy, zoom) for shot i at normalized time u in [0, 1]."""
    d_in = DIRS[ROUTE[i - 1][2]] if i > 0 else DIRS["push"]
    d_out = DIRS[ROUTE[i][2]]
    in_k = (1.0 - min(u / 0.45, 1.0)) ** 2          # decelerating tail of the incoming move
    out_k = max(0.0, (u - 0.45) / 0.55) ** 2          # accelerating head of the outgoing move
    z = 1.20 - 0.10 * in_k * d_in[2] + 0.14 * out_k * d_out[2]
    if d_out[2] == 0:
        z += 0.035 * u                                 # gentle forward creep on lateral shots
    if ROUTE[i][2] is None:                            # finale: slow pull-back reveal
        z = 1.30 - 0.12 * smooth(u)
    cx = 0.5 - 0.055 * in_k * d_in[0] + 0.062 * out_k * d_out[0] + 0.014 * (u - 0.5) * d_out[0]
    cy = 0.5 - 0.055 * in_k * d_in[1] + 0.062 * out_k * d_out[1] + 0.014 * (u - 0.5) * d_out[1]
    half = 0.5 / z
    cx = min(max(cx, half), 1 - half)
    cy = min(max(cy, half), 1 - half)
    return cx, cy, z


def render_cam(img: Image.Image, cx: float, cy: float, z: float) -> np.ndarray:
    iw, ih = img.size
    ww, wh = iw / z, ih / z
    x0, y0 = cx * iw - ww / 2, cy * ih - wh / 2
    out = img.transform((W, H), Image.Transform.EXTENT, (x0, y0, x0 + ww, y0 + wh),
                        resample=Image.Resampling.BICUBIC)
    return np.asarray(out, dtype=np.float32)


def shot_frame(imgs, i: int, local_f: int, extra_zoom: float = 1.0) -> np.ndarray:
    u = local_f / (SHOT_F - 1)
    cx, cy, z = camera(i, u)
    return render_cam(imgs[i], cx, cy, z * extra_zoom)


def transition(imgs, i: int, v: float, old_lf: int, new_lf: int) -> np.ndarray:
    kind = ROUTE[i][2]
    if kind == "push":
        zb = 1.0 + 0.85 * v * v
        old = (shot_frame(imgs, i, old_lf, zb) * 0.5
               + shot_frame(imgs, i, old_lf, zb * 1.045) * 0.3
               + shot_frame(imgs, i, old_lf, zb * 1.09) * 0.2)
        new = shot_frame(imgs, i + 1, new_lf)
        a = smooth((v - 0.12) / 0.72)
        comp = old * (1 - a) + new * a
        comp += 34.0 * math.sin(math.pi * v)           # light bloom through the doorway
        return comp
    old = shot_frame(imgs, i, old_lf)
    new = shot_frame(imgs, i + 1, new_lf)
    s = ease_io(v)
    comp = np.empty_like(old)
    if kind in ("right", "left"):
        off = int(round(s * W))
        if kind == "right":
            comp[:, :W - off] = old[:, off:]
            comp[:, W - off:] = new[:, :off]
        else:
            comp[:, off:] = old[:, :W - off]
            comp[:, :off] = new[:, W - off:]
        return hblur(comp, int(round(64 * math.sin(math.pi * v))))
    off = int(round(s * H))                              # "up": crane / tilt, content moves down
    comp[off:, :] = old[:H - off, :]
    comp[:off, :] = new[H - off:, :]
    return vblur(comp, int(round(46 * math.sin(math.pi * v))))


# ----------------------------------------------------------------------------
# Overlays
# ----------------------------------------------------------------------------
def build_static_overlays(item: dict, rooms: dict):
    ov = {}
    # Bottom gradient for lower-third legibility
    g = Image.new("RGBA", (W, 240), (0, 0, 0, 0))
    ga = np.zeros((240, W, 4), np.uint8)
    ga[..., :3] = INK
    ga[..., 3] = (np.linspace(0, 1, 240) ** 1.6 * 175).astype(np.uint8)[:, None]
    g = Image.fromarray(ga, "RGBA")
    ov["grad"] = Sprite(g)

    # Brand chip (top-left)
    f_chip = _font("mono", 13, 700)
    txt = f"CINEMATIC TOUR  ·  {item['id']}"
    cw = int(f_chip.getlength(txt)) + 46
    chip = rounded_panel(cw, 32, 16, (9, 13, 22, 196), outline=(255, 255, 255, 40))
    d = ImageDraw.Draw(chip)
    d.ellipse((14, 11, 24, 21), fill=RED + (255,))
    d.text((32, 8), txt, font=f_chip, fill=(248, 250, 252, 255))
    ov["chip"] = Sprite(chip)

    # Title card (first shot)
    f_k = _font("mono", 15, 700)
    f_t = _font("sans", 44, 800)
    f_s = _font("sans", 20, 600)
    tw = 760
    title = item.get("title", "")
    words, lines, cur = title.split(), [], ""
    for wd in words:
        trial = (cur + " " + wd).strip()
        if f_t.getlength(trial) <= tw:
            cur = trial
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    lines = lines[:2]
    if len(lines) == 2:
        lines[1] = truncate(lines[1], f_t, tw)
    card = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    va = np.zeros((H, W, 4), np.uint8)
    va[..., :3] = INK
    va[..., 3] = (np.clip(1.0 - np.linspace(0, 1, W) / 0.75, 0, 1) ** 1.4 * 190).astype(np.uint8)[None, :]
    card = Image.fromarray(va, "RGBA")
    d = ImageDraw.Draw(card)
    y = 250
    d.rectangle((64, y, 64 + 54, y + 4), fill=RED + (255,))
    y += 18
    d.text((64, y), f"{item['id']}  ·  {item.get('city', '')}".upper(), font=f_k, fill=(203, 213, 225, 255))
    y += 30
    for ln in lines:
        d.text((64, y), ln, font=f_t, fill=(255, 255, 255, 255))
        y += 54
    y += 8
    price = f"${int(item.get('price', 0)):,}"
    specs = f"{price}   ·   {item.get('beds')} BD   ·   {item.get('baths')} BA   ·   {int(item.get('sqft', 0)):,} sq ft"
    d.text((64, y), specs, font=f_s, fill=(241, 245, 249, 255))
    ov["title"] = Sprite(card)

    # End card (last shot)
    f_e1 = _font("mono", 14, 700)
    f_e2 = _font("sans", 34, 800)
    f_e3 = _font("sans", 18, 600)
    ew, eh = 620, 176
    end = rounded_panel(ew, eh, 20, (9, 13, 22, 214), outline=(255, 255, 255, 46))
    d = ImageDraw.Draw(end)
    d.rectangle((32, 30, 32 + 46, 33), fill=RED + (255,))
    d.text((32, 44), "TOUR COMPLETE  ·  ROCKET MORTGAGE", font=f_e1, fill=(203, 213, 225, 255))
    d.text((32, 70), f"Verified PITI ${int(item.get('monthly_piti', 0)):,}/mo", font=f_e2, fill=(255, 255, 255, 255))
    d.text((32, 122), f"+${int(item.get('closing_credit', 0)):,} closing credit  ·  {item.get('rate_pct')}% 30-yr fixed",
           font=f_e3, fill=(167, 243, 208, 255))
    ov["end"] = Sprite(end)

    # Lower thirds (one per shot)
    f_kick = _font("mono", 13, 700)
    f_main = _font("sans", 30, 800)
    f_dim = _font("mono", 15, 600)
    lts = []
    for idx, (rid, label, _) in enumerate(ROUTE):
        r = rooms.get(rid, {})
        raw = (r.get("title") or label).strip()
        if rid == "ext_front":
            main, sub = "Front Elevation", raw.split("·", 1)[-1].strip()
        elif rid.startswith("ext_"):
            main, sub = raw.split("·", 1)[-1].strip(), ""
        else:
            main, sub = (raw.split("·", 1)[-1].strip() if raw.lower().startswith("bedroom 1") else raw), ""
        level = (r.get("level") or "").upper()
        kick = f"{idx + 1:02d} / {N_SHOTS:02d}" + (f"  ·  {level}" if level else "")
        dims = (r.get("dimensions") or "").strip()
        if sub:
            dims = f"{dims}  ·  {sub}" if dims else sub
        main = truncate(main, f_main, 640)
        dims = truncate(dims, f_dim, 640)
        pw = int(max(f_main.getlength(main), f_dim.getlength(dims), f_kick.getlength(kick))) + 64
        ph = 104
        lt = rounded_panel(pw, ph, 14, (9, 13, 22, 206), outline=(255, 255, 255, 34))
        d = ImageDraw.Draw(lt)
        d.rounded_rectangle((0, 0, 5, ph - 1), radius=2, fill=RED + (255,))
        d.text((26, 14), kick, font=f_kick, fill=(248, 113, 113, 255))
        d.text((26, 34), main, font=f_main, fill=(255, 255, 255, 255))
        d.text((26, 74), dims, font=f_dim, fill=(203, 213, 225, 255))
        lts.append(Sprite(lt))
    ov["lt"] = lts
    return ov


class MiniMap:
    S = 0.35  # 800x355 blueprint -> 280x124

    def __init__(self, item: dict):
        self.pad = 12
        self.head = 24
        self.mw, self.mh = int(800 * self.S), int(355 * self.S)
        self.pw, self.ph = self.mw + self.pad * 2, self.mh + self.head + self.pad + 4
        self.x, self.y = W - 20 - self.pw, 20
        ss = 3
        base = Image.new("RGBA", (self.pw * ss, self.ph * ss), (0, 0, 0, 0))
        d = ImageDraw.Draw(base)
        d.rounded_rectangle((0, 0, self.pw * ss - 1, self.ph * ss - 1), radius=14 * ss,
                            fill=(9, 13, 22, 200), outline=(255, 255, 255, 46), width=ss)
        boxes = dict(FP_BOXES)
        beds = int(item.get("beds", 3) or 3)
        extra = max(1, beds - 1)
        slot_h = int((238 - (extra - 1) * 6) / extra)
        for b in range(2, beds + 1):
            boxes[f"bedroom_{b}"] = (594, 18 + (b - 2) * (slot_h + 6), 186, slot_h, f"BR {b}")
        self.boxes = boxes
        f_lbl = _font("mono", 8 * ss, 700)
        for rid, (bx, by, bw, bh, lbl) in boxes.items():
            x0, y0 = self._pt(bx, by, ss)
            x1, y1 = self._pt(bx + bw, by + bh, ss)
            on_route = any(rid == r[0] for r in ROUTE)
            d.rounded_rectangle((x0 + ss, y0 + ss, x1 - ss, y1 - ss), radius=3 * ss,
                                fill=(30, 41, 59, 235) if on_route else (22, 30, 44, 220),
                                outline=(100, 116, 139, 200), width=ss)
            tw = d.textlength(lbl, font=f_lbl)
            if tw < (x1 - x0) - 6 * ss and (y1 - y0) > 12 * ss:
                d.text(((x0 + x1) / 2 - tw / 2, (y0 + y1) / 2 - 5 * ss), lbl, font=f_lbl, fill=(148, 163, 184, 255))
        pts = [self._pt(px, py, ss) for px, py in WAYPOINTS]
        for a, b in zip(pts[:-1], pts[1:]):
            self._dashed(d, a, b, (148, 163, 184, 150), ss)
        f_h = _font("mono", 10 * ss, 700)
        d.text((self.pad * ss, 7 * ss), "FLOOR PLAN  ·  YOU ARE HERE", font=f_h, fill=(226, 232, 240, 255))
        d.ellipse(((self.pw - 22) * ss, 9 * ss, (self.pw - 14) * ss, 17 * ss), fill=RED + (255,))
        self.base = base.resize((self.pw, self.ph), Image.Resampling.LANCZOS)
        self.pts = [self._pt(px, py, 1) for px, py in WAYPOINTS]
        # dot + pulse sprites (anti-aliased)
        self.dot = self._disc(9, RED, ring=True)
        self.pulses = []
        for k in range(24):
            ph = k / 24
            r = 6 + 13 * ph
            a = int(200 * (1 - ph) ** 1.5)
            self.pulses.append(self._ring(r, a))

    def _pt(self, px, py, ss):
        return ((self.pad + px * self.S) * ss, (self.head + py * self.S) * ss)

    @staticmethod
    def _dashed(d, a, b, fill, ss):
        (x0, y0), (x1, y1) = a, b
        L = math.hypot(x1 - x0, y1 - y0)
        n = max(1, int(L / (6 * ss)))
        for k in range(0, n, 2):
            t0, t1 = k / n, min(1.0, (k + 1) / n)
            d.line((x0 + (x1 - x0) * t0, y0 + (y1 - y0) * t0, x0 + (x1 - x0) * t1, y0 + (y1 - y0) * t1),
                   fill=fill, width=int(1.4 * ss))

    @staticmethod
    def _disc(r, color, ring=False):
        ss = 4
        sz = int((r * 2 + 10) * ss)
        im = Image.new("RGBA", (sz, sz), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        c = sz / 2
        glow = Image.new("RGBA", (sz, sz), (0, 0, 0, 0))
        gd = ImageDraw.Draw(glow)
        gd.ellipse((c - (r + 4) * ss, c - (r + 4) * ss, c + (r + 4) * ss, c + (r + 4) * ss), fill=color + (150,))
        glow = glow.filter(ImageFilter.GaussianBlur(4 * ss))
        im = Image.alpha_composite(im, glow)
        d = ImageDraw.Draw(im)
        d.ellipse((c - r * ss / 1.6, c - r * ss / 1.6, c + r * ss / 1.6, c + r * ss / 1.6),
                  fill=color + (255,), outline=(255, 255, 255, 255), width=int(2 * ss))
        return im.resize((sz // ss, sz // ss), Image.Resampling.LANCZOS)

    @staticmethod
    def _ring(r, alpha):
        ss = 4
        sz = int((r * 2 + 6) * ss)
        im = Image.new("RGBA", (sz, sz), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        c = sz / 2
        d.ellipse((c - r * ss, c - r * ss, c + r * ss, c + r * ss), outline=RED + (alpha,), width=int(1.6 * ss))
        return im.resize((sz // ss, sz // ss), Image.Resampling.LANCZOS)

    def frame(self, p: float, cur_room: str, f: int, aerial_k: float) -> Sprite:
        im = self.base.copy()
        d = ImageDraw.Draw(im)
        if cur_room in self.boxes:
            bx, by, bw, bh, _ = self.boxes[cur_room]
            x0, y0 = self._pt(bx, by, 1)
            x1, y1 = self._pt(bx + bw, by + bh, 1)
            d.rounded_rectangle((x0 + 1, y0 + 1, x1 - 1, y1 - 1), radius=3, outline=RED + (255,), width=2,
                                fill=(216, 30, 40, 52))
        if aerial_k > 0:
            x0, y0 = self._pt(20, 18, 1)
            x1, y1 = self._pt(780, 335, 1)
            d.rounded_rectangle((x0 - 2, y0 - 2, x1 + 2, y1 + 2), radius=6,
                                outline=RED + (int(255 * aerial_k),), width=2)
        k = int(math.floor(p))
        frac = p - k
        trail = self.pts[:k + 1]
        if k + 1 < len(self.pts):
            a, b = self.pts[k], self.pts[k + 1]
            pos = (a[0] + (b[0] - a[0]) * frac, a[1] + (b[1] - a[1]) * frac)
        else:
            pos = self.pts[-1]
        trail = trail + [pos]
        if len(trail) >= 2:
            d.line(trail, fill=RED + (235,), width=3, joint="curve")
        pulse = self.pulses[(f // 2) % len(self.pulses)]
        im.alpha_composite(pulse, (int(round(pos[0] - pulse.width / 2)), int(round(pos[1] - pulse.height / 2))))
        im.alpha_composite(self.dot, (int(round(pos[0] - self.dot.width / 2)), int(round(pos[1] - self.dot.height / 2))))
        return Sprite(im)


# ----------------------------------------------------------------------------
# Rendering
# ----------------------------------------------------------------------------
def _fetch(url: str, dest: Path) -> Path | None:
    if dest.exists() and dest.stat().st_size > 2000:
        return dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "rocket-tour-renderer/1.0"})
            with urllib.request.urlopen(req, timeout=30) as r:
                data = r.read()
            if len(data) > 2000:
                tmp = dest.with_suffix(".part")
                tmp.write_bytes(data)
                tmp.replace(dest)
                return dest
        except Exception:
            time.sleep(0.6 * (attempt + 1))
    return None


def _cover(img: Image.Image) -> Image.Image:
    img = img.convert("RGB")
    iw, ih = img.size
    target = W / H
    if abs(iw / ih - target) > 0.01:
        if iw / ih > target:
            nw = int(ih * target)
            img = img.crop(((iw - nw) // 2, 0, (iw - nw) // 2 + nw, ih))
        else:
            nh = int(iw / target)
            img = img.crop((0, (ih - nh) // 2, iw, (ih - nh) // 2 + nh))
    if img.size != (W, H):
        img = img.resize((W, H), Image.Resampling.LANCZOS)
    return img


def chapter_times():
    out = []
    for i, (rid, label, _) in enumerate(ROUTE):
        t = 0.0 if i == 0 else (i * STEP_F + XF_F / 2) / FPS
        out.append({"room_id": rid, "title": label, "t": round(t, 2)})
    return out


def render_listing(item: dict, out_dir: Path = OUT_DIR, crf: int = 22) -> dict:
    t0 = time.time()
    lid = item["id"]
    rooms = {r.get("room_id"): r for r in item.get("rooms", [])}
    imgs = []
    fallback_pool = [r.get("image_url") for r in item.get("rooms", []) if r.get("image_url")]
    for idx, (rid, _, _) in enumerate(ROUTE):
        url = (rooms.get(rid) or {}).get("image_url") or (fallback_pool[idx % len(fallback_pool)] if fallback_pool else None)
        p = _fetch(url, IMG_CACHE / lid / f"{rid}.jpg") if url else None
        if p is None:
            raise RuntimeError(f"{lid}: missing image for {rid}")
        imgs.append(_cover(Image.open(p)))

    ov = build_static_overlays(item, rooms)
    mm = MiniMap(item)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_mp4 = out_dir / f"{lid}_16x9.mp4"
    tmp_mp4 = out_dir / f"{lid}_16x9.tmp.mp4"
    poster = out_dir / f"{lid}_poster.jpg"
    cmd = [
        "ffmpeg", "-y", "-loglevel", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
        "-c:v", "libx264", "-preset", "medium", "-crf", str(crf), "-maxrate", "6M", "-bufsize", "12M",
        "-pix_fmt", "yuv420p", "-profile:v", "high", "-level", "4.0", "-g", str(FPS * 2),
        "-movflags", "+faststart", "-threads", "2", "-f", "mp4", str(tmp_mp4),
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    lt_x, lt_y = 40, H - 40 - 104
    try:
        for f in range(TOTAL_F):
            active = [i for i in range(N_SHOTS) if i * STEP_F <= f < i * STEP_F + SHOT_F]
            if len(active) == 2:
                i = active[0]
                v = (f - active[1] * STEP_F + 0.5) / XF_F
                frame = transition(imgs, i, v, f - i * STEP_F, f - active[1] * STEP_F)
                cur_i = i if v < 0.5 else i + 1
                p = i + 0.22 + 0.78 * ease_io(v)
            else:
                i = active[0]
                lf = f - i * STEP_F
                frame = shot_frame(imgs, i, lf)
                cur_i = i
                u = lf / (SHOT_F - 1)
                p = float(i) + (0.22 * max(0.0, (u - 0.62) / 0.38) ** 2 if i < N_SHOTS - 1 else 0.0)
            np.clip(frame, 0, 255, out=frame)

            ov["grad"].blend(frame, 0, H - 240)
            # Opening title card + closing card
            t = f / FPS
            if t < 3.0:
                k = smooth((t - 0.15) / 0.5) * (1 - smooth((t - 2.25) / 0.55))
                ov["title"].blend(frame, -24 * (1 - smooth((t - 0.15) / 0.6)), 0, k)
            ov["chip"].blend(frame, 20, 20)
            t_end = (TOTAL_F - f) / FPS
            if t_end < 1.9:
                k = smooth((1.9 - t_end) / 0.45)
                ov["end"].blend(frame, (W - ov["end"].w) / 2, (H - ov["end"].h) / 2 + 30 * (1 - k), k)
            # Lower third for the current shot
            for j in active:
                lf = f - j * STEP_F
                start = XF_F + 4 if j > 0 else int(2.55 * FPS)
                stop = SHOT_F - XF_F - 4 if j < N_SHOTS - 1 else SHOT_F - int(2.0 * FPS)
                if start <= lf <= stop:
                    a_in = ease_out((lf - start) / (0.45 * FPS))
                    a_out = 1 - smooth((lf - (stop - 0.3 * FPS)) / (0.3 * FPS))
                    ov["lt"][j].blend(frame, lt_x - 46 * (1 - a_in), lt_y, min(a_in, a_out))
            # Mini-map + route dot
            aerial_k = smooth((f - (N_SHOTS - 1) * STEP_F) / XF_F) if f >= (N_SHOTS - 1) * STEP_F else 0.0
            mm.frame(min(p, N_SHOTS - 1), ROUTE[cur_i][0], f, aerial_k).blend(frame, mm.x, mm.y)
            # Progress rail
            frame[H - 4:H, :, :] = frame[H - 4:H, :, :] * 0.55 + 255 * 0.12
            pw = int(W * (f + 1) / TOTAL_F)
            frame[H - 4:H, :pw, :] = RED
            for c in chapter_times()[1:]:
                tx = int(W * c["t"] * FPS / TOTAL_F)
                frame[H - 6:H, max(0, tx - 1):tx + 1, :] = 255

            out = frame.astype(np.uint8)
            if f == int(1.6 * FPS):
                Image.fromarray(out).save(poster, quality=84, optimize=True)
            proc.stdin.write(out.tobytes())
        proc.stdin.close()
        rc = proc.wait(timeout=600)
    except Exception:
        proc.kill()
        raise
    if rc != 0 or not tmp_mp4.exists():
        raise RuntimeError(f"{lid}: ffmpeg exit {rc}")
    tmp_mp4.replace(out_mp4)
    return {
        "id": lid,
        "file": str(out_mp4),
        "poster_file": str(poster),
        "bytes": out_mp4.stat().st_size,
        "duration_s": round(TOTAL_F / FPS, 2),
        "chapters": chapter_times(),
        "render_s": round(time.time() - t0, 1),
    }


def _render_safe(item):
    try:
        return render_listing(item)
    except Exception as e:  # keep the batch going
        return {"id": item.get("id"), "error": repr(e)}


def upload_and_write_manifest(results: list[dict]) -> dict:
    ok = [r for r in results if not r.get("error") and Path(r["file"]).exists()]
    files = [r["file"] for r in ok] + [r["poster_file"] for r in ok if Path(r["poster_file"]).exists()]
    if files:
        cmd = ["gcloud", "storage", "cp", *files, GCS_PREFIX + "/",
               "--cache-control=public, max-age=86400", "--project=vtxdemos"]
        subprocess.run(cmd, check=True)
    stamp = time.strftime("%Y%m%d%H%M")
    manifest = {}
    if MANIFEST.exists():
        try:
            manifest = json.loads(MANIFEST.read_text())
        except Exception:
            manifest = {}
    for r in ok:
        lid = r["id"]
        manifest[lid] = {
            "url": f"{PUBLIC_PREFIX}/{lid}_16x9.mp4?v={stamp}",
            "poster": f"{PUBLIC_PREFIX}/{lid}_poster.jpg?v={stamp}",
            "duration_s": r["duration_s"],
            "kind": "cinematic",
            "model": f"rocket-cinematic-tour-{TOUR_VERSION}",
            "width": W,
            "height": H,
            "fps": FPS,
            "bytes": r["bytes"],
            "chapters": r["chapters"],
        }
    manifest = dict(sorted(manifest.items()))
    MANIFEST.write_text(json.dumps(manifest, indent=1))
    return manifest


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ids", nargs="*")
    ap.add_argument("--workers", type=int, default=30)
    ap.add_argument("--upload", action="store_true")
    ap.add_argument("--upload-only", action="store_true")
    args = ap.parse_args()
    cat = json.loads(CATALOG.read_text())
    items = cat.get("announcements", [])
    if args.ids:
        want = set(args.ids)
        items = [x for x in items if x.get("id") in want]
    results = []
    if args.upload_only:
        for it in items:
            mp4 = OUT_DIR / f"{it['id']}_16x9.mp4"
            if mp4.exists():
                results.append({"id": it["id"], "file": str(mp4), "poster_file": str(OUT_DIR / f"{it['id']}_poster.jpg"),
                                "bytes": mp4.stat().st_size, "duration_s": round(TOTAL_F / FPS, 2),
                                "chapters": chapter_times()})
    else:
        t0 = time.time()
        with ProcessPoolExecutor(max_workers=max(1, min(args.workers, len(items)))) as ex:
            futs = [ex.submit(_render_safe, it) for it in items]
            for fu in as_completed(futs):
                r = fu.result()
                results.append(r)
                status = r.get("error") or f"{r['bytes'] / 1e6:.1f} MB in {r['render_s']} s"
                print(f"[{len(results):3d}/{len(items)}] {r['id']}: {status}", flush=True)
        print(f"rendered {sum(1 for r in results if not r.get('error'))}/{len(items)} in {time.time() - t0:.0f} s", flush=True)
    if args.upload or args.upload_only:
        m = upload_and_write_manifest(results)
        print(f"manifest: {len(m)} tours -> {MANIFEST}", flush=True)


if __name__ == "__main__":
    main()
