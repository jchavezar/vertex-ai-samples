#!/usr/bin/env python3
"""
clone_libertad.py
Cloning and asset extraction engine for https://www.libertad.com.mx/
Preserves 100% visual, layout, typographic, and structural fidelity.
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
DAM_DIR = ASSETS_DIR / "dam"
JS_DIR = ASSETS_DIR / "js"

BASE_URL = "https://www.libertad.com.mx/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "es-MX,es;q=0.9,en;q=0.8",
}

# SSL context for corporate environments
SSL_CTX = ssl.create_default_context()
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode = ssl.CERT_NONE


def ensure_dirs():
    for d in [TARGET_DIR, ASSETS_DIR, CSS_DIR, FONTS_DIR, DAM_DIR, JS_DIR]:
        d.mkdir(parents=True, exist_ok=True)


def safe_filename(url: str, default_ext: str = "") -> str:
    parsed = urlparse(url)
    clean_path = unquote(parsed.path)
    base = os.path.basename(clean_path)
    if not base:
        h = hashlib.md5(url.encode("utf-8")).hexdigest()[:8]
        return f"asset_{h}{default_ext}"
    # sanitize characters
    clean_name = re.sub(r'[^\w\-_\.]', '_', base)
    if default_ext and not os.path.splitext(clean_name)[1]:
        clean_name += default_ext
    return clean_name


def normalize_url(url: str) -> str:
    parsed = urlparse(url)
    encoded_path = urllib.parse.quote(unquote(parsed.path), safe="/:@!$&'()*+,;=")
    encoded_query = urllib.parse.quote(unquote(parsed.query), safe="/:@!$&'()*+,;=?")
    return parsed._replace(path=encoded_path, query=encoded_query).geturl()


def fetch_bytes(url: str) -> bytes | None:
    try:
        clean_url = normalize_url(url)
        req = urllib.request.Request(clean_url, headers=HEADERS)
        with urllib.request.urlopen(req, context=SSL_CTX, timeout=20) as resp:
            return resp.read()
    except Exception as e:
        print(f"  [WARN] Failed to download {url}: {e}")
        return None


def fetch_text(url: str) -> str | None:
    b = fetch_bytes(url)
    if b is None:
        return None
    try:
        return b.decode("utf-8")
    except UnicodeDecodeError:
        return b.decode("latin-1", errors="ignore")


def process_css_content(css_text: str, css_url: str) -> str:
    """Download fonts & background images referenced inside CSS and rewrite to local relative paths."""
    url_pattern = re.compile(r'url\s*\(\s*[\'"]?([^\'"\)]+)[\'"]?\s*\)', re.IGNORECASE)

    def replacer(match):
        raw_target = match.group(1).strip()
        if raw_target.startswith("data:") or raw_target.startswith("#"):
            return match.group(0)

        full_url = urljoin(css_url, raw_target)
        parsed = urlparse(full_url)
        ext = os.path.splitext(parsed.path)[1].lower()

        # Is it a font?
        if ext in [".ttf", ".woff", ".woff2", ".eot", ".otf"]:
            fname = safe_filename(full_url, ext)
            dest = FONTS_DIR / fname
            if not dest.exists():
                print(f"    [FONT] Downloading: {fname}")
                b = fetch_bytes(full_url)
                if b:
                    dest.write_bytes(b)
            # From CSS directory to fonts directory: ../fonts/fname
            return f'url("../fonts/{fname}")'

        # Is it an image/SVG?
        elif ext in [".png", ".jpg", ".jpeg", ".svg", ".gif", ".webp"]:
            fname = safe_filename(full_url, ext)
            dest = DAM_DIR / fname
            if not dest.exists():
                print(f"    [IMG] Downloading CSS asset: {fname}")
                b = fetch_bytes(full_url)
                if b:
                    dest.write_bytes(b)
            return f'url("../dam/{fname}")'

        return match.group(0)

    return url_pattern.sub(replacer, css_text)


def clone_site():
    print("=" * 60)
    print("🚀 INITIATING CLONE OF LIBERTAD FINANCIERA (100% FIDELITY)")
    print(f"   Target URL: {BASE_URL}")
    print("=" * 60)

    ensure_dirs()

    print("\n[Step 1/5] Fetching main page HTML...")
    html_raw = fetch_text(BASE_URL)
    if not html_raw:
        print("❌ Fatal: Unable to retrieve main page HTML.")
        sys.exit(1)
    print(f"  ✓ Fetched {len(html_raw):,} bytes of HTML.")

    soup = BeautifulSoup(html_raw, "html.parser")

    # [Step 2/5] Process Stylesheets
    print("\n[Step 2/5] Downloading & parsing stylesheets and font families...")
    css_links = soup.find_all("link", rel=lambda x: x and "stylesheet" in x)
    for idx, link in enumerate(css_links):
        href = link.get("href")
        if not href:
            continue
        full_url = urljoin(BASE_URL, href)
        fname = safe_filename(full_url, ".css")
        # Ensure uniqueness
        fname = f"{idx:02d}_{fname}"
        local_css_path = CSS_DIR / fname

        print(f"  [CSS {idx+1}/{len(css_links)}] {fname}")
        css_content = fetch_text(full_url)
        if css_content is not None:
            processed_css = process_css_content(css_content, full_url)
            local_css_path.write_text(processed_css, encoding="utf-8")
            link["href"] = f"./assets/css/{fname}"

    # [Step 3/5] Download all Images and Media Assets
    print("\n[Step 3/5] Downloading all high-res DAM assets, SVGs, and images...")
    imgs = soup.find_all("img")
    for idx, img in enumerate(imgs):
        src = img.get("src")
        if not src or src.startswith("data:"):
            continue
        full_url = urljoin(BASE_URL, src)
        fname = safe_filename(full_url)
        dest = DAM_DIR / fname
        if not dest.exists():
            print(f"  [IMG {idx+1}/{len(imgs)}] {fname}")
            b = fetch_bytes(full_url)
            if b:
                dest.write_bytes(b)
        img["src"] = f"./assets/dam/{fname}"

        # Also check img srcset
        img_srcset = img.get("srcset")
        if img_srcset and not img_srcset.startswith("data:"):
            new_parts = []
            for part in img_srcset.split(","):
                tokens = part.strip().split()
                if not tokens:
                    continue
                u = tokens[0]
                desc = " " + tokens[1] if len(tokens) > 1 else ""
                full_u = urljoin(BASE_URL, u)
                f = safe_filename(full_u)
                d = DAM_DIR / f
                if not d.exists():
                    b = fetch_bytes(full_u)
                    if b:
                        d.write_bytes(b)
                new_parts.append(f"./assets/dam/{f}{desc}")
            img["srcset"] = ", ".join(new_parts)

        # Remove or adjust data-cmp-src if it references Adobe dynamic media with {width} placeholder
        if img.get("data-cmp-src"):
            del img["data-cmp-src"]

    # Process picture sources
    sources = soup.find_all("source")
    for source in sources:
        srcset = source.get("srcset")
        if srcset and not srcset.startswith("data:"):
            new_parts = []
            for part in srcset.split(","):
                tokens = part.strip().split()
                if not tokens:
                    continue
                u = tokens[0]
                desc = " " + tokens[1] if len(tokens) > 1 else ""
                full_u = urljoin(BASE_URL, u)
                f = safe_filename(full_u)
                d = DAM_DIR / f
                if not d.exists():
                    b = fetch_bytes(full_u)
                    if b:
                        d.write_bytes(b)
                new_parts.append(f"./assets/dam/{f}{desc}")
            source["srcset"] = ", ".join(new_parts)

    # Favicon
    icons = soup.find_all("link", rel=lambda x: x and "icon" in x)
    for icon in icons:
        href = icon.get("href")
        if href and not href.startswith("data:"):
            full_url = urljoin(BASE_URL, href)
            fname = safe_filename(full_url)
            dest = DAM_DIR / fname
            if not dest.exists():
                b = fetch_bytes(full_url)
                if b:
                    dest.write_bytes(b)
    # Canonical link
    canon = soup.find("link", rel=lambda x: x and "canonical" in x)
    if canon:
        canon["href"] = "./index.html"

    # [Step 3.5/5] Process Inline Styles & Background Images (Desktop Hero Banners)
    print("\n[Step 3.5/5] Processing inline CSS background images (Hero banners)...")
    for el in soup.find_all(style=True):
        style_str = el["style"]
        if "url(" in style_str:
            # Decode CSS escape sequences like \2f 
            clean_style = style_str.replace(r"\2f ", "/").replace(r"\2f", "/")
            matches = re.findall(r'url\s*\(\s*[\'"]?([^\'"\)]+)[\'"]?\s*\)', clean_style)
            for raw_u in matches:
                if raw_u.startswith("data:") or raw_u.startswith("#"):
                    continue
                full_u = urljoin(BASE_URL, raw_u)
                fname = safe_filename(full_u)
                dest = DAM_DIR / fname
                if not dest.exists():
                    print(f"  [HERO BG] Downloading: {fname}")
                    b = fetch_bytes(full_u)
                    if b:
                        dest.write_bytes(b)
                clean_style = clean_style.replace(raw_u, f"./assets/dam/{fname}")
            el["style"] = clean_style

    # [Step 4/5] Process Scripts & Neutralize Blocking Trackers
    print("\n[Step 4/5] Processing JavaScript and neutralizing telemetry blocks...")
    scripts = soup.find_all("script")
    for s in scripts:
        src = s.get("src")
        if not src:
            continue
        # Check if it is an external tracker (GTM, Adobe Launch, Google Ads)
        if any(tracker in src.lower() for tracker in ["adobedtm.com", "google-analytics", "googletagmanager", "google-ads"]):
            # Deactivate tracking script to prevent CORS/offline blocks
            s.decompose()
            continue

        full_url = urljoin(BASE_URL, src)
        fname = safe_filename(full_url, ".js")
        dest = JS_DIR / fname
        if not dest.exists():
            b = fetch_bytes(full_url)
            if b is not None:
                dest.write_bytes(b)
        s["src"] = f"./assets/js/{fname}"

    # [Step 5/5] Insetting Feature Slots for Jetski Live Demo
    print("\n[Step 5/5] Inserting semantic Feature Slots for Jetski live additions...")
    from bs4 import Comment

    # Body end slots (completely safe from affecting grid layouts)
    if soup.body:
        soup.body.append(Comment(" FEATURE_SLOT: FLOATING_ASSISTANT "))
        soup.body.append(Comment(" FEATURE_SLOT: HERO_OVERLAY "))
        soup.body.append(Comment(" FEATURE_SLOT: FOOTER_INJECTIONS "))

    # Save finalized index.html
    out_file = TARGET_DIR / "index.html"
    out_file.write_text(str(soup), encoding="utf-8")
    print(f"\n✅ SUCCESS! Cloned site saved to: {out_file}")
    print(f"   Total Size: {out_file.stat().st_size:,} bytes")
    print(f"   Assets Directory: {ASSETS_DIR}")


if __name__ == "__main__":
    clone_site()
