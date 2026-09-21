#!/usr/bin/env python3
"""
clone_weil.py
High-fidelity cloning and asset extraction engine for https://www.weil.com/
Preserves 100% visual, typographic, and corporate branding fidelity.
"""

import os
import re
import sys
import ssl
import hashlib
import urllib.request
from urllib.parse import urljoin, urlparse, unquote
from pathlib import Path
from bs4 import BeautifulSoup

TARGET_DIR = Path(__file__).parent / "site"
ASSETS_DIR = TARGET_DIR / "assets"
CSS_DIR = ASSETS_DIR / "css"
FONTS_DIR = ASSETS_DIR / "fonts"
IMAGES_DIR = ASSETS_DIR / "images"
JS_DIR = ASSETS_DIR / "js"

BASE_URL = "https://www.weil.com/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

SSL_CTX = ssl.create_default_context()
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode = ssl.CERT_NONE


def ensure_dirs():
    for d in [TARGET_DIR, ASSETS_DIR, CSS_DIR, FONTS_DIR, IMAGES_DIR, JS_DIR]:
        d.mkdir(parents=True, exist_ok=True)


def safe_filename(url: str, default_ext: str = "") -> str:
    parsed = urlparse(url)
    clean_path = unquote(parsed.path)
    base = os.path.basename(clean_path)
    if not base or len(base) > 60:
        h = hashlib.md5(url.encode("utf-8")).hexdigest()[:10]
        return f"asset_{h}{default_ext}"
    clean_name = re.sub(r"[^\w\-_\.]", "_", base)
    if default_ext and not os.path.splitext(clean_name)[1]:
        clean_name += default_ext
    return clean_name


def fetch_bytes(url: str) -> bytes | None:
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, context=SSL_CTX, timeout=20) as resp:
            return resp.read()
    except Exception as e:
        print(f"  ⚠️ Warning: Failed fetching {url}: {e}")
        return None


def clone_site():
    print("==================================================================")
    print("⚖️  CLONING ENGINE: WEIL, GOTSHAL & MANGES LLP (weil.com)")
    print("==================================================================")
    ensure_dirs()

    print("📥 [1/4] Fetching official landing page from https://www.weil.com/...")
    html_data = fetch_bytes(BASE_URL)
    if not html_data:
        print("❌ Critical: Could not download landing page.")
        sys.exit(1)

    soup = BeautifulSoup(html_data.decode("utf-8", errors="ignore"), "html.parser")

    # Remove tracking / cookie consent overlays that block local inspection
    for elem in soup.find_all("script"):
        src = elem.get("src", "")
        if "cookielaw.org" in src or "googletagmanager" in src or "OtAutoBlock" in src:
            elem.decompose()
    for noscript in soup.find_all("noscript"):
        if "googletagmanager" in noscript.get_text():
            noscript.decompose()

    print("🎨 [2/4] Harvesting CSS & Stylesheets...")
    for link in soup.find_all("link", rel="stylesheet"):
        href = link.get("href")
        if not href:
            continue
        css_url = urljoin(BASE_URL, href)
        fname = safe_filename(css_url, default_ext=".css")
        local_path = CSS_DIR / fname
        css_data = fetch_bytes(css_url)
        if css_data:
            css_text = css_data.decode("utf-8", errors="ignore")
            # Harvest embedded webfonts or images in CSS
            font_urls = re.findall(r"url\([\'\"]?([^\'\"\)]+)[\'\"]?\)", css_text)
            for f_match in set(font_urls):
                if f_match.startswith("data:") or f_match.startswith("#"):
                    continue
                full_furl = urljoin(css_url, f_match)
                font_fname = safe_filename(full_furl)
                font_data = fetch_bytes(full_furl)
                if font_data:
                    (FONTS_DIR / font_fname).write_bytes(font_data)
                    css_text = css_text.replace(f_match, f"/assets/fonts/{font_fname}")
            local_path.write_text(css_text, encoding="utf-8")
            link["href"] = f"/assets/css/{fname}"
            print(f"  • Downloaded CSS: {fname} ({len(css_text)} chars)")

    print("🖼️  [3/4] Harvesting corporate branding & high-res images...")
    for img in soup.find_all("img"):
        src = img.get("src")
        if not src or src.startswith("data:"):
            continue
        img_url = urljoin(BASE_URL, src)
        ext = os.path.splitext(urlparse(img_url).path)[1] or ".png"
        img_fname = safe_filename(img_url, default_ext=ext)
        img_data = fetch_bytes(img_url)
        if img_data:
            (IMAGES_DIR / img_fname).write_bytes(img_data)
            img["src"] = f"/assets/images/{img_fname}"

    print("📜 [4/4] Harvesting essential JavaScript libraries...")
    for script in soup.find_all("script"):
        src = script.get("src")
        if not src or (src.startswith("http") and "weil.com" not in src):
            continue
        js_url = urljoin(BASE_URL, src)
        js_fname = safe_filename(js_url, default_ext=".js")
        js_data = fetch_bytes(js_url)
        if js_data:
            (JS_DIR / js_fname).write_bytes(js_data)
            script["src"] = f"/assets/js/{js_fname}"

    # Setup Feature Slots for clean modular injection
    html_content = str(soup)

    # Insert HEADER_SLOT around header
    header_tag = soup.find("header")
    if header_tag:
        header_str = str(header_tag)
        replacement = f"<!-- FEATURE_SLOT: HEADER_SLOT -->\n{header_str}\n<!-- FEATURE_SLOT_END: HEADER_SLOT -->"
        html_content = html_content.replace(header_str, replacement, 1)

    # Insert FLOATING_ASSISTANT & MULTIMODAL_MODAL slots before </body>
    slots_footer = """
<!-- FEATURE_SLOT: FLOATING_ASSISTANT -->
<!-- FEATURE_SLOT_END: FLOATING_ASSISTANT -->

<!-- FEATURE_SLOT: MULTIMODAL_MODAL -->
<!-- FEATURE_SLOT_END: MULTIMODAL_MODAL -->
"""
    if "</body>" in html_content:
        html_content = html_content.replace("</body>", f"{slots_footer}\n</body>")

    # Write pristine and index
    (TARGET_DIR / "index.pristine.html").write_text(html_content, encoding="utf-8")
    (TARGET_DIR / "index.html").write_text(html_content, encoding="utf-8")

    print("\n✅ Clone operation completed successfully!")
    print(f"📁 Cloned Portal Directory: {TARGET_DIR}")
    print(f"📄 Pristine Baseline: {TARGET_DIR / 'index.pristine.html'}")


if __name__ == "__main__":
    clone_site()
