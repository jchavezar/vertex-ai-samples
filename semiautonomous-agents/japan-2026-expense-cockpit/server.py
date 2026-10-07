import json
import re
import subprocess
from pathlib import Path
from typing import Optional
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse

BASE_DIR = Path(__file__).parent
DATA_FILE = BASE_DIR / "receipts_ground_truth.json"


def load_data():
    return json.loads(DATA_FILE.read_text(encoding="utf-8"))


def save_data(data):
    # Recompute diffs and summaries across all 3 FX sources
    expenses = [p for p in data["pages"] if p["page_type"] == "EXPENSE"]
    data["total_jpy"] = sum(p["jpy_amount"] for p in expenses)
    data["total_usd_market"] = round(sum(p["usd_market"] for p in expenses), 2)
    data["total_usd_yahoo"] = round(sum(p.get("usd_market_yahoo", p["usd_market"]) for p in expenses), 2)
    data["total_usd_capi"] = round(sum(p.get("usd_market_capi", p["usd_market"]) for p in expenses), 2)
    data["total_usd_effective"] = round(
        sum(p["usd_charged"] if p.get("usd_charged") is not None else p["usd_market"] for p in expenses), 2
    )
    for p in data["pages"]:
        if p.get("usd_charged") is not None and p.get("fx_mode") == "FOREIGN_JPY":
            p["usd_diff"] = round(float(p["usd_charged"]) - float(p["usd_market"]), 2)
            p["usd_diff_yahoo"] = round(float(p["usd_charged"]) - float(p.get("usd_market_yahoo", p["usd_market"])), 2)
            p["usd_diff_capi"] = round(float(p["usd_charged"]) - float(p.get("usd_market_capi", p["usd_market"])), 2)
        else:
            p["usd_diff"] = None
            p["usd_diff_yahoo"] = None
            p["usd_diff_capi"] = None
    DATA_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return data


class CockpitHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(BASE_DIR), **kwargs)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/data":
            data = load_data()
            self._send_json(200, data)
            return
        if parsed.path == "/":
            self.path = "/index.html"
        return super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length).decode("utf-8")) if length > 0 else {}

        if parsed.path == "/api/update-charge":
            page_num = int(body.get("page"))
            usd_charged = body.get("usd_charged")
            payment_method = body.get("payment_method")
            card_network = body.get("card_network")

            data = load_data()
            for p in data["pages"]:
                if p["page"] == page_num:
                    if usd_charged is None or usd_charged == "":
                        p["usd_charged"] = None
                    else:
                        p["usd_charged"] = round(float(usd_charged), 2)
                    if payment_method:
                        p["payment_method"] = payment_method
                    if card_network:
                        p["card_network"] = card_network
                # Also sync paired slip display if applicable
                if p.get("paired_page") == page_num and usd_charged not in (None, ""):
                    p["usd_charged"] = round(float(usd_charged), 2)

            updated = save_data(data)
            self._send_json(200, {"status": "ok", "data": updated})
            return

        if parsed.path == "/api/sync-chrome":
            # Attempt to read active gemini.google.com or banking tab in Google Chrome via AppleScript
            apple = '''
            tell application "Google Chrome"
                repeat with w in windows
                    repeat with t in tabs of w
                        if (URL of t contains "gemini.google.com") or (URL of t contains "bankofamerica.com") or (URL of t contains "americanexpress.com") then
                            set tabText to execute t javascript "document.body.innerText"
                            return (URL of t) & "\\n---SPLIT---\\n" & tabText
                        end if
                    end repeat
                end repeat
                return "NO_MATCHING_TAB"
            end tell
            '''
            proc = subprocess.run(["osascript", "-e", apple], capture_output=True, text=True)
            if proc.returncode != 0:
                self._send_json(200, {
                    "status": "error",
                    "error": proc.stderr.strip(),
                    "instructions": "In Google Chrome, click 'View > Developer > Allow JavaScript from Apple Events' in the top macOS menu bar (and click Allow on the popup), then click Sync again."
                })
                return
            self._send_json(200, {
                "status": "ok",
                "raw_preview": proc.stdout[:2000]
            })
            return

        self._send_json(404, {"error": "Not found"})

    def _send_json(self, code: int, payload: dict):
        raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)


if __name__ == "__main__":
    port = 8095
    print(f"Starting Japan 2026 Expense & FX Intelligence Cockpit on http://localhost:{port}")
    server = HTTPServer(("0.0.0.0", port), CockpitHandler)
    server.serve_forever()
