#!/usr/bin/env python3
"""
Renders high-resolution Pixel 11 Pro hardware-framed screenshots from
`mock_showcase/pixel11_whatsapp_showcase.html` using a headless browser batch runner.
"""
import json
import os
import subprocess
from pathlib import Path

GBROWSER_BIN = os.environ.get("HEADLESS_BROWSER_BIN", "gbrowser")
BASE_DIR = Path(__file__).resolve().parent.parent
HTML_PATH = BASE_DIR / "mock_showcase" / "pixel11_whatsapp_showcase.html"
OUT_DIR = BASE_DIR / "docs" / "screenshots"


def run_gbrowser(actions: list, width: int, height: int) -> None:
    proc = subprocess.run(
        [
            GBROWSER_BIN,
            "batch",
            "--width",
            str(width),
            "--height",
            str(height),
            "--clean-profile",
            "-",
        ],
        input=json.dumps(actions),
        capture_output=True,
        text=True,
        timeout=45,
    )
    if proc.returncode != 0:
        print("gbrowser stderr:", proc.stderr)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    url = f"file://{HTML_PATH}"

    # 1. Capture panoramic 4-phone showcase hero (2020 x 1180)
    hero_path = OUT_DIR / "05_px11_4screen_showcase_hero.png"
    run_gbrowser(
        [
            {"action": "navigate", "url": url, "waitUntil": "networkidle0"},
            {"action": "sleep", "duration": "800ms"},
            {"action": "screenshot", "file": str(hero_path)},
        ],
        width=2120,
        height=1160,
    )
    print(f"[ok] {hero_path.name}: {hero_path.stat().st_size} bytes")

    # 2. Capture each individual Pixel 11 Pro framed phone (520 x 1060)
    phones = [
        ("capturePhone1", "01_px11_whatsapp_live_stream_framed.png"),
        ("capturePhone2", "02_px11_split_copilot_hud_framed.png"),
        ("capturePhone3", "03_px11_pack_analytics_5pillars_framed.png"),
        ("capturePhone4", "04_px11_cdp_qr_hub_and_crawler_framed.png"),
    ]

    for phone_id, filename in phones:
        out_path = OUT_DIR / filename
        isolate_js = (
            f"(() => {{"
            f"  const hdr = document.querySelector('.showcase-header');"
            f"  if (hdr) hdr.style.display = 'none';"
            f"  document.body.style.padding = '12px';"
            f"  document.body.style.justifyContent = 'center';"
            f"  ['capturePhone1','capturePhone2','capturePhone3','capturePhone4'].forEach(id => {{"
            f"    const el = document.getElementById(id);"
            f"    if (el) el.style.display = (id === '{phone_id}') ? 'inline-flex' : 'none';"
            f"  }});"
            f"  return 'isolated:{phone_id}';"
            f"}})()"
        )
        run_gbrowser(
            [
                {"action": "navigate", "url": url, "waitUntil": "networkidle0"},
                {"action": "sleep", "duration": "500ms"},
                {"action": "eval", "expression": isolate_js, "print": "false"},
                {"action": "sleep", "duration": "250ms"},
                {"action": "screenshot", "file": str(out_path)},
            ],
            width=500,
            height=1050,
        )
        print(f"[ok] {out_path.name}: {out_path.stat().st_size} bytes")


if __name__ == "__main__":
    main()
