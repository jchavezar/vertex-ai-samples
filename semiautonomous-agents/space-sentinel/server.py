#!/usr/bin/env python3
import os
import sys
import json
import shutil
import gzip
import subprocess
import time
import threading
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

HOME_DIR = os.path.expanduser("~")
QUARANTINE_DIR = os.path.join(HOME_DIR, ".space_sentinel_quarantine")
MANIFEST_FILE = os.path.join(QUARANTINE_DIR, "manifest.json")

os.makedirs(QUARANTINE_DIR, exist_ok=True)
if not os.path.exists(MANIFEST_FILE):
    with open(MANIFEST_FILE, "w") as f:
        json.dump([], f)

# Global memory caches for ultra-fast response (<10ms)
CACHE_LOCK = threading.Lock()
PRESET_CACHE = []
FILES_CACHE = []
LAST_SCAN_TIME = 0

def get_disk_usage():
    try:
        total, used, free = shutil.disk_usage(HOME_DIR)
        return {
            "total_bytes": total,
            "used_bytes": used,
            "free_bytes": free,
            "free_percent": round((free / total) * 100, 1),
            "used_percent": round((used / total) * 100, 1)
        }
    except Exception as e:
        return {"error": str(e)}

def load_quarantine_manifest():
    try:
        with open(MANIFEST_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return []

def save_quarantine_manifest(items):
    with open(MANIFEST_FILE, "w") as f:
        json.dump(items, f, indent=2)

def is_safe_path(target_path):
    try:
        resolved = os.path.realpath(target_path)
        forbidden = ["/", "/System", "/usr", "/bin", "/sbin", "/Library", HOME_DIR]
        if resolved in forbidden:
            return False
        return resolved.startswith(HOME_DIR + os.sep) or resolved.startswith(QUARANTINE_DIR)
    except Exception:
        return False

def get_preset_definitions():
    return [
        {
            "id": "uv_cache",
            "name": "Python UV Package Cache",
            "category": "Dev Cache",
            "path": os.path.join(HOME_DIR, ".cache", "uv"),
            "safe_to_wipe": True,
            "description": "Wheel caches and download archives used by uv package manager."
        },
        {
            "id": "npm_cache",
            "name": "NPM Global Cache",
            "category": "Dev Cache",
            "path": os.path.join(HOME_DIR, ".npm"),
            "safe_to_wipe": True,
            "description": "Cached Node packages and distribution archives."
        },
        {
            "id": "jetbrains_cache",
            "name": "JetBrains / IntelliJ Caches & Patches",
            "category": "IDE Cache",
            "path": os.path.join(HOME_DIR, "Library", "Caches", "JetBrains"),
            "safe_to_wipe": True,
            "description": "Old indexes, compilation caches, and patch updater jars."
        },
        {
            "id": "llama_cpp_cache",
            "name": "llama.cpp Downloaded GGUF Models",
            "category": "AI Bloat",
            "path": os.path.join(HOME_DIR, "Library", "Caches", "llama.cpp"),
            "safe_to_wipe": False,
            "description": "Quantized GGUF LLM models (e.g. Gemma 3 12B)."
        },
        {
            "id": "ollama_blobs",
            "name": "Ollama Heavy Model Blobs",
            "category": "AI Bloat",
            "path": os.path.join(HOME_DIR, ".ollama", "models"),
            "safe_to_wipe": False,
            "description": "Large parameter checkpoints used by local Ollama runner."
        },
        {
            "id": "gemma_checkpoint",
            "name": "Gemma 7B Local Checkpoint",
            "category": "AI Bloat",
            "path": os.path.join(HOME_DIR, "gemma_7b-it"),
            "safe_to_wipe": False,
            "description": "Uncompressed legacy Gemma weights directory."
        },
        {
            "id": "downloads_zips",
            "name": "Downloads Print ZIP Archives",
            "category": "Archives",
            "path": os.path.join(HOME_DIR, "Downloads"),
            "safe_to_wipe": False,
            "description": "Large zip print packages in ~/Downloads."
        }
    ]

def get_dir_size_fast(target_path):
    if not os.path.exists(target_path):
        return 0, False
    try:
        if os.path.isfile(target_path):
            return os.path.getsize(target_path), True
        # Fast estimation with ls/du cap timeout
        out = subprocess.check_output(["du", "-sk", target_path], stderr=subprocess.DEVNULL, timeout=2.5).decode("utf-8")
        kb = int(out.split()[0])
        return kb * 1024, True
    except Exception:
        return 0, True

def run_background_scanner():
    global PRESET_CACHE, FILES_CACHE, LAST_SCAN_TIME
    while True:
        try:
            # 1. Update presets size
            new_presets = []
            for p in get_preset_definitions():
                size_bytes, exists = get_dir_size_fast(p["path"])
                new_presets.append({
                    **p,
                    "exists": exists,
                    "size_bytes": size_bytes
                })

            # 2. Update largest files (fast direct search)
            known_heavy_paths = [
                os.path.join(HOME_DIR, ".ollama/models/blobs/sha256-ccc0cddac56136ef0969cf2e3e9ac051124c937be42503b47ec570dead85ff87"),
                os.path.join(HOME_DIR, "Library/Caches/llama.cpp/google_gemma-3-12b-it-qat-q4_0-gguf_gemma-3-12b-it-q4_0.gguf"),
                os.path.join(HOME_DIR, "Library/Parallels/Downloads/26100.2033.241004-2336.ge_release_svc_refresh_CLIENTCONSUMER_RET_A64FRE_en-us.iso"),
                os.path.join(HOME_DIR, ".gemini/antigravity-browser-profile/OptGuideOnDeviceModel/2025.8.8.1141/weights.bin"),
                os.path.join(HOME_DIR, "Downloads/PRINT-20250717T185736Z-1-001.zip"),
                os.path.join(HOME_DIR, "Downloads/Tulum_CC2025_FullHighlight.mp4"),
                os.path.join(HOME_DIR, "Downloads/PRINT-20250703T182202Z-1-002.zip"),
                os.path.join(HOME_DIR, "Downloads/PRINT-20250703T182202Z-1-001.zip"),
                os.path.join(HOME_DIR, "Downloads/PRINT-20250717T185736Z-1-004.zip"),
                os.path.join(HOME_DIR, "Downloads/PRINT-20250717T185736Z-1-003.zip"),
                os.path.join(HOME_DIR, "gemma_7b-it/checkpoint_00000000/state/mdl_vars.params.lm.softmax.w/0.0"),
                os.path.join(HOME_DIR, "Downloads/PRINT-20250717T185736Z-1-002.zip"),
                os.path.join(HOME_DIR, "Downloads/PRINT-20250703T182202Z-1-003.zip"),
                os.path.join(HOME_DIR, "Downloads/PRINT-20250703T182202Z-1-004.zip"),
                os.path.join(HOME_DIR, "Downloads/PRINT-20250703T182202Z-1-005.zip"),
                os.path.join(HOME_DIR, "Documents/recordings/time_magazine_2.mov"),
            ]

            # Fast find for any extra files > 100MB in Downloads, Desktop, Documents, IdeaProjects
            cmd = ["find", os.path.join(HOME_DIR, "Downloads"), os.path.join(HOME_DIR, "Documents"), "-type", "f", "-size", "+50M"]
            try:
                out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL, timeout=4.0).decode("utf-8")
                for line in out.splitlines():
                    p = line.strip()
                    if p not in known_heavy_paths:
                        known_heavy_paths.append(p)
            except Exception:
                pass

            new_files = []
            for filepath in known_heavy_paths:
                if QUARANTINE_DIR in filepath or not os.path.exists(filepath):
                    continue
                try:
                    st = os.stat(filepath)
                    size = st.st_size
                    ext = Path(filepath).suffix.lower()

                    cat = "Other Heavy"
                    if ext in [".bin", ".gguf", ".safetensors", ".pt", ".onnx", ".ckpt"] or "gemma" in filepath or "ollama" in filepath:
                        cat = "AI & ML Weights"
                    elif ext in [".zip", ".tar", ".gz", ".tgz", ".7z", ".iso", ".dmg", ".pkg"]:
                        cat = "Archives & Disk Images"
                    elif ext in [".mp4", ".mov", ".mkv", ".avi", ".wav", ".flac"]:
                        cat = "Media & Video"
                    elif ext in [".log", ".dat", ".storage", ".values", ".index"]:
                        cat = "System & Index Logs"
                    elif "/.cache/" in filepath or "/Library/Caches/" in filepath:
                        cat = "Cache File"

                    new_files.append({
                        "path": filepath,
                        "name": os.path.basename(filepath),
                        "size_bytes": size,
                        "modified_timestamp": int(st.st_mtime),
                        "modified_human": time.strftime("%Y-%m-%d %H:%M", time.localtime(st.st_mtime)),
                        "extension": ext or "none",
                        "category": cat
                    })
                except Exception:
                    pass

            new_files.sort(key=lambda x: x["size_bytes"], reverse=True)

            with CACHE_LOCK:
                PRESET_CACHE = new_presets
                FILES_CACHE = new_files
                LAST_SCAN_TIME = int(time.time())

        except Exception as err:
            print("Background scan exception:", err)
        time.sleep(12)  # Update every 12 seconds in background

class SpaceSentinelHandler(BaseHTTPRequestHandler):
    def _send_json(self, data, status=200):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def _send_file(self, filepath, content_type):
        try:
            with open(filepath, "rb") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(content)))
            self.send_header("X-Content-Type-Options", "nosniff")
            self.end_headers()
            self.wfile.write(content)
        except Exception:
            self.send_error(404, "File Not Found")

    def do_GET(self):
        parsed = urlparse(self.path)
        route = parsed.path
        
        if route == "/" or route == "/index.html":
            static_html = os.path.join(os.path.dirname(__file__), "static", "index.html")
            return self._send_file(static_html, "text/html; charset=utf-8")
        elif route == "/styles.css":
            return self._send_file(os.path.join(os.path.dirname(__file__), "static", "styles.css"), "text/css")
        elif route == "/app.js":
            return self._send_file(os.path.join(os.path.dirname(__file__), "static", "app.js"), "application/javascript")
            
        elif route == "/api/telemetry":
            disk = get_disk_usage()
            with CACHE_LOCK:
                presets = list(PRESET_CACHE)
            quarantine = load_quarantine_manifest()
            quarantine_bytes = sum(q.get("size_bytes", 0) for q in quarantine)
            self._send_json({
                "disk": disk,
                "presets": presets,
                "quarantine_count": len(quarantine),
                "quarantine_bytes": quarantine_bytes,
                "last_scan_time": LAST_SCAN_TIME
            })
            
        elif route == "/api/files":
            qs = parse_qs(parsed.query)
            min_mb = int(qs.get("min_mb", [50])[0])
            min_bytes = min_mb * 1024 * 1024
            with CACHE_LOCK:
                filtered = [f for f in FILES_CACHE if f["size_bytes"] >= min_bytes]
            self._send_json({"files": filtered})
            
        elif route == "/api/quarantine/list":
            manifest = load_quarantine_manifest()
            self._send_json({"quarantine": manifest})
            
        else:
            self.send_error(404, "Route not found")

    def do_POST(self):
        parsed = urlparse(self.path)
        route = parsed.path
        length = int(self.headers.get("Content-Length", 0))
        raw_body = self.rfile.read(length).decode("utf-8") if length > 0 else "{}"
        try:
            payload = json.loads(raw_body)
        except Exception:
            payload = {}

        if route == "/api/quarantine/add":
            target = payload.get("path")
            if not target or not os.path.exists(target):
                return self._send_json({"error": "Path does not exist"}, 400)
            if not is_safe_path(target):
                return self._send_json({"error": "Path protected or unsafe"}, 403)
                
            size = os.path.getsize(target) if os.path.isfile(target) else 0
            file_id = f"q_{int(time.time() * 1000)}"
            dest = os.path.join(QUARANTINE_DIR, file_id + "_" + os.path.basename(target))
            
            try:
                shutil.move(target, dest)
                manifest = load_quarantine_manifest()
                entry = {
                    "id": file_id,
                    "original_path": target,
                    "quarantine_path": dest,
                    "name": os.path.basename(target),
                    "size_bytes": size,
                    "staged_at": time.strftime("%Y-%m-%d %H:%M:%S")
                }
                manifest.append(entry)
                save_quarantine_manifest(manifest)
                
                # Remove from file memory cache immediately
                with CACHE_LOCK:
                    FILES_CACHE[:] = [f for f in FILES_CACHE if f["path"] != target]
                    
                return self._send_json({"success": True, "entry": entry})
            except Exception as e:
                return self._send_json({"error": str(e)}, 500)

        elif route == "/api/quarantine/restore":
            entry_id = payload.get("id")
            manifest = load_quarantine_manifest()
            found = None
            for idx, item in enumerate(manifest):
                if item["id"] == entry_id:
                    found = (idx, item)
                    break
            if not found:
                return self._send_json({"error": "Quarantine ID not found"}, 404)
                
            idx, item = found
            q_path = item["quarantine_path"]
            orig_path = item["original_path"]
            
            if not os.path.exists(q_path):
                manifest.pop(idx)
                save_quarantine_manifest(manifest)
                return self._send_json({"error": "Quarantined file missing on disk"}, 404)
                
            try:
                os.makedirs(os.path.dirname(orig_path), exist_ok=True)
                shutil.move(q_path, orig_path)
                manifest.pop(idx)
                save_quarantine_manifest(manifest)
                return self._send_json({"success": True, "restored_path": orig_path})
            except Exception as e:
                return self._send_json({"error": str(e)}, 500)

        elif route == "/api/quarantine/empty":
            manifest = load_quarantine_manifest()
            deleted_count = 0
            freed_bytes = 0
            for item in manifest:
                q_path = item.get("quarantine_path")
                if q_path and os.path.exists(q_path):
                    try:
                        if os.path.isdir(q_path):
                            shutil.rmtree(q_path)
                        else:
                            os.remove(q_path)
                        deleted_count += 1
                        freed_bytes += item.get("size_bytes", 0)
                    except Exception:
                        pass
            save_quarantine_manifest([])
            return self._send_json({"success": True, "deleted_count": deleted_count, "freed_bytes": freed_bytes})

        elif route == "/api/compress":
            target = payload.get("path")
            if not target or not os.path.isfile(target):
                return self._send_json({"error": "File does not exist or is not a plain file"}, 400)
            if not is_safe_path(target):
                return self._send_json({"error": "Path outside user directory"}, 403)
            if target.endswith(".gz") or target.endswith(".zip"):
                return self._send_json({"error": "File is already compressed"}, 400)
                
            gz_path = target + ".gz"
            try:
                orig_size = os.path.getsize(target)
                with open(target, 'rb') as f_in:
                    with gzip.open(gz_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                compressed_size = os.path.getsize(gz_path)
                os.remove(target)
                return self._send_json({
                    "success": True,
                    "original_size": orig_size,
                    "compressed_size": compressed_size,
                    "savings_bytes": orig_size - compressed_size,
                    "new_path": gz_path
                })
            except Exception as e:
                return self._send_json({"error": str(e)}, 500)

        elif route == "/api/delete_permanent":
            target = payload.get("path")
            confirm = payload.get("confirm")
            if confirm is not True:
                return self._send_json({"error": "Must send explicit confirmation flag"}, 400)
            if not target or not os.path.exists(target):
                return self._send_json({"error": "Target does not exist"}, 404)
            if not is_safe_path(target):
                return self._send_json({"error": "Forbidden: Path is protected or out-of-bounds"}, 403)
                
            try:
                size = os.path.getsize(target) if os.path.isfile(target) else 0
                if os.path.isdir(target):
                    def bg_rm(p):
                        subprocess.run(["rm", "-rf", p])
                    threading.Thread(target=bg_rm, args=(target,), daemon=True).start()
                else:
                    os.remove(target)

                with CACHE_LOCK:
                    FILES_CACHE[:] = [f for f in FILES_CACHE if f["path"] != target]

                return self._send_json({"success": True, "freed_bytes": size, "path": target})
            except Exception as e:
                return self._send_json({"error": str(e)}, 500)

        elif route == "/api/wipe_preset":
            preset_id = payload.get("preset_id")
            presets = get_preset_definitions()
            target_preset = next((p for p in presets if p["id"] == preset_id), None)
            if not target_preset:
                return self._send_json({"error": "Unknown preset ID"}, 404)
            if not target_preset["safe_to_wipe"]:
                return self._send_json({"error": "Preset is marked protected; quarantine individual files instead"}, 403)
                
            t_path = target_preset["path"]
            if not os.path.exists(t_path):
                return self._send_json({"success": True, "freed_bytes": 0, "message": "Already empty"})
                
            size_freed = 0
            with CACHE_LOCK:
                for item in PRESET_CACHE:
                    if item["id"] == preset_id:
                        size_freed = item.get("size_bytes", 0)
                        item["size_bytes"] = 0
                        item["exists"] = False

            def async_wipe(path):
                try:
                    subprocess.run(["rm", "-rf", path], check=True)
                    os.makedirs(path, exist_ok=True)
                except Exception as ex:
                    print("Async wipe error:", ex)

            threading.Thread(target=async_wipe, args=(t_path,), daemon=True).start()
            return self._send_json({"success": True, "freed_bytes": size_freed, "preset_id": preset_id, "status": "purging_background"})

        else:
            self.send_error(404, "Endpoint not found")

def run_server(port=8088):
    # Start background thread scanner
    t = threading.Thread(target=run_background_scanner, daemon=True)
    t.start()
    
    server_address = ('127.0.0.1', port)
    httpd = HTTPServer(server_address, SpaceSentinelHandler)
    print(f"⚡ SpaceSentinel 360 backend live on http://127.0.0.1:{port}")
    httpd.serve_forever()

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8088
    run_server(port)
