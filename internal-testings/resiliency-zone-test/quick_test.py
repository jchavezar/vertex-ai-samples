import json
import time
from google.cloud import aiplatform

PROJECT_ID = "vtxdemos"
REGION = "us-central1"
ENDPOINT_ID = "6943746332649586688"

def main():
    print(f"[*] Connecting to Vertex AI Endpoint: {ENDPOINT_ID} ({REGION})...")
    aiplatform.init(project=PROJECT_ID, location=REGION)
    endpoint = aiplatform.Endpoint(ENDPOINT_ID)

    print("\n[*] Sending 10 consecutive requests to observe zone distribution...")
    print("-" * 75)
    print(f"{'Req #':<6} | {'GCP Zone':<15} | {'Replica UUID':<36} | {'Latency':<10}")
    print("-" * 75)

    zones_seen = {}
    for i in range(10):
        t0 = time.time()
        response = endpoint.predict(instances=[{"test_id": i + 1}])
        latency_ms = (time.time() - t0) * 1000

        pred = response.predictions[0]["served_by"]
        zone = pred.get("zone", "unknown")
        ruuid = pred.get("replica_uuid", "unknown")[:8] + "..."
        zones_seen[zone] = zones_seen.get(zone, 0) + 1

        print(f"{i+1:<6} | {zone:<15} | {ruuid:<36} | {latency_ms:.1f} ms")
        time.sleep(0.2)

    print("-" * 75)
    print(f"[+] Summary: {dict(zones_seen)}")

if __name__ == "__main__":
    main()
