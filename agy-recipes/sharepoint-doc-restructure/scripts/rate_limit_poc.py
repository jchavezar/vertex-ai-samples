import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.request
import urllib.error
import json

# --- CONFIGURATION ---
PORT = 8999
HOST = "localhost"
QPS_LIMIT = 2.0  # Max requests per second before throttling
RETRY_AFTER_SEC = 3

# --- STATE ---
lock = threading.Lock()
last_request_time = 0.0

class RateLimitingHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        return

    def do_GET(self):
        global last_request_time
        current_time = time.time()
        
        with lock:
            time_since_last = current_time - last_request_time
            last_request_time = current_time

        # Check QPS
        if time_since_last > 0 and (1.0 / time_since_last) > QPS_LIMIT:
            self.send_response(429)
            self.send_header("Content-Type", "application/json")
            self.send_header("Retry-After", str(RETRY_AFTER_SEC))
            self.end_headers()
            response = json.dumps({"error": "Too Many Requests", "retry_after": RETRY_AFTER_SEC})
            self.wfile.write(response.encode("utf-8"))
            print(f"[SERVER] Throttled request from client. Sent Retry-After: {RETRY_AFTER_SEC}s")
        else:
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            response = json.dumps({"status": "success", "data": "Mock SharePoint Document Content"})
            self.wfile.write(response.encode("utf-8"))
            print("[SERVER] Request processed successfully (200 OK)")

def run_server():
    server_address = (HOST, PORT)
    httpd = HTTPServer(server_address, RateLimitingHandler)
    print(f"[SERVER] Started mock SharePoint server on http://{HOST}:{PORT}")
    httpd.serve_forever()

# --- CLIENT WITH RETRY-AFTER LOGIC (urllib version) ---
def run_client():
    time.sleep(1)
    print("[CLIENT] Initializing client ingestion run...")
    
    url = f"http://{HOST}:{PORT}/items/doc_123"
    total_docs = 5
    doc_index = 1
    
    while doc_index <= total_docs:
        print(f"\n[CLIENT] Requesting document {doc_index}/{total_docs}...")
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req) as response:
                body = response.read().decode("utf-8")
                print(f"[CLIENT] Successfully ingested document {doc_index}!")
                doc_index += 1
                # Fast pacing to trigger throttling
                time.sleep(0.1)
                
        except urllib.error.HTTPError as e:
            if e.code == 429:
                retry_after = int(e.headers.get("Retry-After", 1))
                print(f"[CLIENT] WARNING: Received HTTP 429 (Throttled).")
                print(f"[CLIENT] Respecting Retry-After header. Sleeping for {retry_after} seconds...")
                time.sleep(retry_after)
                print("[CLIENT] Resuming execution...")
            else:
                print(f"[CLIENT] HTTP Error: {e.code} - {e.reason}")
                doc_index += 1
        except Exception as e:
            print(f"[CLIENT] Error: {e}")
            break

    print("\n[CLIENT] Ingestion run completed.")

if __name__ == "__main__":
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    run_client()
