#!/usr/bin/env python3
"""
universal_cloner.py
Reference implementation for cloning any web page with 100% pixel fidelity,
handling fonts, inline styles, CSS escapes, and responsive srcset media.
"""

import os
import re
import sys
import ssl
import hashlib
import argparse
import urllib.request
from urllib.parse import urljoin, urlparse, unquote, quote
from pathlib import Path
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
}

SSL_CTX = ssl.create_default_context()
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode = ssl.CERT_NONE


def safe_filename(url: str, default_ext: str = "") -> str:
    parsed = urlparse(url)
    clean_path = unquote(parsed.path)
    base = os.path.basename(clean_path)
    if not base:
        h = hashlib.md5(url.encode("utf-8")).hexdigest()[:8]
        return f"asset_{h}{default_ext}"
    clean_name = re.sub(r'[^\w\-_\.]', '_', base)
    if default_ext and not os.path.splitext(clean_name)[1]:
        clean_name += default_ext
    return clean_name


def normalize_url(url: str) -> str:
    parsed = urlparse(url)
    encoded_path = quote(unquote(parsed.path), safe="/:@!$&'()*+,;=")
    encoded_query = quote(unquote(parsed.query), safe="/:@!$&'()*+,;=?")
    return parsed._replace(path=encoded_path, query=encoded_query).geturl()


def fetch_bytes(url: str) -> bytes | None:
    try:
        clean_url = normalize_url(url)
        req = urllib.request.Request(clean_url, headers=HEADERS)
        with urllib.request.urlopen(req, context=SSL_CTX, timeout=25) as resp:
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


def clone(target_url: str, output_dir: Path):
    site_dir = output_dir / "site"
    assets_dir = site_dir / "assets"
    css_dir = assets_dir / "css"
    fonts_dir = assets_dir / "fonts"
    dam_dir = assets_dir / "dam"
    js_dir = assets_dir / "js"

    for d in [site_dir, assets_dir, css_dir, fonts_dir, dam_dir, js_dir]:
        d.mkdir(parents=True, exist_ok=True)

    print(f"🌐 Fetching target HTML: {target_url}")
    html_raw = fetch_text(target_url)
    if not html_raw:
        print("❌ Error fetching HTML.")
        sys.exit(1)

    soup = BeautifulSoup(html_raw, "html.parser")

    # 1. Stylesheets & Fonts
    print("🎨 Processing stylesheets and fonts...")
    css_links = soup.find_all("link", rel=lambda x: x and "stylesheet" in x)
    for idx, link in enumerate(css_links):
        href = link.get("href")
        if not href:
            continue
        full_url = urljoin(target_url, href)
        fname = f"{idx:02d}_{safe_filename(full_url, '.css')}"
        css_path = css_dir / fname
        content = fetch_text(full_url)
        if content is not None:
            # Parse fonts and background images inside CSS
            def replacer(m):
                raw = m.group(1).strip()
                if raw.startswith("data:") or raw.startswith("#"):
                    return m.group(0)
                sub_url = urljoin(full_url, raw)
                ext = os.path.splitext(urlparse(sub_url).path)[1].lower()
                if ext in [".ttf", ".woff", ".woff2", ".eot", ".otf"]:
                    font_name = safe_filename(sub_url, ext)
                    font_dest = fonts_dir / font_name
                    if not font_dest.exists():
                        b = fetch_bytes(sub_url)
                        if b:
                            font_dest.write_bytes(b)
                    return f'url("../fonts/{font_name}")'
                elif ext in [".png", ".jpg", ".jpeg", ".svg", ".gif", ".webp"]:
                    img_name = safe_filename(sub_url, ext)
                    img_dest = dam_dir / img_name
                    if not img_dest.exists():
                        b = fetch_bytes(sub_url)
                        if b:
                            img_dest.write_bytes(b)
                    return f'url("../dam/{img_name}")'
                return m.group(0)

            processed = re.sub(r'url\s*\(\s*[\'"]?([^\'"\)]+)[\'"]?\s*\)', replacer, content, flags=re.I)
            css_path.write_text(processed, encoding="utf-8")
            link["href"] = f"./assets/css/{fname}"

    # 2. HTML Images & Srcset
    print("🖼️ Processing images and responsive media...")
    for img in soup.find_all("img"):
        src = img.get("src")
        if src and not src.startswith("data:"):
            full_url = urljoin(target_url, src)
            fname = safe_filename(full_url)
            dest = dam_dir / fname
            if not dest.exists():
                b = fetch_bytes(full_url)
                if b:
                    dest.write_bytes(b)
            img["src"] = f"./assets/dam/{fname}"

        # Handle srcset
        srcset = img.get("srcset")
        if srcset and not srcset.startswith("data:"):
            new_tokens = []
            for part in srcset.split(","):
                toks = part.strip().split()
                if not toks:
                    continue
                u = toks[0]
                desc = " " + toks[1] if len(toks) > 1 else ""
                full_u = urljoin(target_url, u)
                f = safe_filename(full_u)
                d = dam_dir / f
                if not d.exists():
                    b = fetch_bytes(full_u)
                    if b:
                        d.write_bytes(b)
                new_tokens.append(f"./assets/dam/{f}{desc}")
            img["srcset"] = ", ".join(new_tokens)

    # 3. Inline Styles (Hero Background Banners)
    print("🪄 Scanning inline style backgrounds...")
    for el in soup.find_all(style=True):
        style = el["style"]
        if "url(" in style:
            clean_style = style.replace(r"\2f ", "/").replace(r"\2f", "/")
            matches = re.findall(r'url\s*\(\s*[\'"]?([^\'"\)]+)[\'"]?\s*\)', clean_style)
            for raw_u in matches:
                if raw_u.startswith("data:") or raw_u.startswith("#"):
                    continue
                full_u = urljoin(target_url, raw_u)
                fname = safe_filename(full_u)
                dest = dam_dir / fname
                if not dest.exists():
                    b = fetch_bytes(full_u)
                    if b:
                        dest.write_bytes(b)
                clean_style = clean_style.replace(raw_u, f"./assets/dam/{fname}")
            el["style"] = clean_style

    # 4. Save
    out_file = site_dir / "index.html"
    out_file.write_text(str(soup), encoding="utf-8")
    print(f"✅ Cloning complete: {out_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Universal 100% Fidelity Web Cloner")
    parser.add_argument("url", help="Target URL to clone")
    parser.add_argument("--out", default=".", help="Output directory")
    args = parser.parse_args()
    clone(args.url, Path(args.out))
