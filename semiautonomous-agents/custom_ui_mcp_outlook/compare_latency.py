import time
import requests

def test_endpoint(name, port, path, payload):
    url = f"http://localhost:{port}{path}"
    headers = {"Content-Type": "application/json"}
    t0 = time.time()
    try:
        if path == "/api/chat":
            r = requests.post(url, headers=headers, json=payload, timeout=60)
            elapsed = round(time.time() - t0, 2)
            print(f"[{name}] Latency: {elapsed}s | Status: {r.status_code}")
            return elapsed
        else:
            headers["X-Entra-Id-Token"] = "session-active-token"
            first_chunk_time = None
            with requests.post(url, headers=headers, json=payload, stream=True, timeout=60) as r:
                for line in r.iter_lines():
                    if line:
                        decoded = line.decode("utf-8")
                        if "type\": \"text" in decoded or "type\": \"tool_call" in decoded:
                            if not first_chunk_time:
                                first_chunk_time = round(time.time() - t0, 2)
            total_time = round(time.time() - t0, 2)
            print(f"[{name}] First Chunk: {first_chunk_time}s | Total Streaming Latency: {total_time}s")
            return total_time
    except Exception as e:
        print(f"[{name}] Error: {e}")
        return None

if __name__ == "__main__":
    print("========================================")
    print("Latency Benchmark Comparison")
    print("========================================")
    query = "What was my last email?"
    test_endpoint("Cloud Agent Platform (Reasoning Engine + Agent Identity)", 8001, "/api/search", {"query": query})
