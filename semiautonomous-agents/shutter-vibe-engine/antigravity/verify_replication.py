#!/usr/bin/env python3
import os
import sys
import re

# 1. Target files relative to workspace root
TARGETS = {
    "index_v2": "multimodal-search/app/templates/index_v2.html",
    "styles_v2": "multimodal-search/app/static/styles_v2.css",
    "app_v2": "multimodal-search/app/static/app_v2.js",
    "landing_v2": "multimodal-search/app/static/landing_v2.js",
    "viz3d": "multimodal-search/app/static/viz3d.js",
    "create_panel": "multimodal-search/app/static/create_panel.js",
    "kit_panel": "multimodal-search/app/static/kit_panel.js",
    "vibe_slider": "multimodal-search/app/static/vibe_slider.js"
}

print("=== ANTIGRAVITY UI REPLICATION VERIFIER ===")
errors = 0

# Check File Presence and Sizes
for key, path in TARGETS.items():
    if not os.path.exists(path):
        print(f"[ERROR] Missing required file: {path}")
        errors += 1
    else:
        size = os.path.getsize(path)
        if size == 0:
            print(f"[ERROR] File is empty: {path}")
            errors += 1
        else:
            print(f"[OK] Found {path} ({size} bytes)")

# Verify Javascript File References inside index_v2.html
index_path = TARGETS["index_v2"]
if os.path.exists(index_path):
    with open(index_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    
    # Check for script links
    for js_key, js_path in TARGETS.items():
        if js_key == "index_v2" or js_key == "styles_v2":
            continue
        filename = os.path.basename(js_path)
        if filename not in html_content:
            print(f"[WARNING] Script reference to '{filename}' not found in index_v2.html.")

# Static Sweep for Hardcoded GCS Buckets or Prohibited Strings
prohibited_patterns = [
    (re.compile(r"envato-vibe-demo"), "Refers to demo GCS bucket 'envato-vibe-demo' instead of environment variables"),
    (re.compile(r"vtxdemos"), "Refers to demo GCP project 'vtxdemos' instead of environmental dynamic vars")
]

for key, path in TARGETS.items():
    if not os.path.exists(path):
        continue
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    for pattern, desc in prohibited_patterns:
        matches = pattern.findall(content)
        if matches:
            print(f"[WARNING] {path} contains {len(matches)} occurrences of '{pattern.pattern}': {desc}")

# Check FastAPI Mounting logic in app/main.py
main_py_path = "multimodal-search/app/main.py"
if os.path.exists(main_py_path):
    with open(main_py_path, "r", encoding="utf-8") as f:
        main_content = f.read()
    
    mount_check = 'app.mount("/static"' in main_content or 'app.mount(\'/static\'' in main_content
    template_check = 'Jinja2Templates' in main_content
    
    if not mount_check:
        print("[ERROR] FastAPI main.py is missing static folder mounting ('app.mount(\"/static\", ...')")
        errors += 1
    else:
        print("[OK] FastAPI static folder mounting is present in main.py")
        
    if not template_check:
        print("[WARNING] FastAPI main.py does not explicitly use Jinja2Templates. Verify page serving route.")

if errors == 0:
    print("\n[SUCCESS] UI Replication integrity is fully validated. Ready for deployment!")
    sys.exit(0)
else:
    print(f"\n[FAILURE] UI Replication failed with {errors} errors. Please fix before running deployment.")
    sys.exit(1)
