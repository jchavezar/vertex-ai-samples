#!/usr/bin/env python3
"""
Renders 3x HiDPI Retina Pixel 11 Pro hardware-framed screenshots from
`mock_showcase/pixel11_whatsapp_showcase.html` using Playwright + Google Chrome.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_DIR = Path(__file__).resolve().parent.parent
HTML_PATH = BASE_DIR / "mock_showcase" / "pixel11_whatsapp_showcase.html"
OUT_DIR = BASE_DIR / "docs" / "screenshots"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    url = f"file://{HTML_PATH}"

    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path="/usr/bin/google-chrome",
            headless=True,
            args=["--no-sandbox", "--disable-gpu", "--font-render-hinting=none"],
        )
        page = browser.new_page(
            viewport={"width": 2120, "height": 1160},
            device_scale_factor=3,
        )
        page.goto(url, wait_until="networkidle")
        page.evaluate("document.fonts.ready")
        page.wait_for_timeout(400)

        # 1. Capture panoramic 4-phone showcase hero at 3x Retina (6360 x 3480)
        hero_path = OUT_DIR / "05_px11_4screen_showcase_hero.png"
        page.screenshot(path=str(hero_path), full_page=True)
        print(f"[ok] {hero_path.name}: {hero_path.stat().st_size} bytes")

        # 2. Capture each individual Pixel 11 Pro framed phone at 3x Retina (~1428 x 3080)
        phones = [
            ("#capturePhone1", "01_px11_whatsapp_live_stream_framed.png"),
            ("#capturePhone2", "02_px11_split_copilot_hud_framed.png"),
            ("#capturePhone3", "03_px11_pack_analytics_5pillars_framed.png"),
            ("#capturePhone4", "04_px11_cdp_qr_hub_and_crawler_framed.png"),
        ]
        for selector, filename in phones:
            out_path = OUT_DIR / filename
            loc = page.locator(selector)
            loc.screenshot(path=str(out_path))
            print(f"[ok] {out_path.name}: {out_path.stat().st_size} bytes")

        browser.close()


if __name__ == "__main__":
    main()
