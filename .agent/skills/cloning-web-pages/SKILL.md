---
name: cloning-web-pages
description: Automatically mirrors and recreates web pages with 100% pixel-perfect visual, typographic, and behavioral fidelity. Extracts and localizes HTML, CSS stylesheets, deep font-face binaries (TTF/WOFF/WOFF2), DAM/SVG assets, responsive srcset variants, and inline CSS background images (handling CSS Unicode escapes like \2f). Automatically sets up an isolated local HTTP server with correct typography MIME types, opens the page, and executes visual evaluation and screenshot capture using the browser MCP tools. Use whenever the user requests "clon pagina", "clonar web", "clonar sitio", "clone website", "mirror page", or asks to replicate a website's UI faithfully.
---

# Web Page Cloning & Visual Fidelity Engine

This skill defines the standardized, zero-defect process for cloning any public web page with **100% identical UI/UX**, exact fonts, colors, responsive layouts, media assets, and interactive controls, followed by automated visual evaluation using the browser MCP tool.

## When to use this skill
- When the user asks to clone a webpage: `"clon pagina"`, `"clona la pagina"`, `"copia fiel de la web"`, `"mirror website"`.
- When replicating an existing enterprise portal or CMS page (Adobe Experience Manager, WordPress, Drupal, Next.js, Webflow).
- When preparing an existing live application for modernization demos, feature injections, or local development.

---

## The 5-Pillar Fidelity Checklist

Before claiming that any cloned web page is complete, the agent MUST verify all 5 pillars:

- [ ] **1. Non-ASCII URL Encoding**: Paths containing accents, spaces, or characters like `ñ` (e.g. `rediseño-sitio-web`) must be percent-encoded (`%C3%B1`) during download.
- [ ] **2. Deep Typography Harvesting**: Scan every stylesheet for `@font-face` blocks. Download all binary `.ttf`, `.woff`, `.woff2` files locally and rewrite CSS rules.
- [ ] **3. Inline Style & CMS Escaped Assets**: Enterprise CMSs (like AEM) inject desktop hero banners via inline `style="background-image:url(\2f ...)"`. The agent must decode `\2f ` escapes and download all inline background images.
- [ ] **4. Responsive `srcset` Parsing**: Multi-resolution `srcset` attributes contain comma-separated entries (`url1 320w, url2 800w`). Parse each variant individually.
- [ ] **5. Visual Evaluation via Browser MCP**: Launch the browser, navigate to the local server, test interactive controls (such as carousel slides), take screenshots via `browser_screenshot`, and inspect the image with `view_file` to confirm pixel-perfect parity.

---

## Step-by-Step Workflow

### Step 1: Pre-flight Analysis & Tooling Setup
- Always use `uv` for Python tooling: `uv run --with beautifulsoup4 python3 ...`.
- Check and proactively allocate a free port (e.g. `8088`, `3000`), never hardcoding conflicting ports like `8000` or `5173`.
- Configure an SSL context that bypasses corporate proxy certificate verification (`ssl.CERT_NONE`).

### Step 2: Extraction & Local Mirroring Engine
Create a dedicated standalone cloner (e.g. `clone_site.py`):
1. **Fetch Raw HTML**: Download the full document from the target URL with browser user-agent headers.
2. **Download Stylesheets & Sub-Resources**:
   - Save all `<link rel="stylesheet">` into `site/assets/css/`.
   - In each CSS, search with regex `url\s*\(\s*['"]?([^'")]+)['"]?\s*\)`.
   - Download fonts to `site/assets/fonts/` and rewrite to `url("../fonts/<filename>")`.
   - Download CSS background images to `site/assets/dam/` and rewrite to `url("../dam/<filename>")`.
3. **Download HTML Images & Responsive Media**:
   - Extract `<img src="...">`, `<picture>`, and parse multi-variant `<source srcset="...">`.
   - Save to `site/assets/dam/` and update attributes to `./assets/dam/<filename>`.
4. **Scan Inline Element Styles**:
   - Crucial step often missed: inspect all elements with a `style` attribute.
   - Replace CSS Unicode escapes: `style.replace(r"\2f ", "/").replace(r"\2f", "/")`.
   - Extract all `url(...)` targets, download hero banner images, and rewrite inline styles to relative paths.
5. **Neutralize External Trackers**:
   - Remove or stub scripts that call external analytics (e.g. Adobe Launch `adobedtm.com`, Google Tag Manager, Google Ads, Imperva captchas).
   - This prevents offline timeouts, CORS errors, and console clutter while keeping interactive UI mechanics functioning.
6. **Feature Slots (Zero Screen Leaks)**:
   - If inserting extension markers for future feature injections, NEVER use unescaped text nodes or string insertions that render into the DOM.
   - Always append pure HTML comments (e.g. `<!-- FEATURE_SLOT: NAME -->`) or place them safely at the bottom of `<body>` so they never alter CSS grid flow.

### Step 3: High-Fidelity Local HTTP Server (`serve_site.py`)
Deploy an HTTP server configured specifically for local asset delivery:
```python
from http.server import HTTPServer, SimpleHTTPRequestHandler

class LocalMirrorHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-cache, must-revalidate")
        super().end_headers()

    def guess_type(self, path):
        p = str(path).lower()
        if p.endswith(".ttf"): return "font/ttf"
        if p.endswith(".woff"): return "font/woff"
        if p.endswith(".woff2"): return "font/woff2"
        if p.endswith(".svg"): return "image/svg+xml"
        if p.endswith(".css"): return "text/css; charset=utf-8"
        if p.endswith(".js"): return "application/javascript; charset=utf-8"
        return super().guess_type(path)
```
- Include fallback URL rewriting so any lingering CMS dynamic delivery paths (e.g. `/adobe/dynamicmedia/deliver/...`) are routed automatically to local assets.

### Step 4: Automated Visual Evaluation (Browser MCP)
The task is NOT complete until the visual output has been inspected and confirmed with the browser MCP tools:

1. **Launch Browser with Remote Debugging**:
   ```bash
   open -na "Google Chrome" --args --remote-debugging-port=9222 --user-data-dir="/tmp/chrome_dev_eval" "http://localhost:<PORT>/"
   ```
2. **Connect & Select Tab**:
   - Call `browser_list_tabs` via `call_mcp_tool` (Server: `antigravity-browser`).
   - Call `browser_select_tab` with `url_pattern: "localhost:<PORT>"`.
3. **Navigate & Stabilize**:
   - Call `browser_go_to` with `http://localhost:<PORT>/`.
4. **Interactive Control Verification**:
   - If the page has carousels, tabs, or menus, simulate clicks with `browser_js_click` to verify all slides/tabs render correctly.
5. **Capture & Inspect Screenshot**:
   - Call `browser_screenshot` with `filename: "clone_verification.png"`.
   - Call `view_file` on the saved image path to verify that:
     - Typography and fonts match the original.
     - Hero people/product photography is visible and not blank.
     - No unrendered comment text appears on screen.
     - Layout, spacing, and header navigation are 100% faithful.
